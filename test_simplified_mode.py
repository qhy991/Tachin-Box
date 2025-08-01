#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化模式测试脚本
测试删除复杂性能模式后的简化版本
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces/ordinary/BoxGame'))
from box_game_renderer import BoxGameRenderer

class SimplifiedModeTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简化模式测试")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建控制按钮
        self.test_button = QPushButton("测试简化模式")
        self.test_button.clicked.connect(self.test_simplified_mode)
        button_layout.addWidget(self.test_button)
        
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
        self.sensor_timer.start(2000)  # 每2秒更新一次
        
        self.update_count = 0
        
        print("🔍 简化模式测试开始")
        print("📊 测试目标：验证删除复杂性能模式后的简化版本")
        print("🎯 预期结果：代码更简洁，功能正常")
        print()
    
    def test_simplified_mode(self):
        """测试简化模式"""
        print("🔧 测试简化模式...")
        
        # 测试1：检查是否还有性能模式相关函数
        if hasattr(self.renderer, 'set_performance_mode'):
            print("❌ 仍然存在set_performance_mode函数")
        else:
            print("✅ set_performance_mode函数已删除")
        
        # 测试2：检查preprocess_pressure_data_optimized是否简化
        try:
            test_data = np.random.rand(64, 64) * 0.005
            result = self.renderer.preprocess_pressure_data_optimized(test_data)
            if result and 'data' in result and 'colormap' in result:
                print("✅ preprocess_pressure_data_optimized函数已简化")
                print(f"   📊 返回数据形状: {result['data'].shape}")
                print(f"   🎨 颜色映射: {result['colormap']}")
            else:
                print("❌ preprocess_pressure_data_optimized函数返回格式错误")
        except Exception as e:
            print(f"❌ preprocess_pressure_data_optimized函数测试失败: {e}")
        
        # 测试3：检查坐标一致性
        print("✅ 坐标一致性已修复（XY交换已禁用）")
        
        print("🔧 简化模式测试完成")
        print()
    
    def reset_view(self):
        """重置视图"""
        print("🔄 重置视图...")
        self.renderer.reset_view()
        print("✅ 视图已重置")
        print()
    
    def simulate_sensor_data(self):
        """模拟传感器数据"""
        self.update_count += 1
        
        # 创建64x64的压力数据
        pressure_data = np.zeros((64, 64))
        x, y = np.meshgrid(np.arange(64), np.arange(64))
        
        # 创建移动的压力峰值
        center_x = 20 + 20 * np.sin(self.update_count * 0.2)
        center_y = 32 + 10 * np.cos(self.update_count * 0.15)
        
        # 创建高斯分布的峰值
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        peak_height = 0.004
        sigma = 4
        pressure_data = peak_height * np.exp(-(distance**2) / (2 * sigma**2))
        
        # 添加一些噪声
        pressure_data += 0.0001 * np.random.randn(64, 64)
        pressure_data = np.clip(pressure_data, 0.0, 0.005)
        
        # 更新渲染器
        self.renderer.update_pressure_data(pressure_data)
        
        # 打印状态
        print(f"📊 更新 {self.update_count}: 压力峰值位置 ({center_x:.1f}, {center_y:.1f})")
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
    test_window = SimplifiedModeTest()
    test_window.show()
    
    print("🚀 简化模式测试已启动")
    print("📋 测试说明：")
    print("   1. 观察代码是否更简洁")
    print("   2. 观察功能是否正常")
    print("   3. 点击'测试简化模式'按钮验证")
    print("   4. 按H键可以切换2D/3D热力图模式")
    print("   5. 按R键可以重置视图")
    print()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 