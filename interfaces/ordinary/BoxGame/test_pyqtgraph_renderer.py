# -*- coding: utf-8 -*-
"""
PyQtGraph渲染器测试脚本
Test Script for PyQtGraph Renderer

用于测试PyQtGraph版本的BoxGameRenderer
"""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer
import time

# 导入PyQtGraph版本的渲染器
from box_game_renderer import BoxGameRenderer

class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQtGraph渲染器测试')
        self.setGeometry(100, 100, 1400, 800)
        
        # 创建中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建控制按钮
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton('开始测试')
        self.start_btn.clicked.connect(self.start_test)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('停止测试')
        self.stop_btn.clicked.connect(self.stop_test)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.toggle_3d_btn = QPushButton('切换2D/3D')
        self.toggle_3d_btn.clicked.connect(self.toggle_3d_mode)
        control_layout.addWidget(self.toggle_3d_btn)
        
        layout.addLayout(control_layout)
        
        # 创建渲染器
        self.renderer = BoxGameRenderer()
        layout.addWidget(self.renderer)
        
        # 测试数据
        self.test_data = None
        self.is_testing = False
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.update_test_data)
        
        # 初始化测试数据
        self.init_test_data()
    
    def init_test_data(self):
        """初始化测试数据"""
        # 创建64x64的压力数据
        size = (64, 64)
        rows, cols = size
        
        # 创建基础压力分布
        x = np.linspace(-2, 2, cols)
        y = np.linspace(-2, 2, rows)
        X, Y = np.meshgrid(x, y)
        
        # 创建多个压力中心
        centers = [
            (0, 0, 1.0),
            (-1, -1, 0.8),
            (1, 1, 0.6),
            (-0.5, 1, 0.4),
            (1, -0.5, 0.3)
        ]
        
        data = np.zeros((rows, cols))
        for cx, cy, intensity in centers:
            r_squared = (X - cx)**2 + (Y - cy)**2
            data += intensity * np.exp(-r_squared / 0.5)
        
        # 添加噪声
        noise = np.random.normal(0, 0.05, (rows, cols))
        data += noise
        data = np.clip(data, 0, 1)
        
        self.test_data = data
    
    def start_test(self):
        """开始测试"""
        self.is_testing = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # 设置定时器，30Hz更新
        self.test_timer.start(33)  # 约30Hz
        
        print("🚀 开始PyQtGraph渲染器测试")
    
    def stop_test(self):
        """停止测试"""
        self.is_testing = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.test_timer.stop()
        
        print("⏹️ 停止PyQtGraph渲染器测试")
    
    def toggle_3d_mode(self):
        """切换2D/3D模式"""
        self.renderer.toggle_heatmap_mode()
        current_mode = "3D" if self.renderer.heatmap_view_mode == '3d' else "2D"
        print(f"🎨 切换到{current_mode}模式")
    
    def update_test_data(self):
        """更新测试数据"""
        if not self.is_testing:
            return
        
        # 添加一些变化
        noise = np.random.normal(0, 0.02, self.test_data.shape)
        current_data = self.test_data + noise
        current_data = np.clip(current_data, 0, 1)
        
        # 更新压力数据
        self.renderer.update_pressure_data(current_data)
        
        # 更新游戏状态
        game_state = {
            'box_position': [32 + 10 * np.sin(time.time()), 32 + 10 * np.cos(time.time())],
            'box_target_position': [50, 50],
            'current_cop': [32 + 5 * np.sin(time.time() * 2), 32 + 5 * np.cos(time.time() * 2)],
            'initial_cop': [32, 32],
            'movement_distance': 5.0,
            'is_contact': True,
            'is_tangential': False,
            'is_sliding': False,
            'consensus_angle': 45.0,
            'consensus_confidence': 0.8,
            'control_mode': 'touchpad',
            'current_system_mode': 'touchpad_only'
        }
        
        self.renderer.update_game_state(game_state)
        
        # 更新显示
        self.renderer.update_display()

def main():
    """主函数"""
    print("🚀 启动PyQtGraph渲染器测试...")
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    # 运行应用
    result = app.exec_()
    
    print("✅ PyQtGraph渲染器测试完成")
    return result

if __name__ == "__main__":
    main() 