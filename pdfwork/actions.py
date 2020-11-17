import re
from pathlib import Path
from sys import stdin
from typing import *

from pikepdf import Pdf
from tqdm import tqdm, trange

from .outline import *
from .range import *
from .utils import check_paths_exists, export_outline, get_fmt_pat, import_outline

__all__ = ("action_merge", "action_split", "action_import_outline",
           "action_export_outline", "action_erase_outline")


def action_merge(inputs: List[str], output: str):
    """合并一系列 PDF 文件。

    :param input: 当输入一组路径时，按照顺序合并对应的文件；当输入以 ``@`` 开头的文件名（如 ``@files.txt``）时，从 `@files.txt` 读取文件路径并按顺序合并；当为 None 时，从 stdin 读取文件路径并按顺序合并。
    :param output: 输出路径。

    **注意** ：书签会丢失，如果想要保留，需提前导出备份，见 :meth:`action_export_outline`。
    """
    if len(inputs) == 0:
        # 从 stdin 读取文件路径
        paths = check_paths_exists([i.rstrip("\n") for i in stdin.readlines()])
    elif len(inputs) == 1 and inputs[0].startswith("@"):
        # 从 @file.list 读取文件路径
        with open(inputs[0], "rt", encoding="utf-8") as file_list:
            paths = check_paths_exists(
                [i.rstrip("\n") for i in file_list.readlines()])
    else:
        paths = check_paths_exists(inputs)

    pdfw: Pdf = Pdf.new()

    for path in trange(paths, ascii=True, desc="组合"):
        pdfr = Pdf.open(path)
        pdfw.pages.extend(pdfr.pages)
        pdfr.close()

    pdfw.save(output, linearize=True)


def action_split(input: str, outputs: Optional[str]):
    """一个分割任务。

    :param input: 输入文件的路径
    :param str outputs: 输出路径。可使用 Python format 模板格式化页码。如果只提供目录名（如 ``out/``），则会自动推导文件名格式化样式。例如，假设文件有超过 100 但不足 1000 页时，将格式化为 ``{:03d}.pdf``。默认输出到当前文件夹

    **注意** ：书签、标记等可能会遗失。
    """
    pdfr: Pdf = Pdf.open(input)

    fmt = get_fmt_pat(outputs, len(pdfr.pages))

    for i, page in enumerate(tqdm(pdfr.pages, ascii=True, desc=f"拆分 {fmt!r}")):
        pdfw: Pdf = Pdf.new()
        pdfw.pages.append(page)

        path = Path(fmt.format(i))
        path.parent.mkdir(parents=True, exist_ok=True)
        pdfw.save(path, linearize=True)

    pdfr.close()


def action_import_outline(pdf: str,
                          input: Optional[str],
                          output: str,
                          offset=0):
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
    pdfw.save(output, linearize=True)


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


def action_erase_outline(pdf: str, output: str):
    """抹除一个 PDF 文件中的目录信息

    :param str pdf: PDF 文件的路径
    """
    pdfw = Pdf.new()

    pdfr = Pdf.open(pdf)
    pdfw.pages.extend(pdfr.pages)
    pdfr.close()

    pdfw.save(output, linearize=True)
