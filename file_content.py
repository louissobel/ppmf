"""
Wrappers for files

Convenience methods for accessing their different parts, too
"""
import json

import html_wrapper
from base64 import b64encode, b64decode
from encryption import aes
from encryption import rsa
from mimetypes import guess_type

DEFAULT_MIMETYPE = 'application/octet-stream'

class CryptboxContent(object):
    pass

class EncryptedContent(CryptboxContent):

    def __init__(self, b64ciphertext):
        self.b64ciphertext = b64ciphertext

    def decrypt(self, password):
        """
        decrypt from password
        """
        ciphertext = b64decode(self.b64ciphertext)
        plaintext_blob = aes.decrypt(ciphertext, password)
        return UnencryptedContent.from_blob(plaintext_blob)

class UnencryptedContent(CryptboxContent):

    @classmethod
    def from_blob(cls, plaintext_blob):
        """
        plaintext blob is json string
        """
        obj = json.loads(plaintext_blob)
        plaintext = b64decode(obj['b64plaintext'])
        mimetype = obj['mimetype']
        return cls(plaintext, mimetype)

    def create_blob(self):
        """
        returns blob - mirror of
        """
        obj = {
            'b64plaintext' : b64encode(self.plaintext),
            'mimetype' : self.mimetype,
        }
        return json.dumps(obj)

    def __init__(self, plaintext, mimetype):
        self.plaintext = plaintext
        self.mimetype = mimetype

    def encrypt(self, password):
        """
        returns an encrypted file!
        """
        plaintext_blob = self.create_blob()
        ciphertext = aes.encrypt(plaintext_blob, password)
        b64ciphertext = b64encode(ciphertext)

        return EncryptedContent(b64ciphertext)
