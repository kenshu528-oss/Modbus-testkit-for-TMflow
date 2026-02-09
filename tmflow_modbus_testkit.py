#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TM Robot 座標測試 GUI
簡潔、高效的座標測試工具
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pymodbus.client import ModbusTcpClient
import struct
import threading
import time
from datetime import datetime

class TMRobotTestGUI:
    VERSION = "v1.0.1.0002"  # 版本號
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"🤖 TM Robot 座標測試工具 {self.VERSION}")
        self.root.geometry("1100x800")
        
        self.client = None
        self.is_connected = False
        
        self.setup_ui()
        
    def validate_number(self, value):
        """驗證輸入是否為有效數字"""
        if value == "":
            return True
        try:
            num = int(value)
            return 1 <= num <= 100000  # 限制範圍 1-100000
        except ValueError:
            return False
    
    def validate_interval(self, value):
        """驗證測試間隔輸入"""
        if value == "":
            return True
        try:
            num = int(value)
            return 0 <= num <= 60000  # 限制範圍 0-60000ms (1分鐘)
        except ValueError:
            return False
        
    def setup_ui(self):
        """建立使用者介面"""
        
        # === 連線區域 ===
        conn_frame = ttk.LabelFrame(self.root, text="🔌 連線設定", padding="10")
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        # IP 和 Port
        ttk.Label(conn_frame, text="IP:").grid(row=0, column=0, sticky="w")
        self.ip_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(conn_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="w", padx=(20,0))
        self.port_var = tk.StringVar(value="502")
        ttk.Entry(conn_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, padx=5)
        
        # 整合的連線/斷線按鈕（移除燈號，縮小寬度）
        self.connection_btn = ttk.Button(conn_frame, text="連線", command=self.toggle_connection, width=10)
        self.connection_btn.grid(row=0, column=4, padx=10)
        
        # 狀態顯示（移到按鈕後方）
        self.status_var = tk.StringVar(value="🔴 未連線")
        status_label = ttk.Label(conn_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, width=30)
        status_label.grid(row=0, column=5, padx=5, sticky="ew")
        
        # === 主要內容區域 (添加滾動支援) ===
        # 創建 Canvas 和 Scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar_v = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(self.root, orient="horizontal", command=canvas.xview)
        
        # 可滾動的框架
        scrollable_frame = ttk.Frame(canvas)
        
        # 配置滾動
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # 佈局滾動組件
        canvas.pack(side="left", fill="both", expand=True, padx=(10,0), pady=5)
        scrollbar_v.pack(side="right", fill="y", padx=(0,10), pady=5)
        scrollbar_h.pack(side="bottom", fill="x", padx=10, pady=(0,5))
        
        # 鼠標滾輪支援
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 主要內容區域
        main_content = ttk.Frame(scrollable_frame)
        main_content.pack(fill="both", expand=True, padx=10, pady=5)
        
        # === 左側：預設測試區域 ===
        left_frame = ttk.Frame(main_content)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0,5))
        
        test_frame = ttk.LabelFrame(left_frame, text="🧪 預設測試", padding="10")
        test_frame.pack(fill="x", pady=(0,5))
        
        # 測試按鈕 - 第一排
        btn_frame1 = ttk.Frame(test_frame)
        btn_frame1.pack(fill="x", pady=(0,5))
        
        ttk.Button(btn_frame1, text="🎯 Base 座標", command=self.test_base_coords, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame1, text="🔧 Tool 座標", command=self.test_tool_coords, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame1, text="🦾 Joint 角度", command=self.test_joint_angles, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame1, text="👤 User Define", command=self.test_user_define_area, width=12).pack(side="left", padx=2)
        
        # 測試按鈕 - 第二排
        btn_frame2 = ttk.Frame(test_frame)
        btn_frame2.pack(fill="x", pady=(0,5))
        
        ttk.Button(btn_frame2, text="📊 Robot 狀態", command=self.test_robot_status, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame2, text="🔄 全部測試", command=self.test_all, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame2, text="🔁 連續監控", command=self.toggle_monitoring, width=12).pack(side="left", padx=2)
        
        # 測試按鈕 - 第三排
        btn_frame3 = ttk.Frame(test_frame)
        btn_frame3.pack(fill="x")
        
        ttk.Button(btn_frame3, text="🗑️ 清除日誌", command=self.clear_log, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame3, text="💾 儲存日誌", command=self.save_log, width=12).pack(side="left", padx=2)
        
        # === 右側：USER DEFINE 測試區域 ===
        right_frame = ttk.Frame(main_content)
        right_frame.pack(side="right", fill="y", padx=(5,0))
        
        user_frame = ttk.LabelFrame(right_frame, text="⚙️ USER DEFINE 測試", padding="10")
        user_frame.pack(fill="both", expand=True)
        
        # 功能碼選擇
        ttk.Label(user_frame, text="功能碼:").grid(row=0, column=0, sticky="w", pady=2)
        self.function_var = tk.StringVar(value="Input Registers (04)")
        function_combo = ttk.Combobox(user_frame, textvariable=self.function_var, width=20, state="readonly")
        function_combo['values'] = ("Coils (01)", "Discrete Inputs (02)", "Holding Registers (03)", "Input Registers (04)")
        function_combo.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # 起始位址
        ttk.Label(user_frame, text="起始位址:").grid(row=1, column=0, sticky="w", pady=2)
        self.start_addr_var = tk.StringVar(value="7001")
        ttk.Entry(user_frame, textvariable=self.start_addr_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # 數量
        ttk.Label(user_frame, text="數量:").grid(row=2, column=0, sticky="w", pady=2)
        self.count_var = tk.StringVar(value="12")
        ttk.Entry(user_frame, textvariable=self.count_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        # 資料型別
        ttk.Label(user_frame, text="資料型別:").grid(row=3, column=0, sticky="w", pady=2)
        self.datatype_var = tk.StringVar(value="Float32")
        datatype_combo = ttk.Combobox(user_frame, textvariable=self.datatype_var, width=15, state="readonly")
        datatype_combo['values'] = ("Bool", "Int16", "UInt16", "Int32", "UInt32", "Float32", "Raw")
        datatype_combo.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # Slave ID
        ttk.Label(user_frame, text="Slave ID:").grid(row=4, column=0, sticky="w", pady=2)
        self.slave_id_var = tk.StringVar(value="1")
        ttk.Entry(user_frame, textvariable=self.slave_id_var, width=10).grid(row=4, column=1, padx=5, pady=2)
        
        # 測試名稱
        ttk.Label(user_frame, text="測試名稱:").grid(row=5, column=0, sticky="w", pady=2)
        self.test_name_var = tk.StringVar(value="Custom Test")
        ttk.Entry(user_frame, textvariable=self.test_name_var, width=20).grid(row=5, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # 執行按鈕
        ttk.Button(user_frame, text="🚀 執行自定義測試", command=self.execute_user_define_test, width=20).grid(row=6, column=0, columnspan=3, pady=10)
        
        # 預設測試案例
        ttk.Label(user_frame, text="快速設定:").grid(row=7, column=0, sticky="w", pady=(10,2))
        
        preset_frame = ttk.Frame(user_frame)
        preset_frame.grid(row=8, column=0, columnspan=3, sticky="ew", pady=2)
        
        ttk.Button(preset_frame, text="Base座標", command=lambda: self.load_preset("base"), width=8).pack(side="left", padx=1)
        ttk.Button(preset_frame, text="Tool座標", command=lambda: self.load_preset("tool"), width=8).pack(side="left", padx=1)
        ttk.Button(preset_frame, text="Joint角度", command=lambda: self.load_preset("joint"), width=8).pack(side="left", padx=1)
        
        preset_frame2 = ttk.Frame(user_frame)
        preset_frame2.grid(row=9, column=0, columnspan=3, sticky="ew", pady=2)
        
        ttk.Button(preset_frame2, text="Robot狀態", command=lambda: self.load_preset("status"), width=8).pack(side="left", padx=1)
        ttk.Button(preset_frame2, text="Light控制", command=lambda: self.load_preset("light"), width=8).pack(side="left", padx=1)
        ttk.Button(preset_frame2, text="清除", command=self.clear_preset, width=8).pack(side="left", padx=1)
        
        preset_frame3 = ttk.Frame(user_frame)
        preset_frame3.grid(row=10, column=0, columnspan=3, sticky="ew", pady=2)
        
        ttk.Button(preset_frame3, text="UserDefine", command=lambda: self.load_preset("userdefine"), width=12).pack(side="left", padx=1)
        
        # 設定欄位權重
        user_frame.columnconfigure(1, weight=1)
        
        # === 性能測試區域 ===
        perf_frame = ttk.LabelFrame(right_frame, text="⏱️ 性能測試", padding="10")
        perf_frame.pack(fill="x", pady=(10,0))
        
        # 測試類型選擇
        ttk.Label(perf_frame, text="測試類型:").grid(row=0, column=0, sticky="w", pady=2)
        self.perf_test_var = tk.StringVar(value="Base座標讀取")
        perf_combo = ttk.Combobox(perf_frame, textvariable=self.perf_test_var, width=18, state="readonly")
        perf_combo['values'] = ("Base座標讀取", "Tool座標讀取", "Joint角度讀取", "Robot狀態讀取", "User Define讀取", "User Define寫入", "User Define讀寫", "混合測試", "極限測試")
        perf_combo.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # 測試次數
        ttk.Label(perf_frame, text="測試次數:").grid(row=1, column=0, sticky="w", pady=2)
        self.test_count_var = tk.StringVar(value="100")
        
        # 使用 Frame 來包含 Entry 和快速選擇按鈕
        count_frame = ttk.Frame(perf_frame)
        count_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # 自定義輸入框
        self.test_count_entry = ttk.Entry(count_frame, textvariable=self.test_count_var, width=8, validate="key")
        self.test_count_entry.pack(side="left")
        
        # 驗證函數 - 只允許數字
        vcmd = (self.root.register(self.validate_number), '%P')
        self.test_count_entry.config(validatecommand=vcmd)
        
        # 快速選擇按鈕
        quick_counts = [("50", "50"), ("100", "100"), ("500", "500"), ("1K", "1000"), ("5K", "5000")]
        for text, value in quick_counts:
            btn = ttk.Button(count_frame, text=text, width=4, 
                           command=lambda v=value: self.test_count_var.set(v))
            btn.pack(side="left", padx=1)
        
        # 測試間隔
        ttk.Label(perf_frame, text="間隔(ms):").grid(row=2, column=0, sticky="w", pady=2)
        self.test_interval_var = tk.StringVar(value="100")
        
        # 使用 Frame 來包含 Entry 和快速選擇按鈕
        interval_frame = ttk.Frame(perf_frame)
        interval_frame.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # 自定義輸入框
        self.test_interval_entry = ttk.Entry(interval_frame, textvariable=self.test_interval_var, width=8, validate="key")
        self.test_interval_entry.pack(side="left")
        
        # 驗證函數 - 只允許數字
        vcmd_interval = (self.root.register(self.validate_interval), '%P')
        self.test_interval_entry.config(validatecommand=vcmd_interval)
        
        # 快速選擇按鈕
        quick_intervals = [("0", "0"), ("1", "1"), ("10", "10"), ("100", "100"), ("1K", "1000")]
        for text, value in quick_intervals:
            btn = ttk.Button(interval_frame, text=text, width=4, 
                           command=lambda v=value: self.test_interval_var.set(v))
            btn.pack(side="left", padx=1)
        
        # 控制按鈕
        perf_btn_frame = ttk.Frame(perf_frame)
        perf_btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_perf_btn = ttk.Button(perf_btn_frame, text="🚀 開始測試", command=self.start_performance_test, width=12)
        self.start_perf_btn.pack(side="left", padx=2)
        
        self.stop_perf_btn = ttk.Button(perf_btn_frame, text="⏹️ 停止", command=self.stop_performance_test, state="disabled", width=12)
        self.stop_perf_btn.pack(side="left", padx=2)
        
        # 即時結果顯示
        result_frame = ttk.LabelFrame(perf_frame, text="📊 即時結果", padding="5")
        result_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10,0))
        
        # 進度條
        ttk.Label(result_frame, text="進度:").grid(row=0, column=0, sticky="w")
        self.progress_var = tk.StringVar(value="0/0")
        ttk.Label(result_frame, textvariable=self.progress_var).grid(row=0, column=1, sticky="w", padx=5)
        
        self.progress_bar = ttk.Progressbar(result_frame, length=200, mode='determinate')
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)
        
        # 統計結果
        stats_frame = ttk.Frame(result_frame)
        stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(stats_frame, text="平均:").grid(row=0, column=0, sticky="w")
        self.avg_time_var = tk.StringVar(value="-- ms")
        ttk.Label(stats_frame, textvariable=self.avg_time_var, foreground="blue").grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(stats_frame, text="最小:").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.min_time_var = tk.StringVar(value="-- ms")
        ttk.Label(stats_frame, textvariable=self.min_time_var, foreground="green").grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(stats_frame, text="最大:").grid(row=1, column=0, sticky="w")
        self.max_time_var = tk.StringVar(value="-- ms")
        ttk.Label(stats_frame, textvariable=self.max_time_var, foreground="red").grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(stats_frame, text="成功率:").grid(row=1, column=2, sticky="w", padx=(10,0))
        self.success_rate_var = tk.StringVar(value="-- %")
        ttk.Label(stats_frame, textvariable=self.success_rate_var, foreground="purple").grid(row=1, column=3, sticky="w", padx=5)
        
        # 報告按鈕
        ttk.Button(result_frame, text="📈 生成報告", command=self.generate_performance_report, width=15).grid(row=3, column=0, columnspan=2, pady=5)
        
        # 性能測試相關變數
        self.perf_testing = False
        self.perf_thread = None
        self.perf_results = []
        
        # 設定權重
        perf_frame.columnconfigure(1, weight=1)
        result_frame.columnconfigure(0, weight=1)
        
        # === 結果顯示區域 ===
        result_frame = ttk.LabelFrame(left_frame, text="📋 測試結果", padding="5")
        result_frame.pack(fill="both", expand=True)
        
        # 日誌文字區域
        self.log_text = scrolledtext.ScrolledText(
            result_frame, 
            height=20, 
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True)
        
        # 監控相關變數
        self.monitoring = False
        self.monitor_thread = None
        
        # 初始化日誌
        self.log(f"🚀 TM Robot 座標測試工具 {self.VERSION} 已啟動")
        self.log("📝 請先連線到 Modbus 設備，然後選擇測試項目")
        
    def log(self, message, level="INFO"):
        """記錄日誌"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 根據等級添加圖示
        if level == "ERROR":
            icon = "❌"
        elif level == "SUCCESS":
            icon = "✅"
        elif level == "WARNING":
            icon = "⚠️"
        else:
            icon = "ℹ️"
            
        log_entry = f"[{timestamp}] {icon} {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
        
    def clear_log(self):
        """清除日誌"""
        self.log_text.delete(1.0, tk.END)
        self.log("🗑️ 日誌已清除")
        
    def save_log(self):
        """儲存日誌到檔案"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tm_robot_test_log_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
                
            self.log(f"💾 日誌已儲存: {filename}", "SUCCESS")
            
        except Exception as e:
            self.log(f"💾 儲存日誌失敗: {e}", "ERROR")
        
    def toggle_connection(self):
        """切換連線/斷線狀態"""
        if self.is_connected:
            self.disconnect()
        else:
            self.connect()
    
    def update_connection_button(self, state):
        """更新連線按鈕的狀態和文字
        state: 'disconnected', 'connecting', 'connected'
        """
        if state == 'disconnected':
            self.connection_btn.config(text="連線", state="normal")
            self.status_var.set("🔴 未連線")
        elif state == 'connecting':
            self.connection_btn.config(text="連線中...", state="disabled")
            self.status_var.set("⚪ 連線中...")
        elif state == 'connected':
            self.connection_btn.config(text="斷線", state="normal")
    
    def connect(self):
        """連線到 Modbus"""
        try:
            ip = self.ip_var.get()
            port = int(self.port_var.get())
            
            # 更新為連線中狀態
            self.update_connection_button('connecting')
            self.log(f"🔌 正在連線到 {ip}:{port}...")
            self.root.update()  # 強制更新 GUI
            
            self.client = ModbusTcpClient(ip, port=port, timeout=3)
            if self.client.connect():
                self.is_connected = True
                self.update_connection_button('connected')
                self.log(f"🔌 連線成功: {ip}:{port}", "SUCCESS")
                self.status_var.set(f"🟢 已連線: {ip}:{port}")
            else:
                self.is_connected = False
                self.update_connection_button('disconnected')
                self.log("🔌 連線失敗", "ERROR")
                messagebox.showerror("連線失敗", f"無法連線到 {ip}:{port}")
                
        except Exception as e:
            self.is_connected = False
            self.update_connection_button('disconnected')
            self.log(f"🔌 連線錯誤: {e}", "ERROR")
            messagebox.showerror("連線錯誤", str(e))
            
    def disconnect(self):
        """斷線"""
        if self.monitoring:
            self.toggle_monitoring()  # 停止監控
            
        if self.client:
            self.client.close()
            
        self.is_connected = False
        self.update_connection_button('disconnected')
        self.log("🔌 已斷線")
        
    def read_coordinates(self, start_addr, coord_type, count=12):
        """讀取座標數據"""
        if not self.is_connected:
            self.log("❌ 請先連線", "ERROR")
            return None
            
        try:
            self.log(f"📍 讀取 {coord_type} (位址 {start_addr}-{start_addr+count-1})...")
            
            result = self.client.read_input_registers(start_addr, count=count, device_id=1)
            
            if result.isError():
                self.log(f"📍 讀取失敗: {result}", "ERROR")
                return None
                
            registers = result.registers
            self.log(f"📊 原始數據: {registers}")
            
            # 轉換為 Float32
            coords = []
            for i in range(0, len(registers), 2):
                if i + 1 < len(registers):
                    float_val = struct.unpack('>f', struct.pack('>HH', registers[i], registers[i+1]))[0]
                    coords.append(float_val)
                    
            # 格式化顯示
            self.log(f"✅ {coord_type}:", "SUCCESS")
            
            if coord_type == "Joint 角度":
                for i, angle in enumerate(coords[:6], 1):
                    self.log(f"   Joint {i}: {angle:8.3f}°")
            else:
                if len(coords) >= 6:
                    self.log(f"   X:  {coords[0]:8.3f} mm")
                    self.log(f"   Y:  {coords[1]:8.3f} mm") 
                    self.log(f"   Z:  {coords[2]:8.3f} mm")
                    self.log(f"   Rx: {coords[3]:8.3f}°")
                    self.log(f"   Ry: {coords[4]:8.3f}°")
                    self.log(f"   Rz: {coords[5]:8.3f}°")
                else:
                    self.log(f"   數據: {coords}")
                    
            self.log("─" * 50)
            return coords
            
        except Exception as e:
            self.log(f"📍 讀取錯誤: {e}", "ERROR")
            return None
            
    def read_robot_status(self):
        """讀取 Robot 狀態"""
        if not self.is_connected:
            self.log("❌ 請先連線", "ERROR")
            return
            
        try:
            self.log("📊 讀取 Robot 狀態...")
            
            # 讀取 Discrete Inputs
            di_addrs = [7200, 7201, 7202, 7208]
            di_names = ["Robot Link", "Error", "Project Running", "ESTOP"]
            
            for addr, name in zip(di_addrs, di_names):
                result = self.client.read_discrete_inputs(addr, count=1, device_id=1)
                if not result.isError():
                    value = result.bits[0]
                    status = "🟢 True" if value else "🔴 False"
                    self.log(f"   {name} ({addr}): {status}")
                    
            # 讀取 Input Registers
            ir_addrs = [7215, 7216]
            ir_names = ["Robot State", "Operation Mode"]
            
            for addr, name in zip(ir_addrs, ir_names):
                result = self.client.read_input_registers(addr, count=1, device_id=1)
                if not result.isError():
                    value = result.registers[0]
                    self.log(f"   {name} ({addr}): {value}")
                    
            self.log("✅ Robot 狀態讀取完成", "SUCCESS")
            self.log("─" * 50)
            
        except Exception as e:
            self.log(f"📊 狀態讀取錯誤: {e}", "ERROR")
            
    def test_base_coords(self):
        """測試 Base 座標"""
        self.read_coordinates(7001, "Base 座標")
        
    def test_tool_coords(self):
        """測試 Tool 座標"""  
        self.read_coordinates(7025, "Tool 座標")
        
    def test_joint_angles(self):
        """測試 Joint 角度"""
        self.read_coordinates(7013, "Joint 角度")
        
    def test_robot_status(self):
        """測試 Robot 狀態"""
        self.read_robot_status()
        
    def test_user_define_area(self):
        """測試 TM Robot User Define Area (9000-9999)"""
        if not self.is_connected:
            self.log("❌ 請先連線", "ERROR")
            return
            
        self.log("👤 測試 TM Robot User Define Area...")
        self.log("📍 位址範圍: 9000-9999 (User-define)")
        
        # 測試幾個 User Define 位址
        test_addresses = [9000, 9001, 9002, 9010, 9020, 9100]
        
        for addr in test_addresses:
            try:
                # 嘗試讀取 Holding Registers (功能碼 03)
                result = self.client.read_holding_registers(addr, count=1, device_id=1)
                
                if result.isError():
                    self.log(f"   位址 {addr}: ❌ 讀取失敗 - {result}")
                else:
                    value = result.registers[0]
                    self.log(f"   位址 {addr}: ✅ 值 = {value} (0x{value:04X})")
                    
            except Exception as e:
                self.log(f"   位址 {addr}: ❌ 錯誤 - {e}")
        
        # 測試寫入功能 (如果支援)
        self.log("\n📝 測試 User Define Area 寫入功能...")
        test_write_addr = 9000
        test_value = 12345
        
        try:
            # 寫入測試值
            write_result = self.client.write_register(test_write_addr, test_value, device_id=1)
            
            if write_result.isError():
                self.log(f"   寫入位址 {test_write_addr}: ❌ 失敗 - {write_result}")
            else:
                self.log(f"   寫入位址 {test_write_addr}: ✅ 成功寫入 {test_value}")
                
                # 讀回驗證
                read_result = self.client.read_holding_registers(test_write_addr, count=1, device_id=1)
                if not read_result.isError():
                    read_value = read_result.registers[0]
                    if read_value == test_value:
                        self.log(f"   驗證讀取: ✅ 值匹配 = {read_value}")
                    else:
                        self.log(f"   驗證讀取: ⚠️ 值不匹配 = {read_value} (預期: {test_value})")
                        
        except Exception as e:
            self.log(f"   寫入測試錯誤: {e}")
        
        self.log("✅ User Define Area 測試完成", "SUCCESS")
        self.log("─" * 50)
        
    def test_all(self):
        """測試所有項目"""
        if not self.is_connected:
            self.log("❌ 請先連線", "ERROR")
            return
            
        self.log("🚀 開始完整測試...")
        self.log("=" * 50)
        
        self.test_base_coords()
        time.sleep(0.2)
        self.test_joint_angles()
        time.sleep(0.2)
        self.test_tool_coords()
        time.sleep(0.2)
        self.test_robot_status()
        
        self.log("🎉 完整測試完成！", "SUCCESS")
        self.log("=" * 50)
        
    def toggle_monitoring(self):
        """切換連續監控模式"""
        if not self.monitoring:
            if not self.is_connected:
                self.log("❌ 請先連線", "ERROR")
                return
                
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.log("🔁 開始連續監控...", "SUCCESS")
        else:
            self.monitoring = False
            self.log("🔁 停止連續監控", "WARNING")
            
    def load_preset(self, preset_type):
        """載入預設測試案例"""
        presets = {
            "base": {
                "function": "Input Registers (04)",
                "address": "7001",
                "count": "12",
                "datatype": "Float32",
                "name": "Base Coordinates"
            },
            "tool": {
                "function": "Input Registers (04)",
                "address": "7025",
                "count": "12",
                "datatype": "Float32",
                "name": "Tool Coordinates"
            },
            "joint": {
                "function": "Input Registers (04)",
                "address": "7013",
                "count": "12",
                "datatype": "Float32",
                "name": "Joint Angles"
            },
            "status": {
                "function": "Discrete Inputs (02)",
                "address": "7200",
                "count": "4",
                "datatype": "Bool",
                "name": "Robot Status"
            },
            "light": {
                "function": "Coils (01)",
                "address": "7206",
                "count": "1",
                "datatype": "Bool",
                "name": "Light Control"
            },
            "userdefine": {
                "function": "Holding Registers (03)",
                "address": "9000",
                "count": "10",
                "datatype": "UInt16",
                "name": "User Define Area"
            }
        }
        
        if preset_type in presets:
            preset = presets[preset_type]
            self.function_var.set(preset["function"])
            self.start_addr_var.set(preset["address"])
            self.count_var.set(preset["count"])
            self.datatype_var.set(preset["datatype"])
            self.test_name_var.set(preset["name"])
            self.log(f"📋 已載入預設: {preset['name']}")
    
    def clear_preset(self):
        """清除預設值"""
        self.function_var.set("Input Registers (04)")
        self.start_addr_var.set("")
        self.count_var.set("")
        self.datatype_var.set("Float32")
        self.test_name_var.set("")
        self.log("🗑️ 已清除預設值")
    
    def execute_user_define_test(self):
        """執行自定義測試"""
        if not self.is_connected:
            self.log("❌ 請先連線", "ERROR")
            return
        
        try:
            # 取得參數
            function = self.function_var.get()
            start_addr = int(self.start_addr_var.get())
            count = int(self.count_var.get())
            datatype = self.datatype_var.get()
            slave_id = int(self.slave_id_var.get())
            test_name = self.test_name_var.get() or "Custom Test"
            
            self.log(f"🚀 執行自定義測試: {test_name}")
            self.log(f"📊 參數: {function}, 位址={start_addr}, 數量={count}, 型別={datatype}, Slave={slave_id}")
            
            # 根據功能碼執行讀取
            if "Coils" in function:
                result = self.client.read_coils(start_addr, count=count, device_id=slave_id)
            elif "Discrete Inputs" in function:
                result = self.client.read_discrete_inputs(start_addr, count=count, device_id=slave_id)
            elif "Holding Registers" in function:
                result = self.client.read_holding_registers(start_addr, count=count, device_id=slave_id)
            elif "Input Registers" in function:
                result = self.client.read_input_registers(start_addr, count=count, device_id=slave_id)
            else:
                self.log("❌ 不支援的功能碼", "ERROR")
                return
            
            if result.isError():
                self.log(f"❌ 讀取失敗: {result}", "ERROR")
                return
            
            # 處理結果
            if hasattr(result, 'bits'):
                # Coils 或 Discrete Inputs
                values = result.bits[:count]
                self.log(f"✅ {test_name} 結果:", "SUCCESS")
                for i, value in enumerate(values):
                    self.log(f"   [{start_addr + i}]: {value}")
            else:
                # Registers
                registers = result.registers[:count]
                self.log(f"📊 原始數據: {registers}")
                
                # 根據資料型別轉換
                converted_values = self.convert_user_data(registers, datatype)
                
                self.log(f"✅ {test_name} 結果:", "SUCCESS")
                
                # 特殊處理座標數據
                if datatype == "Float32" and count >= 6:
                    self.display_user_coordinates(converted_values, test_name)
                else:
                    for i, value in enumerate(converted_values):
                        self.log(f"   [{start_addr + i * (2 if datatype == 'Float32' or datatype == 'Int32' or datatype == 'UInt32' else 1)}]: {value}")
            
            self.log("─" * 50)
            
        except ValueError as e:
            self.log(f"❌ 參數錯誤: {e}", "ERROR")
            messagebox.showerror("參數錯誤", "請檢查輸入的數值格式")
        except Exception as e:
            self.log(f"❌ 測試錯誤: {e}", "ERROR")
    
    def convert_user_data(self, registers, datatype):
        """轉換用戶自定義的數據型別"""
        if datatype == "Raw":
            return registers
        elif datatype == "Bool":
            return [bool(reg) for reg in registers]
        elif datatype == "Int16":
            return [reg if reg < 32768 else reg - 65536 for reg in registers]
        elif datatype == "UInt16":
            return registers
        elif datatype == "Int32":
            values = []
            for i in range(0, len(registers), 2):
                if i + 1 < len(registers):
                    value = struct.unpack('>i', struct.pack('>HH', registers[i], registers[i+1]))[0]
                    values.append(value)
            return values
        elif datatype == "UInt32":
            values = []
            for i in range(0, len(registers), 2):
                if i + 1 < len(registers):
                    value = struct.unpack('>I', struct.pack('>HH', registers[i], registers[i+1]))[0]
                    values.append(value)
            return values
        elif datatype == "Float32":
            values = []
            for i in range(0, len(registers), 2):
                if i + 1 < len(registers):
                    value = struct.unpack('>f', struct.pack('>HH', registers[i], registers[i+1]))[0]
                    values.append(value)
            return values
        else:
            return registers
    
    def display_user_coordinates(self, coords, test_name):
        """顯示用戶自定義的座標數據"""
        if "Joint" in test_name or "joint" in test_name.lower():
            for i, angle in enumerate(coords[:6], 1):
                self.log(f"   Joint {i}: {angle:8.3f}°")
        elif len(coords) >= 6:
            self.log(f"   X:  {coords[0]:8.3f} mm")
            self.log(f"   Y:  {coords[1]:8.3f} mm") 
            self.log(f"   Z:  {coords[2]:8.3f} mm")
            self.log(f"   Rx: {coords[3]:8.3f}°")
            self.log(f"   Ry: {coords[4]:8.3f}°")
            self.log(f"   Rz: {coords[5]:8.3f}°")
        else:
            for i, coord in enumerate(coords):
                self.log(f"   [{i}]: {coord:8.3f}")

    def start_performance_test(self):
        """開始性能測試"""
        if not self.is_connected:
            self.log("❌ 請先連線", "ERROR")
            return
        
        if self.perf_testing:
            self.log("⚠️ 性能測試已在進行中", "WARNING")
            return
        
        # 驗證測試次數
        try:
            test_count = int(self.test_count_var.get())
            if test_count < 1:
                self.log("❌ 測試次數必須大於 0", "ERROR")
                return
            elif test_count > 100000:
                self.log("❌ 測試次數不能超過 100,000", "ERROR")
                return
        except ValueError:
            self.log("❌ 請輸入有效的測試次數", "ERROR")
            return
        
        # 驗證測試間隔
        try:
            interval = int(self.test_interval_var.get())
            if interval < 0:
                self.log("❌ 測試間隔不能為負數", "ERROR")
                return
        except ValueError:
            self.log("❌ 請輸入有效的測試間隔", "ERROR")
            return
        
        # 重置結果
        self.perf_results = []
        self.progress_bar['value'] = 0
        self.progress_var.set("0/0")
        self.avg_time_var.set("-- ms")
        self.min_time_var.set("-- ms")
        self.max_time_var.set("-- ms")
        self.success_rate_var.set("-- %")
        
        # 啟動測試
        self.perf_testing = True
        self.start_perf_btn.config(state="disabled")
        self.stop_perf_btn.config(state="normal")
        
        # 在新線程中執行測試
        self.perf_thread = threading.Thread(target=self.performance_test_loop, daemon=True)
        self.perf_thread.start()
        
        test_type = self.perf_test_var.get()
        
        self.log(f"🚀 開始性能測試: {test_type}")
        self.log(f"📊 測試參數: {test_count}次, 間隔{interval}ms")
    
    def stop_performance_test(self):
        """停止性能測試"""
        self.perf_testing = False
        self.start_perf_btn.config(state="normal")
        self.stop_perf_btn.config(state="disabled")
        self.log("⏹️ 性能測試已停止", "WARNING")
    
    def performance_test_loop(self):
        """性能測試循環"""
        try:
            test_type = self.perf_test_var.get()
            test_count = int(self.test_count_var.get())
            interval = int(self.test_interval_var.get()) / 1000.0  # 轉換為秒
            
            self.progress_bar['maximum'] = test_count
            
            for i in range(test_count):
                if not self.perf_testing:
                    break
                
                # 執行單次測試
                start_time = time.time()
                success = self.execute_single_performance_test(test_type)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # 轉換為毫秒
                
                # 記錄結果
                self.perf_results.append({
                    'time': response_time,
                    'success': success,
                    'timestamp': datetime.now()
                })
                
                # 更新 GUI
                self.root.after(0, self.update_performance_display, i + 1, test_count)
                
                # 等待間隔 (支援 0ms 極限測試)
                if i < test_count - 1 and interval > 0:  # 最後一次不需要等待，0ms 不等待
                    time.sleep(interval)
            
            # 測試完成
            if self.perf_testing:
                self.root.after(0, self.performance_test_completed)
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ 性能測試錯誤: {e}", "ERROR"))
            self.root.after(0, self.stop_performance_test)
    
    def execute_single_performance_test(self, test_type):
        """執行單次性能測試"""
        try:
            if test_type == "Base座標讀取":
                result = self.client.read_input_registers(7001, count=12, device_id=1)
            elif test_type == "Tool座標讀取":
                result = self.client.read_input_registers(7025, count=12, device_id=1)
            elif test_type == "Joint角度讀取":
                result = self.client.read_input_registers(7013, count=12, device_id=1)
            elif test_type == "Robot狀態讀取":
                result = self.client.read_discrete_inputs(7200, count=4, device_id=1)
            elif test_type == "User Define讀取":
                result = self.client.read_holding_registers(9000, count=10, device_id=1)
            elif test_type == "User Define寫入":
                # 測試寫入操作
                import random
                test_value = random.randint(1, 65535)
                result = self.client.write_register(9000, test_value, device_id=1)
            elif test_type == "User Define讀寫":
                # 測試讀寫組合操作
                import random
                test_value = random.randint(1, 65535)
                # 先寫入
                write_result = self.client.write_register(9000, test_value, device_id=1)
                if write_result.isError():
                    return False
                # 再讀取驗證
                result = self.client.read_holding_registers(9000, count=1, device_id=1)
            elif test_type == "混合測試":
                # 執行多種操作的組合
                result1 = self.client.read_input_registers(7001, count=6, device_id=1)  # Base XYZ
                result2 = self.client.read_discrete_inputs(7200, count=2, device_id=1)  # Status
                result = result1 if not result1.isError() else result2
            elif test_type == "極限測試":
                # 最小數據量的極限測試
                result = self.client.read_holding_registers(9000, count=1, device_id=1)
            else:
                return False
            
            return not result.isError()
            
        except Exception:
            return False
    
    def update_performance_display(self, current, total):
        """更新性能測試顯示"""
        # 更新進度
        self.progress_bar['value'] = current
        self.progress_var.set(f"{current}/{total}")
        
        # 計算統計數據
        if self.perf_results:
            times = [r['time'] for r in self.perf_results]
            successes = [r['success'] for r in self.perf_results]
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            success_rate = (sum(successes) / len(successes)) * 100
            
            self.avg_time_var.set(f"{avg_time:.1f} ms")
            self.min_time_var.set(f"{min_time:.1f} ms")
            self.max_time_var.set(f"{max_time:.1f} ms")
            self.success_rate_var.set(f"{success_rate:.1f} %")
    
    def performance_test_completed(self):
        """性能測試完成"""
        self.perf_testing = False
        self.start_perf_btn.config(state="normal")
        self.stop_perf_btn.config(state="disabled")
        
        if self.perf_results:
            times = [r['time'] for r in self.perf_results]
            successes = [r['success'] for r in self.perf_results]
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            success_rate = (sum(successes) / len(successes)) * 100
            
            # 計算 95% 百分位數
            sorted_times = sorted(times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_time
            
            # 計算標準差
            variance = sum((t - avg_time) ** 2 for t in times) / len(times)
            std_dev = variance ** 0.5
            
            test_type = self.perf_test_var.get()
            interval = self.test_interval_var.get()
            
            self.log("🎉 性能測試完成！", "SUCCESS")
            self.log("📊 測試結果統計:")
            self.log(f"   測試類型: {test_type}")
            self.log(f"   測試次數: {len(self.perf_results)}")
            self.log(f"   測試間隔: {interval} ms")
            self.log(f"   平均時間: {avg_time:.2f} ms")
            self.log(f"   最小時間: {min_time:.2f} ms")
            self.log(f"   最大時間: {max_time:.2f} ms")
            self.log(f"   95% 百分位: {p95_time:.2f} ms")
            self.log(f"   標準差: {std_dev:.2f} ms")
            self.log(f"   成功率: {success_rate:.1f}%")
            
            # 特殊提示
            if interval == "0":
                self.log("⚡ 極限測試模式: 無間隔連續測試", "WARNING")
                if avg_time < 5:
                    self.log("🚀 優秀性能: 平均反應時間 < 5ms", "SUCCESS")
                elif avg_time < 10:
                    self.log("✅ 良好性能: 平均反應時間 < 10ms", "SUCCESS")
                else:
                    self.log("⚠️ 注意: 平均反應時間較高，可能需要優化", "WARNING")
            
            if "寫入" in test_type:
                self.log("📝 寫入測試: 包含寫入操作的性能測試")
            
            self.log("─" * 50)
    
    def generate_performance_report(self):
        """生成性能測試報告"""
        if not self.perf_results:
            self.log("❌ 沒有測試結果可生成報告", "ERROR")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tm_robot_performance_report_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("TM Robot 性能測試報告\n")
                f.write("=" * 50 + "\n\n")
                
                # 測試參數
                f.write("測試參數:\n")
                f.write(f"  測試類型: {self.perf_test_var.get()}\n")
                f.write(f"  測試次數: {len(self.perf_results)}\n")
                f.write(f"  測試間隔: {self.test_interval_var.get()} ms\n")
                f.write(f"  測試時間: {self.perf_results[0]['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 統計結果
                times = [r['time'] for r in self.perf_results]
                successes = [r['success'] for r in self.perf_results]
                
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                success_rate = (sum(successes) / len(successes)) * 100
                
                sorted_times = sorted(times)
                p95_index = int(len(sorted_times) * 0.95)
                p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_time
                
                variance = sum((t - avg_time) ** 2 for t in times) / len(times)
                std_dev = variance ** 0.5
                
                f.write("統計結果:\n")
                f.write(f"  平均反應時間: {avg_time:.2f} ms\n")
                f.write(f"  最小反應時間: {min_time:.2f} ms\n")
                f.write(f"  最大反應時間: {max_time:.2f} ms\n")
                f.write(f"  95% 百分位數: {p95_time:.2f} ms\n")
                f.write(f"  標準差: {std_dev:.2f} ms\n")
                f.write(f"  成功率: {success_rate:.1f}%\n\n")
                
                # 詳細數據
                f.write("詳細測試數據:\n")
                f.write("序號\t反應時間(ms)\t成功\t時間戳\n")
                for i, result in enumerate(self.perf_results, 1):
                    f.write(f"{i}\t{result['time']:.2f}\t\t{result['success']}\t{result['timestamp'].strftime('%H:%M:%S.%f')[:-3]}\n")
            
            self.log(f"📈 性能報告已生成: {filename}", "SUCCESS")
            
        except Exception as e:
            self.log(f"📈 生成報告失敗: {e}", "ERROR")

    def monitor_loop(self):
        """監控循環"""
        while self.monitoring and self.is_connected:
            try:
                self.log("🔄 監控中...")
                self.test_all()
                time.sleep(5)  # 每5秒監控一次
            except Exception as e:
                self.log(f"🔄 監控錯誤: {e}", "ERROR")
                break

def main():
    root = tk.Tk()
    app = TMRobotTestGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()