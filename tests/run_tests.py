"""TODO: add documentation."""

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_command(cmd: list[str], description: str) -> bool:
    """TODO: add documentation."""
    print(f"[RUN] {description}")
    print(f"命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"执行命令时出错: {exc}")
        return False

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    print(f"退出码: {result.returncode}")
    return result.returncode == 0


def _pytest_cmd(*extra: str) -> list[str]:
    return [sys.executable, "-m", "pytest", *extra]


def run_all_tests() -> bool:
    """TODO: add documentation."""
    cmd = _pytest_cmd(
        "tests/",
        "-v",
        "--tb=short",
        "--html=test_report.html",
        "--self-contained-html",
    )
    return run_command(cmd, "运行所有测试")


def run_unit_tests() -> bool:
    """TODO: add documentation."""
    cmd = _pytest_cmd("tests/unit/", "-v", "--tb=short", "-m", "unit")
    return run_command(cmd, "运行单元测试")


def run_integration_tests() -> bool:
    """TODO: add documentation."""
    cmd = _pytest_cmd("tests/integration/", "-v", "--tb=short", "-m", "integration")
    return run_command(cmd, "运行集成测试")


def run_all_command_tests() -> bool:
    """TODO: add documentation."""
    cmd = _pytest_cmd("tests/integration/test_all_command.py", "-v", "--tb=short")
    return run_command(cmd, "运行 all-command 测试")


def run_code_quality_tests() -> bool:
    """TODO: add documentation."""
    cmd = _pytest_cmd("tests/unit/test_code_quality.py", "-v", "--tb=short", "-s")
    return run_command(cmd, "运行代码质量检查")


def run_syntax_check() -> bool:
    """TODO: add documentation."""
    cmd = [sys.executable, "-m", "py_compile", "src"]
    return run_command(cmd, "运行语法检查")


def run_lint_check() -> bool:
    """TODO: add documentation."""
    try:
        subprocess.run(
            [sys.executable, "-m", "flake8", "--version"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ flake8未安装，跳过代码规范检查 (pip install flake8)")
        return True

    cmd = [
        sys.executable,
        "-m",
        "flake8",
        "src/",
        "--max-line-length=120",
        "--ignore=E501,W503",
    ]
    return run_command(cmd, "运行代码规范检查")


def run_type_check() -> bool:
    """TODO: add documentation."""
    try:
        subprocess.run(
            [sys.executable, "-m", "mypy", "--version"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ mypy未安装，跳过类型检查 (pip install mypy)")
        return True

    cmd = [
        sys.executable,
        "-m",
        "mypy",
        "src/",
        "--ignore-missing-imports",
        "--no-strict-optional",
    ]
    return run_command(cmd, "运行类型检查")


def run_coverage() -> bool:
    """TODO: add documentation."""
    try:
        subprocess.run(
            [sys.executable, "-m", "coverage", "--version"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ coverage未安装，跳过覆盖率检查 (pip install coverage)")
        return True

    coverage_run = [
        sys.executable,
        "-m",
        "coverage",
        "run",
        "-m",
        "pytest",
        "tests/",
    ]
    coverage_report = [sys.executable, "-m", "coverage", "report", "--show-missing"]
    coverage_html = [sys.executable, "-m", "coverage", "html"]
    success = run_command(coverage_run, "收集测试覆盖率")
    if success:
        success = run_command(coverage_report, "生成覆盖率报告") and run_command(
            coverage_html, "生成 HTML 覆盖率报告"
        )
    return success


def main() -> int:
    """TODO: add documentation."""
    parser = argparse.ArgumentParser(description="执行项目测试命令")

    parser.add_argument(
        "--type",
        choices=[
            "all",
            "unit",
            "integration",
            "all-command",
            "quality",
            "syntax",
            "lint",
            "type",
            "coverage",
        ],
        default="all",
        help="选择需要运行的测试类型",
    )
    parser.add_argument("--quick", action="store_true", help="暂未使用的占位参数")
    parser.add_argument("--report", action="store_true", help="测试完成后提示报告位置")

    args = parser.parse_args()

    print("🧪 JMeter 测试套件 - 运行器")
    print("=" * 50)

    runners = {
        "all": run_all_tests,
        "unit": run_unit_tests,
        "integration": run_integration_tests,
        "all-command": run_all_command_tests,
        "quality": run_code_quality_tests,
        "syntax": run_syntax_check,
        "lint": run_lint_check,
        "type": run_type_check,
        "coverage": run_coverage,
    }

    runner = runners.get(args.type, run_all_tests)
    success = runner()

    if args.report and success:
        print("\n📊 测试报告位置:")
        html_report = PROJECT_ROOT / "test_report.html"
        coverage_html = PROJECT_ROOT / "htmlcov" / "index.html"
        if html_report.exists():
            print(f"  - HTML报告: {html_report}")
        if coverage_html.exists():
            print(f"  - 覆盖率报告: {coverage_html}")

    print(f"\n{'✅ 测试完成' if success else '❌ 测试失败'}")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
