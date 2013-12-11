import json
import os

class CredentialConfigManager(object):
    """
    parses .config file in root for info about files
    
    {
        personal_keys: {
            public: public key,
            private: private key,
        },

        files : {
            file_pathname : {
                password : aes key,
                public_keys : list of public keys to encrypt with, excluding own
            }
        }
    }
    """
    def __init__(self, root, config_pathname):
        self.root = root
        self.pathname = config_pathname
        self.refresh_config_file()

    def parse_config_file(self, contents):
        """
        reads in above json object. also can be used to refresh
        todo: when to refresh? ask louis, but for now just do it before every get call
        """
        config = json.loads(contents)

        self.public_key, self.private_key = None, None
        keys = config.get("personal_keys", None)
        if keys is not None:
            self.public_key, self.private_key = keys["public"], keys["private"]

        self.default_password = config["default_password"]
        self.files = config.get("files", {})

    def refresh_config_file(self):
        with open(self.pathname, 'r') as f:
            config_contents = f.read()
        self.parse_config_file(config_contents)

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key

    def get_default_password(self):
        return self.default_password

    def get_password_for(self, cryptbox_pathname):
        """
        returns password for a given pathname if there is one
        but public/private keys should always be tried first
        """
        cryptbox_pathname = self._get_cryptbox_filename(cryptbox_pathname)
        file_config = self.files.get(cryptbox_pathname, {})
        return file_config.get("password", None)

    def get_public_keys_for(self, cryptbox_pathname):
        """
        return list of public keys for sharing, the identities authorized to the file
        """
        cryptbox_pathname = self._get_cryptbox_filename(cryptbox_pathname)
        file_config = self.files.get(cryptbox_pathname, {})
        return file_config.get("public_keys", [])

    def _get_cryptbox_filename(self, cryptbox_pathname):
        """
        takes off root path
        """
        return cryptbox_pathname.split(self.root)[1]