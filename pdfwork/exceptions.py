class PdfWorkException(Exception):
    "pdfwork 包的基础异常"
    pass


class OutlineParseError(Exception):
    "在解析大纲源码时发生的异常"
    pass
