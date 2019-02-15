"""合并 PDF 文件

"""

from argparse import Action, ArgumentParser, _copy_items
from pathlib import Path

import PyPDF2 as pdf


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


class SetOutputAction(Action):
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
        super(SetOutputAction, self).__init__(
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
        path = Path(values)
        setattr(namespace, self.dest, path)


def _get_parser():
    parser = ArgumentParser(
        prog='pdf-merge',
        description='合并多个 PDF 文件',
    )

    parser.add_argument(
        '-o', '--output', type=str, default=Path('merged.pdf'),
        metavar='example.pdf', help='合并输出到 PDF 文件',
        action=SetOutputAction
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
        with path.open('rb') as file:
            reader = pdf.PdfFileReader(file)
            for i in range(repeat):
                writer.appendPagesFromReader(reader)
                reader.stream.seek(0)
    with args.output.open("wb") as file:
        writer.write(file)

def main():
    parser = _get_parser()
    args = parser.parse_args()
    merge(args)
