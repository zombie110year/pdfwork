import unittest as t
from pathlib import Path

from pdfwork.entries import _get_parser

from . import NameSpace


class TestArgSend(t.TestCase):
    def setUp(self):
        self.parser = _get_parser()

    @t.skip("--help 参数是通过 sys.exit() 退出的")
    def test_send_help(self):
        args = self.parser.parse_args(
            ['extract', '--help']
        )

    def test_send_merge(self):
        args = self.parser.parse_args(
            ['merge', '-o', 'output.pdf', '-i', '1.pdf', '1']
        )

        self.assertEqual(
            args.files, [(Path('1.pdf'), 1)]
        )

        self.assertEqual(
            args.output, Path('output.pdf')
        )


    def test_send_extract(self):
        args = self.parser.parse_args(
            ['extract', 'origin.pdf', '-e', 'first.pdf', '1,3,5']
        )

        self.assertEqual(
            args.origin, Path('origin.pdf')
        )

        self.assertEqual(
            args.extract,
            [
                (Path('first.pdf'), [(1,2), (3,4), (5,6)])
            ]
        )
