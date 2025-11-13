"""Bulk upgrade helper for pip packages.

Only use this script inside a dedicated virtual environment. It upgrades
every outdated package reported by ``pip list --outdated``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    """执行命令并返回结果，失败时抛出异常"""

    print(f"🚀 Running: {' '.join(command)}")
    return subprocess.run(command, check=True, text=True, capture_output=True)


def fetch_outdated_packages() -> list[dict[str, str]]:
    """获取待升级的包列表（JSON 格式）"""

    result = run_command([
        sys.executable,
        "-m",
        "pip",
        "list",
        "--outdated",
        "--format",
        "json",
    ])
    packages = json.loads(result.stdout)
    packages.sort(key=lambda item: item["name"].lower())
    return packages


def upgrade_package(name: str) -> None:
    """升级单个包，打印实时输出"""

    print(f"📦 Upgrading: {name}")
    process = subprocess.Popen(
        [sys.executable, "-m", "pip", "install", "--upgrade", name],
        text=True,
    )
    process.communicate()
    if process.returncode == 0:
        print(f"✅ Completed: {name}\n")
    else:
        print(f"❌ Failed: {name} (exit code {process.returncode})\n")


def main() -> None:
    """主入口：升级所有包，允许 dry-run 和跳过列表"""

    dry_run = "--dry-run" in sys.argv
    skip_file = Path("tools/upgrade_skip.txt")
    skip: set[str] = set()
    if skip_file.exists():
        skip = {line.strip() for line in skip_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")}
        if skip:
            print(f"⚠️ Skip list loaded: {', '.join(sorted(skip))}")

    packages = fetch_outdated_packages()
    if not packages:
        print("🎉 所有软件包已经是最新版本")
        return

    print(f"📋 Total packages to update: {len(packages)}")
    if dry_run:
        for pkg in packages:
            if pkg["name"] in skip:
                continue
            print(f"- {pkg['name']}: {pkg['version']} -> {pkg['latest']}")
        print("ℹ️ Dry-run mode, no changes were made.")
        return

    for pkg in packages:
        name = pkg["name"]
        if name in skip:
            print(f"⏭️ Skip: {name}")
            continue
        upgrade_package(name)


if __name__ == "__main__":
    main()
