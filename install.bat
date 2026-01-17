@echo off
REM Installation script for Egile MCP Reporter (Windows)

echo ========================================
echo Egile MCP Reporter - Installation
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo Installing egile-mcp-reporter...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install egile-mcp-reporter
    pause
    exit /b 1
)

echo.
echo ========================================
echo Additional Dependencies
echo ========================================
echo.
echo For PDF generation, you need GTK3 runtime on Windows.
echo Install via Chocolatey:
echo   choco install gtk-runtime
echo.
echo Or download the installer from:
echo   https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
echo.
echo For chart generation, install kaleido:
echo   pip install kaleido
echo.

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To test the installation:
echo   python example.py
echo.
echo This will create sample reports in the 'reports' directory.
echo.
pause
