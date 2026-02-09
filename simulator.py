#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TM Robot Modbus TCP 模擬器
提供完整的 TM Robot 座標和狀態模擬
"""

from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext
import asyncio
import logging
import sys
import struct
import random
import time

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

def float_to_registers(float_val):
    """將 Float32 轉換為兩個 16-bit registers"""
    packed = struct.pack('>f', float_val)
    return struct.unpack('>HH', packed)

class RealisticModbusDataBlock(ModbusSequentialDataBlock):
    """添加真實延遲的 Modbus 數據區塊"""
    
    def __init__(self, address, values):
        super().__init__(address, values)
        self.read_count = 0
        self.write_count = 0
    
    def getValues(self, address, count=1):
        """讀取時添加延遲"""
        # 模擬網路和處理延遲 (5-15ms)
        delay = random.uniform(0.005, 0.015)
        time.sleep(delay)
        
        self.read_count += 1
        
        # 偶爾模擬較長的延遲 (模擬網路抖動)
        if self.read_count % 50 == 0:
            time.sleep(random.uniform(0.02, 0.05))
        
        return super().getValues(address, count)
    
    def setValues(self, address, values):
        """寫入時添加延遲"""
        # 寫入通常比讀取慢一些
        delay = random.uniform(0.008, 0.020)
        time.sleep(delay)
        
        self.write_count += 1
        
        return super().setValues(address, values)

def create_tm_robot_context():
    """建立 TM Robot Modbus Context"""
    
    # 準備數據陣列 - 支援高位址
    ir_data = [0] * 8000  # Input Registers
    di_data = [0] * 8000  # Discrete Inputs  
    co_data = [0] * 8000  # Coils
    hr_data = [0] * 8000  # Holding Registers
    
    # === TM Robot 座標數據 ===
    
    # Base 座標系 (7001-7012)
    base_coords = [350.5, -120.3, 450.8, 0.0, 90.0, -45.0]
    for i, coord in enumerate(base_coords):
        reg1, reg2 = float_to_registers(coord)
        addr = 7001 + i * 2
        ir_data[addr] = reg1
        ir_data[addr + 1] = reg2
    
    # Joint 角度 (7013-7024)  
    joint_angles = [0.0, -30.0, 45.0, 0.0, 75.0, 0.0]
    for i, angle in enumerate(joint_angles):
        reg1, reg2 = float_to_registers(angle)
        addr = 7013 + i * 2
        ir_data[addr] = reg1
        ir_data[addr + 1] = reg2
    
    # Tool 座標系 (7025-7036)
    tool_coords = [355.2, -118.7, 455.3, 2.1, 91.5, -43.8]
    for i, coord in enumerate(tool_coords):
        reg1, reg2 = float_to_registers(coord)
        addr = 7025 + i * 2
        ir_data[addr] = reg1
        ir_data[addr + 1] = reg2
    
    # === TM Robot 狀態數據 ===
    
    # Discrete Inputs
    di_data[7200] = 1  # Robot Link (已連線)
    di_data[7201] = 0  # Error (無錯誤)
    di_data[7202] = 0  # Project Running (未運行)
    di_data[7208] = 0  # ESTOP (已恢復)
    
    # Input Registers  
    ir_data[7215] = 0  # Robot State (Normal)
    ir_data[7216] = 0  # Operation Mode (Manual)
    
    # Coils
    co_data[7206] = 0  # Light (關閉)
    
    # Control Box DI/DO (0-15)
    for i in range(16):
        di_data[i] = i % 2  # DI 交替 0/1
        co_data[i] = 0      # DO 全部為 0
    
    # === User Define Area (9000-9999) ===
    # 初始化 User Define Area 的 Holding Registers
    for i in range(9000, 10000):
        if i < len(hr_data):
            hr_data[i] = i - 9000  # 設定初始值 (0, 1, 2, 3, ...)
    
    # 設定一些特殊的 User Define 值
    if 9000 < len(hr_data): hr_data[9000] = 12345   # 測試值
    if 9001 < len(hr_data): hr_data[9001] = 67890   # 測試值
    if 9010 < len(hr_data): hr_data[9010] = 0xABCD  # 十六進位測試值
    if 9020 < len(hr_data): hr_data[9020] = 0x1234  # 十六進位測試值
    if 9100 < len(hr_data): hr_data[9100] = 65535   # 最大值測試
    
    # 建立資料區塊 (使用真實延遲版本)
    di = RealisticModbusDataBlock(0, di_data)
    co = RealisticModbusDataBlock(0, co_data)  
    hr = RealisticModbusDataBlock(0, hr_data)
    ir = RealisticModbusDataBlock(0, ir_data)
    
    return ModbusDeviceContext(di=di, co=co, hr=hr, ir=ir)

async def run_simulator(host="127.0.0.1", port=502):
    """啟動 TM Robot 模擬器"""
    
    device = create_tm_robot_context()
    context = ModbusServerContext(devices={1: device}, single=False)
    
    print("=" * 60)
    print("TM Robot Modbus TCP Simulator v1.0.1.0001")
    print("=" * 60)
    print(f"Server: {host}:{port}")
    print(f"Slave ID: 1")
    print("\nSimulated Coordinates:")
    print("   Base: X=350.5, Y=-120.3, Z=450.8 mm")
    print("   Tool: X=355.2, Y=-118.7, Z=455.3 mm") 
    print("   Joint: J1=0deg, J2=-30deg, J3=45deg")
    print("\nSupported Addresses:")
    print("   Base Coordinates: 7001-7012")
    print("   Joint Angles: 7013-7024")
    print("   Tool Coordinates: 7025-7036")
    print("   Robot Status: 7200, 7201, 7215, 7216")
    print("   User Define Area: 9000-9999 (R/W)")
    print("\nSimulator is running... (Press Ctrl+C to stop)")
    print("=" * 60)
    
    await StartAsyncTcpServer(context=context, address=(host, port))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 502
    asyncio.run(run_simulator("127.0.0.1", port))