@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   TMflow Modbus 測試工具 - 快速安裝
echo ========================================
echo.

REM 檢查 Python 是否已安裝
echo [1/3] 檢查 Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 錯誤: 未安裝 Python
    echo.
    echo 請先安裝 Python 3.7 或更高版本
    echo 下載網址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python 已安裝
echo.

REM 安裝依賴套件
echo [2/3] 安裝依賴套件...
pip install -r requirements.txt
echo.

if %ERRORLEVEL% EQU 0 (
    echo [3/3] 安裝完成！
    echo.
    echo ========================================
    echo   安裝成功！
    echo ========================================
    echo.
    echo 現在可以雙擊「啟動測試工具.bat」來啟動程式
    echo.
) else (
    echo ========================================
    echo   安裝失敗
    echo ========================================
    echo.
    echo 請檢查網路連線或手動執行:
    echo pip install -r requirements.txt
    echo.
)

pause
