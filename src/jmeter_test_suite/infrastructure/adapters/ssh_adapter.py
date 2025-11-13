"""TODO: add documentation."""

import os
import shlex
from typing import Any

import paramiko

from jmeter_test_suite.domain.entities.system_monitor import SystemMonitor


class SSHAdapter:
    """TODO: add documentation."""

    def __init__(self) -> None:
        self.ssh_client: paramiko.SSHClient | None = None
        self.sftp_client: paramiko.SFTPClient | None = None
        self.connected = False
        self._password: str | None = None

    def connect(
        self, host: str, port: int, username: str, password: str, timeout: int = 30
    ) -> bool:
        """TODO: add documentation."""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self.ssh_client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
            )

            # CreateSFTP客户端
            self.sftp_client = self.ssh_client.open_sftp()
            self.connected = True
            self._password = password

            return True

        except Exception as e:
            print(f"❌ SSH连接失败: {str(e)}")
            self.connected = False
            self._password = None
            return False

    def disconnect(self) -> None:
        """TODO: add documentation."""
        try:
            if self.sftp_client:
                self.sftp_client.close()
                self.sftp_client = None

            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None

            self.connected = False
            self._password = None

        except Exception as e:
            print(f"⚠️ SSH断开连接时出错: {str(e)}")

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """TODO: add documentation."""
        if not self.connected or not self.sftp_client:
            print("❌ SSH未连接")
            return False

        try:
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_path)
            self._ensure_remote_directory(remote_dir)

            # Upload文件
            self.sftp_client.put(local_path, remote_path)
            return True

        except Exception as e:
            print(f"❌ 文件上传失败: {str(e)}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """TODO: add documentation."""
        if not self.connected or not self.sftp_client:
            print("❌ SSH未连接")
            return False

        try:
            # Ensure本地目录存在
            local_dir = os.path.dirname(local_path)
            os.makedirs(local_dir, exist_ok=True)

            # Download文件
            self.sftp_client.get(remote_path, local_path)
            return True

        except Exception as e:
            print(f"❌ 文件下载失败: {str(e)}")
            return False

    def stat_file(self, remote_path: str) -> paramiko.SFTPAttributes | None:
        """TODO: add documentation."""
        if not self.connected or not self.sftp_client:
            print("❌ SSH未连接")
            return None

        try:
            return self.sftp_client.stat(remote_path)
        except FileNotFoundError:
            print(f"⚠️ 远程文件不存在: {remote_path}")
            return None
        except Exception as e:  # pylint: disable=broad-except
            print(f"⚠️ 获取远程文件状态失败: {str(e)}")
            return None

    def execute_command(self, command: str) -> bool:
        """TODO: add documentation."""
        if not self.connected or not self.ssh_client:
            print("❌ SSH未连接")
            return False

        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

            # 实时Display输出
            def show_output() -> None:
                for line in iter(stdout.readline, ""):
                    print(f"[远程] {line.strip()}")

            import threading

            output_thread = threading.Thread(target=show_output)
            output_thread.daemon = True
            output_thread.start()

            # WaitcommandExecute完成
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                return True
            else:
                error_output = stderr.read().decode("utf-8")
                if error_output:
                    print(f"❌ 命令执行失败: {error_output}")
                return False

        except Exception as e:
            print(f"❌ 命令执行异常: {str(e)}")
            return False

    def run_command(
        self, command: str, use_sudo: bool = False, password: str | None = None
    ) -> tuple[int, str, str]:
        """TODO: add documentation."""
        if not self.connected or not self.ssh_client:
            raise RuntimeError("SSH未连接")

        password_value: str | None = None
        full_command = command
        if use_sudo:
            password_value = password or self._password
            if not password_value:
                raise ValueError("使用sudo需要提供密码")
            full_command = f"sudo -S -p '' {command}"

        stdin, stdout, stderr = self.ssh_client.exec_command(full_command)

        if use_sudo and password_value is not None:
            stdin.write(f"{password_value}\n")
            stdin.flush()

        exit_status = stdout.channel.recv_exit_status()
        stdout_text = stdout.read().decode("utf-8", errors="ignore")
        stderr_text = stderr.read().decode("utf-8", errors="ignore")

        return exit_status, stdout_text, stderr_text

    def sudo_stream_file(
        self, remote_path: str, local_path: str, password: str | None = None
    ) -> None:
        """TODO: add documentation."""
        if not self.connected or not self.ssh_client:
            raise RuntimeError("SSH未连接")

        password_value = password or self._password
        if not password_value:
            raise ValueError("使用sudo需要提供密码")

        command = f"sudo -S cat {shlex.quote(remote_path)}"
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        stdin.write(f"{password_value}\n")
        stdin.flush()

        with open(local_path, "wb") as output:
            while True:
                data = stdout.channel.recv(65536)
                if not data:
                    break
                output.write(data)

        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            err_text = stderr.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"sudo cat 失败 (exit {exit_status}): {err_text}")

    def _ensure_remote_directory(self, remote_dir: str) -> None:
        """TODO: add documentation."""
        if not self.connected or not self.ssh_client:
            return

        try:
            # TryCreate directory
            command = f'mkdir -p "{remote_dir}"'
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            stdout.channel.recv_exit_status()

        except Exception as e:
            print(f"⚠️ 创建远程目录失败: {str(e)}")

    def is_connected(self) -> bool:
        """TODO: add documentation."""
        return self.connected

    def start_nmon_monitoring(self, system_monitor: SystemMonitor) -> bool:
        """TODO: add documentation."""
        if not self.connected or not self.ssh_client:
            print("❌ SSH未连接")
            return False

        try:
            # Get服务器主机名用于文件名
            stdin, stdout, stderr = self.ssh_client.exec_command("hostname")
            hostname = stdout.read().decode().strip() or "localhost"

            # 生成唯一的nmon文件路径
            # 使用显式文件名，避免依赖目录扫描
            from datetime import datetime

            session_id = getattr(
                system_monitor, "session_id", None
            ) or datetime.now().strftime("%y%m%d_%H%M%S")
            nmon_filename = f"{hostname}_{session_id}.nmon"
            remote_path = f"/tmp/{nmon_filename}"
            output_dir = system_monitor.output_dir or ""
            if not output_dir:
                raise ValueError("SystemMonitor output_dir 未设置")
            local_path = os.path.join(output_dir, nmon_filename)

            # 在远程服务器上启动nmon监控（一直运行）并显式指定输出文件
            command = (
                "cd /tmp && nohup nmon -f -t -s 1 -c 999999 "
                f"-F '{remote_path}' > /dev/null 2>&1 &"
            )
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

            # Wait让nmonCreate文件并开始写入
            import time

            time.sleep(3)

            # Simple validation文件是否存在（non-mandatory）
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"[ -s '{remote_path}' ] || [ -f '{remote_path}' ]; echo $?"
            )
            stdout.read().decode().strip()
            # Even if not detected immediately，也先Set路径，后续停止/Download再验证
            system_monitor.nmon_file = local_path
            system_monitor.remote_nmon_file = remote_path

            print(f"🚀 nmon监控已启动: {remote_path}")
            print(f"📊 文件将保存到: {local_path}")

            return True

        except Exception as e:
            print(f"❌ 启动nmon监控失败: {str(e)}")
            return False

    def stop_nmon_monitoring(self) -> bool:
        """TODO: add documentation."""
        if not self.connected or not self.ssh_client:
            print("❌ SSH未连接")
            return False

        try:
            # Kill所有nmon进程
            command = "pkill -f 'nmon -f'"
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                print("✅ nmon监控已停止")
                return True
            else:
                # pkill可能Returns非0（not finding process is also normal）
                print("⚠️ 停止nmon监控（可能已经停止）")
                return True

        except Exception as e:
            print(f"⚠️ 停止nmon监控时出错: {str(e)}")
            return False

    def download_nmon_file(self, system_monitor: SystemMonitor) -> bool:
        """TODO: add documentation."""
        if not self.connected or not self.sftp_client:
            print("❌ SSH未连接")
            return False

        try:
            # 从system_monitorGet远程和本地路径
            remote_path = system_monitor.remote_nmon_file
            local_path = system_monitor.nmon_file

            if remote_path is None or local_path is None:
                print("❌ nmon文件路径未设置")
                return False

            # Download文件
            return self.download_file(remote_path, local_path)

        except Exception as e:
            print(f"❌ 下载nmon文件失败: {str(e)}")
            return False

    def __enter__(self) -> 'SSHAdapter':
        """TODO: add documentation."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """TODO: add documentation."""
        self.disconnect()
