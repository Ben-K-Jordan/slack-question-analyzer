@echo off
echo ============================================================
echo Slack Question Analyzer - Test Suite
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/4] Testing Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo.

echo [2/4] Testing syntax...
python test_syntax.py
if errorlevel 1 (
    echo ERROR: Syntax test failed!
    pause
    exit /b 1
)
echo.

echo [3/4] Testing CLI help...
python -m src.cli --help
if errorlevel 1 (
    echo ERROR: CLI test failed!
    pause
    exit /b 1
)
echo.

echo [4/4] Validating example input...
python -m src.cli validate example_input.txt
if errorlevel 1 (
    echo ERROR: Validation test failed!
    pause
    exit /b 1
)
echo.

echo ============================================================
echo ALL TESTS PASSED!
echo ============================================================
echo.
echo Next steps:
echo 1. Install dependencies: pip install -r requirements.txt
echo 2. Install Ollama: https://ollama.ai/download
echo 3. Pull model: ollama pull nomic-embed-text
echo 4. Run analysis: python -m src.cli analyze example_input.txt
echo.
pause

@REM Made with Bob
