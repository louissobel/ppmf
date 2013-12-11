"""
basic checks on an html_wrapper roundtrip
"""
import html_wrapper

def test_roundtrip():
    ciphertext = "sdfkjl 3209oij \x03 sdlfkj \x34 dlfkj FOOBAR wekhj lalal pooop"
    assert ciphertext == html_wrapper.unwrap(html_wrapper.wrap(ciphertext))

def test_roundtrip_html_entities():
    ciphertext = "</pre> foobar < \" & <> = <b> <pre> </bloop>"
    assert ciphertext == html_wrapper.unwrap(html_wrapper.wrap(ciphertext))
