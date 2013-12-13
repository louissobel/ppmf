"""
File manager for open decrypted files
"""
import os
import os.path
import tempfile
import threading
import mimetypes

from open_decrypted_file import OpenDecryptedFile
from decrypted_file_handle import DecryptedFileHandle

class DecryptedFileManager(object):
    """
    manages access and existence of cryptbox files
    """

    def __init__(self, root, encrypted_root, credentials):

        # the root dir of where the files actually live
        self.root = root

        # the VFS prefix for the encrypted root
        # probably something like /foo/bar/mountpoint/__enc__
        self.encrypted_root = encrypted_root

        self.open_files_by_path = {}
        self.file_handles = {}

        self.open_close_lock = threading.Lock()

        self.credentials = credentials

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
        """
        with self.open_close_lock:

            readable = kwargs.get('read', False)
            writable = kwargs.get('write', False)

            relative_path = self._relative_path(path)

            if relative_path not in self.credentials.get_files(): 
                self.credentials.create_file_creds_for(relative_path)
            file_creds = self.credentials.file_creds_for(relative_path)

            decrypted_file = self._get_or_open_decrypted_file(path, file_creds, kwargs.get('create', False))
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

    def _get_or_open_decrypted_file(self, path, file_creds, create=False):
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

            vfs_path = self._encrypted_path(path)

            temp_fd, temp_path = tempfile.mkstemp(suffix=temp_extension)
            open_file = OpenDecryptedFile(temp_path, path, temp_fd,
                credentials=file_creds,
                vfs_path=vfs_path,
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

    def _relative_path(self, path):
        return os.path.relpath(path, self.root)

    def _encrypted_path(self, path):
        return os.path.join(
            self.encrypted_root,
            self._relative_path(path),
        )
