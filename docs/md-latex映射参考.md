# Markdown格式与LaTeX代码对应关系表

## 📋 格式映射总览

本文档列出MD源文件中所有格式规范，以及每个格式在LaTeX模板中的对应代码。

---

## 1. 标题格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **一级标题** | `# 标题` | `\section{}` | `\section{引言}` | `gb8567-template-noto.tex:18-23` | 黑体18pt，段前12pt，段后6pt |
| **二级标题** | `## 标题` | `\subsection{}` | `\subsection{目的}` | `gb8567-template-noto.tex:26-31` | 黑体16pt，段前6pt，段后3pt |
| **三级标题** | `### 标题` | `\subsubsection{}` | `\subsubsection{术语和定义}` | `gb8567-template-noto.tex:34-39` | 黑体14pt，段前3pt，段后3pt |
| **四级标题** | `#### 标题` | `\paragraph{}` | `\paragraph{详细说明}` | `gb8567-template-noto.tex:42-47` | 黑体12pt，段前3pt，段后0pt |

**LaTeX模板代码：**
```latex
% 一级标题：黑体18pt，段前12pt，段后6pt
\titleformat{\section}
  {\fontsize{18pt}{18pt}\bfseries\CJKfamily{zhhei}}
  {}
  {0em}
  {}
\titlespacing{\section}{0pt}{12pt}{6pt}

% 二级标题：黑体16pt，段前6pt，段后3pt
\titleformat{\subsection}
  {\fontsize{16pt}{16pt}\bfseries\CJKfamily{zhhei}}
  {}
  {0em}
  {}
\titlespacing{\subsection}{0pt}{6pt}{3pt}

% 三级标题：黑体14pt，段前3pt，段后3pt
\titleformat{\subsubsection}
  {\fontsize{14pt}{14pt}\bfseries\CJKfamily{zhhei}}
  {}
  {0em}
  {}
\titlespacing{\subsubsection}{0pt}{3pt}{3pt}

% 四级标题：黑体12pt，段前3pt，段后0pt
\titleformat{\paragraph}
  {\fontsize{12pt}{12pt}\bfseries\CJKfamily{zhhei}}
  {}
  {0em}
  {}
\titlespacing{\paragraph}{0pt}{3pt}{0pt}
```

---

## 2. 文本格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **加粗** | `**文本**` | `\textbf{}` | `\textbf{重要}` | 模板全局 | 黑体，加粗 |
| **斜体** | `*文本*` | `\textit{}` | `\textit{强调}` | 模板全局 | 斜体 |
| **行内代码** | `` `代码` `` | `\texttt{}` | `\texttt{command}` | 模板全局 | 等宽字体，Courier New |
| **普通文本** | `文本` | 直接文本 | `本文档旨在...` | `gb8567-template-noto.tex:50-53` | 宋体12pt，1.5倍行距 |

**LaTeX模板代码：**
```latex
% 段落格式：1.5倍行距，首行缩进2字符
\onehalfspacing  % 1.5倍行距
\setlength{\parindent}{2em}  % 首行缩进2字符
\setlength{\parskip}{6pt}    % 段后间距6pt
```

---

## 3. 列表格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **无序列表** | `- 项目1`<br>`- 项目2` | `\begin{itemize}`<br>`\item` | `\begin{itemize}`<br>`\item 项目1`<br>`\item 项目2`<br>`\end{itemize}` | Pandoc自动转换 | 悬挂缩进2字符 |
| **有序列表** | `1. 项目1`<br>`2. 项目2` | `\begin{enumerate}`<br>`\item` | `\begin{enumerate}`<br>`\item 项目1`<br>`\item 项目2`<br>`\end{enumerate}` | Pandoc自动转换 | 阿拉伯数字编号 |
| **嵌套列表** | `- 项目1`<br>`  - 子项1` | `\begin{itemize}`<br>`\item`<br>`  \begin{itemize}` | 嵌套itemize环境 | Pandoc自动转换 | 多级缩进 |

**注意：** 列表格式由Pandoc自动转换，模板中不需要特殊设置。

---

## 4. 表格格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **简单表格** | `\| 列1 \| 列2 \|`<br>`\|-----`<br>`\| 值1 \| 值2 \|` | `\begin{longtable}`<br>`\hline`<br>`\end{longtable}` | `\begin{longtable}{\|p{3cm}\|p{4cm}\|}`<br>`\toprule`<br>`列1 & 列2 \\`<br>`\midrule`<br>`值1 & 值2 \\`<br>`\bottomrule`<br>`\end{longtable}` | `gb8567-template-noto.tex:84-103` | 边框、表头背景、字体 |

**LaTeX模板代码：**
```latex
% 表格格式设置
\usepackage{longtable}  % 长表格支持
\usepackage{booktabs}  % 表格线条
\usepackage{array}     % 数组支持
\usepackage{colortbl}  % 表格背景色支持
\usepackage{xcolor}    % 颜色支持

% 表格格式设置
\definecolor{tableheaderbg}{RGB}{240,240,240}  % 表头背景色RGB(240,240,240)
\renewcommand{\arraystretch}{1.2}              % 表格行高
\setlength{\arrayrulewidth}{0.5pt}            % 表格内边框宽度

% 表格字体设置（表格文字：宋体，五号10.5pt）
\newcolumntype{C}[1]{>{\centering\arraybackslash\fontsize{10.5pt}{12.6pt}\selectfont}p{#1}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash\fontsize{10.5pt}{12.6pt}\selectfont}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash\fontsize{10.5pt}{12.6pt}\selectfont}p{#1}}
```

**表格格式要求：**
- 表格宽度：占页面宽度的90%-100%
- 表格边框：外边框1.5pt粗线，内边框0.5pt细线
- 表头背景：RGB(240,240,240)浅灰色
- 表头字体：黑体，五号（10.5pt），加粗
- 表格内容：宋体，五号（10.5pt）

---

## 5. 代码块格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **代码块** | ` ```python`<br>`代码`<br>` ``` ` | `\begin{lstlisting}` | `\begin{lstlisting}[language=Python]`<br>`代码`<br>`\end{lstlisting}` | `gb8567-template-noto.tex:56-77` | 等宽字体，边框，背景色 |

**LaTeX模板代码：**
```latex
% 代码块格式设置
\usepackage{listings}  % 代码块支持

\lstset{
    basicstyle=\ttfamily\fontsize{10.5pt}{12.6pt}\selectfont,  % 代码字体：Courier New，五号（10.5pt）
    breaklines=true,              % 自动换行
    breakatwhitespace=true,      % 在空格处换行
    frame=single,                % 边框
    framesep=3pt,                % 边框间距
    framerule=0.5pt,             % 边框宽度
    rulecolor=\color{black},    % 边框颜色
    backgroundcolor=\color{gray!5},  % 背景色（浅灰色）
    showstringspaces=false,      % 不显示字符串中的空格
    showspaces=false,            % 不显示空格
    showtabs=false,              % 不显示制表符
    tabsize=4,                   % 制表符大小
    captionpos=b,                % 标题位置（底部）
    numbers=left,                % 行号位置
    numberstyle=\tiny\color{gray},  % 行号样式
    stepnumber=1,                % 行号步长
    numbersep=5pt                % 行号与代码间距
}

% 代码块标题格式
\renewcommand{\lstlistingname}{代码}
```

**代码块格式要求：**
- 字体：Courier New或Consolas（等宽字体）
- 字号：五号（10.5pt）
- 背景色：浅灰色（RGB(245,245,245)）
- 边框：1pt细线，颜色RGB(200,200,200)
- 内边距：上下0.3cm，左右0.5cm
- 行距：单倍行距

---

## 6. 水平线格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **水平线** | `---` | `\hrule` 或 `\hline` | `\hrule height 0.5pt` | Pandoc自动转换 | 分隔线 |

**注意：** 水平线由Pandoc自动转换，模板中不需要特殊设置。

---

## 7. 链接格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **超链接** | `[文本](URL)` | `\href{URL}{文本}` | `\href{https://example.com}{链接}` | `gb8567-template-noto.tex:138` | 可点击链接 |
| **引用链接** | `[文本][ref]` | `\href{URL}{文本}` | Pandoc自动转换 | `gb8567-template-noto.tex:138` | 引用式链接 |

**LaTeX模板代码：**
```latex
\usepackage{hyperref}  % 超链接支持
```

---

## 8. 图片格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **图片** | `![alt](path)` | `\includegraphics{}` | `\begin{figure}`<br>`\includegraphics{path}`<br>`\caption{标题}`<br>`\end{figure}` | Pandoc自动转换 | 图表编号：图X-Y |

**LaTeX模板代码：**
```latex
% 图表编号格式：图1-1、表2-3
\usepackage{caption}  % 图表标题格式
\captionsetup{
    labelsep=space,           % 标签和标题之间用空格分隔
    font=small,               % 字体大小
    format=hang,              % 标题格式
    justification=centering,   % 居中
    singlelinecheck=false     % 允许多行标题
}

\renewcommand{\figurename}{图}
\renewcommand{\thefigure}{\arabic{section}-\arabic{figure}}
\captionsetup[figure]{font={bf,small},labelfont=bf}
```

---

## 9. 数学公式格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **行内公式** | `$公式$` | `$公式$` | `$E = mc^2$` | 模板全局 | 行内公式 |
| **块级公式** | `$$公式$$` | `\[公式\]` 或 `\begin{equation}` | `\[E = mc^2\]`<br>`\begin{equation}`<br>`E = mc^2`<br>`\end{equation}` | `gb8567-template-noto.tex:141-142` | 公式编号：(1-1) |

**LaTeX模板代码：**
```latex
% 公式编号格式：(1-1)、(2-3)
\numberwithin{equation}{section}  % 公式按章节编号
\renewcommand{\theequation}{\arabic{section}-\arabic{equation}}
```

---

## 10. 引用格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **引用块** | `> 引用文本` | `\begin{quote}` | `\begin{quote}`<br>`引用文本`<br>`\end{quote}` | Pandoc自动转换 | 引用段落 |

**注意：** 引用格式由Pandoc自动转换，模板中不需要特殊设置。

---

## 11. YAML元数据

| MD格式 | MD示例 | LaTeX处理 | 模板位置 | 说明 |
|--------|--------|-----------|---------|------|
| **YAML元数据** | `---`<br>`title: "文档计划"`<br>`---` | 模板变量 `$body$` | `gb8567-template-noto.tex:146` | Pandoc提取元数据，替换模板变量 |

**LaTeX模板代码：**
```latex
\begin{document}
$body$  % Pandoc会将MD内容替换到这里
\end{document}
```

---

## 12. 页面设置

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **页面规格** | YAML中：`geometry: margin=2.5cm` | `\usepackage[geometry]{geometry}` | `\usepackage[top=2.5cm, bottom=2.5cm, left=2cm, right=2cm]{geometry}` | `gb8567-template-noto.tex:13` | A4纸张，页边距2.5cm |
| **页眉页脚** | YAML中：`header-includes:` | `\usepackage{fancyhdr}` | `\fancyhead[L]{文档名称}`<br>`\fancyfoot[C]{第\thepage\ 页}` | `gb8567-template-noto.tex:106-115` | 页眉：文档名称、版本号<br>页脚：编制单位、页码、日期 |

**LaTeX模板代码：**
```latex
% 页面设置（A4，2.5cm边距）
\usepackage[top=2.5cm, bottom=2.5cm, left=2cm, right=2cm]{geometry}

% 页眉页脚
\usepackage{fancyhdr}
\setlength{\headheight}{14pt}  % 修复页眉高度警告
\pagestyle{fancy}
\fancyhead[L]{\small\bfseries 文档名称}
\fancyhead[R]{\small\bfseries 版本号：v1.0}
\fancyfoot[L]{\small 编制单位}
\fancyfoot[C]{\small 第\thepage\ 页 共\pageref{LastPage}\ 页}
\fancyfoot[R]{\small \today}
\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\footrulewidth}{0pt}
```

---

## 13. 字体设置

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **中文正文** | YAML中：`mainfont: "SimSun"` | `\setCJKmainfont{}` | `\setCJKmainfont{Noto Serif CJK SC}` | `gb8567-template-noto.tex:5` | 宋体（正文） |
| **中文标题** | YAML中：`sansfont: "SimHei"` | `\setCJKsansfont{}` | `\setCJKsansfont{Noto Sans CJK SC}` | `gb8567-template-noto.tex:6` | 黑体（标题） |
| **代码字体** | 代码块自动使用 | `\setCJKmonofont{}` | `\setCJKmonofont{Courier New}` | `gb8567-template-noto.tex:7` | 等宽字体（代码） |

**LaTeX模板代码：**
```latex
% 中文支持 - 使用Noto字体（适用于Linux系统）
\usepackage{xeCJK}
\setCJKmainfont{Noto Serif CJK SC}      % 宋体（正文）- 使用Noto Serif替代
\setCJKsansfont{Noto Sans CJK SC}      % 黑体（标题）- 使用Noto Sans替代
\setCJKmonofont{Courier New}            % 等宽字体（代码）

% 定义黑体字体族
\setCJKfamilyfont{zhhei}{Noto Sans CJK SC}  % 黑体字体族定义
```

---

## 14. 图表编号

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **图表编号** | MD中不需要手动编号 | `\caption{}` | `\caption{图1-1 系统架构}` | `gb8567-template-noto.tex:128-131` | 自动编号：图X-Y、表X-Y |

**LaTeX模板代码：**
```latex
% 图表编号格式：图1-1、表2-3
\renewcommand{\figurename}{图}
\renewcommand{\tablename}{表}
\renewcommand{\thefigure}{\arabic{section}-\arabic{figure}}
\renewcommand{\thetable}{\arabic{section}-\arabic{table}}

% 表格标题字体：黑体，五号（10.5pt），加粗
\captionsetup[table]{font={bf,small},labelfont=bf}
\captionsetup[figure]{font={bf,small},labelfont=bf}
```

---

## 15. 目录格式

| MD格式 | MD示例 | LaTeX代码 | LaTeX示例 | 模板位置 | 说明 |
|--------|--------|-----------|-----------|---------|------|
| **目录** | YAML中：`toc: true` | `\tableofcontents` | `\tableofcontents` | Pandoc自动生成 | 自动生成目录 |

**注意：** 目录由Pandoc自动生成，模板中不需要特殊设置。

---

## 📊 格式映射总结

### 完全映射的格式（✅）
- ✅ 标题格式（#、##、###、####）
- ✅ 文本格式（加粗、斜体、行内代码）
- ✅ 列表格式（无序、有序、嵌套）
- ✅ 表格格式（简单表格、复杂表格）
- ✅ 代码块格式（代码块、行内代码）
- ✅ 链接格式（超链接、引用链接）
- ✅ 图片格式（图片、图表编号）
- ✅ 数学公式格式（行内、块级）
- ✅ 页面设置（页边距、页眉页脚）
- ✅ 字体设置（中文、英文、代码字体）
- ✅ 图表编号（图X-Y、表X-Y）
- ✅ 目录格式（自动生成）

### 需要注意的格式（⚠️）
- ⚠️ **表格列宽**：MD中不指定列宽，Pandoc自动计算，可能生成复杂的`\real{}`命令
- ⚠️ **表格边框**：MD中不指定边框，Pandoc可能生成无边框表格
- ⚠️ **列表格式**：MD中的文本列表（如"文本： - 项目1 - 项目2"）可能不被识别为列表

### 转换问题（❌）
- ❌ **表格列宽计算**：Pandoc生成的`\real{}`命令在LaTeX中不存在
- ❌ **表格边框定义**：Pandoc生成的`@{}`格式可能不正确
- ❌ **列表识别**：文本格式的列表可能不被识别

---

## 🔧 修复策略

### 当前问题分析

1. **表格列宽问题**：
   - MD格式：`| 列1 | 列2 |`
   - Pandoc转换：`\begin{longtable}[]{@{...\real{0.2941}...}}`
   - LaTeX要求：`\begin{longtable}{|p{3cm}|p{4cm}|}`
   - **修复方案**：在转换后替换`\real{}`命令为固定列宽

2. **表格边框问题**：
   - MD格式：简单表格
   - Pandoc转换：`\begin{longtable}[]{@{}}`
   - LaTeX要求：`\begin{longtable}{|p{3cm}|p{4cm}|}`
   - **修复方案**：在转换后添加边框定义

3. **列表格式问题**：
   - MD格式：`文本： - 项目1 - 项目2`
   - Pandoc转换：可能不识别为列表
   - LaTeX要求：`\begin{itemize}\item 项目1\item 项目2\end{itemize}`
   - **修复方案**：在转换后识别并修复文本列表

---

## 📝 总结

### 理解要点

1. **MD是内容标记语言**：MD只标记内容结构，不控制格式
2. **LaTeX是格式控制语言**：LaTeX通过代码精确控制格式
3. **Pandoc是转换工具**：Pandoc将MD转换为LaTeX，但可能生成不兼容的代码
4. **模板是格式定义**：LaTeX模板定义了所有格式要求
5. **后处理是必要的**：需要在转换后修复Pandoc生成的问题代码

### 下一步工作

1. ✅ 建立完整的格式映射表（本文档）
2. ⏳ 优化转换脚本，自动修复问题
3. ⏳ 完善LaTeX模板，确保所有格式正确
4. ⏳ 建立格式验证机制

---

**文档版本**：v1.0  
**创建日期**：2025-11-05  
**作者**：Auto AI Assistant

