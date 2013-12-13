"""
Tests that is is working __basically__
"""
import tempfile
import subprocess
import shutil
import os
import os.path
import time
import signal
import random
import unittest
import errno

from nose.tools import nottest

import cryptboxfs
import file_content
from config_file_manager import CredentialConfigManager

class TestCryptbox(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        """
         - create a mount dir
         - create a mirror dir
         - set environment vars for fs testing
         - mount the fs in another process
        """
        cls.mirror_dir = tempfile.mkdtemp()
        cls.mount_point = tempfile.mkdtemp()
        cls.config_file = "cryptbox_test_config.json"
        cls.key_file = "cryptbox_test_keys.json"
        cls.credentials = CredentialConfigManager(cls.mirror_dir, cls.config_file, cls.key_file)

        cryptbox_path =  cryptboxfs.__file__
        cls.fs_process = subprocess.Popen(['python', cryptbox_path, cls.mirror_dir, cls.mount_point, cls.config_file, cls.key_file])

        # janky give it time to mount
        time.sleep(1)

    @classmethod
    def teardown_class(cls):
        """
         - kill the process
         - remove directories
        """
        cls.fs_process.send_signal(signal.SIGINT)
        cls.fs_process.wait()

        shutil.rmtree(cls.mount_point)
        shutil.rmtree(cls.mirror_dir)

    def setUp(self):
        """
        runs before each test
        makes sure the file system is still running!

        clear out the directory,
        assert that listing it returns nothing
        """
        res = self.fs_process.poll()
        if res is not None:
            raise AssertionError("Filesystem shutdown! Exit code %d" % res)

        for node in os.listdir(self.mirror_dir):
            full_path = os.path.join(self.mirror_dir, node)
            if os.path.isfile(full_path):
                os.unlink(full_path)
            else:
                shutil.rmtree(full_path)

        expected_contents = [cryptboxfs.ENCRYPTION_PREFIX]
        self.assertListEqual(os.listdir(self.mount_point), expected_contents, "Mount Point not empty after being cleared!")

    def write_file(self, path, contents):
        with open(path, 'w') as f:
            f.write(contents)
            f.close()

    def read_file(self, path):
        with open(path, 'r') as f:
            return f.read()

    def get_encrypted(self, message, filename):
        creds = self.credentials.file_creds_for(filename)
        return file_content.UnencryptedContent(message, filename=filename).encrypt(**creds).value()

    def get_decrypted(self, message, filename):
        creds = self.credentials.file_creds_for(filename)
        return file_content.EncryptedContent(message).decrypt(**creds).value()

    def test_write_read(self):
        """
        makes sure I can write to the mount point
        and read back the same thing
        """
        path = os.path.join(self.mount_point, 'foobar_writeread')

        message = 'bloop doop $823- 19 \n\t2308 sdli2\d2083\ds\x03'
        self.write_file(path, message)
        self.assertEqual(self.read_file(path), message)

    def test_write_over_existing_file(self):
        """
        checks that overwriting existing file works
        """
        filename = 'floop_write_over_existing'
        path = os.path.join(self.mount_point, filename)
        self.write_file(path, 'ok')

        message = 'hehe'
        self.write_file(path, message)
        self.assertEqual(self.read_file(path), message)

    def test_write_over_existing_file_shorter(self):
        """
        checks that overwriting existing file with shorter content works
        """
        filename = 'floop_write_over_existing_shorter'
        path = os.path.join(self.mount_point, filename)
        self.write_file(path, 'okokokok')

        message = 'hehe'
        self.write_file(path, message)
        self.assertEqual(self.read_file(path), message)

    def test_append_to_existing_file(self):
        """
        checks that overwriting existing file works
        """
        filename = 'floop_append_to_existing'
        path = os.path.join(self.mount_point, filename)
        self.write_file(path, 'ok')

        message = 'hehe'
        with open(path, 'a') as f:
            f.write(message)

        self.assertEqual(self.read_file(path), 'ok' + message)

    def test_write_read_encrypted(self):
        """
        make sure that reading from the
        encrypted prefix gives an encrypted result
        """
        message = "Well hello."
        filename = 'test_write_read_encrypted'

        path = os.path.join(self.mount_point, filename)
        self.write_file(path, message)

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)
        cipher_text = self.read_file(encrypted_path)
        decrypted = self.get_decrypted(cipher_text, filename)

        self.assertEqual(message, decrypted)

    def test_write_read_encrypted_using_config(self):
        """
        make sure that reading from the
        encrypted prefix gives an encrypted result
        """
        message = "Well hello!!!!!!!"
        filename = 'test_using_config.html' # this filename has a special password in the config

        path = os.path.join(self.mount_point, filename)
        self.write_file(path, message)

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)
        cipher_text = self.read_file(encrypted_path)
        decrypted = self.get_decrypted(cipher_text, filename)

        self.assertEqual(message, decrypted)

    def test_listdir_root(self):
        """
        test listdir /
        """
        files = ['bloop_lsroot', 'doop_lsroot', 'dap_lsroot']
        for filename in files:
            path = os.path.join(self.mount_point, filename)
            self.write_file(path, 'ok')

        self.assertItemsEqual(os.listdir(self.mount_point), files + [cryptboxfs.ENCRYPTION_PREFIX])

    def test_listdir_encrypted(self):
        """
        test listdir /__enc__
        """
        files = ['bloop_lsenc', 'doop_lsenc', 'dap_lsenc']
        for filename in files:
            path = os.path.join(self.mount_point, filename)
            self.write_file(path, 'ok')

        self.assertItemsEqual(os.listdir(os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX)), files)

    def test_stat(self):
        """
        stat should return real size
        """
        size = random.randint(300, 500)
        message = 'x' * size
        path = os.path.join(self.mount_point, 'test_stat')
        self.write_file(path, message)

        st = os.lstat(path)
        self.assertEqual(st.st_size, size)

    def test_stat_encrypted(self):
        """
        stat on enrypted file should size of the encrypted file
        """
        size = random.randint(100, 250)
        message = 'x' * size
        filename = 'test_stat_enc.txt'
        path = os.path.join(self.mount_point, filename)
        self.write_file(path, message)

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)
        st = os.lstat(encrypted_path)
        self.assertEqual(st.st_size, len(self.get_encrypted(message, filename)))

    def test_unlink(self):
        """
        test deleting a file
        """
        filename = 'deleteme_unlink'
        path = os.path.join(self.mount_point, filename)
        self.write_file(path, 'bah bah bah')

        os.unlink(path)

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)
        real_path = os.path.join(self.mirror_dir, filename)

        self.assertFalse(os.path.exists(path))
        self.assertFalse(os.path.exists(encrypted_path))
        self.assertFalse(os.path.exists(real_path))

    def test_enc_create_fail(self):
        """
        creaeting a enc file should fail with EROFS
        """
        filename = 'bloop_enc_create_fail'
        path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)

        with self.assertRaises(OSError) as cm:
            os.open(path, os.O_CREAT)
        self.assertEqual(cm.exception.errno, errno.EROFS)

    def test_enc_write_fail(self):
        """
        writing to an enc fd should fail with EROFS
        """
        filename = 'bloop_enc_write_fail'
        path = os.path.join(self.mount_point, filename)
        self.write_file(path, 'ok')

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)
        fd = os.open(encrypted_path, os.O_WRONLY)

        with self.assertRaises(OSError) as cm:
            os.write(fd, 'NO NO NO')
        self.assertEqual(cm.exception.errno, errno.EROFS) # read only filesystem

    def test_enc_truncate_fail(self):
        """
        trying to truncate an enc fd should fail with EROFS
        """
        filename = 'bloop_enc_truncate_fail'
        path = os.path.join(self.mount_point, filename)
        self.write_file(path, 'ok')

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)
        fd = os.open(encrypted_path, os.O_WRONLY)

        with self.assertRaises(OSError) as cm:
            os.ftruncate(fd, 0)
        self.assertEqual(cm.exception.errno, errno.EROFS)

    def test_enc_unlink_fail(self):
        """
        do not permit delete
        """
        filename = 'bloop_enc_unlink_fail'
        path = os.path.join(self.mount_point, filename)
        self.write_file(path, 'ok')

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)

        with self.assertRaises(OSError) as cm:
            os.remove(encrypted_path)
        self.assertEqual(cm.exception.errno, errno.EROFS)

    def test_appending(self):
        """
        opening a file in append mode should work...
        """
        filename = 'bloop_appending'
        path = os.path.join(self.mount_point, filename)

        # open for appending
        fd = os.open(path, os.O_RDWR | os.O_APPEND | os.O_CREAT)
        os.write(fd, 'ABC'*10000)
        os.lseek(fd, 0, os.SEEK_SET)

        os.write(fd, '123'*10000)
        os.lseek(fd, 0, os.SEEK_SET)

        val = os.read(fd, (3 * 10000) * 2)
        self.assertEqual(val, 'ABC' * 10000 + '123'*10000)

    def test_open_notexist_file(self):
        """
        trying to open a file that does not exist should through an OS ENOENT err
        """
        filename = 'idontexist'
        path = os.path.join(self.mount_point, filename)

        with self.assertRaises(OSError) as cm:
            os.open(path, os.O_RDONLY)
        self.assertEqual(cm.exception.errno, errno.ENOENT)

    def test_open_notexist_enc_file(self):
        """
        trying to open a file through __enc__ should throw an error
        if that file does not exist
        """
        filename = 'idontexist_enc'
        path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)

        with self.assertRaises(OSError) as cm:
            os.open(path, os.O_RDONLY)
        self.assertEqual(cm.exception.errno, errno.ENOENT)

    def test_fsync(self):
        """
        fsync!
        """
        filename = 'test_fsync.txt'
        path = os.path.join(self.mount_point, filename)
        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)

        message = 'hi hi hi hello there'
        fh = open(path, 'w')
        fh.write(message)
        fh.flush()
        os.fsync(fh.fileno())

        # read encrypted... after decryption it should match message
        cipher_text = self.read_file(encrypted_path)
        decrypted = self.get_decrypted(cipher_text, filename)

        self.assertEqual(decrypted, message)

    def test_flush(self):
        """
        flush
        """
        filename = 'test_flush.txt'
        path = os.path.join(self.mount_point, filename)

        message = 'yippee yippee'
        fh = open(path, 'w')
        fh2 = open(path, 'r')

        fh.write(message)
        fh.flush()

        fh3 = open(path, 'r')

        self.assertEqual(fh2.read(), message)
        self.assertEqual(fh3.read(), message)
