from file_content import EncryptedContent, UnencryptedContent

def test_roundtrip():
    message = "blooper dooper deepy doo"
    password = "he haw"
    mime = 'text/plain'

    unc = UnencryptedContent(message, mime)
    res = unc.encrypt(password=password).decrypt(password=password)
    assert unc.mimetype == res.mimetype
    assert unc.plaintext == res.plaintext