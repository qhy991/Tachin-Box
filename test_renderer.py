#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试渲染器是否正常工作
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# 添加路径
sys.path.append(os.path.dirname(__file__))

def test_renderer():
    """测试渲染器"""
    print("🧪 开始测试渲染器...")
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 测试优化渲染器导入
    try:
        from interfaces.ordinary.BoxGame.box_game_renderer_optimized import BoxGameRendererOptimized
        print("✅ 优化渲染器导入成功")
        
        # 创建主窗口
        main_window = QMainWindow()
        main_window.setWindowTitle("渲染器测试")
        main_window.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建渲染器
        renderer = BoxGameRendererOptimized()
        layout.addWidget(renderer)
        
        # 启动渲染器
        renderer.start_rendering()
        
        # 发送测试数据
        test_pressure = np.random.rand(64, 64) * 0.1
        renderer.update_pressure_data(test_pressure)
        
        test_state = {
            'is_contact': True,
            'is_sliding': False,
            'current_cop': (32, 32),
            'initial_cop': (30, 30),
            'movement_distance': 2.0,
            'box_position': np.array([32.0, 32.0]),
            'box_target_position': np.array([35.0, 35.0]),
            'consensus_angle': 45.0,
            'consensus_confidence': 0.8,
            'control_mode': 'active'
        }
        renderer.update_game_state(test_state)
        
        print("✅ 渲染器测试数据已发送")
        
        # 显示窗口
        main_window.show()
        
        print("✅ 渲染器测试窗口已显示")
        print("💡 如果看到2D游戏区域和压力分布图，说明渲染器工作正常")
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"❌ 优化渲染器导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 渲染器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_renderer() 