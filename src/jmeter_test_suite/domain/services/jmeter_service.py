"""TODO: add documentation."""

from datetime import datetime
from typing import Any

from jmeter_test_suite.domain.entities.test_execution import TestExecution
from jmeter_test_suite.infrastructure.adapters.file_adapter import FileAdapter
from jmeter_test_suite.infrastructure.adapters.jmeter_adapter import JMeterAdapter
from jmeter_test_suite.infrastructure.config import config_manager


class JMeterService:
    """TODO: add documentation."""

    def __init__(self, jmeter_command: str | None = None):
        """TODO: add documentation."""
        self.jmeter_adapter = JMeterAdapter(jmeter_command)
        self.file_adapter = FileAdapter()

    def execute_test_with_entity(self, test_execution: TestExecution) -> TestExecution:
        """TODO: add documentation."""
        try:
            # 更新Execute状态
            test_execution.status = "running"
            test_execution.start_time = datetime.now()

            # ExecuteJMeter测试
            result = self.jmeter_adapter.execute_test(test_execution)

            if result:
                test_execution.status = "completed"
                test_execution.end_time = datetime.now()

                if test_execution.jtl_file is None:
                    raise ValueError("JTL 文件路径缺失")

                # ParseJTL文件Get性能数据
                performance_data = self.jmeter_adapter.parse_jtl_file(
                    test_execution.jtl_file, test_execution
                )

                # 更新性能数据
                self._update_performance_data(test_execution, performance_data)

                print(f"JMeter测试执行成功，会话ID: {test_execution.session_id}")
            else:
                test_execution.status = "failed"
                test_execution.end_time = datetime.now()
                print(f"JMeter测试执行失败，会话ID: {test_execution.session_id}")

        except Exception as e:
            test_execution.status = "failed"
            test_execution.end_time = datetime.now()
            print(f"JMeter测试执行异常: {str(e)}")

        return test_execution

    def execute_test(
        self,
        jmx_file: str,
        threads: int,
        loops: int | None = None,
        output_dir: str | None = None,
    ) -> TestExecution:
        """TODO: add documentation."""
        # use配置default value
        if loops is None:
            loops = config_manager.get_default_loops()
        if output_dir is None:
            output_dir = config_manager.get_default_output_dir()

        # Create测试Execute实体
        test_execution = TestExecution(
            jmx_file=jmx_file, threads=threads, loops=loops, output_dir=output_dir
        )

        # use实体方法Execute测试
        return self.execute_test_with_entity(test_execution)

    def _update_performance_data(
        self, test_execution: TestExecution, performance_data: dict[str, Any]
    ) -> None:
        """TODO: add documentation."""
        test_execution.total_samples = int(performance_data.get("total_samples", 0))
        test_execution.successful_samples = int(
            performance_data.get("successful_samples", 0)
        )
        test_execution.failed_samples = int(performance_data.get("failed_samples", 0))
        test_execution.average_response_time = float(
            performance_data.get("average_response_time", 0.0)
        )
        test_execution.tps = float(performance_data.get("tps", 0.0))
        test_execution.error_rate = float(performance_data.get("error_rate", 0.0))

    def get_test_result_summary(self, test_execution: TestExecution) -> dict[str, Any]:
        """TODO: add documentation."""
        return {
            "success": test_execution.is_completed(),
            "threads": test_execution.threads,
            "loops": test_execution.loops,
            "jtl_file": test_execution.jtl_file,
            "html_report": test_execution.html_report_dir,
            "performance_data": {
                "total_samples": test_execution.total_samples,
                "successful_samples": test_execution.successful_samples,
                "failed_samples": test_execution.failed_samples,
                "average_response_time": test_execution.average_response_time,
                "tps": test_execution.tps,
                "error_rate": test_execution.error_rate,
            },
            "status": test_execution.status,
            "duration": test_execution.get_duration(),
        }
