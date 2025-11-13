# Markdown文档模板（带YAML元数据）

---
title: "[文档名称]"
document-number: "[文档编号]"
project-name: "[项目名称]"
version: "v1.0"
date: "YYYY-MM-DD"
author: "[编制人姓名]"
organization: "[编制单位]"

# PDF格式设置（使用pandoc转换为PDF时生效）
pdf-engine: xelatex
mainfont: "SimSun"          # 宋体（中文正文）
sansfont: "SimHei"          # 黑体（中文标题）
monofont: "Consolas"        # 等宽字体（代码）
fontsize: 12pt              # 正文字号：小四号（12pt）
linestretch: 1.5            # 行距：1.5倍
geometry:
  - margin=2.5cm            # 页边距：上下左右均为2.5cm
  - a4paper                 # 纸张：A4

# 页眉页脚设置（使用LaTeX命令）
header-includes:
  - \usepackage{fancyhdr}
  - \usepackage{lastpage}
  - \pagestyle{fancy}
  - \fancyhead[L]{\leftmark}                    # 页眉左侧：当前章节名
  - \fancyhead[R]{v1.0}                         # 页眉右侧：版本号
  - \fancyfoot[C]{第\thepage\ 页\ 共\pageref{LastPage}\ 页}  # 页脚中间：页码
  - \fancyfoot[R]{2025-11-05}                   # 页脚右侧：编制日期
  - \fancyfoot[L]{[编制单位]}                    # 页脚左侧：编制单位

# 字体设置
CJKmainfont: "SimSun"       # 中文主字体：宋体
---

# [文档编号] [文档名称]

## 文档变更记录

| 版本号 | 变更日期 | 变更内容 | 变更人 | 审核人 |
|-------|---------|---------|--------|--------|
| v1.0 | YYYY-MM-DD | 初始版本 | [姓名] | [姓名] |

---

## 目录

<!-- 目录会自动生成，或使用工具生成 -->

---

## 1. 引言

### 1.1 目的

本文档旨在...

### 1.2 范围

本文档适用于...

---

## 说明

**格式控制说明**：

1. **YAML元数据**：文件开头的`---`之间的内容是格式参数，用于控制PDF转换时的格式
2. **标题格式**：使用Markdown标准语法（`#`、`##`、`###`），转换时会自动应用格式
3. **段落格式**：正文段落会自动应用YAML中定义的字体和字号
4. **表格格式**：Markdown表格会转换为符合标准的表格格式

**转换命令**：

```bash
# 转换为PDF
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  --template=template.tex \
  -V mainfont="SimSun" \
  -V fontsize=12pt \
  -V geometry:margin=2.5cm

# 转换为DOCX（使用参考文档）
pandoc input.md -o output.docx \
  --reference-doc=reference.docx
```

---

**文档状态**: 草稿  
**最后更新**: YYYY-MM-DD

