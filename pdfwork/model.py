from typing import *
import re

__all__ = ("PageRange", "PdfSlice")

RangePattern = Union[Tuple[Optional[int], Optional[int]], int]


class PageRange(Iterable[int]):
    """
    表示一个页码范围，可以用迭代的方式遍历可选的数字。
    可以用来表示无穷区间。

    :param str r: 用字符串表示的范围，闭区间
    :param Optional[int] max: 最大的迭代值，如果设置为 None 则为无限

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
    maxn: Optional[int]

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
                    while i <= e:
                        yield i
                        i += 1


class PdfSlice:
    pdf: str
    page_range: PageRange
