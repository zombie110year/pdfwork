import re
import sys
from io import BytesIO, StringIO
from os import fdopen
from typing import *

import pikepdf
from PyPDF2.generic import Destination, IndirectObject
from PyPDF2.pdf import PdfFileReader, PdfFileWriter
from pikepdf import Pdf, OutlineItem

from .range import *
from .outline import *
from .utils import export_outline, import_outline, open_pdf

__all__ = ("action_merge", "action_split", "action_import_outline",
           "action_export_outline", "action_erase_outline")


def action_merge(inputs: str, output: Optional[str]):
    """一个合并任务。

    :param str inputs: 用字符串表示的输入
    :param Optional[str] output: 输出文件路径，如果为 None 则为 stdout

    一个输入字符串应满足 ``<filename> / <page range> & <file2> / <pr 2>`` 的形式，如::

        action_merge("example.pdf / 1,2,3: & example2.pdf / 5,2,4", None)

    将会输出以这样的顺序排列的新文档::

        example.pdf:1
        example.pdf:2
        example.pdf:3
        example.pdf:...直到末尾
        example2.pdf:5
        example2.pdf:2
        example2.pdf:4

    **注意** ：页码是从 1 开始的。
    **注意** ：书签、标记等可能会遗失。
    """
    pdfw: pikepdf.Pdf = pikepdf.Pdf.new()

    slices = re.split(r" *& *", inputs)
    # 合并各文件
    for sliced in slices:
        path, pages = re.split(r" */ *", sliced)
        pdfin = open_pdf(path)
        pdfs: pikepdf.Pdf = pikepdf.Pdf.open(pdfin)

        for pn in MultiRange(pages):
            page = pdfs.pages.p(pn)
            pdfw.pages.append(page)

    if output is None:
        outbuf = fdopen(sys.stdout.fileno(), "wb")
        pdfw.save(outbuf)
        outbuf.close()
    else:
        pdfw.save(output)


def action_split(input: Optional[str], outputs: str):
    """一个分割任务。

    :param Optional[str] input: 输入文件的路径，如果为 None 则为 stdin
    :param str outputs: 输出文件以及它们所得到的页码

    输出参数应满足 ``<filename> / <page range> | <file2>/<pr 2>`` 的形式，如::

        action_split("p1.pdf / 1,2,3: | p2.pdf / 5,2,4")

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


    **注意** ：页码是从 1 开始的。
    **注意** ：书签、标记等可能会遗失。
    """
    # 获取输入
    if input is None:
        fp = fdopen(sys.stdin.fileno(), "rb")
        pdfin = BytesIO(fp.read())
        fp.close()
    else:
        pdfin = open_pdf(input)

    pdfr: pikepdf.Pdf = pikepdf.Pdf.open(pdfin)
    # 输出切片
    slices = re.split(r" *\| *", outputs)
    for sliced in slices:
        pdfw: pikepdf.Pdf = pikepdf.Pdf.new()

        path, pages = re.split(r" */ *", sliced)
        pr = MultiRange(pages).iter()

        for p in pr:
            # QPDF 用 1 做索引起始
            page = pdfr.pages.p(p)
            pdfw.pages.append(page)

        pdfw.save(path)


def action_import_outline(pdf: str, input: Optional[str], offset=0):
    """将输入的目录信息导入到 pdf 文件中。

    :param str pdf: 要导入的 PDF 文件的路径。
    :param Optional[str] input: 记录目录信息的文本文件，如果为 None 则从 stdin 读取。
    :param int offset: 页码的偏移量，默认为 0；这个参数是为了弥补照抄书籍目录页时，
        由于前方页数未计算在内的造成的偏移。一般设置为目录页中标记为第一页的页面在 PDF 阅读器中的实际页码。

    目录信息将具有以下格式::

        《标题》 @ <页码>
            《次级标题》 @ <页码>

    **注意** ： 页码是在书籍目录页中书写的页码，一般从 1 开始。如果有一行没有标注页码，那么会继承上一行的页码。
    """
    if input is None:
        outline_src = sys.stdin.read()
    else:
        with open(input, "rt", encoding="utf-8") as src:
            outline_src = src.read()
    root = outline_decode(outline_src)

    pdfw = Pdf.open(pdf, allow_overwriting_input=True)
    import_outline(pdfw, root, offset)
    pdfw.save(pdf)


def action_export_outline(pdf: str, output: Optional[str]):
    """将 PDF 文件中的目录信息导出到文本文件中。

    :param Optional[str] output: 记录目录信息的文本文件，如果为 None 则输出到 stdout。
    :param str pdf: PDF 文件的路径。

    目录信息将具有以下格式::

        《标题》 @ <页码>
            《次级标题》 @ <页码>

    **注意** ： 页码是在书籍目录页中书写的页码，一般从 1 开始。如果有一行没有标注页码，那么会继承上一行的页码。
    """
    pdfr = Pdf.open(pdf)
    with pdfr.open_outline() as pikeoutline:
        root: Outline = export_outline(pdfr, pikeoutline)

    content = outline_encode(root)
    if output is not None:
        with open(output, "wt", encoding="utf-8") as outbuf:
            outbuf.write(content)
    else:
        print(content)


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
