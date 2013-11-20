"""
modules with functions implementing core plaintext encryption

core of the future encryption layers
"""

def encrypt(plaintext, password):
    """
    encrypts that shit
    """
    header = "Encrypted with password: %s\n" % password
    return header + plaintext

def decrypt(ciphertext, password):
    """
    decrypts that shit!
    """
    first_newline = ciphertext.find('\n')
    return ciphertext[first_newline + 1:]
