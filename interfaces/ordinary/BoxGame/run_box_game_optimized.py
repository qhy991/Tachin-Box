#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推箱子游戏启动脚本 - 高性能优化版
Box Game Launcher - Optimized Version

启动高性能优化版推箱子智能传感器游戏
"""

import sys
import os
from pathlib import Path

# 🔧 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import sys
import numpy as np
import time
from pathlib import Path
from collections import deque
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QGridLayout, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# 🔍 检查真实传感器可用性
REAL_SENSOR_AVAILABLE = False
try:
    from data_processing.data_handler import DataHandler
    from backends.sensor_driver import LargeUsbSensorDriver
    REAL_SENSOR_AVAILABLE = True
    print("✅ 真实传感器驱动已加载")
except ImportError as e:
    print(f"⚠️ 真实传感器驱动不可用，将使用模拟传感器: {e}")

# 🎮 帧率配置常量
class FrameRateConfig:
    """帧率配置类 - 集中管理所有帧率设置"""
    
    # 预设帧率配置
    PERFORMANCE_MODES = {
        "低性能": {
            "sensor_fps": 15,          # 传感器采集：15 FPS
            "simulation_fps": 10,      # 模拟传感器：10 FPS  
            "renderer_fps": 15,        # 渲染器：15 FPS
            "core_fps": 15,           # 游戏核心：15 FPS
            "description": "省电模式，适合低配置设备"
        },
        "标准": {
            "sensor_fps": 30,          # 传感器采集：30 FPS
            "simulation_fps": 20,      # 模拟传感器：20 FPS
            "renderer_fps": 30,        # 渲染器：30 FPS
            "core_fps": 30,           # 游戏核心：30 FPS
            "description": "平衡模式，标准体验"
        },
        "高性能": {
            "sensor_fps": 60,          # 传感器采集：60 FPS
            "simulation_fps": 30,      # 模拟传感器：30 FPS
            "renderer_fps": 60,        # 渲染器：60 FPS
            "core_fps": 60,           # 游戏核心：60 FPS
            "description": "高帧率模式，流畅体验"
        },
        "极限": {
            "sensor_fps": 120,         # 传感器采集：120 FPS
            "simulation_fps": 60,      # 模拟传感器：60 FPS
            "renderer_fps": 120,       # 渲染器：120 FPS
            "core_fps": 120,          # 游戏核心：120 FPS
            "description": "极限性能，需要高配置设备"
        }
    }
    
    # 当前性能模式
    current_mode = "极限"
    
    @classmethod
    def get_current_config(cls):
        """获取当前帧率配置"""
        return cls.PERFORMANCE_MODES[cls.current_mode]
    
    @classmethod
    def set_performance_mode(cls, mode_name):
        """设置性能模式"""
        if mode_name in cls.PERFORMANCE_MODES:
            cls.current_mode = mode_name
            print(f"🎯 性能模式已设置为: {mode_name}")
            print(f"📊 配置: {cls.PERFORMANCE_MODES[mode_name]['description']}")
            return True
        return False
    
    @classmethod
    def get_interval_ms(cls, fps_type):
        """获取对应的毫秒间隔"""
        config = cls.get_current_config()
        fps = config.get(fps_type, 30)
        return max(8, int(1000 / fps))  # 最小8ms间隔，对应125 FPS上限


class RealSensorInterface:
    """真实传感器接口"""
    
    def __init__(self):
        self.data_handler = None
        self.is_connected = False
        
    def connect(self, port="0"):
        """连接传感器"""
        if not REAL_SENSOR_AVAILABLE:
            return False
        
        try:
            self.data_handler = DataHandler(LargeUsbSensorDriver, max_len=64)
            if self.data_handler.connect(port):
                self.is_connected = True
                return True
        except Exception as e:
            print(f"传感器连接失败: {e}")
        
        return False
    
    def disconnect(self):
        """断开连接"""
        if self.data_handler and self.is_connected:
            try:
                self.data_handler.disconnect()
                self.is_connected = False
                return True
            except:
                pass
        return False
    
    def start_reading(self):
        """开始读取数据"""
        return self.is_connected
    
    def stop_reading(self):
        """停止读取数据"""
        pass
    
    def get_pressure_matrix(self):
        """获取压力矩阵"""
        if not self.is_connected or not self.data_handler:
            return None
        
        try:
            self.data_handler.trigger()
            if len(self.data_handler.value) > 0:
                latest_data = self.data_handler.value[-1]
                return np.maximum(latest_data, 0).astype(np.float32)
        except Exception as e:
            print(f"获取传感器数据失败: {e}")
        
        return None


class SimulatedSensorInterface:
    """模拟传感器接口 - 用于测试"""
    
    def __init__(self):
        self.is_connected = False
        self.pressure_matrix = np.zeros((64, 64))  # 修改为64x64以匹配真实传感器
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.generate_simulated_data)
        self.mouse_pos = (32, 32)  # 中心点改为(32, 32)
        
    def connect(self, port="0"):
        """连接模拟传感器"""
        return True
    
    def disconnect(self):
        """断开连接"""
        self.stop_reading()
        return True
    
    def start_reading(self):
        """开始读取数据"""
        self.is_connected = True
        # 🚀 使用动态帧率配置
        interval_ms = FrameRateConfig.get_interval_ms("simulation_fps")
        self.simulation_timer.start(interval_ms)
        print(f"🎯 模拟传感器启动，帧率: {1000/interval_ms:.1f} FPS")
        return True
    
    def stop_reading(self):
        """停止读取数据"""
        self.is_connected = False
        self.simulation_timer.stop()
    
    def get_pressure_matrix(self):
        """获取压力矩阵"""
        if self.is_connected:
            return self.pressure_matrix.copy()
        return None
    
    def generate_simulated_data(self):
        """生成模拟压力数据"""
        # 🔄 创建模拟压力分布
        self.pressure_matrix = np.zeros((64, 64))  # 修改为64x64
        
        # 🎯 添加高斯分布的压力点
        center_x, center_y = self.mouse_pos
        
        # 🚫 默认不生成压力，只有在用户主动交互时才生成
        # 检查是否有用户交互（通过检查鼠标位置是否在中心）
        if abs(center_x - 32) < 1 and abs(center_y - 32) < 1:
            # 如果鼠标在中心位置，说明没有用户交互，不生成压力
            return
        
        # 用户有交互时，生成压力数据
        # 随机移动压力中心（模拟手指移动）
        center_x += np.random.normal(0, 0.3)  # 减少随机移动幅度
        center_y += np.random.normal(0, 0.3)  # 减少随机移动幅度
        center_x = np.clip(center_x, 5, 59)  # 修改边界为5-59
        center_y = np.clip(center_y, 5, 59)  # 修改边界为5-59
        self.mouse_pos = (center_x, center_y)
        
        # 生成压力分布
        y, x = np.ogrid[:64, :64]  # 修改为64x64
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # 高斯分布 + 随机噪声
        base_pressure = np.exp(-distance**2 / (2 * 3**2)) * 0.8
        noise = np.random.normal(0, 0.01, (64, 64))  # 减少噪声
        
        self.pressure_matrix = np.clip(base_pressure + noise, 0, 1)
        
        # 🎲 随机添加/移除压力（模拟接触/离开）
        if np.random.random() < 0.1:  # 10% 概率无压力
            self.pressure_matrix *= 0.1
    
    def set_mouse_position(self, x, y):
        """设置鼠标位置（用于交互）"""
        # 将游戏坐标转换为传感器坐标
        # 游戏坐标: x范围(-4,4), y范围(-3,3)
        # 传感器坐标: 64x64, 中心在(32,32)
        sensor_x = int((x + 4) / 8 * 64)  # 修改映射公式
        sensor_y = int((y + 3) / 6 * 64)  # 修改映射公式
        sensor_x = np.clip(sensor_x, 0, 63)  # 修改边界为0-63
        sensor_y = np.clip(sensor_y, 0, 63)  # 修改边界为0-63
        self.mouse_pos = (sensor_x, sensor_y)
    
    def update_frame_rate(self):
        """更新帧率设置"""
        if self.is_connected:
            interval_ms = FrameRateConfig.get_interval_ms("simulation_fps")
            self.simulation_timer.setInterval(interval_ms)
            print(f"🎯 模拟传感器帧率已更新: {1000/interval_ms:.1f} FPS")


class SensorDataThread(QThread):
    """传感器数据采集线程"""
    
    data_received = pyqtSignal(np.ndarray)
    status_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.sensor_interface = None
        self.sensor_type = "unknown"  # "real", "simulated" 或 "unknown"
        
        # 🚫 不自动创建传感器接口，等待明确连接
        print("📡 传感器线程已创建，等待连接...")
    
    def setup_simulated_sensor(self):
        """设置模拟传感器"""
        self.sensor_interface = SimulatedSensorInterface()
        self.sensor_type = "simulated"
        print("📱 模拟传感器接口已准备")
    
    def setup_real_sensor(self):
        """设置真实传感器"""
        if REAL_SENSOR_AVAILABLE:
            try:
                self.sensor_interface = RealSensorInterface()
                self.sensor_type = "real"
                print("✅ 真实传感器接口已准备")
                return True
            except Exception as e:
                print(f"❌ 真实传感器初始化失败: {e}")
                self.setup_simulated_sensor()
                return False
        else:
            print("❌ 真实传感器组件不可用")
            return False
    
    def connect_sensor(self, port="0", use_real=False):
        """连接传感器"""
        # 先停止当前数据采集
        if self.running:
            self.stop_reading()
        
        # 设置传感器类型
        if use_real:
            if not self.setup_real_sensor():
                return False
        else:
            self.setup_simulated_sensor()
        
        # 连接传感器
        try:
            if self.sensor_interface.connect(port):
                self.status_changed.emit(f"传感器连接成功 ({self.sensor_type})")
                return True
            else:
                self.status_changed.emit("传感器连接失败")
                return False
        except Exception as e:
            self.status_changed.emit(f"连接错误: {str(e)}")
            return False
    
    def disconnect_sensor(self):
        """断开传感器连接"""
        if self.running:
            self.stop_reading()
        
        if self.sensor_interface:
            success = self.sensor_interface.disconnect()
            if success:
                self.status_changed.emit("传感器已断开")
            return success
        return True
    
    def start_reading(self):
        """开始读取数据"""
        if not self.sensor_interface:
            self.status_changed.emit("传感器未连接")
            return False
        
        success = self.sensor_interface.start_reading()
        if success:
            self.running = True
            self.start()
            current_fps = 1000 / FrameRateConfig.get_interval_ms("sensor_fps")
            self.status_changed.emit(f"数据采集中... ({current_fps:.1f} FPS)")
            return True
        else:
            self.status_changed.emit("传感器启动失败")
            return False
    
    def stop_reading(self):
        """停止读取数据"""
        self.running = False
        if self.sensor_interface:
            self.sensor_interface.stop_reading()
        self.status_changed.emit("数据采集已停止")
        
        # 等待线程结束
        if self.isRunning():
            self.wait(1000)
    
    def run(self):
        """线程主循环"""
        frame_count = 0
        last_time = time.time()
        
        while self.running:
            try:
                if self.sensor_interface:
                    pressure_data = self.sensor_interface.get_pressure_matrix()
                    if pressure_data is not None:
                        self.data_received.emit(pressure_data)
                        frame_count += 1
                        
                        # 🕐 每100帧显示一次实际帧率
                        if frame_count % 100 == 0:
                            current_time = time.time()
                            elapsed = current_time - last_time
                            actual_fps = 100 / elapsed if elapsed > 0 else 0
                            expected_fps = 1000 / FrameRateConfig.get_interval_ms("sensor_fps")
                            print(f"📡 传感器实际帧率: {actual_fps:.1f} FPS (期望: {expected_fps:.1f} FPS)")
                            print(f"📊 传感器配置: {FrameRateConfig.current_mode}模式, 间隔: {FrameRateConfig.get_interval_ms('sensor_fps')}ms")
                            last_time = current_time
                
                # 🚀 使用动态帧率配置
                interval_ms = FrameRateConfig.get_interval_ms("sensor_fps")
                self.msleep(interval_ms)
                
            except Exception as e:
                print(f"❌ 传感器数据读取失败: {e}")
                self.status_changed.emit(f"读取错误: {str(e)}")
                break
    
    def set_mouse_position(self, x, y):
        """设置鼠标位置（仅模拟传感器）"""
        if isinstance(self.sensor_interface, SimulatedSensorInterface):
            self.sensor_interface.set_mouse_position(x, y)
    
    def is_sensor_connected(self):
        """检查传感器是否已连接"""
        if self.sensor_interface:
            return getattr(self.sensor_interface, 'is_connected', False)
        return False
    
    def update_frame_rate(self):
        """更新帧率设置"""
        if isinstance(self.sensor_interface, SimulatedSensorInterface):
            self.sensor_interface.update_frame_rate()

# 📊 检查依赖
def check_dependencies():
    """检查必要的依赖"""
    required_packages = [
        ('numpy', 'NumPy'),
        ('PyQt5', 'PyQt5'),
        ('matplotlib', 'Matplotlib'),
        ('scipy', 'SciPy'),
        ('skimage', 'scikit-image')
    ]
    missing_packages = []
    for package, display_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {display_name} 已安装")
        except ImportError:
            print(f"❌ {display_name} 未安装")
            missing_packages.append(display_name)
    if missing_packages:
        print(f"\n缺少以下依赖包: {', '.join(missing_packages)}")
        print("请使用以下命令安装:")
        print("pip install numpy PyQt5 matplotlib scipy scikit-image")
        return False
    return True

def check_modules():
    """检查自定义模块"""
    required_modules = [
        'interfaces/ordinary/BoxGame/box_game_core_optimized.py',
        'interfaces/ordinary/BoxGame/box_game_renderer.py',
        'box_game_app_optimized.py'
    ]
    missing_modules = []
    for module_file in required_modules:
        module_path = project_root / module_file
        if module_path.exists():
            print(f"✅ {module_file} 存在")
        else:
            print(f"❌ {module_file} 不存在")
            missing_modules.append(module_file)
    if missing_modules:
        print(f"\n缺少以下模块文件: {', '.join(missing_modules)}")
        return False
    return True

def main():
    """主函数 - 仅检查依赖和模块，不自动启动游戏"""
    print("🚀 推箱子游戏启动器 v2.0 (高性能优化)")
    print("=" * 50)
    # 🔍 检查依赖
    print("\n📋 检查Python依赖...")
    if not check_dependencies():
        sys.exit(1)
    # 🔍 检查模块
    print("\n📁 检查项目模块...")
    if not check_modules():
        sys.exit(1)
    # 🔍 检查传感器接口
    print("\n📡 检查传感器接口...")
    try:
        # 测试传感器接口
        test_thread = SensorDataThread()
        test_thread.setup_simulated_sensor()
        if test_thread.connect_sensor(use_real=False):
            print("✅ 传感器接口测试成功")
            test_thread.disconnect_sensor()
        else:
            print("❌ 传感器接口测试失败")
            sys.exit(1)
        
        print("\n✅ 所有检查通过！")
        print("💡 提示：要启动游戏，请运行 'python box_game_app_optimized.py'")
        print("💡 或者导入传感器接口类到其他模块中使用")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断程序")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序检查失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print("\n🐛 详细错误信息:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 