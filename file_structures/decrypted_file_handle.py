"""
handle pointing to an open decrypted file
"""
import os

class DecryptedFileHandle(object):

    def __init__(self, decrypted_file, fd, **kwargs):
        """
        decrypted file is the OpenDecryptedFile holding the contents

        TODO: maintains a position within the file?
        """
        self.decrypted_file = decrypted_file
        self.fd = fd
        self.readable = kwargs['readable']
        self.writable = kwargs['writable']

        self.open = True

    def is_read_only(self):
        """
        useful
        """
        return self.readable is True and self.writable is False

    def read(self, size, offset):
        """
        reads
        """
        if not self.readable:
            raise exceptions.CannotRead('from fd %d' % self.fd)

        with self.decrypted_file.rwlock:
            # TODO errors? they bubble right now
            fd = self.decrypted_file.fd
            os.lseek(fd, offset, os.SEEK_SET)
            return os.read(fd, size)

    def write(self, data, offset):
        """
        write!
        """
        if not self.writable:
            raise exceptions.CannotWrite('to fd %d' % self.fd)

        if len(data) > 0:
            with self.decrypted_file.rwlock:
                # TODO errors? let em bubble
                fd = self.decrypted_file.fd
                os.lseek(fd, offset, os.SEEK_SET)
                result = os.write(fd, data)
                self.decrypted_file.changed()
                return result

    def truncate(self, length):
        """
        truncate
        """
        if not self.writable:
            raise exceptions.CannotWrite('to fd %d' % self.fd)

        with self.decrypted_file.rwlock:
            # TODO errors? let em bubble
            result = os.ftruncate(self.decrypted_file.fd, length)
            self.decrypted_file.changed()
            return result
