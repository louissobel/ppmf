"""
Encapsulation of an open decrypted file
"""
import os
import os.path
import threading

from file_content import EncryptedContent, UnencryptedContent, CryptboxContent
from . import exceptions

class OpenDecryptedFile(object):
    """
    represents one handle to an open decrypted file
    """

    def __init__(self, path, source_path, fd, **kwargs):
        """
        path is path of temp file where the decrypted file is actually on disk
        fd is fd of temp file where it actually is on disk
        source_path is the path where the encrypted file lives

        kwargs is to set some stuff
        """
        self.path = path
        self.fd = fd
        self.source_path = source_path

        self.password = kwargs['password']

        self.dirty = False
        self.reference_count = 0
        self.rwlock = threading.Lock()

        # if im creating, do an encrypt
        # otherwise, decrypt and let the err bubble
        # TODO: should it bubble?
        if kwargs.get('create', False):
            self.encrypt()
        else:
            self.decrypt()

    def close(self):
        """
        do a flush
        """
        with self.rwlock:
            self.flush()
        os.close(self.fd)

    def decrypt(self):
        """
        loads content from source_path
        writes it to path (using fd)

        self.decrypted_fd will be set to start of file

        could do some weird things if someone has another handle to the
        tempfile. is that even possible? nah.
        """
        ciphertext = self._load_ciphertext(path=self.source_path)
        plaintext = ciphertext.decrypt(self.password)
        self._dump_file(plaintext, fd=self.fd)

    def encrypt(self):
        """
        encrypted contents of self.fd,
        writing them to the source path

        NOT THREAD SAFE SOMEONE ELSE COULD BE WRITING TO SOURCE PATH?
        """
        plaintext = self._load_plaintext(fd=self.fd)
        ciphertext = plaintext.encrypt(self.password)
        self._dump_file(ciphertext, path=self.source_path)

    def changed(self):
        """
        for now, flush! (assume outside syncrhonization)
        """
        self.dirty = True
        self.flush()

    def flush(self):
        """
        dump encrypted if dirty and set clean

        ASSUMING SOMEONE ELSE IN SYNCHRONIZING ACCESS...
        """
        if self.dirty:
            self.encrypt()
            self.dirty = False
        return 0

    def _load_ciphertext(self, **kwargs):
        kwargs['kind'] = 'cipher'
        return self._load_file(**kwargs)

    def _load_plaintext(self, **kwargs):
        kwargs['kind'] = 'plain'
        return self._load_file(**kwargs)

    def _load_file(self, path=None, fd=None, kind=None):
        """
        loads file using fd or path into ContentKlass
        specified by kind

        if given fd, might change its position. evil?
        """
        if kind == 'cipher':
            content_klass = EncryptedContent
        elif kind == 'plain':
            content_klass = UnencryptedContent
        else:
            raise ValueError("argument kind must be either 'cipher' or 'plain'")

        if fd is not None:
            # use fd
            size = os.lseek(fd, 0, os.SEEK_END)
            os.lseek(fd, 0, os.SEEK_SET)
            contents = os.read(fd, size)
        elif path is not None:
            # use path then
            with open(path, 'rb') as f:
                contents = f.read()
        else:
            raise ValueError('Either path or fd must be specified')

        return content_klass(contents, self.path)

    def _dump_file(self, content, path=None, fd=None):
        """
        dumps `content` to path or fd
        will completely overwrite them
        content is an instance of CryptboxContent

        if given fd, unspecified ending position
        """
        if not isinstance(content, CryptboxContent):
            raise ValueError('content argument must be instance of CryptboxContent')

        if fd is not None:
            # use fd
            os.lseek(fd, 0, os.SEEK_SET)
            location = os.write(fd, content.value())
            os.ftruncate(fd, location)
            # TODO: do I need fsync? no flush on fd...
        elif path is not None:
            # use path then
            with open(path, 'wb') as f:
                f.write(content.value())
                f.flush()
        else:
            raise ValueError('Either path of fd must be specified')

