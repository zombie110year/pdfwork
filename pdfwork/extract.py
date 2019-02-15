"""提取 pdf 文件内容

可将一个文件中的不同页面或连续页面提取到不同文件::

    pdf-extract origin.pdf -e first.pdf 0-9,13-16,99 -e second.pdf 10-12
"""

from argparse import Action, ArgumentParser, _copy_items
from pathlib import Path

import PyPDF2 as pdf

from .utils import PageNumberParser, SetFilePathAction


class ParsePagesAction(Action):
    """解析 -e 参数, 分析输出文件以及解析页码

    :return: (Path('output.pdf'), [(begin, end), (begin, end), ...])
    :rtype: (Path, [(int, int)])
    """

    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):

        if nargs != 2:
            raise ValueError("nargs != 2")

        super(ParsePagesAction, self).__init__(option_strings, dest, nargs=nargs, const=const,
                                               default=default, type=type, choices=choices, required=required, help=help, metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, [])
        items = _copy_items(items)

        page_number_parser = PageNumberParser()

        pair = (
            Path(values[0]),
            page_number_parser.parse(values[1]),
        )

        items.append(pair)

        setattr(namespace, self.dest, items)


def _get_parser():
    parser = ArgumentParser(
        prog="pdf-extract", description="提取 PDF 的一部分, 输出至目标文件中",
    )

    parser.add_argument(
        "origin", help="原文件", metavar="origin.pdf",
        action=SetFilePathAction
    )

    parser.add_argument(
        "-e", "--extract", help="输出文件, 以及抽取的页码, 连续页码用 - 间断页码用 ,. 连续页码为闭区间", metavar="exam.pdf 1-19,2,34",
        nargs=2, action=ParsePagesAction, required=True
    )

    return parser


def extract(args):
    """提取 PDF 内容
    """

    reader = pdf.PdfFileReader(str(args.origin.absolute()))

    for output, pages in args.extract:
        writer = pdf.PdfFileWriter()
        begin, end = pages
        for i in range(begin, end):
            writer.addPage(
                reader.getPage(i)
            )
        with output.open("wb") as file:
            writer.write(file)
        del writer


def main():
    args = _get_parser().parse_args()
    extract(args)
