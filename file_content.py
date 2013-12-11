"""
Wrappers for files

Convenience methods for accessing their different parts, too
"""
from StringIO import StringIO

import html_wrapper
from encryption import aes
from mimetypes import guess_type

DEFAULT_MIMETYPE = 'application/octet-stream'

class CryptboxContent(object):

    def __init__(self, value, filename=None):
        self.file = StringIO(value)
        if filename is not None:
            self.mimetype = guess_type(filename)[0]
            if self.mimetype is None:
                self.mimetype = DEFAULT_MIMETYPE
        else:
            self.mimetype = DEFAULT_MIMETYPE

    def value(self):
        return self.file.getvalue()

class EncryptedContent(CryptboxContent):

    def extract_password(self, keys):
        """
        uses private key to pull out password
        """
        pass

    def extract_ciphertext(self):
        """
        gets the raw cipher text from whatever
        format this file is in
        """
        return html_wrapper.unwrap(self.value())

    def decrypt(self, password):
        ciphertext = self.extract_ciphertext()
        plaintext = aes.decrypt(ciphertext, password)
        return UnencryptedContent(plaintext)


class UnencryptedContent(CryptboxContent):

    def encrypt(self, password):
        """
        returns an encrypted file!
        """
        plaintext = self.value()
        ciphertext = aes.encrypt(plaintext, password)
        formatted_content = html_wrapper.wrap(ciphertext, self.mimetype)
        return EncryptedContent(formatted_content)
