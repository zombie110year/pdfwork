"""提取 pdf 文件内容

可将一个文件中的不同页面或连续页面提取到不同文件::

    pdf-extract origin.pdf -e first.pdf 0-9,13-16,99 -e second.pdf 10-12
"""

from pathlib import Path

import PyPDF2 as pdf


def extract(args):
    """提取 PDF 内容
    """

    reader = pdf.PdfFileReader(str(args.origin.absolute()))

    for output, pages in args.extract:
        writer = pdf.PdfFileWriter()
        for begin, end in pages:
            for i in range(begin, end):
                writer.addPage(
                    reader.getPage(i)
                )
        with output.open("wb") as file:
            writer.write(file)
        del writer
