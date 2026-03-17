@echo off
REM ============================================================
REM CRM Lead Audit Automation - Windows Batch Script
REM ============================================================
REM 
REM This script runs the CRM Lead Audit automation on Windows
REM 
REM Usage: run_lead_audit.bat
REM ============================================================

ECHO ============================================================
ECHO CRM Lead Audit Automation
ECHO Starting: %date% %time%
ECHO ============================================================

REM Change to script directory
cd /d %~dp0

REM Activate virtual environment
ECHO Activating virtual environment...
call venv\Scripts\activate.bat

IF %ERRORLEVEL% NEQ 0 (
    ECHO ERROR: Failed to activate virtual environment
    ECHO Make sure you have run: python -m venv venv
    PAUSE
    EXIT /B 1
)

REM Run the automation script
ECHO Running lead audit automation...
python lead_audit_automation.py

IF %ERRORLEVEL% NEQ 0 (
    ECHO ERROR: Script execution failed
    ECHO Check logs in: logs\lead_audit_%date:~-4%%date:~4,2%%date:~7,2%.log
    deactivate
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO ============================================================
ECHO Automation completed successfully
ECHO Finished: %date% %time%
ECHO ============================================================

REM Deactivate virtual environment
deactivate

REM Uncomment to pause at the end (useful for debugging)
REM PAUSE

EXIT /B 0
