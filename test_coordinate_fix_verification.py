#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
坐标映射修复验证脚本
简单测试上下移动，验证2D热力图和推箱子区域的移动方向是否一致
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces/ordinary/BoxGame'))
from box_game_renderer import BoxGameRenderer

class CoordinateFixVerification(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("坐标映射修复验证")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建说明标签
        info_label = QLabel("坐标映射修复验证：测试上下移动，观察2D热力图和推箱子区域的移动方向是否一致")
        info_label.setStyleSheet("color: white; background-color: #333; padding: 10px; font-size: 14px;")
        layout.addWidget(info_label)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建控制按钮
        self.test_up_down_button = QPushButton("测试上下移动")
        self.test_up_down_button.clicked.connect(self.test_up_down_movement)
        button_layout.addWidget(self.test_up_down_button)
        
        self.switch_to_2d_button = QPushButton("切换到2D视图")
        self.switch_to_2d_button.clicked.connect(self.switch_to_2d)
        button_layout.addWidget(self.switch_to_2d_button)
        
        self.reset_button = QPushButton("重置视图")
        self.reset_button.clicked.connect(self.reset_view)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        # 创建渲染器
        self.renderer = BoxGameRenderer()
        layout.addWidget(self.renderer)
        
        # 初始化测试数据
        self.current_test_data = np.zeros((64, 64))
        self.test_center = [32, 32]
        self.test_step = 0
        
        # 创建定时器用于动画
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        print("🎯 坐标映射修复验证界面已创建")
        print("🎯 请先切换到2D视图，然后点击'测试上下移动'按钮")
        print("🎯 观察2D热力图中压力峰值的移动方向")
        print("🎯 观察推箱子区域中红点（COP点）的移动方向")
        print("🎯 两个方向的移动应该完全一致")
    
    def test_up_down_movement(self):
        """测试上下移动 - 压力峰值从上到下移动"""
        print("🎯 开始测试上下移动...")
        self.test_center = [32, 16]  # 从上方开始
        self.test_step = 0
        self.animation_timer.start(1000)  # 每1秒更新一次，便于观察
    
    def switch_to_2d(self):
        """切换到2D视图"""
        print("🎨 切换到2D视图...")
        self.renderer.toggle_heatmap_mode()
    
    def update_animation(self):
        """更新动画 - 移动压力峰值"""
        # 清除之前的数据
        self.current_test_data = np.zeros((64, 64))
        
        # 从上到下移动
        new_y = 16 + self.test_step * 4
        if new_y > 48:
            self.animation_timer.stop()
            print("🎯 上下移动测试完成")
            return
        self.test_center = [32, new_y]
        print(f"🎯 上下移动: 峰值位置 (32, {new_y})")
        
        # 🔧 修复坐标映射问题：确保数据生成方式正确
        # 创建坐标网格
        x, y = np.meshgrid(np.arange(64), np.arange(64))
        
        # 计算到峰值位置的距离
        # 注意：在numpy数组中，第一个索引是行（Y），第二个索引是列（X）
        # 所以我们需要确保坐标映射正确
        distance = np.sqrt((x - self.test_center[0])**2 + (y - self.test_center[1])**2)
        
        # 生成高斯分布的压力数据
        self.current_test_data = 0.004 * np.exp(-(distance**2) / (2 * 2**2))
        
        # 🔧 关键修复：转置数据以匹配PyQtGraph的期望格式
        # PyQtGraph的ImageItem期望数据格式为 [Y, X]，但我们的生成方式需要转置
        self.current_test_data = self.current_test_data.T
        
        print(f"🎯 数据生成完成: 峰值位置({self.test_center[0]}, {self.test_center[1]}), 数据形状{self.current_test_data.shape}")
        
        # 更新渲染器
        self.renderer.update_pressure_data(self.current_test_data)
        self.test_step += 1
    
    def reset_view(self):
        """重置视图"""
        print("🔄 重置视图...")
        self.renderer.reset_view()
        self.animation_timer.stop()

def main():
    app = QApplication(sys.argv)
    
    # 设置PyQtGraph样式
    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')
    
    window = CoordinateFixVerification()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 