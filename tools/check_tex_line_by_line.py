#!/usr/bin/env python3
"""
逐行检查TeX文件，对照PDF显示问题
重点检查可能导致中文显示为方框的问题
"""

import re
import sys
from pathlib import Path


def check_tex_line_by_line(tex_file: str):
    """逐行检查TeX文件"""
    
    tex_path = Path(tex_file)
    if not tex_path.exists():
        print(f"错误：TeX文件不存在: {tex_path}")
        sys.exit(1)
    
    with open(tex_path, encoding='utf-8') as f:
        lines = f.readlines()
    
    print("=" * 70)
    print("TeX文件逐行检查 - 对照PDF显示问题")
    print("=" * 70)
    print(f"\n文件: {tex_path}")
    print(f"总行数: {len(lines)}")
    print()
    
    issues = []
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
    
    # 检查关键区域（根据PDF中显示为方框的部分）
    key_areas = {
        'PDF格式部分': (460, 480),
        'DOCX格式部分': (470, 490),
        'Markdown格式部分': (478, 490),
        '工具列表部分': (480, 490),
    }
    
    print("=" * 70)
    print("1. 检查关键区域（PDF中显示为方框的部分）")
    print("=" * 70)
    
    for area_name, (start, end) in key_areas.items():
        print(f"\n【{area_name}】行 {start}-{end}:")
        print("-" * 70)
        for i in range(start-1, min(end, len(lines))):
            line = lines[i]
            line_num = i + 1
            
            # 检查中文
            if chinese_pattern.search(line):
                # 检查是否在verbatim或lstlisting中
                in_verbatim = r'\begin{verbatim}' in line or r'\end{verbatim}' in line
                in_lstlisting = r'\begin{lstlisting}' in line or r'\end{lstlisting}' in line
                
                # 检查是否有问题
                problems = []
                
                # 检查1: 在lstlisting中且有中文（应该用verbatim）
                if in_lstlisting and chinese_pattern.search(line):
                    problems.append("⚠️ lstlisting中有中文，应使用verbatim")
                
                # 检查2: 在\texttt{}中且有中文（应该用CJKfamily）
                if r'\texttt{' in line:
                    # 检查是否使用了CJKfamily
                    if r'\CJKfamily{zhfs}' not in line:
                        texttt_with_chinese = re.search(r'\\texttt\{([^}]*[\u4e00-\u9fa5][^}]*)\}', line)
                        if texttt_with_chinese:
                            problems.append(f"⚠️ \\texttt{{}}中有中文: {texttt_with_chinese.group(1)[:20]}")
                
                # 检查3: 检查特殊字符（emoji等）
                emoji_pattern = re.compile(r'[⚠️✅❌]')
                if emoji_pattern.search(line):
                    problems.append("⚠️ 包含emoji字符，可能无法显示")
                
                # 检查4: 检查是否有未转义的特殊字符
                if '%' in line and '\\%' not in line and not line.strip().startswith('%'):
                    problems.append("⚠️ 未转义的%字符")
                
                if problems:
                    print(f"行 {line_num}: {problems[0]}")
                    print(f"  内容: {line.rstrip()[:80]}")
                    issues.append((line_num, problems[0], line.rstrip()[:80]))
                else:
                    # 显示正常的中文行（用于对比）
                    if line.strip() and not line.strip().startswith('%'):
                        print(f"行 {line_num}: ✓ {line.rstrip()[:80]}")
    
    print("\n" + "=" * 70)
    print("2. 检查所有可能的问题模式")
    print("=" * 70)
    
    # 检查所有行
    problem_count = 0
    for i, line in enumerate(lines, 1):
        # 跳过注释和空行
        if line.strip().startswith('%') or not line.strip():
            continue
        
        # 检查问题模式
        problems = []
        
        # 模式1: lstlisting中有中文
        if r'\begin{lstlisting}' in line or (r'\end{lstlisting}' not in line and 'lstlisting' in line.lower()):
            # 检查后续行是否有中文
            if i < len(lines):
                next_lines = '\n'.join(lines[i:min(i+10, len(lines))])
                if chinese_pattern.search(next_lines) and r'\end{lstlisting}' in next_lines:
                    problems.append("lstlisting环境中有中文")
        
        # 模式2: \texttt{}中有中文但未使用CJKfamily
        texttt_matches = re.finditer(r'\\texttt\{([^}]+)\}', line)
        for match in texttt_matches:
            content = match.group(1)
            if chinese_pattern.search(content) and r'\CJKfamily{zhfs}' not in line:
                problems.append(f"\\texttt{{}}中有中文: {content[:30]}")
        
        # 模式3: emoji字符
        if re.search(r'[⚠️✅❌]', line):
            problems.append("包含emoji字符")
        
        if problems:
            problem_count += 1
            if problem_count <= 20:  # 只显示前20个
                print(f"\n行 {i}: {problems[0]}")
                print(f"  内容: {line.rstrip()[:80]}")
    
    print("\n" + "=" * 70)
    print("3. 统计总结")
    print("=" * 70)
    print(f"\n发现的问题: {len(issues) + problem_count} 个")
    
    if issues:
        print("\n关键问题列表:")
        for line_num, problem, content in issues[:10]:
            print(f"  行 {line_num}: {problem}")
    
    print("\n" + "=" * 70)
    print("4. 建议修复")
    print("=" * 70)
    
    if issues or problem_count > 0:
        print("\n需要修复的问题:")
        print("1. 检查所有lstlisting环境，如果包含中文，改为verbatim")
        print("2. 检查所有\\texttt{}，如果包含中文，改为{\\CJKfamily{zhfs}\\ttfamily}")
        print("3. 检查emoji字符，可能需要移除或替换")
    else:
        print("\n✅ 未发现明显问题")
    
    print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python check_tex_line_by_line.py <tex_file>")
        print("\n示例:")
        print("  python check_tex_line_by_line.py temp/DP_文档计划模板_final.tex")
        sys.exit(1)
    
    check_tex_line_by_line(sys.argv[1])

