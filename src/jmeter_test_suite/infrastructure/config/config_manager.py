"""TODO: add documentation."""

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

PathType = str | os.PathLike[str]


class ConfigManager:
    """TODO: add documentation."""

    def __init__(self, config_file: PathType | None = None) -> None:
        """TODO: add documentation."""
        self._config_file = self._resolve_config_path(config_file)
        self._config: dict[str, Any] = {}
        self.load_config()

    def _resolve_config_path(self, config_file: PathType | None) -> Path:
        """TODO: add documentation."""
        if config_file is not None:
            return Path(config_file).expanduser().resolve()
        return Path(__file__).resolve().with_name("jmeter_config.yaml")

    def load_config(self) -> None:
        """TODO: add documentation."""
        if not self._config_file.exists():
            self._config = {}
            return
        try:
            with self._config_file.open(encoding="utf-8") as fp:
                data = yaml.safe_load(fp) or {}
            self._config = data if isinstance(data, dict) else {}
        except Exception as exc:  # noqa: BLE001
            print(f"加载配置文件失败: {exc}")
            self._config = {}

    def reload_config(self) -> None:
        """TODO: add documentation."""
        self.load_config()

    def get(self, key: str, default: Any = None) -> Any:
        """TODO: add documentation."""
        current: Any = self._config
        for section in key.split("."):
            if isinstance(current, dict) and section in current:
                current = current[section]
            else:
                return default
        return current

    def get_all_config(self) -> dict[str, Any]:
        """TODO: add documentation."""
        return dict(self._config)

    def _which(self, command: str) -> str | None:
        """TODO: add documentation."""
        from shutil import which

        return which(command)

    def get_jmeter_command(self) -> str:
        """TODO: add documentation."""
        system_name = os.name
        env_home = os.environ.get("JMETER_HOME")
        if env_home:
            candidate = (
                Path(env_home) / "bin" / "jmeter.bat"
                if system_name == "nt"
                else PurePosixPath(env_home) / "bin" / "jmeter"
            )
            if os.path.exists(candidate):
                return str(candidate)

        env_path = os.environ.get("JMETER_PATH")
        if env_path and os.path.exists(env_path):
            return env_path

        config_cmd = self.get("jmeter.command")
        if isinstance(config_cmd, str) and config_cmd:
            if os.path.isabs(config_cmd) and os.path.exists(config_cmd):
                return config_cmd
            project_root = self._detect_project_root()
            candidate_path = project_root / config_cmd
            if candidate_path.exists():
                return str(candidate_path)

        detected = self._which("jmeter")
        if detected:
            return detected

        if system_name == "nt":
            detected_bat = self._which("jmeter.bat")
            if detected_bat:
                return detected_bat

        fallback_candidates = (
            list(self._windows_fallback_paths()) if system_name == "nt" else ["jmeter"]
        )
        for fallback_candidate in fallback_candidates:
            if os.path.exists(fallback_candidate):
                return fallback_candidate
            detected_cmd = self._which(fallback_candidate)
            if detected_cmd:
                return detected_cmd
        return fallback_candidates[-1]

    def _windows_fallback_paths(self) -> Iterable[str]:
        """TODO: add documentation."""
        return (
            r"C:\apache-jmeter\bin\jmeter.bat",
            r"D:\tools\apache-jmeter\bin\jmeter.bat",
            "jmeter.bat",
        )

    def _detect_project_root(self) -> Path:
        """TODO: add documentation."""
        probe = Path(__file__).resolve()
        for _ in range(5):
            candidate = probe.parent
            if (candidate / "src").exists():
                return candidate
            probe = candidate
        return probe

    def get_result_dir(self) -> str:
        """TODO: add documentation."""
        return str(self.get("result_dir", self._detect_project_root() / "result"))

    def get_nmon_config(self) -> dict[str, Any]:
        """TODO: add documentation."""
        return dict(self.get("nmon", {}) or {})

    def get_excel_config(self) -> dict[str, Any]:
        """TODO: add documentation."""
        return dict(self.get("excel", {}) or {})

    def get_log_capture_config(self) -> dict[str, Any]:
        """TODO: add documentation."""
        return dict(self.get("log_capture", {}) or {})

    def get_server_logs_config(self) -> dict[str, Any]:
        """TODO: add documentation."""
        return dict(self.get("server_logs", {}) or {})

    def get_system_config(self) -> dict[str, Any]:
        """TODO: add documentation."""
        return dict(self.get("system", {}) or {})

    def get_sync_config(self) -> dict[str, Any]:
        """TODO: add documentation."""
        return dict(self.get("sync", {}) or {})

    def get_error_handling_config(self) -> dict[str, Any]:
        """TODO: add documentation."""
        return dict(self.get("error_handling", {}) or {})

    def get_excel_report_config(self) -> dict[str, Any]:
        """TODO: add documentation."""
        return dict(self.get("excel_report", {}) or {})

    def get_excel_template_file(self) -> str:
        """TODO: add documentation."""
        return str(
            self.get(
                "excel_report.template_file",
                "docs/diagrams/sample-test-data.xlsx",
            )
        )

    def get_excel_output_dir(self) -> str:
        """TODO: add documentation."""
        default_dir = Path(self.get_result_dir()) / "excel"
        return str(self.get("excel_report.output_dir", default_dir))

    def get_excel_field_mapping(self, sheet_type: str) -> dict[str, str]:
        """TODO: add documentation."""
        mapping = self.get("excel_report.field_mapping", {})
        if not isinstance(mapping, dict):
            return {}
        sheet_mapping = mapping.get(sheet_type, {})
        return dict(sheet_mapping) if isinstance(sheet_mapping, dict) else {}

    def get_thread_range_min(self) -> int:
        """TODO: add documentation."""
        thread_range = str(self.get("thread_range", "100 100 0"))
        return self._parse_range_min(thread_range, 100)

    def get_loop_range_min(self) -> int:
        """TODO: add documentation."""
        loop_range = str(self.get("loop_range", "1 1 0"))
        return self._parse_range_min(loop_range, 1)

    def get_default_output_dir(self) -> str:
        """TODO: add documentation."""
        default = self._detect_project_root() / "result"
        configured = self.get("result_dir", default)
        if isinstance(configured, Path):
            return str(configured)
        if isinstance(configured, PurePosixPath):
            return str(configured)
        if isinstance(configured, os.PathLike):
            return str(Path(configured))
        if isinstance(configured, str):
            return str(Path(configured).expanduser())
        return str(default)

    def get_default_loops(self) -> int:
        """TODO: add documentation."""
        loop_range = str(self.get("loop_range", "1 1 0"))
        return self._parse_range_min(loop_range, 1)

    @staticmethod
    def _parse_range_min(range_text: str, default: int) -> int:
        """TODO: add documentation."""
        try:
            parts = [int(part) for part in range_text.split() if part.strip()]
            return parts[0] if parts else default
        except ValueError:
            return default


config_manager = ConfigManager()
