#!/usr/bin/env python3
"""
TeX文件逐行审核工具
检测LaTeX编译错误、格式问题、中文显示问题等
"""

import re
import sys
from collections import defaultdict
from pathlib import Path


class TeXAuditor:
    """TeX文件审核器"""
    
    def __init__(self, tex_file: str):
        self.tex_file = Path(tex_file)
        self.lines = []
        self.issues = []
        self.line_context = {}
        
    def load_file(self):
        """加载TeX文件"""
        if not self.tex_file.exists():
            raise FileNotFoundError(f"TeX文件不存在: {self.tex_file}")
        
        with open(self.tex_file, encoding='utf-8') as f:
            self.lines = f.readlines()
        
        print(f"[OK] 已加载文件: {self.tex_file}")
        print(f"   总行数: {len(self.lines)}")
        print()
    
    def audit(self):
        """执行审核"""
        print("=" * 70)
        print("TeX文件逐行审核")
        print("=" * 70)
        print()
        
        # 1. 检查基本结构
        self._check_document_structure()
        
        # 2. 检查命令闭合
        self._check_command_balance()
        
        # 3. 检查中文显示问题
        self._check_chinese_display()
        
        # 4. 检查转义问题
        self._check_escaping()
        
        # 5. 检查特殊字符
        self._check_special_chars()
        
        # 6. 检查环境匹配
        self._check_environments()
        
        # 7. 检查嵌套问题
        self._check_nesting()
        
        # 8. 检查常见LaTeX错误
        self._check_common_errors()
        
        # 生成报告
        self._generate_report()
    
    def _add_issue(self, line_num: int, category: str, severity: str, 
                   message: str, suggestion: str = ""):
        """添加问题记录"""
        line_content = self.lines[line_num - 1].rstrip() if line_num <= len(self.lines) else ""
        self.issues.append({
            'line': line_num,
            'category': category,
            'severity': severity,  # critical, warning, info
            'message': message,
            'suggestion': suggestion,
            'content': line_content
        })
    
    def _check_document_structure(self):
        """检查文档结构"""
        print("📋 检查文档结构...")
        
        has_begin_document = False
        has_end_document = False
        
        for i, line in enumerate(self.lines, 1):
            if r'\begin{document}' in line:
                has_begin_document = True
            if r'\end{document}' in line:
                has_end_document = True
        
        if not has_begin_document:
            self._add_issue(1, '结构', 'critical', '缺少 \\begin{document}')
        if not has_end_document:
            self._add_issue(len(self.lines), '结构', 'critical', '缺少 \\end{document}')
        
        print(f"   {'✅' if has_begin_document and has_end_document else '❌'} 文档结构检查完成")
        print()
    
    def _check_command_balance(self):
        """检查命令闭合"""
        print("🔍 检查命令闭合（大括号、命令）...")
        
        brace_stack = []
        command_pattern = re.compile(r'\\([a-zA-Z]+\*?)(\*?)')
        
        for i, line in enumerate(self.lines, 1):
            # 检查大括号
            for char in line:
                if char == '{':
                    brace_stack.append((i, 'brace'))
                elif char == '}':
                    if brace_stack and brace_stack[-1][1] == 'brace':
                        brace_stack.pop()
                    elif brace_stack and brace_stack[-1][1] != 'brace':
                        # 不匹配
                        self._add_issue(i, '闭合', 'critical', 
                                       f'大括号不匹配：在闭合 }} 时栈顶是 {brace_stack[-1][1]}',
                                       '检查大括号是否配对')
                    else:
                        self._add_issue(i, '闭合', 'critical', 
                                       '多余的闭合大括号 }',
                                       '删除多余的大括号或添加对应的开始大括号')
            
            # 检查未闭合的命令
            open_braces = line.count('{')
            close_braces = line.count('}')
            if open_braces > close_braces:
                # 可能在下一行继续
                continue
            
            # 检查常见命令是否闭合
            unclosed_cmds = re.findall(r'\\(textbf|textit|texttt|CJKfamily|section|subsection|subsubsection|paragraph)\{([^{]*?)$', line)
            for cmd, content in unclosed_cmds:
                if not content.strip():
                    self._add_issue(i, '闭合', 'warning', 
                                   f'命令 \\{cmd}{{}} 可能未正确闭合',
                                   f'检查 \\{cmd}{{}} 命令是否完整')
        
        # 检查文件末尾未闭合的大括号
        if brace_stack:
            for line_num, brace_type in brace_stack:
                self._add_issue(line_num, '闭合', 'critical',
                               f'未闭合的大括号 {{ (在行{line_num})',
                               '添加对应的闭合大括号 }')
        
        print(f"   检查完成，发现 {len([i for i in self.issues if i['category'] == '闭合'])} 个闭合问题")
        print()
    
    def _check_chinese_display(self):
        """检查中文显示问题"""
        print("🔤 检查中文显示问题...")
        
        chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
        verbatim_open = False
        lstlisting_open = False
        
        for i, line in enumerate(self.lines, 1):
            # 检查环境状态
            if r'\begin{verbatim}' in line:
                verbatim_open = True
                continue
            elif r'\end{verbatim}' in line:
                verbatim_open = False
                continue
            elif r'\begin{lstlisting}' in line:
                lstlisting_open = True
                continue
            elif r'\end{lstlisting}' in line:
                lstlisting_open = False
                continue
            
            # 跳过verbatim环境中的内容（这些应该没问题）
            if verbatim_open:
                continue
            
            # 检查中文在错误的位置
            if chinese_pattern.search(line):
                # 在lstlisting中且有中文 - 应该是verbatim
                if lstlisting_open:
                    self._add_issue(i, '中文显示', 'critical',
                                   'lstlisting环境中包含中文，无法正确显示',
                                   '将包含中文的代码块改为verbatim环境')
                
                # 在texttt中且有中文
                if r'\texttt{' in line:
                    # 检查是否使用了CJKfamily或zhfs
                    if r'\CJKfamily{zhfs}' not in line and r'{\CJKfamily{zhfs}' not in line:
                        # 进一步检查是否是\texttt{中文}模式
                        texttt_pattern = r'\\texttt\{([^}]*[\u4e00-\u9fa5][^}]*)\}'
                        if re.search(texttt_pattern, line):
                            self._add_issue(i, '中文显示', 'critical',
                                           '\\texttt{}中包含中文，Courier New无法显示',
                                           '使用 {\\CJKfamily{zhfs}\\ttfamily 中文} 替代 \\texttt{中文}')
        
        print(f"   检查完成，发现 {len([i for i in self.issues if i['category'] == '中文显示'])} 个中文显示问题")
        print()
    
    def _check_escaping(self):
        """检查转义问题"""
        print("🔐 检查转义问题...")
        
        verbatim_open = False
        
        for i, line in enumerate(self.lines, 1):
            # 跟踪verbatim环境状态
            if r'\begin{verbatim}' in line:
                verbatim_open = True
                continue
            elif r'\end{verbatim}' in line:
                verbatim_open = False
                continue
            
            # 跳过verbatim环境中的内容
            if verbatim_open:
                continue
            
            # 检查是否在注释中（LaTeX注释）
            stripped = line.strip()
            if stripped.startswith('%'):
                continue  # 跳过注释行
            
            # 检查未转义的&（不在表格环境中）
            if '&' in line and '\\&' not in line:
                # 检查是否在表格环境中
                in_table_env = any(env in '\n'.join(self.lines[max(0, i-5):i+1]) 
                                 for env in [r'\begin{longtable}', r'\begin{table}', 
                                            r'\begin{tabular}', r'\begin{array}'])
                if not in_table_env and '\\begin' not in line and '\\end' not in line:
                    # 检查是否有表格相关的命令
                    if not any(cmd in line for cmd in ['longtable', 'table', 'tabular', 'array', '\\\\']):
                        self._add_issue(i, '转义', 'warning',
                                       '发现未转义的 & 字符（不在表格中）',
                                       '在普通文本中使用 \\& 替代 &')
            
            # 检查未转义的%（在正文内容中，不在注释中）
            if '%' in line and '\\%' not in line:
                # 排除注释行和已转义的
                if not stripped.startswith('%'):
                    # 检查是否有中文后跟%的情况（可能是正文中的百分号）
                    if re.search(r'[\u4e00-\u9fa5].*%', line):
                        self._add_issue(i, '转义', 'warning',
                                       '正文中发现未转义的 % 字符',
                                       '使用 \\% 替代 %')
        
        print(f"   检查完成，发现 {len([i for i in self.issues if i['category'] == '转义'])} 个转义问题")
        print()
    
    def _check_special_chars(self):
        """检查特殊字符"""
        print("✨ 检查特殊字符...")
        
        # 树状结构字符
        tree_chars = ['├', '└', '│', '─']
        verbatim_open = False
        
        for i, line in enumerate(self.lines, 1):
            # 跟踪verbatim环境
            if r'\begin{verbatim}' in line:
                verbatim_open = True
                continue
            elif r'\end{verbatim}' in line:
                verbatim_open = False
                continue
            
            # 检查树状字符是否在verbatim环境中
            has_tree = any(char in line for char in tree_chars)
            if has_tree and not verbatim_open:
                # 检查是否在verbatim块中（前面有\begin{verbatim}但还没闭合）
                # 这个已经在上面通过verbatim_open检查了
                # 只在确实不在verbatim中时报告
                self._add_issue(i, '特殊字符', 'warning',
                               '发现树状结构字符，但不在verbatim环境中',
                               '将树状结构放在 \\begin{verbatim}...\\end{verbatim} 中')
        
        print(f"   检查完成，发现 {len([i for i in self.issues if i['category'] == '特殊字符'])} 个特殊字符问题")
        print()
    
    def _check_environments(self):
        """检查环境匹配"""
        print("📦 检查LaTeX环境匹配...")
        
        env_stack = []
        env_pattern = re.compile(r'\\(begin|end)\{([^}]+)\}')
        
        for i, line in enumerate(self.lines, 1):
            matches = env_pattern.findall(line)
            for cmd, env_name in matches:
                if cmd == 'begin':
                    env_stack.append((env_name, i))
                elif cmd == 'end':
                    if not env_stack:
                        self._add_issue(i, '环境', 'critical',
                                       f'\\end{{{env_name}}} 没有对应的 \\begin{{{env_name}}}',
                                       f'添加 \\begin{{{env_name}}} 或删除多余的 \\end{{{env_name}}}')
                    elif env_stack[-1][0] != env_name:
                        expected = env_stack[-1][0]
                        expected_line = env_stack[-1][1]
                        self._add_issue(i, '环境', 'critical',
                                       f'环境不匹配：\\end{{{env_name}}} 但期望 \\end{{{expected}}} (开始于行{expected_line})',
                                       f'将 \\end{{{env_name}}} 改为 \\end{{{expected}}} 或在行{expected_line}将 \\begin{{{expected}}} 改为 \\begin{{{env_name}}}')
                        env_stack.pop()
                    else:
                        env_stack.pop()
        
        # 检查未闭合的环境
        for env_name, line_num in env_stack:
            self._add_issue(line_num, '环境', 'critical',
                           f'环境 {env_name} 开始于行{line_num}但未闭合',
                           f'添加 \\end{{{env_name}}}')
        
        print(f"   检查完成，发现 {len([i for i in self.issues if i['category'] == '环境'])} 个环境问题")
        print()
    
    def _check_nesting(self):
        """检查嵌套问题"""
        print("🔗 检查命令嵌套...")
        
        for i, line in enumerate(self.lines, 1):
            # 检查text格式命令嵌套
            if r'\textbf{' in line and r'\textit{' in line:
                # 检查是否嵌套正确
                if line.count(r'\textbf{') > 1 or line.count(r'\textit{') > 1:
                    self._add_issue(i, '嵌套', 'info',
                                   '发现多个文本格式命令，检查嵌套是否正确',
                                   '确保格式命令正确嵌套')
            
            # 检查texttt嵌套
            if r'\texttt{' in line:
                # 检查是否有未闭合的texttt
                texttt_count = line.count(r'\texttt{')
                close_count = line.count('}')
                # 简单检查，可能有误报
                if texttt_count > 0 and close_count < texttt_count:
                    # 检查下一行
                    if i < len(self.lines):
                        next_line = self.lines[i]
                        if '}' not in next_line[:50]:  # 前50个字符
                            self._add_issue(i, '嵌套', 'warning',
                                           '\\texttt{} 可能跨越了多行，检查是否正确闭合',
                                           '确保 \\texttt{ 和 } 在同一行或正确处理多行情况')
        
        print(f"   检查完成，发现 {len([i for i in self.issues if i['category'] == '嵌套'])} 个嵌套问题")
        print()
    
    def _check_common_errors(self):
        """检查常见LaTeX错误"""
        print("⚠️ 检查常见LaTeX错误...")
        
        verbatim_open = False
        
        for i, line in enumerate(self.lines, 1):
            # 跟踪verbatim环境
            if r'\begin{verbatim}' in line:
                verbatim_open = True
                continue
            elif r'\end{verbatim}' in line:
                verbatim_open = False
                continue
            
            # 跳过verbatim中的内容
            if verbatim_open:
                continue
            
            # 检查section嵌套
            if r'\section{' in line and r'\section{' in line.replace(r'\section{', '', 1):
                self._add_issue(i, '常见错误', 'warning',
                               'section命令可能嵌套',
                               '检查section是否正确闭合')
            
            # 检查未转义的$（不在数学环境中）
            dollar_count = line.count('$')
            if dollar_count > 0 and dollar_count % 2 != 0:
                # 检查是否在数学命令中
                if r'\[' not in line and r'\]' not in line and r'\(' not in line and r'\)' not in line:
                    self._add_issue(i, '常见错误', 'warning',
                                   f'发现奇数个 $ 符号（{dollar_count}个）',
                                   '检查数学公式是否正确闭合')
            
            # 检查空的大括号组（只检查明显的）
            if r'{}' in line:
                # 排除命令中的空参数
                if not re.search(r'\\[a-zA-Z]+\{\}', line):
                    if len(line.strip()) > 3:
                        self._add_issue(i, '常见错误', 'info',
                                       '发现空的大括号组 {}',
                                       '检查是否有遗漏的内容或参数')
        
        print(f"   检查完成，发现 {len([i for i in self.issues if i['category'] == '常见错误'])} 个常见错误")
        print()
    
    def _generate_report(self):
        """生成审核报告"""
        print("=" * 70)
        print("审核报告")
        print("=" * 70)
        print()
        
        # 按严重程度分类
        critical_issues = [i for i in self.issues if i['severity'] == 'critical']
        warning_issues = [i for i in self.issues if i['severity'] == 'warning']
        info_issues = [i for i in self.issues if i['severity'] == 'info']
        
        # 按类别分类
        by_category = defaultdict(list)
        for issue in self.issues:
            by_category[issue['category']].append(issue)
        
        print(f"📊 问题统计：")
        print(f"   严重问题 (Critical): {len(critical_issues)} 个")
        print(f"   警告 (Warning): {len(warning_issues)} 个")
        print(f"   信息 (Info): {len(info_issues)} 个")
        print(f"   总计: {len(self.issues)} 个")
        print()
        
        # 按类别显示
        print("📋 按类别分类：")
        for category, issues in sorted(by_category.items()):
            print(f"   {category}: {len(issues)} 个")
        print()
        
        # 显示严重问题
        if critical_issues:
            print("=" * 70)
            print("🔴 严重问题 (Critical)")
            print("=" * 70)
            for issue in sorted(critical_issues, key=lambda x: x['line']):
                print(f"\n行 {issue['line']}: {issue['message']}")
                print(f"   内容: {issue['content'][:80]}")
                if issue['suggestion']:
                    print(f"   建议: {issue['suggestion']}")
            print()
        
        # 显示警告
        if warning_issues:
            print("=" * 70)
            print("🟡 警告 (Warning)")
            print("=" * 70)
            # 只显示前20个，避免输出过长
            for issue in sorted(warning_issues, key=lambda x: x['line'])[:20]:
                print(f"\n行 {issue['line']}: {issue['message']}")
                print(f"   内容: {issue['content'][:80]}")
                if issue['suggestion']:
                    print(f"   建议: {issue['suggestion']}")
            
            if len(warning_issues) > 20:
                print(f"\n... 还有 {len(warning_issues) - 20} 个警告未显示")
            print()
        
        # 显示信息问题（仅前10个）
        if info_issues:
            print("=" * 70)
            print("ℹ️ 信息 (Info) - 前10个")
            print("=" * 70)
            for issue in sorted(info_issues, key=lambda x: x['line'])[:10]:
                print(f"\n行 {issue['line']}: {issue['message']}")
                print(f"   内容: {issue['content'][:80]}")
            
            if len(info_issues) > 10:
                print(f"\n... 还有 {len(info_issues) - 10} 个信息问题未显示")
            print()
        
        # 总结和建议
        print("=" * 70)
        print("💡 修复建议")
        print("=" * 70)
        
        if critical_issues:
            print("\n1. 🔴 优先修复严重问题：")
            print("   - 修复所有未闭合的大括号和环境")
            print("   - 确保文档结构完整")
        
        if warning_issues:
            print("\n2. 🟡 然后处理警告：")
            print("   - 修复中文显示问题")
            print("   - 检查转义问题")
        
        print("\n3. ✅ 验证修复：")
        print("   - 重新编译TeX文件")
        print("   - 检查PDF输出")
        print("   - 逐页验证格式")
        
        print()
        print("=" * 70)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python audit_tex.py <tex_file>")
        print("\n示例:")
        print("  python audit_tex.py temp/DP_文档计划模板_v3.tex")
        sys.exit(1)
    
    tex_file = sys.argv[1]
    
    try:
        auditor = TeXAuditor(tex_file)
        auditor.load_file()
        auditor.audit()
        
    except Exception as e:
        print(f"❌ 审核过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

