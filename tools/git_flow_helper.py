#!/usr/bin/env python3
"""Git 操作自动化脚本"""

import argparse
import datetime
import re
import shlex
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 默认配置，保证脚本开箱即用
DEFAULT_CONFIG = {
    "remote": "origin,gitee",
    "auto_push": True,
    "allow_empty_commit": True,
    "auto_message_template": "release: v{version} automated iteration {timestamp}",
    "timestamp_format": "%Y%m%d-%H%M%S",
    "show_status": True,
    "version_management": {
        "enabled": False,
        "version_file": "src/jmeter_test_suite/_version.py",
        "readme_files": [],
        "start_version": "7.0.0",
        "increment": "patch",
    },
}


def load_config() -> dict:
    """加载配置，优先从 jmeter_config.yaml 读取，否则使用默认配置。"""
    try:
        # 尝试加载 jmeter_config.yaml
        config_path = Path(__file__).parent.parent / "src" / "jmeter_test_suite" / "infrastructure" / "config" / "jmeter_config.yaml"
        if config_path.exists():
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                if 'git' in config_data:
                    # 合并默认配置和自定义配置
                    config = DEFAULT_CONFIG.copy()
                    config.update(config_data['git'])
                    return config
    except Exception as e:
        print(f"加载配置文件时出错: {e}")
    
    # 如果加载失败或配置不存在，返回默认配置
    config = DEFAULT_CONFIG.copy()
    config["version_management"] = DEFAULT_CONFIG["version_management"].copy()
    return config


CommandType = str | Sequence[str]


def normalize_remotes(remote_value: str | Sequence[str] | None) -> list[str]:
    """将远程配置统一转换为远程名称列表"""

    if remote_value is None:
        return ["origin"]

    if isinstance(remote_value, str):
        parts = [part.strip() for part in remote_value.split(",")]
        return [part for part in parts if part]

    remotes: list[str] = []
    for item in remote_value:
        name = str(item).strip()
        if name:
            remotes.append(name)
    return remotes or ["origin"]


def _format_command(command: CommandType) -> str:
    """用于打印的命令字符串"""

    if isinstance(command, str):
        return command
    return " ".join(shlex.quote(str(part)) for part in command)


def get_existing_remotes() -> set[str]:
    """获取当前仓库已配置的远程名称集合。"""

    result = subprocess.run(
        ["git", "remote"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print("无法获取远程列表，请确认当前目录为Git仓库。", file=sys.stderr)
        return set()
    return {line.strip() for line in (result.stdout or "").splitlines() if line.strip()}


def run_command(command: CommandType, description: str, allow_error: bool = False) -> subprocess.CompletedProcess:
    """执行命令并输出调试信息"""

    # 打印统一格式的分隔符，方便阅读日志
    divider = "=" * 70
    print(f"\n{divider}")
    print(f"步骤: {description}")
    print(f"命令: {_format_command(command)}")
    print(divider)

    if isinstance(command, str):
        run_args = {
            "args": command,
            "shell": True,
        }
    else:
        run_args = {
            "args": list(command),
            "shell": False,
        }

    result = subprocess.run(
        **run_args,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore",
    )

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(f"错误输出: {result.stderr.strip()}")

    if result.returncode != 0 and not allow_error:
        print(f"命令执行失败，返回码: {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)

    return result


def resolve_commit_message(args: argparse.Namespace, config: dict, version: str | None) -> str:
    """确定提交信息"""

    if args.message:
        return args.message

    # 使用配置中的格式生成时间戳，保持提交信息可追溯
    timestamp = datetime.datetime.now().strftime(config["timestamp_format"])
    message = config["auto_message_template"].format(
        timestamp=timestamp,
        version=version or "unknown",
    )
    print(f"使用自动提交信息: {message}")
    return message


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""

    parser = argparse.ArgumentParser(description="自动化完成 git status/add/commit/push 流程")
    parser.add_argument("--message", "-m", help="自定义提交信息")
    parser.add_argument("--remote", help="指定推送的远程名称")
    parser.add_argument("--no-push", action="store_true", help="仅提交，不执行 push")
    parser.add_argument("--dry-run", action="store_true", help="仅打印命令流程，不实际提交或推送")
    parser.add_argument(
        "--allow-empty",
        dest="allow_empty",
        action="store_true",
        help="允许空提交 (覆盖配置)",
    )
    parser.add_argument(
        "--no-allow-empty",
        dest="allow_empty",
        action="store_false",
        help="禁止空提交 (覆盖配置)",
    )
    parser.set_defaults(allow_empty=None)
    return parser.parse_args()


def ensure_branch() -> str:
    """获取当前分支名称"""

    result = run_command("git rev-parse --abbrev-ref HEAD", "获取当前分支", allow_error=False)
    branch = (result.stdout or "").strip()
    if not branch:
        print("无法识别当前分支", file=sys.stderr)
        sys.exit(1)
    print(f"当前分支: {branch}")
    return branch


def parse_semver(value: str) -> tuple[int, int, int] | None:
    """解析语义化版本，无法解析时返回None"""

    match = re.search(r"(\d+)\.(\d+)\.(\d+)", value or "")
    if not match:
        return None
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def format_version_tuple(version: tuple[int, int, int]) -> str:
    """格式化版本号元组"""

    major, minor, patch = version
    return f"({major}, {minor}, {patch})"


def ensure_version_settings(settings: dict) -> dict:
    """确保版本管理配置完整"""

    defaults = DEFAULT_CONFIG["version_management"].copy()
    defaults.update(settings or {})
    return defaults


def load_current_version(version_file: Path) -> str | None:
    """读取版本文件中的当前版本"""

    if not version_file.exists():
        print(f"未找到版本文件: {version_file}")
        return None

    content = version_file.read_text(encoding="utf-8")
    match = re.search(r"__version__\s*=\s*version\s*=\s*'([^']+)'", content)
    if match:
        return match.group(1)
    return None


def determine_next_version(current: str | None, settings: dict) -> str:
    """根据配置决定下一个版本号"""

    start_version = settings.get("start_version", "7.0.0")
    increment = settings.get("increment", "patch")

    start_tuple = parse_semver(start_version)
    if not start_tuple:
        raise ValueError("start_version 配置无效，必须是形如 6.0.0 的格式")

    current_tuple = parse_semver(current or "")
    if current_tuple is None or current_tuple[0] < start_tuple[0]:
        print(f"当前版本 {current or '未知'} 小于起始版本，将重置为 {start_version}")
        return start_version

    major, minor, patch = current_tuple
    if increment == "minor":
        minor += 1
        patch = 0
    elif increment == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    print(f"版本将从 {current} 迭代到 {new_version}")
    return new_version


def write_version_file(version_file: Path, new_version: str) -> None:
    """写回版本文件"""

    content = version_file.read_text(encoding="utf-8")
    tuple_value = parse_semver(new_version)
    if not tuple_value:
        raise ValueError("无法解析新版本号")

    content = re.sub(
        r"__version__\s*=\s*version\s*=\s*'[^']+'",
        f"__version__ = version = '{new_version}'",
        content,
    )
    content = re.sub(
        r"__version_tuple__\s*=\s*version_tuple\s*=\s*\([^)]+\)",
        f"__version_tuple__ = version_tuple = {format_version_tuple(tuple_value)}",
        content,
    )
    content = re.sub(
        r"__commit_id__\s*=\s*commit_id\s*=\s*'[^']*'",
        "__commit_id__ = commit_id = 'auto'",
        content,
    )

    version_file.write_text(content, encoding="utf-8")
    print(f"已更新版本文件: {version_file}")


def update_readme_versions(files: list[Path], new_version: str) -> None:
    """统一更新 README 中的版本号"""

    pattern = re.compile(r"v\d+\.\d+(?:\.\d+)?")
    for file_path in files:
        if not file_path.exists():
            print(f"未找到README文件: {file_path}")
            continue

        content = file_path.read_text(encoding="utf-8")
        matches = sorted(set(pattern.findall(content)))
        if not matches:
            print(f"在 {file_path} 中未找到需要替换的版本号")
            continue

        print(f"在 {file_path} 中发现版本号 {matches}，将替换为 v{new_version}")
        content = pattern.sub(f"v{new_version}", content)
        file_path.write_text(content, encoding="utf-8")


def manage_version(config: dict, dry_run: bool) -> str | None:
    """执行版本管理逻辑"""

    settings = ensure_version_settings(config.get("version_management", {}))
    version_file = PROJECT_ROOT / settings.get("version_file", "src/jmeter_test_suite/_version.py")
    readme_files = [PROJECT_ROOT / Path(item) for item in settings.get("readme_files", [])]

    if not settings.get("enabled", False):
        print("版本管理已禁用，跳过版本处理")
        return load_current_version(version_file)

    current_version = load_current_version(version_file)
    new_version = determine_next_version(current_version, settings)

    if current_version == new_version:
        print(f"版本号保持不变: {new_version}")
    elif dry_run:
        print(f"干运行模式：将版本从 {current_version} 迭代为 {new_version}（不写入文件）")
    else:
        write_version_file(version_file, new_version)
        update_readme_versions(readme_files, new_version)

    return new_version


def ensure_remote_configured(remote: str, config: dict) -> bool:
    """确保远程仓库已配置，如果不存在则自动配置"""
    
    existing_remotes = get_existing_remotes()
    if remote in existing_remotes:
        return True
    
    # 从配置中获取URL
    remotes_config = config.get("remotes", {})
    if remote not in remotes_config:
        print(f"警告: 配置文件中未找到远程 '{remote}' 的URL配置")
        return False
    
    remote_url = remotes_config[remote].get("url")
    if not remote_url:
        print(f"警告: 远程 '{remote}' 的URL配置为空")
        return False
    
    # 自动配置远程（使用不带Token的URL）
    try:
        # 确保URL中没有Token
        if "@" in remote_url and "://" in remote_url:
            # 移除URL中的认证信息（如果有）
            protocol_part = remote_url.split("://")[0] + "://"
            domain_part = remote_url.split("@")[-1] if "@" in remote_url else remote_url.split("://")[1]
            clean_url = protocol_part + domain_part
            remote_url = clean_url
        
        subprocess.check_call(["git", "remote", "add", remote, remote_url])
        print(f"✅ 已自动配置远程 '{remote}': {remote_url}")
        return True
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e):
            # 远程已存在，继续使用
            return True
        print(f"⚠️ 配置远程 '{remote}' 失败: {e}")
        return False


def auto_sync_and_push(remote: str, branch: str) -> None:
    """推送逻辑，必要时自动拉取并重试"""
    
    print(f"尝试推送到远程仓库 {remote}/{branch}...")
    
    # 加载配置
    config = load_config()
    
    # 确保远程已配置
    if not ensure_remote_configured(remote, config):
        print(f"⚠️ 跳过推送: {remote}（配置失败）")
        return
    
    # 获取远程URL（仅用于显示，不修改）
    try:
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", remote], 
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
        # 隐藏URL中的认证信息，避免泄露
        if "@" in remote_url:
            safe_url = remote_url.split("@")[-1] if "@" in remote_url else remote_url
            print(f"远程仓库: {safe_url}")
        else:
            print(f"远程仓库: {remote_url}")
    except Exception as e:
        print(f"获取远程URL失败: {e}")
    
    # 配置Git凭据存储（自动保存用户名密码，避免重复输入）
    # 这是Git的标准功能，用于存储认证信息
    try:
        # 只在需要时配置（不强制覆盖用户已有配置）
        current_helper = subprocess.run(
            ["git", "config", "--global", "credential.helper"],
            capture_output=True,
            text=True
        )
        if current_helper.returncode != 0:
            # 用户未配置，使用store方式（存储到文件）
            subprocess.check_call(["git", "config", "--global", "credential.helper", "store"])
            print("💡 已启用Git凭据存储（首次推送时会提示输入用户名密码，之后自动保存）")
        else:
            print(f"✅ 已使用Git凭据管理器: {current_helper.stdout.strip()}")
    except Exception as e:
        print(f"⚠️ 配置Git凭据存储失败: {e}")
        print("提示: 您可能需要手动输入Git用户名和密码")
    
    push_cmd = ["git", "push", remote, branch]
    print(f"执行命令: {' '.join(push_cmd)}")
    try:
        # 直接使用subprocess运行命令，以便更好地控制输出
        push_result = subprocess.run(
            push_cmd,
            capture_output=True,
            text=True,
            check=False
        )
        print(push_result.stdout)
        if push_result.stderr:
            print(push_result.stderr, file=sys.stderr)
    except Exception as e:
        print(f"执行推送命令时出错: {e}", file=sys.stderr)
        push_result = subprocess.CompletedProcess(
            push_cmd, 1, "", str(e)
        )

    if push_result.returncode == 0:
        print("推送完成。")
        return

    stderr = (push_result.stderr or "").lower()
    stdout = (push_result.stdout or "").lower()
    hint_non_ff = "non-fast-forward" in stderr or "non-fast-forward" in stdout
    hint_fetch_first = "fetch first" in stderr or "fetch first" in stdout
    hint_rejected = "failed to push some refs" in stderr or "failed to push some refs" in stdout
    hint_auth = "authentication failed" in stderr or "authentication failed" in stdout or "access denied" in stderr
    hint_credential = "credential" in stderr or "username" in stderr or "password" in stderr

    # 如果是认证问题，给出清晰提示
    if hint_auth or hint_credential:
        print("\n" + "="*70, file=sys.stderr)
        print("❌ 认证失败！需要配置Git凭据", file=sys.stderr)
        print("="*70, file=sys.stderr)
        print("\n💡 解决方案（任选一种）:", file=sys.stderr)
        print("\n1️⃣ 【推荐】使用SSH方式（无需每次输入密码）:", file=sys.stderr)
        print("   - 生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email@example.com\"", file=sys.stderr)
        print("   - 将公钥添加到Gitee/GitHub: cat ~/.ssh/id_ed25519.pub", file=sys.stderr)
        print("   - 修改远程URL为SSH: git remote set-url <remote> git@gitee.com:username/repo.git", file=sys.stderr)
        print("\n2️⃣ 使用HTTPS方式（首次推送时会提示输入用户名和Token）:", file=sys.stderr)
        print("   - Gitee: 用户名 = 你的用户名, 密码 = 你的个人访问令牌", file=sys.stderr)
        print("   - GitHub: 用户名 = 你的用户名, 密码 = Personal Access Token", file=sys.stderr)
        print("   - 首次输入后会保存，后续自动使用", file=sys.stderr)
        print("\n3️⃣ 手动配置凭据:", file=sys.stderr)
        print("   git config --global credential.helper store", file=sys.stderr)
        print("   然后在推送时输入用户名和Token", file=sys.stderr)
        print("="*70 + "\n", file=sys.stderr)
        sys.exit(push_result.returncode)

    if not (hint_non_ff or hint_fetch_first or hint_rejected):
        print("推送失败且不是远端领先导致，请检查输出手动处理。", file=sys.stderr)
        sys.exit(push_result.returncode)

    print("检测到远端存在更新，开始执行 fetch + pull --rebase。")
    fetch_result = run_command(f"git fetch {remote}", "获取远端更新", allow_error=True)
    if fetch_result.returncode != 0:
        print("fetch 执行失败，无法继续自动处理，请手动解决。", file=sys.stderr)
        sys.exit(fetch_result.returncode)

    pull_result = run_command(
        f"git pull --rebase {remote} {branch}",
        "拉取远端分支并执行 rebase",
        allow_error=True,
    )
    if pull_result.returncode != 0:
        print("rebase 过程中出现冲突或错误，请手动解决后再推送。", file=sys.stderr)
        sys.exit(pull_result.returncode)

    print("rebase 完成，准备重新推送。")
    retry_result = run_command(push_cmd, "推送到远程（重试）", allow_error=True)
    if retry_result.returncode != 0:
        print("重试推送依旧失败，请查看输出手动处理。", file=sys.stderr)
        sys.exit(retry_result.returncode)

    print("推送完成。")


def main() -> None:
    """脚本入口"""

    config = load_config()
    args = parse_arguments()

    # 根据参数与配置决定推送目标与是否允许空提交
    remote_values: list[str]
    if args.remote:
        remote_values = normalize_remotes(args.remote)
    else:
        # 优先使用 push_remotes，如果没有则使用 remote
        remote_values = normalize_remotes(config.get("push_remotes") or config.get("remote"))

    allow_empty = config["allow_empty_commit"] if args.allow_empty is None else args.allow_empty

    # 版本管理处理放在Git操作之前
    new_version = manage_version(config, args.dry_run)

    print("\n开始执行 Git 自动化流程")
    print(f"使用远程仓库: {', '.join(remote_values)}")
    print(f"允许空提交: {allow_empty}")
    print(f"自动推送: {not args.no_push and config['auto_push']}")
    print(f"仅演练模式: {args.dry_run}")

    if config.get("show_status", True):
        run_command("git status", "查看仓库状态", allow_error=False)

    if args.dry_run:
        print("干运行模式下不执行 add/commit/push，仅展示流程。")
        return

    run_command("git add .", "添加所有更改", allow_error=False)
    run_command("git status --short", "查看暂存区状态", allow_error=False)

    commit_message = resolve_commit_message(args, config, new_version)
    commit_cmd: list[str] = ["git", "commit", "-m", commit_message]
    if allow_empty:
        commit_cmd.append("--allow-empty")

    commit_result = run_command(commit_cmd, "提交更改", allow_error=True)

    if commit_result.returncode != 0:
        if "nothing to commit" in (commit_result.stderr or ""):
            print("没有可提交的内容，若要强制空提交请使用 --allow-empty。")
        else:
            print("提交失败，请检查以上输出。", file=sys.stderr)
            sys.exit(commit_result.returncode)
    else:
        print("提交完成。")

    if config.get("auto_push", True) and not args.no_push:
        branch = ensure_branch()
        # 自动配置远程（如果需要）
        for remote_name in remote_values:
            auto_sync_and_push(remote_name, branch)
    else:
        print("跳过推送步骤。")

    run_command("git status", "最终状态", allow_error=False)
    print("完成全部 Git 操作。")


if __name__ == "__main__":
    main()


