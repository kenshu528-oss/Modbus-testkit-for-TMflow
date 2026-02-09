# TMflow Modbus 測試工具

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v1.0.1.0001-orange.svg)](https://github.com/kenshu528-oss/Modbus-testkit-for-TMflow)

> 專業的 TMflow Modbus 功能驗證工具 - 測試 TMflow 的 Modbus TCP 讀寫是否符合 TM Robot 規範

---

## 📋 專案簡介

這是一個用於測試和驗證 **TMflow 程式的 Modbus 功能**的專業測試工具。透過圖形化介面，可以輕鬆驗證 TMflow 的 Modbus TCP 通訊是否符合 TM Robot 的規範要求。

### 主要用途
- ✅ 驗證 TMflow 的 Modbus 讀取功能
- ✅ 驗證 TMflow 的 Modbus 寫入功能
- ✅ 確認數據格式符合規範（Float32, Int16, Bool 等）
- ✅ 測試通訊性能和穩定性
- ✅ 生成測試報告作為驗證證明

---

## ✨ 主要功能

### 🎯 預設測試功能
- **Base 座標測試** - 驗證 7001-7012 位址的座標讀取
- **Tool 座標測試** - 驗證 7025-7036 位址的座標讀取
- **Joint 角度測試** - 驗證 7013-7024 位址的關節角度讀取
- **Robot 狀態測試** - 驗證機器人狀態位元讀取
- **User Define 測試** - 驗證 9000-9999 位址的讀寫功能

### ⚙️ 自定義測試功能
- 支援所有 Modbus 功能碼（01, 02, 03, 04, 06）
- 支援多種數據型別（Bool, Int16, UInt16, Int32, UInt32, Float32）
- 自定義位址範圍和數量
- 快速預設模板

### ⏱️ 性能測試功能
- 反應時間測試（平均、最小、最大、95% 百分位）
- 穩定性測試（成功率統計）
- 極限測試（0ms 間隔連續測試）
- 自動生成測試報告

### 📊 其他功能
- 連續監控模式
- 即時日誌顯示
- 日誌儲存功能
- 完整的錯誤處理

---

## 🚀 快速開始

### 前置需求
- Python 3.7 或更高版本
- TMflow 程式（測試目標）

### 安裝步驟

1. **Clone 專案**
   ```bash
   git clone https://github.com/kenshu528-oss/Modbus-testkit-for-TMflow.git
   cd Modbus-testkit-for-TMflow
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **啟動測試工具**
   
   **Windows 使用者（推薦）**：
   ```bash
   雙擊 啟動測試工具.bat
   ```
   
   **或手動啟動**：
   ```bash
   python tmflow_modbus_testkit.py
   ```

---

## 📖 使用說明

### 1. 連線到 TMflow

1. 確保 TMflow 程式正在運行，且 Modbus TCP Server 已啟用
2. 在測試工具中輸入 TMflow 的 IP 位址（例如：192.168.1.100）
3. 輸入 Port（預設：502）
4. 點擊「連線」按鈕

### 2. 執行測試

**預設測試**：
- 點擊對應的測試按鈕（Base 座標、Tool 座標等）
- 查看日誌區域的測試結果

**自定義測試**：
1. 選擇功能碼（Coils, Discrete Inputs, Holding Registers, Input Registers）
2. 輸入起始位址和數量
3. 選擇數據型別
4. 點擊「執行自定義測試」

**性能測試**：
1. 選擇測試類型
2. 設定測試次數和間隔
3. 點擊「開始測試」
4. 測試完成後點擊「生成報告」

### 3. 查看結果

- 所有測試結果會即時顯示在日誌區域
- 可以點擊「儲存日誌」保存測試記錄
- 性能測試會生成詳細的報告檔案

---

## 📊 測試項目清單

### 座標讀取驗證
| 項目 | Modbus 位址 | 功能碼 | 數據格式 |
|------|------------|--------|----------|
| Base 座標 | 7001-7012 | 04 | Float32 |
| Tool 座標 | 7025-7036 | 04 | Float32 |
| Joint 角度 | 7013-7024 | 04 | Float32 |

### 狀態讀取驗證
| 項目 | Modbus 位址 | 功能碼 | 數據格式 |
|------|------------|--------|----------|
| Robot Link | 7200 | 02 | Bool |
| Error | 7201 | 02 | Bool |
| Project Running | 7202 | 02 | Bool |
| ESTOP | 7208 | 02 | Bool |
| Robot State | 7215 | 04 | Int16 |
| Operation Mode | 7216 | 04 | Int16 |

### User Define Area
| 項目 | Modbus 位址 | 功能碼 | 說明 |
|------|------------|--------|------|
| 讀取 | 9000-9999 | 03 | 讀取自定義區域 |
| 寫入 | 9000-9999 | 06 | 寫入自定義區域 |

---

## 🛠️ 開發工具

### Modbus 模擬器

專案包含一個 Modbus 模擬器（`simulator.py`），用於開發階段測試：

```bash
python simulator.py
```

**注意**：實際測試 TMflow 時不需要模擬器，直接連線到 TMflow 即可。

---

## 📁 專案結構

```
Modbus-testkit-for-TMflow/
├── tmflow_modbus_testkit.py    # 主測試工具
├── simulator.py                # Modbus 模擬器（開發用）
├── requirements.txt            # Python 依賴
├── 啟動測試工具.bat             # Windows 啟動腳本
├── README.md                   # 專案說明（本文件）
├── 專案規格文件.md              # 完整技術規格
├── 使用說明.txt                 # 詳細使用說明
├── 功能說明.txt                 # 功能詳細說明
└── .gitignore                  # Git 忽略規則
```

---

## 🔧 技術棧

- **Python**: 3.7+
- **pymodbus**: 3.0+ (Modbus TCP 通訊)
- **tkinter**: GUI 框架（Python 內建）
- **threading**: 多線程支援
- **struct**: 數據格式轉換

---

## 📝 常見問題

### Q: 無法連線到 TMflow？
**A**: 
1. 確認 TMflow 程式正在運行
2. 確認 TMflow 的 Modbus TCP Server 已啟用
3. 檢查 IP 位址是否正確
4. 檢查防火牆設定（Port 502）
5. 確認網路連線正常

### Q: 讀取數據失敗？
**A**: 
1. 確認 TMflow 的 Modbus Server 已啟動
2. 確認位址範圍正確
3. 查看日誌中的錯誤訊息

### Q: 需要使用模擬器嗎？
**A**: 不需要。模擬器（simulator.py）僅用於開發階段，實際測試時直接連線到 TMflow 程式。

### Q: 如何生成測試報告？
**A**: 執行性能測試後，點擊「生成報告」按鈕，會自動生成 `.txt` 格式的測試報告。

---

## 📄 授權

本專案採用 MIT License - 詳見 [LICENSE](LICENSE) 檔案

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

---

## 📞 聯絡方式

如有問題或建議，請透過 GitHub Issues 聯繫。

---

## 🔖 版本歷史

### v1.0.1.0001 (2026-02-09)
- ✅ 完整的 GUI 測試工具
- ✅ 預設測試功能（Base, Tool, Joint, Status, User Define）
- ✅ 自定義測試功能
- ✅ 性能測試功能
- ✅ 日誌管理
- ✅ 連續監控
- ✅ 測試報告生成

---

**⭐ 如果這個專案對你有幫助，請給個 Star！**
