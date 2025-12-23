@echo off
echo ============================================================
echo GitHub Repository Push Helper
echo ============================================================
echo.

if "%1"=="" (
    echo Usage: push_to_github.bat ^<github_username^> [repository_name]
    echo.
    echo Example: push_to_github.bat myusername discord-selfbot
    echo.
    echo If repository_name is not provided, it will use "discord-selfbot"
    echo.
    pause
    exit /b 1
)

set GITHUB_USER=%1
if "%2"=="" (
    set REPO_NAME=discord-selfbot
) else (
    set REPO_NAME=%2
)

echo Step 1: Creating repository on GitHub...
echo.
echo Please go to: https://github.com/new
echo.
echo Repository name: %REPO_NAME%
echo Visibility: Choose Public or Private
echo IMPORTANT: Do NOT initialize with README, .gitignore, or license
echo.
echo Press any key after you have created the repository...
pause >nul

echo.
echo Step 2: Adding remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git

echo.
echo Step 3: Getting current branch name...
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
if "%BRANCH%"=="" set BRANCH=master

echo Current branch: %BRANCH%
echo.

echo Step 4: Pushing to GitHub...
git push -u origin %BRANCH%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Repository pushed to GitHub
    echo ============================================================
    echo.
    echo Repository URL: https://github.com/%GITHUB_USER%/%REPO_NAME%
    echo.
) else (
    echo.
    echo ============================================================
    echo ERROR: Failed to push to GitHub
    echo ============================================================
    echo.
    echo You may need to:
    echo 1. Authenticate with GitHub (use Personal Access Token)
    echo 2. Set up SSH keys
    echo 3. Use GitHub Desktop
    echo.
    echo You can also manually run:
    echo   git push -u origin %BRANCH%
    echo.
)

pause

