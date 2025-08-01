#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试BoxGame渲染器的缩放功能
Test script for BoxGame renderer zoom functionality
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces/ordinary/BoxGame'))

try:
    from box_game_renderer import BoxGameRenderer
    print("✅ 成功导入BoxGameRenderer")
except ImportError as e:
    print(f"❌ 导入BoxGameRenderer失败: {e}")
    sys.exit(1)

def create_test_pressure_data():
    """创建测试压力数据"""
    # 创建一个64x64的测试压力数据
    test_data = np.zeros((64, 64))
    
    # 在中心区域添加一些压力
    center_x, center_y = 32, 32
    for i in range(64):
        for j in range(64):
            distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
            if distance < 15:
                test_data[i, j] = 0.003 * np.exp(-distance / 10)
    
    return test_data

def test_zoom_functionality():
    """测试缩放功能"""
    app = QApplication(sys.argv)
    
    # 创建渲染器
    renderer = BoxGameRenderer()
    renderer.setWindowTitle("BoxGame渲染器 - 缩放功能测试")
    renderer.resize(1200, 800)
    renderer.show()
    
    # 添加测试压力数据
    test_data = create_test_pressure_data()
    renderer.update_pressure_data(test_data)
    
    # 添加测试游戏状态
    test_state = {
        'box_position': [32.0, 32.0],
        'box_target_position': [50.0, 50.0],
        'current_cop': [35.0, 35.0],
        'initial_cop': [30.0, 30.0],
        'is_contact': True,
        'is_tangential': False,
        'is_sliding': False,
        'control_mode': 'touchpad',
        'current_system_mode': 'touchpad_only'
    }
    renderer.update_game_state(test_state)
    
    # 设置调试级别
    renderer.set_debug_level(2)
    
    # 显示使用说明
    print("\n" + "="*60)
    print("🎮 BoxGame渲染器缩放功能测试")
    print("="*60)
    print("📋 测试说明:")
    print("  1. 在游戏区域或压力视图上拖拽鼠标进行缩放")
    print("  2. 按R键重置视图到默认状态")
    print("  3. 按H键切换2D/3D热力图模式")
    print("  4. 按F11键切换全屏模式")
    print("  5. 观察控制台输出的视图范围变化信息")
    print("="*60)
    
    # 启动应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_zoom_functionality() 