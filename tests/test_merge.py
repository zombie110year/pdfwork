import unittest as t
from hashlib import md5
from pathlib import Path

from pdfwork.merge import _get_parser, merge

from . import NameSpace


class TestParser(t.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = _get_parser()


    def test_set_input(self):
        args = self.parser.parse_args(
            ['-i', 'test.pdf', '100']
        )

        files = args.files

        self.assertIsInstance(
            files, list, "files 是一个列表"
        )

        pair = files[0]

        self.assertIsInstance(
            pair, tuple, "files 中的一组元素为一个元组"
        )

        path, repeat = pair

        self.assertIsInstance(
            path, Path, "Path"
        )

        self.assertIsInstance(
            repeat, int, "repeat 重复次数为 int"
        )


        self.assertEqual(
            path, Path("test.pdf")
        )

        self.assertEqual(
            repeat, 100
        )

    def test_set_output(self):
        args = self.parser.parse_args(
            ['-i', 'test.pdf', '100', '-o', 'output.pdf']
        )

        path = args.output

        self.assertIsInstance(
            path, Path, "输出文件也是 Path"
        )

    def test_default_output(self):
        args = self.parser.parse_args(
            ['-i', 'test.pdf', '100']
        )

        self.assertIsInstance(
            args.output, Path
        )

    @t.skip('argparse 没有在选项缺失时抛出错误, 而是使用 sys.exit, 测试方法未知')
    def test_required_intput_setting(self):
        args = self.parser.parse_args([])

class TestMergePDF(t.TestCase):
    def setUp(self):
        self.file = Path(__file__).parent / "origin.pdf"
        self.target = Path(__file__).parent / "merged.pdf"

    def test_merge_file(self):
        check = Path(__file__).parent / "check.pdf"
        conf = NameSpace()

        conf.files = [
            (self.file, 10)
        ]

        conf.output = self.target

        merge(conf)

        x = md5(); y = md5()

        with check.open("rb") as file:
            x.update(file.read())

        with self.target.open("rb") as file:
            y.update(file.read())

        self.assertEqual(
            x.hexdigest(), y.hexdigest()
        )
