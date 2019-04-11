"""实用工具
"""
import re
from argparse import Action, _copy_items
from pathlib import Path


class AppendInputAction(Action):
    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None
    ):
        if nargs != 2:
            raise ValueError("nargs != 2")

        super(AppendInputAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = _copy_items(items)

        pair = (
            Path(values[0]),
            int(values[1]),
        )

        items.append(pair)

        setattr(namespace, self.dest, items)


class PageNumberError(ValueError):
    pass


class PageNumberParser:
    """
    将形如 "0-9,12-16" 这样的字符串, 解析为多个 (begin, end) 对.
    """
    NUMBER_PATTERN = re.compile(r"^\d+$")
    SEQUENCE_PATTERN = re.compile(r"^\d+-\d+$")

    def __init__(self):
        pass

    def parse(self, sentence: str):
        """解析形如 "1-2,3-4, 5" 的字符串

        "1-2,3-4,5" -> [(1, 3), (3, 5), (5, 6)]

        :param str sentence: 形如 "1-2,3-4" 这样的字符串
        :return: [(begin, end), (begin, end), ...]
        :rtype: [(int,int)]
        """

        result = []
        code_pair = sentence.split(',')
        for pair in code_pair:
            if re.match(self.NUMBER_PATTERN, pair):
                result.append((int(pair), int(pair) + 1))
            elif re.match(self.SEQUENCE_PATTERN, pair):
                begin, end = pair.split('-')
                begin = int(begin)
                end = int(end)
                if begin > end:
                    raise PageNumberError(
                        "连续页码中起始值不能超过终止值 {}-{}".format(begin, end))
                else:
                    result.append((begin, end + 1))
            else:
                raise PageNumberError("页码参数形式错误!")

        return result


class ParsePagesAction(Action):
    """解析 -e 参数, 分析输出文件以及解析页码

    :return: (Path('output.pdf'), [(begin, end), (begin, end), ...])
    :rtype: (Path, [(int, int)])
    """

    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):

        if nargs != 2:
            raise ValueError("nargs != 2")

        super(ParsePagesAction, self).__init__(option_strings, dest, nargs=nargs, const=const,
                                               default=default, type=type, choices=choices, required=required, help=help, metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, [])
        items = _copy_items(items)

        page_number_parser = PageNumberParser()

        pair = (
            Path(values[0]),
            page_number_parser.parse(values[1]),
        )

        items.append(pair)

        setattr(namespace, self.dest, items)


class SetFilePathAction(Action):
    """设置输出格式, 得到的 output 参数的类型为 Path
    """

    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None
    ):
        super(SetFilePathAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        path = Path(values)
        setattr(namespace, self.dest, path)


class PositiveIndexList(list):
    """当 index 小于 0 时, 返回值总是 None
    """

    def __getitem__(self, index):
        if index < 0:
            return None
        else:
            return super().__getitem__(index)
