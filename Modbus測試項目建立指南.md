# TMflow Modbus 測試項目建立指南

根據官方文件 (TMflow SW2.24) 整理

---

## 📋 Modbus 功能碼對照表

| 功能碼 | 名稱 | 信號類型 | 讀寫 | 說明 |
|--------|------|---------|------|------|
| 01 | Read Coils | Digital Output | R | 讀取線圈狀態 |
| 02 | Read Discrete Inputs | Digital Input | R | 讀取離散輸入 |
| 03 | Read Holding Registers | Register Output | R | 讀取保持寄存器 |
| 04 | Read Input Registers | Register Input | R | 讀取輸入寄存器 |
| 05 | Write Single Coil | Digital Output | W | 寫入單一線圈 |
| 06 | Write Single Register | Register Output | W | 寫入單一寄存器 |
| 15 | Write Multiple Coils | Digital Output | W | 寫入多個線圈 |
| 16 | Write Multiple Registers | Register Output | W | 寫入多個寄存器 |

---

## 🎯 測試項目分類

### 1. 機器人狀態測試 (Robot Status)

#### 1.1 基本狀態 (功能碼 02 - Discrete Inputs)

| 測試項目 | 位址 | 類型 | 讀寫 | 預期值 | 測試目的 |
|---------|------|------|------|--------|---------|
| Robot Link | 7200 | Bool | R | 0/1 | 確認機器人連線狀態 |
| Error or Not | 7201 | Bool | R | 0/1 | 確認是否有錯誤 |
| Get UI Control | 7205 | Bool | R | 0/1 | 確認是否取得控制權 |
| Light | 7206 | Bool | R/W | 0/1 | 測試燈號控制 |
| ESTOP | 7208 | Bool | R | 0/1 | 確認緊急停止狀態 |
| Project Running | 7202 | Bool | R | 0/1 | 確認專案運行狀態 |

**測試腳本範例**：
```python
def test_robot_status():
    # 讀取 Robot Link
    result = client.read_discrete_inputs(7200, count=1, device_id=1)
    assert not result.isError()
    print(f"Robot Link: {result.bits[0]}")
    
    # 讀取 Error
    result = client.read_discrete_inputs(7201, count=1, device_id=1)
    assert not result.isError()
    print(f"Error: {result.bits[0]}")
    
    # 讀取 ESTOP
    result = client.read_discrete_inputs(7208, count=1, device_id=1)
    assert not result.isError()
    print(f"ESTOP: {result.bits[0]}")
```

#### 1.2 進階狀態 (功能碼 04 - Input Registers)

| 測試項目 | 位址 | 類型 | 讀寫 | 說明 |
|---------|------|------|------|------|
| Robot State | 7215 | Int16 | R | 0=Normal, 1=SOS, 2=Error, 3=Recovery, 4=STO |
| Operation Mode | 7216 | Int16 | R | 0=Manual, 1=Auto |
| Manual Mode Settings | 7217 | Int16 | R | 0=T1, 1=TCH |

**測試腳本範例**：
```python
def test_robot_state():
    result = client.read_input_registers(7215, count=1, device_id=1)
    assert not result.isError()
    state = result.registers[0]
    states = {0: "Normal", 1: "SOS", 2: "Error", 3: "Recovery", 4: "STO"}
    print(f"Robot State: {states.get(state, 'Unknown')}")
```

---

### 2. 座標讀取測試 (Robot Coordinate)

#### 2.1 Base 座標 (不含 Tool，功能碼 04)

| 測試項目 | 位址 | 類型 | 單位 | 說明 |
|---------|------|------|------|------|
| X | 7001-7002 | Float32 | mm | X 軸位置 |
| Y | 7003-7004 | Float32 | mm | Y 軸位置 |
| Z | 7005-7006 | Float32 | mm | Z 軸位置 |
| Rx | 7007-7008 | Float32 | degree | X 軸旋轉角度 |
| Ry | 7009-7010 | Float32 | degree | Y 軸旋轉角度 |
| Rz | 7011-7012 | Float32 | degree | Z 軸旋轉角度 |

**數據格式**: Float32 (Big-Endian)，每個座標佔用 2 個 registers

**測試腳本範例**：
```python
import struct

def test_base_coordinates():
    # 讀取 12 個 registers (6 個 Float32)
    result = client.read_input_registers(7001, count=12, device_id=1)
    assert not result.isError()
    
    registers = result.registers
    coords = []
    
    # 轉換為 Float32
    for i in range(0, len(registers), 2):
        float_val = struct.unpack('>f', struct.pack('>HH', 
                                  registers[i], registers[i+1]))[0]
        coords.append(float_val)
    
    print(f"Base Coordinates:")
    print(f"  X:  {coords[0]:.3f} mm")
    print(f"  Y:  {coords[1]:.3f} mm")
    print(f"  Z:  {coords[2]:.3f} mm")
    print(f"  Rx: {coords[3]:.3f}°")
    print(f"  Ry: {coords[4]:.3f}°")
    print(f"  Rz: {coords[5]:.3f}°")
```

#### 2.2 Joint 角度 (功能碼 04)

| 測試項目 | 位址 | 類型 | 單位 | 說明 |
|---------|------|------|------|------|
| Joint 1 | 7013-7014 | Float32 | degree | 關節 1 角度 |
| Joint 2 | 7015-7016 | Float32 | degree | 關節 2 角度 |
| Joint 3 | 7017-7018 | Float32 | degree | 關節 3 角度 |
| Joint 4 | 7019-7020 | Float32 | degree | 關節 4 角度 |
| Joint 5 | 7021-7022 | Float32 | degree | 關節 5 角度 |
| Joint 6 | 7023-7024 | Float32 | degree | 關節 6 角度 |

**測試腳本範例**：
```python
def test_joint_angles():
    result = client.read_input_registers(7013, count=12, device_id=1)
    assert not result.isError()
    
    registers = result.registers
    angles = []
    
    for i in range(0, len(registers), 2):
        float_val = struct.unpack('>f', struct.pack('>HH', 
                                  registers[i], registers[i+1]))[0]
        angles.append(float_val)
    
    print(f"Joint Angles:")
    for i, angle in enumerate(angles, 1):
        print(f"  Joint {i}: {angle:.3f}°")
```

#### 2.3 Tool 座標 (含 Tool，功能碼 04)

| 測試項目 | 位址 | 類型 | 單位 | 說明 |
|---------|------|------|------|------|
| X | 7025-7026 | Float32 | mm | X 軸位置 (含 Tool) |
| Y | 7027-7028 | Float32 | mm | Y 軸位置 (含 Tool) |
| Z | 7029-7030 | Float32 | mm | Z 軸位置 (含 Tool) |
| Rx | 7031-7032 | Float32 | degree | X 軸旋轉角度 (含 Tool) |
| Ry | 7033-7034 | Float32 | degree | Y 軸旋轉角度 (含 Tool) |
| Rz | 7035-7036 | Float32 | degree | Z 軸旋轉角度 (含 Tool) |

---

### 3. Control Box DI/DO 測試

#### 3.1 Digital Output (功能碼 01/05)

| 測試項目 | 位址 | 類型 | 讀寫 | 說明 |
|---------|------|------|------|------|
| DO 0-15 | 0-15 | Bool | R/W | 數位輸出 0-15 |

**測試腳本範例**：
```python
def test_digital_output():
    # 讀取 DO 0
    result = client.read_coils(0, count=1, device_id=1)
    assert not result.isError()
    print(f"DO 0: {result.bits[0]}")
    
    # 寫入 DO 0
    result = client.write_coil(0, True, device_id=1)
    assert not result.isError()
    print("DO 0 set to True")
    
    # 讀取驗證
    result = client.read_coils(0, count=1, device_id=1)
    assert result.bits[0] == True
```

#### 3.2 Digital Input (功能碼 02)

| 測試項目 | 位址 | 類型 | 讀寫 | 說明 |
|---------|------|------|------|------|
| DI 0-15 | 0-15 | Bool | R | 數位輸入 0-15 |

---

### 4. User Define Area 測試 (9000-9999)

**支援功能碼**: 01, 03, 05, 06, 15, 16

這是使用者自定義區域，可以用來：
- 儲存自定義數據
- 與外部設備交換資料
- 測試讀寫功能

#### 4.1 讀取測試 (功能碼 03)

**測試腳本範例**：
```python
def test_user_define_read():
    # 讀取 10 個 registers
    result = client.read_holding_registers(9000, count=10, device_id=1)
    assert not result.isError()
    
    print("User Define Area (9000-9009):")
    for i, value in enumerate(result.registers):
        print(f"  [{9000+i}]: {value} (0x{value:04X})")
```

#### 4.2 寫入測試 (功能碼 06)

**測試腳本範例**：
```python
def test_user_define_write():
    test_value = 12345
    
    # 寫入
    result = client.write_register(9000, test_value, device_id=1)
    assert not result.isError()
    print(f"Written {test_value} to address 9000")
    
    # 讀取驗證
    result = client.read_holding_registers(9000, count=1, device_id=1)
    assert not result.isError()
    assert result.registers[0] == test_value
    print(f"Verified: {result.registers[0]}")
```

#### 4.3 讀寫驗證測試

**測試腳本範例**：
```python
def test_user_define_read_write():
    import random
    
    # 測試多個位址
    test_addresses = [9000, 9001, 9010, 9100, 9999]
    
    for addr in test_addresses:
        # 產生隨機測試值
        test_value = random.randint(0, 65535)
        
        # 寫入
        write_result = client.write_register(addr, test_value, device_id=1)
        assert not write_result.isError()
        
        # 讀取
        read_result = client.read_holding_registers(addr, count=1, device_id=1)
        assert not read_result.isError()
        
        # 驗證
        actual_value = read_result.registers[0]
        assert actual_value == test_value
        
        print(f"✓ Address {addr}: Write {test_value}, Read {actual_value}")
```

---

## 🧪 完整測試套件範例

### 測試套件結構

```python
class TMflowModbusTestSuite:
    def __init__(self, ip, port=502):
        self.client = ModbusTcpClient(ip, port=port, timeout=3)
        self.test_results = []
    
    def run_all_tests(self):
        """執行所有測試"""
        tests = [
            ("Robot Status", self.test_robot_status),
            ("Base Coordinates", self.test_base_coordinates),
            ("Joint Angles", self.test_joint_angles),
            ("Tool Coordinates", self.test_tool_coordinates),
            ("Digital IO", self.test_digital_io),
            ("User Define Area", self.test_user_define_area),
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*50}")
                print(f"Testing: {test_name}")
                print(f"{'='*50}")
                test_func()
                self.test_results.append((test_name, "PASS"))
            except Exception as e:
                print(f"❌ Test Failed: {e}")
                self.test_results.append((test_name, "FAIL"))
        
        self.print_summary()
    
    def print_summary(self):
        """列印測試摘要"""
        print(f"\n{'='*50}")
        print("Test Summary")
        print(f"{'='*50}")
        
        for test_name, result in self.test_results:
            status = "✓" if result == "PASS" else "✗"
            print(f"{status} {test_name}: {result}")
        
        total = len(self.test_results)
        passed = sum(1 for _, r in self.test_results if r == "PASS")
        print(f"\nTotal: {total}, Passed: {passed}, Failed: {total-passed}")
```

---

## 📊 測試檢查清單

### 基本功能測試
- [ ] Robot Link 狀態讀取
- [ ] Error 狀態讀取
- [ ] ESTOP 狀態讀取
- [ ] Robot State 讀取
- [ ] Operation Mode 讀取

### 座標測試
- [ ] Base 座標讀取 (7001-7012)
- [ ] Joint 角度讀取 (7013-7024)
- [ ] Tool 座標讀取 (7025-7036)
- [ ] 數據格式驗證 (Float32)
- [ ] 單位驗證 (mm, degree)

### IO 測試
- [ ] Digital Output 讀取 (功能碼 01)
- [ ] Digital Output 寫入 (功能碼 05)
- [ ] Digital Input 讀取 (功能碼 02)

### User Define Area 測試
- [ ] 讀取功能 (功能碼 03)
- [ ] 寫入功能 (功能碼 06)
- [ ] 讀寫驗證
- [ ] 邊界測試 (9000, 9999)
- [ ] 多筆寫入 (功能碼 16)

### 性能測試
- [ ] 反應時間測試
- [ ] 連續讀取穩定性
- [ ] 大量資料傳輸
- [ ] 錯誤處理

---

## 🎯 測試優先級

### P0 (必須測試)
1. Robot Link 狀態
2. Base 座標讀取
3. Joint 角度讀取
4. User Define Area 讀寫

### P1 (重要測試)
1. Tool 座標讀取
2. Robot State
3. Digital IO
4. 性能測試

### P2 (進階測試)
1. 錯誤處理
2. 邊界條件
3. 壓力測試
4. 長時間穩定性

---

## 📝 測試報告範本

```
TMflow Modbus 測試報告
======================

測試日期: YYYY-MM-DD
測試人員: [姓名]
TMflow 版本: 2.24
測試工具版本: v1.0.1.0002

測試環境:
- IP: [TMflow IP]
- Port: 502
- 連線狀態: [成功/失敗]

測試結果:
1. Robot Status: [PASS/FAIL]
2. Base Coordinates: [PASS/FAIL]
3. Joint Angles: [PASS/FAIL]
4. Tool Coordinates: [PASS/FAIL]
5. Digital IO: [PASS/FAIL]
6. User Define Area: [PASS/FAIL]

問題記錄:
[記錄發現的問題]

結論:
[測試結論]
```

---

## 🔗 參考資料

- TMflow Software Manual SW2.24 Rev1.00E
- Appendix C: Modbus List (Page 305)
- Programming Language TMscript 2.24 Rev1.0

---

**建立日期**: 2026-02-09  
**文件版本**: 1.0  
**適用版本**: TMflow SW2.24
