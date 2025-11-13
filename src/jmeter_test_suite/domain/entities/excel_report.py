"""TODO: add documentation."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExcelReport:
    """TODO: add documentation."""

    nmon_data_file: str | None = None
    output_file: str = ""
    template_file: str | None = None
    jmeter_data_file: str | None = None

    # Execute状态
    status: str = "pending"  # pending, processing, completed, failed
    start_time: datetime | None = None
    end_time: datetime | None = None

    # 报告内容
    include_charts: bool = True
    chart_types: list[str] | None = None

    # 数据统计
    jmeter_samples_count: int | None = None
    nmon_records_count: int | None = None

    def __post_init__(self) -> None:
        if self.chart_types is None:
            self.chart_types = ["line", "bar"]

    def is_completed(self) -> bool:
        """TODO: add documentation."""
        return self.status == "completed"

    def is_failed(self) -> bool:
        """TODO: add documentation."""
        return self.status == "failed"

    def is_processing(self) -> bool:
        """TODO: add documentation."""
        return self.status == "processing"

    def get_processing_time(self) -> float | None:
        """TODO: add documentation."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
