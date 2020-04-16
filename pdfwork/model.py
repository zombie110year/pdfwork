import re
from io import SEEK_SET
from io import BytesIO
from pathlib import Path
from typing import *

from PyPDF2.pdf import PdfFileReader
from PyPDF2.pdf import PageObject

from .utils import export_outline

__all__ = ("PageRange", "PdfSlice", "InfiniteInteger")

RangePattern = Union[Tuple[Optional[int], Optional[int]], int]


class InfiniteInteger(Exception):
    pass


class PageRange(Iterable[int]):
    """
    表示一个页码范围，可以用迭代的方式遍历可选的数字。
    可以用来表示无穷区间。

    :param str r: 用字符串表示的范围，闭区间
    :param Optional[int] max: 最大的迭代值，如果设置为 None 则为无限

    可以对其进行迭代，得到页码范围内的每一位数字；
    也可以计算它的长度，如果无限长，会抛出 :exc:`InfiniteInteger` 异常。

    >>> pr = PageRange("-3,16-17,200-")
    >>> next(pr)
    0
    >>> next(pr)
    1
    >>> next(pr)
    2
    >>> next(pr)
    3
    >>> next(pr)
    16
    >>> next(pr)
    17
    >>> next(pr)
    200
    >>> next(pr)
    201
    >>> # 无穷...
    """
    RE_ITEM = re.compile(r"-|\d+|\d+-|-\d+|\d+-\d+")
    RE_RANGE = re.compile(r"(-|\d+|\d+-|-\d+|\d+-\d+)(,\d+|\d+-|-\d+|\d+-\d+)*")
    ranges: Optional[List[RangePattern]] = None
    maxn: Optional[int] = None

    def __init__(self, r: str, max=None):
        self.maxn = max
        if self.RE_RANGE.match(r):
            ranges = (tuple(i.split("-")) for i in (x for x in r.split(",") if x != ""))
            self.ranges = []
            for t in ranges:
                if len(t) == 1:
                    self.ranges.append(int(t[0]))
                elif len(t) == 2:
                    if t == ("", ""):
                        pat = (None, None)
                    elif t[0] == "":
                        pat = (None, int(t[1]))
                    elif t[1] == "":
                        pat = (int(t[0]), None)
                    else:
                        pat = (int(t[0]), int(t[1]))
                    self.ranges.append(pat)
        else:
            raise SyntaxError(f"{repr(r)}")

    def __iter__(self):
        return self.iter_numbers()

    def iter_numbers(self) -> Iterator[int]:
        for pat in self.ranges:
            if isinstance(pat, int):
                yield pat
            elif isinstance(pat, tuple):
                b, e = pat
                if e is None:
                    i = b if b is not None else 0
                    if self.maxn is None:
                        while True:
                            yield i
                            i += 1
                    else:
                        while i <= self.maxn:
                            yield i
                            i += 1
                else:
                    i = b if b is not None else 0
                    end = min(e, self.maxn) if self.maxn is not None else e
                    while i <= end:
                        yield i
                        i += 1

    def __len__(self) -> int:
        return self.get_length()

    def get_length(self) -> int:
        """计算长度

        :exc InfiniteInteger: 当此页码范围拥有无限的长度时。
        """
        length = 0
        for pat in self.ranges:
            if isinstance(pat, int):
                length += 1
            elif isinstance(pat, tuple):
                b, e = pat
                if b is None and e is None:
                    if self.maxn is None:
                        raise InfiniteInteger
                    else:
                        length += self.maxn + 1
                elif b is None and e is not None:
                    length += e + 1
                elif b is not None and e is None:
                    if self.maxn is None:
                        raise InfiniteInteger
                    else:
                        length += self.maxn - b + 1
                else:
                    length += e - b + 1
        return length


class VirtualPdfSlice:
    """一个虚拟的 PDF 片段，不假设在文件系统中存在对应文件

    :param str pdf: 假设的 PDF 文件路径
    :param str pr: PageRange
    :param Optional[int] max: 最大页数

    >>> vps = VirtualPdfSlice("<memory>", "2,3,5,7,11-13")
    >>> vps.view_slice()
    [
        "<memory>:2",
        "<memory>:3",
        "<memory>:5",
        "<memory>:7",
        "<memory>:11",
        "<memory>:12",
        "<memory>:13"
    ]
    """
    pdf: str
    page_range: PageRange

    def __init__(self, pdf: str, pr: str, max=None):
        self.pdf = pdf
        self.page_range = PageRange(pr, max)

    def view_slice(self) -> List[str]:
        return [f"{self.pdf}:{p}" for p in self.page_range]


class PdfSlice:
    """一个对应到文件系统的 PDF 片段

    :param BytesIO pdf: 假设的 PDF 文件路径
    :param str pr: PageRange
    """
    pdf: VirtualPdfSlice
    _stream: BytesIO

    def __init__(self, pdf: BytesIO, pr: str):
        self._stream = pdf
        pdfreader = PdfFileReader(self._stream)
        self.pdf = VirtualPdfSlice("<memory>", pr, pdfreader.getNumPages() - 1)

        self._stream.seek(SEEK_SET, SEEK_SET)
        del pdfreader

    def __iter__(self) -> Iterator[PageObject]:
        return self.iter_pages()

    def iter_pages(self) -> Iterator[PageObject]:
        pdfreader = PdfFileReader(self._stream)
        for p in self.pdf.page_range:
            yield pdfreader.getPage(p)

    # (level, title)
    def iter_outlines(self) -> Iterator[Optional[Tuple[int, str]]]:
        """迭代页码对应的页面上的书签，同一页的书签只会得到一个。
        若某个页面没有书签，那么得到 None。

        这是为了与 :meth:`iter_pages` 配合。
        """
        outlines = export_outline(self._stream)
        outline_query = {}
        for level, title, pn in outlines:
            outline_query[pn] = (level, title)

        for pn in self.pdf.page_range:
            yield outline_query.get(pn, None)
