from io import BytesIO
from typing import *

from PyPDF2.pdf import Destination, PdfFileReader, PdfFileWriter

from pikepdf import Pdf, OutlineItem

from .outline import Outline

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


def export_outline(pdf: BytesIO) -> Outline:
    """将 pdf 中的书签导出为一个 Outline 树
    """
    root = Outline(-1, "OUTLINE ROOT", 0)

    def tree_copy(subtree: list, level: int):
        """

        :param list tree: 一个表示树结构的嵌套列表，例如 ``[[], [[]]]``
        """
        nonlocal root

        for l in subtree:
            if isinstance(l, list):
                tree_copy(l, level + 1)
            else:
                title = l.get("/Title", "untitled")
                index = reader.getDestinationPageNumber(l)
                o = Outline(level, title, index)
                root.add_node(o, o.indent)

    reader = PdfFileReader(pdf)
    pdfoutlines = reader.getOutlines()
    tree_copy(pdfoutlines, 0)

    return root


def import_outline(pdfw: Pdf, root: Outline, offset: int):
    """将大纲导入到 pdf 中。
    """
    with pdfw.open_outline() as outlines:
        pikeroot = outlines.root
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

            seqn = ".".join([f"{i}" for i in seq[:o.indent + 1]])

            bookmark = OutlineItem(
                # title
                f"{seqn} {o.title}",
                # 页码，pikepdf 从 0 开始计数
                o.index + offset - 1,
                # 跳转效果：适应页面
                "Fit")

            if parent := bookmarks[o.indent]:
                parent.children.append(bookmark)
            else:
                pikeroot.append(bookmark)

            if o.indent > stack[-1].indent:
                stack.append(o)
                bookmarks.append(bookmark)
            elif o.indent < stack[-1].indent:
                stack = stack[:o.indent + 2]
                bookmarks = bookmarks[:o.indent + 2]
                stack[o.indent + 1] = o
                bookmarks[o.indent + 1] = bookmark
            else:
                stack[o.indent + 1] = o
                bookmarks[o.indent + 1] = bookmark

            for subtree in o.children:
                import_sub(subtree)

        for node in root.children:
            import_sub(node)