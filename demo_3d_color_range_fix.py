#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D热力图颜色范围修复演示
Demo of 3D heatmap color range fix
"""

import numpy as np
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces/ordinary/BoxGame'))

class ColorRangeDemo(QMainWindow):
    """颜色范围修复演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D热力图颜色范围修复演示")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建标题
        title = QLabel("🎨 3D热力图颜色范围修复演示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF6B35; margin: 10px;")
        layout.addWidget(title)
        
        # 创建说明
        description = QLabel("""
        🔧 修复内容：
        • 3D热力图现在使用设置的颜色范围，而不是硬编码的值
        • 设置界面的颜色范围控制同时影响2D和3D热力图
        • 支持实时动态调整颜色范围
        
        💡 使用方法：
        • 点击下方按钮测试不同的颜色范围
        • 观察3D热力图的颜色变化
        • 控制台会显示当前的颜色范围设置
        """)
        description.setStyleSheet("font-size: 12px; color: #4ECDC4; margin: 10px; background-color: #2C3E50; padding: 10px; border-radius: 5px;")
        layout.addWidget(description)
        
        # 创建渲染器
        try:
            from box_game_renderer import BoxGameRenderer
            self.renderer = BoxGameRenderer()
            layout.addWidget(self.renderer)
            
            # 生成测试数据
            self.test_data = np.random.exponential(0.001, (64, 64))
            self.test_data[25:35, 25:35] += 0.002  # 添加接触区域
            self.renderer.update_pressure_data(self.test_data)
            
            # 切换到3D模式
            self.renderer.heatmap_view_mode = '3d'
            
            print("✅ 渲染器创建成功")
            
        except Exception as e:
            error_label = QLabel(f"❌ 渲染器创建失败: {e}")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label)
            self.renderer = None
            return
        
        # 创建控制按钮
        button_layout = QHBoxLayout()
        
        # 测试按钮
        test_ranges = [
            ("小范围 (0.0-0.005)", [0.0, 0.005]),
            ("中等范围 (0.0-0.01)", [0.0, 0.01]),
            ("大范围 (0.0-0.02)", [0.0, 0.02]),
            ("自定义范围 (0.001-0.008)", [0.001, 0.008]),
            ("高对比度 (0.002-0.01)", [0.002, 0.01])
        ]
        
        for name, (vmin, vmax) in test_ranges:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
            """)
            btn.clicked.connect(lambda checked, vmin=vmin, vmax=vmax, name=name: self.test_color_range(vmin, vmax, name))
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        # 创建状态显示
        self.status_label = QLabel("当前颜色范围: [0.0, 0.005]")
        self.status_label.setStyleSheet("font-size: 14px; color: #E74C3C; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # 创建信息显示
        self.info_label = QLabel("点击上方按钮测试不同的颜色范围")
        self.info_label.setStyleSheet("font-size: 12px; color: #95A5A6; margin: 10px;")
        layout.addWidget(self.info_label)
        
        # 启动渲染
        if self.renderer:
            self.renderer.start_rendering()
    
    def test_color_range(self, vmin, vmax, name):
        """测试颜色范围"""
        if not self.renderer:
            return
        
        print(f"\n🎨 测试颜色范围: {name}")
        print(f"   设置范围: [{vmin:.6f}, {vmax:.6f}]")
        
        # 设置颜色范围
        self.renderer.set_color_range(vmin, vmax)
        
        # 重新渲染
        self.renderer.render_pressure_distribution()
        
        # 更新状态显示
        current_range = self.renderer.y_lim
        self.status_label.setText(f"当前颜色范围: [{current_range[0]:.6f}, {current_range[1]:.6f}]")
        self.info_label.setText(f"✅ 已应用 {name} - 观察3D热力图的颜色变化")
        
        print(f"   ✅ 颜色范围已更新: [{current_range[0]:.6f}, {current_range[1]:.6f}]")
        
        # 验证设置是否正确
        if abs(current_range[0] - vmin) < 1e-6 and abs(current_range[1] - vmax) < 1e-6:
            print(f"   ✅ 颜色范围设置正确")
        else:
            print(f"   ❌ 颜色范围设置错误")
            print(f"      期望: [{vmin:.6f}, {vmax:.6f}]")
            print(f"      实际: [{current_range[0]:.6f}, {current_range[1]:.6f}]")

def main():
    """主函数"""
    print("🚀 3D热力图颜色范围修复演示")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # 创建演示窗口
    demo = ColorRangeDemo()
    demo.show()
    
    print("✅ 演示窗口已创建")
    print("💡 点击按钮测试不同的颜色范围")
    print("💡 观察3D热力图的颜色变化")
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 