@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   Push "bus-flow-agent" to GitHub
echo ============================================
echo.
echo Repo: https://github.com/169-chen/------
echo.
echo No need to type anything. Just wait for the login window.
echo.

echo [1/3] Switching branch to main...
git branch -M main

echo [2/3] Setting remote...
git remote remove origin 2>nul
git remote add origin https://github.com/169-chen/------.git

echo.
echo [3/3] Pushing code... A login window may pop up.
echo.
echo   If asked for Username:  type  169-chen
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
