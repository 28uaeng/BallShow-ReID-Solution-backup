@echo off
setlocal

echo ========================================================
echo       Git Repository Initialization Script
echo ========================================================

:: 1. Check if .git exists and remove it
if exist ".git" (
    echo [INFO] Removing existing .git directory...
    rmdir /s /q .git
) else (
    echo [INFO] No existing .git directory found.
)

:: 2. Initialize new git repository
echo [INFO] Initializing new Git repository...
git init

:: 3. Add all files
echo [INFO] Adding files to staging area...
git add .

:: 4. Create initial commit
echo [INFO] Creating initial commit...
git commit -m "Initial commit: BallShow ReID solution based on TransReID"

:: 5. Ask for remote URL
echo.
echo ========================================================
echo Please paste your new GitHub repository URL below:
echo (e.g., https://github.com/yourname/your-repo.git)
echo ========================================================
set /p REMOTE_URL="Repository URL: "

if "%REMOTE_URL%"=="" (
    echo [ERROR] No URL provided. Exiting.
    goto :end
)

:: 6. Add remote and push
echo [INFO] Adding remote origin...
git remote add origin %REMOTE_URL%

echo [INFO] Pushing to main branch...
git branch -M main
git push -u origin main

echo.
echo ========================================================
echo [SUCCESS] Project successfully pushed to GitHub!
echo ========================================================

:end
pause
