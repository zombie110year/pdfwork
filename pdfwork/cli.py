"""PdfWork 的命令行入口
"""
from argparse import ArgumentParser
from argparse import Namespace
from typing import *

from .actions import *

__all__ = ("cli_main", )

how_to_calculate_offset = """
计算 offset 的参考意见
======================

对于大部分 PDF 阅读器，其页码的起点是 1，
而本程序为 0，当你在书籍的目录页面查找某章节的页码时，
其起点又是从正文处以 1 开始的。

因此，在计算 offset 时，以正文起点页在 PDF 中所处页码为 n，
则 offset 为 n - 1。
"""

def cli_parser():
    p = ArgumentParser("pdfwork", description="manipulate PDFs.")
    opera = p.add_subparsers(title="Commands", description="subcommands", dest="opera")
    merge = opera.add_parser("merge")
    split = opera.add_parser("split")
    outline = opera.add_parser("outline")
    outline_action = outline.add_subparsers(title="Outline Actions",
                                            description="import, export or erase",
                                            dest="outlinecmd")
    import_outline = outline_action.add_parser("import")
    export_outline = outline_action.add_parser("export")
    erase_outline = outline_action.add_parser("erase")

    merge.add_argument("-i", help="输入文件", dest="input", required=True)
    merge.add_argument("-o", help="合并后文件的输出路径，默认输出到 stdout", dest="output", required=False, default=None)

    split.add_argument("-i", help="输入一个PDF文件，将其分割", dest="input", required=False, default=None)
    split.add_argument("-o", help="输出文件的路径和它们所分走的页码", dest="output", required=True)

    outline.add_argument("pdf", help="PDF文件的路径")
    import_outline.add_argument("-i",
                                help="存储目录大纲信息的文本文件，默认从 stdin 读取",
                                dest="input",
                                required=False,
                                default=None)
    import_outline.add_argument("--offset", help="页码的偏移量", dest="offset", required=False, default=0, type=int)

    export_outline.add_argument("-o", help="目录信息保存路径，默认输出至 stdout", dest="output")

    return p


class Args(Namespace):
    opera: str
    outlinecmd: str
    input: Optional[str]
    output: Optional[str]
    pdf: str
    offset: int


def cli_main():
    p = cli_parser()
    args: Args = p.parse_args()

    if args.opera == "merge":
        action_merge(args.input, args.output)
    elif args.opera == "split":
        action_split(args.input, args.output)
    elif args.opera == "outline":
        if args.outlinecmd == "import":
            action_import_outline(args.pdf, args.input, args.offset)
        elif args.outlinecmd == "export":
            action_export_outline(args.pdf, args.output)
        elif args.outlinecmd == "erase":
            action_erase_outline(args.pdf)
