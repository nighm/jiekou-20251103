#!/bin/bash
# JMeter Test Suite v3.0 - One-Click Single Interface (Linux/macOS)
# Usage: bash 一键运行-单个接口.sh

# 启用调试模式
set -x

# 设置控制台编码为 UTF-8
export LANG=C.UTF-8
export LANGUAGE=en_US:en
export LC_ALL=C.UTF-8

# 记录开始时间
START_TIME=$(date +%s)
echo "=== 脚本开始执行 $(date) ==="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 设置虚拟环境目录
VENV_DIR="$SCRIPT_DIR/venv"

# 检查 Python 命令
PYTHON_CMD="python3"
if ! command -v python3; then
    echo "Python3 未找到，尝试使用 python 命令..."
    PYTHON_CMD="python"
    if ! command -v python; then
        echo "❌ 未找到 Python，请先安装 Python 3.6 或更高版本"
        echo "💡 Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "💡 CentOS/RHEL: sudo yum install python3 python3-pip"
        exit 1
    fi
fi

echo "===================================="
echo "  JMeter Test Suite v3.0 One-Click"
echo "===================================="
echo ""
echo "当前执行入口: 一键运行-单个接口.sh"
echo "内部流程由 Python 模块统一处理，日志将保存至 logs 目录"
echo ""

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "🔄 创建虚拟环境..."
    $PYTHON_CMD -m venv "$VENV_DIR" || {
        echo "❌ 创建虚拟环境失败"
        echo "💡 请确保已安装 python3-venv 包"
        echo "💡 Ubuntu/Debian: sudo apt install python3-venv"
        exit 1
    }
fi

# 激活虚拟环境
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "❌ 无法激活虚拟环境"
    exit 1
fi

# 设置 Python 路径
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# 升级 pip 并安装依赖
echo "🔄 安装/更新依赖..."
"$VENV_DIR/bin/pip" install --upgrade pip
# 显示详细的安装信息
"$VENV_DIR/bin/pip" install -v -e .

# 执行 Python 模块
echo "🚀 启动测试..."
# 设置 PYTHONUNBUFFERED 以确保 Python 输出不会被缓冲
export PYTHONUNBUFFERED=1
# 执行 Python 模块并显示详细输出
set +x  # 临时关闭调试模式以避免过多输出
"$VENV_DIR/bin/python" -u -m jmeter_test_suite.infrastructure.scripts.one_click_single
EXIT_CODE=$?
set -x  # 重新启用调试模式

echo ""
echo "执行完成，退出码: $EXIT_CODE"
if [ "$EXIT_CODE" -ne 0 ]; then
    echo "⚠️  任务执行失败，请查看 logs 目录中的最新日志文件"
else
    echo "✅ 任务执行成功"
fi

# 计算并显示脚本执行时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo ""
echo "=== 脚本执行完成，总耗时: ${DURATION} 秒 ==="
echo ""

# 根据退出码显示不同信息
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✅ 任务执行成功"
else
    echo "❌ 任务执行失败，退出码: $EXIT_CODE"
    echo "💡 请查看上面的错误信息或检查 logs 目录中的日志文件"
fi

echo ""
read -p "按回车键退出..."

exit $EXIT_CODE
