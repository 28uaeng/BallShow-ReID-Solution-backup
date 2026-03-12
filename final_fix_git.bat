@echo off
setlocal

echo ========================================================
echo       Final Git Repository Reset & Push Script
echo ========================================================

cd /d "%~dp0"

:: 1. Remove dirty .git directory
echo [INFO] Removing .git directory to clear all history...
if exist ".git" (
    rmdir /s /q .git
)

:: 2. Initialize fresh
echo [INFO] Initializing fresh Git repository...
git init

:: 3. Ensure .gitignore is correct
echo [INFO] Verifying .gitignore...
findstr /C:"*.pth" .gitignore >nul
if %errorlevel% neq 0 (
    echo *.pth>> .gitignore
    echo [INFO] Added *.pth to .gitignore
)
findstr /C:"weights/" .gitignore >nul
if %errorlevel% neq 0 (
    echo weights/>> .gitignore
    echo [INFO] Added weights/ to .gitignore
)

:: 4. Add files (large files will be ignored now)
echo [INFO] Adding files...
git add .

:: 5. Commit
echo [INFO] Creating initial commit...
git commit -m "Initial commit (Clean version without large weights)"

:: 6. Set branch and remote
echo [INFO] Setting main branch...
git branch -M main

echo.
echo ========================================================
echo Please paste your GitHub repository URL again:
echo (e.g., https://github.com/28uaeng/BallShow-ReID-Solution.git)
echo ========================================================
set /p REMOTE_URL="Repository URL: "

if "%REMOTE_URL%"=="" (
    echo [ERROR] No URL provided. Exiting.
    goto :end
)

echo [INFO] Adding remote origin...
git remote add origin %REMOTE_URL%

echo [INFO] Force pushing to GitHub...
git push -u origin main --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo [SUCCESS] Successfully pushed clean project to GitHub!
    echo ========================================================
) else (
    echo.
    echo [ERROR] Push failed.
)

:end
pause
