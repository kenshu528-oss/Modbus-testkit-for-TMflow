@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   上傳到 GitHub
echo ========================================
echo.

REM 檢查是否已經初始化 Git
if not exist .git (
    echo [1/5] 初始化 Git Repository...
    git init
    echo.
) else (
    echo [1/5] Git Repository 已存在
    echo.
)

echo [2/5] 加入所有檔案...
git add .
echo.

echo [3/5] 建立 Commit...
git commit -m "Initial commit: TMflow Modbus Testkit v1.0.1.0001"
echo.

echo [4/5] 請輸入你的 GitHub Repository URL
echo 範例: https://github.com/你的帳號/Modbus-testkit-for-TMflow.git
echo.
set /p REPO_URL="Repository URL: "
echo.

if "%REPO_URL%"=="" (
    echo 錯誤: 未輸入 Repository URL
    pause
    exit /b 1
)

echo [5/5] 連結並推送到 GitHub...
git remote add origin %REPO_URL% 2>nul
git branch -M main
git push -u origin main
echo.

if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo   上傳成功！
    echo ========================================
    echo.
    echo 你的專案已經上傳到 GitHub
    echo Repository: %REPO_URL%
    echo.
) else (
    echo ========================================
    echo   上傳失敗
    echo ========================================
    echo.
    echo 可能的原因:
    echo 1. Repository URL 錯誤
    echo 2. 沒有權限
    echo 3. 需要登入 GitHub
    echo.
    echo 請參考 上傳步驟.md 手動上傳
    echo.
)

pause
