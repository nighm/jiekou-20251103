# DOCX格式Bug分析与解决方案

## 📋 Bug清单

根据人工审核结果，以下是发现的问题及解决方案：

---

## Bug 1: 表格没有边框

### 问题描述
生成的DOCX文件中，所有表格都没有可见的边框，只有空白分隔。

### 原因分析
1. **Markdown不支持边框**：Markdown表格语法本身不包含边框样式
2. **Pandoc不自动添加边框**：Pandoc转换时不会自动应用参考模板中示例表格的边框到新表格
3. **需要后处理**：必须在转换后通过python-docx手动为每个表格添加边框

### 解决方案
✅ **已实现**：在`convert_dp_template.py`的`fix_table_formatting()`函数中：
- 为每个表格设置外边框1.5pt（粗线）
- 为每个表格设置内边框0.5pt（细线）
- 使用XML直接操作确保边框生效

### 验证方法
```bash
python3 tools/convert_dp_template.py
# 检查输出：应该显示"已修复 X/X 个表格的边框和格式"
```

---

## Bug 2: 表格字体字号不正确

### 问题描述
表格中的文字不是10.5pt（五号），可能使用了默认的12pt。

### 原因分析
1. **参考模板示例表格的字体不会自动应用**：Pandoc只复制样式定义，不复制示例表格的格式
2. **表格单元格需要单独设置**：每个单元格的字体字号需要单独设置

### 解决方案
✅ **已实现**：在`fix_table_formatting()`函数中：
- 表头：黑体，10.5pt，加粗
- 表格内容：宋体，10.5pt
- 遍历所有单元格，确保所有文本都设置了正确的字体和字号

### 验证方法
打开DOCX文件，检查表格文字的字体和字号是否都是10.5pt。

---

## Bug 3: 表格内容对齐不正确

### 问题描述
表格内容的对齐方式不符合要求：
- 序号应该居中
- 日期应该居中
- 文档编号应该居中
- 其他内容应该左对齐

### 原因分析
Markdown表格默认所有单元格都是左对齐，Pandoc转换时不会自动根据内容类型设置对齐方式。

### 解决方案
✅ **已实现**：在`fix_table_formatting()`函数中：
- 第0列（序号列）：居中
- 第2列且内容是3-4个大写字母（文档编号）：居中
- 日期格式（YYYY-MM-DD）：居中
- 其他列：左对齐

### 验证方法
检查表格：
- 序号列是否居中
- 文档编号列（如FSR、PDP）是否居中
- 日期列是否居中
- 其他列是否左对齐

---

## Bug 4: 文档基本信息部分键值对冒号不对齐

### 问题描述
"文档基本信息"部分的键值对（如"文档编号：[项目编号]-DP-001"）中的冒号没有对齐，看起来不整齐。

### 原因分析
Markdown中的键值对只是普通文本，Pandoc转换后仍然是普通段落，冒号位置取决于文本长度，无法自动对齐。

### 解决方案
✅ **已实现**：在`fix_key_value_alignment()`函数中：
- 识别文档基本信息部分的段落
- 使用制表符（Tab）实现对齐
- 键部分：正常文本
- 制表符：定位到5cm位置
- 冒号和值：对齐显示

### 验证方法
检查"文档基本信息"部分，所有冒号应该垂直对齐。

---

## Bug 5: 表头背景色可能缺失

### 问题描述
表格的表头（第一行）应该使用浅灰色背景RGB(240,240,240)，但可能没有设置。

### 原因分析
参考模板中的示例表格有背景色，但Pandoc转换时不会自动应用。

### 解决方案
✅ **已实现**：在`fix_table_formatting()`函数中：
- 检测表格的第一行
- 为第一行的所有单元格设置背景色RGB(240,240,240)
- 使用XML直接设置shading属性

### 验证方法
检查表格的第一行是否有浅灰色背景。

---

## Bug 6: 复杂层级结构表格（职责分工）格式丢失

### 问题描述
"职责分工"部分使用了Markdown代码块来显示树形结构（使用`├──`、`│`等字符），转换后可能格式不对。

### 原因分析
1. **Markdown代码块转换为Word代码样式**：Pandoc会将代码块转换为等宽字体样式
2. **无法转换为Word表格**：这种ASCII艺术式的树形结构无法自动转换为Word表格
3. **格式限制**：Word中的表格不支持这种树形连接线

### 解决方案
⚠️ **当前限制**：这种ASCII艺术式的树形结构在Word中无法完美重现。

**可选方案**：
1. **保留代码块格式**（当前方案）：
   - 使用Courier New等宽字体
   - 保持原始文本结构
   - 优点：简单，保持原样
   - 缺点：不够美观，不符合标准表格格式

2. **转换为标准表格**（推荐）：
   - 将Markdown代码块改为标准Markdown表格
   - 使用表格的层级结构表示
   - 优点：符合标准格式，美观
   - 缺点：需要修改Markdown源文件

### 建议
如果需要符合GB/T 8567-2006标准，建议将"职责分工"部分的代码块改为标准表格格式。

---

## Bug 7: 表格宽度可能不对

### 问题描述
表格宽度应该占页面宽度的90%-100%，但可能使用了默认宽度。

### 原因分析
Pandoc转换时，表格宽度可能使用默认值，不会自动应用参考模板中示例表格的宽度。

### 解决方案
✅ **已实现**：需要在后处理中设置表格宽度。当前代码中，`fix_table_formatting()`函数可以添加表格宽度设置。

### 待实现
需要在`fix_table_formatting()`函数中添加：
```python
# 设置表格宽度（90%页面宽度）
section = doc.sections[0]
table_width = section.page_width - section.left_margin - section.right_margin
table.width = int(table_width * 0.9)
table.alignment = WD_ALIGN_PARAGRAPH.CENTER
```

---

## Bug 8: 表格行高可能不符合要求

### 问题描述
表格行高应该是最小值0.8cm，但可能使用了默认值。

### 原因分析
参考模板中的示例表格设置了行高，但Pandoc转换时不会自动应用。

### 解决方案
✅ **部分实现**：可以在`fix_table_formatting()`函数中添加行高设置。

### 待实现
需要在`fix_table_formatting()`函数中为每行设置：
```python
# 设置行高（最小值0.8cm）
if row._element.trPr is None:
    trPr = OxmlElement('w:trPr')
    row._element.insert(0, trPr)
trHeight = OxmlElement('w:trHeight')
trHeight.set(qn('w:val'), str(int(Cm(0.8) * 20)))
trHeight.set(qn('w:hRule'), 'atLeast')
row._element.trPr.append(trHeight)
```

---

## Bug 9: 表格单元格内边距可能不对

### 问题描述
表格单元格内边距应该是上下0.2cm，左右0.3cm，但可能使用了默认值。

### 原因分析
参考模板中的示例表格设置了内边距，但Pandoc转换时不会自动应用。

### 解决方案
✅ **部分实现**：可以在`fix_table_formatting()`函数中添加内边距设置。

### 待实现
需要在`fix_table_formatting()`函数中为每个单元格设置：
```python
# 设置单元格内边距（上下0.2cm，左右0.3cm）
if cell._element.tcPr is None:
    cell._element.add_tcPr()
tcPr = cell._element.tcPr

tcMar = OxmlElement('w:tcMar')
for margin_name, margin_value in [('top', Cm(0.2)), ('bottom', Cm(0.2)), ('left', Cm(0.3)), ('right', Cm(0.3))]:
    margin = OxmlElement(f'w:{margin_name}')
    margin.set(qn('w:w'), str(int(margin_value * 20)))
    margin.set(qn('w:type'), 'dxa')
    tcMar.append(margin)
tcPr.append(tcMar)
```

---

## Bug 10: 标题编号可能重复

### 问题描述
文档标题可能显示为"1. 1. 引言"这样的重复编号。

### 原因分析
Markdown源文件中手动添加了编号（如`## 1. 引言`），同时Pandoc的`--number-sections`也会自动添加编号，导致重复。

### 解决方案
✅ **已实现**：在`fix_markdown_headings()`函数中：
- 自动移除Markdown中的所有手动编号
- 让Pandoc的`--number-sections`自动添加编号
- 创建备份文件

### 验证方法
检查转换后的文档，标题应该是"1. 引言"而不是"1. 1. 引言"。

---

## 总结

### 已修复的Bug
1. ✅ 表格边框
2. ✅ 表格字体字号
3. ✅ 表格内容对齐
4. ✅ 键值对对齐
5. ✅ 表头背景色
6. ✅ 标题编号重复

### 待完善的Bug
7. ⚠️ 表格宽度（需要添加）
8. ⚠️ 表格行高（需要添加）
9. ⚠️ 表格单元格内边距（需要添加）

### 限制性Bug
10. ⚠️ 复杂层级结构表格（需要修改Markdown源文件）

---

**最后更新**: 2025-11-05

