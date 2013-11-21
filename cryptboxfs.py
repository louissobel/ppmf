"""
FUSE implementing decrypt on read
Encrypt on write
"""

import sys

import fuse

ENCRYPTION_PREFIX = '__enc__'

class CryptboxFS(fuse.Operations):
    """
    File System
    """

    def __init__(self, root):
        self.root = root


def main(root, mountpoint):
    return fuse.FUSE(CryptboxFS(root), mountpoint, foreground=True)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: %s <root> <mountpoint>' % sys.argv[0])
        sys.exit(1)

    fuse = main(sys.argv[1], sys.argv[2])
