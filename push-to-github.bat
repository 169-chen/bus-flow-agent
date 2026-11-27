@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   Push "bus-flow-agent" to GitHub
echo ============================================
echo.
set /p REPO_URL="Paste the repo URL from browser address bar, then press Enter: "
set "REPO_URL=%REPO_URL: =%"
if "%REPO_URL:~-1%"=="/" set "REPO_URL=%REPO_URL:~0,-1%"
if /i not "%REPO_URL:~-4%"==".git" set "REPO_URL=%REPO_URL%.git"
echo.
echo Remote address: %REPO_URL%
echo.

echo [1/3] Switching branch to main...
git branch -M main

echo [2/3] Setting remote...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo [3/3] Pushing code... A login window may pop up.
echo.
echo   If asked for Username:  type 169-chen
echo   If asked for Password:  paste your Personal Access Token
echo                           (starts with ghp_, NOT your account password)
echo.
echo ============================================
echo.
git push -u origin main

echo.
echo -------- Done --------
echo Check your repo page in the browser now.
echo.
pause
