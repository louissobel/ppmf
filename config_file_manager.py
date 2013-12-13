import json
import getpass
import os
from encryption import rsa

NONENCRYPTED_FILES = [
    '.xdg-volume-info', 
    'autorun.inf',
]

class CredentialConfigManager(object):
    """
    parses config and key files for info about files
    
    CONFIG FILE
    {
        default_password : used if per-file password or key pair can't be,
        files : {
            file_pathname : {
                password : aes key,
                public_keys : list of public keys to encrypt with, excluding own
            }
        }
    }
    KEY FILE
    {
        public: public key,
        private: private key,
    }
    """
    def __init__(self, root, config_pathname, rsa_key_pathname):
        self.config_pathname = config_pathname
        self.rsa_key_pathname = rsa_key_pathname
        self.read_config_and_key_file()

    def read_config_and_key_file(self):
        with open(self.config_pathname, 'r') as f:
            config_contents = f.read()

        with open(self.rsa_key_pathname, 'r') as f:
            key_contents = f.read()

        self.config, self.keys = json.loads(config_contents), json.loads(key_contents)

    def write_config_file(self):
        config_json = json.dumps(self.config)
        with open(self.config_pathname, 'w') as f:
            f.write(config_json)

    def file_creds_for(self, path):
        return {
            "default_password" : self.get_default_password(),
            "password" : self.get_password_for(path),
            "passwords" : self.get_passwords_for(path),
            "public_keys" : self.get_public_keys_for(path),
        }

    def create_file_creds_for(self, relative_path):
        #overwrites a file if already there
        self.config["files"][relative_path] = {
            "public_keys" : [self.get_public_key()],
        }
        # ehhh this also writes to config file
        self.set_password_for(relative_path)
        return self.config["files"][relative_path]

    def get_public_key(self):
        return self.keys.get("public").replace('\\n', '\n')

    def get_private_key(self):
        return self.keys.get("private").replace('\\n', '\n')

    def get_default_password(self):
        return self.config["default_password"].encode('utf-8')

    def get_files(self):
        return self.config["files"]


    def get_password_for(self, cryptbox_pathname):
        """
        returns decrypted password for cryptbox_pathname file if own public key was found
        else returns None
        """
        file_config = self.config.get('files').get(cryptbox_pathname, {})
        if "passwords" not in file_config:
            return self.get_default_password() 

        fingerprint = rsa.get_fingerprint(self.get_public_key())
        encrypted_password = file_config["passwords"].get(fingerprint)
        if encrypted_password is None:
            return None

        #ascii errors were thrown without encoding with utf8?
        return rsa.decrypt(encrypted_password, self.get_private_key()).encode('utf-8')

    def get_passwords_for(self, cryptbox_pathname):
        """
        returns encrypted passwords, based on the public_keys for cryptbox_pathname
        """
        file_config = self.get_files().get(cryptbox_pathname, {})
        if "passwords" not in file_config: 
            return None
        return file_config.get("passwords")

    def get_public_keys_for(self, cryptbox_pathname):
        """
        return list of public keys for sharing, the identities authorized to the file
        includes own public key
        """
        file_config = self.config.get('files').get(cryptbox_pathname, {})
        return file_config.get("public_keys", [])

    def set_password_for(self, cryptbox_pathname, password=None):
        #prompt in terminal for password
        #i don't know why this is asking for a password twice...
        if password is None:
            password = self.get_default_password()

        passwords = self.encrypt_passwords(password, self.get_public_keys_for(cryptbox_pathname))

        if cryptbox_pathname in self.config["files"]:
            file_config = self.config.get('files')[cryptbox_pathname]
        else:
            file_config = self.create_file_creds_for(cryptbox_pathname)

        file_config["passwords"] = passwords
        self.config["files"][cryptbox_pathname] = file_config

        self.write_config_file()

    def set_public_keys_for(self, cryptbox_pathname, public_keys):
        public_key = self.get_public_key()
        if public_key not in public_keys:
            public_keys.append(public_key)

        password = self.get_password_for(cryptbox_pathname)
        passwords = self.encrypt_passwords(password, public_keys)

        self.config["files"][cryptbox_pathname] = {
            "public_keys" : public_keys,
            "passwords" : passwords,
        }
        self.write_config_file()

    def add_public_key_for(self, cryptbox_pathname, public_key, add):
        keys = self.get_public_keys_for(cryptbox_pathname)
        if add:
            if public_key not in keys:
                keys.append(public_key)
        else:
            if public_key in keys:
                keys.remove(public_key)
        self.set_public_keys_for(cryptbox_pathname, keys)

    def encrypt_passwords(self, password, public_keys):
        passwords = {}
        for public_key in public_keys:
            passwords[rsa.get_fingerprint(public_key)] = rsa.encrypt(password, public_key)
        return passwords

    def set_new_rsa_keypair(self):
        self.keys = {}
        self.keys["private"], self.keys["public"] = rsa.generate_keypair()
        with open(self.rsa_key_pathname, 'w') as f:
            f.write(json.dumps(self.keys))

    def set_default_password(self, password):
        self.config["default_password"] = password
        self.write_config_file()
   

if __name__ == '__main__':
    import sys
    root, config_pathname, keys_pathname, cryptbox_pathname = sys.argv[1:5]
    if sys.argv[5] == '--set-password':
        #this also creates a file cred object for the pathname if needed
        password = getpass.getpass().encode('utf-8')
        CredentialConfigManager(root, config_pathname, keys_pathname).set_password_for(cryptbox_pathname, password)
    if sys.argv[5] == '--add-key' or '--delete-key':
        try:
            key = sys.argv[6]
        except IndexError:
            print "must specify public key"

        add = sys.argv[5] == '--add-key'    
        CredentialConfigManager(root, config_pathname, keys_pathname).set_public_key_for(cryptbox_pathname, key, add)

