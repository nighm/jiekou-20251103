import importlib.util
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple

# 统一质量检查脚本：依次执行各类工具，对于具备自动修复能力的工具，按照检查->修复->复检模式执行


class PhaseResult(NamedTuple):
    tool: str
    phase: str
    exit_code: int


def run_command(command: list[str]) -> int:
    """Execute command and return exit status, never stopping the pipeline."""
    print(f"[INFO] Running: {' '.join(command)}")
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print(f"[WARN] Command exited with status {result.returncode}, continuing...")
    return result.returncode


def execute_pipeline() -> list[PhaseResult]:
    """Run all quality tools and return phase results."""
    project_root = Path(__file__).resolve().parents[1]
    src_path = project_root / "src"
    tests_path = project_root / "tests"
    python_exec = sys.executable

    bandit_available = importlib.util.find_spec("bandit") is not None

    pipelines: list[tuple[str, Iterable[tuple[str, list[str]]]]] = [
        (
            "autoflake",
            [
                (
                    "initial-check",
                    [
                        python_exec,
                        "-m",
                        "autoflake",
                        "--check",
                        "--remove-unused-variables",
                        "--recursive",
                        str(src_path),
                        str(tests_path),
                    ],
                ),
                (
                    "auto-fix",
                    [
                        python_exec,
                        "-m",
                        "autoflake",
                        "--in-place",
                        "--remove-unused-variables",
                        "--recursive",
                        str(src_path),
                        str(tests_path),
                    ],
                ),
                (
                    "final-check",
                    [
                        python_exec,
                        "-m",
                        "autoflake",
                        "--check",
                        "--remove-unused-variables",
                        "--recursive",
                        str(src_path),
                        str(tests_path),
                    ],
                ),
            ],
        ),
        (
            "pycln",
            [
                (
                    "initial-check",
                    [
                        python_exec,
                        "-m",
                        "pycln",
                        "--check",
                        str(src_path),
                        str(tests_path),
                    ],
                ),
                (
                    "auto-fix",
                    [
                        python_exec,
                        "-m",
                        "pycln",
                        "--all",
                        str(src_path),
                        str(tests_path),
                    ],
                ),
                (
                    "final-check",
                    [
                        python_exec,
                        "-m",
                        "pycln",
                        "--check",
                        str(src_path),
                        str(tests_path),
                    ],
                ),
            ],
        ),
        (
            "ruff",
            [
                ("initial-check", [python_exec, "-m", "ruff", "check", str(src_path), str(tests_path)]),
                ("auto-fix", [python_exec, "-m", "ruff", "check", "--fix", str(src_path), str(tests_path)]),
                ("format", [python_exec, "-m", "ruff", "format", str(src_path), str(tests_path)]),
                ("final-check", [python_exec, "-m", "ruff", "check", str(src_path), str(tests_path)]),
            ],
        ),
        (
            "mypy",
            [
                ("type-check", [python_exec, "-m", "mypy", str(src_path)]),
            ],
        ),
        (
            "pytest-quality",
            [
                ("quality-suite", [python_exec, "-m", "pytest", "-m", "quality"]),
            ],
        ),
        (
            "pytest",
            [
                ("full-suite", [python_exec, "-m", "pytest"]),
            ],
        ),
        (
            "coverage",
            [
                ("erase", [python_exec, "-m", "coverage", "erase"]),
                ("run-pytest", [python_exec, "-m", "coverage", "run", "-m", "pytest"]),
                (
                    "report",
                    [python_exec, "-m", "coverage", "report", "--fail-under=0", "-m"],
                ),
            ],
        ),
        (
            "pip-audit",
            [
                ("dependency-audit", [python_exec, "-m", "pip_audit", "--progress-spinner", "off"]),
            ],
        ),
    ]

    if bandit_available:
        pipelines.append(
            (
                "bandit",
                [
                    (
                        "security-scan",
                        [
                            python_exec,
                            "-m",
                            "bandit",
                            "-c",
                            "pyproject.toml",
                            "-r",
                            str(src_path),
                        ],
                    ),
                ],
            )
        )
    else:
        print(
            "[INFO] bandit 未安装，已跳过安全扫描阶段。"
            " 请通过 `pip install .[security]` 或 `pip install .[dev]` 安装后再运行。"
        )

    results: list[PhaseResult] = []
    for tool, phases in pipelines:
        print(f"\n[INFO] === Processing {tool} ===")
        for phase_name, command in phases:
            exit_code = run_command(command)
            results.append(PhaseResult(tool=tool, phase=phase_name, exit_code=exit_code))

    return results


def summarize(results: list[PhaseResult]) -> None:
    """Print summary for all phases and highlight remaining issues."""
    print("\n[INFO] === Quality Pipeline Summary ===")
    grouped: dict[str, list[PhaseResult]] = {}
    for result in results:
        grouped.setdefault(result.tool, []).append(result)

    pending_tools: list[str] = []
    for tool, phases in grouped.items():
        status_line = "  " + tool + ":"
        for phase in phases:
            status_text = "ok" if phase.exit_code == 0 else f"fail({phase.exit_code})"
            status_line += f" {phase.phase}={status_text};"
        print(status_line)
        if any(phase.exit_code != 0 for phase in phases):
            pending_tools.append(tool)

    if pending_tools:
        pending_str = ", ".join(sorted(set(pending_tools)))
        print(f"[INFO] 自动修复和检查已完成，但以下工具仍有问题需要人工处理: {pending_str}")
    else:
        print("[INFO] 所有工具执行完毕，没有检测到剩余问题。")


def main() -> None:
    results = execute_pipeline()
    summarize(results)


if __name__ == "__main__":
    main()
