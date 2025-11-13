"""TODO: add documentation."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class DailyReportTask:
    """TODO: add documentation."""

    result_dir: str | None = None
    config_file: str | None = None
    output_file: str | None = None
    action: str = "generate"
    target_file: str | None = None
    target_time: str | None = None


@dataclass(slots=True)
class DailyReportResult:
    """TODO: add documentation."""

    success: bool = False
    excel_file: str | None = None
    zip_file: str | None = None
    warnings: list[str] = field(default_factory=list)
