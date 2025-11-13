"""TODO: add documentation."""

import os
from datetime import datetime
from typing import Any

from jmeter_test_suite.domain.entities.excel_report import ExcelReport
from jmeter_test_suite.infrastructure.adapters.beautiful_excel_adapter import (
    BeautifulExcelAdapter,
)
from jmeter_test_suite.infrastructure.config.config_manager import config_manager


class ReportService:
    """TODO: add documentation."""

    def __init__(self) -> None:
        """TODO: add documentation."""
        self.excel_adapter = BeautifulExcelAdapter()

    def generate_batch_excel_report(self, result_dir: str = "result") -> ExcelReport:
        """TODO: add documentation."""
        # CreateExcel报告实体
        excel_report = ExcelReport(
            jmeter_data_file="batch_processing",
            nmon_data_file="batch_processing",
            output_file="batch_output",
            template_file=config_manager.get_excel_template_file(),
        )

        try:
            # Update report status
            excel_report.status = "processing"
            excel_report.start_time = datetime.now()

            # Get所有JTL和nmon file
            jtl_files, nmon_files = self._get_all_test_files(result_dir)

            if not jtl_files:
                print("❌ 未找到JTL文件")
                excel_report.status = "failed"
                return excel_report

            if not nmon_files:
                print("❌ 未找到nmon文件")
                excel_report.status = "failed"
                return excel_report

            # 生成带接口标识和时间戳的输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 识别接口类型：单个接口还是多个接口
            interface_names = set()
            for jtl_file in jtl_files:
                # 从JTL文件名提取接口名称
                # 示例: 02_device_strategy_10threads_3loops_timestamp.jtl
                basename = os.path.basename(jtl_file)
                parts = basename.split("_")
                if len(parts) >= 3:  # 至少有接口名称部分
                    # 前两部分是接口名称，如: 02_device_strategy
                    interface_name = f"{parts[0]}_{parts[1]}"
                    interface_names.add(interface_name)

            # 根据接口数量决定文件名
            if len(interface_names) == 1:
                interface_suffix = list(interface_names)[0]
                output_file = (
                    f"{result_dir}/beautiful_test_report_{interface_suffix}_"
                    f"{timestamp}.xlsx"
                )
            else:
                output_file = (
                    f"{result_dir}/beautiful_test_report_all_interfaces_"
                    f"{timestamp}.xlsx"
                )

            # use新的美观适配器生成报告 - Handle所有nmon file
            success = self.excel_adapter.generate_complete_report(
                jtl_files, nmon_files, output_file
            )

            # Update report status
            excel_report.output_file = output_file
            excel_report.end_time = datetime.now()
            excel_report.status = "completed" if success else "failed"

        except Exception as e:
            excel_report.status = "failed"
            excel_report.end_time = datetime.now()
            print(f"批量Excel报告生成异常: {str(e)}")

        return excel_report

    def _get_all_test_files(self, result_dir: str) -> tuple[list[str], list[str]]:
        """TODO: add documentation."""

        jtl_files = []
        nmon_files = []

        # Get所有JTL文件
        for file in os.listdir(result_dir):
            if file.endswith(".jtl") and not file.startswith("."):
                jtl_path = os.path.join(result_dir, file)
                jtl_files.append(jtl_path)

        # Get所有nmon file（以.nmon结尾或nmon_开头）
        for file in os.listdir(result_dir):
            if (
                (file.endswith(".nmon") or file.startswith("nmon_"))
                and not file.startswith(".")
                and not file.endswith(".jtl")
            ):
                nmon_path = os.path.join(result_dir, file)
                nmon_files.append(nmon_path)

        print(f"📁 找到 {len(jtl_files)} 个JTL文件, {len(nmon_files)} 个nmon文件")

        return jtl_files, nmon_files

    def get_report_summary(self, excel_report: ExcelReport) -> dict[str, Any]:
        """TODO: add documentation."""
        return {
            "success": excel_report.is_completed(),
            "excel_file": excel_report.output_file,
            "jmeter_data_file": excel_report.jmeter_data_file,
            "nmon_data_file": excel_report.nmon_data_file,
            "template_file": excel_report.template_file,
            "status": excel_report.status,
            "processing_time": excel_report.get_processing_time(),
            "include_charts": excel_report.include_charts,
        }
