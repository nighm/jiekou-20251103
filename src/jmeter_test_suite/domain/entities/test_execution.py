"""TODO: add documentation."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from jmeter_test_suite.infrastructure.config import config_manager


@dataclass
class TestExecution:
    """TODO: add documentation."""

    threads: int
    loops: int = 1
    output_dir: str | None = None
    jmx_file: str | None = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Execute状态
    status: str = "pending"  # pending, running, completed, failed
    start_time: datetime | None = None
    end_time: datetime | None = None

    # 输出文件
    jtl_file: str | None = None
    html_report_dir: str | None = None

    # 性能数据
    total_samples: int | None = None
    successful_samples: int | None = None
    failed_samples: int | None = None
    average_response_time: float | None = None
    tps: float | None = None
    error_rate: float | None = None

    def is_completed(self) -> bool:
        """TODO: add documentation."""
        return self.status == "completed"

    def is_failed(self) -> bool:
        """TODO: add documentation."""
        return self.status == "failed"

    def get_duration(self) -> float | None:
        """TODO: add documentation."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __post_init__(self) -> None:
        """TODO: add documentation."""
        if self.output_dir is None:
            self.output_dir = config_manager.get_default_output_dir()
