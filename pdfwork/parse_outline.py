"""这个模块提供了解析大纲（Outline） 表示文本（大纲源码）的功能。
语法满足：

```
《标题》 @ 《页码》
```

的文本解析为 :class:`OutlineInfo` 对象，用于构建 :class:`OutlineTree`。

OutlineItem 语法
================

OutlineItem 的表示法可分为三个部分：

1. 缩进：用于表示当前大纲对象的层级
2. 标题：大纲的标题文本
3. 页码：大纲所跳转的逻辑页码。可以忽略，令解析器自动推导，在这种情况下会使用上一条大纲的页码。
    这里的页码只涉及逻辑页码，与物理页码的偏移是在 import_outline 模块处理的。
"""
import re

from dataclasses import dataclass
from typing import *

from .exceptions import OutlineParseError

__all__ = ("outline_encode", "outline_decode", "OutlineItem", "OutlineTree")


class OutlineItem:
    """一条大纲：

    + :param int indent: 此大纲的缩进级别，从 0 开始
    + :param str title: 大纲文本
    + :param int index: 对应的页码，需要解析为确定的整数
    """
    indent: int
    title: str
    index: int

    def __init__(self, indent: int, title: str, index: int):
        self.indent = indent
        self.title = title
        self.index = index

        self.__children = []

    def add_child(self, child: "OutlineItem"):
        self.__children.append(child)

    def __repr__(self) -> str:
        return f"OutlineItem({self.indent!r}, {self.title!r}, {self.index!r})"

class OutlineTree:
    """组合成树状结构的 OutlineItem 对象们。
    """
    root: OutlineItem

    def __init__(self, root: OutlineItem):
        self.root = root

    def encode(self) -> str:
        """将树编码为文本
        """
        raise NotImplementedError


@dataclass
class ParsingDebugInfo:
    """解析时的调试信息，精确到行。

    :param int linenum: 当前行号
    :param int lines: 源码的全部行数
    :param str text: 当前行内容
    :param str filepath: 当前处理的源码文件路径
    """
    linenum: int
    lines: int
    text: str


def outline_decode(text: str) -> OutlineTree:
    """解析大纲源码为大纲树
    """
    # 当前解析条目的缩进等级
    cur_indent: int = 0
    # 用于识别缩进的模式
    indent_pat: Optional[str] = None
    # 解析一行
    oi = parse_line
    raise NotImplementedError


def outline_encode(ot: OutlineTree) -> str:
    """将大纲树编码为源码表示，见 :meth:`OutlineTree.encode`。
    """
    return ot.encode()


def parse_line(
        line: str, indent_pat: Optional[str], last_index: int,
        dbg: Optional[ParsingDebugInfo]) -> Tuple[OutlineItem, Optional[str]]:
    """解析一行

    :param str line: 单行大纲源码文本
    :param Optional[str] indent_pat: 用于识别缩进的模式，如果为 None 则需要自动推导
    :param int last_index: 上条大纲的页码
    :param int dbg_linenum: 调试信息，当前处理的行号

    :returns: (OutlineItem, 识别出的缩进模式)

    行格式::

        <缩进> <标题> @ <页码>?
    """
    if not indent_pat:
        # 自动推导缩进模式：第一个缩进条目的前缀空格或制表符
        # 要求：只能是纯空格或纯制表符，不能混用
        m = re.match(r"^ +|\t+", line)
        indent_pat = m[0]
    indent = re.match(r"^ *|\t*", line)[0].count(indent_pat)
    remain = line.lstrip(indent_pat * indent)

    pat = re.compile(r"(?P<title>[^@ \n]+)(?: *@ *(?P<index>\d+))?")
    if (m := pat.match(remain)) is None:
        if dbg:
            raise OutlineParseError(f"{dbg.linenum}（格式错误）：{line:!r}", dbg)
        else:
            raise OutlineParseError(f"（格式错误）：{line!r}",
                                    ParsingDebugInfo(0, 0, line))
    else:
        title = m["title"]
        index = int(m["index"]) if m["index"] else last_index
        oi = OutlineItem(indent, title, index)
        return (oi, indent_pat)
