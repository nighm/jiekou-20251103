"""TODO: add documentation."""

from pathlib import Path

from jmeter_test_suite.infrastructure.config.config_manager import ConfigManager


def test_config_manager_defaults(tmp_path: Path) -> None:
    """TODO: add documentation."""
    manager = ConfigManager(tmp_path / "nonexistent.yaml")
    assert manager.get("thread_range") is None
    assert manager.get_nmon_config() == {}
    assert manager.get_result_dir()
