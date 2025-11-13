@echo on
chcp 65001
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%src;%PYTHONPATH%"

echo ====================================
echo   JMeter Test Suite v3.0 One-Click
echo ====================================
echo.
echo 当前执行入口: 一键运行-单个接口.bat
echo 内部流程由 Python 模块统一处理，日志将保存至 logs 目录
echo.

python -m jmeter_test_suite.infrastructure.scripts.one_click_single
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo 执行完成，退出码: %EXIT_CODE%
if not "%EXIT_CODE%"=="0" (
    echo ⚠️ 任务执行失败，请查看 logs 目录中的最新日志文件
) else (
    echo ✅ 任务执行成功
)

echo.
echo 按任意键退出...
pause
exit /b %EXIT_CODE%
