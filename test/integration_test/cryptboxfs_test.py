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

from nose.tools import nottest

import cryptboxfs
import cryptbox_files

TEST_PASSWORD = 'password123'

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

        cryptbox_path =  cryptboxfs.__file__
        os.environ['TEST_CRYPTBOXFS'] = 'True'
        os.environ['TEST_CRYPTBOXFS_PASSWORD'] = TEST_PASSWORD
        cls.fs_process = subprocess.Popen(['python', cryptbox_path, cls.mirror_dir, cls.mount_point])

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

    def get_encrypted(self, message):
        return cryptbox_files.UnencryptedFile(message).encrypt(TEST_PASSWORD).contents()

    def test_write_read(self):
        """
        makes sure I can write to the mount point
        and read back the same thing
        """
        path = os.path.join(self.mount_point, 'foobar')

        message = 'bloop doop $823- 19 \n\t2308 sdli2\d2083\ds\x03'
        self.write_file(path, message)
        self.assertEqual(self.read_file(path), message)

    def test_write_read_encrypted(self):
        """
        make sure that reading from the
        encrypted prefix gives an encrypted result
        """
        message = "Well hello."
        filename = 'test.txt'

        path = os.path.join(self.mount_point, filename)
        self.write_file(path, message)

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)
        cipher_text = self.read_file(encrypted_path)
        expected = self.get_encrypted(message)
        self.assertEqual(cipher_text, expected)

    def test_listdir_root(self):
        """
        test listdir /
        """
        files = ['bloop', 'doop', 'dap']
        for filename in files:
            path = os.path.join(self.mount_point, filename)
            self.write_file(path, 'ok')

        self.assertItemsEqual(os.listdir(self.mount_point), files + [cryptboxfs.ENCRYPTION_PREFIX])

    def test_listdir_encrypted(self):
        """
        test listdir /__enc__
        """
        files = ['bloop', 'doop', 'dap']
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
        path = os.path.join(self.mount_point, 'test')
        self.write_file(path, message)

        st = os.lstat(path)
        self.assertEqual(st.st_size, size)

    def test_stat_encrypted(self):
        """
        stat on enrypted file should size of the encrypted file
        """
        size = random.randint(100, 250)
        message = 'x' * size
        path = os.path.join(self.mount_point, 'test')
        self.write_file(path, message)

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, 'test')
        st = os.lstat(encrypted_path)
        self.assertEqual(st.st_size, len(self.get_encrypted(message)))

    def test_unlink(self):
        """
        test deleting a file
        """
        filename = 'deleteme'
        path = os.path.join(self.mount_point, filename)
        self.write_file(path, 'bah bah bah')

        os.unlink(path)

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)
        real_path = os.path.join(self.mirror_dir, filename)

        self.assertFalse(os.path.exists(path))
        self.assertFalse(os.path.exists(encrypted_path))
        self.assertFalse(os.path.exists(real_path))
