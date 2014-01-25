"""
basic checks on an html_wrapper roundtrip
"""
import html_wrapper
from file_content import EncryptedContent

def test_roundtrip():
    wrapper = html_wrapper.HTMLWrapper()
    content = EncryptedContent("sdfkjl 3209oij \x03 sdlfkj \x34 dlfkj FOOBAR wekhj lalal pooop")
    assert content.b64ciphertext == wrapper.unwrap(wrapper.wrap(content)).b64ciphertext

def test_long_string():
    wrapper = html_wrapper.HTMLWrapper()
    content = EncryptedContent('a' * 1024)
    assert content.b64ciphertext == wrapper.unwrap(wrapper.wrap(content)).b64ciphertext