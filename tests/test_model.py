import pytest

from pdfwork.model import *


@pytest.mark.parametrize("r, e", [
    ("0", [0]),
    ("0-2", [0, 1, 2]),
    ("0,3", [0, 3]),
    ("0,1-2", [0, 1, 2]),
    ("0,3,4-5", [0, 3, 4, 5]),
    ("-2", [0, 1, 2]),
    ("-2,3", [0, 1, 2, 3]),
    ("-2,4-5", [0, 1, 2, 4, 5]),
])
def test_PageRange_common(r, e):
    pr = PageRange(r)
    for i, j in zip(pr, e):
        assert i == j


def test_PageRange_infinite0():
    pr = PageRange("-")
    for i, j in zip(pr, range(1000)):
        assert i == j


def test_PageRange_infinite1():
    pr = PageRange("300-")
    for i, j in zip(pr, range(300, 1000)):
        assert i == j


def test_PageRange_infinite2():
    pr = PageRange("-2,3,7-11,300-")
    it = iter(pr)
    assert next(it) == 0
    assert next(it) == 1
    assert next(it) == 2
    assert next(it) == 3
    assert next(it) == 7
    assert next(it) == 8
    assert next(it) == 9
    assert next(it) == 10
    assert next(it) == 11
    assert next(it) == 300
    assert next(it) == 301


@pytest.mark.parametrize("r, e", [
    ("9,3,6", [9, 3, 6]),
    ("1-,0", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0]),
])
def test_PageRange_mixed(r, e):
    pr = PageRange(r, max=10)
    for i, j in zip(pr, e):
        assert i == j


@pytest.mark.parametrize("r, length", [
    ("1,3,5,7,9", 5),
    ("2-7,11", 7),
    ("-3,5,8", 6),
])
def test_PageRange_len0(r, length):
    assert len(PageRange(r)) == length


@pytest.mark.parametrize("r, length", [
    ("-", 101),
    ("3,7,98-", 5),
])
def test_PageRange_len1(r, length):
    assert len(PageRange(r, max=100)) == length


@pytest.mark.parametrize("r", [
    "-",
    "1-",
    "1,2-",
])
def test_PageRange_len2(r):
    with pytest.raises(InfiniteInteger):
        len(PageRange(r))
