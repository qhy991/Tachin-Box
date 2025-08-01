#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D山峰效果测试脚本
Test script for 3D peak effect

测试BoxGameRenderer的3D视图是否能显示明显的山峰效果
"""

import sys
import os
import numpy as np
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces/ordinary/BoxGame'))
from box_game_renderer import BoxGameRenderer


class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D山峰效果测试")
        self.setGeometry(100, 100, 1400, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建渲染器
        self.renderer = BoxGameRenderer()
        layout.addWidget(self.renderer)
        
        # 创建模拟传感器数据定时器
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.simulate_sensor_data)
        self.sensor_timer.start(100)  # 每100ms更新一次数据
        
        # 数据更新计数器
        self.update_count = 0
        
        print("🚀 3D山峰效果测试已启动")
        print("📋 测试说明:")
        print("   1. 观察3D视图是否显示明显的山峰效果")
        print("   2. 压力峰值应该形成明显的3D山峰")
        print("   3. 低值区域也应该有可见的高度变化")
        print("   4. 按R键重置视图")
        print("   5. 按H键切换2D/3D模式")
        print("   6. 观察控制台输出，确认增强算法生效")
        print()
        
    def simulate_sensor_data(self):
        """模拟传感器数据更新 - 创建明显的山峰效果"""
        self.update_count += 1
        
        # 创建64x64的压力数据
        pressure_data = np.zeros((64, 64))
        x, y = np.meshgrid(np.arange(64), np.arange(64))
        
        # 创建多个移动的压力山峰
        for i in range(3):
            # 主山峰 - 在中心区域移动
            center_x = 32 + 15 * np.sin(self.update_count * 0.05 + i * 2)
            center_y = 32 + 10 * np.cos(self.update_count * 0.03 + i * 1.5)
            
            # 创建高斯分布的山峰
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            peak_height = 0.004 * (1 + 0.5 * np.sin(self.update_count * 0.1 + i))
            sigma = 5 + 2 * np.sin(self.update_count * 0.08 + i)
            
            peak = peak_height * np.exp(-(distance**2) / (2 * sigma**2))
            pressure_data += peak
        
        # 添加一些随机噪声
        pressure_data += 0.0001 * np.random.randn(64, 64)
        
        # 确保数据在合理范围内
        pressure_data = np.clip(pressure_data, 0.0, 0.005)
        
        # 更新渲染器
        self.renderer.update_pressure_data(pressure_data)
        
        # 每50次更新打印一次状态
        if self.update_count % 50 == 0:
            print(f"📊 已更新 {self.update_count} 次传感器数据")
            print(f"🎯 当前压力范围: [{pressure_data.min():.6f}, {pressure_data.max():.6f}]")
            print(f"📈 压力峰值位置: ({np.unravel_index(pressure_data.argmax(), pressure_data.shape)})")
            print()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print("✅ 测试窗口已显示")
    print("🔍 请观察以下现象:")
    print("   1. 3D视图是否显示明显的山峰效果")
    print("   2. 压力峰值是否形成明显的3D山峰")
    print("   3. 低值区域是否有可见的高度变化")
    print("   4. 控制台是否显示增强算法的调试信息")
    print("   5. 山峰是否随时间移动")
    print()
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 