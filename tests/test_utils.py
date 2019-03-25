import unittest as t
from pdfwork.utils import PageNumberParser, PageNumberError

QA_set = [
    ("1", [(1, 2)]),
    ("1-1", [(1, 2)]),
    ("1-2", [(1, 3)]),
    ("1,2", [(1, 2), (2, 3)]),
    ("1,0", [(1, 2), (0, 1)]),
    ("1-9,2-10", [(1, 10), (2, 11)]),
]

QA_set_error = [
    "",
    "-",
    ",",
    "1-0",
    "-1",
]


class TestPageNumberParser(t.TestCase):
    def setUp(self):
        self.worker = PageNumberParser()

    def test_common_input(self):
        for q, a in QA_set:
            self.assertListEqual(
                self.worker.parse(q), a
            )


    def test_error_input(self):
        for q in QA_set_error:
            self.assertRaises(PageNumberError, self.worker.parse, q)
