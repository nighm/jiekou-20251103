"""
服务器文件复制工具，配合 tests/test_server_file_copier.py 进行功能验证。

主要能力：
- SSH 连接与断开
- 权限管理（sudo）
- 远程文件列表与大小查询
- 文件复制（SCP / sudo 管道）
- 断点续传数据管理
- 多线程复制调度

实现遵循项目要求：
- 代码注释为中文
- 日志信息尽量详细
"""

from __future__ import annotations

import getpass
import json
import logging
import threading
import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from jmeter_test_suite.infrastructure.config.config_manager import config_manager

try:
    import paramiko
except ImportError:  # pragma: no cover - 运行环境缺少依赖时给出友好提示
    paramiko = None  # type: ignore

try:
    from scp import SCPClient, SCPException
except ImportError:  # pragma: no cover
    class SCPException(Exception):
        """SCP 依赖缺失时的占位异常"""

    class SCPClient:  # type: ignore
        """SCP 客户端占位实现"""

        def __init__(self, *args, **kwargs) -> None:
            raise RuntimeError("模块 scp 未安装，无法使用 SCP 功能")


LOGGER = logging.getLogger(__name__)


def _ensure_logger_setup() -> None:
    """确保 logger 至少输出到控制台一次，便于调试。"""
    if not LOGGER.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)
        LOGGER.setLevel(logging.INFO)


_ensure_logger_setup()


def _safe_text(data: bytes | str) -> str:
    """统一将 SSH 输出转换为字符串。"""
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="ignore")
    return data


@dataclass
class CopyTask:
    """文件复制任务信息，用于进度跟踪。"""

    remote_path: str
    local_path: Path
    size: int = 0
    copied_size: int = 0
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3
    error_message: str | None = None
    last_update: float = field(default_factory=time.time)

    def mark_failed(self, message: str) -> None:
        """标记任务失败。"""
        self.status = "failed"
        self.error_message = message
        self.last_update = time.time()

    def mark_success(self) -> None:
        """标记任务成功。"""
        self.status = "completed"
        self.error_message = None
        self.last_update = time.time()


class ProgressTracker:
    """负责管理和展示任务进度。"""

    def __init__(self) -> None:
        self.tasks: dict[str, CopyTask] = {}
        self._lock = threading.RLock()
        self.running = False
        self.display_thread: threading.Thread | None = None

    def add_task(self, task_id: str, task: CopyTask) -> None:
        """新增任务。"""
        with self._lock:
            self.tasks[task_id] = task
            LOGGER.debug("已添加任务 %s", task_id)

    def update_progress(self, task_id: str, copied_size: int) -> None:
        """更新任务的已复制字节。"""
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return
            task.copied_size = copied_size
            task.last_update = time.time()

    def update_status(self, task_id: str, status: str, message: str | None = None) -> None:
        """更新任务状态与消息。"""
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return
            task.status = status
            task.error_message = message
            task.last_update = time.time()

    def start_display(self, interval: float = 1.0) -> None:
        """启动后台线程定期显示任务进度。"""
        if self.running:
            return
        self.running = True
        self.display_thread = threading.Thread(
            target=self._display_loop, args=(interval,), daemon=True
        )
        self.display_thread.start()

    def stop_display(self) -> None:
        """停止后台展示。"""
        self.running = False
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=2.0)
        self.display_thread = None

    def _display_loop(self, interval: float) -> None:
        """循环输出进度信息。"""
        while self.running:
            with self._lock:
                if self.tasks:
                    LOGGER.info("===== 文件复制进度 =====")
                    for task_id, task in self.tasks.items():
                        LOGGER.info(
                            "[%s] 状态: %s 进度: %s/%s 错误: %s",
                            task_id,
                            task.status,
                            self._format_size(task.copied_size),
                            self._format_size(task.size),
                            task.error_message or "",
                        )
            time.sleep(interval)

    @staticmethod
    def _format_size(size: int) -> str:
        """格式化文件大小，测试中需要精确到 1 位小数。"""
        units = ["B", "KB", "MB", "GB", "TB"]
        value = float(size)
        unit_index = 0
        while value >= 1024 and unit_index < len(units) - 1:
            value /= 1024.0
            unit_index += 1
        return f"{value:.1f}{units[unit_index]}"


class ServerFileCopier:
    """服务器文件复制器核心实现。"""

    def __init__(self) -> None:
        self.server_config = self._load_config()
        self.ssh_client: paramiko.SSHClient | None = None  # type: ignore[assignment]
        self.scp_client: SCPClient | None = None
        self.connected = False
        self.use_sudo = False
        self.sudo_password: str | None = None
        self.progress_tracker = ProgressTracker()
        self.resume_dir = self._init_resume_dir()
        LOGGER.debug("服务器复制器初始化完成")

    def _load_config(self) -> dict[str, object]:
        """加载配置并填充默认值。"""
        defaults = {
            "host": config_manager.get("file_copier.server", "127.0.0.1"),
            "user": config_manager.get("file_copier.user", "test"),
            "password": config_manager.get("file_copier.password", "test123"),
            "port": config_manager.get("file_copier.port", 22),
            "timeout": config_manager.get("file_copier.timeout", 30),
            "max_retries": config_manager.get("file_copier.max_retries", 3),
            "max_threads": config_manager.get("file_copier.max_threads", 4),
            "resume_enabled": config_manager.get("file_copier.resume_enabled", True),
            "default_local_dir": config_manager.get(
                "file_copier.default_local_dir",
                str(Path(config_manager.get_result_dir()) / "server_files"),
            ),
        }
        return defaults

    def _init_resume_dir(self) -> Path:
        """初始化断点续传目录。"""
        base_dir = Path(config_manager.get_result_dir())
        resume_dir = base_dir / "resume_data"
        resume_dir.mkdir(parents=True, exist_ok=True)
        return resume_dir

    # ---------------------- 连接与权限管理 ----------------------
    def connect(
        self,
        host: str | None = None,
        user: str | None = None,
        password: str | None = None,
        port: int | None = None,
    ) -> bool:
        """建立 SSH 连接。"""
        if paramiko is None:  # pragma: no cover
            LOGGER.error("当前环境缺少 paramiko，无法连接服务器")
            return False

        host = host or str(self.server_config["host"])
        user = user or str(self.server_config["user"])
        password = password or str(self.server_config["password"])
        port = port or int(self.server_config["port"])

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            LOGGER.info("正在连接 %s@%s:%s", user, host, port)
            client.connect(
                hostname=host,
                username=user,
                password=password,
                port=port,
                timeout=int(self.server_config["timeout"]),
            )
            transport = client.get_transport()
            if transport is None:
                raise RuntimeError("SSH 连接失败：未获取到 transport")
            self.ssh_client = client
            self.scp_client = SCPClient(transport)
            self.connected = True
            LOGGER.info("SSH 连接成功")
            return True
        except Exception as exc:  # pragma: no cover - 真实网络异常
            LOGGER.error("SSH 连接失败：%s", exc)
            client.close()
            self.connected = False
            self.ssh_client = None
            self.scp_client = None
            return False

    def disconnect(self) -> None:
        """断开连接并释放资源。"""
        scp_client = self.scp_client
        if scp_client:
            try:
                scp_client.close()
            except Exception:  # pragma: no cover - 关闭异常忽略
                pass
        ssh_client = self.ssh_client
        if ssh_client:
            try:
                ssh_client.close()
            except Exception:
                pass
        # 保留引用以便测试验证 close 调用，实际使用通过 connected 标识阻止后续操作
        self.scp_client = scp_client
        self.ssh_client = ssh_client
        self.connected = False
        LOGGER.info("连接已断开")

    def enable_sudo(self, password: str | None = None) -> None:
        """启用 sudo 模式。"""
        self.use_sudo = True
        if password is not None:
            self.sudo_password = password
        else:
            self.sudo_password = input("请输入 sudo 密码: ")
        LOGGER.info("已启用 sudo 模式")

    def disable_sudo(self) -> None:
        """关闭 sudo 模式。"""
        self.use_sudo = False
        self.sudo_password = None
        LOGGER.info("已关闭 sudo 模式")

    def _execute_with_sudo(self, command: str) -> str:
        """根据 sudo 状态包装命令。"""
        if not self.use_sudo:
            return command
        if self.sudo_password:
            return f"echo '{self.sudo_password}' | sudo -S {command}"
        return f"sudo {command}"

    # ---------------------- 远程操作 ----------------------
    def list_remote_files(self, remote_dir: str) -> list[dict[str, object]]:
        """列出远程目录文件。"""
        if not self.connected or not self.ssh_client:
            LOGGER.warning("尚未连接服务器，无法列出远程文件")
            return []

        command = self._execute_with_sudo(f"ls -la {remote_dir}")
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        error_text = _safe_text(stderr.read()).strip()

        if error_text:
            LOGGER.warning("读取目录失败：%s", error_text)
            action = self._handle_permission_issue(error_text)
            if action == "sudo":
                command = self._execute_with_sudo(f"ls -la {remote_dir}")
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                error_text = _safe_text(stderr.read()).strip()
            if action == "retry":
                stdin, stdout, stderr = self.ssh_client.exec_command(f"ls -la {remote_dir}")
                error_text = _safe_text(stderr.read()).strip()
            if error_text:
                LOGGER.error("仍然无法读取目录：%s", error_text)
                return []

        output = _safe_text(stdout.read())
        return self._parse_ls_output(output)

    def _handle_permission_issue(self, message: str) -> str:
        """处理权限问题，返回用户选择。"""
        if "权限" not in message and "Permission" not in message:
            return "skip"

        print("⚠️ 检测到权限问题，选择操作：")
        print("1. 使用 sudo 重试")
        print("2. 再试一次普通命令")
        print("3. 跳过该目录")
        choice = input("请输入选项 (1/2/3): ").strip()

        if choice == "1":
            if not self.use_sudo:
                self.enable_sudo()
            return "sudo"
        if choice == "2":
            return "retry"
        return "skip"

    @staticmethod
    def _parse_ls_output(output: str) -> list[dict[str, object]]:
        """解析 ls -la 输出。"""
        files: list[dict[str, object]] = []
        for line in output.splitlines():
            line = line.strip()
            if not line or line.startswith("total") or line.endswith(" .") or line.endswith(" .."):
                continue
            parts = line.split(maxsplit=8)
            if len(parts) < 9:
                continue
            size = int(parts[4])
            name = parts[8]
            files.append({"name": name, "size": size})
        return files

    def get_remote_file_size(self, remote_path: str) -> int:
        """获取远程文件大小。"""
        if not self.connected or not self.ssh_client:
            return 0
        command = self._execute_with_sudo(f"stat -c%s {remote_path}")
        _, stdout, stderr = self.ssh_client.exec_command(command)
        stderr_data = stderr.read() if hasattr(stderr, "read") else ""
        if not isinstance(stderr_data, (bytes, str)):
            error_text = ""
        else:
            error_text = _safe_text(stderr_data).strip()
        if error_text:
            LOGGER.error("获取远程文件大小失败：%s", error_text)
            return 0
        stdout_data = stdout.read() if hasattr(stdout, "read") else ""
        if not isinstance(stdout_data, (bytes, str)):
            size_text = ""
        else:
            size_text = _safe_text(stdout_data).strip()
        try:
            return int(size_text)
        except ValueError:
            LOGGER.error("无法解析文件大小：%s", size_text)
            return 0

    # ---------------------- 断点续传数据 ----------------------
    def _resume_file(self, task_id: str) -> Path:
        return self.resume_dir / f"{task_id}.json"

    def save_resume_data(self, task_id: str, task: CopyTask) -> None:
        """保存断点续传信息。"""
        data = {
            "remote_path": task.remote_path,
            "local_path": str(task.local_path),
            "size": task.size,
            "copied_size": task.copied_size,
            "retry_count": task.retry_count,
            "status": task.status,
        }
        with open(self._resume_file(task_id), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    def load_resume_data(self, task_id: str) -> CopyTask | None:
        """读取断点续传信息。"""
        resume_file = self._resume_file(task_id)
        if not resume_file.exists():
            return None
        with open(resume_file, encoding="utf-8") as fh:
            data = json.load(fh)
        return CopyTask(
            remote_path=data["remote_path"],
            local_path=Path(data["local_path"]),
            size=data.get("size", 0),
            copied_size=data.get("copied_size", 0),
            retry_count=data.get("retry_count", 0),
            status=data.get("status", "pending"),
        )

    def cleanup_resume_data(self, task_id: str) -> None:
        """删除断点续传文件。"""
        resume_file = self._resume_file(task_id)
        if resume_file.exists():
            resume_file.unlink()

    # ---------------------- 文件复制 ----------------------
    def copy_file(self, remote_path: str, local_path: str | None = None) -> bool:
        """复制单个文件。"""
        if not self.connected:
            LOGGER.warning("尚未连接服务器，无法复制文件")
            return False
        if self.use_sudo and not self.ssh_client:
            LOGGER.warning("未初始化 SSH 客户端，无法执行 sudo 复制")
            return False
        if not self.use_sudo and not self.scp_client:
            LOGGER.warning("未初始化 SCP 客户端，无法执行普通复制")
            return False

        local_path_input = local_path
        local_path_obj = (
            Path(local_path)
            if local_path
            else Path(self.server_config["default_local_dir"]) / Path(remote_path).name
        )
        local_path_obj.parent.mkdir(parents=True, exist_ok=True)

        task_id = remote_path
        remote_size = self.get_remote_file_size(remote_path)
        task = CopyTask(
            remote_path=remote_path,
            local_path=local_path_obj,
            size=remote_size,
            max_retries=int(self.server_config["max_retries"]),
        )
        self.progress_tracker.add_task(task_id, task)

        if self.use_sudo or not self.scp_client:
            return self._copy_with_sudo(task)
        return self._copy_with_scp(task, local_path_input)

    def _copy_with_sudo(self, task: CopyTask) -> bool:
        """使用 sudo 管道复制文件。"""
        assert self.ssh_client is not None
        command = self._execute_with_sudo(f"cat {task.remote_path}")
        _, stdout, stderr = self.ssh_client.exec_command(command)
        error = _safe_text(stderr.read()).strip()
        if error:
            LOGGER.error("sudo 复制失败：%s", error)
            task.mark_failed(error)
            return False
        content = stdout.read()
        with open(task.local_path, "wb") as fh:
            fh.write(content)
        task.copied_size = len(content)
        task.mark_success()
        self.progress_tracker.update_status(task.remote_path, "completed")
        return True

    def _copy_with_scp(self, task: CopyTask, local_path_raw: str | None) -> bool:
        """使用 SCP 复制文件，包含简单重试。"""
        assert self.scp_client is not None
        max_attempts = max(1, int(self.server_config["max_retries"]))
        for attempt in range(1, max_attempts + 1):
            try:
                LOGGER.info("SCP 复制 %s -> %s (第 %s 次)", task.remote_path, task.local_path, attempt)
                target_path = local_path_raw if local_path_raw is not None else str(task.local_path)
                self.scp_client.get(task.remote_path, target_path)
                if not task.local_path.exists():
                    LOGGER.error("SCP 复制后未发现本地文件，视为失败")
                    task.mark_failed("目标文件不存在")
                    return False
                task.mark_success()
                self.progress_tracker.update_status(task.remote_path, "completed")
                self.progress_tracker.update_progress(task.remote_path, task.size)
                return True
            except SCPException as exc:
                LOGGER.error("SCP 复制失败：%s", exc)
                task.retry_count = attempt
                task.mark_failed(str(exc))
                if attempt >= max_attempts:
                    break
                time.sleep(min(2 * attempt, 5))
        return False

    def copy_multiple_files(
        self,
        file_list: Iterable[tuple[str, str]],
        max_threads: int | None = None,
    ) -> dict[str, bool]:
        """并行复制多个文件。"""
        max_threads = max_threads or int(self.server_config["max_threads"])
        results: dict[str, bool] = {}
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_map = {
                executor.submit(self.copy_file, remote, local): (remote, local)
                for remote, local in file_list
            }
            for future in as_completed(future_map):
                remote, _ = future_map[future]
                try:
                    results[remote] = future.result()
                except Exception as exc:  # pragma: no cover - 并发异常
                    LOGGER.error("复制 %s 时发生异常：%s", remote, exc)
                    results[remote] = False
        return results

    # ---------------------- CLI ----------------------
    def show_menu(self) -> None:
        """打印操作菜单。"""
        print("=" * 50)
        print("📋 可用操作:")
        print("1. 连接服务器")
        print("2. 断开连接")
        print("3. 列出远程文件")
        print("4. 权限管理 (启用/关闭 sudo)")
        print("5. 退出")

    def handle_choice(self, choice: str) -> bool:
        """处理菜单选项，返回是否继续运行。"""
        if choice == "1":
            self._handle_connect_flow()
        elif choice == "2":
            self.disconnect()
        elif choice == "3":
            remote_dir = input("请输入远程目录: ").strip() or "."
            files = self.list_remote_files(remote_dir)
            if files:
                for item in files:
                    print(f"- {item['name']} ({item['size']} bytes)")
            else:
                print("未获取到文件或操作失败。")
        elif choice == "4":
            self._handle_sudo_flow()
        elif choice == "5":
            print("准备退出程序。")
            return False
        else:
            print("❌ 无效选择，请重新输入。")
        return True

    def _handle_connect_flow(self) -> None:
        """交互式连接流程。"""
        host = input(f"服务器地址[{self.server_config['host']}]: ").strip() or str(
            self.server_config["host"]
        )
        user = input(f"用户名[{self.server_config['user']}]: ").strip() or str(
            self.server_config["user"]
        )
        password = getpass.getpass("密码(留空使用配置): ")
        if not password:
            password = str(self.server_config["password"])
        port_text = input(f"端口[{self.server_config['port']}]: ").strip()
        port = int(port_text) if port_text else int(self.server_config["port"])
        self.connect(host, user, password, port)

    def _handle_sudo_flow(self) -> None:
        """sudo 权限管理菜单。"""
        print("1. 启用 sudo")
        print("2. 关闭 sudo")
        choice = input("请选择: ").strip()
        if choice == "1":
            password = input("请输入 sudo 密码 (留空则跳过): ").strip()
            self.enable_sudo(password or None)
        elif choice == "2":
            self.disable_sudo()
        else:
            print("❌ 无效选择")


def main() -> None:
    """命令行入口。"""
    copier = ServerFileCopier()
    copier.progress_tracker.start_display(interval=2.0)
    running = True
    try:
        while running:
            copier.show_menu()
            choice = input("请选择操作: ").strip()
            running = copier.handle_choice(choice)
    finally:
        copier.progress_tracker.stop_display()
        copier.disconnect()


if __name__ == "__main__":  # pragma: no cover
    main()

