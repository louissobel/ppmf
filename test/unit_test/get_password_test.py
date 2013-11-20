"""
tests the testing mode of get_password

not ideal.
"""
import os

import get_password


def test_get_password():
    os.environ['TEST_CRYPTBOXFS'] = 'yes'
    password = "dsjflsdjflkjheheh"
    os.environ['TEST_CRYPTBOXFS_PASSWORD'] = password

    assert password == get_password.get_password('testing')
