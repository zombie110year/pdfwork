from io import BytesIO
from typing import *

from PyPDF2.pdf import Destination, PdfFileReader, PdfFileWriter

from .outline import OutlineTuple

__all__ = ("open_pdf", "export_outline")


def open_pdf(path: str) -> BytesIO:
    """将 PDF 文件的内容读入 BytesIO 并返回。

    为什么？

    相比现代计算机的内存，PDF 文件最大也不过数百 MB，足够使用。
    将其完全读取入内存，能够提高读写效率。

    另外，也不需要占用文件句柄（描述符），方便对源文件进行覆写。
    """
    with open(path, "rb") as src:
        content = src.read()
    io = BytesIO(content)
    return io


def export_outline(pdf: BytesIO) -> list:
    """将 pdf 中的书签导出为一组列表。

    这个列表是非嵌套的，每个元素是一个三元组：（缩进，标题，页码）。
    """
    def get_outlines_from_nested(nested: list, level: int):
        """访问外部的 outbuf 与 reader 变量。
        """
        for l in nested:
            if isinstance(l, list):
                get_outlines_from_nested(l, level + 1)
            else:
                title = l.get("/Title", "untitled")
                pagenumber = reader.getDestinationPageNumber(l)
                outlines.append((level, title, pagenumber))

    outlines: List[OutlineTuple] = []
    reader = PdfFileReader(pdf)
    pdfoutlines = reader.getOutlines()
    get_outlines_from_nested(pdfoutlines, 0)

    return outlines


def import_outline(pdfw: PdfFileWriter, outlines: List[OutlineTuple]):
    """将 outlines 导入到 pdf 中。
    outlines 的三个字段分别是 (缩进，标题，页码)

    **注意** ： 当输入的标签等级并非从 0 开始时，高于最初等级的书签将会丢失。
    """

    if len(outlines) == 0:
        return

    # 第一次
    level, title, pn = outlines[0]
    parents: List[Optional[Destination]] = [None] * 16
    lastobj = pdfw.addBookmark(title, pn, parents[level], None, False, False,
                               "/Fit")
    lastone = (level, title, pn)

    for outline in outlines[1:]:
        level, title, pn = outline

        if level > lastone[0]:
            parents[level] = lastobj

        lastobj = pdfw.addBookmark(title, pn, parents[level], None, False,
                                   False, "/Fit")
        lastone = (level, title, pn)
