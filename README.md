# Pdf Work

# Install

```
    git clone https://github.com/zombie110year/pdfwork.git
    cd pdfwork
    python setup.py install
```

# Usage

```
$ pdf-merge --help
usage: pdf-merge [-h] [-o example.pdf] -i page.pdf 100

merge pdf files

optional arguments:
  -h, --help            show this help message and exit
  -o example.pdf, --output example.pdf
                        output file path
  -i page.pdf 100 page.pdf 100
                        input file path and repeat times
```

## Example

```sh
    $ pdf-merge -o wanted.pdf -i cover.pdf 1 -i main.pdf 3 -i back.pdf 1
```

You got:

```
    wanted.pdf ->

        cover
        main
        main
        main
        back
```
