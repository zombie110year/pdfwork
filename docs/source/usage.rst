##################
PdfWork 的使用方法
##################

基于 PyPDF2 封装的一个便于使用的 pdf 处理命令行工具。
提供以下功能：

-   书签（也叫目录）
    -   导入、导入、抹除PDF文件中的书签
-   合并 PDF
-   分割 PDF

安装方法
========

可以通过 pip 或 pipx 安装：

.. code:: sh

    # pip
    pip install pdfwork
    # pipx
    pipx install pdfwork

使用
====

对于 merge 和 split，其命令行参数呈现如下形式：

.. code:: text

    pdfwork {merge|split} -i '输入' -o '输出'

输入和输出中如果要设定多个文件（片段）的话，需要按照 ``<路径>:<页码>|<path>:<page range>``
的格式排列，例如：

-   将文件 example.pdf 拆分成 p1, p2, p3 三个部分：

.. code:: text

    pdfwork split -i example.pdf -o 'p1.pdf:1,3,5,7,9|p2.pdf:0,2,4,6,8|p3.pdf:2,3,5,7,11'

-   将文件 p1, p2, p3 合并成一个文件：

.. code:: text

    pdfwork merge -i 'p1.pdf:-|p2.pdf:-|p3.pdf:-' -o merged.pdf

对于导入导出书签，其命令行参数呈现如下形式：

.. code:: text

    pdfwork outline {erase|import|export} [-i outlines.txt] [-o outlines.txt] <被操作的PDF文件路径>

例如：

-   将 PDF 中的书签导出到 outlines.txt 文件中

.. code:: text

    pdfwork outline export -o outlines.txt example.pdf

-   将 outlines.txt 的书签导入到 PDF 文件中（原有的书签被抹除）

.. code:: text

    pdfwork outline import -i outlines.txt example.pdf

-   抹除 PDF 文件中的书签

.. code:: text

    pdfwork outline erase example.pdf

.. warning::

    在 outline 子命令下的 PDF 文件路径参数必须在最后。

页码范围的表示法详见 :class:`pdfwork.model.MultiRange` 的说明文档。
