"""TODO: add documentation."""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from jmeter_test_suite.domain.entities.test_execution import TestExecution
from jmeter_test_suite.infrastructure.config import config_manager


class JMeterAdapter:
    """TODO: add documentation."""

    def __init__(self, jmeter_command: str | None = None):
        """TODO: add documentation."""
        if jmeter_command is None:
            # 从配置文件ReadJMetercommand路径
            self.jmeter_command = config_manager.get_jmeter_command()
        else:
            self.jmeter_command = jmeter_command

    def execute_test(self, test_execution: TestExecution) -> bool:
        """TODO: add documentation."""
        try:
            if test_execution.jmx_file is None:
                raise ValueError("JMX文件路径未设置")

            # Validate that the JMX file exists
            if not os.path.exists(test_execution.jmx_file):
                raise FileNotFoundError(f"JMX文件不存在: {test_execution.jmx_file}")

            project_root_path = Path(__file__).resolve().parents[4]

            # Create output directory
            output_dir = (
                test_execution.output_dir or config_manager.get_default_output_dir()
            )
            test_execution.output_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)

            # Read log capture configuration
            log_config = config_manager.get_log_capture_config() or {}
            result_dir = Path(config_manager.get_result_dir())
            if not result_dir.is_absolute():
                result_dir = (project_root_path / result_dir).resolve()
            os.makedirs(result_dir, exist_ok=True)

            latest_log_name = Path(
                log_config.get("latest_file", "jmeter_latest.log")
            ).name
            archive_suffix = log_config.get("archive_suffix", "_jmeter.log")
            stdout_suffix = log_config.get("stdout_suffix", "_stdout.log")
            stderr_suffix = log_config.get("stderr_suffix", "_stderr.log")

            latest_log_path = result_dir / latest_log_name

            # Generate filename with interface name, args, and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 从JMXfile path提取接口名称
            jmx_basename = os.path.basename(test_execution.jmx_file)
            interface_name = jmx_basename.replace(".jmx", "")  # 如: 02_device_strategy

            base_filename = (
                f"{interface_name}_{test_execution.threads}threads_"
                f"{test_execution.loops}loops_{timestamp}"
            )
            jtl_file = os.path.join(output_dir, f"{base_filename}.jtl")
            stdout_file = result_dir / f"{base_filename}{stdout_suffix}"
            stderr_file = result_dir / f"{base_filename}{stderr_suffix}"
            archived_log_file = result_dir / f"{base_filename}{archive_suffix}"

            # BuildJMetercommand（不生成HTML报告）
            cmd = self._build_jmeter_command(
                test_execution.jmx_file,
                test_execution.threads,
                test_execution.loops,
                jtl_file,
                None,  # 不生成HTML报告
                output_dir,  # 传递输出目录
                str(latest_log_path),
            )

            # 更新测试Execute状态
            test_execution.status = "running"
            test_execution.start_time = datetime.now()
            test_execution.jtl_file = jtl_file
            # 不再SetHTML报告目录

            # ExecuteJMetercommand
            print(f"执行JMeter命令: {' '.join(cmd)}")
            # Ensureuse项目根目录作为工作目录
            project_root = str(project_root_path)
            print(f"工作目录: {project_root}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=project_root
            )

            # 写入stdout/stderr日志
            stdout_file.write_text(result.stdout or "", encoding="utf-8")
            stderr_file.write_text(result.stderr or "", encoding="utf-8")

            # 归档本次JMeter日志
            if latest_log_path.exists():
                shutil.copy2(latest_log_path, archived_log_file)

            # Update execution result
            test_execution.end_time = datetime.now()

            if result.returncode == 0:
                test_execution.status = "completed"
                print("JMeter执行成功")
                return True
            else:
                test_execution.status = "failed"
                print(f"JMeter执行失败，返回码: {result.returncode}")
                print(f"错误输出: {result.stderr}")
                print(f"标准输出: {result.stdout}")
                return False

        except Exception as e:
            test_execution.status = "failed"
            test_execution.end_time = datetime.now()
            print(f"JMeter执行异常: {str(e)}")
            import traceback

            traceback.print_exc()
            return False

    def _build_jmeter_command(
        self,
        jmx_file: str,
        threads: int,
        loops: int,
        jtl_file: str,
        html_dir: str | None = None,
        _output_dir: str | None = None,
        log_file: str | None = None,
    ) -> list[str]:
        """TODO: add documentation."""
        cmd = [
            self.jmeter_command,
            "-n",  # 非GUI模式
            "-t",
            jmx_file,  # 测试计划文件
            "-l",
            jtl_file,  # 结果文件
            "-Jthread_count=" + str(threads),  # 线程数
            "-Jloop_count=" + str(loops),  # 循环次数
            "-Jsampleresult.nanoThreadSleep=0",  # 禁用线程延迟，用于CPU极限测试
        ]

        if log_file:
            cmd.extend(["-j", log_file])

        # 不再usejmeter.properties配置文件

        # 只有在指定HTML目录时才生成HTML报告
        if html_dir:
            cmd.extend(["-e", "-o", html_dir])

        return cmd

    def parse_jtl_file(
        self,
        jtl_file: str,
        test_execution: TestExecution | None = None,
    ) -> dict[str, float | int]:
        """TODO: add documentation."""
        try:
            if not os.path.exists(jtl_file):
                raise FileNotFoundError(f"JTL文件不存在: {jtl_file}")

            # ReadJTL文件
            with open(jtl_file, encoding="utf-8") as f:
                lines = f.readlines()

            if len(lines) < 2:  # 至少需要标题行和一行数据
                return self._get_empty_performance_data()

            # Parse数据
            total_samples = 0
            successful_samples = 0
            failed_samples = 0
            total_response_time = 0.0

            # Skip the header row
            for line in lines[1:]:
                if line.strip():
                    total_samples += 1
                    parts = line.strip().split(",")
                    if len(parts) >= 8:
                        success = parts[7].lower() == "true"
                        response_time = float(parts[1])

                        if success:
                            successful_samples += 1
                            total_response_time += response_time
                        else:
                            failed_samples += 1

            # Calculate performance metrics
            avg_response_time = (
                total_response_time / successful_samples
                if successful_samples > 0
                else 0.0
            )
            error_rate = (
                (failed_samples / total_samples * 100) if total_samples > 0 else 0.0
            )

            # CalculateTPS（从测试Execute时间Calculate）
            duration = test_execution.get_duration() if test_execution else None
            if duration is None or duration <= 0:
                duration = 1.0  # 避免除零错误
            tps = successful_samples / duration if duration > 0 else 0.0

            return {
                "total_samples": total_samples,
                "successful_samples": successful_samples,
                "failed_samples": failed_samples,
                "average_response_time": round(avg_response_time, 2),
                "tps": round(tps, 2),
                "error_rate": round(error_rate, 2),
            }

        except Exception as e:
            print(f"解析JTL文件失败: {str(e)}")
            return self._get_empty_performance_data()

    def _get_empty_performance_data(self) -> dict[str, float | int]:
        """TODO: add documentation."""
        return {
            "total_samples": 0,
            "successful_samples": 0,
            "failed_samples": 0,
            "average_response_time": 0.0,
            "tps": 0.0,
            "error_rate": 0.0,
        }
