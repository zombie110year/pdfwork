"测试解析目录的能力"
import pytest

from pdfwork.outline import parse_outline_iter

test_str = ("晶体与晶体学 @ 1\n"
            "    晶体学概述\n"
            "        引言\n"
            "        经典晶体学 @ 2\n"
            "        近代晶体学\n"
            "    晶体与晶体材料\n"
            "        晶体的概念\n"
            "        晶体的基本特征 @ 3\n"
            "        非晶体 @ 5\n"
            "        液晶 @ 6\n")

test_str_out = [
    (0, "晶体与晶体学", 1),
    (1, "晶体学概述", 1),
    (2, "引言", 1),
    (2, "经典晶体学", 2),
    (2, "近代晶体学", 2),
    (1, "晶体与晶体材料", 2),
    (2, "晶体的概念", 2),
    (2, "晶体的基本特征", 3),
    (2, "非晶体", 5),
    (2, "液晶", 6),
]


def test_parse_outline_iter():
    out = parse_outline_iter(test_str)
    for got, exp in zip(out, test_str_out):
        assert got == exp
