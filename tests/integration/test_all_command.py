"""TODO: add documentation."""

import os
from unittest.mock import Mock, patch

import pytest

import jmeter_test_suite.application.services.sync_execution_service as sync_module
from jmeter_test_suite.application.services.sync_execution_service import (
    SyncExecutionService,
)
from jmeter_test_suite.infrastructure.config import config_manager
from jmeter_test_suite.interfaces.cli.main import handle_all_command


@pytest.fixture
def temp_output_dir(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    yield str(output_dir)


@pytest.fixture
def mock_jmx_file(tmp_path):
    jmx_file = tmp_path / "test_plan.jmx"
    jmx_file.write_text("test-plan", encoding="utf-8")
    return str(jmx_file)


@pytest.fixture
def mock_server_config():
    return {"server": "127.0.0.1", "user": "tester", "password": "secret"}


class TestAllCommand:
    """TODO: add documentation."""

    @patch("jmeter_test_suite.interfaces.cli.main.SyncExecutionService")
    @patch("jmeter_test_suite.interfaces.cli.main.handle_report_command")
    def test_all_command_basic_execution(
        self,
        mock_report_command,
        mock_sync_service,
        temp_output_dir,
        mock_jmx_file,
        mock_server_config,
    ):
        """TODO: add documentation."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_report_command.return_value = 0

        # 模拟Execute结果
        mock_result = {
            "success": True,
            "sync_status": "success",
            "jmeter": {"success": True, "message": "testcommandExecute成功"},
            "nmon": {"success": True, "message": "nmon监控成功"},
            "total_duration": 120.5,
            "status": "completed",
        }
        mock_service_instance.execute_batch_sync_test.return_value = mock_result

        # 准备command行Args
        args = [
            mock_jmx_file,
            "--server",
            mock_server_config["server"],
            "--user",
            mock_server_config["user"],
            "--password",
            mock_server_config["password"],
            "--output",
            temp_output_dir,
        ]

        # Executeallcommand
        result = handle_all_command(args)

        # 验证结果
        assert result == 0  # 成功Exit code
        mock_service_instance.execute_batch_sync_test.assert_called_once()

        # 验证调用Args
        call_args = mock_service_instance.execute_batch_sync_test.call_args
        args, kwargs = call_args
        assert args[0] == mock_jmx_file
        assert args[1] == mock_server_config["server"]
        assert args[2] == mock_server_config["user"]
        assert args[3] == mock_server_config["password"]
        assert args[4] == temp_output_dir
        assert kwargs == {}

    @patch("jmeter_test_suite.interfaces.cli.main.SyncExecutionService")
    @patch("jmeter_test_suite.interfaces.cli.main.handle_report_command")
    def test_all_command_jmeter_failure(
        self,
        mock_report_command,
        mock_sync_service,
        temp_output_dir,
        mock_jmx_file,
        mock_server_config,
    ):
        """TODO: add documentation."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_report_command.return_value = 0

        # 模拟JMeter失败的结果
        mock_result = {
            "success": False,
            "sync_status": "partial_failed",
            "jmeter": {"success": False, "error": "JMeter执行失败"},
            "nmon": {"success": True, "message": "nmon监控成功"},
            "total_duration": 60.0,
            "status": "completed",
        }
        mock_service_instance.execute_batch_sync_test.return_value = mock_result

        args = [
            mock_jmx_file,
            "--server",
            mock_server_config["server"],
            "--user",
            mock_server_config["user"],
            "--password",
            mock_server_config["password"],
            "--output",
            temp_output_dir,
        ]

        # Executeallcommand
        result = handle_all_command(args)

        # 验证失败Exit code
        assert result == 1  # 失败退出码

    @patch("jmeter_test_suite.interfaces.cli.main.SyncExecutionService")
    @patch("jmeter_test_suite.interfaces.cli.main.handle_report_command")
    def test_all_command_nmon_failure(
        self,
        mock_report_command,
        mock_sync_service,
        temp_output_dir,
        mock_jmx_file,
        mock_server_config,
    ):
        """TODO: add documentation."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_report_command.return_value = 0

        # 模拟nmon失败的结果
        mock_result = {
            "success": False,
            "sync_status": "partial_failed",
            "jmeter": {"success": True, "message": "testcommandExecute成功"},
            "nmon": {"success": False, "error": "nmon监控失败"},
            "total_duration": 120.0,
            "status": "completed",
        }
        mock_service_instance.execute_batch_sync_test.return_value = mock_result

        args = [
            mock_jmx_file,
            "--server",
            mock_server_config["server"],
            "--user",
            mock_server_config["user"],
            "--password",
            mock_server_config["password"],
            "--output",
            temp_output_dir,
        ]

        # Executeallcommand
        result = handle_all_command(args)

        # 验证失败Exit code
        assert result == 1  # 失败Exit code

    def test_all_command_invalid_arguments(self):
        """TODO: add documentation."""
        with pytest.raises(SystemExit):
            handle_all_command([])

        # 测试无效的JMX文件
        args = [
            "invalid.jmx",
            "--server",
            "192.168.1.1",
            "--user",
            "test",
            "--password",
            "test",
        ]
        result = handle_all_command(args)
        assert result == 1  # 应该失败

    @patch("jmeter_test_suite.interfaces.cli.main.SyncExecutionService")
    @patch("jmeter_test_suite.interfaces.cli.main.handle_report_command")
    def test_all_command_timeout_handling(
        self,
        mock_report_command,
        mock_sync_service,
        temp_output_dir,
        mock_jmx_file,
        mock_server_config,
    ):
        """TODO: add documentation."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_report_command.return_value = 0

        # 模拟超时异常
        mock_service_instance.execute_batch_sync_test.side_effect = TimeoutError(
            "Execute超时"
        )

        args = [
            mock_jmx_file,
            "--server",
            mock_server_config["server"],
            "--user",
            mock_server_config["user"],
            "--password",
            mock_server_config["password"],
            "--output",
            temp_output_dir,
        ]

        # Executeallcommand
        result = handle_all_command(args)

        # 验证超时失败Exit code
        assert result == 1  # 失败Exit code


class TestSyncExecutionService:
    """TODO: add documentation."""

    @patch("jmeter_test_suite.application.services.sync_execution_service.NmonService")
    def test_execute_batch_sync_test_success(
        self, mock_nmon_service, temp_output_dir, monkeypatch
    ):
        """TODO: add documentation."""
        # 模拟nmon服务
        mock_nmon_instance = Mock()
        mock_nmon_service.return_value = mock_nmon_instance

        # 模拟nmon监控成功
        mock_monitor = Mock()
        mock_nmon_instance.execute_monitoring_with_entity.return_value = mock_monitor
        mock_nmon_instance.ssh_adapter = Mock()
        mock_nmon_instance.ssh_adapter.stop_nmon_monitoring = Mock()
        mock_nmon_instance.ssh_adapter.download_nmon_file.return_value = True
        mock_nmon_instance.ssh_adapter.ssh_client = Mock()

        monkeypatch.setattr(config_manager, "get_result_dir", lambda: temp_output_dir)
        monkeypatch.setattr(
            config_manager, "get_server_logs_config", lambda: {"enabled": False}
        )

        cli_mock = Mock(return_value=0)
        monkeypatch.setattr(sync_module, "CLI_HANDLE_TEST_COMMAND", cli_mock)
        monkeypatch.setattr(sync_module, "handle_test_command", cli_mock)

        service = SyncExecutionService()

        # Execute测试
        result = service.execute_batch_sync_test(
            jmx_file="data/test_plans/08_device_mqtt.jmx",
            server="192.168.24.45",
            user="user",
            password="qwer1234",
            output_dir=temp_output_dir,
        )

        # 验证结果
        assert result["success"] is True
        assert result["sync_status"] == "success"
        assert result["jmeter"]["success"] is True
        assert result["nmon"]["success"] is True
        assert result["status"] == "completed"

        # 验证调用
        cli_mock.assert_called_once()
        mock_nmon_instance.execute_monitoring_with_entity.assert_called_once()

    def test_archive_old_results(self, temp_output_dir, monkeypatch):
        """TODO: add documentation."""
        test_files = ["test1.jtl", "test2.nmon", "test3.xlsx"]
        for filename in test_files:
            file_path = os.path.join(temp_output_dir, filename)
            with open(file_path, "w") as f:
                f.write("test content")

        monkeypatch.setattr(config_manager, "get_result_dir", lambda: temp_output_dir)
        service = SyncExecutionService()

        # ExecuteArchive
        service._archive_old_results(temp_output_dir)

        # 验证文件被Move到old目录
        old_dir = os.path.join(temp_output_dir, "old")
        assert os.path.exists(old_dir)

        for filename in test_files:
            old_file_path = os.path.join(old_dir, filename)
            assert os.path.exists(old_file_path)

        # 验证原目录为空
        remaining_files = os.listdir(temp_output_dir)
        assert len(remaining_files) == 1  # 只有old目录


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
