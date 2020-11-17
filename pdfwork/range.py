"""解析一个离散的区间

用 `,` 分隔各个部分，用 `:` 表示区间的两极，为了与 Python 的区间表示法保持一致， ``a:b`` 表示左闭右开区间 ``[a, b)``。

例如::

    # 单个组件
    1 => [1]
    1:3 => [1, 2]
    ## 可以附加步长
    1:10:2 => [1, 3, 5, 7, 9]
    ## 可以表示无穷区间
    1: => [1, 2, 3, ...]
    : => [...]
    # 多个组件
    1,2,3 => [1, 2, 3]
    ## 将会按照表示法的顺序迭代
    1,3,2 => [1, 3, 2]
    ## 不会合并区间
    3,2:4 => [3, 2, 3]
"""
import re
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Union


class RangeParseError(Exception):
    pass


__all__ = ("MultiRange", )


class MultiRange(Iterable):
    components: List[range]
    # 一次检查一个组件
    comp_chker = re.compile(
        r"(-?\d+)|(-?\d+)?:(-?\d+)?|(-?\d+)?:(-?\d+)?:(-?\d+)")

    def __init__(self, *repr: Iterable[Union[str, range, int]]):
        self.components = []
        for r in repr:
            if isinstance(r, str):
                for comp in re.split(r" *, *", r):
                    if self.comp_chker.fullmatch(comp):
                        comp_: range = parse_component(comp)
                        self.components.append(comp_)
                    else:
                        raise RangeParseError(
                            f"{comp!r} cann't represent a range")
            elif isinstance(r, range):
                self.components.append(r)
            elif isinstance(r, int):
                self.components.append(range(r, r + 1))
            else:
                raise ValueError(f"{r!r} is not str or range or int")

    def __iter__(self) -> Iterator[int]:
        return self.iter()

    def iter(self) -> Iterator[int]:
        for comp in self.components:
            yield from comp


def parse_component(pat: str) -> range:
    if m := re.fullmatch(r"-?\d+", pat):
        # 单个数字
        num = int(m[0])
        return range(num, num + 1)
    elif m := re.fullmatch(r"(-?\d+)?:(-?\d+)?", pat):
        start = int(m[1])
        stop = int(m[2])
        return range(start, stop)
    elif m := re.fullmatch(r"(-?\d+)?:(-?\d+)?:(-?\d+)", pat):
        start = int(m[1])
        stop = int(m[2])
        step = int(m[3])
        return range(start, stop, step)
    else:
        raise RangeParseError(f"{pat!r} cann't represent a range")
