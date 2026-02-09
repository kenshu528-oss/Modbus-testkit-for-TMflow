@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   建立發布包
echo ========================================
echo.

REM 設定版本號
set VERSION=v1.0.1.0001

REM 建立發布資料夾
set RELEASE_DIR=TMflow_Modbus_Testkit_%VERSION%
echo [1/4] 建立發布資料夾: %RELEASE_DIR%
if exist "%RELEASE_DIR%" (
    rmdir /s /q "%RELEASE_DIR%"
)
mkdir "%RELEASE_DIR%"
echo.

REM 複製必要檔案
echo [2/4] 複製檔案...
copy tmflow_modbus_testkit.py "%RELEASE_DIR%\"
copy simulator.py "%RELEASE_DIR%\"
copy requirements.txt "%RELEASE_DIR%\"
copy 啟動測試工具.bat "%RELEASE_DIR%\"
copy 快速安裝.bat "%RELEASE_DIR%\"
copy README.md "%RELEASE_DIR%\"
copy 使用說明.txt "%RELEASE_DIR%\"
copy 功能說明.txt "%RELEASE_DIR%\"
copy 給同事的使用指南.md "%RELEASE_DIR%\"
copy LICENSE "%RELEASE_DIR%\" 2>nul
echo.

REM 建立快速開始文件
echo [3/4] 建立快速開始文件...
(
echo ========================================
echo TMflow Modbus 測試工具 %VERSION%
echo ========================================
echo.
echo 快速開始:
echo.
echo 1. 雙擊「快速安裝.bat」安裝依賴
echo 2. 雙擊「啟動測試工具.bat」啟動程式
echo 3. 詳細說明請參考「給同事的使用指南.md」
echo.
echo ========================================
echo.
echo 專案網址:
echo https://github.com/kenshu528-oss/Modbus-testkit-for-TMflow
echo.
echo ========================================
) > "%RELEASE_DIR%\開始使用.txt"
echo.

REM 壓縮成 ZIP（需要 PowerShell）
echo [4/4] 壓縮成 ZIP...
powershell -command "Compress-Archive -Path '%RELEASE_DIR%' -DestinationPath '%RELEASE_DIR%.zip' -Force"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   發布包建立成功！
    echo ========================================
    echo.
    echo 檔案位置: %RELEASE_DIR%.zip
    echo.
    echo 你可以將這個 ZIP 檔案分享給同事
    echo.
) else (
    echo.
    echo ========================================
    echo   壓縮失敗
    echo ========================================
    echo.
    echo 請手動壓縮資料夾: %RELEASE_DIR%
    echo.
)

pause
