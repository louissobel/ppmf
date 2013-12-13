from file_content import EncryptedContent, UnencryptedContent
from Crypto.PublicKey import RSA


def test_roundtrip_no_keys():
    message = "blooper dooper deepy doo"
    password = "he haw"
    unc = UnencryptedContent(message)
    assert message == unc.encrypt(password=password).decrypt(password=password).value()

def test_roundtrip_with_key():
    message = "blooper dooper deepy doo"
    password = "he haw"
    new_key = RSA.generate(2048, e=65537)
    public_key, private_key = new_key.publickey().exportKey("PEM"), new_key.exportKey("PEM") 
    unc = UnencryptedContent(message)

    assert message == unc.encrypt(password=password, public_keys=[public_key]).decrypt(password=password).value()