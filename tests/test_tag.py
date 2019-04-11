import unittest as t
from pdfwork.tag import _yield_taginfo_from_txt
from pdfwork.tag import TAG_NAME, TAG_PAGE, TAG_INDENT
from pdfwork.tag import tag_check


class TestTag(t.TestCase):

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
        pass
