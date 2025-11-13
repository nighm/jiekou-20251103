"""TODO: add documentation."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DistributedMode(Enum):
    """TODO: add documentation."""

    SSH_REMOTE = "ssh_remote"


class SlaveStatus(Enum):
    """TODO: add documentation."""

    PENDING = "pending"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SlaveNode:
    """TODO: add documentation."""

    name: str
    host: str
    port: int
    username: str
    password: str
    jmeter_path: str
    thread_ratio: float = 0.5

    # 状态信息
    status: SlaveStatus = SlaveStatus.PENDING
    connection_time: datetime | None = None
    execution_time: datetime | None = None
    error_message: str | None = None

    # Execute结果
    result_file: str | None = None
    local_result_file: str | None = None


@dataclass
class DistributedExecution:
    """TODO: add documentation."""

    mode: DistributedMode = DistributedMode.SSH_REMOTE

    # 测试配置
    jmx_file: str = ""
    total_threads: int = 0
    loops: int = 1
    ramp_time: int = 60

    # Slave节点
    slaves: list[SlaveNode] = field(default_factory=list)

    # Execute状态
    status: str = "pending"  # pending, running, completed, failed
    start_time: datetime | None = None
    end_time: datetime | None = None

    # 结果统计
    total_tests: int = 0
    successful_tests: int = 0
    failed_tests: int = 0

    # 结果文件
    result_files: list[str] = field(default_factory=list)

    def add_slave(self, slave: SlaveNode) -> None:
        """TODO: add documentation."""
        self.slaves.append(slave)

    def get_slave_by_name(self, name: str) -> SlaveNode | None:
        """TODO: add documentation."""
        for slave in self.slaves:
            if slave.name == name:
                return slave
        return None

    def calculate_slave_threads(self, slave: SlaveNode) -> int:
        """TODO: add documentation."""
        if not self.total_threads:
            return 0
        ratio = max(slave.thread_ratio, 0)
        threads = int(self.total_threads * ratio)
        return max(1, threads) if threads else 0

    def is_completed(self) -> bool:
        """TODO: add documentation."""
        if self.status != "completed":
            return False
        return all(
            slave.status in {SlaveStatus.COMPLETED, SlaveStatus.FAILED}
            for slave in self.slaves
        )

    def is_successful(self) -> bool:
        """TODO: add documentation."""
        if not self.slaves:
            return False
        return all(slave.status == SlaveStatus.COMPLETED for slave in self.slaves)

    def get_success_rate(self) -> float:
        """TODO: add documentation."""
        if self.total_tests == 0:
            return 0.0
        return self.successful_tests / self.total_tests

    def get_duration(self) -> float | None:
        """TODO: add documentation."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
