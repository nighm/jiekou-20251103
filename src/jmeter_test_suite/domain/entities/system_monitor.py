"""TODO: add documentation."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from jmeter_test_suite.infrastructure.config import config_manager


@dataclass
class SystemMonitor:
    """TODO: add documentation."""

    server: str
    user: str
    password: str
    port: int = 22  # SSH端口，默认22
    duration: int | None = None
    output_dir: str | None = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # 测试Args（用于文件名标识）
    threads: int | None = None
    loops: int | None = None
    interface_name: str | None = None  # 接口名称，用于nmon文件命名

    # Execute状态
    status: str = "pending"  # pending, connecting, monitoring, completed, failed
    start_time: datetime | None = None
    end_time: datetime | None = None

    # 输出文件
    nmon_file: str | None = None
    remote_nmon_file: str | None = None

    # 系统数据
    cpu_usage_avg: float | None = None
    memory_usage_avg: float | None = None
    disk_io_avg: float | None = None
    network_io_avg: float | None = None

    def is_completed(self) -> bool:
        """TODO: add documentation."""
        return self.status == "completed"

    def is_failed(self) -> bool:
        """TODO: add documentation."""
        return self.status == "failed"

    def is_monitoring(self) -> bool:
        """TODO: add documentation."""
        return self.status == "monitoring"

    def get_duration(self) -> float | None:
        """TODO: add documentation."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __post_init__(self) -> None:
        """TODO: add documentation."""
        self.duration = None  # 强制设置为None，表示无限运行
        if self.output_dir is None:
            self.output_dir = config_manager.get_result_dir()

    # set_dynamic_duration方法已删除 - nmonrun indefinitely，不需要动态调整时长
