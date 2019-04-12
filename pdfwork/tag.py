"""PDF 书签
"""
import re
from hashlib import sha256
from pathlib import Path

from PyPDF2 import PdfFileReader, PdfFileWriter

from .utils import PositiveIndexList

# 定义 tagfile 文法 begin
TAG = re.compile(r"^( *)([^\s][\S ]+?)( *@ *)(\d+?)(?: *)$")
TAG_NAME = re.compile(r"([^\s][\S ]+?)(?: *@)")
TAG_PAGE = re.compile(r"(?:@ *)(\d+?)(?: *)$")
TAG_INDENT = re.compile(r"^( *)")

tag_check = lambda x: True if TAG.match(x) else False

# 定义 tagfile 文法 end

def tag(args):
    """args 为携带了该功能将使用的参数的命名空间

    操作 PDF 文件的书签.

    :param args.pdfpath: 将操作的 PDF 文件路径
    :param args.offset:  页码偏移量
    :param args.tagfile: 指定 tagfile 路径
    :param args.export:  指定是导出模式, 或者导入模式
    """
    if args.export:
        export_tag(args.pdfpath.resolve(), args.tagfile.resolve())
    else:
        import_tag(args.pdfpath.resolve(), args.tagfile.resolve(), args.offset)

def import_tag(pdfpath: Path, tagfile: Path, offset: int):
    """导入书签

    使用以下参数:

    :param pdfpath: PDF 文件路径
    :param tagfile:  指定 tagfile 路径, 读取其中的 taginfo
    :param offset: 设置页码偏移量, 在对每一个页码操作时, 将会加上此量
    """
    file = PdfFileWriter()
    _ = PdfFileReader(str(pdfpath.absolute()))
    file.appendPagesFromReader(_)

    taginfos = _yield_taginfo_from_txt(tagfile)

    stack = PositiveIndexList()

    file = _write_taginfo_to_pdfwriter(file, taginfos, offset, stack)

    with pdfpath.open("wb") as writer:
        file.write(writer)

def export_tag(pdfpath: Path, tagfile: Path):
    """导出书签

    使用以下参数:

    :param pdfpath: PDF 文件路径
    :param tagfile:  将 taginfo 输出至 tagfile
    """

    with tagfile.open("wb") as writer:
        writer.write('非常抱歉, 此功能暂未实现'.encode("utf-8"))

def _yield_taginfo_from_txt(tagfile: Path):
    with tagfile.open("rt", encoding="utf-8") as file:
        for line in file.readlines():
            line = line.rstrip()
            if TAG.match(line):
                name = TAG_NAME.findall(line)[0]
                page = int(TAG_PAGE.findall(line)[0])
                indent = TAG_INDENT.findall(line)[0].count(" ") // 4

                yield (name, page, indent)

            else:
                raise ValueError("无效的表示法: {}".format(line))


def _write_taginfo_to_pdfwriter(writer: PdfFileWriter, taginfos, offset: int, stack: PositiveIndexList):
    """将 taginfos 中的内容写入 PdfFileWriter 中.

    :param writer: 一个 PdfFileWriter 实例
    :param taginfos: 由 :func:`_yield_taginfo_from_txt` 返回的生成器
    :return: 返回被修改的 writer
    """
    last_indent = 0

    name, page, indent = next(taginfos)
    stack.append(writer.addBookmark(name, page + offset, fit="/FitB"))

    for name, page, indent in taginfos:
        if indent == last_indent:
            stack[-1] = writer.addBookmark(name, page + offset, parent=stack[-2])
        elif indent == last_indent + 1:
            stack.append(writer.addBookmark(name, page + offset, parent=stack[-1]))
        elif indent < last_indent:
            for i in range(last_indent - indent):
                stack.pop()
            stack[-1] = writer.addBookmark(name, page + offset, parent=stack[-2])
        else:
            pass

        last_indent = indent

    return writer
