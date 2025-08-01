#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XY坐标问题测试和修复脚本
测试并修复2D热力图和推箱子游戏区域的XY坐标颠倒问题
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces/ordinary/BoxGame'))
from box_game_renderer import BoxGameRenderer

class XYCoordinateTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XY坐标问题测试和修复")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建控制按钮
        self.fix_xy_button = QPushButton("修复XY坐标")
        self.fix_xy_button.clicked.connect(self.fix_xy_coordinates)
        button_layout.addWidget(self.fix_xy_button)
        
        self.toggle_xy_swap_button = QPushButton("切换XY交换")
        self.toggle_xy_swap_button.clicked.connect(self.toggle_xy_swap)
        button_layout.addWidget(self.toggle_xy_swap_button)
        
        self.reset_button = QPushButton("重置视图")
        self.reset_button.clicked.connect(self.reset_view)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        # 创建渲染器
        self.renderer = BoxGameRenderer()
        layout.addWidget(self.renderer)
        
        # 设置定时器模拟传感器数据
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.simulate_sensor_data)
        self.sensor_timer.start(3000)  # 每3秒更新一次
        
        self.update_count = 0
        
        print("🔍 XY坐标问题测试开始")
        print("📊 测试目标：验证并修复2D热力图和推箱子游戏区域的XY坐标一致性")
        print("🎯 预期结果：手指移动方向在两个视图中应该完全一致")
        print()
    
    def fix_xy_coordinates(self):
        """修复XY坐标问题"""
        print("🔧 开始修复XY坐标问题...")
        
        # 方法1：禁用XY交换
        self.renderer.use_xy_swap = False
        print("✅ 已禁用XY交换")
        
        # 方法2：强制设置性能模式为"低性能"以避免完整预处理
        self.renderer.set_performance_mode("低性能")
        print("✅ 已设置性能模式为低性能")
        
        # 方法3：强制刷新视图
        self.renderer.reset_view()
        print("✅ 已重置视图")
        
        # 方法4：清除预处理缓存
        self.renderer._preprocessed_cache = None
        print("✅ 已清除预处理缓存")
        
        print("🔧 XY坐标修复完成")
        print()
    
    def toggle_xy_swap(self):
        """切换XY交换状态"""
        current_state = self.renderer.use_xy_swap
        self.renderer.use_xy_swap = not current_state
        print(f"🔄 XY交换状态: {'启用' if self.renderer.use_xy_swap else '禁用'}")
        
        # 清除缓存并刷新
        self.renderer._preprocessed_cache = None
        self.renderer.pressure_data_changed = True
        print("✅ 已清除缓存并设置刷新标志")
        print()
    
    def reset_view(self):
        """重置视图"""
        print("🔄 重置视图...")
        self.renderer.reset_view()
        print("✅ 视图已重置")
        print()
    
    def simulate_sensor_data(self):
        """模拟传感器数据 - 创建明显的移动模式"""
        self.update_count += 1
        
        # 创建64x64的压力数据
        pressure_data = np.zeros((64, 64))
        x, y = np.meshgrid(np.arange(64), np.arange(64))
        
        # 创建移动的压力峰值 - 从左到右移动
        center_x = 10 + 40 * np.sin(self.update_count * 0.3)  # 在10-50范围内移动
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
        print(f"🔧 当前XY交换状态: {'启用' if self.renderer.use_xy_swap else '禁用'}")
        print(f"🔧 当前性能模式: {self.renderer.performance_mode}")
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
    test_window = XYCoordinateTest()
    test_window.show()
    
    print("🚀 XY坐标问题测试已启动")
    print("📋 测试说明：")
    print("   1. 观察2D热力图中压力峰值的移动方向")
    print("   2. 观察推箱子游戏区域中COP点的移动方向")
    print("   3. 如果方向不一致，点击'修复XY坐标'按钮")
    print("   4. 可以尝试'切换XY交换'来测试不同设置")
    print("   5. 按H键可以切换2D/3D热力图模式")
    print("   6. 按R键可以重置视图")
    print()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 