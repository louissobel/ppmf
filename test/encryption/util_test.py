"""
unit test for encryption utils
"""
import unittest

from encryption import util

## chunks_of
class AlignedChunksTestCase(unittest.TestCase):

    def runTest(self):
        self.assertEqual(
            [
                ('abc', False),
                ('def', False),
                ('ghi', True)
            ],
            list(util.chunks_of(
                'abcdefghi',
                size=3,
            ))
        )


class UnalignedChunksTestCase(unittest.TestCase):

    def runTest(self):
        self.assertEqual(
            [
                ('abc', False),
                ('de', True),
            ],
            list(util.chunks_of(
                'abcde',
                size=3,
            ))
        )

class ShortUnalignedChunksTestCase(unittest.TestCase):

    def runTest(self):
        self.assertEqual(
            [
                ('ab', True),
            ],
            list(util.chunks_of(
                'ab',
                size=3,
            ))
        )

class ShortAlignedChunksTestCase(unittest.TestCase):

    def runTest(self):
        self.assertEqual(
            [
                ('abc', True),
            ],
            list(util.chunks_of(
                'abc',
                size=3,
            ))
        )

class EmptyChunksTestCase(unittest.TestCase):

    def runTest(self):
        self.assertEqual(
            [],
            list(util.chunks_of('', size=3))
        )


## pkcs7_pad
class BlockAlignedNecessaryTestCase(unittest.TestCase):

    def runTest(self):
        s = '\x08' * 15
        res = util.pkcs7_pad(s, 15)
        self.assertEqual(len(res), 30)
        self.assertEqual(s + '\x0F' * 15, res)


class SomePaddingRequiredTestCase(unittest.TestCase):

    def runTest(self):
        s = '\x00' * (8 * 15 + 8)
        res = util.pkcs7_pad(s, 15)
        self.assertEqual(len(res), 9 * 15)
        self.assertEqual(res[-7:], '\x07' * 7)
        self.assertEqual(res[:-7], s)


class EmptyStringTestCase(unittest.TestCase):

    def runTest(self):
        s = ''
        res = util.pkcs7_pad(s, 15)
        self.assertEqual(len(res), 15)
        self.assertEqual(res, '\x0F' * 15)


## pkcs7_unpad
class FullStringUnpad(unittest.TestCase):

    def runTest(self):
        s = chr(18) * 18
        res = util.pkcs7_unpad(s)
        self.assertEqual(res, '')


class PartialStringUnpad(unittest.TestCase):

    def runTest(self):
        s = 'hello there!'
        s_p = s + chr(67) * 67
        res = util.pkcs7_unpad(s_p)
        self.assertEqual(res, s)


class BadString(unittest.TestCase):

    def runTest(self):
        s = chr(67) * 45 # not enough!
        with self.assertRaises(ValueError):
            util.pkcs7_unpad(s)


class EmptyString(unittest.TestCase):

    def runTest(self):
        with self.assertRaises(ValueError):
            util.pkcs7_unpad('')
