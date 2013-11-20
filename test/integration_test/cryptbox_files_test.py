from cryptbox_files import EncryptedFile, UnencryptedFile

def test_roundtrip():
    message = "blooper dooper deepy doo"
    password = "he haw"
    unc = UnencryptedFile(message)
    assert message == unc.encrypt(password).decrypt(password).contents()
