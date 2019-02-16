# Pdf Work

# Install

```
    git clone https://github.com/zombie110year/pdfwork.git
    cd pdfwork
    python setup.py install
```

# Usage

```
    usage: pdfwork [-h] {merge,extract} ...

        处理 PDF 文件

        optional arguments:
        -h, --help       show this help message and exit

        sub-cmd:
        {merge,extract}  子命令

    usage: pdfwork merge [-h] [-o example.pdf] -i page.pdf 100 page.pdf 100

        合并多个 PDF 文件

        optional arguments:
        -h, --help            show this help message and exit
        -o example.pdf, --output example.pdf
                                合并输出到 PDF 文件
        -i page.pdf 100 page.pdf 100
                                输入文件以及重复次数

    usage: pdfwork extract [-h] -e exam.pdf 1-19,2,34 exam.pdf 1-19,2,34
                        origin.pdf

        提取 PDF 的一部分, 输出至目标文件中

        positional arguments:
        origin.pdf            原文件

        optional arguments:
        -h, --help            show this help message and exit
        -e exam.pdf 1-19,2,34 exam.pdf 1-19,2,34, --extract exam.pdf 1-19,2,34 exam.pdf 1-19,2,34
                                输出文件, 以及抽取的页码, 连续页码用 - 间断页码用 ,. 连续页码为闭区间
```

## Example

```sh
    $ pdfwork merge -o wanted.pdf -i cover.pdf 1 -i main.pdf 3 -i back.pdf 1
    $ pdfwork extract origin.pdf -e first.pdf 1,3,5 -e second.pdf 10-12
```

You got:

```
    wanted.pdf ->

        cover
        main
        main
        main
        back

    first.py ->

        origin (p1)
        origin (p3)
        origin (p5)

    second.pdf ->

        origin (p10)
        origin (p11)
        origin (p12)
```
