"""
if testing, just return the set environment variable
"""
import os

def get_password(forwhat):
    return os.environ.get('TEST_CRYPTBOXFS_PASSWORD')
