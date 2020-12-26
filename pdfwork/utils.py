import re
from pathlib import Path
from typing import Callable
from typing import List
from typing import Optional

# mypy 无法导入类型声明
from pikepdf import Outline as PikeOutline  # type: ignore
from pikepdf import OutlineItem
from pikepdf import Pdf

from .outline import Outline

__all__ = ("import_outline", "export_outline")


def export_outline(pdf: Pdf, pike: PikeOutline) -> Outline:
    """将 pdf 中的书签导出为一个 Outline 树
    """
    root = Outline(-1, "OUTLINE ROOT", 0)
    pn_map = make_pagenum_search_table(pdf)

    def tree_copy(subtree: List[OutlineItem], level: int):
        nonlocal root
        for oi in subtree:
            # Destination 结构为 [pageid, action, action_args]
            # https://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
            # 374 页，第 12.3.2.2 章
            pageid = oi.destination[0].to_json().decode()
            pn = pn_map(pageid)
            pn = pn if pn else 0
            o = Outline(level, oi.title, pn + 1)
            root.add_node(o, o.indent)
            tree_copy(oi.children, level + 1)

    tree_copy(pike.root, 0)

    return root


def import_outline(pdfw: Pdf, root: Outline, offset: int):
    """将大纲导入到 pdf 中。
    """
    with pdfw.open_outline() as outlines:
        pikeroot = outlines.root
        seq = [1]
        stack = [root]
        bookmarks = [None]

        def import_sub(o: Outline):
            nonlocal seq
            nonlocal stack
            nonlocal bookmarks

            if o.indent > stack[-1].indent:
                seq.append(1)
            elif o.indent < stack[-1].indent:
                seq = seq[:o.indent + 1]
                seq[o.indent] += 1
            else:
                seq[o.indent] += 1

            seqn = ".".join([f"{i}" for i in seq[:o.indent + 1]])

            bookmark = OutlineItem(
                # title
                f"{seqn} {o.title}",
                # 页码，pikepdf 从 0 开始计数
                o.index + offset - 1,
                # 跳转效果：适应页面
                "Fit")

            if parent := bookmarks[o.indent]:
                parent.children.append(bookmark)
            else:
                pikeroot.append(bookmark)

            if o.indent > stack[-1].indent:
                stack.append(o)
                bookmarks.append(bookmark)
            elif o.indent < stack[-1].indent:
                stack = stack[:o.indent + 2]
                bookmarks = bookmarks[:o.indent + 2]
                stack[o.indent + 1] = o
                bookmarks[o.indent + 1] = bookmark
            else:
                stack[o.indent + 1] = o
                bookmarks[o.indent + 1] = bookmark

            for subtree in o.children:
                import_sub(subtree)

        for node in root.children:
            import_sub(node)


def make_pagenum_search_table(pdf: Pdf) -> Callable[[str], Optional[int]]:
    """构建 《Page Object 标识符》 => 《页码》 查询表。

    返回一个可执行对象，输入标识符便返回对应的页码。
    """
    id2num = {}

    for i, page in enumerate(pdf.pages):
        identifier = page.to_json().decode()
        id2num[identifier] = i

    def query(pageid: str) -> Optional[int]:
        return id2num.get(pageid, None)

    return query


def check_paths_exists(paths: List[str]) -> List[str]:
    """检查文件是否存在
    """
    valid = []
    invalid = []
    for i, p in enumerate(paths):
        path = Path(p)
        if path.exists():
            valid.append(path.absolute().as_posix())
        else:
            invalid.append((i, p))

    if not invalid:
        return valid
    else:
        raise FileNotFoundError(invalid)


def fmt_pat(pat: Optional[str], maxn: int) -> str:
    # 有无 .pdf {}
    # (.pdf, {}) => 文件（可能需要父目录），按指定样式序列化
    # (.pdf, _) => 文件，在后缀按默认样式序列化
    # (_, {}) => 按指定样式序列化目录，然后每个目录下按默认样式序列化
    # (_, _) => 指定目录下的默认序列化

    width = sum([
        1 for _ in range(maxn) if (maxn := maxn // 10) != 0  # type: ignore
    ]) + 1

    if pat is None:
        fmt = f"{{0:0{width}d}}.pdf"
    else:
        have_pdf = pat.endswith(".pdf")
        have_fmt = re.match(r"{.*?[dxob]?}", pat)
        if have_pdf and have_fmt:
            fmt = pat
        elif have_pdf and not have_fmt:
            fmt = pat.replace(".pdf", f"{{0:0{width}d}}.pdf")
        elif not have_pdf and have_fmt:
            fmt = (Path(pat) / f"{{0:0{width}d}}.pdf").as_posix()
        else:
            fmt = (Path(pat) / f"{{0:0{width}d}}.pdf").as_posix()

    return fmt
