"""TODO: add documentation."""

from abc import ABC, abstractmethod

from jmeter_test_suite.domain.entities.distributed_execution import (
    DistributedExecution,
    SlaveNode,
)


class DistributedService(ABC):
    """TODO: add documentation."""

    @abstractmethod
    def create_execution(
        self, jmx_file: str, total_threads: int, loops: int = 1, ramp_time: int = 60
    ) -> DistributedExecution:
        """TODO: add documentation."""

    @abstractmethod
    def add_slave_node(
        self,
        execution: DistributedExecution,
        name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        jmeter_path: str,
        thread_ratio: float = 0.5,
    ) -> SlaveNode:
        """TODO: add documentation."""

    @abstractmethod
    def validate_distributed_config(self, execution: DistributedExecution) -> bool:
        """TODO: add documentation."""

    @abstractmethod
    def calculate_thread_distribution(self, execution: DistributedExecution) -> None:
        """TODO: add documentation."""


class DefaultDistributedService(DistributedService):
    """TODO: add documentation."""

    def create_execution(
        self, jmx_file: str, total_threads: int, loops: int = 1, ramp_time: int = 60
    ) -> DistributedExecution:
        """TODO: add documentation."""
        return DistributedExecution(
            jmx_file=jmx_file,
            total_threads=total_threads,
            loops=loops,
            ramp_time=ramp_time,
        )

    def add_slave_node(
        self,
        execution: DistributedExecution,
        name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        jmeter_path: str,
        thread_ratio: float = 0.5,
    ) -> SlaveNode:
        """TODO: add documentation."""
        slave = SlaveNode(
            name=name,
            host=host,
            port=port,
            username=username,
            password=password,
            jmeter_path=jmeter_path,
            thread_ratio=thread_ratio,
        )
        execution.add_slave(slave)
        return slave

    def validate_distributed_config(self, execution: DistributedExecution) -> bool:
        """TODO: add documentation."""
        if execution.total_threads <= 0:
            return False

        if not execution.slaves:
            return False

        # 验证线程比例总和
        total_ratio = sum(slave.thread_ratio for slave in execution.slaves)
        return abs(total_ratio - 1.0) <= 0.01  # 允许0.01的误差

    def calculate_thread_distribution(self, execution: DistributedExecution) -> None:
        """TODO: add documentation."""
        if not execution.slaves:
            return

        # Ensure线程比例总和为1
        total_ratio = sum(slave.thread_ratio for slave in execution.slaves)
        if total_ratio != 1.0:
            # 重新分配，平均分配
            ratio_per_slave = 1.0 / len(execution.slaves)
            for slave in execution.slaves:
                slave.thread_ratio = ratio_per_slave

        # Calculate每个Slave的线程数
        for slave in execution.slaves:
            slave_threads = execution.calculate_slave_threads(slave)
            # Ensure至少分配1个线程
            if slave_threads < 1:
                slave.thread_ratio = 1.0 / max(1, len(execution.slaves))
