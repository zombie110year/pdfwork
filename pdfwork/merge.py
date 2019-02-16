"""合并 PDF 文件

"""

from argparse import ArgumentParser
from pathlib import Path

import PyPDF2 as pdf


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
