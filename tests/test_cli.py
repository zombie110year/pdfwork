from argparse import Namespace
from typing import *

import pytest

from pdfwork.cli import cli_parser


@pytest.mark.parametrize("argv, namesp", [
    (
        ["merge", "-i", "p1.pdf:1,2,3|p2.pdf:4,5,6"],
        Namespace(opera="merge", input="p1.pdf:1,2,3|p2.pdf:4,5,6", output=None),
    ),
    (
        ["merge", "-i", "p1.pdf:1,2,3|p2.pdf:4,5,6", "-o", "out.pdf"],
        Namespace(opera="merge", input="p1.pdf:1,2,3|p2.pdf:4,5,6", output="out.pdf"),
    ),
    (
        ["split", "-o", "p1.pdf:1,2,3|p2.pdf:5,6,7"],
        Namespace(opera="split", input=None, output="p1.pdf:1,2,3|p2.pdf:5,6,7"),
    ),
    (
        ["split", "-i", "full.pdf", "-o", "p1.pdf:1,2,3|p2.pdf:5,6,7"],
        Namespace(opera="split", input="full.pdf", output="p1.pdf:1,2,3|p2.pdf:5,6,7"),
    ),
    (
        ["outline", "import", "abc.pdf"],
        Namespace(opera="outline", outlinecmd="import", pdf="abc.pdf", input=None, offset=0),
    ),
    (
        ["outline", "import", "-i", "outline.txt", "abc.pdf"],
        Namespace(opera="outline", outlinecmd="import", pdf="abc.pdf", input="outline.txt", offset=0),
    ),
    (
        ["outline", "import", "--offset", "12", "abc.pdf"],
        Namespace(opera="outline", outlinecmd="import", pdf="abc.pdf", input=None, offset=12),
    ),
    (
        ["outline", "import", "-i", "menu.txt", "--offset", "12", "abc.pdf"],
        Namespace(opera="outline", outlinecmd="import", pdf="abc.pdf", input="menu.txt", offset=12),
    ),
    (
        ["outline", "export", "abc.pdf"],
        Namespace(opera="outline", outlinecmd="export", pdf="abc.pdf", output=None),
    ),
    (
        ["outline", "export", "-o", "menu.txt", "abc.pdf"],
        Namespace(opera="outline", outlinecmd="export", pdf="abc.pdf", output="menu.txt"),
    ),
    (
        ["outline", "erase", "abc.pdf"],
        Namespace(opera="outline", outlinecmd="erase", pdf="abc.pdf"),
    ),
])
def test_cli_parser(argv: List[str], namesp):
    p = cli_parser()
    args = p.parse_args(argv)
    assert vars(args) == vars(namesp)
