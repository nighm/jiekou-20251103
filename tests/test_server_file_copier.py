"""TODO: add documentation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from tools.server_file_copier import CopyTask, ProgressTracker, ServerFileCopier


@pytest.fixture
def copier(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ServerFileCopier:
    """TODO: add documentation."""
    mock_config = Mock()
    mock_config.get_result_dir.return_value = str(tmp_path)
    mock_config.get.side_effect = lambda _section, default=None: default
    monkeypatch.setattr("tools.server_file_copier.config_manager", mock_config)
    instance = ServerFileCopier()
    instance.resume_dir = tmp_path / "resume"
    instance.resume_dir.mkdir(exist_ok=True)
    return instance


def test_copy_task_defaults() -> None:
    """TODO: add documentation."""
    task = CopyTask(remote_path="/remote", local_path=Path("local"))
    assert task.status == "pending"
    task.mark_success()
    assert task.status == "completed"


def test_progress_tracker_add_and_update() -> None:
    """TODO: add documentation."""
    tracker = ProgressTracker()
    task = CopyTask(remote_path="/remote", local_path=Path("local"))
    tracker.add_task("job", task)
    tracker.update_progress("job", 512)
    tracker.update_status("job", "running")
    assert tracker.tasks["job"].copied_size == 512
    assert tracker.tasks["job"].status == "running"


@patch("tools.server_file_copier.paramiko.SSHClient")
@patch("tools.server_file_copier.SCPClient")
def test_connect_success(
    mock_scp: Mock, mock_ssh: Mock, copier: ServerFileCopier
) -> None:
    """TODO: add documentation."""
    ssh_client = Mock()
    ssh_client.get_transport.return_value = Mock()
    mock_ssh.return_value = ssh_client
    mock_scp.return_value = Mock()
    assert copier.connect() is True
    assert copier.connected is True


def test_list_remote_files_without_connection(copier: ServerFileCopier) -> None:
    """TODO: add documentation."""
    assert copier.list_remote_files("/tmp") == []
