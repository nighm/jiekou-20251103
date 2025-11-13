"""TODO: add documentation."""

from __future__ import annotations

from pathlib import Path


class NmonParser:
    """TODO: add documentation."""

    @classmethod
    def parse_nmon_file(cls, nmon_file: str) -> dict[str, float]:
        """TODO: add documentation."""
        path = Path(nmon_file)
        if not path.exists():
            print(f"⚠️ nmon 文件不存在: {nmon_file}")
            return cls._get_empty_system_data()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception as exc:  # noqa: BLE001
            print(f"❌ 读取 nmon 文件失败: {exc}")
            return cls._get_empty_system_data()

        if len(lines) < 2:
            print("⚠️ nmon 文件内容过少，返回默认值")
            return cls._get_empty_system_data()

        # 当前实现仅返回默认统计数据，详细解析留待后续实现
        return cls._get_empty_system_data()

    @classmethod
    def get_excel_nmon_data(cls, nmon_file: str) -> dict[str, float]:
        """TODO: add documentation."""
        metrics = cls.parse_nmon_file(nmon_file)
        if not metrics:
            return cls._get_default_excel_data()
        return {
            "cpu_all_percent": metrics.get("cpu_all_usage_percent", 0.0),
            "mem_usage_percent": metrics.get("mem_usage_percent", 0.0),
            "diskbusy_percent": metrics.get("diskbusy_percent", 0.0),
            "diskread_kb_per_sec": metrics.get("diskread_kb_per_sec", 0.0),
            "diskwrite_kb_per_sec": metrics.get("diskwrite_kb_per_sec", 0.0),
            "net_io_kb_per_sec": metrics.get("net_io_kb_per_sec", 0.0),
        }

    @staticmethod
    def _get_empty_system_data() -> dict[str, float]:
        """TODO: add documentation."""
        return {
            "cpu_all_usage_percent": 0.0,
            "mem_usage_percent": 0.0,
            "diskbusy_percent": 0.0,
            "diskread_kb_per_sec": 0.0,
            "diskwrite_kb_per_sec": 0.0,
            "net_io_kb_per_sec": 0.0,
        }

    @staticmethod
    def _get_default_excel_data() -> dict[str, float]:
        """TODO: add documentation."""
        return {
            "cpu_all_percent": 45.5,
            "mem_usage_percent": 65.2,
            "diskbusy_percent": 8.3,
            "diskread_kb_per_sec": 125.8,
            "diskwrite_kb_per_sec": 89.3,
            "net_io_kb_per_sec": 1250.5,
        }
