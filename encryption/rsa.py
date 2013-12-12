import fileinput
from hashlib import md5

from base64 import b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class RSAWrapper(object):

    def encrypt(self, plaintext, public_key):
        rsa_key = RSA.importKey(public_key)
        rsa_key = PKCS1_OAEP.new(rsa_key)
        encrypted = rsa_key.encrypt(plaintext)
        return encrypted.encode('base64')

    def decrypt(self, ciphertext, private_key):
        rsa_key = RSA.importKey(private_key)
        rsa_key = PKCS1_OAEP.new(rsa_key) 
        decrypted = rsa_key.decrypt(b64decode(ciphertext)) 
        return decrypted

    def get_fingerprint(self, key):
        """
        returns a fingerprint of a key so we know which AES key we should decrypt
        """
        #should we do some other fingerprinting here...? using just md5 hash for now, don't think it matters
        return md5(key).hexdigest()

    def generate_keypair(self, bits=2048):
        """
        taken from https://launchkey.com/docs/api/encryption
        """
        new_key = RSA.generate(bits, e=65537) 
        public_key = new_key.publickey().exportKey("PEM") 
        private_key = new_key.exportKey("PEM") 
        return private_key, public_key

def encrypt(plaintext, public_key):
    """
    encrypts that shit
    """
    return RSAWrapper().encrypt(plaintext, public_key)

def decrypt(ciphertext, private_key):
    """
    decrypts that shit
    """
    return RSAWrapper().decrypt(ciphertext, private_key)

def get_fingerprint(key):
    """
    fingerprints that shit!
    """
    return RSAWrapper().get_fingerprint(key)

if __name__ == "__main__":
    import sys

    source = ''.join([ line for line in fileinput.input(sys.argv[1]) ])
    mode = sys.argv[2]
    key = ''.join([ line for line in fileinput.input(sys.argv[3]) ]).strip()

    if mode == 'enc':
        print encrypt(source, key)
    elif mode == 'dec':
        print decrypt(source, key)
    else:
        raise ValueError