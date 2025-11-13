"""TODO: add documentation."""

import os
from pathlib import Path

from jmeter_test_suite.domain.reporting import DailyReportResult, DailyReportTask
from jmeter_test_suite.infrastructure.reporting import DailyReportGenerator


class DailyReportService:
    """TODO: add documentation."""

    def process(self, task: DailyReportTask) -> DailyReportResult:
        """TODO: add documentation."""
        generator = DailyReportGenerator(
            result_dir=task.result_dir,
            config_file=task.config_file,
            output_file=task.output_file,
        )

        action = task.action
        if action == "generate":
            excel_file, zip_file = generator.generate()
            return DailyReportResult(
                success=True,
                excel_file=excel_file,
                zip_file=zip_file,
                warnings=list(generator.runtime_warnings),
            )

        if action == "analyze_jtl":
            target_file = task.target_file or self._locate_latest_jtl(generator)
            if not target_file:
                return DailyReportResult(
                    success=False,
                    warnings=[f"未在目录 {generator.result_dir} 中找到任何JTL文件"],
                )
            generator.analyze_jtl_stuck_detail(target_file)
            return DailyReportResult(
                success=True, warnings=list(generator.runtime_warnings)
            )

        if action == "analyze_nmon":
            generator.analyze_nmon_data(task.target_time or "")
            return DailyReportResult(
                success=True, warnings=list(generator.runtime_warnings)
            )

        if action == "audit":
            target_excel = task.target_file or self._locate_latest_excel(generator)
            if not target_excel:
                return DailyReportResult(
                    success=False, warnings=["未找到Excel报告文件"]
                )
            generator.audit_excel_report(target_excel)
            return DailyReportResult(
                success=True, warnings=list(generator.runtime_warnings)
            )

        if action == "check_logs":
            generator.check_server_logs(task.target_time or "")
            return DailyReportResult(
                success=True, warnings=list(generator.runtime_warnings)
            )

        return DailyReportResult(success=False, warnings=[f"不支持的操作: {action}"])

    def _locate_latest_jtl(self, generator: DailyReportGenerator) -> str | None:
        """TODO: add documentation."""
        result_dir = generator.result_dir
        if not os.path.isdir(result_dir):
            return None
        jtl_files = [
            os.path.join(result_dir, name)
            for name in os.listdir(result_dir)
            if name.endswith(".jtl")
        ]
        if not jtl_files:
            return None
        jtl_files.sort(key=os.path.getmtime)
        return jtl_files[-1]

    def _locate_latest_excel(self, generator: DailyReportGenerator) -> str | None:
        """TODO: add documentation."""
        result_dir = generator.result_dir
        candidates = [
            *[
                os.path.join(result_dir, name)
                for name in os.listdir(result_dir)
                if name.endswith(".xlsx") and name.startswith("测试日报_")
            ]
        ]

        default_reports_dir = (
            Path(generator.result_dir).resolve().parent.parent / "reports"
        )
        if default_reports_dir.exists():
            candidates.extend(
                [
                    str(path)
                    for path in default_reports_dir.glob("测试日报_*.xlsx")
                    if path.is_file()
                ]
            )

        if not candidates:
            return None

        candidates.sort(key=os.path.getmtime)
        return candidates[-1]
