"""
Wrappers for files

Convenience methods for accessing their different parts, too
"""
from StringIO import StringIO

import html_wrapper
from base64 import b64encode, b64decode
from get_password import get_keys
from encryption import aes
from encryption import rsa
import mimetypes


class CryptboxContent(object):

    def __init__(self, value, filename=None):
        self.file = StringIO(value)
        if filename is not None:
            self.mimetype = mimetypes.guess_type(filename)[0]
        else:
            self.mimetype = 'application/octet-stream'

    def value(self):
        return self.file.getvalue()

class EncryptedContent(CryptboxContent):

    def __init__(self, value, filename=None):
        super(EncryptedContent, self).__init__(value)
        self.cipherblock = html_wrapper.unwrap(self.value())

    def extract_encrypted_aes_key(self, public_key):
        """
        uses public key to get the RSA-encrypted AES key
        returns none if no match
        """
        fingerprint = rsa.get_fingerprint(public_key)
        return self.cipherblock["keys"].get(fingerprint, None)

    def extract_ciphertext(self):
        """
        gets the raw cipher text (b64-encoded) from whatever
        format this file is in
        """
        return b64decode(self.cipherblock["ciphertext"])

    def extract_mimetype(self):
        #i am not sure if we need this
        return self.cipherblock["mimetype"]

    def decrypt(self, password=None):
        #where to get the key?
        ciphertext = self.extract_ciphertext()
        if password is not None:
            plaintext = aes.decrypt(ciphertext, password)
        else:
            #i need to write this one...exceptions?
            public_key, private_key = get_keys.get_public_key(), get_keys.get_private_key()
            aes_key = rsa.decrypt(self.extract_encrypted_aes_key(public_key), private_key)
            plaintext = aes.decrypt(ciphertext, aes_key)
        
        return UnencryptedContent(plaintext)

class UnencryptedContent(CryptboxContent):

    def encrypt(self, password, keys={}):
        """
        returns an encrypted file!
        keys is a list of public keys to encrypt with
        """
        plaintext = self.value()
        ciphertext = aes.encrypt(plaintext, password)
        encrypted_keys = dict( [(rsa.get_fingerprint(key), rsa.encrypt(plaintext, key)) for key in keys] )
        cipherblock = {
            "ciphertext" : b64encode(ciphertext),
            "mimetype" : self.mimetype,
            "keys" : encrypted_keys,
        }
        formatted_content = html_wrapper.wrap(cipherblock)
        return EncryptedContent(formatted_content)
