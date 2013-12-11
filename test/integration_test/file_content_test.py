from file_content import EncryptedContent, UnencryptedContent
from Crypto.PublicKey import RSA


def test_roundtrip_no_keys():
    message = "blooper dooper deepy doo"
    password = "he haw"
    unc = UnencryptedContent(message)
    assert message == unc.encrypt(password).decrypt(password).value()

def test_roundtrip_with_key():
    message = "blooper dooper deepy doo"
    password = "he haw"
    new_key = RSA.generate(2048, e=65537)
    public_key, private_key = new_key.publickey().exportKey("PEM"), new_key.exportKey("PEM") 
    unc = UnencryptedContent(message)

    assert message == unc.encrypt(password, [public_key]).decrypt(rsa_key_pair=(public_key, private_key)).value()

def test_roundtrip_with_key_incorrect_pw():
    message = "blooper dooper deepy doo"
    password, wrong_password = "he haw", "bloooop"
    new_key = RSA.generate(2048, e=65537)
    public_key, private_key = new_key.publickey().exportKey("PEM"), new_key.exportKey("PEM") 
    unc = UnencryptedContent(message)

    assert message == unc.encrypt(password, [public_key]).decrypt(password=wrong_password, rsa_key_pair=(public_key, private_key)).value()
