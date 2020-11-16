from io import BytesIO
from typing import *

from PyPDF2.pdf import Destination, PdfFileReader, PdfFileWriter

from .parse_outline import Outline

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

    outlines: List[Outline] = []
    reader = PdfFileReader(pdf)
    pdfoutlines = reader.getOutlines()
    get_outlines_from_nested(pdfoutlines, 0)

    return outlines


def import_outline(pdfw: PdfFileWriter, root: Outline, offset: int):
    """将大纲导入到 pdf 中。
    """
    seq = [1]
    stack = [root]
    bookmarks = [None]

    def import_sub(o: Outline):
        nonlocal seq
        nonlocal stack
        nonlocal bookmarks

        if o.indent > stack[-1].indent:
            seq.append(1)
        elif o.indent < stack[-1].indent:
            seq = seq[:o.indent + 1]
            seq[o.indent] += 1
        else:
            seq[o.indent] += 1

        parent = bookmarks[o.indent]

        seqn = ".".join([f"{i}" for i in seq[:o.indent + 1]])
        bookmark = o

        bookmark = pdfw.addBookmark(
        # title
        f"{seqn} {o.title}",
        # pagenum： -1 是因为逻辑页码从 1 开始，而 PyPDF2 对页码的索引从 0 开始
        # offset = 物理页码 - 逻辑页码
        # 逻辑页码表示这是正文中的第几页，物理页码则表示这是第几张纸
        o.index + offset - 1,
        # parent
        parent,
        #color
        None,
        #bold
        False,
        #italic
        False,
        #fit
        '/Fit')

        if o.indent > stack[-1].indent:
            stack.append(o)
            bookmarks.append(bookmark)
        elif o.indent < stack[-1].indent:
            stack = stack[:o.indent + 2]
            bookmarks = bookmarks[:o.indent + 2]
        else:
            stack[o.indent + 1] = o
            bookmarks[o.indent + 1] = bookmark

        for subo in o.children:
            import_sub(subo)

    for node in root.children:
        import_sub(node)