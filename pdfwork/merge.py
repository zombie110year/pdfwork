"""合并 PDF 文件

"""

from argparse import Action, ArgumentParser, _copy_items
from pathlib import Path

import PyPDF2 as pdf
from .utils import SetFilePathAction

class AppendInputAction(Action):
    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None
    ):
        if nargs != 2:
            raise ValueError("nargs != 2")

        super(AppendInputAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = _copy_items(items)

        pair = (
            Path(values[0]),
            int(values[1]),
        )

        items.append(pair)

        setattr(namespace, self.dest, items)


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
