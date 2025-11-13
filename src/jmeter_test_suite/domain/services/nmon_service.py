"""TODO: add documentation."""

from datetime import datetime
from typing import Any

from jmeter_test_suite.domain.entities.system_monitor import SystemMonitor
from jmeter_test_suite.infrastructure.adapters.file_adapter import FileAdapter
from jmeter_test_suite.infrastructure.adapters.ssh_adapter import SSHAdapter
from jmeter_test_suite.infrastructure.config import config_manager


class NmonService:
    """TODO: add documentation."""

    def __init__(self) -> None:
        """TODO: add documentation."""
        self.file_adapter = FileAdapter()
        self.ssh_adapter = SSHAdapter()

    def execute_monitoring_with_entity(
        self, system_monitor: SystemMonitor
    ) -> SystemMonitor:
        """TODO: add documentation."""
        try:
            # 更新监控状态
            system_monitor.status = "connecting"
            system_monitor.start_time = datetime.now()

            # Create output directory
            output_dir = system_monitor.output_dir or config_manager.get_result_dir()
            system_monitor.output_dir = output_dir
            self.file_adapter.create_directory(output_dir)

            # 连接SSH服务器
            if not self.ssh_adapter.connect(
                system_monitor.server,
                system_monitor.port,
                system_monitor.user,
                system_monitor.password,
            ):
                system_monitor.status = "failed"
                system_monitor.end_time = datetime.now()
                print(f"SSH连接失败，会话ID: {system_monitor.session_id}")
                return system_monitor

            # Start nmon monitoring
            success = self.ssh_adapter.start_nmon_monitoring(system_monitor)

            if success:
                system_monitor.status = (
                    "monitoring"  # 改为monitoring状态，表示正在监控中
                )
                # 不Setend_time，因为监控还在进行中

                # 简化：不在这里Parse数据，留给Excel adapterHandle
                print(f"nmon文件路径: {system_monitor.nmon_file}")

                print(f"nmon监控执行成功，会话ID: {system_monitor.session_id}")
            else:
                system_monitor.status = "failed"
                system_monitor.end_time = datetime.now()
                print(f"nmon监控执行失败，会话ID: {system_monitor.session_id}")

        except Exception as e:
            system_monitor.status = "failed"
            system_monitor.end_time = datetime.now()
            print(f"nmon监控服务异常: {str(e)}")
        # 注意：不在这里关闭SSH连接
        # 因为同步执行服务仍需使用它终止nmon进程并下载文件

        return system_monitor

    def _update_system_data(
        self, system_monitor: SystemMonitor, system_data: dict[str, Any]
    ) -> None:
        """TODO: add documentation."""
        system_monitor.cpu_usage_avg = float(system_data.get("cpu_usage_avg", 0.0))
        system_monitor.memory_usage_avg = float(
            system_data.get("memory_usage_avg", 0.0)
        )
        system_monitor.disk_io_avg = float(system_data.get("disk_io_avg", 0.0))
        system_monitor.network_io_avg = float(system_data.get("network_io_avg", 0.0))

    def get_monitoring_result_summary(
        self, system_monitor: SystemMonitor
    ) -> dict[str, Any]:
        """TODO: add documentation."""
        return {
            "success": system_monitor.is_completed(),
            "server": system_monitor.server,
            "duration": system_monitor.duration,
            "nmon_file": system_monitor.nmon_file,
            "system_data": {
                "cpu_usage_avg": system_monitor.cpu_usage_avg,
                "memory_usage_avg": system_monitor.memory_usage_avg,
                "disk_io_avg": system_monitor.disk_io_avg,
                "network_io_avg": system_monitor.network_io_avg,
            },
            "status": system_monitor.status,
            "actual_duration": system_monitor.get_duration(),
        }
