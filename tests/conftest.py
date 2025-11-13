"""TODO: add documentation."""

import shutil
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

try:
    from jmeter_test_suite.infrastructure.adapters.ssh_adapter import SSHAdapter
except Exception:  # pragma: no cover - 确保测试环境不会因依赖缺失崩溃
    SSHAdapter = Mock  # type: ignore[assignment]


@pytest.fixture(scope="session")
def project_root() -> Path:
    """TODO: add documentation."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def src_directory(project_root: Path) -> Path:
    """TODO: add documentation."""
    return project_root / "src"


@pytest.fixture(scope="session")
def data_directory(project_root: Path) -> Path:
    """TODO: add documentation."""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """TODO: add documentation."""
    temp_path = Path(tempfile.mkdtemp(prefix="jmeter-test-suite-"))
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_jmx_file(data_directory: Path) -> str:
    """TODO: add documentation."""
    path = data_directory / "sample.jmx"
    path.write_text("<jmeterTestPlan />", encoding="utf-8")
    return str(path)


@pytest.fixture
def mock_server_config() -> dict[str, str]:
    """TODO: add documentation."""
    return {
        "host": "127.0.0.1",
        "port": "22",
        "user": "root",
        "password": "1",
    }


@pytest.fixture
def mock_jmeter_config() -> dict[str, str]:
    """TODO: add documentation."""
    return {
        "result_dir": "./result",
        "test_plans_dir": "./src/jmeter_test_suite/infrastructure/config/test_plans",
        "thread_range": "100 700 300",
        "loop_range": "300 1000 200",
    }


@pytest.fixture
def mock_nmon_config() -> dict[str, str]:
    """TODO: add documentation."""
    return {"user": "root", "password": "1", "interval": 5, "count": 60}


@pytest.fixture
def mock_test_result() -> dict[str, float]:
    """TODO: add documentation."""
    return {
        "total_samples": 1_000,
        "successful_samples": 950,
        "failed_samples": 50,
        "tps": 100.5,
        "avg_response_time": 50.2,
        "max_response_time": 200.0,
        "error_rate": 5.0,
    }


@pytest.fixture
def mock_nmon_result() -> dict[str, float]:
    """TODO: add documentation."""
    return {
        "cpu_usage_avg": 45.5,
        "memory_usage_avg": 65.2,
        "disk_io_avg": 30.8,
        "network_io_avg": 25.6,
        "nmon_file": "test_session_12345.nmon",
    }


@pytest.fixture
def mock_sync_result(
    mock_test_result: dict[str, float], mock_nmon_result: dict[str, float]
) -> dict[str, object]:
    """TODO: add documentation."""
    return {
        "sync_status": "success",
        "jmeter": {"success": True, "message": "testcommandExecuteSuccess"},
        "nmon": {"success": True, "message": "nmonMonitorSuccess"},
        "test_result": mock_test_result,
        "nmon_result": mock_nmon_result,
        "total_duration": 120.5,
        "status": "completed",
    }


@pytest.fixture
def mock_ssh_client() -> Mock:
    """TODO: add documentation."""
    client = Mock()
    client.exec_command.return_value = (Mock(), Mock(), Mock())
    client.close.return_value = None
    return client


@pytest.fixture
def mock_ssh_adapter(mock_ssh_client: Mock) -> SSHAdapter:
    """TODO: add documentation."""
    adapter = SSHAdapter()
    adapter.ssh_client = mock_ssh_client
    adapter.connected = True
    with patch.object(adapter, "disconnect", return_value=None):
        yield adapter


def pytest_configure(config: pytest.Config) -> None:
    """TODO: add documentation."""
    config.addinivalue_line("markers", "e2e: end-to-end test marker")
    config.addinivalue_line("markers", "slow: slow test marker")
    try:
        if config.getoption("--html"):
            config.option.htmlpath = "test_report.html"
    except ValueError:
        # --html 未启用时忽略
        pass


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """TODO: add documentation."""
    _ = config  # 保留参数，方便后续扩展
    for item in items:
        node_id = item.nodeid
        test_name = item.name
        if "tests/integration" in node_id:
            item.add_marker(pytest.mark.integration)
        if "tests/unit" in node_id:
            item.add_marker(pytest.mark.unit)
        if "slow" in test_name or "timeout" in test_name:
            item.add_marker(pytest.mark.slow)
