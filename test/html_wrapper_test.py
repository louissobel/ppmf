"""
basic checks on an html_wrapper roundtrip
"""
import html_wrapper

def test_roundtrip():
    wrapper = html_wrapper.HTMLWrapper()
    ciphertext = "sdfkjl 3209oij \x03 sdlfkj \x34 dlfkj FOOBAR wekhj lalal pooop"
    assert ciphertext == wrapper.unwrap(wrapper.wrap(ciphertext))

def test_roundtrip_html_entities():
    wrapper = html_wrapper.HTMLWrapper()
    ciphertext = "</pre> foobar < \" & <> = <b> <pre> </bloop>"
    assert ciphertext == wrapper.unwrap(wrapper.wrap(ciphertext))

def test_long_string():
    wrapper = html_wrapper.HTMLWrapper()
    ciphertext = 'a' * 1024
    assert ciphertext == wrapper.unwrap(wrapper.wrap(ciphertext))