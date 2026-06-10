@echo off
echo ========================================
echo  Slack Question Analyzer - GitHub Push
echo ========================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git for Windows from:
    echo https://git-scm.com/download/win
    echo.
    echo After installing, restart this script.
    pause
    exit /b 1
)

echo Git is installed. Proceeding...
echo.

REM Navigate to project directory
cd /d "%~dp0"

REM Check if already initialized
if exist ".git" (
    echo Git repository already initialized.
    echo.
) else (
    echo Initializing Git repository...
    git init
    echo.
)

REM Get GitHub username
set /p GITHUB_USERNAME="Enter your GitHub username: "
if "%GITHUB_USERNAME%"=="" (
    echo ERROR: GitHub username cannot be empty!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Step 1: Staging files
echo ========================================
git add .
echo Files staged successfully.
echo.

REM Check if there's anything to commit
git diff --cached --quiet
if %ERRORLEVEL% EQU 0 (
    echo No changes to commit. Repository is up to date.
    echo.
) else (
    echo ========================================
    echo  Step 2: Creating commit
    echo ========================================
    git commit -m "Initial commit: Slack Question Analyzer with AI-powered grouping"
    echo Commit created successfully.
    echo.
)

echo ========================================
echo  Step 3: Setting up remote
echo ========================================

REM Check if remote already exists
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Remote 'origin' already exists.
    set /p CHANGE_REMOTE="Do you want to change it? (y/n): "
    if /i "%CHANGE_REMOTE%"=="y" (
        git remote remove origin
        git remote add origin https://github.com/%GITHUB_USERNAME%/slack-question-analyzer.git
        echo Remote updated.
    )
) else (
    git remote add origin https://github.com/%GITHUB_USERNAME%/slack-question-analyzer.git
    echo Remote added: https://github.com/%GITHUB_USERNAME%/slack-question-analyzer.git
)
echo.

echo ========================================
echo  Step 4: Pushing to GitHub
echo ========================================
echo.
echo IMPORTANT: You will be asked for authentication.
echo.
echo If you haven't created the repository yet:
echo 1. Go to https://github.com/new
echo 2. Repository name: slack-question-analyzer
echo 3. Click "Create repository"
echo.
echo For authentication, use a Personal Access Token:
echo 1. Go to: https://github.com/settings/tokens
echo 2. Generate new token (classic)
echo 3. Select 'repo' scope
echo 4. Copy the token
echo 5. Use it as your password when prompted
echo.
pause

git branch -M main
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  SUCCESS!
    echo ========================================
    echo.
    echo Your code has been pushed to GitHub!
    echo.
    echo View it at:
    echo https://github.com/%GITHUB_USERNAME%/slack-question-analyzer
    echo.
) else (
    echo.
    echo ========================================
    echo  Push failed!
    echo ========================================
    echo.
    echo Common issues:
    echo 1. Repository doesn't exist on GitHub - create it first
    echo 2. Authentication failed - use a Personal Access Token
    echo 3. Network issues - check your internet connection
    echo.
    echo See GITHUB_SETUP.md for detailed instructions.
    echo.
)

pause

@REM Made with Bob
