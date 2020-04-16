from typing import *
import re

__all__ = ("PageRange", "PdfSlice")

RangePattern = Union[Tuple[Optional[int], Optional[int]], int]


class PageRange(Iterable[int]):
    """
    表示一个页码范围，可以用迭代的方式遍历可选的数字。
    可以用来表示无穷区间。

    :param str r: 用字符串表示的范围，闭区间

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

    def __init__(self, r: str):
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
                if b is None and e is None:
                    i = 0
                    while True:
                        yield i
                        i += 1
                elif b is None:
                    i = 0
                    while i <= e:
                        yield i
                        i += 1
                elif e is None:
                    i = b
                    while True:
                        yield i
                        i += 1
                else:
                    i = b
                    while i <= e:
                        yield i
                        i += 1


class PdfSlice:
    pdf: str
    page_range: PageRange
