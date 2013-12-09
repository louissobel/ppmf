"""
Wrappers for files

Convenience methods for accessing their different parts, too
"""
from StringIO import StringIO

import html_wrapper
from encryption import aes


class CryptboxContent(object):

    def __init__(self, value):
        self.file = StringIO(value)

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
        formatted_content = html_wrapper.wrap(ciphertext)
        return EncryptedContent(formatted_content)
