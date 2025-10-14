@echo off
REM n8ntools Windows批处理包装器
REM 自动使用Python运行n8ntools.py

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0

REM 调用Python脚本，传递所有参数
python "%SCRIPT_DIR%n8ntools.py" %*

