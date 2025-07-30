#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D可视化演示脚本
Demo script for 3D visualization
"""

import sys
import os
import numpy as np
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_demo_pressure_data():
    """创建演示用的压力数据"""
    data = np.zeros((64, 64))
    
    # 创建多个压力点模拟手指接触
    pressure_points = [
        (20, 20, 0.08),  # 左上角，高强度
        (44, 44, 0.06),  # 右下角，中强度
        (32, 32, 0.04),  # 中心，低强度
        (15, 50, 0.05),  # 左下角
        (50, 15, 0.07),  # 右上角
    ]
    
    for x, y, intensity in pressure_points:
        for i in range(64):
            for j in range(64):
                distance = np.sqrt((i - x)**2 + (j - y)**2)
                if distance < 12:
                    data[i, j] += intensity * np.exp(-distance**2 / 30)
    
    # 添加一些随机噪声
    noise = np.random.normal(0, 0.002, (64, 64))
    data += noise
    
    # 确保数据非负
    data = np.maximum(data, 0)
    
    return data

def main():
    """主演示函数"""
    print("🎨 3D可视化演示启动")
    print("=" * 50)
    
    # 创建QApplication
    app = QApplication(sys.argv)
    
    try:
        # 导入主窗口
        from box_game_app_optimized import BoxGameMainWindow
        
        # 创建主窗口
        main_window = BoxGameMainWindow()
        main_window.show()
        
        print("✅ 主窗口创建成功")
        print("🎮 演示说明:")
        print("   1. 点击'连接传感器'按钮")
        print("   2. 点击'3D选项'按钮调整3D渲染参数")
        print("   3. 点击'平滑选项'按钮调整平滑参数")
        print("   4. 点击'2D热力图'按钮切换到3D模式")
        print("   5. 观察美观的3D压力分布可视化")
        
        # 创建演示数据更新定时器
        demo_timer = QTimer()
        demo_data_index = 0
        
        def update_demo_data():
            """更新演示数据"""
            nonlocal demo_data_index
            
            # 创建不同的演示数据模式
            patterns = [
                create_demo_pressure_data(),  # 多点压力
                create_single_pressure_data(),  # 单点压力
                create_moving_pressure_data(demo_data_index),  # 移动压力
                create_wave_pressure_data(demo_data_index),  # 波动压力
            ]
            
            current_data = patterns[demo_data_index % len(patterns)]
            
            # 发送数据到渲染器
            if hasattr(main_window, 'renderer') and main_window.renderer:
                main_window.renderer.update_pressure_data(current_data)
            
            demo_data_index += 1
        
        # 设置定时器，每2秒更新一次演示数据
        demo_timer.timeout.connect(update_demo_data)
        demo_timer.start(2000)  # 2秒间隔
        
        print("🔄 演示数据将每2秒自动更新")
        print("💡 提示：可以手动连接传感器查看真实数据")
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ 演示启动失败: {e}")
        import traceback
        traceback.print_exc()

def create_single_pressure_data():
    """创建单点压力数据"""
    data = np.zeros((64, 64))
    
    # 中心压力点
    center_x, center_y = 32, 32
    for i in range(64):
        for j in range(64):
            distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
            if distance < 20:
                data[i, j] = 0.1 * np.exp(-distance**2 / 100)
    
    return data

def create_moving_pressure_data(frame):
    """创建移动压力数据"""
    data = np.zeros((64, 64))
    
    # 移动的压力点
    angle = frame * 0.1
    radius = 15
    x = 32 + radius * np.cos(angle)
    y = 32 + radius * np.sin(angle)
    
    for i in range(64):
        for j in range(64):
            distance = np.sqrt((i - x)**2 + (j - y)**2)
            if distance < 10:
                data[i, j] = 0.08 * np.exp(-distance**2 / 25)
    
    return data

def create_wave_pressure_data(frame):
    """创建波动压力数据"""
    data = np.zeros((64, 64))
    
    # 波动效果
    for i in range(64):
        for j in range(64):
            wave = np.sin(i * 0.3 + frame * 0.2) * np.cos(j * 0.3 + frame * 0.1)
            data[i, j] = 0.05 * (wave + 1) * np.exp(-((i-32)**2 + (j-32)**2) / 200)
    
    return data

if __name__ == "__main__":
    main() 