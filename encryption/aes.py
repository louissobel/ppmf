"""
modules with functions implementing core plaintext encryption

core of the future encryption layers
"""

from hashlib import md5
import io
import itertools

from Crypto.Cipher import AES
from Crypto import Random

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

    KEY_LENGTH = 32 # 8 * 32 = 256 bits

    def derive_key_and_iv(self, password, salt, iv_length):
        d = d_i = ''
        while len(d) < KEY_LENGTH + iv_length:
            d_i = md5(d_i + password + salt).digest()
            d += d_i
        return d[:KEY_LENGTH], d[KEY_LENGTH:KEY_LENGTH+iv_length]

    def pad(self, string, block_size):
        padding_length = block_size - (len(string) % block_size)
        return string + chr(padding_length) * padding_length

    def chunks_of(self, string, size):
        """
        returns list of chunks of size bytes from string
        last one may be less
        """
        iterator = iter(string)
        out = []
        while True:
            res = ''.join(itertools.islice(iterator, size))

            if res:
                out.append(res)
            else:
                return out

    def encrypt(self, text, password):

        salt = Random.new().read(BLOCK_SIZE - len(SALT_PREFIX))
        key, iv = self.derive_key_and_iv(password, salt, BLOCK_SIZE)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        chunks = self.chunks_of(text, size=CHUNK_SIZE)

        out = []
        out.append(SALT_PREFIX + salt)
        for index, chunk in enumerate(chunks):
            last_chunk = len(chunks) == index + 1

            if last_chunk:
                if len(chunk) == CHUNK_SIZE:
                    # then we need to add a full padded block
                    chunk = chunk + self.pad('', BLOCK_SIZE)
                elif len(chunk) % BLOCK_SIZE != 0:
                    # pad it to a multiple of block_size
                    chunk = self.pad(chunk, BLOCK_SIZE)

            out.append(cipher.encrypt(chunk))

        return ''.join(out)

    def decrypt(self, text, password):
        # first block is salt
        saltblock, ciphertext = text[:BLOCK_SIZE], text[BLOCK_SIZE:]
        salt = saltblock[len(SALT_PREFIX):]

        chunks = self.chunks_of(ciphertext, size=CHUNK_SIZE)
        key, iv = self.derive_key_and_iv(password, salt, BLOCK_SIZE)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        out = []
        for index, chunk in enumerate(chunks):
            last_chunk = len(chunks) == index + 1

            decrypted_chunk = cipher.decrypt(chunk)
            if last_chunk:
                padding_length = ord(decrypted_chunk[-1])
                out.append(decrypted_chunk[:-padding_length])
            else:
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
