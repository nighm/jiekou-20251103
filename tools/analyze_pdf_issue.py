#!/usr/bin/env python3
"""
分析PDF转换问题
检查代码块、文本格式等转换是否正确
"""

import re
from pathlib import Path

# 读取MD源文件
md_file = Path('docs/templates/DP_文档计划模板.md')
tex_file = Path('temp/DP_文档计划模板.tex')

print("=" * 60)
print("PDF转换问题分析")
print("=" * 60)
print()

# 1. 分析MD源文件中的代码块
print("1. MD源文件中的代码块分析")
print("-" * 60)
with open(md_file, encoding='utf-8') as f:
    md_content = f.read()

# 查找"组织架构"部分的代码块
org_match = re.search(r'### 组织架构.*?```\n(.*?)\n```', md_content, re.DOTALL)
if org_match:
    code_content = org_match.group(1)
    print(f"找到代码块内容（{len(code_content)}字符）：")
    print(code_content[:200])
    chinese_pattern = r'[\u4e00-\u9fa5]'
    tree_pattern = r'[├└│─]'
    print(f"\n包含中文字符：{bool(re.search(chinese_pattern, code_content))}")
    print(f"包含特殊字符（├└│）：{bool(re.search(tree_pattern, code_content))}")
else:
    print("未找到组织架构代码块")

print()

# 2. 分析TeX文件中的对应部分
print("2. TeX文件中的对应部分分析")
print("-" * 60)
with open(tex_file, encoding='utf-8') as f:
    tex_content = f.read()

# 查找组织架构部分
tex_match = re.search(r'\\subsubsection\{组织架构\}.*?\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}', tex_content, re.DOTALL)
if tex_match:
    lst_content = tex_match.group(1)
    print(f"找到lstlisting内容（{len(lst_content)}字符）：")
    print(lst_content[:200])
    chinese_pattern = r'[\u4e00-\u9fa5]'
    escape_pattern = r'\\\\'
    tree_pattern = r'[├└│─]'
    print(f"\n包含中文字符：{bool(re.search(chinese_pattern, lst_content))}")
    print(f"包含转义字符：{bool(re.search(escape_pattern, lst_content))}")
    print(f"包含特殊字符（├└│）：{bool(re.search(tree_pattern, lst_content))}")
    
    # 检查是否有LaTeX转义导致的问题
    if '\\textbackslash' in lst_content:
        print("⚠️ 发现textbackslash转义，可能影响显示")
    if '\\{' in lst_content:
        print("⚠️ 发现转义的大括号")
else:
    print("未找到组织架构的lstlisting代码块")

print()

# 3. 分析问题类型
print("3. 问题类型分析")
print("-" * 60)

# 检查代码块转换函数的问题
print("可能的问题：")
print("1. 代码块中的中文字符可能在转义时被破坏")
print("2. lstlisting环境可能不支持某些Unicode字符（如├└│─）")
print("3. 需要配置lstlisting的字体和编码")

print()
print("4. 解决方案建议")
print("-" * 60)
print("方案1：配置lstlisting支持中文")
print("  在模板中添加：\\lstset{basicstyle=\\ttfamily\\fontsize{10.5pt}{12.6pt}\\selectfont}")
print()
print("方案2：树状结构改用其他LaTeX环境")
print("  使用verbatim环境或自定义环境")
print()
print("方案3：检查转义逻辑")
print("  确保代码块中的中文不被错误转义")

