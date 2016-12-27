@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
IF %SCRIPT_DIR:~-1%==\ set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
pushd "%SCRIPT_DIR%/tests"
python -m unittest discover -s "%SCRIPT_DIR%/tests" -p "test*.py"
popd