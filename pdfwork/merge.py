"""合并 PDF 文件

"""

from argparse import ArgumentParser
from pathlib import Path

import PyPDF2 as pdf

from .utils import AppendInputAction, SetFilePathAction


def _get_parser():
    """

    :return: conf

        .. data:: conf

            .. attribute:: files

                ``files = [(Path('file1.pdf'), int(repeat_number)), ...]``

            .. attribute:: output

                ``output = Path("Output.pdf")``

    """
    parser = ArgumentParser(
        prog='pdf-merge',
        description='合并多个 PDF 文件',
    )

    parser.add_argument(
        '-o', '--output', default=Path('merged.pdf'),
        metavar='example.pdf', help='合并输出到 PDF 文件',
        action=SetFilePathAction
    )

    parser.add_argument(
        '-i', dest='files', nargs=2, required=True,
        metavar='page.pdf 100', help='输入文件以及重复次数', type=str,
        action=AppendInputAction
    )

    return parser


def merge(args):
    """合并 PDF 文件
    """

    # 空白页
    writer = pdf.PdfFileWriter()
    for path, repeat in args.files:
        reader = pdf.PdfFileReader(str(path.absolute()))

        # pages = [reader.getPage(i) for i in range(reader.getNumPages())]

        for i in range(repeat):
            writer.appendPagesFromReader(reader)

    with args.output.open("wb") as file:
        writer.write(file)


def main():
    parser = _get_parser()
    args = parser.parse_args()
    merge(args)
