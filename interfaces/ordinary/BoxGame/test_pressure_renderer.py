#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力渲染器测试脚本
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

# 添加路径
sys.path.append(os.path.dirname(__file__))

from box_game_renderer import BoxGameRenderer

class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("压力渲染器测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建渲染器
        self.renderer = BoxGameRenderer()
        layout.addWidget(self.renderer)
        
        # 创建定时器来更新压力数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_test_data)
        self.timer.start(100)  # 每100ms更新一次
        
        print("🧪 测试窗口已创建")
    
    def update_test_data(self):
        """更新测试数据"""
        try:
            # 创建动态测试数据
            test_data = np.zeros((64, 64))
            
            # 添加一些动态压力点
            import time
            t = time.time()
            
            # 中心压力点
            center_x, center_y = 32, 32
            for i in range(64):
                for j in range(64):
                    distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
                    if distance < 15:
                        # 添加动态变化
                        dynamic_factor = 0.5 + 0.5 * np.sin(t * 2)
                        test_data[i, j] = 0.003 * dynamic_factor * np.exp(-distance / 10)
            
            # 添加第二个压力点
            point2_x, point2_y = 16, 48
            for i in range(64):
                for j in range(64):
                    distance = np.sqrt((i - point2_x)**2 + (j - point2_y)**2)
                    if distance < 8:
                        dynamic_factor = 0.3 + 0.7 * np.sin(t * 3)
                        test_data[i, j] += 0.002 * dynamic_factor * np.exp(-distance / 5)
            
            # 更新渲染器
            self.renderer.update_pressure_data(test_data)
            
            # 更新游戏状态
            game_state = {
                'box_position': [32, 32],
                'box_target_position': [48, 16],
                'current_cop': [32, 32],
                'initial_cop': [30, 30],
                'movement_distance': 2.0,
                'is_contact': True,
                'is_tangential': False,
                'is_sliding': False,
                'consensus_angle': 45.0,
                'consensus_confidence': 0.8,
                'control_mode': 'touchpad',
                'current_system_mode': 'touchpad_only'
            }
            self.renderer.update_game_state(game_state)
            
        except Exception as e:
            print(f"❌ 更新测试数据失败: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print("🚀 测试应用已启动")
    print("💡 提示：")
    print("  - 左侧显示游戏区域")
    print("  - 右侧显示压力分布")
    print("  - 压力数据会动态变化")
    print("  - 按F11可以切换全屏")
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 