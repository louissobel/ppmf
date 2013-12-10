"""
if testing, just return the set environment variable
public_key and private_key files can be used for rsa testing
"""
import os

def get_password(forwhat):
    return os.environ.get('TEST_CRYPTBOXFS_PASSWORD')

def get_public_key():
	with open('test_public_key', 'r') as f:
		return f.read()

def get_private_key():
	with open('test_private_key', 'r') as f:
		return f.read()