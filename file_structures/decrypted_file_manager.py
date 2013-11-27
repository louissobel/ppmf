"""
File manager for open decrypted files
"""
import os
import tempfile
import threading

from open_decrypted_file import OpenDecryptedFile

class DecryptedFileManager(object):
    """
    manages access and existence of cryptbox files
    """

    def __init__(self, get_password):
        self.open_files_by_inode = {}
        self.registry_lock = threading.Lock()

        self.get_password = get_password

    def _inode_for_fd(self, fd):
        """
        given fd, returns Inode it points to
        """
        return os.fstat(fd).st_ino

    def _register(self, open_file):
        inode = self._inode_for_fd(open_file.fd)

        with self.registry_lock:
            if inode in self.open_files_by_inode:
                raise ValueError("Duplicate Inode!")

            self.open_files_by_inode[inode] = open_file

    def _deregister(self, open_file):
        inode = self._inode_for_fd(open_file.fd)

        with self.registry_lock:
            if not inode in self.open_files_by_inode:
                raise ValueError('No such file!')

            del self.open_files_by_inode[inode]

    def get_file(self, fd):
        """
        looks up the inode then the file
        returns None if cannot find it
        """
        inode = self._inode_for_fd(fd)
        return self.open_files_by_inode.get(inode)

    def open(self, path, **kwargs):
        """
        path is path on filesystem to encrypted version of the file
        password is password to decrypt the mother fucker
        """
        password = self.get_password("opening %s" % path)

        # open a temp file
        temp_fd, temp_path = tempfile.mkstemp()
        open_file = OpenDecryptedFile(temp_path, path,
            fd=temp_fd,
            password=password,
        )
        self._register(open_file)

        if not kwargs.get('create', False):
            open_file.decrypt()

        return open_file

    def close(self, open_file):
        """
        closes the given file
        :(
        """
        if not open_file.open:
            raise ValueError('File is already closed!')

        # take it out of circulation first
        self._deregister(open_file)
        open_file.open = False

        # then re-encrypt? is that my job??
        if open_file.dirty:
            open_file.encrypt()