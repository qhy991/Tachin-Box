# -*- coding: utf-8 -*-
"""
压力渲染测试脚本
Pressure Rendering Test Script
"""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer
import time

# 导入PyQtGraph版本的渲染器
from box_game_renderer import BoxGameRenderer

class PressureTestWindow(QMainWindow):
    """压力渲染测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('压力渲染测试')
        self.setGeometry(100, 100, 1400, 800)
        
        # 创建中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建控制按钮布局
        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout)
        
        # 创建测试按钮
        self.test_btn = QPushButton('开始/停止测试')
        self.test_btn.clicked.connect(self.toggle_test)
        control_layout.addWidget(self.test_btn)
        
        # 创建模式切换按钮
        self.mode_btn = QPushButton('切换2D/3D模式')
        self.mode_btn.clicked.connect(self.toggle_mode)
        control_layout.addWidget(self.mode_btn)
        
        # 创建渲染器
        self.renderer = BoxGameRenderer()
        main_layout.addWidget(self.renderer)
        
        # 测试状态
        self.is_testing = False
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.update_test)
        
        # 初始化测试数据
        self.init_test_data()
        
        print("✅ 压力渲染测试窗口创建成功")
    
    def init_test_data(self):
        """初始化测试数据"""
        # 创建64x64的压力数据
        size = (64, 64)
        rows, cols = size
        
        # 创建多个压力中心
        data = np.zeros((rows, cols))
        
        # 中心压力
        x = np.linspace(-2, 2, cols)
        y = np.linspace(-2, 2, rows)
        X, Y = np.meshgrid(x, y)
        
        # 添加多个高斯分布
        centers = [(32, 32), (16, 16), (48, 48), (32, 16), (16, 48)]
        for cx, cy in centers:
            data += np.exp(-((X - (cx-32)/16)**2 + (Y - (cy-32)/16)**2) / 0.5)
        
        # 添加噪声
        noise = np.random.normal(0, 0.1, (rows, cols))
        data += noise
        data = np.clip(data, 0, 1)
        
        self.test_data = data
        print("✅ 测试数据初始化完成")
        print(f"📊 数据形状: {data.shape}")
        print(f"📊 数据范围: [{data.min():.3f}, {data.max():.3f}]")
    
    def toggle_test(self):
        """切换测试状态"""
        if self.is_testing:
            self.stop_test()
        else:
            self.start_test()
    
    def toggle_mode(self):
        """切换2D/3D模式"""
        self.renderer.toggle_heatmap_mode()
        print(f"🎨 当前模式: {self.renderer.heatmap_view_mode}")
    
    def start_test(self):
        """开始测试"""
        self.is_testing = True
        self.test_btn.setText('停止测试')
        self.test_timer.start(200)  # 5Hz更新
        print("🚀 开始压力渲染测试")
    
    def stop_test(self):
        """停止测试"""
        self.is_testing = False
        self.test_btn.setText('开始测试')
        self.test_timer.stop()
        print("⏹️ 停止压力渲染测试")
    
    def update_test(self):
        """更新测试数据"""
        if not self.is_testing:
            return
        
        try:
            # 添加一些变化
            t = time.time()
            noise = np.random.normal(0, 0.05, self.test_data.shape)
            
            # 创建动态压力数据
            current_data = self.test_data.copy()
            
            # 添加移动的压力中心
            center_x = 32 + 8 * np.sin(t * 0.5)
            center_y = 32 + 8 * np.cos(t * 0.5)
            
            x = np.linspace(-2, 2, 64)
            y = np.linspace(-2, 2, 64)
            X, Y = np.meshgrid(x, y)
            
            # 添加移动的高斯分布
            moving_pressure = np.exp(-((X - (center_x-32)/16)**2 + (Y - (center_y-32)/16)**2) / 0.3)
            current_data += moving_pressure * 0.5
            
            current_data += noise
            current_data = np.clip(current_data, 0, 1)
            
            # 更新压力数据
            self.renderer.update_pressure_data(current_data)
            
            # 更新游戏状态
            game_state = {
                'box_position': [center_x, center_y],
                'box_target_position': [50, 50],
                'current_cop': [center_x + 2, center_y + 2],
                'initial_cop': [32, 32],
                'movement_distance': 3.0,
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
            
        except Exception as e:
            print(f"❌ 更新测试数据时出错: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    print("🚀 启动压力渲染测试...")
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = PressureTestWindow()
    window.show()
    
    print("✅ 测试窗口已显示")
    
    # 运行应用
    result = app.exec_()
    
    print("✅ 压力渲染测试完成")
    return result

if __name__ == "__main__":
    main() 