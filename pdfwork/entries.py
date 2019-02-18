from argparse import REMAINDER, ArgumentParser
from pathlib import Path

import PyPDF2 as pdf

from .utils import (AppendInputAction, PageNumberParser, ParsePagesAction,
                    SetFilePathAction)

TOOLS = {
    'merge',
    'split',
}

def _get_parser():
    parser = ArgumentParser(
        prog="pdfwork", description="处理 PDF 文件",
    )
    tools = parser.add_subparsers(
        dest="cmd", title="sub-cmd", help="子命令"
    )

    merge = tools.add_parser(
        name="merge", description="合并多个 PDF 文件"
    )
    merge.add_argument(
        '-o', '--output', default=Path('merged.pdf'),
        metavar='example.pdf', help='合并输出到 PDF 文件',
        action=SetFilePathAction
    )

    merge.add_argument(
        '-i', dest='files', nargs=2, required=True,
        metavar='page.pdf 100', help='输入文件以及重复次数', type=str,
        action=AppendInputAction
    )

    split = tools.add_parser(
        name="split", description="将 PDF 分割为不同部分, 输出至目标文件中",
    )

    split.add_argument(
        "origin", help="原文件", metavar="origin.pdf",
        action=SetFilePathAction
    )

    split.add_argument(
        "-s", "--split", help="输出文件, 以及抽取的页码, 连续页码用 - 间断页码用 ,. 连续页码为闭区间", metavar="exam.pdf 1-19,2,34",
        nargs=2, action=ParsePagesAction, required=True
    )


    return parser

def _main(args):

    if args.cmd == 'merge':
        from .merge import merge
        merge(args)
    elif args.cmd == 'split':
        from .split import split
        split(args)


def main():
    args = _get_parser().parse_args()
    _main(args)
