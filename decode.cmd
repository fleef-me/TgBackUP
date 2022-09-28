@echo off

setlocal EnableExtensions DisableDelayedExpansion

echo %CMDCMDLINE% | find /I "%~0" >nul 2>&1

if [%ERRORLEVEL%] equ [0] (
    set "interactive=0"
) else (
    set "interactive=1"
)

set "begin=setlocal"
set "end=goto :end"

goto :main

:end
endlocal & exit /B %ERRORLEVEL%

:run
%begin%
    pushd %~dp0
    chcp 65001 >nul

    set PYTHONUTF8=1
    set PYTHONIOENCODING=utf-8

    py -3 -c "import sys; assert sys.version_info >= (3, 7)" >nul 2>&1

    if [%ERRORLEVEL%] neq [0] (
        echo ERROR: get Python ^>=3.7 first>&2
        set "ERRORLEVEL=1" & goto :end
    )

    py -3 src/decode.py
%end%

:main
%begin%
    call :run

    if [%interactive%] equ [0] (
        pause
    )
%end%
