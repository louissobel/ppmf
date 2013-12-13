import json
import getpass
import os
from encryption import rsa

class CredentialConfigManager(object):
    """
    parses .config file in root for info about files
    
    {
        personal_keys: {
            public: public key,
            private: private key,
        },
        default_password : used if per-file password or key pair can't be,
        files : {
            file_pathname : {
                password : aes key,
                public_keys : list of public keys to encrypt with, excluding own
            }
        }
    }

    .config should be instantiated with personal_keys, public/private key, default_password, empty files
    """
    def __init__(self, root, config_pathname):
        self.pathname = config_pathname
        self.refresh_config_file()

    def parse_config_file(self, contents):
        """
        reads in above json object. also can be used to refresh
        todo: when to refresh? ask louis, but for now just do it before every get call
        """
        self.config = json.loads(contents)

    def refresh_config_file(self):
        with open(self.pathname, 'r') as f:
            config_contents = f.read()
        self.parse_config_file(config_contents)

    def write_config_file(self):
        config_json = json.dumps(self.config)
        with open(self.pathname, 'w') as f:
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

    def get_public_key(self):
        keys = self.config.get("personal_keys")
        if keys is not None:
            return keys["public"].replace('\\n', '\n')

    def get_private_key(self):
        keys = self.config.get("personal_keys")
        if keys is not None:
            return keys["private"].replace('\\n', '\n')

    def get_default_password(self):
        return self.config["default_password"]

    def get_files(self):
        return self.config["files"]


    def get_password_for(self, cryptbox_pathname):
        """
        returns decrypted password for cryptbox_pathname file if own public key was found
        else returns None
        """
        file_config = self.config.get('files').get(cryptbox_pathname, {})
        if "passwords" not in file_config:
            return None

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

    def set_password_for(self, cryptbox_pathname):
        #prompt in terminal for password
        #i don't know why this is asking for a password twice...
        password = getpass.getpass()
        if password == "DEFAULT":
            password = self.get_default_password()
        passwords = self.encrypt_passwords(password, self.get_public_keys_for(cryptbox_pathname))

        if cryptbox_pathname in self.config["files"]:
            file_config = self.config.get('files')[cryptbox_pathname]
        else:
            file_config = {}

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

    def encrypt_passwords(self, password, public_keys):
        passwords = {}
        for public_key in public_keys:
            passwords[rsa.get_fingerprint(public_key)] = rsa.encrypt(password, public_key)
        return passwords

    def set_new_rsa_keypair(self):
        keys = self["personal_keys"]
        keys["private"], keys["public"] = rsa.generate_keypair()
        self.write_config_file()

    def set_default_password(self, password):
        self.config["default_password"] = password
        self.write_config_file()
   