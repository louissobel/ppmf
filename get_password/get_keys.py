"""
get personal public or private key
this only has test key pair for now
"""
import sys
import os

import using_test

def get_public_key():
    if os.environ.get('TEST_CRYPTBOXFS') is not None:
    	return using_test.get_public_key()

def get_private_key():
    if os.environ.get('TEST_CRYPTBOXFS') is not None:
    	return using_test.get_private_key()