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

    def extract_password(self, public_key, private_key):
        fingerprint = rsa.get_fingerprint(public_key)
        encrypted_aes_key = self.cipherblock["keys"].get(fingerprint, None)

        if encrypted_aes_key is not None:
            return rsa.decrypt(encrypted_aes_key, private_key)
        return None


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
        ciphertext, plaintext = self.extract_ciphertext(), None

        password = None
        if credentials.get('password', None) is not None:
            password = credentials['password']
        elif credentials.get('rsa_key_pair', None) is not None:
            password = self.extract_password(*(credentials['rsa_key_pair']))
        
        if password is None:
            password = credentials['default_password']

        password = password.encode('utf-8')

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
        password = credentials['password']
        if password is None:
            password = credentials['default_password']
        password = password.encode('utf-8')

        keys = credentials.get('public_keys', [])

        plaintext = self.value()
        ciphertext = aes.encrypt(plaintext, password)
        encrypted_keys = dict( [(rsa.get_fingerprint(key), rsa.encrypt(password, key)) for key in keys] )
        cipherblock = {
            "ciphertext" : b64encode(ciphertext),
            "mimetype" : self.mimetype,
            "keys" : encrypted_keys,
        }
        formatted_content = html_wrapper.wrap(cipherblock)
        return EncryptedContent(formatted_content)
