"""TODO: add documentation."""

import os
import posixpath
import shlex
import shutil
import threading
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from jmeter_test_suite.domain.entities.system_monitor import SystemMonitor
from jmeter_test_suite.domain.services.jmeter_service import JMeterService
from jmeter_test_suite.domain.services.nmon_service import NmonService
from jmeter_test_suite.infrastructure.adapters.ssh_adapter import SSHAdapter
from jmeter_test_suite.infrastructure.config import config_manager

HandleTestCommandFunc = Callable[[list[str]], int]
CLIHandleType = HandleTestCommandFunc | None
try:
    from jmeter_test_suite.interfaces.cli.main import (
        handle_test_command as _imported_cli_handle_test_command,
    )

    _CLI_HANDLE_TEST_COMMAND: CLIHandleType = _imported_cli_handle_test_command
except Exception:  # pragma: no cover - 避免导入时循环依赖导致的异常
    _CLI_HANDLE_TEST_COMMAND = None

# 供测试 patch 使用的模块级符号
handle_test_command: HandleTestCommandFunc | None = _CLI_HANDLE_TEST_COMMAND
CLI_HANDLE_TEST_COMMAND: CLIHandleType = _CLI_HANDLE_TEST_COMMAND


class SyncExecutionService:
    """TODO: add documentation."""

    def __init__(self, jmeter_command: str | None = None):
        """TODO: add documentation."""
        self.jmeter_service = JMeterService(jmeter_command)
        self.nmon_service = NmonService()

    def _archive_old_results(self, output_dir: str) -> None:
        """TODO: add documentation."""
        try:
            # Createold目录
            old_dir = os.path.join(output_dir, "old")
            os.makedirs(old_dir, exist_ok=True)

            # Getresult目录中的所有文件（排除old目录本身）
            files_to_move = []
            if os.path.exists(output_dir):
                for item in os.listdir(output_dir):
                    item_path = os.path.join(output_dir, item)
                    # 只Move文件，不Move目录（排除old目录）
                    if os.path.isfile(item_path) and item != "old":
                        files_to_move.append(item)

            if files_to_move:
                print(f"📦 归档 {len(files_to_move)} 个旧文件到 old/ 目录...")

                # Move文件到old目录
                for filename in files_to_move:
                    src_path = os.path.join(output_dir, filename)
                    dst_path = os.path.join(old_dir, filename)

                    # 如果目标文件已存在，先删除再移动（避免覆盖错误）
                    if os.path.exists(dst_path):
                        os.remove(dst_path)
                    shutil.move(src_path, dst_path)

                print(f"✅ 已归档 {len(files_to_move)} 个文件到 old/ 目录")
            else:
                print("📁 result目录为空，无需归档")

        except Exception as e:
            print(f"⚠️ 归档文件时出错: {str(e)}")
            import traceback

            traceback.print_exc()
            # Archive失败不应该影响测试Execute

    def execute_batch_sync_test(
        self,
        jmx_file: str,
        server: str,
        user: str,
        password: str,
        output_dir: str | None = None,
    ) -> dict[str, Any]:
        """TODO: add documentation."""
        # use配置default value
        if output_dir is None:
            output_dir = config_manager.get_result_dir()

        # 在开始测试前Archive旧文件
        self._archive_old_results(output_dir)

        print(f"🚀 开始批量测试: JMX={jmx_file}")
        print(f"🔍 nmon: 服务器={server}, 用户={user}")
        print(f"📁 输出目录: {output_dir}")

        # 用于存储Execute结果
        jmeter_result: dict[str, Any] = {"success": False}
        nmon_result: dict[str, Any] = {"success": False}

        # 生成统一的会话ID
        session_id = str(uuid.uuid4())[:8]
        print(f"测试会话ID: {session_id}")

        # 用于存储JMeterExecute时长和状态，供nmonuse
        jmeter_duration = None
        jmeter_completed = False

        # 定义JMeterExecute线程（调用testcommand）
        def execute_jmeter() -> None:
            nonlocal jmeter_result, jmeter_duration, jmeter_completed
            try:
                print("⏳ 开始执行JMeter测试（调用test命令）...")

                global handle_test_command
                command = handle_test_command
                if command is None:
                    from jmeter_test_suite.interfaces.cli.main import (
                        handle_test_command as imported_handle_test_command,
                    )

                    command = imported_handle_test_command
                    handle_test_command = command
                start_time = datetime.now()

                # 调用testcommand（不传递任何Args，use配置default value）
                test_exit_code = command([])

                end_time = datetime.now()
                jmeter_duration = (end_time - start_time).total_seconds()

                if test_exit_code == 0:
                    jmeter_result = {
                        "success": True,
                        "message": "testcommandExecute成功",
                    }
                    print(f"✅ JMeter测试执行成功，总时长: {jmeter_duration:.2f}秒")
                else:
                    jmeter_result = {
                        "success": False,
                        "message": "testcommandExecute失败",
                    }
                    print("❌ JMeter测试执行失败")

                # 标记JMeter已完成
                jmeter_completed = True

            except Exception as e:
                print(f"JMeter执行异常: {str(e)}")
                jmeter_result = {"success": False, "error": str(e)}
                jmeter_completed = True

        # 定义全局nmon监控线程
        def execute_global_nmon() -> None:
            nonlocal nmon_result
            try:
                print("⏳ 开始全局nmon监控...")

                # nmonrun indefinitely，覆盖整个JMeterExecute周期
                # 不再Set时长限制，让nmon持续监控直到JMeter完成

                # 从JMXfile path提取接口名称
                interface_name = "global"
                if jmx_file:
                    jmx_filename = os.path.basename(jmx_file)
                    if "_" in jmx_filename:
                        parts = jmx_filename.split("_")
                        if len(parts) >= 2:
                            interface_name = f"{parts[0]}_{parts[1]}"

                # Create全局系统监控对象（run indefinitely）
                system_monitor = SystemMonitor(
                    server=server,
                    user=user,
                    password=password,
                    duration=None,  # run indefinitely，不Set时长限制
                    output_dir=output_dir,
                    session_id=session_id,
                    threads=None,  # 全局监控，不指定具体线程数
                    loops=None,  # 全局监控，不指定具体循环数
                    interface_name=interface_name,  # Set接口名称
                )

                # 立即开始nmon监控
                print("🚀 立即开始nmon监控，覆盖整个JMeter执行周期...")
                self.nmon_service.execute_monitoring_with_entity(system_monitor)

                # WaitJMeter完成
                wait_count = 0
                while not jmeter_completed and wait_count < 3600:  # 最多Wait60分钟
                    time.sleep(1)
                    wait_count += 1

                if jmeter_duration is not None:
                    print(f"🚀 JMeter执行完成，实际执行时长: {jmeter_duration:.2f}秒")
                    print("📋 最后一个JTL文件已生成，等待5秒后停止nmon...")

                    # Wait5秒Ensurenmon收集到足够的后续数据
                    time.sleep(5)

                    # 手动Stop nmon monitoring（这是正确的逻辑）
                    ssh_adapter = self.nmon_service.ssh_adapter
                    if ssh_adapter:
                        print("🛑 停止nmon监控...")
                        ssh_adapter.stop_nmon_monitoring()

                        # Downloadnmon file
                        print("📥 下载nmon数据文件...")
                        download_success = ssh_adapter.download_nmon_file(
                            system_monitor
                        )
                        nmon_result = {"success": download_success}
                    else:
                        nmon_result = {"success": False, "error": "SSH Adapter不可用"}
                else:
                    nmon_result = {"success": False, "error": "JMeterExecute时长未知"}

            except Exception as e:
                print(f"全局nmon监控异常: {str(e)}")
                nmon_result = {"success": False, "error": str(e)}

        # 启动两个线程
        jmeter_thread = threading.Thread(target=execute_jmeter)
        nmon_thread = threading.Thread(target=execute_global_nmon)

        print("开始同步执行JMeter测试和全局nmon监控...")

        print("🔍 Capturing initial server log offsets...")
        try:
            log_offsets = self._capture_server_log_offsets()
            print(f"✅ Recorded offsets for {len(log_offsets)} server log files")
        except Exception as exc:  # pragma: no cover
            print(f"⚠️ 获取服务器日志偏移失败，已跳过：{exc}")
            log_offsets = {}

        # 同时启动两个线程
        jmeter_thread.start()
        nmon_thread.start()

        # Wait两个线程完成
        jmeter_thread.join()
        nmon_thread.join()

        # 拉取服务端日志
        print("📥 Fetching incremented server logs...")
        server_logs_result = self._fetch_server_logs(
            session_id, log_offsets, self.nmon_service.ssh_adapter
        )
        print("✅ Server log collection finished")

        # Check同步状态
        sync_status = (
            "success"
            if (jmeter_result["success"] and nmon_result["success"])
            else "partial_failed"
        )

        if not jmeter_result["success"] and not nmon_result["success"]:
            sync_status = "failed"

        # BuildReturns结果
        result = {
            "success": sync_status == "success",
            "sync_status": sync_status,
            "jmeter": jmeter_result,
            "nmon": nmon_result,
            "server_logs": server_logs_result,
            "total_duration": jmeter_duration,
            "status": "completed",
        }

        # 关闭SSH连接
        try:
            if self.nmon_service.ssh_adapter.ssh_client:
                self.nmon_service.ssh_adapter.disconnect()
                print("✅ SSH连接已关闭")
        except Exception as e:
            print(f"⚠️ 关闭SSH连接时出错: {str(e)}")

        print(f"同步执行完成，状态: {sync_status}")
        return result

    def _capture_server_log_offsets(self) -> dict[str, int]:
        """TODO: add documentation."""
        config = config_manager.get_server_logs_config() or {}
        if not config.get("enabled", False):
            return {}

        host = config.get("host") or config.get("server")
        username = config.get("username") or config.get("user")
        password = config.get("password")
        port = config.get("port", 22)
        base_path = config.get("base_path")
        files = config.get("files", [])

        if not host or not username or not password or not base_path or not files:
            raise RuntimeError(
                "Server log configuration is incomplete; cannot capture offsets"
            )

        adapter = SSHAdapter()
        if not adapter.connect(host, port, username, password):
            raise RuntimeError("Unable to connect to server when capturing log offsets")

        offsets: dict[str, int] = {}
        try:
            for file_name in files:
                remote_path = posixpath.join(base_path, file_name)
                stat = adapter.stat_file(remote_path)
                if stat is not None:
                    offsets[file_name] = stat.st_size
                    print(
                        f"   • {remote_path}: size={stat.st_size} bytes (direct access)"
                    )
                    continue

                exit_code, stdout_text, stderr_text = adapter.run_command(
                    f"stat -c %s {shlex.quote(remote_path)}",
                    use_sudo=True,
                )
                if exit_code != 0:
                    raise RuntimeError(
                        f"Unable to stat {remote_path}: {stderr_text.strip()}"
                    )
                size = int(stdout_text.strip() or 0)
                offsets[file_name] = size
                print(f"   • {remote_path}: size={size} bytes (sudo stat)")
        finally:
            adapter.disconnect()

        return offsets

    def _fetch_server_logs(
        self,
        session_id: str,
        offsets: dict[str, int],
        shared_adapter: SSHAdapter | None = None,
    ) -> dict[str, Any]:
        """TODO: add documentation."""

        config = config_manager.get_server_logs_config() or {}
        if not config.get("enabled", False):
            return {"enabled": False, "status": "skipped"}

        host = config.get("host") or config.get("server")
        username = config.get("username") or config.get("user")
        password = config.get("password")
        port = config.get("port", 22)
        base_path = config.get("base_path")
        local_prefix = config.get("local_prefix", "server")
        files = config.get("files", [])
        include_timestamp = config.get("include_timestamp", True)

        result_dir = Path(config_manager.get_result_dir())
        if not result_dir.is_absolute():
            project_root_path = Path(__file__).resolve().parents[4]
            result_dir = (project_root_path / result_dir).resolve()
        os.makedirs(result_dir, exist_ok=True)

        summary: dict[str, Any] = {
            "enabled": True,
            "status": "processing",
            "downloaded": [],
            "skipped": [],
            "errors": [],
        }

        if not host or not username or not password or not base_path or not files:
            summary["status"] = "config_incomplete"
            summary["errors"].append("Server log configuration is incomplete")
            return summary

        adapter = (
            shared_adapter
            if (shared_adapter and shared_adapter.is_connected())
            else SSHAdapter()
        )
        need_disconnect = adapter is not shared_adapter

        if not adapter.is_connected():
            print("🔌 Connecting to server for log retrieval...")
            if not adapter.connect(host, port, username, password):
                summary["status"] = "connect_failed"
                summary["errors"].append("Failed to establish SSH connection")
                return summary

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        current_remote = ""
        try:
            for file_name in files:
                remote_path = posixpath.join(base_path, file_name)
                current_remote = remote_path

                file_stat = adapter.stat_file(remote_path)
                file_size = file_stat.st_size if file_stat is not None else None
                if file_stat is None:
                    print(f"⚠️ Direct access failed for {remote_path}; fallback to sudo")

                safe_name = file_name.replace("/", "_").replace("\\", "_")
                name_root, name_ext = os.path.splitext(safe_name)
                if not name_ext:
                    name_ext = ".log"

                local_name_parts = [local_prefix, name_root, session_id]
                if include_timestamp:
                    local_name_parts.append(timestamp)
                local_name = "_".join(filter(None, local_name_parts)) + name_ext

                local_path = result_dir / local_name
                start_offset = offsets.get(file_name, 0)

                if file_size is not None and file_size < start_offset:
                    # 日志被截断或轮转，回退到完整拉取
                    start_offset = 0

                if file_size is not None and file_size == start_offset:
                    local_path.write_text("", encoding="utf-8")
                    summary["downloaded"].append(str(local_path))
                    no_new_bytes_msg = (
                        f"📥 {remote_path}: no new bytes; "
                        f"created empty file at {local_path}"
                    )
                    print(no_new_bytes_msg)
                    continue

                if start_offset > 0:
                    start_byte = start_offset + 1
                    command = f"tail -c +{start_byte} {shlex.quote(remote_path)}"
                    exit_code, stdout_text, stderr_text = adapter.run_command(
                        command,
                        use_sudo=True,
                    )
                    if exit_code != 0:
                        error_detail = stderr_text.strip()
                        raise RuntimeError(
                            f"tail failed: {remote_path}, exit={exit_code}, "
                            f"stderr={error_detail}"
                        )
                    local_path.write_text(stdout_text, encoding="utf-8")
                    copied_bytes = len(stdout_text.encode("utf-8"))
                    print(
                        f"📥 {remote_path}: copied {copied_bytes} bytes "
                        f"(from offset {start_offset})"
                    )
                else:
                    adapter.sudo_stream_file(remote_path, str(local_path))
                    size_on_disk = (
                        local_path.stat().st_size if local_path.exists() else 0
                    )
                    print(f"📥 {remote_path}: copied full file ({size_on_disk} bytes)")

                summary["downloaded"].append(str(local_path))

        except Exception as exc:  # pylint: disable=broad-except
            error_msg = (
                f"Error while processing {current_remote or 'unknown file'}: {exc}"
            )
            summary["errors"].append(error_msg)
            raise RuntimeError(error_msg) from exc
        finally:
            if need_disconnect:
                adapter.disconnect()

        summary["status"] = "completed"

        return summary

    def get_sync_execution_summary(self, result: dict[str, Any]) -> str:
        """TODO: add documentation."""
        jmeter_success = result["jmeter"]["success"]
        nmon_success = result["nmon"]["success"]
        sync_status = result["sync_status"]

        summary = f"同步Execute结果: {sync_status}\n"
        summary += f"JMeter测试: {'成功' if jmeter_success else '失败'}\n"
        summary += f"nmon监控: {'成功' if nmon_success else '失败'}\n"

        if jmeter_success and "performance_data" in result["jmeter"]:
            perf = result["jmeter"]["performance_data"]
            summary += (
                "性能数据: "
                f"总样本={perf.get('total_samples', 0)}, "
                f"TPS={perf.get('tps', 0.0)}\n"
            )

        if nmon_success and "system_data" in result["nmon"]:
            sys_data = result["nmon"]["system_data"]
            summary += (
                "系统数据: "
                f"CPU={sys_data.get('cpu_usage_avg', 0.0)}%, "
                f"内存={sys_data.get('memory_usage_avg', 0.0)}%\n"
            )

        return summary

    def _parse_range(self, range_str: str) -> list[int]:
        """TODO: add documentation."""
        parts = list(map(int, range_str.split()))
        if len(parts) == 3:
            start, max_val, step = parts
            # 如果step is 0，且start等于max_val，只返回一个值
            if step == 0:
                if start != max_val:
                    print(f'⚠️ 范围配置 "{range_str}" 步长为0，已按单值 {start} 处理')
                return [start]
            # 生成从start开始，步长为step的序列，包含max_val
            result = []
            current = start
            while current <= max_val:
                result.append(current)
                current += step
            # 如果最后一个值加上步长后仍然在合理范围内，继续添加
            if result and result[-1] + step <= max_val + step:
                result.append(result[-1] + step)
            return result
        elif len(parts) == 1:
            return [parts[0]]
        else:
            raise ValueError(f"无效的范围字符串: {range_str}")
