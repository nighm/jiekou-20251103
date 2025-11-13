"""TODO: add documentation."""

import argparse
import sys
from collections.abc import Callable
from types import FrameType

from jmeter_test_suite.application.services.report_service import ReportService
from jmeter_test_suite.application.services.sync_execution_service import (
    SyncExecutionService,
)
from jmeter_test_suite.infrastructure.config import config_manager


def main() -> int:
    """TODO: add documentation."""
    if len(sys.argv) < 2:
        print_help()
        return 1

    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    if command == "test":
        return handle_test_command(args)
    elif command == "run":
        return handle_run_command(args)
    elif command == "report":
        return handle_report_command(args)
    elif command == "all":
        return handle_all_command(args)
    elif command == "distributed":
        return handle_distributed_command(args)
    elif command == "config-info":
        return handle_config_info_command(args)
    elif command == "mode-info":
        return handle_mode_info_command(args)
    elif command == "open-result":
        return handle_open_result_command(args)
    elif command == "help" or command == "--help" or command == "-h":
        print_help()
        return 0
    else:
        print(f"错误：未知命令 '{command}'")
        print_help()
        return 1


def print_help() -> None:
    """TODO: add documentation."""
    print(
        """
JMeter和nmon性能测试数据收集与Excel报告生成工具 v5.0.0

用法:
    jmeter_test_suite <command> [options]

可用命令:
    test         - 单次JMeter测试（指定线程数和循环数）
    run          - 批量执行JMeter和nmon（推荐，调用test命令+全局nmon监控）
    report       - 生成Excel报告
    all          - 一键执行：run + report（自动执行测试并生成报告）
    distributed  - 分布式压测（使用多台设备同时压测）
    open-result  - 打开结果文件夹（跨平台）
    help         - 显示帮助信息

示例:
    jmeter_test_suite all                             # 一键执行（推荐）
    jmeter_test_suite run test.jmx                    # 批量执行
    jmeter_test_suite test test.jmx --threads 200 --loops 5  # 单次测试
    jmeter_test_suite report --jmeter-data result.jtl \
        --nmon-data nmon_data.nmon --output report.xlsx

批量执行说明:
    run命令会调用test命令执行所有JMeter测试，同时启动全局nmon监控，
    生成一个完整的nmon文件覆盖整个测试周期。

更多信息请参考文档。
"""
    )


def handle_test_command(args: list[str]) -> int:
    """TODO: add documentation."""
    try:
        # Get default parameters from config
        test_plans = config_manager.get("test_plans", [])
        test_plans_dir = config_manager.get(
            "test_plans_dir", "./src/jmeter_test_suite/infrastructure/config/test_plans"
        )
        if not test_plans:
            print("❌ 错误：配置中没有test_plans")
            return 1

        # Use default JMX file from config
        jmx_file = f"{test_plans_dir}/{test_plans[0]}"
        output_dir = config_manager.get_result_dir()

        # Create JMeter service
        from jmeter_test_suite.domain.services.jmeter_service import JMeterService

        jmeter_service = JMeterService()

        # Check if direct parameters provided (threads and loops)
        if len(args) >= 2:
            try:
                threads = int(args[0])
                loops = int(args[1])

                print("🚀 执行单次JMeter测试")
                print(f"📊 JMX文件: {jmx_file}")
                print(f"📊 线程数: {threads}")
                print(f"📊 循环数: {loops}")
                print(f"📁 输出目录: {output_dir}")

                # Execute single test
                test_execution = jmeter_service.execute_test(
                    jmx_file, threads, loops, output_dir
                )

                if test_execution.is_completed():
                    print(f"✅ 测试成功: {threads}线程, {loops}循环")
                    if test_execution.tps:
                        print(f"📊 TPS: {test_execution.tps:.2f}")
                    if test_execution.average_response_time:
                        avg_resp = test_execution.average_response_time
                        print(f"📊 Average response time: {avg_resp:.2f}ms")
                    if test_execution.error_rate:
                        print(f"📊 Error rate: {test_execution.error_rate:.2f}%")
                    return 0
                else:
                    print(f"❌ 测试失败: {threads}线程, {loops}循环")
                    return 1

            except ValueError:
                print("❌ 错误：线程数和循环数必须是整数")
                print("用法: jmeter_test_suite test <线程数> <循环数>")
                return 1

        # Use complete thread and loop ranges from config
        thread_range = config_manager.get("thread_range", "1000 4000 3000")
        loop_range = config_manager.get("loop_range", "1 4 3")

        print("🚀 Execute the JMeter test（使用YAML完整参数范围）")
        print(f"📊 JMX文件: {jmx_file}")
        print(f"📊 线程范围: {thread_range}")
        print(f"📊 循环范围: {loop_range}")
        print(f"📁 输出目录: {output_dir}")

        # Archive old result files
        archive_old_results(output_dir)

        # Parse thread and loop ranges
        thread_values = parse_range(thread_range)
        loop_values = parse_range(loop_range)

        total_tests = len(thread_values) * len(loop_values)
        success_count = 0

        print(f"⏳ 开始执行批量JMeter测试，共{total_tests}轮...")

        # Execute batch tests
        for threads in thread_values:
            for loops in loop_values:
                print(f"🔄 执行测试: {threads}线程, {loops}循环")

                try:
                    # Execute single JMeter test
                    test_execution = jmeter_service.execute_test(
                        jmx_file, threads, loops, output_dir
                    )

                    if test_execution.is_completed():
                        success_count += 1
                        print(f"✅ 测试成功: {threads}线程, {loops}循环")
                    else:
                        print(f"❌ 测试失败: {threads}线程, {loops}循环")

                except Exception as e:
                    print(f"❌ 测试异常: {threads}线程, {loops}循环 - {str(e)}")

        # Display execution summary
        print("📋 执行摘要:")
        print(f"总测试数: {total_tests}")
        print(f"成功数: {success_count}")
        print(f"失败数: {total_tests - success_count}")

        if success_count == total_tests:
            print("✅ 所有JMeter测试执行成功!")
            return 0
        else:
            print("⚠️ 部分JMeter测试执行失败!")
            return 1

    except Exception as e:
        print(f"❌ execution exception: {str(e)}")
        return 1


def archive_old_results(output_dir: str) -> None:
    """TODO: add documentation."""
    import os
    import shutil

    try:
        # Create old directory
        old_dir = os.path.join(output_dir, "old")
        os.makedirs(old_dir, exist_ok=True)

        # Get all files to move (excluding old directory itself)
        files_to_move = []
        if os.path.exists(output_dir):
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                # 只Move file，不移动目录（排除old目录）
                if os.path.isfile(item_path) and item != "old":
                    files_to_move.append(item)

        if files_to_move:
            print(f"📦 归档 {len(files_to_move)} 个旧文件到 old/ 目录...")

            # Move files to old directory
            for filename in files_to_move:
                src_path = os.path.join(output_dir, filename)
                dst_path = os.path.join(old_dir, filename)
                # 如果目标文件已存在，直接覆盖
                if os.path.exists(dst_path):
                    os.remove(dst_path)
                shutil.move(src_path, dst_path)

            print(f"✅ 已归档 {len(files_to_move)} 个文件到 old/ 目录")
        else:
            print("📁 result目录为空，无需归档")

    except Exception as e:
        print(f"⚠️ 归档旧文件时出错: {str(e)}")
        # 归档失败不应该影响测试执行


def parse_range(range_str: str) -> list[int]:
    """TODO: add documentation."""
    try:
        parts = range_str.split()
        if len(parts) != 3:
            raise ValueError("Invalid range format")

        start, end, step = map(int, parts)
        if step == 0:
            if start != end:
                warning_text = (
                    f'⚠️ range configuration "{range_str}" step is 0，'
                    f"已按单值 {start} 处理"
                )
                print(warning_text)
            return [start]
        return list(range(start, end + 1, step))
    except Exception as e:
        print(f"❌ 解析范围失败: {range_str} - {str(e)}")
        return [100]  # Default value


def handle_run_command(args: list[str]) -> int:
    """TODO: add documentation."""
    parser = argparse.ArgumentParser(
        description="execute in batchJMeter和nmon（调用testcommand+全局nmon监控）"
    )
    parser.add_argument(
        "jmx_file",
        nargs="?",
        default=None,
        help="JMXfile path（可选，默认use配置中的test_plans）",
    )
    parser.add_argument(
        "--server",
        default=config_manager.get("nmon.server", "192.168.24.45"),
        help="nmon服务器IP地址",
    )
    parser.add_argument(
        "--user", default=config_manager.get("nmon.user", "test"), help="SSH用户名"
    )
    parser.add_argument(
        "--password", default=config_manager.get("nmon.password", "1"), help="SSH密码"
    )
    parser.add_argument(
        "--output", default=config_manager.get_result_dir(), help="输出目录"
    )

    try:
        parsed_args = parser.parse_args(args)

        # If jmx_file is not specified, get default from config
        if parsed_args.jmx_file is None:
            test_plans = config_manager.get("test_plans", [])
            test_plans_dir = config_manager.get(
                "test_plans_dir",
                "./src/jmeter_test_suite/infrastructure/config/test_plans",
            )
            if not test_plans:
                print("❌ 错误：未指定JMX文件，且配置中也没有test_plans")
                return 1
            # Build complete file path
            parsed_args.jmx_file = f"{test_plans_dir}/{test_plans[0]}"
            print(f"📋 使用配置中的默认测试计划: {parsed_args.jmx_file}")

        print("🚀 批量Execute the JMeter test和nmon监控")
        print(f"📊 JMeter: {parsed_args.jmx_file}")
        print(f"🔍 nmon: 服务器={parsed_args.server}, 用户={parsed_args.user}")
        print(f"📁 输出目录: {parsed_args.output}")

        # Create sync execution service
        sync_service = SyncExecutionService()

        # Execute batch sync tests (call test command + global nmon monitoring)
        print("⏳ 开始批量执行...")
        result = sync_service.execute_batch_sync_test(
            parsed_args.jmx_file,
            parsed_args.server,
            parsed_args.user,
            parsed_args.password,
            parsed_args.output,
        )

        # Display batch execution summary
        print("📋 批量执行摘要:")
        print(f"JMeter测试: {'成功' if result['jmeter']['success'] else '失败'}")
        print(f"nmon监控: {'成功' if result['nmon']['success'] else '失败'}")
        if result.get("total_duration"):
            print(f"总执行时长: {result['total_duration']:.2f}秒")
        print(f"同步状态: {result['sync_status']}")

        if result["success"]:
            print("✅ 批量执行全部成功!")
            return 0
        else:
            print("⚠️ 批量执行部分失败，请检查详细信息")
            return 1

    except Exception as e:
        print(f"❌ execution exception: {str(e)}")
        return 1


def handle_report_command(args: list[str]) -> int:
    """TODO: add documentation."""
    try:
        # Check arguments, support specifying directory
        result_dir = "result"
        if args:
            if len(args) == 1:
                result_dir = args[0]
                print("📊 批量Generate Excel report")
                print(f"📁 处理目录: {result_dir}")
            else:
                print("❌ report命令最多只接受一个参数（directory path）")
                return 1
        else:
            print("📊 批量Generate Excel report")
            print("📁 处理目录: result")

        print("⏳ 开始批量处理...")

        # Create report service
        report_service = ReportService()

        # Batch process specified directory
        excel_report = report_service.generate_batch_excel_report(result_dir)

        # Get report summary
        report_summary = report_service.get_report_summary(excel_report)

        if report_summary["success"]:
            print("✅ Excel报告生成成功!")
            print(f"📄 报告文件: {report_summary['excel_file']}")
            print(f"⏱️ 处理时间: {report_summary['processing_time']}秒")
            print(f"📊 包含图表: {'是' if report_summary['include_charts'] else '否'}")
            return 0
        else:
            print("❌ Excel报告生成失败!")
            print(f"状态: {report_summary['status']}")
            return 1

    except Exception as e:
        print(f"❌ execution exception: {str(e)}")
        return 1


def handle_all_command(args: list[str]) -> int:
    """TODO: add documentation."""
    import signal
    import sys

    if not args:
        raise SystemExit("all 命令缺少必要参数")

    # Set global timeout (90 minutes)
    def timeout_handler(_signum: int, _frame: FrameType | None) -> None:
        print("\n⏰ 执行超时（90分钟），强制退出")
        print("💡 建议检查网络连接和服务器状态")
        sys.exit(1)

    alarm_fn: Callable[[int], None] | None = None
    sigalrm = getattr(signal, "SIGALRM", None)

    try:
        alarm_candidate = getattr(signal, "alarm", None)
        if sigalrm is not None and callable(alarm_candidate):
            alarm_fn = alarm_candidate
            signal.signal(sigalrm, timeout_handler)
            alarm_fn(5400)  # 90 minutes timeout

        # Set timeout signal (only effective on Unix systems)
        if sigalrm is not None:
            print("⏰ 设置90分钟超时保护")

        # Check distributed configuration
        distributed_config = config_manager.get("distributed", {})
        distributed_enabled = distributed_config.get("enabled", False)

        if distributed_enabled:
            print("🚀 开始一键执行：分布式压测 + report")
            print("📡 将自动调用笔记本2上的JMeter")
        else:
            print("🚀 开始一键执行：单机压测 + report")

        print("=" * 60)

        # Step 1: Execute stress test (distributed or standalone)
        print("📋 第一步：执行压测...")
        if distributed_enabled:
            test_exit_code = handle_distributed_command(args)
        else:
            test_exit_code = handle_run_command(args)

        if test_exit_code != 0:
            print("❌ 压测执行失败，停止执行")
            return test_exit_code

        print("✅ 压测执行成功")
        print("=" * 60)

        # Step 2: Wait 5 seconds to ensure files are fully generated
        print("⏳ 第二步：等待5秒确保文件完全生成...")
        import time

        time.sleep(5)
        print("✅ 等待完成")
        print("=" * 60)

        # Step 3: Execute report command
        print("📋 第三步：执行report命令...")
        report_exit_code = handle_report_command([])

        if report_exit_code != 0:
            print("❌ reportCommand execution failed")
            return report_exit_code

        print("✅ report命令执行成功")
        print("=" * 60)

        # Summary
        print("🎉 一键执行完成！")
        print("📊 已生成完整的测试报告")
        print("📁 报告文件位置: result/complete_test_report_*.xlsx")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
        return 1
    except Exception as e:
        print(f"❌ 一键execution exception: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        # Clear timeout signal
        if sigalrm is not None and alarm_fn is not None:
            alarm_fn(0)


def handle_distributed_command(_args: list[str]) -> int:
    """TODO: add documentation."""
    try:
        from jmeter_test_suite.application.services import (
            distributed_execution_service,
        )

        DistributedExecutionService = (
            distributed_execution_service.DistributedExecutionService
        )

        # Get test parameters
        test_plans = config_manager.get("test_plans", [])
        test_plans_dir = config_manager.get(
            "test_plans_dir", "./src/jmeter_test_suite/infrastructure/config/test_plans"
        )
        jmx_file = f"{test_plans_dir}/{test_plans[0]}"

        thread_range = config_manager.get("thread_range", "100 600 200")
        loop_range = config_manager.get("loop_range", "30 110 30")

        print("🚀 开始分布式压测...")
        print(f"📊 JMX文件: {jmx_file}")
        print(f"📊 线程范围: {thread_range}")
        print(f"📊 循环范围: {loop_range}")

        # Create distributed execution service
        distributed_service = DistributedExecutionService()

        # Create distributed execution instance
        execution = distributed_service.create_distributed_execution_from_config(
            jmx_file=jmx_file,
            total_threads=1000,  # Initial value, will be parsed from config
            loops=50,
            ramp_time=60,
        )

        print(f"📊 Slave数量: {len(execution.slaves)}")
        for slave in execution.slaves:
            print(f"   - {slave.name}: {slave.host}:{slave.port}")

        # Execute distributed tests
        success = distributed_service.execute_distributed_test(execution)

        # Display execution summary
        print("📋 分布式压测摘要:")
        print(f"总测试数: {execution.total_tests}")
        print(f"成功数: {execution.successful_tests}")
        print(f"失败数: {execution.failed_tests}")
        print(f"成功率: {execution.get_success_rate():.2%}")

        if execution.get_duration():
            print(f"执行时长: {execution.get_duration():.2f}秒")

        if success:
            print("✅ 分布式压测执行成功!")
            return 0
        else:
            print("❌ 分布式压测执行失败!")
            return 1

    except Exception as e:
        print(f"❌ 分布式压测异常: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


def handle_config_info_command(_args: list[str]) -> int:
    """TODO: add documentation."""
    try:
        # Read configuration
        thread_range = config_manager.get("thread_range", "100 600 200")
        loop_range = config_manager.get("loop_range", "30 110 30")
        test_plans = config_manager.get("test_plans", [])

        print(f"📊 线程范围: {thread_range}")
        print(f"📊 循环范围: {loop_range}")
        if test_plans:
            print(f"📊 测试计划: {test_plans[0]}")

        # Calculate test rounds
        thread_values = parse_range(thread_range)
        loop_values = parse_range(loop_range)
        thread_count = len(thread_values)
        loop_count = len(loop_values)
        total = thread_count * loop_count

        print(f"📊 预计测试轮数: {thread_count} × {loop_count} = {total}轮")
        print(f"⏱️ 预计耗时: {total // 4 + 1}-{total // 2 + 2}分钟")

        return 0

    except Exception as e:
        print(f"❌ 配置信息读取失败: {str(e)}")
        return 1


def open_file_manager(path: str) -> bool:
    """TODO: add documentation."""
    import os
    import platform
    import shutil
    import subprocess

    # Convert to absolute path
    abs_path = os.path.abspath(path)

    if not os.path.exists(abs_path):
        print(f"❌ 路径不存在: {abs_path}")
        return False

    if not os.path.isdir(abs_path):
        print(f"❌ 路径不是目录: {abs_path}")
        return False

    system = platform.system()

    try:
        if system == "Windows":
            # Windows: use explorer
            subprocess.Popen(["explorer", abs_path])
        elif system == "Darwin":
            # macOS: use open
            subprocess.Popen(["open", abs_path])
        else:
            # Linux: try multiple file managers
            file_managers = ["xdg-open", "nautilus", "dolphin", "thunar", "pcmanfm"]
            opened = False

            for cmd in file_managers:
                if shutil.which(cmd):
                    subprocess.Popen([cmd, abs_path])
                    opened = True
                    break

            if not opened:
                print("⚠️ 未找到可用的文件管理器")
                print(f"📁 请手动打开文件夹: {abs_path}")
                return False

        print(f"✅ 已打开文件夹: {abs_path}")
        return True

    except Exception as e:
        print(f"❌ 打开文件夹失败: {str(e)}")
        print(f"📁 文件夹路径: {abs_path}")
        return False


def handle_open_result_command(args: list[str]) -> int:
    """TODO: add documentation."""
    try:
        # Get result directory
        result_dir = args[0] if args else config_manager.get_result_dir()

        # Open folder
        if open_file_manager(result_dir):
            return 0
        else:
            return 1

    except Exception as e:
        print(f"❌ execution exception: {str(e)}")
        return 1


def handle_mode_info_command(_args: list[str]) -> int:
    """TODO: add documentation."""
    try:
        # Read distributed configuration
        distributed_config = config_manager.get("distributed", {})
        enabled = distributed_config.get("enabled", False)

        mode_text = "✅ 分布式压测" if enabled else "✅ 单机压测"
        print(f"📊 测试模式: {mode_text}")

        if enabled:
            slaves = distributed_config.get("slaves", [])
            print(f"📊 Slave数量: {len(slaves)}")
            for slave in slaves:
                host = slave.get("host", "unknown")
                port = slave.get("port", "unknown")
                name = slave.get("name", "unknown")
                print(f"   - {name}: {host}:{port}")

        return 0

    except Exception as e:
        print(f"❌ 模式信息读取失败: {str(e)}")
        return 1
