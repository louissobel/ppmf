"""
modules with functions implementing aes crypto
"""
from hashlib import md5

from Crypto.Cipher import AES
from Crypto import Random

from . import util

KEY_LENGTH = 32 # bytes = 256 bits
BLOCK_SIZE = AES.block_size
CHUNK_SIZE = 1024 * BLOCK_SIZE
SALT_PREFIX = 'Salted__'


class AESWrapper(object):
    """
    open SSL compatibility layer:
    Janked from
    http://stackoverflow.com/questions/16761458/how-to-aes-encrypt-decrypt-files-using-python-pycrypto-in-an-openssl-compatible
    """

    def derive_key_and_iv(self, password, salt, iv_length):
        """
        returns key, iv
        based on md5 of password
        not super secure!
        """
        d = d_i = ''
        while len(d) < KEY_LENGTH + iv_length:
            d_i = md5(d_i + password + salt).digest()
            d += d_i
        return d[:KEY_LENGTH], d[KEY_LENGTH:KEY_LENGTH+iv_length]

    def get_cipher(self, password, salt):
        """
        builds and returns an Crypto.AES instance
        based on given password and salt
        """
        key, iv = self.derive_key_and_iv(password, salt, BLOCK_SIZE)
        return AES.new(key, AES.MODE_CBC, iv)

    def encrypt(self, text, password):
        """
        encrypts the text given the password
        compatible with OpenSSL AES
        """
        salt = Random.new().read(BLOCK_SIZE - len(SALT_PREFIX))
        cipher = self.get_cipher(password, salt)

        header = SALT_PREFIX + salt
        out = [header]
        for chunk, is_last in util.chunks_of(text, size=CHUNK_SIZE):
            if is_last:
                chunk = util.pkcs7_pad(chunk, BLOCK_SIZE)
            out.append(cipher.encrypt(chunk))

        return ''.join(out)

    def decrypt(self, text, password):
        """
        decrypts the given text using the password
        assumes ciphertext is OpenSSL compatible
        """
        # first block is salt
        saltblock, ciphertext = text[:BLOCK_SIZE], text[BLOCK_SIZE:]
        salt = saltblock[len(SALT_PREFIX):]
        cipher = self.get_cipher(password, salt)

        out = []
        for chunk, is_last in util.chunks_of(ciphertext, size=CHUNK_SIZE):
            decrypted_chunk = cipher.decrypt(chunk)
            if is_last:
                decrypted_chunk = util.pkcs7_unpad(decrypted_chunk)
            out.append(decrypted_chunk)

        return ''.join(out)

## Module level wrappers

def encrypt(plaintext, password):
    """
    encrypts that shit
    """
    return AESWrapper().encrypt(plaintext, password)

def decrypt(ciphertext, password):
    """
    decrypts that shit!
    """
    print password
    return AESWrapper().decrypt(ciphertext, password)

if __name__ == "__main__":
    import sys

    source = sys.argv[1]
    mode = sys.argv[2]
    password = sys.argv[3]

    with open(source, 'rb') as f:
        c = f.read()
        if mode == 'enc':
            sys.stdout.write(encrypt(c, password))
        elif mode == 'dec':
            sys.stdout.write(decrypt(c, password))
        else:
            raise ValueError
