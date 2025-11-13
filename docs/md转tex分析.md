# MD→TeX直接转换可行性分析

## 📋 核心目标

**目标：实现MD→TeX的直接转换，绕过Pandoc**

**当前流程：**
```
MD → Pandoc → AST → LaTeX → 后处理修复
```

**目标流程：**
```
MD → Python解析器 → 直接生成LaTeX
```

---

## ✅ 可行性分析

### 方案：完全可行 ✅

**为什么可行：**

1. **MD语法相对简单**
   - MD语法规则明确，易于解析
   - 不需要复杂的AST构建
   - 可以直接转换为LaTeX代码

2. **已知对应关系明确**
   - 项目中已有完整的MD→LaTeX映射表
   - 每个MD语法都有对应的LaTeX代码
   - 可以参考：`docs/MD_TO_LATEX_FORMAT_MAPPING.md`

3. **Python实现简单**
   - 使用正则表达式 + 字符串处理
   - 不需要复杂的解析器
   - 可以完全控制转换逻辑

---

## 📊 MD语法元素清单

### 需要实现的核心MD语法（约20-25个）

#### 1. 标题（4个级别）
- `# 标题` → `\section{标题}`
- `## 标题` → `\subsection{标题}`
- `### 标题` → `\subsubsection{标题}`
- `#### 标题` → `\paragraph{标题}`

#### 2. 文本格式（3个）
- `**文本**` → `\textbf{文本}`
- `*文本*` → `\textit{文本}`
- `` `代码` `` → `\texttt{代码}`

#### 3. 列表（2个类型）
- 无序列表：`- 项目` → `\begin{itemize}\item 项目\end{itemize}`
- 有序列表：`1. 项目` → `\begin{enumerate}\item 项目\end{enumerate}`

#### 4. 表格（1个）
- 管道表格：`| 列1 | 列2 |` → `\begin{longtable}...`

#### 5. 代码块（1个）
- 围栏代码块：`` ```language 代码 ``` `` → `\begin{lstlisting}...`

#### 6. 链接和图片（2个）
- 链接：`[文本](URL)` → `\href{URL}{文本}`
- 图片：`![alt](path)` → `\includegraphics{path}`

#### 7. 数学公式（2个）
- 行内公式：`$公式$` → `$公式$`
- 块级公式：`$$公式$$` → `\[公式\]` 或 `\begin{equation}...`

#### 8. 其他（3个）
- 水平线：`---` → `\hrule` 或 `\hline`
- 引用块：`> 文本` → `\begin{quote}文本\end{quote}`
- 段落：普通文本 → 直接段落

**总计：约18-20个核心语法元素**

---

## 🎯 实现方案

### 架构设计

```
MD文件
  ↓
Python解析器
  ├─ YAML元数据解析
  ├─ 标题解析
  ├─ 文本格式解析
  ├─ 列表解析
  ├─ 表格解析
  ├─ 代码块解析
  ├─ 链接/图片解析
  ├─ 数学公式解析
  └─ 其他元素解析
  ↓
LaTeX代码生成
  ├─ 模板头部（文档类、包等）
  ├─ 主体内容
  └─ 模板尾部（\end{document}）
  ↓
完整的.tex文件
```

### 实现步骤

#### 阶段1：基础转换（核心语法）

**优先级1：必须实现**
1. ✅ 标题（4个级别）
2. ✅ 段落（普通文本）
3. ✅ 文本格式（加粗、斜体、行内代码）
4. ✅ 列表（有序、无序）

**优先级2：重要功能**
5. ✅ 表格（管道表格）
6. ✅ 代码块（围栏代码块）
7. ✅ 链接和图片

**优先级3：增强功能**
8. ✅ 数学公式
9. ✅ 水平线
10. ✅ 引用块

#### 阶段2：高级功能

11. ✅ YAML元数据处理
12. ✅ 嵌套列表
13. ✅ 复杂表格（合并单元格等）
14. ✅ 目录生成

---

## 💻 技术实现

### 核心代码结构

```python
class MDToTeXConverter:
    """MD到TeX直接转换器"""
    
    def __init__(self, template_file):
        """初始化转换器"""
        self.template_file = template_file
        self.template = self.load_template()
    
    def load_template(self):
        """加载LaTeX模板"""
        # 读取模板文件，提取$body$部分
        pass
    
    def parse_yaml(self, content):
        """解析YAML元数据"""
        # 提取YAML front matter
        pass
    
    def parse_headings(self, content):
        """解析标题"""
        # # 标题 → \section{标题}
        pass
    
    def parse_text_format(self, content):
        """解析文本格式"""
        # **文本** → \textbf{文本}
        # *文本* → \textit{文本}
        # `代码` → \texttt{代码}
        pass
    
    def parse_lists(self, content):
        """解析列表"""
        # - 项目 → \begin{itemize}\item 项目\end{itemize}
        # 1. 项目 → \begin{enumerate}\item 项目\end{enumerate}
        pass
    
    def parse_tables(self, content):
        """解析表格"""
        # | 列1 | 列2 | → \begin{longtable}...
        pass
    
    def parse_code_blocks(self, content):
        """解析代码块"""
        # ```language 代码 ``` → \begin{lstlisting}...
        pass
    
    def parse_links_images(self, content):
        """解析链接和图片"""
        # [文本](URL) → \href{URL}{文本}
        # ![alt](path) → \includegraphics{path}
        pass
    
    def parse_math(self, content):
        """解析数学公式"""
        # $公式$ → $公式$
        # $$公式$$ → \[公式\]
        pass
    
    def convert(self, md_file):
        """主转换函数"""
        # 1. 读取MD文件
        # 2. 解析YAML元数据
        # 3. 按顺序解析各种元素
        # 4. 生成LaTeX代码
        # 5. 插入模板
        # 6. 返回完整TeX文件
        pass
```

### 转换规则示例

#### 示例1：标题转换

```python
def parse_headings(self, content):
    """解析标题"""
    # 一级标题
    content = re.sub(
        r'^# (.+)$',
        r'\\section{\1}',
        content,
        flags=re.MULTILINE
    )
    # 二级标题
    content = re.sub(
        r'^## (.+)$',
        r'\\subsection{\1}',
        content,
        flags=re.MULTILINE
    )
    # 三级标题
    content = re.sub(
        r'^### (.+)$',
        r'\\subsubsection{\1}',
        content,
        flags=re.MULTILINE
    )
    # 四级标题
    content = re.sub(
        r'^#### (.+)$',
        r'\\paragraph{\1}',
        content,
        flags=re.MULTILINE
    )
    return content
```

#### 示例2：文本格式转换

```python
def parse_text_format(self, content):
    """解析文本格式"""
    # 加粗：**文本** → \textbf{文本}
    content = re.sub(
        r'\*\*(.+?)\*\*',
        r'\\textbf{\1}',
        content
    )
    # 斜体：*文本* → \textit{文本}
    content = re.sub(
        r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)',
        r'\\textit{\1}',
        content
    )
    # 行内代码：`代码` → \texttt{代码}
    content = re.sub(
        r'`(.+?)`',
        r'\\texttt{\1}',
        content
    )
    return content
```

#### 示例3：列表转换

```python
def parse_lists(self, content):
    """解析列表"""
    lines = content.split('\n')
    result = []
    in_list = False
    list_type = None
    
    for line in lines:
        # 无序列表：- 项目
        if re.match(r'^\s*-\s+(.+)', line):
            if not in_list:
                result.append('\\begin{itemize}')
                in_list = True
                list_type = 'itemize'
            match = re.match(r'^\s*-\s+(.+)', line)
            result.append(f'\\item {match.group(1)}')
        # 有序列表：1. 项目
        elif re.match(r'^\s*\d+\.\s+(.+)', line):
            if not in_list:
                result.append('\\begin{enumerate}')
                in_list = True
                list_type = 'enumerate'
            match = re.match(r'^\s*\d+\.\s+(.+)', line)
            result.append(f'\\item {match.group(1)}')
        else:
            if in_list:
                result.append(f'\\end{{{list_type}}}')
                in_list = False
            result.append(line)
    
    if in_list:
        result.append(f'\\end{{{list_type}}}')
    
    return '\n'.join(result)
```

---

## ⚖️ 优缺点分析

### 优点 ✅

1. **完全控制**
   - 不依赖Pandoc，完全控制转换逻辑
   - 可以精确控制每个MD元素转换为LaTeX的方式

2. **无后处理问题**
   - 不需要修复Pandoc生成的错误代码
   - 直接生成正确的LaTeX代码

3. **扩展性强**
   - 容易添加新的MD语法支持
   - 容易添加自定义LaTeX功能

4. **性能更好**
   - 不需要调用外部程序（Pandoc）
   - 纯Python实现，速度更快

5. **调试简单**
   - 代码逻辑清晰，易于调试
   - 可以精确控制每个转换步骤

### 缺点 ⚠️

1. **开发工作量大**
   - 需要实现所有MD语法解析
   - 需要处理各种边界情况

2. **维护成本**
   - 需要自己维护解析器
   - 需要处理新的MD语法扩展

3. **复杂情况处理**
   - 嵌套结构（嵌套列表、嵌套引用等）
   - 边界情况（表格格式、代码块中的代码等）

4. **功能覆盖**
   - 初期可能不支持所有Pandoc扩展语法
   - 需要逐步完善

---

## 🎯 实现建议

### 推荐方案：分阶段实现

**阶段1：核心功能（约1-2周）**
- ✅ 实现基础转换器框架
- ✅ 实现标题、段落、文本格式、列表
- ✅ 测试基础功能

**阶段2：重要功能（约1-2周）**
- ✅ 实现表格、代码块
- ✅ 实现链接、图片
- ✅ 测试复杂文档

**阶段3：增强功能（约1周）**
- ✅ 实现数学公式、水平线、引用块
- ✅ 实现YAML元数据处理
- ✅ 完善边界情况处理

**阶段4：优化和扩展（持续）**
- ✅ 优化转换逻辑
- ✅ 添加高级功能
- ✅ 性能优化

### 技术选择

**推荐：纯Python实现**

- **使用正则表达式**：处理简单语法
- **使用状态机**：处理复杂语法（列表、表格等）
- **使用模板系统**：生成LaTeX代码

**不推荐：使用外部库**

- ❌ 不使用markdown库（会增加依赖）
- ❌ 不使用Pandoc（目标就是绕过它）
- ✅ 纯Python实现，无外部依赖

---

## 📝 代码示例

### 完整示例：简单的MD→TeX转换器

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MD到TeX直接转换器
绕过Pandoc，直接实现MD→TeX转换
"""

import re
from pathlib import Path


class MDToTeXConverter:
    """MD到TeX直接转换器"""
    
    def __init__(self, template_file):
        """初始化转换器"""
        self.template_file = Path(template_file)
        self.template_header = ""
        self.template_footer = ""
        self.load_template()
    
    def load_template(self):
        """加载LaTeX模板"""
        with open(self.template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分离模板头部和尾部
        parts = content.split('$body$')
        if len(parts) == 2:
            self.template_header = parts[0]
            self.template_footer = parts[1]
        else:
            # 如果没有$body$标记，使用默认模板
            self.template_header = self.get_default_template_header()
            self.template_footer = "\n\\end{document}\n"
    
    def get_default_template_header(self):
        """获取默认模板头部"""
        return """\\documentclass[12pt,a4paper]{article}
\\usepackage{xeCJK}
\\setCJKmainfont{SimSun}
\\setCJKsansfont{SimHei}
\\setCJKmonofont{Courier New}
\\begin{document}
"""
    
    def parse_headings(self, content):
        """解析标题"""
        # 一级标题
        content = re.sub(r'^# (.+)$', r'\\section{\1}', content, flags=re.MULTILINE)
        # 二级标题
        content = re.sub(r'^## (.+)$', r'\\subsection{\1}', content, flags=re.MULTILINE)
        # 三级标题
        content = re.sub(r'^### (.+)$', r'\\subsubsection{\1}', content, flags=re.MULTILINE)
        # 四级标题
        content = re.sub(r'^#### (.+)$', r'\\paragraph{\1}', content, flags=re.MULTILINE)
        return content
    
    def parse_text_format(self, content):
        """解析文本格式"""
        # 加粗：**文本** → \textbf{文本}
        content = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', content)
        # 行内代码：`代码` → \texttt{代码}
        content = re.sub(r'`(.+?)`', r'\\texttt{\1}', content)
        # 斜体：*文本* → \textit{文本}（注意：避免与粗体冲突）
        # 先处理粗体，再处理斜体
        content = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\\textit{\1}', content)
        return content
    
    def parse_lists(self, content):
        """解析列表"""
        lines = content.split('\n')
        result = []
        in_list = False
        list_type = None
        
        for line in lines:
            # 无序列表：- 项目
            if re.match(r'^\s*-\s+(.+)', line):
                if not in_list:
                    result.append('\\begin{itemize}')
                    in_list = True
                    list_type = 'itemize'
                match = re.match(r'^\s*-\s+(.+)', line)
                result.append(f'\\item {match.group(1)}')
            # 有序列表：1. 项目
            elif re.match(r'^\s*\d+\.\s+(.+)', line):
                if not in_list:
                    result.append('\\begin{enumerate}')
                    in_list = True
                    list_type = 'enumerate'
                match = re.match(r'^\s*\d+\.\s+(.+)', line)
                result.append(f'\\item {match.group(1)}')
            else:
                if in_list:
                    result.append(f'\\end{{{list_type}}}')
                    in_list = False
                result.append(line)
        
        if in_list:
            result.append(f'\\end{{{list_type}}}')
        
        return '\n'.join(result)
    
    def convert(self, md_file):
        """主转换函数"""
        # 读取MD文件
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除YAML front matter（先简单处理）
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        
        # 按顺序解析各种元素
        content = self.parse_headings(content)
        content = self.parse_text_format(content)
        content = self.parse_lists(content)
        # TODO: 添加更多解析函数
        
        # 生成完整TeX文件
        tex_content = self.template_header + content + self.template_footer
        
        return tex_content


if __name__ == '__main__':
    # 使用示例
    converter = MDToTeXConverter('templates/gb8567-template.tex')
    
    md_file = Path('docs/templates/DP_文档计划模板.md')
    tex_content = converter.convert(md_file)
    
    # 保存TeX文件
    output_file = Path('temp/direct_conversion_test.tex')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(tex_content)
    
    print(f"✅ 转换完成：{output_file}")
```

---

## 🔍 与Pandoc方案对比

| 特性 | Pandoc方案 | 直接转换方案 |
|------|-----------|-------------|
| **依赖** | 需要Pandoc | 不需要外部依赖 |
| **控制力** | 受限于Pandoc | 完全控制 |
| **后处理** | 需要修复问题 | 不需要修复 |
| **开发工作量** | 小（使用现有工具） | 大（需要自己实现） |
| **维护成本** | 低（依赖Pandoc） | 高（自己维护） |
| **扩展性** | 中等（受限于Pandoc） | 高（完全自由） |
| **性能** | 慢（调用外部程序） | 快（纯Python） |

---

## ✅ 结论

### 可行性：完全可行 ✅

**推荐实现：**

1. **分阶段实现**
   - 先实现核心功能（标题、段落、列表、文本格式）
   - 逐步添加高级功能（表格、代码块、数学公式等）

2. **参考现有映射表**
   - 使用 `docs/MD_TO_LATEX_FORMAT_MAPPING.md` 作为参考
   - 确保转换结果与Pandoc方案一致

3. **保持兼容性**
   - 生成的LaTeX代码应该与Pandoc方案兼容
   - 可以使用相同的模板文件

4. **测试验证**
   - 创建测试用例
   - 对比与Pandoc方案的输出差异

---

## 🎯 下一步行动

1. **创建基础转换器框架**
   - 实现模板加载
   - 实现基础解析函数

2. **实现核心语法**
   - 标题、段落、文本格式、列表

3. **测试验证**
   - 创建测试MD文件
   - 对比转换结果

4. **逐步完善**
   - 添加表格、代码块等高级功能
   - 处理边界情况

---

**文档版本**：v1.0  
**创建日期**：2025-11-06  
**作者**：Auto AI Assistant

