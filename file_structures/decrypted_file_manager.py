"""
File manager for open decrypted files
"""
import os
import tempfile
import threading
import mimetypes

from open_decrypted_file import OpenDecryptedFile
from decrypted_file_handle import DecryptedFileHandle

class DecryptedFileManager(object):
    """
    manages access and existence of cryptbox files
    """

    def __init__(self, get_password):
        self.open_files_by_path = {}
        self.file_handles = {}

        self.open_close_lock = threading.Lock()

        self.get_password = get_password

        self.fdcounter = 0

    def get_handle(self, fd):
        """
        get the handle for the given fd
        """
        return self.file_handles.get(fd)

    def get_decrypted_file(self, fd):
        """
        gets decrypted file for fd
        """
        handle = self.get_handle(fd)
        if handle is None:
            return None
        return handle.decrypted_file

    def open(self, path, **kwargs):
        """
        path is path on filesystem to encrypted version of the file
        password is password to decrypt the mother fucker
        """
        password = self.get_password("opening %s" % path)

        with self.open_close_lock:

            readable = kwargs.get('read', False)
            writable = kwargs.get('write', False)

            decrypted_file = self._get_or_open_decrypted_file(path, password, kwargs.get('create', False))
            fd = self._next_fd()

            file_handle = DecryptedFileHandle(decrypted_file, fd,
                readable=readable,
                writable=writable,
            )

            decrypted_file.reference_count += 1
            self.file_handles[fd] = file_handle

            return file_handle

    def close(self, file_handle):
        """
        closes the given file handle
        """
        if not file_handle.open:
            raise ValueError('File is already closed!')

        with self.open_close_lock:
            try:
                del self.file_handles[file_handle.fd]
            except KeyError:
                raise ValueError("No such fd!")

            file_handle.open = False

            decrypted_file = file_handle.decrypted_file
            decrypted_file.reference_count -= 1

            if decrypted_file.reference_count == 0:
                assert decrypted_file.source_path in self.open_files_by_path
                del self.open_files_by_path[decrypted_file.source_path]
                decrypted_file.close()

    def _get_or_open_decrypted_file(self, path, password, create=False):
        """
        gets or creates and sets the open file
        assumes outside synchronization
        """
        open_file = self.open_files_by_path.get(path)
        if not open_file:
            # make it
            mimetype = mimetypes.guess_type(path)
            temp_extension = ''
            if mimetype[0] is not None:
                temp_extension = mimetypes.guess_extension(mimetype[0])

            temp_fd, temp_path = tempfile.mkstemp(suffix=temp_extension)
            open_file = OpenDecryptedFile(temp_path, path, temp_fd,
                password=password,
                create=create,
            )
            self.open_files_by_path[path] = open_file
        return open_file

    def _next_fd(self):
        """
        assumes outside syncrhonzation

        TODO make this not so dumb?
        """
        self.fdcounter += 1
        return self.fdcounter
