"""提取 pdf 文件内容

可将一个文件中的不同页面或连续页面提取到不同文件::

    pdf-extract origin.pdf -e first.pdf 0-9,13-16,99 -e second.pdf 10-12
"""

from argparse import ArgumentParser
from pathlib import Path

import PyPDF2 as pdf

from .utils import PageNumberParser, ParsePagesAction, SetFilePathAction


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
