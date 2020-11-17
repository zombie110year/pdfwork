"""PdfWork 的命令行入口
"""
from argparse import ArgumentParser
from argparse import Namespace
from typing import *

from . import __version__
from .actions import *

__all__ = ("cli_main", )


def cli_parser():
    p = ArgumentParser("pdfwork", description="对 PDF 进行拆分、合并、书签等操作")
    p.add_argument("--version",
                   action="version",
                   version=f"pdfwork({__version__}) of zombie110year")
    opera = p.add_subparsers(title="指令", description="一级子命令", dest="opera")
    merge = opera.add_parser("merge", help="合并 PDF 文件，可通过命令行或 stdin 输入文件路径")
    split = opera.add_parser("split",
                             help="将 PDF 文件拆分为单页的 PDF 文件，以 0%%d.pdf 的风格命名")
    outline = opera.add_parser("outline", help="处理 PDF 文件的书签")
    outline_action = outline.add_subparsers(title="书签指令",
                                            description="针对书签可进行的操作",
                                            dest="outlinecmd")
    import_outline = outline_action.add_parser("import", help="从文本导入书签")
    export_outline = outline_action.add_parser("export", help="从 PDF 导出书签")
    erase_outline = outline_action.add_parser("erase", help="抹除书签")

    merge.add_argument("-i",
                       help=("按顺序输入需要合并的文件。如果不提供，则从 stdin 读取；"
                             "如果输入以 @ 开头，如 @filelist.txt 则从此文件中读取路径，每行一个。"),
                       dest="input",
                       nargs="*")

    merge.add_argument("-o",
                       help="合并后文件的输出路径",
                       dest="output",
                       required=True,
                       default=None)

    split.add_argument("-i",
                       help="输入一个 PDF 文件，将其分割成一系列单页 PDF",
                       dest="input",
                       required=True)
    split.add_argument("-o",
                       help=("输出文件的路径，占位符 `%%d` 代表页面的页码（从 1 开始）；"
                             "如果仅输入目录名，则自动推导页码格式化样式"),
                       dest="output",
                       required=True)

    outline.add_argument("--pdf", required=True, help="要处理的 PDF 文件的路径")

    import_outline.add_argument("-i",
                                help="存储目录大纲信息的文本文件，默认从 stdin 读取",
                                dest="input",
                                required=False,
                                default=None)
    import_outline.add_argument("--offset",
                                help=("逻辑页码和物理页码的偏移量。"
                                      "可通过观察正文第 1 页在 PDF 中的物理页码，求两者的差。"
                                      "例如，正文第 1 页在 PDF 中处于第 33 页，则 offset=32。"
                                      "默认为 0"),
                                dest="offset",
                                required=False,
                                default=0,
                                type=int)
    import_outline.add_argument("-o",
                                help="添加了书签的 PDF 输出路径",
                                dest="output",
                                required=True)

    export_outline.add_argument("-o",
                                help="目录信息保存路径，默认输出至 stdout",
                                dest="output")

    erase_outline.add_argument("-o",
                               help="被抹除了书签的 PDF 文件保存路径",
                               dest="output",
                               required=True)

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
            action_import_outline(args.pdf, args.input, args.output,
                                  args.offset)
        elif args.outlinecmd == "export":
            action_export_outline(args.pdf, args.output)
        elif args.outlinecmd == "erase":
            action_erase_outline(args.pdf, args.output)
