"""
basic check on a core_encryption roundtrip
"""
import core_encryption

def test_roundtrip():
    message = "sdfkjl 3209oij \x03 sdlfkj \x34 dlfkj FOOBAR wekhj lalal pooop"
    password = 'poop'
    assert message == core_encryption.decrypt(
        core_encryption.encrypt(message, password),
        password
    )
