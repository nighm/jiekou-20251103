"""TODO: add documentation."""

import os
import threading
import time
from datetime import datetime

from jmeter_test_suite.domain.entities.distributed_execution import (
    DistributedExecution,
    SlaveNode,
    SlaveStatus,
)
from jmeter_test_suite.domain.services.distributed_service import (
    DefaultDistributedService,
)
from jmeter_test_suite.infrastructure.adapters.ssh_adapter import SSHAdapter
from jmeter_test_suite.infrastructure.config import config_manager


class DistributedExecutionService:
    """TODO: add documentation."""

    def __init__(self) -> None:
        self.distributed_service = DefaultDistributedService()
        self.ssh_adapter = SSHAdapter()

    def create_distributed_execution_from_config(
        self, jmx_file: str, total_threads: int, loops: int = 1, ramp_time: int = 60
    ) -> DistributedExecution:
        """TODO: add documentation."""
        execution = self.distributed_service.create_execution(
            jmx_file, total_threads, loops, ramp_time
        )

        # 从配置中GetSlave信息
        distributed_config = config_manager.get("distributed", {})
        slaves_config = distributed_config.get("slaves", [])

        if not slaves_config:
            raise ValueError("未找到分布式Slave配置")

        # use第一个Slave配置
        slave_config = slaves_config[0]

        # 添加Slave节点
        self.distributed_service.add_slave_node(
            execution,
            slave_config["name"],
            slave_config["host"],
            slave_config["port"],
            slave_config["username"],
            slave_config["password"],
            slave_config["jmeter_path"],
            slave_config.get("thread_ratio", 1.0),  # 默认100%线程分配
        )

        # 验证配置
        if not self.distributed_service.validate_distributed_config(execution):
            raise ValueError("分布式配置验证失败")

        # Calculate线程分配
        self.distributed_service.calculate_thread_distribution(execution)

        return execution

    def execute_distributed_test(self, execution: DistributedExecution) -> bool:
        """TODO: add documentation."""
        try:
            execution.status = "running"
            execution.start_time = datetime.now()

            print("🚀 开始分布式压测...")
            print(f"📊 总线程数: {execution.total_threads}")
            print(f"📊 循环次数: {execution.loops}")
            print(f"📊 Slave数量: {len(execution.slaves)}")

            # 连接所有Slave
            if not self._connect_all_slaves(execution):
                execution.status = "failed"
                return False

            # Execute分布式测试
            success = self._execute_remote_tests(execution)

            execution.end_time = datetime.now()
            execution.status = "completed" if success else "failed"

            return success

        except Exception as e:
            execution.status = "failed"
            execution.end_time = datetime.now()
            print(f"❌ 分布式压测异常: {str(e)}")
            return False

    def _connect_all_slaves(self, execution: DistributedExecution) -> bool:
        """TODO: add documentation."""

        for slave in execution.slaves:
            try:
                slave.status = SlaveStatus.CONNECTING
                print(f"🔗 连接 {slave.name} ({slave.host}:{slave.port})...")

                # useSSH Adapter连接（带重试机制）
                max_retries = 3
                retry_delay = 5  # 秒

                for attempt in range(max_retries):
                    print(f"🔗 尝试连接 {slave.name} (第{attempt + 1}次)...")

                    if self.ssh_adapter.connect(
                        slave.host, slave.port, slave.username, slave.password
                    ):
                        slave.status = SlaveStatus.CONNECTED
                        slave.connection_time = datetime.now()
                        print(f"✅ {slave.name} 连接成功")
                        break
                    else:
                        if attempt < max_retries - 1:
                            print(f"⏳ 连接失败，{retry_delay}秒后重试...")
                            time.sleep(retry_delay)
                        else:
                            slave.status = SlaveStatus.FAILED
                            slave.error_message = f"SSH连接失败，已重试{max_retries}次"
                            print(f"❌ {slave.name} 连接失败，已重试{max_retries}次")
                            return False

            except Exception as e:
                slave.status = SlaveStatus.FAILED
                slave.error_message = str(e)
                print(f"❌ {slave.name} 连接异常: {str(e)}")
                return False

        return True

    def _execute_remote_tests(self, execution: DistributedExecution) -> bool:
        """TODO: add documentation."""

        # Get测试Args
        thread_range = config_manager.get("thread_range", "100 600 200")
        loop_range = config_manager.get("loop_range", "30 110 30")
        config_manager.get_result_dir()

        # Parse线程和循环范围
        thread_values = self._parse_range(thread_range)
        loop_values = self._parse_range(loop_range)

        execution.total_tests = len(thread_values) * len(loop_values)
        execution.successful_tests = 0
        execution.failed_tests = 0

        # Execute分布式测试
        for threads in thread_values:
            for loops in loop_values:
                print(f"🔄 执行分布式测试: {threads}线程, {loops}循环")

                # 更新ExecuteArgs
                execution.total_threads = threads
                execution.loops = loops

                # 重新Calculate线程分配
                self.distributed_service.calculate_thread_distribution(execution)

                # Execute远程测试
                if self._execute_single_test_round(execution):
                    execution.successful_tests += 1
                    print(f"✅ 分布式测试成功: {threads}线程, {loops}循环")
                else:
                    execution.failed_tests += 1
                    print(f"❌ 分布式测试失败: {threads}线程, {loops}循环")

        # 关闭所有连接
        self._disconnect_all_slaves(execution)

        return execution.successful_tests > 0

    def _execute_single_test_round(self, execution: DistributedExecution) -> bool:
        """TODO: add documentation."""
        remote_threads: list[threading.Thread] = []
        remote_results: dict[str, str] = {}

        for slave in execution.slaves:

            def remote_test(slave_node: SlaveNode) -> None:
                try:
                    slave_node.status = SlaveStatus.EXECUTING
                    slave_node.execution_time = datetime.now()

                    # UploadJMX文件
                    remote_jmx_path = f"C:\\temp\\test_{int(time.time())}.jmx"
                    if not self.ssh_adapter.upload_file(
                        execution.jmx_file, remote_jmx_path
                    ):
                        slave_node.status = SlaveStatus.FAILED
                        slave_node.error_message = "JMX文件上传失败"
                        return

                    # Calculate该Slave的线程数
                    slave_threads = execution.calculate_slave_threads(slave_node)

                    # Execute远程压测
                    result_file = (
                        f"C:\\temp\\result_{slave_node.name}_{int(time.time())}.jtl"
                    )
                    cmd_parts = [
                        f'"{slave_node.jmeter_path}"',
                        "-n",
                        f'-t "{remote_jmx_path}"',
                        f'-l "{result_file}"',
                        f"-Jthread_count={slave_threads}",
                        f"-Jloop_count={execution.loops}",
                        f"-Jramp_time={execution.ramp_time}",
                    ]
                    cmd = " ".join(cmd_parts)

                    print(f"📡 在 {slave_node.name} 上执行: {cmd}")

                    if self.ssh_adapter.execute_command(cmd):
                        # Download结果文件
                        result_dir = config_manager.get_result_dir()
                        local_result = os.path.join(
                            result_dir,
                            f"{slave_node.name}_{execution.total_threads}t_{execution.loops}l_{int(time.time())}.jtl",
                        )

                        if self.ssh_adapter.download_file(result_file, local_result):
                            slave_node.result_file = result_file
                            slave_node.local_result_file = local_result
                            slave_node.status = SlaveStatus.COMPLETED
                            remote_results[slave_node.name] = local_result
                            success_msg = (
                                f"✅ {slave_node.name} 远程压测完成: "
                                f"{slave_threads}线程"
                            )
                            print(success_msg)
                        else:
                            slave_node.status = SlaveStatus.FAILED
                            slave_node.error_message = "结果文件下载失败"
                    else:
                        slave_node.status = SlaveStatus.FAILED
                        slave_node.error_message = "JMeter执行失败"

                except Exception as e:
                    slave_node.status = SlaveStatus.FAILED
                    slave_node.error_message = str(e)
                    print(f"❌ {slave_node.name} 远程压测异常: {str(e)}")

            thread = threading.Thread(target=remote_test, args=(slave,))
            thread.start()
            remote_threads.append(thread)

        # Wait远程压测完成
        for thread in remote_threads:
            thread.join()

        # Check结果
        success_count = sum(
            1 for slave in execution.slaves if slave.status == SlaveStatus.COMPLETED
        )
        return success_count > 0

    def _disconnect_all_slaves(self, execution: DistributedExecution) -> None:
        """TODO: add documentation."""
        for slave in execution.slaves:
            if slave.status == SlaveStatus.CONNECTED:
                self.ssh_adapter.disconnect()
                slave.status = SlaveStatus.PENDING
                print(f"🔌 断开 {slave.name} 连接")

    def _parse_range(self, range_str: str) -> list[int]:
        """TODO: add documentation."""
        try:
            parts = range_str.split()
            if len(parts) != 3:
                raise ValueError("范围格式错误")

            start, end, step = map(int, parts)
            if step == 0:
                if start != end:
                    print(f'⚠️ 范围配置 "{range_str}" 步长为0，已按单值 {start} 处理')
                return [start]
            return list(range(start, end + 1, step))
        except Exception as e:
            print(f"❌ 解析范围失败: {range_str} - {str(e)}")
            return [100]  # 默认值
