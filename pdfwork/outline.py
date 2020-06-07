"""解析 outline
"""
import re
from typing import *
__all__ = ("parse_outline_iter", "parse_outline")

# (level: int, title: str, page: int)
OutlineTuple = Tuple[int, str, int]


class OutlineParseError(Exception):
    pass

def parse_outline_iter(src: str) -> Generator[OutlineTuple, None, None]:
    """读取传入的文本，解析并抛出目录（大纲）元组：（等级，标题，页码）。

    目录信息将具有以下格式::

        《标题》 @ <页码>
            《次级标题》 @ <页码>

    **注意** ： 所有页码都是从 0 开始的，如果有一行没有标注页码，那么会继承上一行的页码。
    """
    last_page = 0
    linepat = re.compile(
        r"^(?P<level>(?: {4})*)(?P<title>[^@\n]+?)(?: *@ *(?P<page>\d+))?$",
        re.MULTILINE | re.UNICODE)
    for match in linepat.finditer(src):
        level_, title, page_ = match.groups()

        level = level_.count(" ") // 4
        page_ = last_page if page_ is None else page_
        try:
            page = int(page_)
            last_page = page
            yield level, title, page
        except ValueError as e:
            msg = e.args[0]
            err_pat = match[0]
            raise OutlineParseError(f"{err_pat}:\n{msg}")

def parse_outline(src: str) -> List[OutlineTuple]:
    """读取传入的文本，解析并抛出目录（大纲）元组：（等级，标题，页码）。

    目录信息将具有以下格式::

        《标题》 @ <页码>
            《次级标题》 @ <页码>

    **注意** ： 所有页码都是从 0 开始的，如果有一行没有标注页码，那么会继承上一行的页码。
    """
    return [i for i in parse_outline_iter(src)]