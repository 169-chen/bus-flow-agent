@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   Push "bus-flow-agent" to GitHub
echo ============================================
echo.
set /p GH_USER="Enter your GitHub username (only username, not full URL): "
echo.

echo [1/3] Switching branch to main...
git branch -M main

echo [2/3] Setting remote address...
git remote remove origin 2>nul
git remote add origin https://github.com/%GH_USER%/bus-flow-agent.git
echo Remote: https://github.com/%GH_USER%/bus-flow-agent.git

echo.
echo [3/3] Pushing... A login window may pop up.
echo.
echo   If asked for Username:  type your GitHub username
echo   If asked for Password:  paste your Personal Access Token
echo                           (NOT your GitHub account password!)
echo.
echo ============================================
echo.
git push -u origin main

echo.
echo -------- Finished --------
echo Go check your GitHub repo in the browser.
echo.
pause
