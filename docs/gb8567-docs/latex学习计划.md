# LaTeX 学习计划（实践版）

## 目标
掌握LaTeX基础使用，能够使用项目模板将Markdown转换为符合GB/T 8567-2006标准的PDF文档。

---

## 阶段1：环境安装与验证

### 任务1.1：检查LaTeX是否已安装
- [x] 检查 `xelatex` 命令 ✅ 已安装：XeTeX 3.141592653-2.6-0.999995
- [x] 检查 `pandoc` 命令 ✅ 已安装：pandoc 3.1.3
- [x] 检查系统字体（SimSun、SimHei） ⚠️ 未找到SimSun/SimHei，但有Noto Serif CJK和Noto Sans CJK可用

### 任务1.2：安装缺失组件
- [ ] 安装中文语言包 ⚠️ **需要手动安装**：`sudo apt-get install texlive-lang-chinese texlive-xetex`
- [ ] 验证安装成功

**当前状态**：
- ✅ XeLaTeX已安装
- ✅ Pandoc已安装  
- ⚠️ 中文支持包未安装（需要xeCJK或ctex包）
- ⚠️ 系统中无SimSun/SimHei字体，但有Noto字体可用

**安装命令**（需要sudo权限）：
```bash
sudo apt-get update
sudo apt-get install -y texlive-lang-chinese texlive-xetex
```

---

## 阶段2：模板测试

### 任务2.1：测试项目模板
- [ ] 使用模板编译一个简单的测试文档 ⚠️ **等待中文包安装**
- [ ] 验证中文字体显示正常
- [ ] 验证标题格式正确
- [ ] 验证段落格式正确

### 任务2.2：测试Markdown转PDF流程
- [ ] 选择一个简单的Markdown文件
- [ ] 使用pandoc转换为PDF
- [ ] 检查输出格式是否符合要求

**当前问题**：
- 模板需要使用xeCJK包，但该包未安装
- 需要先完成阶段1.2的安装任务

---

## 阶段3：基本语法学习

### 任务3.1：文档结构
- [ ] 理解 `\documentclass`
- [ ] 理解 `\begin{document}` 和 `\end{document}`
- [ ] 理解包引入 `\usepackage`

### 任务3.2：章节和标题
- [ ] 掌握 `\section`, `\subsection`, `\subsubsection`
- [ ] 理解标题编号
- [ ] 理解标题格式设置

### 任务3.3：文本格式
- [ ] 段落和换行
- [ ] 粗体 `\textbf{}`
- [ ] 斜体 `\textit{}`
- [ ] 首行缩进和行距

### 任务3.4：表格
- [ ] 基本表格语法
- [ ] 表格边框设置
- [ ] 表格对齐

### 任务3.5：图片和代码
- [ ] 插入图片 `\includegraphics`
- [ ] 代码块格式
- [ ] 代码字体设置

---

## 阶段4：项目模板深入理解

### 任务4.1：分析模板结构
- [ ] 理解模板中的字体设置
- [ ] 理解标题格式设置
- [ ] 理解段落格式设置
- [ ] 理解页眉页脚设置

### 任务4.2：模板定制
- [ ] 修改页眉页脚内容
- [ ] 调整段落间距
- [ ] 调整标题格式（如需要）

---

## 阶段5：实战应用

### 任务5.1：转换现有文档
- [ ] 选择一个现有的Markdown文档
- [ ] 转换为PDF
- [ ] 检查格式问题
- [ ] 修复格式问题

### 任务5.2：优化转换流程
- [ ] 创建转换脚本（如需要）
- [ ] 自动化转换过程
- [ ] 验证转换结果一致性

---

## 快速参考

### 常用命令
```bash
# 编译LaTeX文档
xelatex document.tex

# Markdown转PDF
pandoc input.md -o output.pdf \
  --template=templates/gb8567-template.tex \
  --pdf-engine=xelatex
```

### 模板位置
- LaTeX模板：`templates/gb8567-template.tex`
- 参考文档：`docs/gb8567-docs/reference/`

### 学习资源
- LaTeX官方文档：https://www.latex-project.org/
- 中文LaTeX教程：https://www.latexstudio.net/
- Overleaf在线编辑器：https://www.overleaf.com/

---

## 执行进度

**当前执行阶段**：阶段1 - 环境安装与验证

**已完成**：
- ✅ 检查xelatex和pandoc命令
- ✅ 确认系统字体情况

**待完成**：
- ⚠️ 需要手动安装中文语言包（需要sudo权限）
- ⚠️ 安装后测试模板编译

---

## 检查清单

完成每个阶段后，请确认：
- [ ] 阶段1：环境安装完成，所有命令可用 ⚠️ **进行中**（需要安装中文包）
- [ ] 阶段2：模板测试通过，输出格式正确
- [ ] 阶段3：基本语法理解，能够编写简单文档
- [ ] 阶段4：模板完全理解，能够修改定制
- [ ] 阶段5：能够独立完成Markdown到PDF的转换

---

## 下一步操作

1. **安装中文语言包**（需要sudo权限）：
   ```bash
   sudo apt-get update
   sudo apt-get install -y texlive-lang-chinese texlive-xetex
   ```

2. **安装完成后，测试模板编译**：
   ```bash
   cd /media/test/新加卷/data/work/jiekou-20251103
   xelatex -interaction=nonstopmode temp/latex_test_ctex.tex
   ```

3. **如果字体问题，修改模板使用Noto字体**：
   - 将`SimSun`改为`Noto Serif CJK SC`
   - 将`SimHei`改为`Noto Sans CJK SC`

