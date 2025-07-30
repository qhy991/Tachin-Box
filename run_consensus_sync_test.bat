@echo off
echo ===========================================
echo   共识角度同步系统测试启动器
echo ===========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo Python版本:
python --version

echo.
echo 正在启动共识角度同步系统测试...
echo.

REM 运行测试脚本
python test_consensus_angle_sync.py

echo.
echo 测试结束，按任意键退出...
pause 