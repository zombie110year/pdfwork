import unittest as t
from pathlib import Path

from pdfwork.tag import (TAG_INDENT, TAG_NAME, TAG_PAGE,
                         _yield_taginfo_from_txt, tag_check, _write_taginfo_to_pdfwriter)
from pdfwork.utils import PositiveIndexList

class TestTag(t.TestCase):

    def setUp(self):
        self.tagfile = Path("tests/tagfile_test.txt")
        self.pdfpath = Path("tests/merged.pdf")

    def test_TAG_common(self):
        common_cases = [
            ("某一页@10", ("某一页", "10", "")),
            ("某1页@10", ("某1页", "10", "")),
            (" 第二页@12", ("第二页", "12", " ")),
            ("第三页 @ 13 ", ("第三页", "13", "")),
            ("第 四页@14", ("第 四页", "14", "")),
        ]

        for question, answer in common_cases:
            name = TAG_NAME.findall(question)[0]
            page = TAG_PAGE.findall(question)[0]
            indent = TAG_INDENT.findall(question)[0]
            self.assertEqual(
                name, answer[0]
            )
            self.assertEqual(
                page, answer[1]
            )
            self.assertEqual(
                indent, answer[2]
            )

    def test_tag_check(self):
        cases = [
            ("某一页@10", True),
            ("某1页@10", True),
            (" 第二页@12", True),
            ("第一页@1", True),
            ("第二页 @2", True),
            ("    第三页@ 3", True),
            ("    第四页 @ 4", True),
            ("        第五页@5", True),
            ("第六页@6", True),
            ("    第七页@7", True),
            ("第八页@8", True),
            ("\t第二张@144", False),
            ("第一张 21", False),
            ("1123 123", False),
            ("", False),
            ("最后不是数字@二十", False)
        ]

        for q, a in cases:
            self.assertEqual(
                tag_check(q), a, msg="{}".format(q)
            )

    def test_yield_taginfo_from_tet(self):
        answers = [
            ("1.第一页", 1, 0),
            ("1.第二页", 2, 0),
            ("2.第三页", 3, 1),
            ("2.第四页", 4, 1),
            ("3.第五页", 5, 2),
            ("1.第六页", 6, 0),
            ("2.第七页", 7, 1),
            ("1.第八页", 8, 0),
        ]
        tagfile = Path("tests/tagfile_test.txt")
        taginfos = _yield_taginfo_from_txt(self.tagfile)
        for i, j, k in answers:
            name, page, indent = next(taginfos)
            self.assertEqual(
                name, i
            )
            self.assertEqual(
                page, j
            )
            self.assertEqual(
                indent, k, msg="{}".format(name)
            )


    def test_indent(self):
        stack = PositiveIndexList()
        taginfos = _yield_taginfo_from_txt(self.tagfile)

        last_indent = 0

        name, page, indent = next(taginfos)
        stack.append((name, page, None))
        current_indent = len(stack) - 1

        for name, page, indent in taginfos:
            if indent == last_indent:
                stack[-1] = (name, page, stack[-2])
            elif indent == last_indent + 1:
                stack.append((name, page, stack[-1]))
            elif indent < last_indent:
                for i in range(last_indent - indent):
                    stack.pop()
                stack[-1] = (name, page, stack[-2])

            current_indent = len(stack) - 1
            self.assertEqual(
                indent, current_indent, msg="{}".format(name)
            )
            last_indent = indent
