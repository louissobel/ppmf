"""
Tests that is is working __basically__
"""
import tempfile
import subprocess
import shutil
import os
import os.path

import cryptboxfs
import cryptbox_files

TEST_PASSWORD = 'password123'

class TestCryptbox(object):

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

    @classmethod
    def teardown_class(cls):
        """
         - kill the process
         - remove directories
        """
        cls.fs_process.kill()
        cls.fs_process.wait()

        shutil.rmtree(cls.mount_point)
        shutil.rmtree(cls.mirror_dir)

    def setUp(self):
        """
        runs before each test
        makes sure the file system is still running!
        """
        res = self.fs_process.poll()
        if res is not None:
            raise AssertionError("Filesystem shutdown! Exit code %d" % res)

    def tearDown(self):
        """
        runs after each test
        clear out the directory,
        assert that listing it returns nothing
        """
        for node in os.listdir(self.mirror_dir):
            full_path = os.path.join(self.mirror_dir, node)
            if os.path.isfile(full_path):
                os.unlink(full_path)
            else:
                shutil.rmtree(full_path)

        assert os.listdir(self.mount_point) == [], "Mount Point not empty after being cleared!"

    def test_write_read(self):
        """
        makes sure I can write to the mount point
        and read back the same thing
        """
        path = os.path.join(self.mount_point, 'foobar')

        message = 'bloop doop $823- 19 \n\t2308 sdli2\d2083\ds\x03'
        with open(path, 'w') as f:
            f.write(message)
        with open(path, 'r') as f:
            assert f.read() == message

    def test_write_read_encrypted(self):
        """
        make sure that reading from the
        encrypted prefix gives an encrypted result
        """
        message = "Well hello."
        filename = 'test.txt'

        path = os.path.join(self.mount_point, filename)
        with open(path, 'w') as f:
            f.write(message)

        encrypted_path = os.path.join(self.mount_point, cryptboxfs.ENCRYPTION_PREFIX, filename)
        with open(path, 'r') as f:
            contents = f.read()
            expected = cryptbox_files.UnencryptedFile(message).encrypt(TEST_PASSWORD).contents()
            assert expected == contents
