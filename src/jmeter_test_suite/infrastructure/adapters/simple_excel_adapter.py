"""TODO: add documentation."""

from __future__ import annotations


class SimpleExcelAdapter:
    """TODO: add documentation."""

    def generate_excel_report(
        self, jmeter_data_file: str, nmon_data_file: str, output_file: str
    ) -> bool:
        """TODO: add documentation."""
        print(
            "[调试] SimpleExcelAdapter.generate_excel_report "
            f"接收JMeter数据 {jmeter_data_file}，nmon数据 {nmon_data_file}，"
            f"输出文件 {output_file}"
        )
        return False

    def generate_batch_excel_report(self, result_dir: str = "result") -> bool:
        """TODO: add documentation."""
        print(
            "[调试] SimpleExcelAdapter.generate_batch_excel_report "
            f"扫描结果目录 {result_dir}"
        )
        return False
