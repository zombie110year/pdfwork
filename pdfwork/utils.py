from io import BytesIO
from typing import *
from functools import lru_cache


def open_pdf(path: str) -> BytesIO:
    """将 PDF 文件的内容读入 BytesIO 并返回。

    为什么
    ======

    相比现代计算机的内存，PDF 文件最大也不过数百 MB，足够使用。
    将其完全读取入内存，能够提高复用效率。

    另外，也不需要占用文件句柄（描述符），方便对源文件进行覆写。
    """
    with open(path, "rb") as src:
        content = src.read()
    io = BytesIO(content)
    return io
