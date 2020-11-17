# 0.3.1

1. 修改了 split 命令使用的文件名模板，使用 Python format 风格的占位符代替 C 风格的
2. 修复了 merge 时 pdf 对象找不到 extends 方法的问题
3. 修复了 split 无法写入文件的问题
4. 在 merge 和 split 中引入了进度条

# 0.3.0

1. 用 pikepdf 2.0.0 重构了项目并完全去除了 PyPDF2 依赖
2. 重新设计了 merge 和 split 的使用方式，去除了繁杂的特定语法
3. 现在所有命令都可以通过 `-o` 指定输出路径，不再只能覆写源文件

# 0.2.0alpha

1. 用 pikepdf 重构了 merge 和 split 功能
