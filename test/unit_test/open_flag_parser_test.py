"""
tests open flag parser
"""
import os

from open_flag_parser import parse

def test_rdonly():
    val = os.O_RDONLY
    res = parse(val)
    assert res.read is True
    assert res.write is False

def test_wronly():
    val = os.O_WRONLY
    res = parse(val)
    assert res.read is False
    assert res.write is True

def test_rdwr():
    val = os.O_RDWR
    res = parse(val)
    assert res.read is True
    assert res.write is True

def test_mask():
    val = (0xFF << 2) | os.O_WRONLY
    res = parse(val)

    assert res.read is False
    assert res.write is True
