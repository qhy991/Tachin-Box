# -*- coding: utf-8 -*-
"""
优化渲染器测试脚本
Optimized Renderer Test Script

用于测试优化渲染器是否能正确显示2D和3D压力分布
"""

import sys
import os
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer

# 添加路径
sys.path.append(os.path.dirname(__file__))

def generate_test_pressure_data():
    """生成测试压力数据"""
    # 创建一个64x64的测试数据
    data = np.zeros((64, 64))
    
    # 添加一些模拟的压力点
    center_x, center_y = 32, 32
    for i in range(64):
        for j in range(64):
            distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
            if distance < 15:
                data[i, j] = 0.005 * np.exp(-distance / 5)
    
    # 添加一些噪声
    noise = np.random.normal(0, 0.0001, (64, 64))
    data += noise
    
    return data

class OptimizedRendererTestWindow(QMainWindow):
    """优化渲染器测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("优化渲染器测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建按钮
        self.test_2d_btn = QPushButton("测试2D模式")
        self.test_2d_btn.clicked.connect(self.test_2d_mode)
        layout.addWidget(self.test_2d_btn)
        
        self.test_3d_btn = QPushButton("测试3D模式")
        self.test_3d_btn.clicked.connect(self.test_3d_mode)
        layout.addWidget(self.test_3d_btn)
        
        self.switch_mode_btn = QPushButton("切换2D/3D模式")
        self.switch_mode_btn.clicked.connect(self.switch_mode)
        layout.addWidget(self.switch_mode_btn)
        
        # 创建结果显示标签
        self.result_label = QLabel("点击按钮开始测试...")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
        
        # 初始化渲染器
        self.init_renderer()
        
        # 生成测试数据
        self.test_data = generate_test_pressure_data()
        
        # 当前模式
        self.current_mode = '2d'
    
    def init_renderer(self):
        """初始化渲染器"""
        try:
            from interfaces.ordinary.BoxGame.box_game_renderer_optimized import BoxGameRendererOptimized
            
            # 创建应用程序
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            # 创建渲染器
            self.renderer = BoxGameRendererOptimized()
            self.renderer.show()
            
            print("✅ 优化渲染器初始化成功")
            self.result_label.setText("优化渲染器已初始化，可以开始测试")
            
        except Exception as e:
            print(f"❌ 优化渲染器初始化失败: {e}")
            self.result_label.setText(f"优化渲染器初始化失败: {str(e)}")
            self.renderer = None
    
    def test_2d_mode(self):
        """测试2D模式"""
        if not self.renderer:
            self.result_label.setText("渲染器未初始化")
            return
        
        try:
            # 设置2D模式
            self.renderer.set_3d_rendering_options({'heatmap_view_mode': '2d'})
            
            # 更新压力数据
            self.renderer.update_pressure_data(self.test_data)
            
            # 更新游戏状态
            state_info = {
                'is_contact': True,
                'is_sliding': False,
                'current_cop': (32.0, 32.0),
                'initial_cop': (30.0, 30.0),
                'movement_distance': 2.0,
                'box_position': np.array([32.0, 32.0]),
                'box_target_position': np.array([35.0, 35.0]),
                'consensus_angle': 45.0,
                'consensus_confidence': 0.8
            }
            self.renderer.update_game_state(state_info)
            
            self.result_label.setText("2D模式测试完成，请查看右侧压力分布图")
            print("✅ 2D模式测试完成")
            
        except Exception as e:
            self.result_label.setText(f"2D模式测试失败: {str(e)}")
            print(f"❌ 2D模式测试失败: {e}")
    
    def test_3d_mode(self):
        """测试3D模式"""
        if not self.renderer:
            self.result_label.setText("渲染器未初始化")
            return
        
        try:
            # 设置3D模式
            self.renderer.set_3d_rendering_options({'heatmap_view_mode': '3d'})
            
            # 更新压力数据
            self.renderer.update_pressure_data(self.test_data)
            
            # 更新游戏状态
            state_info = {
                'is_contact': True,
                'is_sliding': False,
                'current_cop': (32.0, 32.0),
                'initial_cop': (30.0, 30.0),
                'movement_distance': 2.0,
                'box_position': np.array([32.0, 32.0]),
                'box_target_position': np.array([35.0, 35.0]),
                'consensus_angle': 45.0,
                'consensus_confidence': 0.8
            }
            self.renderer.update_game_state(state_info)
            
            self.result_label.setText("3D模式测试完成，请查看右侧压力分布图")
            print("✅ 3D模式测试完成")
            
        except Exception as e:
            self.result_label.setText(f"3D模式测试失败: {str(e)}")
            print(f"❌ 3D模式测试失败: {e}")
    
    def switch_mode(self):
        """切换2D/3D模式"""
        if not self.renderer:
            self.result_label.setText("渲染器未初始化")
            return
        
        try:
            # 切换模式
            if self.current_mode == '2d':
                self.current_mode = '3d'
                self.renderer.set_3d_rendering_options({'heatmap_view_mode': '3d'})
                self.result_label.setText("已切换到3D模式")
            else:
                self.current_mode = '2d'
                self.renderer.set_3d_rendering_options({'heatmap_view_mode': '2d'})
                self.result_label.setText("已切换到2D模式")
            
            # 更新压力数据
            self.renderer.update_pressure_data(self.test_data)
            
            print(f"✅ 已切换到{self.current_mode.upper()}模式")
            
        except Exception as e:
            self.result_label.setText(f"模式切换失败: {str(e)}")
            print(f"❌ 模式切换失败: {e}")

def main():
    """主函数"""
    print("🧪 优化渲染器测试工具")
    print("=" * 30)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = OptimizedRendererTestWindow()
    window.show()
    
    print("💡 提示：在窗口中点击按钮测试2D/3D模式")
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 