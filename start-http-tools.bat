@echo off
REM 启动 n8n HTTP Tools 服务
REM 这个服务为 n8n 工作流提供 HTTP API 接口

echo ====================================
echo 启动 n8n HTTP Tools 服务...
echo ====================================
echo.

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0

REM 切换到脚本目录
cd /d "%SCRIPT_DIR%"

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3.7 或更高版本
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 安装依赖失败
    pause
    exit /b 1
)

REM 启动服务
echo 正在启动服务...
echo.
python n8n-http-tools.py

REM 如果服务退出，暂停以便查看错误信息
if errorlevel 1 (
    echo.
    echo 服务启动失败
    pause
)

