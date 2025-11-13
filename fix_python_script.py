import os
import sys
import subprocess
from pathlib import Path

# 获取脚本路径
script_path = Path("/home/test/jiekou-20251103/src/jmeter_test_suite/infrastructure/scripts/one_click_single.py")

# 读取文件内容
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有 python3_cmd 为 python_cmd
content = content.replace('python3_cmd', 'python_cmd')

# 写回文件
with open(script_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Python 脚本更新完成")
