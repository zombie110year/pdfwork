from hashlib import md5 as get_hash
from pathlib import Path
from sys import stdin
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import typer
# mypy 无法导入类型声明
from pikepdf import Pdf  # type: ignore
from tqdm import tqdm  # type: ignore

from .outline import Outline
from .outline import outline_decode
from .outline import outline_encode
from .utils import check_paths_exists
from .utils import export_outline
from .utils import fmt_pat
from .utils import import_outline

__all__ = ("action_merge", "action_split", "action_import_outline",
           "action_export_outline", "action_erase_outline")


def action_merge(inputs: List[str], output: str):
    """合并一系列 PDF 文件。

    :param input: 当输入一组路径时，按照顺序合并对应的文件；
        当输入以 ``@`` 开头的文件名（如 ``@files.txt``）时，
        从 `@files.txt` 读取文件路径并按顺序合并；
        当为 None 时，从 stdin 读取文件路径并按顺序合并。
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

    for path in tqdm(paths, desc="合并", ascii=True):
        pdfr = Pdf.open(path)
        pdfw.pages.extend(pdfr.pages)
        pdfr.close()

    try:
        pdfw.save(output, linearize=True)
    except RuntimeError as e:
        typer.secho("ERROR: {}, inputs={}, output={}".format(
            e, inputs, output),
                    fg="red",
                    err=True)
        raise e


def action_split(input: str, outputs: Optional[str]):
    """一个分割任务。

    :param input: 输入文件的路径
    :param str outputs: 输出路径。可使用 Python format 模板格式化页码。
        如果只提供目录名（如 ``out/``），则会自动推导文件名格式化样式。
        例如，假设文件有超过 100 但不足 1000 页时，
        将格式化为 ``{:03d}.pdf``。默认输出到当前文件夹

    **注意** ：书签、标记等可能会遗失。
    """
    pdfr: Pdf = Pdf.open(input)

    fmt = fmt_pat(outputs, len(pdfr.pages)) if outputs else fmt_pat(
        "", len(pdfr.pages))

    for i, page in enumerate(tqdm(pdfr.pages, ascii=True, desc=f"拆分 {fmt!r}")):
        pdfw: Pdf = Pdf.new()
        pdfw.pages.append(page)

        path = Path(fmt.format(i))
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            pdfw.save(path, linearize=True)
        except RuntimeError as e:
            # ERROR: operation for name attempted on object of type string
            # 是 PDF 内容的问题，见 https://github.com/qpdf/qpdf/issues/74
            typer.secho("ERROR: {}, input={}, outputs={}".format(
                e, input, fmt),
                        fg="red",
                        err=True)
            raise e

    pdfr.close()


def action_import_outline(pdf: str,
                          input: Optional[str],
                          output: str,
                          offset=0):
    """将输入的目录信息导入到 pdf 文件中。

    :param str pdf: 要导入的 PDF 文件的路径。
    :param Optional[str] input: 记录目录信息的文本文件，如果为 None 则从 stdin 读取。
    :param int offset: 页码的偏移量，默认为 0；
        这个参数是为了弥补照抄书籍目录页时，
        由于前方页数未计算在内的造成的偏移。
        一般设置为目录页中标记为第一页的页面在 PDF 阅读器中的实际页码。

    目录信息将具有以下格式::

        《标题》 @ <页码>
            《次级标题》 @ <页码>

    **注意** ： 页码是在书籍目录页中书写的页码，一般从 1 开始。如果有一行没有标注页码，那么会继承上一行的页码。
    """
    if input is None:
        outline_src = stdin.read()
    else:
        with open(input, "rt", encoding="utf-8") as src:
            outline_src = src.read()
    root = outline_decode(outline_src)

    pdfw = Pdf.open(pdf, allow_overwriting_input=True)
    import_outline(pdfw, root, offset)
    try:
        pdfw.save(output, linearize=True)
    except RuntimeError as e:
        typer.secho("ERROR: {}, pdf={}, input={}, output={}, offset={}".format(
            e, pdf, input, output, offset),
                    fg="red",
                    err=True)
        raise e


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
        typer.echo_via_pager(content)


def action_erase_outline(pdf: str, output: str):
    """抹除一个 PDF 文件中的目录信息

    :param str pdf: PDF 文件的路径
    """
    pdfw = Pdf.new()

    pdfr = Pdf.open(pdf)
    pdfw.pages.extend(pdfr.pages)
    pdfr.close()

    try:
        pdfw.save(output, linearize=True)
    except RuntimeError as e:
        typer.secho("ERROR: {}, pdf={}, output={}".format(e, pdf, output),
                    fg="red",
                    err=True)
        raise e


def action_optimize(src: str, output: Optional[str] = None):
    """优化 PDF 文件：线性化、去重、去除未引用资源

    :param str src: 被处理的 PDF 文件路径
    :param str output: 输出路径，为 Nohene 则保存至原文档加 ``_`` 后缀的 PDF 文件
    """
    src_ = Path(src)
    stem = src_.stem
    parent = src_.parent
    output = (parent / "{}_.pdf".format(stem)
              ).as_posix() if (output is None) or (output == src) else output
    pdf = Pdf.open(src)

    # 来自讨论 https://github.com/pikepdf/pikepdf/issues/198
    # hex hash => [(page number, object name)]
    image_hash: Dict[str, List[Tuple[int, str]]] = {}

    progress1 = tqdm(desc="查重")
    # 构建引用表
    for p in range(len(pdf.pages)):
        for im in pdf.pages[p].images.keys():
            # must record in image_hash
            obj = pdf.pages[p].images[im]
            hashsum = get_hash(obj.read_bytes()).hexdigest()
            if hashsum in image_hash:
                image_hash[hashsum].append((p, im))
            else:
                image_hash[hashsum] = [(p, im)]
            progress1.update()
    progress1.close()

    progress2 = tqdm(desc="去重", total=progress1.n - len(image_hash.keys()))
    # 将图像指向具有相同 hash 的第一个图像
    for first, *others in image_hash.values():
        p0, im0 = first
        for p, im in others:
            pdf.pages[p].Resources.XObject[im] = pdf.pages[
                p0].Resources.XObject[im0]
            progress2.update()
    progress2.close()

    pdf.remove_unreferenced_resources()
    try:
        pdf.save(output, linearize=True)
    except RuntimeError as e:
        typer.secho("ERROR: {}, src={}, output={}".format(e, src, output),
                    fg="red",
                    err=True)
        raise e
