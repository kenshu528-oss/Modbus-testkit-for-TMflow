@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   打包成獨立執行檔 (EXE)
echo ========================================
echo.

REM 檢查 Python
echo [1/5] 檢查 Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 錯誤: 未安裝 Python
    pause
    exit /b 1
)
echo ✅ Python 已安裝
echo.

REM 安裝 PyInstaller
echo [2/5] 安裝 PyInstaller...
pip install pyinstaller
echo.

REM 確保依賴已安裝
echo [3/5] 安裝程式依賴...
pip install -r requirements.txt
echo.

REM 打包成 EXE
echo [4/5] 打包成 EXE（這可能需要幾分鐘）...
pyinstaller --onefile --windowed --name "TMflow_Modbus_Testkit" --icon=NONE tmflow_modbus_testkit.py
echo.

REM 建立發布資料夾
echo [5/5] 建立發布資料夾...
set RELEASE_DIR=TMflow_Modbus_Testkit_Portable_v1.0.1.0001

if exist "%RELEASE_DIR%" (
    rmdir /s /q "%RELEASE_DIR%"
)
mkdir "%RELEASE_DIR%"

REM 複製 EXE
copy dist\TMflow_Modbus_Testkit.exe "%RELEASE_DIR%\"

REM 複製說明文件
copy 使用說明.txt "%RELEASE_DIR%\"
copy 功能說明.txt "%RELEASE_DIR%\"

REM 建立使用說明
(
echo ========================================
echo TMflow Modbus 測試工具 v1.0.1.0001
echo 獨立執行版（免安裝）
echo ========================================
echo.
echo 使用方式:
echo.
echo 1. 雙擊「TMflow_Modbus_Testkit.exe」啟動程式
echo 2. 輸入 TMflow 的 IP 位址和 Port
echo 3. 點擊「連線」按鈕
echo 4. 開始測試
echo.
echo 注意事項:
echo - 不需要安裝 Python
echo - 不需要安裝任何套件
echo - 可以直接執行
echo.
echo 詳細說明請參考「使用說明.txt」
echo.
echo ========================================
) > "%RELEASE_DIR%\開始使用.txt"

REM 壓縮
echo.
echo 壓縮成 ZIP...
powershell -command "Compress-Archive -Path '%RELEASE_DIR%' -DestinationPath '%RELEASE_DIR%.zip' -Force"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   打包成功！
    echo ========================================
    echo.
    echo 檔案位置: %RELEASE_DIR%.zip
    echo EXE 位置: %RELEASE_DIR%\TMflow_Modbus_Testkit.exe
    echo.
    echo 這個版本不需要安裝 Python，可以直接執行！
    echo 檔案大小約 15-20 MB
    echo.
) else (
    echo.
    echo ========================================
    echo   打包失敗
    echo ========================================
    echo.
)

pause
