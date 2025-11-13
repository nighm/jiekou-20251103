"""TODO: add documentation."""

from __future__ import annotations

from collections.abc import Sequence


class BeautifulExcelAdapter:
    """TODO: add documentation."""

    def generate_complete_report(
        self, jtl_files: Sequence[str], nmon_files: Sequence[str], output_file: str
    ) -> bool:
        """TODO: add documentation."""
        print(
            "[调试] BeautifulExcelAdapter.generate_complete_report "
            f"收到 {len(jtl_files)} 个JTL文件，{len(nmon_files)} 个nmon文件，"
            f"输出目标 {output_file}"
        )
        return False
