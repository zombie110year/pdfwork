import re
import sys
from io import BytesIO
from io import StringIO
from typing import *

from PyPDF2.generic import Destination
from PyPDF2.generic import IndirectObject
from PyPDF2.pdf import PdfFileReader
from PyPDF2.pdf import PdfFileWriter

from .model import PdfSlice
from .utils import open_pdf

__all__ = ("action_merge", "action_split", "action_import_outline", "action_export_outline", "action_erase_outline")


def action_merge(inputs: str, output: Optional[str]):
    """一个合并任务。

    :param str inputs: 用字符串表示的输入
    :param Optional[str] output: 输出文件路径，如果为 None 则为 stdout

    一个输入字符串应满足 `<filename>:<page range>|<file2>:<pr 2>` 的形式，如::

        action_merge("example.pdf:1,2,3-|example2.pdf:5,2,4", None)

    将会输出以这样的顺序排列的新文档::

        example.pdf:1
        example.pdf:2
        example.pdf:3
        example.pdf:...直到末尾
        example2.pdf:5
        example2.pdf:2
        example2.pdf:4

    **注意** ：所有页码都是从 0 开始的。
    **注意** ：书签、标记等可能会遗失。
    """
    print(f"{inputs=}, {output=}")


def action_split(input: Optional[str], outputs: str):
    """一个分割任务。

    :param Optional[str] input: 输入文件的路径，如果为 None 则为 stdin
    :param str outputs: 输出文件以及它们所得到的页码

    输出参数应满足 `<filename>:<page range>|<file2>:<pr 2>` 的形式，如::

        action_split("p1.pdf:1,2,3-|p2.pdf:5,2,4")

    这样，分隔出的两个文件将会拥有以下页码的内容::

        p1.pdf:
            1,
            2,
            3,
            ... 直到末尾

        p2.pdf:
            5,
            2,
            4


    **注意** ：所有页码都是从 0 开始的。
    **注意** ：书签、标记等可能会遗失。
    """
    if input is None:
        pdfin = BytesIO(sys.stdin.read())
    else:
        pdfin = open_pdf(input)

    slices = outputs.split("|")
    for sliced in slices:
        pdfw = PdfFileWriter()
        path, pages = sliced.split(":")
        pdfs = PdfSlice(pdfin, pages)
        for p in pdfs:
            pdfw.addPage(p)
        with open(path, "wb") as pdfout:
            pdfw.write(pdfout)


def action_import_outline(pdf: str, input: Optional[str], offset=0):
    """将输入的目录信息导入到 pdf 文件中。

    :param str pdf: 要导入的 PDF 文件的路径。
    :param Optional[str] input: 记录目录信息的文本文件，如果为 None 则从 stdin 读取。
    :param int offset: 页码的偏移两，默认为 0；这个参数是为了弥补照抄书籍目录页时，
        由于前方页数未计算在内的造成的偏移。

    目录信息将具有以下格式::

        《标题》 @ <页码>
            《次级标题》 @ <页码>

    **注意** ： 所有页码都是从 0 开始的
    """
    if input is None:
        outlines = sys.stdin.read()
    else:
        with open(input, "rt", encoding="utf-8") as src:
            outlines = src.read()
    outlines: List[str] = [
        l for l in outlines.split("\n") if l != "" and not l.startswith("#") and not re.match(r"^$", l)
    ]

    pdfile = open_pdf(pdf)
    pdfr = PdfFileReader(pdfile)
    pdfw = PdfFileWriter()
    pdfw.appendPagesFromReader(pdfr)

    parents: List[Optional[Destination]] = [None]

    # 第一次
    parts = outlines[0].split("@")
    pagenum = int(parts[-1].strip())
    level = parts[0].count("\t")
    title = "@".join(parts[:-1]).strip()
    lastobj = pdfw.addBookmark(title, pagenum, parents[level], None, False, False, "/FitH", 0)
    lastone = (level, title, pagenum)

    for outline in outlines[1:]:
        parts = outline.split("@")
        pagenum = int(parts[-1].strip())
        level = parts[0].count("\t")
        title = "@".join(parts[:-1]).strip()

        if level > lastone[0]:
            parents.append(lastobj)
        elif level < lastone[0]:
            diff = lastone[0] - level
            for i in range(diff):
                parents.pop()

        lastobj = pdfw.addBookmark(title, pagenum, parents[-1], None, False, False, "/FitH", 0)
        lastone = (level, title, pagenum)

    with open(pdf, "wb") as out:
        pdfw.write(out)


def action_export_outline(pdf: str, output: Optional[str]):
    """将 PDF 文件中的目录信息导出到文本文件中。

    :param Optional[str] output: 记录目录信息的文本文件，如果为 None 则输出到 stdout。
    :param str pdf: PDF 文件的路径。

    目录信息将具有以下格式::

        《标题》 @ <页码>
            《次级标题》 @ <页码>

    **注意** ： 所有页码都是从 0 开始的
    """
    def write_nested_outlines(nested: list, level: int):
        """访问外部的 outbuf 与 reader 变量。
        """
        for l in nested:
            if isinstance(l, list):
                write_nested_outlines(l, level + 1)
            else:
                l: Destination
                title = l.get("/Title", "untitled")
                pagenumber = reader.getDestinationPageNumber(l)
                outbuf.write("\t" * level)
                outbuf.write(f"{title}")
                outbuf.write(" @ ")
                outbuf.write(f"{pagenumber}")
                outbuf.write("\n")

    pdfile = open_pdf(pdf)
    reader = PdfFileReader(pdfile)
    outline = reader.getOutlines()
    if output is not None:
        with open(output, "wt", encoding="utf-8") as outbuf:
            write_nested_outlines(outline, 0)
    else:
        output = sys.stdout
        write_nested_outlines(outline, 0)
    pdfile.close()


def action_erase_outline(pdf: str):
    """抹除一个 PDF 文件中的目录信息

    :param str pdf: PDF 文件的路径
    """
    pdfile = open_pdf(pdf)
    reader = PdfFileReader(pdfile)
    writer = PdfFileWriter()
    writer.appendPagesFromReader(reader)
    with open("out.pdf", "wb") as out:
        writer.write(out)
    pdfile.close()
