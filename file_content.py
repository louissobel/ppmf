"""
Wrappers for files

Convenience methods for accessing their different parts, too
"""
from StringIO import StringIO

import html_wrapper
from encryption import aes
from encryption import rsa
from mimetypes import guess_type


class CryptboxContent(object):

    def __init__(self, value, filename=None):
        self.file = StringIO(value)
        if filename is not None:
            self.mimetype = guess_type(filename)[0]

    def value(self):
        return self.file.getvalue()

class EncryptedContent(CryptboxContent):

    def __init__(self, value):
        self.value = html_wrapper.unwrap(self.value())

    def extract_encrypted_aes_key(self, public_key):
        """
        uses public key to get the RSA-encrypted AES key
        returns none if no match
        """
        fingerprint = rsa.get_fingerprint(public_key)
        return self.value.keys.get(fingerprint, None)

    def extract_ciphertext(self):
        """
        gets the raw cipher text (b64-encoded) from whatever
        format this file is in
        """
        return self.value.ciphertext

    def extract_mimetype(self):
        #i am not sure if we need this
        return self.value.mimetype

    def decrypt(self):
        #where to get the key?
        ciphertext = self.extract_ciphertext()
        #i need to write this one...exceptions?
        public_key, private_key = rsa.get_public_key(), rsa.get_private_key()
        aes_key = rsa.decrypt(self.extract_encrypted_aes_key(public_key), private_key)
        plaintext = aes.decrypt(ciphertext, aes_key)
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
