@echo off
chcp 65001 >nul
REM JMeter Test Suite v3.0 - All Interfaces Batch Script
REM Double-click to run all interfaces automatically

REM Simple interrupt handler - kill all processes on exit
if not "%1"=="cleanup" (
    echo Press Ctrl+C anytime to stop all tests and cleanup processes
    echo.
)

echo ====================================
echo   JMeter Test Suite v3.0 - All Interfaces
echo ====================================
echo.
echo Auto-running all 9 interfaces:
echo    1. Check Python environment
echo    2. Install dependencies  
echo    3. Run tests for all interfaces
echo    4. Generate individual Excel reports
echo    5. Generate summary report

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.12+ first
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python OK
python --version

echo.
echo Checking and installing dependencies...

REM Set Python path
set PYTHONPATH=%~dp0src;%PYTHONPATH%

REM Check if project is already installed
python -c "import jmeter_test_suite; print('Project already installed')" >nul 2>&1
if %errorlevel% equ 0 (
    echo Project package already installed
    goto deps_done
)

echo Installing dependencies (first time setup)...

REM Install dependencies with progress indication
echo    Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

echo    Installing Python packages...
python -m pip install -e .[dev] >nul 2>&1
if %errorlevel% neq 0 (
    echo    Using China mirror for faster download...
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -e .[dev] >nul 2>&1
)

echo Dependencies installed successfully

:deps_done

echo.
echo Reading test configuration...

REM Get config info using Python (read from correct config path)
for /f "delims=" %%i in ('python -c "import yaml; import sys; f=open('src/jmeter_test_suite/infrastructure/config/jmeter_config.yaml','r',encoding='utf-8'); config=yaml.safe_load(f); f.close(); thread_range=config.get('thread_range','10 50 20'); loop_range=config.get('loop_range','3 10 2'); nmon_server=config.get('nmon',{}).get('server','192.168.24.45'); nmon_user=config.get('nmon',{}).get('user','root'); nmon_password=config.get('nmon',{}).get('password','1'); print('THREAD_RANGE=' + thread_range); print('LOOP_RANGE=' + loop_range); print('NMON_SERVER=' + nmon_server); print('NMON_USER=' + nmon_user); print('NMON_PASSWORD=' + nmon_password); thread_parts=thread_range.split(); loop_parts=loop_range.split(); thread_count=len(range(int(thread_parts[0]),int(thread_parts[1])+1,int(thread_parts[2]))) if len(thread_parts)==3 else 3; loop_count=len(range(int(loop_parts[0]),int(loop_parts[1])+1,int(loop_parts[2]))) if len(loop_parts)==3 else 4; total_rounds=thread_count*loop_count; print('ROUNDS_PER_INTERFACE=' + str(total_rounds)); print('TOTAL_ROUNDS=' + str(total_rounds*9)); print('ESTIMATED_TIME=' + str(total_rounds*9*4) + '-' + str(total_rounds*9*8) + ' minutes')"') do (
    for /f "tokens=1,2 delims==" %%a in ("%%i") do (
        if "%%a"=="THREAD_RANGE" set THREAD_RANGE=%%b
        if "%%a"=="LOOP_RANGE" set LOOP_RANGE=%%b
        if "%%a"=="NMON_SERVER" set NMON_SERVER=%%b
        if "%%a"=="NMON_USER" set NMON_USER=%%b
        if "%%a"=="NMON_PASSWORD" set NMON_PASSWORD=%%b
        if "%%a"=="ROUNDS_PER_INTERFACE" set ROUNDS_PER_INTERFACE=%%b
        if "%%a"=="TOTAL_ROUNDS" set TOTAL_ROUNDS=%%b
        if "%%a"=="ESTIMATED_TIME" set ESTIMATED_TIME=%%b
    )
)

echo Thread range: %THREAD_RANGE%
echo Loop range: %LOOP_RANGE%
echo Test rounds per interface: %ROUNDS_PER_INTERFACE% rounds
echo Total test rounds: %TOTAL_ROUNDS% rounds (9 interfaces)
echo Estimated total time: %ESTIMATED_TIME%

echo.
echo Preparing temporary data folder...
if exist result\temp (
    del /q result\temp\*.* >nul 2>&1
    echo temp folder cleaned
) else (
    mkdir result\temp >nul 2>&1
    echo temp folder created
)

echo.
echo Starting batch tests for all 9 interfaces...
echo This will take several hours, please be patient...
echo Progress will be shown below...

REM List of all interfaces
set INTERFACES=01_register 02_device_strategy 03_device_name 04_device_mode 05_device_vendor 06_device_protect 07_device_logo 08_device_mqtt 09_device_heartbeat

set INTERFACE_COUNT=0
set SUCCESS_COUNT=0
set FAILED_COUNT=0

for %%i in (%INTERFACES%) do (
    set /a INTERFACE_COUNT+=1
    echo.
    echo ============================================================
    echo Interface: %%i
    echo ============================================================
    
    REM Update config to use current interface
    python update_config.py %%i
    
    REM Run the test
    echo Running tests for %%i...
    python -m jmeter_test_suite all
    
    if %errorlevel% equ 0 (
        set /a SUCCESS_COUNT+=1
        echo Interface %%i completed successfully
        
        REM Save current interface data to temp folder
        echo Saving interface %%i data to temp folder...
        copy result\%%i*.jtl result\temp\ >nul 2>&1
        copy result\nmon_%%i*.nmon result\temp\ >nul 2>&1
        echo Interface %%i data saved to temp
    ) else (
        set /a FAILED_COUNT+=1
        echo Interface %%i failed
    )
    
    echo Current interface %%i completed
)

echo.
echo ============================================================
echo Batch execution completed!
echo ============================================================
echo Final Summary:
echo    Total interfaces: 9
echo    Successful: %SUCCESS_COUNT%
echo    Failed: %FAILED_COUNT%
echo    Success rate: 
python -c "print(f'{%SUCCESS_COUNT% * 100 / 9:.1f}%%')"

if %SUCCESS_COUNT% gtr 0 (
    echo.
    echo Generated reports in result/ folder:
    dir result\beautiful_test_report_*.xlsx /b 2>nul
    
    echo.
    echo Generating summary report for all interfaces...
    echo Based on accumulated data from %SUCCESS_COUNT% interfaces in temp folder
    
    REM Switch to result directory temporarily
    cd result
    python -m jmeter_test_suite report temp
    cd ..
    
    echo Summary report generated in result directory
    
    if %errorlevel% equ 0 (
        echo Summary report generated successfully!
        dir result\beautiful_test_report_all_interfaces_*.xlsx /b 2>nul
    ) else (
        echo Summary report generation failed, but individual reports are not affected
    )
    
    echo.
    echo Opening result folder...
    start explorer result
)

echo.
echo ====================================
echo   JMeter Test Suite v3.0 Completed
echo ====================================
echo.
echo Batch tests completed
if %SUCCESS_COUNT% gtr 0 (
    echo Excel reports generated
    echo Result folder opened
)

echo.
echo Individual reports: beautiful_test_report_[interface]_*.xlsx
echo To modify test parameters, edit: src/jmeter_test_suite/infrastructure/config/jmeter_config.yaml
echo See detailed guide: Configuration_Guide.txt
echo.
echo.
echo Restoring original configuration...
python update_config.py restore

echo.
echo Cleaning temporary data folder...
if exist result\temp (
    del /q result\temp\*.* >nul 2>&1
    echo temp folder cleaned
)

echo To run again, double-click this script
echo Technical support: nighm@sina.com
echo.

REM Simple cleanup on exit
echo Cleaning up processes...
taskkill /f /im jmeter.bat >nul 2>&1
taskkill /f /im java.exe >nul 2>&1
plink -ssh %NMON_SERVER% -l %NMON_USER% -pw %NMON_PASSWORD% "pkill -f nmon" >nul 2>&1
echo Cleanup completed

echo Press any key to exit...
pause >nul