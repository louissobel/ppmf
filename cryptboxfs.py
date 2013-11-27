"""
FUSE implementing decrypt on read
Encrypt on write
"""

import sys
import os.path
import errno
import threading

import fuse

import file_structures
import get_password

VERBOSE = False

ENCRYPTION_PREFIX = '__enc__'

class CryptboxFS(fuse.Operations):
    """
    File System

    TODO: prevent writes to __enc__ tree?
    TODO: think hard about concurrency + locking
    """

    def __init__(self, root):
        self.root = root
        self.rwlock = threading.Lock()
        self.loglock = threading.Lock()

        self.file_manager = file_structures.DecryptedFileManager(get_password.get_password)

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

        # this is tricky actually.
        # because of st_size
        # if in encypted context, want the real path
        # otherwise, decrypt it first
        # inefficient as balls right now

        # TODO: properly handle stat call on __enc__ itself?
        #       right now implicitly handled by real_path
        if encrypted_context or os.path.isdir(real_path):
            st = os.lstat(real_path)
        else:
            try:
                decrypted_file = self.file_manager.open(real_path)
            except IOError:
                e = OSError()
                e.errno = errno.ENOENT
                e.filename = "No such file or directory"
                raise e
            fd = decrypted_file.fd
            st = os.fstat(fd)
            self.file_manager.close(decrypted_file)

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

        with self.rwlock:
            new_file = self.file_manager.open(real_path, create=True)
            new_file.encrypt()

        file_info.fh = new_file.fd
        file_info.direct_io = True
        return 0

    def open(self, path, file_info):
        real_path, encrypted_context = self._real_path_and_context(path)

        flags = file_info.flags
        if encrypted_context:
            # just return the file
            file_info.fh = os.open(real_path, flags)
        else:

            # TODO PARSE FLAGS

            # otherwise, decrypt it
            # open and read the real file into the temp file
            decrypted_file = self.file_manager.open(real_path)
            file_info.fh = decrypted_file.fd
            file_info.direct_io = True

        self._log('opened %s, fd %d' % (path, file_info.fh))
        return 0

    def read(self, path, size, offset, file_info):
        fd = file_info.fh
        with self.rwlock:
            # TODO lock file registry?
            decrypted_file = self.file_manager.get_file(fd)
            if decrypted_file is None:
                # encrypted_context check should be more explicit?
                # then just go on our merry way
                os.lseek(fd, offset, os.SEEK_SET)
                return os.read(fd, size)
            else:
                # TODO handle errors?
                return decrypted_file.read(size, offset)

    def write(self, path, data, offset, file_info):
        real_path, encrypted_context = self._real_path_and_context(path)

        if encrypted_context:
            raise fuse.FuseOSError(errno.EROFS)

        fd = file_info.fh
        with self.rwlock:
            # TODO lock file registry?
            decrypted_file = self.file_manager.get_file(fd)
            if decrypted_file is None:
                raise ValueError('No decrypted file for non-__enc__ fd %d' % fd)
            else:
                # TODO handle errors?
                return decrypted_file.write(data, offset)

    def truncate(self, path, length, file_info=None):
        """
        file_info is none if this is a `truncate`
        file_info is an object if an `ftruncate`
        """
        real_path, encrypted_context = self._real_path_and_context(path)

        if encrypted_context:
            raise fuse.FuseOSError(errno.EROFS)

        if file_info:
            fd = file_info.fh
            decrypted_file = self.file_manager.get_file(fd)
            if decrypted_file is None:
                raise ValueError('No decrypted file for non-__enc__ fd %d' % fd)
            opened_file = False

        else:
            # open it!
            decrypted_file = self.file_manager.open(real_path)
            opened_file = True

        decrypted_file.truncate(length)
        if opened_file:
            self.file_manager.close(decrypted_file)

    def release(self, path, file_info):
        """
        reencrypt it if we have to
        """
        fd = file_info.fh
        # TODO lock the registry?
        decrypted_file = self.file_manager.get_file(fd)
        if decrypted_file is None:
            # TODO more explicit __enc__ check?
            # just close it
            return os.close(fd)
        else:
            return self.file_manager.close(decrypted_file)

    def unlink(self, path):
        # TODO: do we need to do anything about other handles on the file?
        real_path, encrypted_context = self._real_path_and_context(path)

        if encrypted_context:
            raise fuse.FuseOSError(errno.EROFS)

        return os.unlink(real_path)

    def readdir(self, path, fh):
        real_path, encrypted_context = self._real_path_and_context(path)
        contents = ['.', '..'] + os.listdir(real_path)

        # add __enc__ for contents of /
        if path == '/':
            contents.append(ENCRYPTION_PREFIX)

        return contents

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
