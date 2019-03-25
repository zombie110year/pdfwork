import unittest as t
from pathlib import Path
from hashlib import md5

from pdfwork.entries import _get_parser, _main

class NameSpace:
    pass


class TestParser(t.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = _get_parser()

    def test_parse_args(self):
        args = self.parser.parse_args(
            ['split', 'origin.pdf', '-s', 'output.pdf', '10']
        )

        self.assertEqual(
            args.origin, Path("origin.pdf")
        )

        self.assertEqual(
            args.split[0][0], Path('output.pdf')
        )

        self.assertEqual(
            args.split[0][1], [(10, 11)]
        )

    def test_multi_pages(self):
        args = self.parser.parse_args(
            ['split', 'origin.pdf', '-s', 'output.pdf', '10,20-30,99-300,17']
        )

        value = args.split[0][1]

        self.assertEqual(
            value, [
                (10, 11),
                (20, 31),
                (99, 301),
                (17, 18),
            ]
        )
