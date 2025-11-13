#!/usr/bin/env python3
"""
MD到TeX直接转换器（不依赖Pandoc）
实现MD→TeX的一一对应转换

按照开发需求计划实现所有功能：
- FR-1: 标题转换（P0）
- FR-2: 文本格式转换（P0）
- FR-3: 段落处理（P0）
- FR-4: 列表转换（P0）
- FR-5: 表格转换（P1）
- FR-6: 代码块转换（P1）
- FR-7: 链接和图片转换（P1）
- FR-8: 数学公式转换（P2）
- FR-9: 其他元素转换（P2）
- FR-10: YAML元数据处理（P2）

作者：Auto AI Assistant
日期：2025-11-06
版本：v1.0
"""

import io
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    # 设置环境变量确保UTF-8编码
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'  # 禁用Windows遗留stdio
    
    # 设置PowerShell编码为UTF-8（使用多种方法确保成功）
    try:
        import ctypes
        # 方法1：使用Windows API设置控制台代码页为UTF-8 (65001)
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except:
        pass
    
    # 方法2：使用PowerShell命令设置编码
    try:
        import subprocess as sp
        # 设置PowerShell输出编码为UTF-8
        ps_cmd = '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8'
        sp.run(['powershell', '-Command', ps_cmd], capture_output=True, timeout=2)
        # 同时设置代码页
        sp.run(['chcp', '65001'], shell=True, capture_output=True, timeout=2)
    except:
        pass  # 如果失败，继续执行
    
    # 设置标准输出为UTF-8编码
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class MDToTeXConverter:
    """
    MD到TeX直接转换器
    
    功能：将Markdown文件直接转换为LaTeX文件，不依赖Pandoc
    特点：纯Python实现，完全控制转换逻辑，语义一一对应
    """
    
    def __init__(self, template_file: str):
        """
        初始化转换器
        
        Args:
            template_file: LaTeX模板文件路径（包含$body$标记）
        """
        self.template_file = Path(template_file)
        self.template_header = ""
        self.template_footer = ""
        self.load_template()
    
    def load_template(self):
        """加载LaTeX模板文件"""
        if not self.template_file.exists():
            raise FileNotFoundError(f"模板文件不存在: {self.template_file}")
        
        try:
            with open(self.template_file, encoding='utf-8') as f:
                content = f.read()
            
            # 分离模板头部和尾部（使用$body$标记）
            parts = content.split('$body$')
            if len(parts) == 2:
                self.template_header = parts[0]
                self.template_footer = parts[1]
            else:
                # 如果没有$body$标记，使用默认模板
                self.template_header = self.get_default_template_header()
                self.template_footer = "\n\\end{document}\n"
        except Exception as e:
            raise Exception(f"加载模板文件失败: {e}")
    
    def get_default_template_header(self) -> str:
        """获取默认LaTeX模板头部"""
        return """\\documentclass[12pt,a4paper]{article}
\\usepackage{xeCJK}
\\setCJKmainfont{SimSun}
\\setCJKsansfont{SimHei}
\\setCJKmonofont{Courier New}
\\begin{document}
"""
    
    def parse_yaml_front_matter(self, content: str) -> tuple[str, dict]:
        """
        FR-10: 解析YAML front matter
        
        Args:
            content: MD文件内容
            
        Returns:
            (处理后的内容, YAML元数据字典)
        """
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            # 简单解析YAML（不依赖外部库）
            yaml_data = {}
            for line in yaml_content.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    yaml_data[key] = value
            # 移除YAML front matter
            content = content[yaml_match.end():]
            return content, yaml_data
        return content, {}
    
    def parse_headings(self, content: str) -> str:
        """
        FR-1: 解析标题（4级）
        
        MD格式 → LaTeX格式：
        # 标题 → \section{标题}
        ## 标题 → \subsection{标题}
        ### 标题 → \subsubsection{标题}
        #### 标题 → \paragraph{标题}
        """
        # 先保护代码块环境（verbatim和lstlisting）中的内容，避免其中的#被识别为标题
        # 使用临时标记替换代码块环境
        code_blocks = []
        def protect_code_block(match):
            code_blocks.append(match.group(0))
            return f'__CODE_BLOCK_{len(code_blocks)-1}__'
        
        # 保护verbatim环境
        content = re.sub(r'\\begin\{verbatim\}.*?\\end\{verbatim\}', protect_code_block, content, flags=re.DOTALL)
        # 保护lstlisting环境
        content = re.sub(r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}', protect_code_block, content, flags=re.DOTALL)
        
        # 一级标题： # 标题（支持前后空格）
        # 注意：不在这里转义下划线，因为标题可能包含行内代码等Markdown格式
        # 转义将在parse_text_format()中统一处理
        content = re.sub(r'^#\s+(.+?)\s*$', r'\\section{\1}', content, flags=re.MULTILINE)
        # 二级标题： ## 标题
        content = re.sub(r'^##\s+(.+?)\s*$', r'\\subsection{\1}', content, flags=re.MULTILINE)
        # 三级标题： ### 标题
        content = re.sub(r'^###\s+(.+?)\s*$', r'\\subsubsection{\1}', content, flags=re.MULTILINE)
        # 四级标题： #### 标题
        content = re.sub(r'^####\s+(.+?)\s*$', r'\\paragraph{\1}', content, flags=re.MULTILINE)
        
        # 恢复代码块环境
        for i, code_block in enumerate(code_blocks):
            content = content.replace(f'__CODE_BLOCK_{i}__', code_block)
        
        return content
    
    def parse_text_format(self, content: str) -> str:
        """
        FR-2: 解析文本格式
        
        MD格式 → LaTeX格式：
        **文本** → \textbf{文本}
        *文本* → \textit{文本}
        `代码` → \texttt{代码}（如果包含中文则使用\textttCJK）
        """
        # 注意：处理顺序很重要，先处理代码，再处理粗体，最后处理斜体
        
        # 行内代码：`代码` → \texttt{代码}
        # 检测是否包含中文，如果包含中文需要使用支持中文的方式
        def replace_inline_code(match):
            code_text = match.group(1)
            # 转义LaTeX特殊字符（特别是下划线）
            escaped_code = self._escape_latex_text(code_text)
            # 检测是否包含中文
            has_chinese = bool(re.search(r'[\u4e00-\u9fa5]', code_text))
            if has_chinese:
                # 包含中文，使用支持中文的格式
                # 简单处理：直接显示，不使用texttt（因为Courier New不支持中文）
                # 或者使用等宽字体样式但用中文字体
                return f'{{\\CJKfamily{{zhfs}}\\ttfamily {escaped_code}}}'
            else:
                # 纯英文/代码，使用texttt
                return f'\\texttt{{{escaped_code}}}'
        
        # 使用更精确的正则，避免匹配代码块
        content = re.sub(r'`([^`\n]+?)`', replace_inline_code, content)
        
        # 加粗：**文本** → \textbf{文本}
        content = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', content)
        
        # 斜体：*文本* → \textit{文本}
        # 只匹配不在**内部的单个*，且不在代码块中
        content = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)', r'\\textit{\1}', content)
        
        return content
    
    def parse_lists(self, content: str) -> str:
        """
        FR-4: 解析列表（有序、无序、嵌套）
        
        MD格式 → LaTeX格式：
        - 项目 → \begin{itemize}\item 项目\end{itemize}
        1. 项目 → \begin{enumerate}\item 项目\end{enumerate}
        """
        lines = content.split('\n')
        result = []
        # 使用栈来跟踪嵌套列表
        list_stack = []  # [(indent, type), ...]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 检测无序列表：- 项目
            unordered_match = re.match(r'^(\s*)(-\s+)(.+)$', line)
            # 检测有序列表：1. 项目
            ordered_match = re.match(r'^(\s*)(\d+\.\s+)(.+)$', line)
            
            if unordered_match:
                indent_len = len(unordered_match.group(1))
                item_text = unordered_match.group(3).strip()
                # 注意：不在这里转义下划线，因为文本可能包含行内代码等Markdown格式
                # 转义将在parse_text_format()中统一处理
                
                # 处理嵌套列表
                self._handle_list_nesting(result, list_stack, indent_len, 'itemize')
                result.append(f'\\item {item_text}')
                
            elif ordered_match:
                indent_len = len(ordered_match.group(1))
                item_text = ordered_match.group(3).strip()
                # 注意：不在这里转义下划线，因为文本可能包含行内代码等Markdown格式
                # 转义将在parse_text_format()中统一处理
                
                # 处理嵌套列表
                self._handle_list_nesting(result, list_stack, indent_len, 'enumerate')
                result.append(f'\\item {item_text}')
                
            else:
                # 空行：保持，但检查是否需要关闭列表
                if not line.strip():
                    # 空行，检查下一行是否还是列表
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        next_unordered = re.match(r'^(\s*)(-\s+)(.+)$', next_line)
                        next_ordered = re.match(r'^(\s*)(\d+\.\s+)(.+)$', next_line)
                        # 如果下一行不是列表，关闭当前列表
                        if not next_unordered and not next_ordered:
                            self._close_all_lists(result, list_stack)
                    result.append(line)
                else:
                    # 非列表行，关闭所有打开的列表
                    self._close_all_lists(result, list_stack)
                    result.append(line)
            
            i += 1
        
        # 文件末尾关闭所有列表
        self._close_all_lists(result, list_stack)
        
        return '\n'.join(result)
    
    def _handle_list_nesting(self, result: list[str], list_stack: list[tuple[int, str]], 
                             indent_len: int, list_type: str):
        """处理列表嵌套逻辑"""
        # 关闭缩进级别大于当前级别的列表（但不关闭等于的）
        while list_stack and list_stack[-1][0] > indent_len:
            old_indent, old_type = list_stack.pop()
            result.append(f'\\end{{{old_type}}}')
        
        # 如果需要开始新列表（当前缩进级别大于栈顶，或者栈为空）
        if not list_stack or list_stack[-1][0] < indent_len:
            result.append(f'\\begin{{{list_type}}}')
            list_stack.append((indent_len, list_type))
        # 如果当前缩进级别等于栈顶，说明是同一级别的item，不需要新建列表环境
        # 但需要检查类型是否一致，如果不一致需要关闭旧的并创建新的
        elif list_stack and list_stack[-1][0] == indent_len:
            if list_stack[-1][1] != list_type:
                # 类型不一致，关闭旧的，创建新的
                old_indent, old_type = list_stack.pop()
                result.append(f'\\end{{{old_type}}}')
                result.append(f'\\begin{{{list_type}}}')
                list_stack.append((indent_len, list_type))
            # 类型一致，不需要操作，直接添加item即可
    
    def _close_all_lists(self, result: list[str], list_stack: list[tuple[int, str]]):
        """关闭所有打开的列表"""
        while list_stack:
            indent, list_type = list_stack.pop()
            result.append(f'\\end{{{list_type}}}')
    
    def parse_tables(self, content: str) -> str:
        """
        FR-5: 解析表格
        
        MD格式 → LaTeX格式：
        | 列1 | 列2 | → \begin{longtable}{|p{3cm}|p{4cm}|}...
        """
        # 匹配表格块（表头 + 分隔符 + 数据行）
        # 更精确的正则：匹配完整的表格块
        lines = content.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 检查是否是表格行（以|开头和结尾）
            if line.startswith('|') and line.endswith('|'):
                # 尝试解析表格
                table_lines = []
                table_start = i
                
                # 收集表头
                header_line = line
                table_lines.append(header_line)
                i += 1
                
                # 收集分隔符行
                if i < len(lines):
                    separator_line = lines[i].strip()
                    if separator_line.startswith('|') and separator_line.endswith('|'):
                        table_lines.append(separator_line)
                        i += 1
                        
                        # 收集数据行
                        while i < len(lines):
                            data_line = lines[i].strip()
                            if data_line.startswith('|') and data_line.endswith('|'):
                                table_lines.append(data_line)
                                i += 1
                            else:
                                break
                        
                        # 生成LaTeX表格
                        tex_table = self._generate_latex_table(table_lines)
                        result.append(tex_table)
                        continue
            
            result.append(lines[i])
            i += 1
        
        return '\n'.join(result)
    
    def _generate_latex_table(self, table_lines: list[str]) -> str:
        """生成LaTeX表格代码"""
        if len(table_lines) < 2:
            return '\n'.join(table_lines)
        
        # 解析表头
        header_line = table_lines[0]
        headers = [h.strip() for h in header_line[1:-1].split('|') if h.strip()]
        num_cols = len(headers)
        
        if num_cols == 0:
            return '\n'.join(table_lines)
        
        # 解析数据行（跳过分隔符行）
        data_rows = []
        for row_line in table_lines[2:]:
            cells = [c.strip() for c in row_line[1:-1].split('|') if c.strip()]
            if len(cells) == num_cols:
                data_rows.append(cells)
        
        # 生成LaTeX表格代码
        col_widths = self._calculate_table_column_widths(num_cols)
        col_def = '|' + '|'.join(col_widths) + '|'
        
        tex = f'\\begin{{longtable}}{{{col_def}}}\n'
        tex += '\\hline\n'
        
        # 表头（转义特殊字符）
        escaped_headers = [self._escape_latex_text(h) for h in headers]
        tex += ' & '.join(escaped_headers) + ' \\\\\n'
        tex += '\\hline\n'
        
        # 数据行（转义特殊字符）
        for row in data_rows:
            escaped_row = [self._escape_latex_text(cell) for cell in row]
            tex += ' & '.join(escaped_row) + ' \\\\\n'
        
        tex += '\\hline\n'
        tex += '\\end{longtable}\n'
        
        return tex
    
    def _calculate_table_column_widths(self, num_cols: int) -> list[str]:
        """
        计算表格列宽
        
        根据列数智能分配列宽，确保表格美观
        """
        # 默认列宽分配策略
        if num_cols == 1:
            return ['p{16cm}']
        elif num_cols == 2:
            return ['p{7cm}', 'p{7cm}']
        elif num_cols == 3:
            return ['p{4cm}', 'p{5cm}', 'p{5cm}']
        elif num_cols == 4:
            return ['p{3cm}', 'p{4cm}', 'p{4cm}', 'p{3cm}']
        elif num_cols == 5:
            return ['p{2.5cm}', 'p{3cm}', 'p{3cm}', 'p{3cm}', 'p{2.5cm}']
        else:
            # 超过5列，平均分配
            width_per_col = f'{16.0 / num_cols:.2f}cm'
            return [f'p{{{width_per_col}}}'] * num_cols
    
    def parse_code_blocks(self, content: str) -> str:
        """
        FR-6: 解析代码块
        
        MD格式 → LaTeX格式：
        ```language 代码 ``` → \begin{lstlisting}[language=language]代码\end{lstlisting}
        对于包含中文的纯文本代码块，使用verbatim环境
        """
        # 匹配围栏代码块：```language 代码 ```
        code_block_pattern = r'```(\w+)?\n(.*?)```'
        
        def replace_code_block(match):
            language = match.group(1) or ''
            code = match.group(2)
            
            # 检测是否包含中文或树状结构字符
            has_chinese = bool(re.search(r'[\u4e00-\u9fa5]', code))
            has_tree_chars = bool(re.search(r'[├└│─┌┐└┘┬┴┼│─━]', code))
            
            # 检测是否是编程代码（有明确的代码特征）
            has_code_features = bool(re.search(r'[{}();=<>+\-*/\[\]\\]', code))
            # 检测是否是配置类代码（yaml, json等）
            is_config_code = language.lower() in ['yaml', 'json', 'xml', 'html', 'css']
            # 检测是否是编程语言代码
            is_programming_code = language.lower() in ['python', 'java', 'c', 'cpp', 'javascript', 
                                                       'typescript', 'go', 'rust', 'php', 'ruby',
                                                       'shell', 'bash', 'sh', 'sql', 'r']
            
            # 决策逻辑：
            # 1. 如果包含树状字符，使用verbatim环境（因为listings对树状字符支持不好）
            # 2. 如果包含中文或树状字符，优先使用verbatim（确保正确显示）
            # 3. 其他情况使用lstlisting（模板已配置中文支持）
            
            if has_tree_chars:
                # 包含树状字符 → 使用verbatim环境（确保树状字符正确显示）
                return f'\\begin{{verbatim}}\n{code}\\end{{verbatim}}\n'
            elif has_chinese:
                # 包含中文但不包含树状字符 → 使用lstlisting（模板已配置中文支持）
                code = self._escape_latex_special_chars(code)
                if language:
                    return f'\\begin{{lstlisting}}[language={language}]\n{code}\\end{{lstlisting}}\n'
                else:
                    return f'\\begin{{lstlisting}}\n{code}\\end{{lstlisting}}\n'
            else:
                # 不包含中文和树状字符 → 使用lstlisting
                code = self._escape_latex_special_chars(code)
                if language:
                    return f'\\begin{{lstlisting}}[language={language}]\n{code}\\end{{lstlisting}}\n'
                else:
                    return f'\\begin{{lstlisting}}\n{code}\\end{{lstlisting}}\n'
        
        content = re.sub(code_block_pattern, replace_code_block, content, flags=re.DOTALL)
        return content
    
    def _escape_latex_special_chars(self, text: str) -> str:
        """转义LaTeX特殊字符（用于代码块中的代码）"""
        # LaTeX特殊字符转义映射
        escape_map = {
            '\\': '\\textbackslash{}',
            '{': '\\{',
            '}': '\\}',
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '~': '\\textasciitilde{}',
        }
        
        for char, escaped in escape_map.items():
            text = text.replace(char, escaped)
        
        return text
    
    def _escape_latex_text(self, text: str) -> str:
        """
        转义LaTeX普通文本中的特殊字符（用于普通文本、URL、路径等）
        
        注意：这个函数只转义下划线等关键字符，用于普通文本环境
        不转义反斜杠、大括号等（因为这些可能已经在LaTeX命令中）
        """
        # 只转义在普通文本中会导致问题的字符
        # 下划线必须转义，否则LaTeX会认为进入数学模式
        # 注意：避免重复转义，如果已经是\_，就不再转义
        text = re.sub(r'(?<!\\)_', r'\\_', text)  # 只转义不在反斜杠后的下划线
        # 其他可能需要的转义
        text = text.replace('&', '\\&')
        text = text.replace('%', '\\%')
        text = text.replace('$', '\\$')
        text = text.replace('#', '\\#')
        text = text.replace('^', '\\textasciicircum{}')
        text = text.replace('~', '\\textasciitilde{}')
        # 注意：不转义 { } 和 \，因为这些可能已经在LaTeX命令中
        
        return text
    
    def _escape_text_in_plain_context(self, text: str) -> str:
        """
        在普通文本上下文中转义下划线（用于列表项、标题等）
        
        这个函数会转义不在LaTeX命令中的下划线
        例如："使用下划线_分隔" → "使用下划线\\_分隔"
        但 "使用下划线\\texttt{\\_}" 中的下划线已经在命令中，不需要再次转义
        """
        # 如果文本中已经有LaTeX命令（如\texttt、\textbf等），说明已经处理过
        # 此时只需要转义不在命令中的下划线
        # 简单策略：转义所有下划线，因为如果下划线在命令中（如\texttt{_}），
        # 它应该已经被转义为\_了
        
        # 但是，如果文本中已经有\texttt{\_}这样的，我们不应该再次转义
        # 所以，我们需要避免转义已经在\{...\}中的下划线
        
        # 更安全的策略：只转义不在大括号对中的下划线
        # 使用正则表达式匹配并转义不在{...}中的下划线
        result = []
        i = 0
        brace_depth = 0
        
        while i < len(text):
            char = text[i]
            
            if char == '{':
                brace_depth += 1
                result.append(char)
            elif char == '}':
                brace_depth -= 1
                result.append(char)
            elif char == '_' and brace_depth == 0:
                # 不在大括号中，转义下划线
                result.append('\\_')
            elif char == '\\' and i + 1 < len(text) and text[i + 1] == '_':
                # 已经是转义的下划线，保持不变
                result.append('\\_')
                i += 1  # 跳过下一个字符
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def _escape_plain_text_underscores(self, content: str) -> str:
        """
        转义普通文本中的下划线（不在LaTeX命令中的）
        
        这个函数会转义不在\texttt{}、\href{}、\includegraphics{}等命令中的下划线
        例如："使用下划线_分隔" → "使用下划线\\_分隔"
        但 "\texttt{convert\_md\_to\_docx.bat}" 中的下划线已经在命令中，不需要再次转义
        """
        result = []
        i = 0
        brace_depth = 0
        in_command = False  # 是否在LaTeX命令的参数中（如\texttt{...}）
        command_start = -1  # 命令开始位置
        
        while i < len(content):
            char = content[i]
            
            # 检测LaTeX命令开始（如\texttt{、\href{等）
            if char == '\\' and i + 1 < len(content):
                # 检查下一个字符是否是下划线（说明已经转义过了）
                if content[i + 1] == '_':
                    # 已经是转义的下划线，直接添加
                    result.append('\\_')
                    i += 2
                    continue
                
                # 检查是否是命令（字母或特殊字符）
                next_char = content[i + 1]
                if next_char.isalpha() or next_char in ['{', '}', '[', ']', '(', ')', '_', '^', '&', '%', '$', '#']:
                    # 找到命令，查找命令名
                    cmd_end = i + 1
                    while cmd_end < len(content) and (content[cmd_end].isalpha() or content[cmd_end] == '*'):
                        cmd_end += 1
                    
                    # 检查命令后是否有大括号
                    if cmd_end < len(content) and content[cmd_end] == '{':
                        in_command = True
                        command_start = i
                        # 添加命令和开括号
                        result.append(content[i:cmd_end + 1])
                        brace_depth = 1
                        i = cmd_end + 1
                        continue
            
            if char == '{':
                brace_depth += 1
                result.append(char)
            elif char == '}':
                brace_depth -= 1
                result.append(char)
                # 如果大括号深度回到0，说明命令参数结束
                if brace_depth == 0 and in_command:
                    in_command = False
            elif char == '_':
                # 检查result的最后一个字符是否是反斜杠（说明已经转义过了）
                if len(result) > 0 and result[-1] == '\\':
                    # 已经转义过了，保持原样
                    result.append(char)
                elif not in_command or brace_depth == 0:
                    # 如果不在命令参数中，转义下划线
                    result.append('\\_')
                else:
                    # 在命令参数中，保持原样（因为已经在\texttt{}等中，应该已经被转义了）
                    result.append(char)
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def parse_links_images(self, content: str) -> str:
        """
        FR-7: 解析链接和图片
        
        MD格式 → LaTeX格式：
        [文本](URL) → \href{URL}{文本}
        ![alt](path) → \includegraphics{path}
        """
        def replace_image(match):
            alt_text = match.group(1)
            path = match.group(2)
            # 转义路径中的下划线等特殊字符
            escaped_path = self._escape_latex_text(path)
            return f'\\includegraphics{{{escaped_path}}}'
        
        def replace_link(match):
            link_text = match.group(1)
            url = match.group(2)
            # 转义URL和链接文本中的下划线等特殊字符
            escaped_url = self._escape_latex_text(url)
            escaped_text = self._escape_latex_text(link_text)
            return f'\\href{{{escaped_url}}}{{{escaped_text}}}'
        
        # 先处理图片：![alt](path) → \includegraphics{path}
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, content)
        
        # 再处理链接：[文本](URL) → \href{URL}{文本}
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
        
        return content
    
    def parse_math(self, content: str) -> str:
        """
        FR-8: 解析数学公式
        
        MD格式 → LaTeX格式：
        $公式$ → $公式$（保持原样）
        $$公式$$ → \[公式\]
        """
        # 块级公式：$$公式$$
        content = re.sub(r'\$\$(.+?)\$\$', r'\\[\1\\]', content, flags=re.DOTALL)
        
        # 行内公式：$公式$（保持原样，但需要确保不在代码块中）
        # 注意：已经处理的$$不会被再次处理
        
        return content
    
    def parse_horizontal_rules(self, content: str) -> str:
        """
        FR-9: 解析水平线
        
        MD格式 → LaTeX格式：
        --- → \hrule
        """
        # --- 或 *** 或 ___
        content = re.sub(r'^---\s*$', r'\\hrule', content, flags=re.MULTILINE)
        content = re.sub(r'^\*\*\*\s*$', r'\\hrule', content, flags=re.MULTILINE)
        content = re.sub(r'^___\s*$', r'\\hrule', content, flags=re.MULTILINE)
        return content
    
    def parse_blockquotes(self, content: str) -> str:
        """
        FR-9: 解析引用块
        
        MD格式 → LaTeX格式：
        > 文本 → \begin{quote}文本\end{quote}
        """
        lines = content.split('\n')
        result = []
        in_quote = False
        
        for line in lines:
            if line.startswith('> '):
                if not in_quote:
                    result.append('\\begin{quote}')
                    in_quote = True
                result.append(line[2:])  # 移除 '> '
            elif line.startswith('>'):
                # 处理只有 > 没有空格的情况
                if not in_quote:
                    result.append('\\begin{quote}')
                    in_quote = True
                result.append(line[1:].lstrip())
            else:
                if in_quote:
                    result.append('\\end{quote}')
                    in_quote = False
                result.append(line)
        
        if in_quote:
            result.append('\\end{quote}')
        
        return '\n'.join(result)
    
    def escape_percent_in_text(self, content: str) -> str:
        """
        转义正文中的百分号（不在代码块、verbatim、数学公式等特殊环境中）
        """
        lines = content.split('\n')
        result = []
        in_verbatim = False
        in_lstlisting = False
        in_math = False
        
        for line in lines:
            # 跟踪环境状态
            if r'\begin{verbatim}' in line:
                in_verbatim = True
                result.append(line)
                continue
            elif r'\end{verbatim}' in line:
                in_verbatim = False
                result.append(line)
                continue
            elif r'\begin{lstlisting}' in line:
                in_lstlisting = True
                result.append(line)
                continue
            elif r'\end{lstlisting}' in line:
                in_lstlisting = False
                result.append(line)
                continue
            
            # 检查数学公式状态（简单检测）
            if r'\[' in line or r'$$' in line or r'\(' in line:
                in_math = True
            if r'\]' in line or r'$$' in line or r'\)' in line:
                in_math = False
            
            # 如果在verbatim、lstlisting或数学公式中，不转义
            if in_verbatim or in_lstlisting or in_math:
                result.append(line)
                continue
            
            # 跳过注释行（LaTeX注释）
            stripped = line.strip()
            if stripped.startswith('%'):
                result.append(line)
                continue
            
            # 转义正文中的百分号（但不在已转义的、URL、邮箱等中）
            # 匹配百分号前后的数字或中文字符（如：20%、90%、约5%）
            # 排除已经在\texttt{}中的（因为代码中可能需要%）
            if '%' in line:
                # 使用正则表达式匹配并替换：数字% 或 中文% 的模式
                # 避免匹配URL、邮箱等
                def replace_percent(match):
                    before = match.group(1)
                    after = match.group(2)
                    # 检查是否在URL或邮箱中
                    if 'http' in before[-10:] or '@' in before[-20:] or '://' in before[-20:]:
                        return match.group(0)  # 不转义
                    # 检查是否在\texttt等命令中（已经有转义逻辑）
                    if r'\texttt{' in before[-50:] or r'\verb' in before[-50:]:
                        return match.group(0)  # 不转义
                    # 否则转义
                    return before + '\\%' + after
                
                # 匹配模式：数字、中文、空格等后跟%号，然后跟中文、空格等
                line = re.sub(r'([0-9\u4e00-\u9fa5\s]+)%([\u4e00-\u9fa5\s\.,；，、：:\)\)\}]*)', 
                             replace_percent, line)
            
            result.append(line)
        
        return '\n'.join(result)
    
    def replace_emoji(self, content: str) -> str:
        """
        替换emoji字符为LaTeX可显示的文本
        """
        # emoji替换映射
        emoji_map = {
            '⚠️': '[警告]',
            '✅': '[正确]',
            '❌': '[错误]',
            '📋': '[列表]',
            '🔍': '[搜索]',
            '🔤': '[文字]',
            '🔐': '[锁定]',
            '✨': '[星星]',
            '📦': '[包裹]',
            '🔗': '[链接]',
            '💡': '[灯泡]',
        }
        
        for emoji, replacement in emoji_map.items():
            content = content.replace(emoji, replacement)
        
        return content
    
    def convert(self, md_file: str) -> str:
        """
        主转换函数
        
        Args:
            md_file: MD文件路径
            
        Returns:
            生成的LaTeX代码字符串
        """
        print("  [1/15] 读取MD文件...")
        # 读取MD文件
        md_path = Path(md_file)
        if not md_path.exists():
            raise FileNotFoundError(f"MD文件不存在: {md_file}")
        
        try:
            with open(md_path, encoding='utf-8') as f:
                content = f.read()
            file_size = len(content)
            line_count = content.count('\n') + 1
            print(f"        ✓ 文件读取成功，大小: {file_size} 字符，行数: {line_count}")
        except Exception as e:
            raise Exception(f"读取MD文件失败: {e}")
        
        print("  [2/15] 解析YAML front matter...")
        # 1. 解析YAML front matter（FR-10）
        content, yaml_data = self.parse_yaml_front_matter(content)
        if yaml_data:
            print(f"        ✓ 发现YAML元数据: {len(yaml_data)} 个字段")
        else:
            print("        ✓ 未发现YAML元数据")
        
        print("  [3/15] 替换emoji字符...")
        # 1.5. 替换emoji字符（在解析前处理）
        original_content = content
        content = self.replace_emoji(content)
        if content != original_content:
            print("        ✓ 已替换emoji字符")
        else:
            print("        ✓ 未发现emoji字符")
        
        # 2. 解析各种元素（按顺序处理）
        # 注意：顺序很重要，先处理复杂结构，再处理简单格式，避免冲突
        print("  [4/15] 解析代码块...")
        code_block_count = len(re.findall(r'```', content)) // 2
        content = self.parse_code_blocks(content)
        print(f"        ✓ 处理了 {code_block_count} 个代码块")
        
        print("  [5/15] 解析表格...")
        table_count = len(re.findall(r'^\|.*\|$', content, re.MULTILINE)) // 2  # 粗略估算
        content = self.parse_tables(content)
        print(f"        ✓ 处理了表格（检测到约 {table_count} 行表格内容）")
        
        print("  [6/15] 解析引用块...")
        quote_count = len(re.findall(r'^> ', content, re.MULTILINE))
        content = self.parse_blockquotes(content)
        print(f"        ✓ 处理了 {quote_count} 行引用内容")
        
        print("  [7/15] 解析列表...")
        list_item_count = len(re.findall(r'^[\s]*[-*] ', content, re.MULTILINE)) + len(re.findall(r'^[\s]*\d+\. ', content, re.MULTILINE))
        content = self.parse_lists(content)
        print(f"        ✓ 处理了 {list_item_count} 个列表项")
        
        print("  [8/15] 解析标题...")
        heading_count = len(re.findall(r'^#+\s+', content, re.MULTILINE))
        content = self.parse_headings(content)
        print(f"        ✓ 处理了 {heading_count} 个标题")
        
        print("  [9/15] 解析数学公式...")
        math_count = len(re.findall(r'\$\$', content)) // 2 + len(re.findall(r'(?<!\$)\$(?!\$)[^$]+\$(?!\$)', content))
        content = self.parse_math(content)
        print(f"        ✓ 处理了数学公式（检测到约 {math_count} 个公式）")
        
        print("  [10/15] 解析链接和图片...")
        link_count = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
        image_count = len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content))
        content = self.parse_links_images(content)
        print(f"        ✓ 处理了 {link_count} 个链接，{image_count} 个图片")
        
        print("  [11/15] 解析文本格式（加粗、斜体、行内代码）...")
        bold_count = len(re.findall(r'\*\*', content)) // 2
        italic_count = len(re.findall(r'(?<!\*)\*(?!\*)', content)) // 2
        inline_code_count = len(re.findall(r'`[^`]+`', content))
        content = self.parse_text_format(content)
        print(f"        ✓ 处理了文本格式（粗体: {bold_count}, 斜体: {italic_count}, 行内代码: {inline_code_count}）")
        
        print("  [12/15] 解析水平线...")
        hr_count = len(re.findall(r'^---\s*$|^\*\*\*\s*$|^___\s*$', content, re.MULTILINE))
        content = self.parse_horizontal_rules(content)
        print(f"        ✓ 处理了 {hr_count} 条水平线")
        
        print("  [13/15] 转义普通文本中的下划线...")
        underscore_count = content.count('_') - content.count('\\_')
        content = self._escape_plain_text_underscores(content)
        escaped_underscore_count = content.count('\\_')
        print(f"        ✓ 转义了下划线（转义了 {escaped_underscore_count} 个）")
        
        print("  [14/15] 转义正文中的百分号...")
        percent_count = content.count('%') - content.count('\\%')
        content = self.escape_percent_in_text(content)
        escaped_percent_count = content.count('\\%')
        print(f"        ✓ 转义了百分号（转义了 {escaped_percent_count} 个）")
        
        print("  [15/15] 处理段落...")
        # 3. 段落处理（FR-3）
        # 段落内容已经保持，只需要确保空行正确处理
        content = self._process_paragraphs(content)
        print("        ✓ 段落处理完成")
        
        print("  [完成] 生成完整TeX文件...")
        # 4. 生成完整TeX文件
        tex_content = self.template_header + content + self.template_footer
        tex_size = len(tex_content)
        tex_line_count = tex_content.count('\n') + 1
        print(f"        ✓ TeX内容生成完成，大小: {tex_size} 字符，行数: {tex_line_count}")
        
        return tex_content
    
    def _process_paragraphs(self, content: str) -> str:
        """
        FR-3: 处理段落
        
        确保段落之间有适当的空行，但不过度
        """
        # 移除多余的空行（超过2个连续空行）
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content


def find_xelatex():
    """查找XeLaTeX可执行文件"""
    system = platform.system()
    
    if system == 'Windows':
        # 检查PATH中的xelatex
        try:
            result = subprocess.run(['xelatex', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return 'xelatex'
        except:
            pass
        
        # 检查环境变量TEXLIVE_ROOT
        texlive_root = os.environ.get('TEXLIVE_ROOT')
        if texlive_root:
            for year in ['2025', '2024', '2023', '2022', '2021', '2020']:
                # 检查两个可能的路径：bin\windows（新版本）和 bin\win32（旧版本）
                for bin_dir in ['windows', 'win32']:
                    xelatex_path = Path(texlive_root) / year / 'bin' / bin_dir / 'xelatex.exe'
                    if xelatex_path.exists():
                        return str(xelatex_path)
        
        # Windows常见路径
        possible_paths = []
        for drive in ['C:', 'D:', 'E:']:
            for year in ['2025', '2024', '2023', '2022', '2021', '2020']:
                # 检查两个可能的路径：bin\windows（新版本）和 bin\win32（旧版本）
                for bin_dir in ['windows', 'win32']:
                    possible_paths.append(f'{drive}\\texlive\\{year}\\bin\\{bin_dir}\\xelatex.exe')
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        # MiKTeX路径
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
        program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        
        miktex_paths = [
            Path(program_files) / 'MiKTeX' / 'miktex' / 'bin' / 'x64' / 'xelatex.exe',
            Path(program_files_x86) / 'MiKTeX' / 'miktex' / 'bin' / 'xelatex.exe',
        ]
        
        for path in miktex_paths:
            if path.exists():
                return str(path)
                
    elif system == 'Linux':
        possible_paths = ['/usr/bin/xelatex', '/usr/local/bin/xelatex']
        for path in possible_paths:
            if Path(path).exists():
                return path
        return 'xelatex'
        
    elif system == 'Darwin':  # macOS
        possible_paths = [
            '/usr/local/texlive/bin/universal-darwin/xelatex',
            '/Library/TeX/texbin/xelatex',
        ]
        for path in possible_paths:
            if Path(path).exists():
                return path
        return 'xelatex'
    
    return None


def compile_tex_to_pdf(tex_path: Path, show_output: bool = True) -> bool:
    """
    编译TeX文件为PDF
    
    Args:
        tex_path: TeX文件路径
        show_output: 是否显示完整输出
        
    Returns:
        是否成功（PDF已生成且无错误）
    """
    print("  [1/4] 查找XeLaTeX可执行文件...")
    xelatex = find_xelatex()
    if not xelatex:
        print("        ❌ 错误：找不到XeLaTeX")
        print("        请确保已安装TeX Live或MiKTeX")
        return False
    
    print(f"        ✓ 找到XeLaTeX: {xelatex}")
    print()
    
    print("  [2/4] 准备编译参数...")
    # 编译命令 - 使用最严格的模式，遇到任何错误立即停止
    work_dir = tex_path.parent
    tex_name = tex_path.name
    pdf_path = tex_path.with_suffix('.pdf')
    
    compile_cmd = [
        xelatex,
        '-interaction=errorstopmode',  # 遇到错误立即停止（最严格模式）
        '-halt-on-error',              # 遇到错误立即停止
        '-file-line-error',            # 显示文件名和行号
        tex_name
    ]
    
    print(f"        ✓ 工作目录: {work_dir.absolute()}")
    print(f"        ✓ TeX文件: {tex_name}")
    print(f"        ✓ 输出PDF: {pdf_path.name}")
    print(f"        ✓ 编译命令: {' '.join(compile_cmd)}")
    print()
    
    # 第一次编译
    print("  [3/4] 第一次编译（生成内容）...")
    print("        - 目的: 生成PDF内容和基本结构")
    print("        - 模式: errorstopmode（遇到任何错误立即停止，最严格模式）")
    print()
    # 准备环境变量，确保UTF-8编码
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    if sys.platform == 'win32':
        env['LANG'] = 'zh_CN.UTF-8'
        env['LC_ALL'] = 'zh_CN.UTF-8'
    
    try:
        result1 = subprocess.run(
            compile_cmd,
            cwd=str(work_dir),
            capture_output=True,  # 始终捕获输出，以便检查错误
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,  # 传递环境变量
            timeout=300
        )
        
        # 显示完整输出（用户要求看到全部原始执行过程和输出）
        # 对输出进行编码修复，确保中文正确显示
        if result1.stdout:
            try:
                # 尝试修复编码问题
                stdout_text = result1.stdout
                # 如果输出包含乱码，尝试重新编码
                if isinstance(stdout_text, bytes):
                    stdout_text = stdout_text.decode('utf-8', errors='replace')
                print(stdout_text)
            except Exception as e:
                # 如果编码失败，直接打印（可能已经是正确编码）
                print(result1.stdout)
        if result1.stderr:
            try:
                stderr_text = result1.stderr
                if isinstance(stderr_text, bytes):
                    stderr_text = stderr_text.decode('utf-8', errors='replace')
                print(stderr_text, file=sys.stderr)
            except Exception as e:
                print(result1.stderr, file=sys.stderr)
        
        # 检查PDF是否已生成
        pdf_generated = pdf_path.exists()
        
        # 检查输出中是否有错误或警告（用户要求不能有任何错误或警告）
        output_text = (result1.stderr + result1.stdout).lower()
        has_error = 'error' in output_text or 'fatal' in output_text or 'emergency stop' in output_text
        has_warning = 'warning' in output_text
        has_missing_character = 'missing character' in output_text  # 检测Missing character警告
        
        # 允许第一次编译时的正常警告（这些警告在第二次编译时会自动解决）
        # 1. hyperref的"Rerun"警告 - 正常，需要第二次编译
        # 2. lastpage的"undefined reference"警告 - 正常，需要第二次编译
        # 3. rerunfilecheck的"Rerun"警告 - 正常，需要第二次编译
        normal_first_run_warnings = [
            'rerun to get',
            'undefined reference',
            'label(s) may have changed',
            'rerun to get cross-references',
            'rerun to get outlines',
            'rerun to get the references'
        ]
        
        # 检查是否有真正的警告（排除正常的第一次编译警告）
        has_real_warning = False
        if has_warning:
            # 检查是否所有警告都是正常的第一次编译警告
            warning_lines = [line.lower() for line in (result1.stderr + result1.stdout).split('\n') if 'warning' in line.lower()]
            real_warnings = []
            for warning_line in warning_lines:
                is_normal = any(normal_warning in warning_line for normal_warning in normal_first_run_warnings)
                if not is_normal:
                    real_warnings.append(warning_line)
            has_real_warning = len(real_warnings) > 0
        
        # 定义清理函数：删除已生成的PDF并打印错误信息
        def cleanup_and_fail(reason, details=""):
            print(f"\n❌ 第一次编译失败：{reason}")
            if details:
                print(f"   详细信息：{details}")
            if pdf_generated:
                try:
                    pdf_path.unlink()
                    print(f"   ✓ 已删除不完整的PDF文件：{pdf_path.name}")
                except Exception as e:
                    print(f"   ⚠️ 删除PDF文件失败：{e}")
            return False
        
        if result1.returncode != 0:
            error_details = f"返回码: {result1.returncode}"
            if result1.stderr:
                error_details += f"\n   错误输出: {result1.stderr[:500]}"
            return cleanup_and_fail("返回码非0（编译过程有错误）", error_details)
        
        if has_error:
            error_lines = [line for line in (result1.stderr + result1.stdout).split('\n') if 'error' in line.lower() or 'fatal' in line.lower()][:10]
            error_details = "\n   ".join(error_lines[:5])
            return cleanup_and_fail("检测到LaTeX错误", error_details)
        
        if has_real_warning:
            warning_lines = [line for line in (result1.stderr + result1.stdout).split('\n') if 'warning' in line.lower()][:10]
            # 过滤掉正常的第一次编译警告
            real_warning_lines = []
            for line in warning_lines:
                line_lower = line.lower()
                is_normal = any(normal_warning in line_lower for normal_warning in normal_first_run_warnings)
                if not is_normal:
                    real_warning_lines.append(line)
            if real_warning_lines:
                warning_details = "\n   ".join(real_warning_lines[:5])
                return cleanup_and_fail("检测到LaTeX警告（用户要求不能有任何警告）", warning_details)
        
        if has_missing_character:
            missing_count = (result1.stderr + result1.stdout).lower().count('missing character')
            return cleanup_and_fail(f"检测到Missing character警告（共{missing_count}个，用户要求不能有任何不完美）", "verbatim环境中的中文无法正确显示")
        
        if not pdf_generated:
            return cleanup_and_fail("PDF未生成", "编译过程可能已中断")
        
        print()
        print("        ✓ 第一次编译完成（无错误无警告）")
        if pdf_generated:
            pdf_size = pdf_path.stat().st_size
            print(f"        ✓ PDF已生成，大小: {pdf_size / 1024:.2f} KB")
        print()
        
    except subprocess.TimeoutExpired:
        print()
        print("        ❌ 第一次编译超时（超过5分钟）")
        return False
    except Exception as e:
        print()
        print(f"        ❌ 第一次编译过程出错：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 第二次编译（生成目录和交叉引用）
    print("  [4/4] 第二次编译（生成目录和交叉引用）...")
    print("        - 目的: 生成目录、交叉引用和页码")
    print("        - 模式: errorstopmode（遇到任何错误立即停止，最严格模式）")
    print()
    try:
        # 使用相同的环境变量设置
        result2 = subprocess.run(
            compile_cmd,
            cwd=str(work_dir),
            capture_output=True,  # 始终捕获输出，以便检查错误
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,  # 传递环境变量
            timeout=300
        )
        
        # 显示完整输出（用户要求看到全部原始执行过程和输出）
        # 对输出进行编码修复，确保中文正确显示
        if result2.stdout:
            try:
                stdout_text = result2.stdout
                if isinstance(stdout_text, bytes):
                    stdout_text = stdout_text.decode('utf-8', errors='replace')
                print(stdout_text)
            except Exception as e:
                print(result2.stdout)
        if result2.stderr:
            try:
                stderr_text = result2.stderr
                if isinstance(stderr_text, bytes):
                    stderr_text = stderr_text.decode('utf-8', errors='replace')
                print(stderr_text, file=sys.stderr)
            except Exception as e:
                print(result2.stderr, file=sys.stderr)
        
        # 检查PDF是否已生成
        pdf_generated_after_second = pdf_path.exists()
        
        # 检查输出中是否有错误或警告（用户要求不能有任何错误或警告）
        output_text = (result2.stderr + result2.stdout).lower()
        has_error = 'error' in output_text or 'fatal' in output_text or 'emergency stop' in output_text
        has_warning = 'warning' in output_text
        has_missing_character = 'missing character' in output_text  # 检测Missing character警告
        
        # 允许第二次编译时的正常警告（这些是LaTeX编译的正常行为）
        normal_second_run_warnings = [
            'rerun to get',
            'label(s) may have changed',
            'rerun to get cross-references',
            'rerun to get outlines',
            'rerun to get the references'
        ]
        
        # 检查是否有真正的警告（排除正常的第二次编译警告）
        has_real_warning_second = False
        if has_warning:
            warning_lines = [line.lower() for line in (result2.stderr + result2.stdout).split('\n') if 'warning' in line.lower()]
            real_warnings = []
            for warning_line in warning_lines:
                is_normal = any(normal_warning in warning_line for normal_warning in normal_second_run_warnings)
                if not is_normal:
                    real_warnings.append(warning_line)
            has_real_warning_second = len(real_warnings) > 0
        
        # 定义清理函数：删除已生成的PDF并打印错误信息
        def cleanup_and_fail_second(reason, details=""):
            print(f"\n❌ 第二次编译失败：{reason}")
            if details:
                print(f"   详细信息：{details}")
            if pdf_path.exists():
                try:
                    pdf_path.unlink()
                    print(f"   ✓ 已删除不完整的PDF文件：{pdf_path.name}")
                except Exception as e:
                    print(f"   ⚠️ 删除PDF文件失败：{e}")
            return False
        
        if result2.returncode != 0:
            error_details = f"返回码: {result2.returncode}"
            if result2.stderr:
                error_details += f"\n   错误输出: {result2.stderr[:500]}"
            return cleanup_and_fail_second("返回码非0（编译过程有错误）", error_details)
        
        if has_error:
            error_lines = [line for line in (result2.stderr + result2.stdout).split('\n') if 'error' in line.lower() or 'fatal' in line.lower()][:10]
            error_details = "\n   ".join(error_lines[:5])
            return cleanup_and_fail_second("检测到LaTeX错误", error_details)
        
        if has_real_warning_second:
            warning_lines = [line for line in (result2.stderr + result2.stdout).split('\n') if 'warning' in line.lower()][:10]
            # 过滤掉正常的第二次编译警告
            real_warning_lines = []
            for line in warning_lines:
                line_lower = line.lower()
                is_normal = any(normal_warning in line_lower for normal_warning in normal_second_run_warnings)
                if not is_normal:
                    real_warning_lines.append(line)
            if real_warning_lines:
                warning_details = "\n   ".join(real_warning_lines[:5])
                return cleanup_and_fail_second("检测到LaTeX警告（用户要求不能有任何警告）", warning_details)
        
        if has_missing_character:
            missing_count = (result2.stderr + result2.stdout).lower().count('missing character')
            return cleanup_and_fail_second(f"检测到Missing character警告（共{missing_count}个，用户要求不能有任何不完美）", "verbatim环境中的中文无法正确显示")
        
        if not pdf_generated_after_second:
            return cleanup_and_fail_second("PDF未生成", "编译过程可能已中断")
        
        print()
        print("        ✓ 第二次编译完成（无错误无警告）")
        print()
        
        # 最终检查PDF是否生成
        if pdf_path.exists():
            size = pdf_path.stat().st_size
            print("  [完成] 最终检查PDF文件...")
            print(f"        ✓ PDF文件已生成")
            print(f"        ✓ 文件路径: {pdf_path.absolute()}")
            if size < 1024 * 1024:
                print(f"        ✓ 文件大小: {size / 1024:.2f} KB ({size} 字节)")
            else:
                print(f"        ✓ 文件大小: {size / 1024 / 1024:.2f} MB ({size} 字节)")
            return True
        else:
            print()
            print("        ❌ PDF文件未生成")
            return False
            
    except subprocess.TimeoutExpired:
        print()
        print("        ❌ 第二次编译超时（超过5分钟）")
        return False
    except Exception as e:
        print()
        print(f"        ❌ 第二次编译过程出错：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数 - 命令行接口，支持三种模式：md--tex, tex--pdf, md--pdf（默认）"""
    project_root = Path(__file__).parent.parent
    
    # 解析命令模式
    mode = 'md--pdf'  # 默认模式
    args_start = 1
    
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        if first_arg in ['md--tex', 'tex--pdf', 'md--pdf']:
            mode = first_arg
            args_start = 2
    
    # 根据模式处理
    if mode == 'md--tex':
        # MD转TeX模式
        if len(sys.argv) < args_start + 2:
            print("=" * 60)
            print("MD→TeX转换器")
            print("=" * 60)
            print()
            print("用法:")
            print("  python md_tex_pdf.py md--tex <md_file> <template_file> [output_file]")
            print()
            print("参数:")
            print("  md_file        - 输入的Markdown文件路径")
            print("  template_file  - LaTeX模板文件路径（包含$body$标记）")
            print("  output_file    - 输出的LaTeX文件路径（可选）")
            print()
            sys.exit(1)
        
        md_file = sys.argv[args_start]
        template_file = sys.argv[args_start + 1]
        output_file = sys.argv[args_start + 2] if len(sys.argv) > args_start + 2 else None
        
        md_path = project_root / md_file
        template_path = project_root / template_file
        
        if not md_path.exists():
            print(f"❌ 错误：MD文件不存在：{md_path}")
            sys.exit(1)
        
        if not template_path.exists():
            print(f"❌ 错误：模板文件不存在：{template_path}")
            sys.exit(1)
        
        if output_file:
            output_path = project_root / output_file
        else:
            temp_dir = project_root / 'temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            output_path = temp_dir / (md_path.stem + '.tex')
        
        try:
            print("=" * 60)
            print("MD→TeX转换器")
            print("=" * 60)
            print(f"MD文件: {md_path}")
            print(f"模板文件: {template_path}")
            print(f"输出文件: {output_path}")
            print()
            
            # 创建转换器
            converter = MDToTeXConverter(str(template_path))
            
            # 转换
            print("正在转换...")
            tex_content = converter.convert(str(md_path))
            
            # 保存
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(tex_content)
            
            print()
            print("=" * 60)
            print("✅ 转换完成！")
            print("=" * 60)
            print(f"输出文件: {output_path.absolute()}")
            print(f"文件大小: {output_path.stat().st_size / 1024:.1f} KB")
            print()
            
        except FileNotFoundError as e:
            print()
            print("=" * 60)
            print("❌ 文件错误")
            print("=" * 60)
            print(f"错误: {e}")
            sys.exit(1)
        except Exception as e:
            print()
            print("=" * 60)
            print("❌ 转换失败")
            print("=" * 60)
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif mode == 'tex--pdf':
        # TeX转PDF模式
        if len(sys.argv) < args_start + 1:
            print("=" * 60)
            print("TeX→PDF转换器")
            print("=" * 60)
            print()
            print("用法:")
            print("  python md_tex_pdf.py tex--pdf <tex_file>")
            print()
            print("参数:")
            print("  tex_file  - 输入的TeX文件路径")
            print()
            sys.exit(1)
        
        tex_file = sys.argv[args_start]
        tex_path = project_root / tex_file
        
        if not tex_path.exists():
            print(f"❌ 错误：TeX文件不存在：{tex_path}")
            sys.exit(1)
        
        print("=" * 60)
        print("TeX→PDF转换器")
        print("=" * 60)
        print(f"TeX文件: {tex_path.absolute()}")
        print()
        
        success = compile_tex_to_pdf(tex_path, show_output=True)
        
        if success:
            pdf_path = tex_path.with_suffix('.pdf')
            print()
            print("=" * 60)
            print("✅ 转换完成！")
            print("=" * 60)
            print(f"PDF文件: {pdf_path.absolute()}")
            print()
        else:
            print()
            print("=" * 60)
            print("❌ 转换失败")
            print("=" * 60)
            print(f"TeX文件: {tex_path.absolute()}")
            print("请检查错误信息并修复后重试")
            sys.exit(1)
    
    else:  # mode == 'md--pdf'
        # MD转PDF模式（默认）
        if len(sys.argv) < args_start + 1:
            print("=" * 60)
            print("MD→PDF一键转换工具")
            print("=" * 60)
            print()
            print("用法:")
            print("  python md_tex_pdf.py <md_file>")
            print("  python md_tex_pdf.py <md_file> [template_file] [output_pdf]")
            print()
            print("参数:")
            print("  md_file      - 输入的Markdown文件路径（必需）")
            print("  template_file - LaTeX模板文件路径（可选，默认templates/gb8567-template.tex）")
            print("  output_pdf   - 输出的PDF文件路径（可选，默认temp/<md文件名>.pdf）")
            print()
            print("示例:")
            print("  python md_tex_pdf.py docs/切换到清华镜像源命令.md")
            print("  python md_tex_pdf.py docs/切换到清华镜像源命令.md templates/gb8567-template.tex")
            print()
            print("其他模式:")
            print("  md--tex      - MD转TeX")
            print("  tex--pdf     - TeX转PDF")
            print()
            sys.exit(1)
        
        md_file = sys.argv[args_start]
        template_file = sys.argv[args_start + 1] if len(sys.argv) > args_start + 1 else 'templates/gb8567-template.tex'
        output_pdf = sys.argv[args_start + 2] if len(sys.argv) > args_start + 2 else None
        
        md_path = project_root / md_file
        
        # 如果MD文件路径不存在，尝试相对路径
        if not md_path.exists():
            # 尝试在docs目录下查找
            docs_path = project_root / 'docs' / md_file
            if docs_path.exists():
                md_path = docs_path
            else:
                print(f"❌ 错误：MD文件不存在：{md_path}")
                print(f"   也尝试查找：{docs_path}")
                sys.exit(1)
        
        template_path = project_root / template_file
        
        if not template_path.exists():
            print(f"❌ 错误：模板文件不存在：{template_path}")
            sys.exit(1)
        
        # 自动生成输出文件名
        if output_pdf:
            pdf_path = project_root / output_pdf
        else:
            temp_dir = project_root / 'temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = temp_dir / (md_path.stem + '.pdf')
        
        tex_path = pdf_path.parent / (pdf_path.stem + '.tex')
        
        print("=" * 60)
        print("MD→PDF一键转换工具")
        print("=" * 60)
        print(f"MD文件：{md_path.absolute()}")
        print(f"模板文件：{template_path.absolute()}")
        print(f"输出PDF：{pdf_path.absolute()}")
        print(f"中间TeX：{tex_path.absolute()}")
        print()
        print("📋 使用的参数（自动推断）：")
        print(f"  - MD文件：{md_file}")
        print(f"  - 模板文件：{template_file} {'（默认）' if len(sys.argv) == args_start + 1 else ''}")
        print(f"  - 输出PDF：{pdf_path.relative_to(project_root)} {'（自动生成）' if not output_pdf else ''}")
        print()
        
        # 步骤1：MD转TeX
        print("=" * 60)
        print("步骤1：MD → TeX")
        print("=" * 60)
        print()
        
        try:
            print("  [初始化] 创建MD到TeX转换器...")
            # 创建转换器
            converter = MDToTeXConverter(str(template_path))
            print(f"        ✓ 转换器创建成功")
            print(f"        ✓ 模板文件: {template_path.absolute()}")
            print()
            
            print("  [转换] 开始转换MD内容到TeX格式...")
            print()
            # 转换
            tex_content = converter.convert(str(md_path))
            print()
            
            print("  [保存] 保存TeX文件...")
            # 保存
            tex_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(tex_content)
            
            tex_file_size = tex_path.stat().st_size
            print(f"        ✓ TeX文件已保存")
            print(f"        ✓ 文件路径: {tex_path.absolute()}")
            print(f"        ✓ 文件大小: {tex_file_size / 1024:.1f} KB ({tex_file_size} 字节)")
            print()
            print("✅ MD→TeX转换完成！")
            print()
            
        except FileNotFoundError as e:
            print()
            print("=" * 60)
            print("❌ MD→TeX转换失败")
            print("=" * 60)
            print(f"错误: {e}")
            sys.exit(1)
        except Exception as e:
            print()
            print("=" * 60)
            print("❌ MD→TeX转换失败")
            print("=" * 60)
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        # 步骤2：TeX编译为PDF
        print("=" * 60)
        print("步骤2：TeX → PDF")
        print("=" * 60)
        print()
        
        success = compile_tex_to_pdf(tex_path, show_output=True)
        
        if success:
            print()
            print("=" * 60)
            print("✅ PDF生成成功！")
            print("=" * 60)
            print(f"PDF文件：{pdf_path.absolute()}")
            size = pdf_path.stat().st_size
            if size < 1024 * 1024:
                print(f"文件大小：{size / 1024:.2f} KB")
            else:
                print(f"文件大小：{size / 1024 / 1024:.2f} MB")
            print()
            print("✅ 转换完成！可以打开PDF查看结果。")
        else:
            print()
            print("=" * 60)
            print("❌ PDF生成失败")
            print("=" * 60)
            print(f"TeX文件已生成：{tex_path.absolute()}")
            print("请检查错误信息并修复后重试")
            sys.exit(1)


if __name__ == '__main__':
    main()
