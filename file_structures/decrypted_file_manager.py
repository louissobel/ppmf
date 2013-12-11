"""
File manager for open decrypted files
"""
import os
import tempfile
import threading
import mimetypes

from open_decrypted_file import OpenDecryptedFile

class DecryptedFileManager(object):
    """
    manages access and existence of cryptbox files
    """

    def __init__(self, credentials):
        self.open_files_by_inode = {}
        self.registry_lock = threading.Lock()

        self.credentials = credentials

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
        """

        readable = kwargs.get('read', False)
        writable = kwargs.get('write', False)

        # open a temp file
        mimetype = mimetypes.guess_type(path)
        temp_extension = ''
        if mimetype[0] is not None:
            temp_extension = mimetypes.guess_extension(mimetype[0])
        temp_fd, temp_path = tempfile.mkstemp(temp_extension)


        file_creds = {
            "rsa_key_pair" : (self.credentials.get_public_key(), self.credentials.get_private_key()),
            "default_password" : self.credentials.get_default_password(),
            "password" : self.credentials.get_password_for(path),
            "public_keys" : self.credentials.get_public_keys_for(path),
        }

        open_file = OpenDecryptedFile(temp_path, path,
            fd=temp_fd,
            readable=readable,
            writable=writable,
            credentials=file_creds
        )
        self._register(open_file)

        if kwargs.get('create', False):
            # we need to create the encrypted empty version
            open_file.encrypt()
        else:
            # load decrypted version
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

        open_file.flush()
