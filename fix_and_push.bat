@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo       Git Large File Fix & Push Script
echo ========================================================

cd /d "%~dp0"

echo [INFO] Soft resetting to remove large file from commit...
git reset --soft HEAD~1

echo [INFO] Clearing git cache...
git rm -r --cached .

echo [INFO] Re-adding files (respecting new .gitignore)...
git add .

echo [INFO] Creating new commit without large weights...
git commit -m "Initial commit (excluding large weights)"

echo [INFO] Force pushing to GitHub...
git push -u origin main --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo [SUCCESS] Fixed and pushed successfully!
    echo ========================================================
) else (
    echo.
    echo [ERROR] Push failed. Please check your network or credentials.
)

pause
