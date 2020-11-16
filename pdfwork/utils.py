import enum
from io import BytesIO
from typing import *
from PyPDF2.generic import Destination

from pikepdf import Pdf, OutlineItem, Object
from pikepdf import Outline as PikeOutline

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


def export_outline(pdf: Pdf, pike: PikeOutline) -> Outline:
    """将 pdf 中的书签导出为一个 Outline 树
    """
    root = Outline(-1, "OUTLINE ROOT", 0)
    pn_map = make_pagenum_search_table(pdf)

    def tree_copy(subtree: List[OutlineItem], level: int):
        nonlocal root
        for oi in subtree:
            # Destination 结构为 [pageid, action, action_args]
            # https://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
            # 374 页，第 12.3.2.2 章
            pageid = oi.destination[0].to_json().decode()
            pn = pn_map(pageid)
            o = Outline(level, oi.title, pn + 1)
            root.add_node(o, o.indent)
            tree_copy(oi.children, level + 1)

    tree_copy(pike.root, 0)

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


def make_pagenum_search_table(pdf: Pdf) -> Callable[[str], Optional[int]]:
    """构建 《Page Object 标识符》 => 《页码》 查询表。

    返回一个可执行对象，输入标识符便返回对应的页码。
    """
    id2num = {}

    for i, page in enumerate(pdf.pages):
        identifier = page.to_json().decode()
        id2num[identifier] = i

    def query(pageid: str) -> Optional[int]:
        return id2num.get(pageid, None)

    return query