@echo off
title Push Pure Python Server to GitHub
color 0B
cd /d "%~dp0"

echo =====================================================================
echo          PUSH PURE PYTHON SERVER TO GITHUB REPOSITORY
echo =====================================================================
echo.
echo This script will package and push the pure_python_server_all_interval folder
echo to a new GitHub repository so you can deploy to Render.com or backup.
echo.

:: 1. Check if git is available
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not in your PATH.
    echo Please install Git for Windows from https://git-scm.com/
    pause
    exit /b 1
)

:: 2. Check Git User Identity
git config --get user.name >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Git user identity is not set. Please provide:
    set /p GIT_NAME="Enter your Name or GitHub Username: "
    set /p GIT_EMAIL="Enter your GitHub Email: "
    if not "%GIT_NAME%"=="" git config user.name "%GIT_NAME%"
    if not "%GIT_EMAIL%"=="" git config user.email "%GIT_EMAIL%"
)

:: 3. Initialize Git if needed
if not exist ".git" (
    echo Initializing new Git repository...
    git init
    git branch -M main
)

:: 4. Add files and Commit
echo Adding files to Git staging...
git add .
git commit -m "Update pure python market server: multi-timeframe intervals, custom stocks, and 1-click launcher"

:: 5. Check or Set Remote URL
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo =====================================================================
    echo No GitHub remote URL configured yet.
    echo Create a new repository on GitHub (e.g. https://github.com/new)
    echo Then paste your repository URL below.
    echo =====================================================================
    echo.
    set /p REPO_URL="Enter GitHub Repository URL (e.g. https://github.com/username/server.git): "
    if "%REPO_URL%"=="" (
        echo [ERROR] No URL entered. Aborted.
        pause
        exit /b 1
    )
    git remote add origin "%REPO_URL%"
) else (
    echo.
    echo Existing remote found:
    git remote -v
)

:: 6. Push to GitHub
echo.
echo Pushing changes to GitHub main branch...
echo (A GitHub login window may appear if you are not already logged in)
echo.
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo =====================================================================
    echo [SUCCESS] Your repository has been updated on GitHub!
    echo.
    echo If connected to Render.com, Render will automatically detect the
    echo new commit and deploy the updated server in ~2 minutes!
    echo =====================================================================
) else (
    echo.
    echo [NOTE] Push completed with status code %ERRORLEVEL%.
    echo If this failed due to permission or authentication, ensure you have
    echo rights to push to this repository or check your GitHub personal token.
)

echo.
pause
