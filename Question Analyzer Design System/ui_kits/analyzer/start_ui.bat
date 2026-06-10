@echo off
echo Starting Question Analyzer UI Server...
echo.
echo The UI will be available at: http://localhost:8080/ui_kits/analyzer/
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0..\.."
python -m http.server 8080

@REM Made with Bob
