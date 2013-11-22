"""
FUSE implementing decrypt on read
Encrypt on write
"""

import sys
import os.path
import errno
import tempfile
import threading

import fuse

import cryptbox_files
import get_password

VERBOSE = False

ENCRYPTION_PREFIX = '__enc__'

class CryptboxFS(fuse.Operations):
    """
    File System
    """

    def __init__(self, root):
        self.root = root
        self.rwlock = threading.Lock()
        self.loglock = threading.Lock()
        self.temp_inode_to_path = {}
        self.dirty_temp_inode = set()

    def __call__(self, *args, **kwargs):
        uid, gid, pid = fuse.fuse_get_context()
        try:
            res = fuse.Operations.__call__(self, *args, **kwargs)
        except Exception as e:
            self._log(pid, args, kwargs, e)
            raise
        else:
            if VERBOSE:
                self._log(pid, args, kwargs, res)
            return res

    def _log(self, *args):
        if VERBOSE:
            with self.loglock:
                print "[cryptboxfs] %s" % ' '.join(str(a) for a in args)

    def _real_path_and_context(self, path):
        rel_path = path[1:]
        components = rel_path.split(os.path.sep)

        if components[0] == ENCRYPTION_PREFIX:
            encrypted_context = True
            components = components[1:]
        else:
            encrypted_context = False

        real_path = os.path.join(self.root, *components)
        return real_path, encrypted_context

    def _get_inode(self, fd):
        return os.fstat(fd).st_ino

    def _register_decrypted_fd(self, fd, path):
        self.temp_inode_to_path[self._get_inode(fd)] = path

    def _deregister_fd(self, fd):
        try:
            del self.temp_inode_to_path[self._get_inode(fd)]
        except KeyError:
            # fine
            pass

        self._clear_dirty(fd)

    def _mark_dirty(self, fd):
        self.dirty_temp_inode.add(self._get_inode(fd))

    def _clear_dirty(self, fd):
        try:
            self.dirty_temp_inode.remove(self._get_inode(fd))
        except KeyError:
            pass

    def _is_dirty(self, fd):
        return self._get_inode(fd) in self.dirty_temp_inode

    def _is_decrypted_fd(self, fd):
        return self._get_inode(fd) in self.temp_inode_to_path

    def _encrypted_path(self, fd):
        return self.temp_inode_to_path.get(self._get_inode(fd), None)

    def _get_decrypted_file(self, path):
        with open(path, 'rb') as f:
            cipher = f.read()
            encrypted_file = cryptbox_files.EncryptedFile(cipher)
            decrypted_file = encrypted_file.decrypt(get_password.get_password("decrypting %s" % path))
            return decrypted_file

    def _make_decrypted_fd(self, contents, encrypted_path):
        # open a temp file
        temp_fd, temp_path = tempfile.mkstemp()

        # map the inode of this fd to it's path so we know where to put it back
        self._register_decrypted_fd(temp_fd, encrypted_path)

        # write the contents to the fd and seek back
        os.write(temp_fd, contents)

        # move it back to the start
        os.lseek(temp_fd, 0, os.SEEK_SET)
        return temp_fd

    def _re_encrypt(self, fd):
        with self.rwlock:
            if self._is_decrypted_fd(fd):
                encrypted_path = self._encrypted_path(fd)

                # encrypt contents back
                size = os.lseek(fd, 0, os.SEEK_END)
                os.lseek(fd, 0, os.SEEK_SET)
                contents = os.read(fd, size)
                unencrypted = cryptbox_files.UnencryptedFile(contents)
                encrypted = unencrypted.encrypt(get_password.get_password("encrypting %s" % encrypted_path))

                with open(encrypted_path, 'w') as f:
                    f.write(encrypted.contents())

                self._clear_dirty(fd)

            else:
                raise ValueError("Must be encrypted!")

    def access(self, path, mode):
        real_path, encrypted_context = self._real_path_and_context(path)
        # first check for existence
        exists = os.access(real_path, 0)
        if not exists:
            raise fuse.FuseOSError(errno.ENOENT)

        if mode == 0:
            # then we're done
            return

        if not os.access(real_path, mode):
            raise fuse.FuseOSError(errno.EACCES)

    def getattr(self, path, fh=None):
        real_path, encrypted_context = self._real_path_and_context(path)

        class FakeFileInfo(object):
            def __init__(self, flags):
                self.flags = flags

        # this is tricky actually.
        # because of st_size
        # if in encypted context, want the real path
        # otherwise, decrypt it first
        # inefficient as balls right now
        if encrypted_context or os.path.isdir(real_path):
            st = os.lstat(real_path)
        else:
            file_info = FakeFileInfo(0)
            try:
                self.open(path, file_info)
                fd = file_info.fh
            except IOError:
                e = OSError()
                e.errno = 2
                e.filename = path
                raise e
            st = os.fstat(fd)
            self.release(path, file_info)

        return dict((key, getattr(st, key)) for key in (
            'st_atime',
            'st_ctime',
            'st_gid',
            'st_mode',
            'st_mtime',
            'st_nlink',
            'st_size',
            'st_uid',
        ))

    def create(self, path, mode, file_info):
        real_path, encrypted_context = self._real_path_and_context(path)

        # is creating it now necessary?
        real_fd = os.open(real_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
        os.close(real_fd)

        fd = self._make_decrypted_fd('', real_path)
        self._re_encrypt(fd)
        file_info.fh = fd
        file_info.direct_io = True
        return 0

    def open(self, path, file_info):
        real_path, encrypted_context = self._real_path_and_context(path)

        flags = file_info.flags
        if encrypted_context:
            # just return the file
            file_info.fh = os.open(real_path, flags)
            return 0

        # otherwise, decrypt it
        # open and read the real file into the temp file
        decrypted_file = self._get_decrypted_file(real_path)
        file_info.fh = self._make_decrypted_fd(decrypted_file.contents(), real_path)
        file_info.direct_io = True
        return 0

    def read(self, path, size, offset, file_info):
        fd = file_info.fh
        with self.rwlock:
            os.lseek(fd, offset, 0)
            v = os.read(fd, size)
            self._log('reading %d from %d, got %d' % (size, fd, len(v)))
            return v

    def write(self, path, data, offset, file_info):
        fd = file_info.fh
        with self.rwlock:
            self._mark_dirty(fd)
            os.lseek(fd, offset, 0)
            return os.write(fd, data)

    def release(self, path, file_info):
        """
        reencrypt it if we have to
        """
        fd = file_info.fh
        if self._is_decrypted_fd(fd):
            if self._is_dirty(fd):
                self._re_encrypt(fd)

            self._deregister_fd(fd)

        return os.close(fd)

    def unlink(self, path):
        real_path, encrypted_context = self._real_path_and_context(path)
        return os.unlink(real_path)

    def readdir(self, path, fh):
        real_path, encrypted_context = self._real_path_and_context(path)
        return ['.', '..'] + os.listdir(real_path)

def main(root, mountpoint):
    return fuse.FUSE(CryptboxFS(root), mountpoint, raw_fi=True, foreground=True)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: %s <root> <mountpoint>' % sys.argv[0])
        sys.exit(1)

    try:
        if sys.argv[3] == '-v':
            VERBOSE = True
    except IndexError:
        # fine
        pass

    fuse = main(sys.argv[1], sys.argv[2])
