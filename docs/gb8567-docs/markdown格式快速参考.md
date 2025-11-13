# Markdown格式能力与转换方案 - 快速参考

## ⚠️ 关键问题解答

### Q1: Markdown能否直接设置字号、行距等格式？

**答案：不能直接设置，但可以通过YAML元数据实现**

**Markdown的限制**：
- ❌ Markdown是**纯文本标记语言**，不包含格式信息
- ❌ Markdown文件本身**无法存储**字体、字号、行距等格式属性
- ✅ Markdown只关注**内容和结构**（标题、段落、列表等）

**解决方案**：
- ✅ 在Markdown文件头部添加**YAML元数据**定义格式参数
- ✅ 使用**转换工具**（pandoc、Mark Text等）在转换时应用格式
- ✅ 使用**CSS样式文件**或**模板文件**控制格式

### Q2: Markdown转PDF时格式能否保留？

**答案：可以保留，但需要提前配置**

**转换能力**：

| 格式要求 | Markdown支持 | 转换后支持 | 实现方式 |
|---------|------------|-----------|---------|
| 章节结构 | ✅ 完全支持 | ✅ 完全保留 | Markdown语法 |
| 字体字号 | ❌ 不支持 | ✅ 可通过配置实现 | YAML元数据 + pandoc |
| 行距段距 | ❌ 不支持 | ✅ 可通过配置实现 | YAML元数据 + pandoc |
| 页眉页脚 | ❌ 不支持 | ✅ 可通过配置实现 | pandoc模板/LaTeX |
| 页码格式 | ❌ 不支持 | ✅ 可通过配置实现 | pandoc模板/LaTeX |
| 表格格式 | ⚠️ 基础支持 | ✅ 可通过配置实现 | CSS样式/模板 |

**结论**：格式**可以保留**，但需要：
1. ✅ 在Markdown文件中使用YAML元数据定义格式参数
2. ✅ 准备转换工具的配置文件（CSS、模板文件等）
3. ✅ 使用正确的转换工具和配置

### Q3: 如果格式不能保留，会影响后期使用吗？

**答案：会！所以必须提前建立转换机制**

**影响**：
- ❌ 打印出来的文档不符合GB/T 8567-2006标准要求
- ❌ 不同文档格式不统一，影响专业性
- ❌ 需要重新手动调整，工作量巨大

**解决方案**：**提前建立转换机制和模板**

## 💡 推荐方案：Markdown + YAML元数据 + Pandoc

### 工作流程

```
1. 编写阶段：Markdown + YAML元数据
   ↓
2. 转换阶段：pandoc转换为PDF
   ↓
3. 验证阶段：检查PDF格式是否符合要求
```

### Markdown文件格式

在Markdown文件开头添加YAML元数据：

```markdown
---
title: "可行性研究报告"
document-number: "FSR"
version: "v1.0"
date: "2025-11-05"

# PDF格式设置
pdf-engine: xelatex
mainfont: "SimSun"          # 宋体（中文正文）
sansfont: "SimHei"          # 黑体（中文标题）
fontsize: 12pt              # 正文字号：小四号（12pt）
linestretch: 1.5            # 行距：1.5倍
geometry: margin=2.5cm       # 页边距：2.5cm
---

# 可行性研究报告

正文内容...
```

### 转换命令

```bash
# 转换为PDF
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V mainfont="SimSun" \
  -V fontsize=12pt \
  -V linestretch=1.5 \
  -V geometry:margin=2.5cm
```

### 转换脚本

已创建转换脚本：
- `tools/convert_md_to_pdf.sh`（Linux/macOS）
- `tools/convert_md_to_pdf.bat`（Windows）

## 📋 格式规范适用范围

### 格式规范的两种理解

**理解1：Markdown源文件格式规范**
- ✅ 章节编号：1、1.1、1.1.1
- ✅ 文档结构：封面、目录、正文、附录
- ✅ 图表编号：图1-1、表2-3
- ❌ 字体字号：Markdown不支持
- ❌ 行距段距：Markdown不支持
- ❌ 页眉页脚：Markdown不支持

**理解2：PDF/DOCX文档格式规范**
- ✅ 字体字号：宋体12pt、黑体18pt等
- ✅ 行距段距：1.5倍行距、6pt段距
- ✅ 页眉页脚：文档名称、版本号、页码
- ✅ 页面设置：A4纸张、2.5cm页边距

### 格式规范的表述调整

**原表述**（可能引起误解）：
> "正文：宋体，小四号（12pt）"

**调整后表述**：
> "**编写阶段**：使用Markdown标准语法编写正文  
> **转换后格式**：正文应为宋体，小四号（12pt）  
> **实现方式**：通过YAML元数据或CSS样式文件设置"

## ✅ 实践建议

### 立即行动

1. **使用带YAML元数据的Markdown模板**
   - 模板位置：`docs/templates/MARKDOWN_TEMPLATE_WITH_YAML.md`
   - 所有文档都使用这个模板

2. **建立转换机制**
   - 使用转换脚本：`tools/convert_md_to_pdf.sh`或`.bat`
   - 或使用Mark Text/Typora的导出功能

3. **验证转换效果**
   - 转换示例文档
   - 检查PDF格式是否符合要求
   - 调整配置直到满意

### 格式规范的使用

1. **编写阶段**：
   - 关注内容结构（章节编号、文档结构等）
   - 在YAML元数据中定义格式参数
   - 不强制格式细节（这些在转换时控制）

2. **转换阶段**：
   - 使用转换工具（pandoc、Mark Text等）
   - 应用格式配置（YAML元数据、CSS样式、模板文件）
   - 生成PDF/DOCX文档

3. **验证阶段**：
   - 检查PDF/DOCX格式是否符合GB/T 8567-2006标准
   - 使用格式检查清单验证
   - 必要时调整转换配置

## 📚 参考文档

- `docs/gb8567-docs/MARKDOWN_FORMAT_SOLUTION.md` - 格式解决方案详细说明
- `docs/templates/MARKDOWN_TEMPLATE_WITH_YAML.md` - 带YAML元数据的Markdown模板
- `tools/convert_md_to_pdf.sh` / `tools/convert_md_to_pdf.bat` - 转换脚本
- `docs/templates/DP_文档计划模板.md`（第5章） - 详细格式规范

---

**创建日期**: 2025-11-05  
**版本**: v1.0  
**重要性**: ⚠️ **关键问题，必须理解**

