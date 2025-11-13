"""TODO: add documentation."""

from __future__ import annotations

from unittest.mock import Mock, patch


@patch("jmeter_test_suite.interfaces.cli.main.config_manager")
@patch("jmeter_test_suite.interfaces.cli.main.open_file_manager", return_value=True)
def test_handle_open_result_command_success(mock_open: Mock, mock_config: Mock) -> None:
    """TODO: add documentation."""
    from jmeter_test_suite.interfaces.cli.main import handle_open_result_command

    mock_config.get_result_dir.return_value = "./result"
    assert handle_open_result_command([]) == 0
    mock_open.assert_called_once_with("./result")


@patch("jmeter_test_suite.interfaces.cli.main.config_manager")
@patch("jmeter_test_suite.interfaces.cli.main.open_file_manager", return_value=False)
def test_handle_open_result_command_failure(mock_open: Mock, mock_config: Mock) -> None:
    """TODO: add documentation."""
    from jmeter_test_suite.interfaces.cli.main import handle_open_result_command

    mock_config.get_result_dir.return_value = "./result"
    assert handle_open_result_command([]) == 1
    mock_open.assert_called_once_with("./result")
