#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COP点移动测试脚本
验证压力数据变化时COP点的移动方向和推箱子区域的变化
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

class COPMovementTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COP点移动测试")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建说明标签
        info_label = QLabel("COP点移动测试：观察压力峰值移动时，推箱子区域中的红点（COP点）是否跟随移动")
        info_label.setStyleSheet("color: white; background-color: #333; padding: 10px; font-size: 14px;")
        layout.addWidget(info_label)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建控制按钮
        self.test_left_right_button = QPushButton("测试左右移动")
        self.test_left_right_button.clicked.connect(self.test_left_right_movement)
        button_layout.addWidget(self.test_left_right_button)
        
        self.test_up_down_button = QPushButton("测试上下移动")
        self.test_up_down_button.clicked.connect(self.test_up_down_movement)
        button_layout.addWidget(self.test_up_down_button)
        
        self.test_diagonal_button = QPushButton("测试对角线移动")
        self.test_diagonal_button.clicked.connect(self.test_diagonal_movement)
        button_layout.addWidget(self.test_diagonal_button)
        
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
        self.test_mode = "center"  # center, left_right, up_down, diagonal
        
        # 创建定时器用于动画
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        print("🎯 COP点移动测试界面已创建")
        print("🎯 请点击测试按钮观察COP点（红点）的移动")
        print("🎯 建议先切换到2D视图进行观察")
    
    def test_left_right_movement(self):
        """测试左右移动 - 压力峰值从左到右移动"""
        print("🎯 开始测试左右移动...")
        self.test_mode = "left_right"
        self.test_center = [16, 32]  # 从左侧开始
        self.test_step = 0
        self.animation_timer.start(500)  # 每500ms更新一次
    
    def test_up_down_movement(self):
        """测试上下移动 - 压力峰值从上到下移动"""
        print("🎯 开始测试上下移动...")
        self.test_mode = "up_down"
        self.test_center = [32, 16]  # 从上方开始
        self.test_step = 0
        self.animation_timer.start(500)  # 每500ms更新一次
    
    def test_diagonal_movement(self):
        """测试对角线移动 - 压力峰值从左上到右下移动"""
        print("🎯 开始测试对角线移动...")
        self.test_mode = "diagonal"
        self.test_center = [16, 16]  # 从左上开始
        self.test_step = 0
        self.animation_timer.start(500)  # 每500ms更新一次
    
    def switch_to_2d(self):
        """切换到2D视图"""
        print("🎨 切换到2D视图...")
        self.renderer.toggle_heatmap_mode()
    
    def update_animation(self):
        """更新动画 - 移动压力峰值"""
        # 清除之前的数据
        self.current_test_data = np.zeros((64, 64))
        
        # 根据测试类型移动峰值
        if self.test_mode == "left_right":
            # 从左到右移动
            new_x = 16 + self.test_step * 2
            if new_x > 48:
                self.animation_timer.stop()
                print("🎯 左右移动测试完成")
                return
            self.test_center = [new_x, 32]
            print(f"🎯 左右移动: 峰值位置 ({new_x}, 32)")
        elif self.test_mode == "up_down":
            # 从上到下移动
            new_y = 16 + self.test_step * 2
            if new_y > 48:
                self.animation_timer.stop()
                print("🎯 上下移动测试完成")
                return
            self.test_center = [32, new_y]
            print(f"🎯 上下移动: 峰值位置 (32, {new_y})")
        elif self.test_mode == "diagonal":
            # 对角线移动
            new_x = 16 + self.test_step * 2
            new_y = 16 + self.test_step * 2
            if new_x > 48 or new_y > 48:
                self.animation_timer.stop()
                print("🎯 对角线移动测试完成")
                return
            self.test_center = [new_x, new_y]
            print(f"🎯 对角线移动: 峰值位置 ({new_x}, {new_y})")
        
        # 创建压力数据 - 使用更明显的峰值
        x, y = np.meshgrid(np.arange(64), np.arange(64))
        distance = np.sqrt((x - self.test_center[0])**2 + (y - self.test_center[1])**2)
        self.current_test_data = 0.004 * np.exp(-(distance**2) / (2 * 4**2))  # 更小的标准差，更尖锐的峰值
        
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
    
    window = COPMovementTest()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 