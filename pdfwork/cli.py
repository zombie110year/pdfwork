"""PdfWork 的命令行入口
"""
from typing import List
from typing import Optional

import pikepdf
import typer

from . import __version__
from .actions import action_erase_outline
from .actions import action_export_outline
from .actions import action_import_outline
from .actions import action_merge
from .actions import action_optimize
from .actions import action_split

__all__ = ("cli_main", )

cli_main = typer.Typer(name="pdfwork")


@cli_main.command()
def version():
    "显示应用程序版本"
    typer.echo(f"pdfwork {__version__}")
    typer.echo(f"+ pikepdf {pikepdf.__version__}")


@cli_main.command()
def merge(pdfs: List[str] = typer.Argument(
    ..., help="PDF 文档路径，如果为 `@` 开头的文本文件，则按照每行一个的规则读取其中的文件路径"),
          out: str = typer.Option(..., "-o", help="输出文件路径", metavar="PATH")):
    """合并两个或多个 PDF 文档，注意，书签可能丢失，需要提前导出备份：

        pdfwork outline export -o outlines.txt this.pdf
    """
    return action_merge(pdfs, out)


@cli_main.command()
def split(pdf: str = typer.Argument(..., help="输入文件路径"),
          out: Optional[str] = typer.Option(".",
                                            "-o",
                                            help="输出路径，用 {0:d} 表示序列化模板",
                                            metavar="PATH TEMPLATE")):
    "分隔 PDF 文档为单页文档"
    return action_split(pdf, out)


outline = typer.Typer(name="outline", help="操作 PDF 中的书签对象")
cli_main.add_typer(outline)


@outline.command("erase")
def erase_outline(pdf: str,
                  out: str = typer.Option(...,
                                          "-o",
                                          help="输出路径",
                                          metavar="PATH")):
    "抹除 PDF 中的书签"
    action_erase_outline(pdf, out)


@outline.command("import")
def import_outline(
        pdf: str = typer.Argument(..., help="PDF 文件路径"),
        input: Optional[str] = typer.Option(
            None,
            "-i",
            help="记录书签信息的文本文件路径，留空则从 stdin 读入",
            metavar="PATH",
        ),
        out: str = typer.Option(..., "-o", help="新生成 PDF 文件的保存路径"),
        offset: int = typer.Option(
            0, help="物理页码对逻辑页码的差。例如，正文第 1 页在 PDF 文件的第 33 页，则认为偏差为 32")):
    "从文本文件导入书签到 PDF"
    action_import_outline(pdf, input, out, offset)


@outline.command("export")
def export_outline(pdf: str = typer.Argument(..., help="PDF 文件路径"),
                   out: Optional[str] = typer.Option(
                       None,
                       "-o",
                       help="输出书签文本文件的路径，默认输出到 stdout",
                       metavar="PATH")):
    "将 PDF 中的书签导出为文本格式"
    return action_export_outline(pdf, out)


@cli_main.command()
def optimize(pdf: str = typer.Argument(..., help="PDF 文件路径"),
             output: Optional[str] = typer.Option(None, "-o", help="输出路径")):
    "优化 PDF 文件：线性化、去重、去除未引用资源"
    action_optimize(pdf, output)
