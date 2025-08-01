#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
坐标一致性测试脚本
测试2D热力图和推箱子游戏区域的坐标系统是否一致
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces/ordinary/BoxGame'))
from box_game_renderer import BoxGameRenderer

class CoordinateConsistencyTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("坐标一致性测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建渲染器
        self.renderer = BoxGameRenderer()
        layout.addWidget(self.renderer)
        
        # 设置定时器模拟传感器数据
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.simulate_sensor_data)
        self.sensor_timer.start(2000)  # 每2秒更新一次
        
        self.update_count = 0
        
        print("🔍 坐标一致性测试开始")
        print("📊 测试目标：验证2D热力图和推箱子游戏区域的坐标系统一致性")
        print("🎯 预期结果：手指移动方向在两个视图中应该一致")
        print()
    
    def simulate_sensor_data(self):
        """模拟传感器数据 - 创建明显的移动模式"""
        self.update_count += 1
        
        # 创建64x64的压力数据
        pressure_data = np.zeros((64, 64))
        x, y = np.meshgrid(np.arange(64), np.arange(64))
        
        # 创建移动的压力峰值 - 从左到右移动
        center_x = 10 + 40 * np.sin(self.update_count * 0.5)  # 在10-50范围内移动
        center_y = 32  # 固定在中间
        
        # 创建高斯分布的峰值
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        peak_height = 0.004
        sigma = 3
        pressure_data = peak_height * np.exp(-(distance**2) / (2 * sigma**2))
        
        # 添加一些噪声
        pressure_data += 0.0001 * np.random.randn(64, 64)
        pressure_data = np.clip(pressure_data, 0.0, 0.005)
        
        # 更新渲染器
        self.renderer.update_pressure_data(pressure_data)
        
        # 打印状态
        print(f"📊 更新 {self.update_count}: 压力峰值位置 ({center_x:.1f}, {center_y:.1f})")
        print(f"🎯 移动方向: {'从左到右' if center_x > 25 else '从右到左'}")
        print(f"📈 压力范围: [{pressure_data.min():.6f}, {pressure_data.max():.6f}]")
        print()
        
        # 每5次更新后切换热力图模式
        if self.update_count % 5 == 0:
            print("🔄 切换热力图模式...")
            self.renderer.toggle_heatmap_mode()
            print(f"🎨 当前模式: {self.renderer.heatmap_view_mode}")
            print()

def main():
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    test_window = CoordinateConsistencyTest()
    test_window.show()
    
    print("🚀 坐标一致性测试已启动")
    print("📋 测试说明：")
    print("   1. 观察2D热力图中压力峰值的移动方向")
    print("   2. 观察推箱子游戏区域中COP点的移动方向")
    print("   3. 两个方向应该一致")
    print("   4. 按H键可以切换2D/3D热力图模式")
    print("   5. 按R键可以重置视图")
    print()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 