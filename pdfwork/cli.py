"""PdfWork 的命令行入口
"""
from argparse import ArgumentParser

__all__ = ("cli_main", )


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
    merge.add_argument("-o", help="合并后文件的输出路径，如果不蹑着，则输出到 stdout", dest="output", required=False, default=None)

    split.add_argument("-i", help="输入一个PDF文件，将其分割", dest="input", required=False, default=None)
    split.add_argument("-o", help="输出文件的路径和它们所分走的页码", dest="output", required=True)

    outline.add_argument("pdf", help="PDF文件的路径")
    import_outline.add_argument("-i",
                                help="存储目录大纲信息的文本文件，如果不设置，将从 stdin 读取",
                                dest="input",
                                required=False,
                                default=None)
    import_outline.add_argument("--offset", help="页码的偏移量", dest="offset", required=False, default=0, type=int)

    export_outline.add_argument("-o", help="目录信息保存路径，如果为 None，则输出至 stdout", dest="output")

    return p
