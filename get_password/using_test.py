"""
if testing, just return the set environment variable
"""
import os

def get_password(forwhat):
    return os.environ.get('TEST_CRYPTBOXFS_PASSWORD')

def get_public_key():
	with open('public_key', 'r') as f:
		return f.read()

def get_private_key():
	with open('private_key', 'r') as f:
		return f.read()