"""
basic check on a core_encryption roundtrip
"""
from encryption import aes

def test_roundtrip():
    message = "sdfkjl 3209oij \x03 sdlfkj \x34 dlfkj FOOBAR wekhj lalal pooop"
    password = 'poop'
    assert message == aes.decrypt(
        aes.encrypt(message, password),
        password
    )
