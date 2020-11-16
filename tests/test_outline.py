"测试解析目录的能力"
import pytest

from pdfwork.parse_outline import parse_line

test_str = (
    "晶体与晶体学 @ 1\n",
    "    晶体学概述\n",
    "        引言\n",
    "        经典晶体学 @ 2\n",
    "        近代晶体学\n",
    "    晶体与晶体材料\n",
    "        晶体的概念\n",
    "        晶体的基本特征 @ 3\n",
    "        非晶体 @ 5\n",
    "        液晶 @ 6\n",
)

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
    last_index = 0
    for src, out in zip(test_str, test_str_out):
        parsed, _ = parse_line(src, "    ", last_index, None)
        last_index = parsed.index
        assert parsed.indent == out[0]
        assert parsed.title == out[1]
        assert parsed.index == out[2]