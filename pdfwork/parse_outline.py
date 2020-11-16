"""这个模块提供了解析大纲（Outline） 表示文本（大纲源码）的功能。
语法满足：

```
《标题》 @ 《页码》
```

的文本解析为 :class:`OutlineInfo` 对象，用于构建 :class:`Outline`。

Outline 语法
================

Outline 的表示法可分为三个部分：

1. 缩进：用于表示当前大纲对象的层级
2. 标题：大纲的标题文本
3. 页码：大纲所跳转的逻辑页码。可以忽略，令解析器自动推导，在这种情况下会使用上一条大纲的页码。
    这里的页码只涉及逻辑页码，与物理页码的偏移是在 import_outline 模块处理的。
"""
import re

from dataclasses import dataclass
from re import match
from typing import *

from .exceptions import OutlineParseError

__all__ = ("outline_encode", "outline_decode", "Outline")


class Outline:
    """一条大纲：

    + :param int indent: 此大纲的缩进级别，从 0 开始
    + :param str title: 大纲文本
    + :param int index: 对应的页码，需要解析为确定的整数
    """
    indent: int
    title: str
    index: int

    def __init__(self,
                 indent: int,
                 title: str,
                 index: int,
                 init_sub: Optional[List["Outline"]] = None):
        self.indent = indent
        self.title = title
        self.index = index

        self._children = init_sub if init_sub else []

    def add_child(self, child: "Outline"):
        self._children.append(child)

    def __repr__(self) -> str:
        if self._children:
            subtree = "[" + ", ".join((f"{i!r}" for i in self._children)) + "]"
            return f"Outline({self.indent!r}, {self.title!r}, {self.index!r}, {subtree})"
        else:
            return f"Outline({self.indent!r}, {self.title!r}, {self.index!r})"

    @property
    def children(self) -> List["Outline"]:
        return self._children

    def add_node(self, oi: "Outline", level: int):
        """在最后一个缩进等级为 ``level`` 的节点下添加节点， -1 表示根节点。
        """
        self.last_node(level - 1).add_child(oi)

    def last_node(self, level: int = -1) -> "Outline":
        """返回最后添加的缩进等级为 ``level`` 的节点， -1 表示根节点。
        """
        if level == -1:
            return self
        else:
            stack = [self]
            for _ in range(level + 1):
                stack.append(stack[-1].last_children())
            return stack[-1]

    def last_children(self) -> Optional["Outline"]:
        if self._children:
            return self._children[-1]
        else:
            return None

    def encode(self) -> str:
        """将树编码为文本
        """
        raise NotImplementedError

    def __eq__(self, o: "Outline") -> bool:
        if all([
                self.indent == o.indent, self.title == o.title,
                self.index == o.index
        ]):
            if len(self.children) == len(self.children):
                return all([a == b for a, b in zip(self.children, o.children)])
        else:
            return False


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


def outline_decode(text: str) -> Outline:
    """解析大纲源码为大纲树
    """
    # 解析时忽略空行和 `#` 起始的行
    source = text.splitlines(False)
    lines = len(source)

    # 上一条目的缩进等级
    last_indent: int = 0
    # 用于识别缩进的模式
    indent_pat: Optional[str] = None
    # 上一条目的页码
    last_index = 0

    tree = Outline(-1, "OUTLINE ROOT", 0)

    for i, line in enumerate(source):
        dbg = ParsingDebugInfo(i, lines, line)
        if i != "" or re.match(r"^[ \t]*#"):
            oi, indent_pat = parse_line(line, indent_pat, last_index, dbg)
            if oi.indent > last_indent + 1:
                raise OutlineParseError(f"{dbg.linenum}（缩进跨度过大）：{line!r}", dbg)
            else:
                tree.add_node(oi, oi.indent)
                last_indent = oi.indent
                last_index = oi.index
    return tree


def outline_encode(ot: Outline) -> str:
    """将大纲树编码为源码表示，见 :meth:`Outline.encode`。
    """
    return ot.encode()


def parse_line(
        line: str, indent_pat: Optional[str], last_index: int,
        dbg: Optional[ParsingDebugInfo]) -> Tuple[Outline, Optional[str]]:
    """解析一行

    :param str line: 单行大纲源码文本
    :param Optional[str] indent_pat: 用于识别缩进的模式，如果为 None 则需要自动推导
    :param int last_index: 上条大纲的页码
    :param int dbg_linenum: 调试信息，当前处理的行号

    :returns: (Outline, 识别出的缩进模式)

    行格式::

        <缩进> <标题> @ <页码>?
    """
    if not indent_pat:
        # 自动推导缩进模式：第一个缩进条目的前缀空格或制表符
        # 要求：只能是纯空格或纯制表符，不能混用
        m = re.match(r"^ +|\t+", line)
        indent_pat = m[0] if m else None

    if indent_pat:
        indent = re.match(r"^ *|\t*", line)[0].count(indent_pat)
        remain = line.lstrip(indent_pat * indent)
    else:
        indent = 0
        remain = line

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
        oi = Outline(indent, title, index)
        return (oi, indent_pat)
