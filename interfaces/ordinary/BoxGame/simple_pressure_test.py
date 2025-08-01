# -*- coding: utf-8 -*-
"""
简单压力渲染测试
Simple Pressure Rendering Test
"""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer

# 导入PyQtGraph版本的渲染器
from box_game_renderer import BoxGameRenderer

class SimplePressureTest(QMainWindow):
    """简单压力测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('简单压力渲染测试')
        self.setGeometry(100, 100, 1200, 600)
        
        # 创建中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建按钮
        self.test_btn = QPushButton('测试压力渲染')
        self.test_btn.clicked.connect(self.test_pressure)
        layout.addWidget(self.test_btn)
        
        self.mode_btn = QPushButton('切换2D/3D')
        self.mode_btn.clicked.connect(self.toggle_mode)
        layout.addWidget(self.mode_btn)
        
        # 创建渲染器
        self.renderer = BoxGameRenderer()
        layout.addWidget(self.renderer)
        
        print("✅ 简单压力测试窗口创建成功")
    
    def test_pressure(self):
        """测试压力渲染"""
        try:
            # 创建测试压力数据
            data = np.zeros((64, 64))
            
            # 添加中心压力
            x, y = np.meshgrid(np.linspace(-2, 2, 64), np.linspace(-2, 2, 64))
            data += np.exp(-(x**2 + y**2) / 0.5)
            
            # 添加噪声
            data += np.random.normal(0, 0.1, (64, 64))
            data = np.clip(data, 0, 1)
            
            print(f"📊 测试数据形状: {data.shape}")
            print(f"📊 数据范围: [{data.min():.3f}, {data.max():.3f}]")
            
            # 更新压力数据
            self.renderer.update_pressure_data(data)
            
            # 更新游戏状态
            game_state = {
                'box_position': [32, 32],
                'box_target_position': [50, 50],
                'current_cop': [32, 32],
                'initial_cop': [32, 32],
                'movement_distance': 0.0,
                'is_contact': True,
                'is_tangential': False,
                'is_sliding': False,
                'consensus_angle': 0.0,
                'consensus_confidence': 1.0,
                'control_mode': 'touchpad',
                'current_system_mode': 'touchpad_only'
            }
            
            self.renderer.update_game_state(game_state)
            
            print("✅ 压力数据已更新")
            
        except Exception as e:
            print(f"❌ 测试压力渲染时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_mode(self):
        """切换2D/3D模式"""
        self.renderer.toggle_heatmap_mode()
        print(f"🎨 当前模式: {self.renderer.heatmap_view_mode}")

def main():
    """主函数"""
    print("🚀 启动简单压力渲染测试...")
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = SimplePressureTest()
    window.show()
    
    print("✅ 测试窗口已显示")
    
    # 运行应用
    result = app.exec_()
    
    print("✅ 简单压力渲染测试完成")
    return result

if __name__ == "__main__":
    main() 