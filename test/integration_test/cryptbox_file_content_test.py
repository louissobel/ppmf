from cryptbox_file_content import EncryptedContent, UnencryptedContent

def test_roundtrip():
    message = "blooper dooper deepy doo"
    password = "he haw"
    unc = UnencryptedContent(message)
    assert message == unc.encrypt(password).decrypt(password).value()
