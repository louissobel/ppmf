"""
Wrappers for files

Convenience methods for accessing their different parts, too
"""
from StringIO import StringIO

import html_wrapper
from base64 import b64encode, b64decode
from encryption import aes
from encryption import rsa
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

    def __init__(self, value, filename=None):
        super(EncryptedContent, self).__init__(value)
        self.cipherblock = html_wrapper.unwrap(self.value())

    def extract_ciphertext(self):
        """
        gets the raw cipher text (b64-encoded) from whatever
        format this file is in
        """
        return b64decode(self.cipherblock["ciphertext"])

    def extract_mimetype(self):
        #i am not sure if we need this
        return self.cipherblock["mimetype"]


    def decrypt(self, **credentials):
        """
        try to decrypt in order, using:
            1. per-file password
            2. rsa key
            3. default password

        all of these should be in the credentials object, but putting in default values of None for testing purposes
        errors if none of the above are in the credentials object
        """
        if credentials.get('password') is not None:
            password = credentials['password']
        else:
            #it should never get here since password is set on create, but just in case...
            password = credentials['default_password']

        ciphertext = self.extract_ciphertext()
        plaintext = aes.decrypt(ciphertext, password)        
        return UnencryptedContent(plaintext)

class UnencryptedContent(CryptboxContent):

    def encrypt(self, **credentials):
        """
        returns an encrypted file!
        keys is a list of public keys to encrypt with
        try to encrypt in order, using:
            1. per-file password
            2. default password

        errors if no password or default password is provided
        """
        passwords = credentials.get("passwords", {})
        password = credentials.get("password")
        keys = credentials.get('public_keys', [])

        plaintext = self.value()
        ciphertext = aes.encrypt(plaintext, password)

        cipherblock = {
            "ciphertext" : b64encode(ciphertext),
            "mimetype" : self.mimetype,
            "keys" : passwords,
        }
        formatted_content = html_wrapper.wrap(cipherblock)
        return EncryptedContent(formatted_content)
