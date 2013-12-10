"""
Encapsulation of an open decrypted file
"""
import os

from file_content import EncryptedContent, UnencryptedContent, CryptboxContent
from . import exceptions

class OpenDecryptedFile(object):

    def __init__(self, path, source_path, **kwargs):
        """
        path is path of temp file where the decrypted file is actually on disk
        source_path is the path where the encrypted file lives

        kwargs is to set some stuff
        """
        self.path = path
        self.source_path = source_path

        self.fd = kwargs['fd']
        self.password = kwargs['password']

        self.readable = kwargs['readable']
        self.writable = kwargs['writable']

        self.dirty = False
        self.open = True

    def is_read_only(self):
        """
        useful
        """
        return self.readable is True and self.writable is False

    def decrypt(self):
        """
        loads content from source_path
        writes it to path (using fd)

        self.fd will be set to start of file

        could do some weird things if someone has another handle to the
        tempfile. is that even possible? nah.
        """
        ciphertext = self._load_ciphertext(path=self.source_path)
        plaintext = ciphertext.decrypt(self.password)
        self._dump_file(plaintext, fd=self.fd)

        # make sure fd is seeked to start
        os.lseek(self.fd, 0, os.SEEK_SET)

    def encrypt(self):
        """
        encrypted contents of self.fd,
        writing them to the source path

        NOT THREAD SAFE SOMEONE ELSE COULD BE WRITING TO SOURCE PATH
        """
        plaintext = self._load_plaintext(fd=self.fd)
        ciphertext = plaintext.encrypt(self.password)
        self._dump_file(ciphertext, path=self.source_path)

    def read(self, size, offset):
        """
        reads
        """
        if not self.readable:
            raise exceptions.CannotRead('from fd %d' % self.fd)

        # TODO errors? they bubble right now
        fd = self.fd
        os.lseek(fd, offset, os.SEEK_SET)
        return os.read(fd, size)

    def write(self, data, offset):
        """
        write!
        """
        if not self.writable:
            raise exceptions.CannotWrite('to fd %d' % self.fd)

        # TODO errors? let em bubble
        if len(data) > 0:
            self.dirty = True
            fd = self.fd
            os.lseek(fd, offset, os.SEEK_SET)
            return os.write(fd, data)

    def truncate(self, length):
        """
        truncate
        """
        if not self.writable:
            raise exceptions.CannotWrite('to fd %d' % self.fd)

        # TODO errors? let em bubble
        self.dirty = True
        os.ftruncate(self.fd, length)

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

        return content_klass(contents)

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

