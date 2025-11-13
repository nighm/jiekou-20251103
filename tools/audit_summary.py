#!/usr/bin/env python3
"""
生成简化的审核报告（只显示统计信息）
"""

import sys
from pathlib import Path

# 导入审核器
sys.path.insert(0, str(Path(__file__).parent))
from audit_tex import TeXAuditor


def main():
    if len(sys.argv) < 2:
        print("用法: python audit_summary.py <tex_file>")
        sys.exit(1)
    
    tex_file = sys.argv[1]
    
    auditor = TeXAuditor(tex_file)
    auditor.load_file()
    auditor.audit()
    
    # 只显示统计
    critical = [i for i in auditor.issues if i['severity'] == 'critical']
    warning = [i for i in auditor.issues if i['severity'] == 'warning']
    info = [i for i in auditor.issues if i['severity'] == 'info']
    
    print("\n" + "="*70)
    print("简化统计报告")
    print("="*70)
    print(f"\n严重问题 (Critical): {len(critical)} 个")
    if critical:
        by_cat = {}
        for i in critical:
            by_cat[i['category']] = by_cat.get(i['category'], 0) + 1
        for cat, count in sorted(by_cat.items()):
            print(f"  - {cat}: {count} 个")
    
    print(f"\n警告 (Warning): {len(warning)} 个")
    if warning:
        by_cat = {}
        for i in warning:
            by_cat[i['category']] = by_cat.get(i['category'], 0) + 1
        for cat, count in sorted(by_cat.items()):
            print(f"  - {cat}: {count} 个")
    
    print(f"\n总计: {len(auditor.issues)} 个问题")
    print("="*70)

if __name__ == '__main__':
    main()

