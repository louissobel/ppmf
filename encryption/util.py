"""
utilites for crypto
"""
import itertools

def pkcs7_pad(string, block_size):
    """
    adds PKCS7 padding
    http://en.wikipedia.org/wiki/Padding_(cryptography)#PKCS7
    """
    padding_length = block_size - (len(string) % block_size)
    return string + chr(padding_length) * padding_length

def pkcs7_unpad(string):
    """
    removes PKCS padding
    http://en.wikipedia.org/wiki/Padding_(cryptography)#PKCS7
    """
    print "string", string
    if not string:
        raise ValueError('Cannot unpad empty string!')

    padding_length = ord(string[-1])
    if padding_length > len(string):
        raise ValueError('Padding length %d is longer than string %d' % (
            padding_length,
            len(string),
        ))

    return string[:-padding_length]

def chunks_of(string, size):
    """
    returns tuples of chunks of size bytes from string, and whether that
    chunk is the last one that will be yielded
    last one may be less than size bytes

    chunks_of('abcdef', size=3) --> [('abc', False), ('def', True)]
    """
    iterator = iter(string)
    buf = None
    while True:
        value = ''.join(itertools.islice(iterator, size))

        if not value:
            # the end
            if buf is not None:
                yield buf, True
            raise StopIteration

        else:
            if buf is not None:
                yield buf, False
            buf = value
