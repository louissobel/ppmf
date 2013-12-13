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
import config_file_manager
import open_flag_parser

VERBOSE = False

ENCRYPTION_PREFIX = '__enc__'

class CryptboxFS(fuse.Operations):
    """
    File System

    TODO: think hard about concurrency + locking
    let's make config_pathname be absolute for now
    """

    def __init__(self, root, mountpoint, config_pathname, rsa_key_pathname):
        self.root = root
        self.rwlock = threading.Lock()
        self.loglock = threading.Lock()

        credentials = config_file_manager.CredentialConfigManager(root, config_pathname, rsa_key_pathname)
        encrypted_root = os.path.join(mountpoint, ENCRYPTION_PREFIX)
        self.file_manager = file_structures.DecryptedFileManager(
            root,
            encrypted_root,
            credentials,
        )

    def __call__(self, *args, **kwargs):
        uid, gid, pid = fuse.fuse_get_context()
        try:
            self._log("starting ", args[0])
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

        # TODO: properly handle stat call on __enc__ itself?
        #       right now implicitly handled by real_path
        with self.rwlock:
            if encrypted_context or os.path.isdir(real_path):
                st = os.lstat(real_path)
            else:
                try:
                    file_handle = self.file_manager.open(real_path)
                except IOError:
                    e = OSError()
                    e.errno = errno.ENOENT
                    e.filename = "No such file or directory"
                    raise e

                # get the fd of the underlying tempfile
                # TODO fix that shit
                fd = file_handle.decrypted_file.fd
                st = os.fstat(fd)
                self.file_manager.close(file_handle)

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

        if encrypted_context:
            raise fuse.FuseOSError(errno.EROFS)

        open_flags = open_flag_parser.parse(file_info.flags)

        with self.rwlock:
            new_file = self.file_manager.open(real_path,
                create=True,
                read=open_flags.read,
                write=open_flags.write,
            )

        file_info.fh = new_file.fd
        file_info.direct_io = True

        self._log('created %s, fd %d (%s)' % (path, file_info.fh, str(open_flags)))
        return 0

    def open(self, path, file_info):
        real_path, encrypted_context = self._real_path_and_context(path)

        flags = file_info.flags
        open_flags = open_flag_parser.parse(flags)

        if encrypted_context:
            file_info.fh = os.open(real_path, flags)
        else:
            with self.rwlock:
                file_handle = self.file_manager.open(real_path,
                    read=open_flags.read,
                    write=open_flags.write,
                )

            file_info.fh = file_handle.fd
            file_info.direct_io = True

        self._log('opened %s, fd %d (%s)' % (path, file_info.fh, str(open_flags)))
        return 0

    def read(self, path, size, offset, file_info):
        real_path, encrypted_context = self._real_path_and_context(path)

        fd = file_info.fh
        with self.rwlock:
            if encrypted_context:
                os.lseek(fd, offset, os.SEEK_SET)
                return os.read(fd, size)
            else:
                # TODO lock file registry?
                file_handle = self.file_manager.get_handle(fd)
                if file_handle is None:
                    raise fuse.FuseOSError(errno.EBADF)

                try:
                    return file_handle.read(size, offset)
                except file_structures.exceptions.CannotRead:
                    raise fuse.FuseOSError(errno.EBADF)
                # TODO handle OSError

    def write(self, path, data, offset, file_info):
        real_path, encrypted_context = self._real_path_and_context(path)

        if encrypted_context:
            raise fuse.FuseOSError(errno.EROFS)

        fd = file_info.fh
        with self.rwlock:
            # TODO lock file registry?
            file_handle = self.file_manager.get_handle(fd)
            if file_handle is None:
                raise fuse.FuseOSError(errno.EBADF)

            try:
                self._log("writing to %d" % file_handle.fd)
                return file_handle.write(data, offset)
            except file_structures.exceptions.CannotWrite:
                raise fuse.FuseOSError(errno.EBADF)
            # TODO handle OSError

    def fsync(self, path, datasync, file_info):
        return self.flush(path, file_info)

    def flush(self, path, file_info):
        real_path, encrypted_context = self._real_path_and_context(path)

        fd = file_info.fh

        if encrypted_context:
            return os.fsync(fd)

        with self.rwlock:

            # TODO lock file registry?
            decrypted_file = self.file_manager.get_decrypted_file(fd)
            if decrypted_file is None:
                raise fuse.FuseOSError(errno.EBADF)

            # TODO handle OSError
            return decrypted_file.flush()

    def truncate(self, path, length, file_info=None):
        """
        file_info is none if this is a `truncate`
        file_info is an object if an `ftruncate`
        """
        real_path, encrypted_context = self._real_path_and_context(path)

        if encrypted_context:
            raise fuse.FuseOSError(errno.EROFS)

        with self.rwlock:

            if file_info:
                self._log("truncating from fd")
                fd = file_info.fh
                file_handle = self.file_manager.get_handle(fd)
                if file_handle is None:
                    raise fuse.FuseOSError(errno.EBADF)
                opened_file = False

            else:
                # open it (with writing allowed)
                file_handle = self.file_manager.open(real_path,
                    write=True,
                )
                opened_file = True
                self._log("truncating from path (fd %d)" % file_handle.fd)

            try:
                file_handle.truncate(length)
            except file_structures.exceptions.CannotWrite:
                raise fuse.FuseOSError(errno.EBADF)
            # TODO: handle OS / IO error?

            if opened_file:
                self.file_manager.close(file_handle)

    def release(self, path, file_info):
        """
        reencrypt it if we have to
        """
        real_path, encrypted_context = self._real_path_and_context(path)

        fd = file_info.fh

        if encrypted_context:
            return os.close(fd)
        else:
            with self.rwlock:
                file_handle = self.file_manager.get_handle(fd)
                if file_handle is None:
                    raise fuse.FuseOSError(errno.EBADF)
                else:
                    try:
                        return self.file_manager.close(file_handle)
                    except ValueError:
                        raise fuse.FuseOSError(errno.EBADF)

    def unlink(self, path):
        # TODO: do we need to do anything about other handles on the file?
        real_path, encrypted_context = self._real_path_and_context(path)

        if encrypted_context:
            raise fuse.FuseOSError(errno.EROFS)

        return os.unlink(real_path)

    def readdir(self, path, fh):
        real_path, encrypted_context = self._real_path_and_context(path)

        with self.rwlock:
            contents = ['.', '..'] + os.listdir(real_path)

        # add __enc__ for contents of /
        if path == '/':
            contents.append(ENCRYPTION_PREFIX)

        return contents

def main(root, mountpoint, config_file, rsa_key_pathname):
    return fuse.FUSE(CryptboxFS(root, mountpoint, config_file, rsa_key_pathname), mountpoint, raw_fi=True, foreground=True)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: %s <root> <mountpoint> <config file>' % sys.argv[0])
        sys.exit(1)

    try:
        if '-v' in sys.argv[5:]:
            VERBOSE = True
    except IndexError:
        # fine
        pass

    fuse = main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
