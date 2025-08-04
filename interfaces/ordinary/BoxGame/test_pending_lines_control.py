# -*- coding: utf-8 -*-
"""
测试中间连接线控制功能
Test script for pending lines control
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
import pyqtgraph as pg

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

def test_pending_lines_control():
    """测试中间连接线控制功能"""
    print("🧪 开始测试中间连接线控制功能...")
    
    # 创建PyQt应用程序
    app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("中间连接线控制测试")
    main_window.setGeometry(100, 100, 1000, 700)
    
    # 创建中央部件
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # 创建布局
    layout = QVBoxLayout(central_widget)
    
    # 创建控制按钮
    button_layout = QHBoxLayout()
    
    show_button = QPushButton("显示中间连接线")
    hide_button = QPushButton("隐藏中间连接线")
    toggle_button = QPushButton("切换显示状态")
    
    button_layout.addWidget(show_button)
    button_layout.addWidget(hide_button)
    button_layout.addWidget(toggle_button)
    
    layout.addLayout(button_layout)
    
    # 创建PyQtGraph绘图部件
    plot_widget = pg.PlotWidget()
    plot_widget.setAspectLocked(True)
    plot_widget.setRange(xRange=[0, 64], yRange=[0, 64])
    plot_widget.setLabel('left', 'Y轴')
    plot_widget.setLabel('bottom', 'X轴')
    plot_widget.setTitle('中间连接线控制测试')
    layout.addWidget(plot_widget)
    
    try:
        # 导入优化后的路径可视化管理器
        from path_visualization_manager_optimized import PathVisualizationManagerOptimized
        
        # 创建路径可视化管理器实例
        path_manager = PathVisualizationManagerOptimized(plot_widget)
        print("✅ 路径可视化管理器创建成功")
        
        # 创建测试路径数据 - 包含已完成和未完成的路径
        print("\n🗺️ 创建测试路径数据...")
        test_path_data = {
            'path_points': [
                {'x': 10, 'y': 10, 'type': 'start', 'completed': True, 'connection_type': 'solid'},
                {'x': 20, 'y': 15, 'type': 'waypoint', 'completed': True, 'connection_type': 'solid'},
                {'x': 30, 'y': 25, 'type': 'checkpoint', 'completed': False, 'connection_type': 'solid'},
                {'x': 40, 'y': 35, 'type': 'waypoint', 'completed': False, 'connection_type': 'solid'},
                {'x': 50, 'y': 45, 'type': 'target', 'completed': False, 'connection_type': 'solid'},
                {'x': 15, 'y': 50, 'type': 'waypoint', 'completed': False, 'connection_type': 'solid'},
                {'x': 25, 'y': 55, 'type': 'waypoint', 'completed': False, 'connection_type': 'solid'},
                {'x': 35, 'y': 60, 'type': 'waypoint', 'completed': False, 'connection_type': 'solid'},
                {'x': 45, 'y': 55, 'type': 'waypoint', 'completed': False, 'connection_type': 'solid'},
                {'x': 55, 'y': 50, 'type': 'waypoint', 'completed': False, 'connection_type': 'solid'}
            ],
            'current_target': {'x': 30, 'y': 25, 'name': '检查点1'},
            'next_target': {'x': 40, 'y': 35, 'name': '路径点2'},
            'progress': {
                'completed_points': 2,
                'total_points': 10,
                'is_completed': False
            },
            'target_distance': 15.5,
            'direction_angle': 45.0,
            'has_navigation': True
        }
        
        # 更新路径数据
        print("📊 更新路径数据...")
        path_manager.update_path_data(test_path_data)
        print("✅ 路径数据更新成功")
        
        # 初始状态：禁用中间连接线
        print("\n🎯 初始状态：禁用中间连接线")
        path_manager.set_performance_options({
            'show_pending_lines': False
        })
        
        # 渲染路径可视化
        print("🎨 渲染路径可视化...")
        box_position = np.array([15.0, 12.0])
        path_manager.render_complete_path_visualization(box_position)
        print("✅ 路径可视化渲染成功")
        
        # 按钮事件处理
        def show_pending_lines():
            print("🎯 显示中间连接线")
            path_manager.set_performance_options({'show_pending_lines': True})
            path_manager.clear_path_visualization()
            path_manager.render_complete_path_visualization(box_position)
        
        def hide_pending_lines():
            print("🎯 隐藏中间连接线")
            path_manager.set_performance_options({'show_pending_lines': False})
            path_manager.clear_path_visualization()
            path_manager.render_complete_path_visualization(box_position)
        
        def toggle_pending_lines():
            current_state = path_manager.show_pending_lines
            new_state = not current_state
            print(f"🎯 切换中间连接线显示: {current_state} -> {new_state}")
            path_manager.set_performance_options({'show_pending_lines': new_state})
            path_manager.clear_path_visualization()
            path_manager.render_complete_path_visualization(box_position)
        
        # 连接按钮信号
        show_button.clicked.connect(show_pending_lines)
        hide_button.clicked.connect(hide_pending_lines)
        toggle_button.clicked.connect(toggle_pending_lines)
        
        print("\n🎉 中间连接线控制测试准备完成！")
        print("💡 提示：")
        print("  - 绿色实线：已完成的路径")
        print("  - 青色虚线：未完成的路径（中间连接线）")
        print("  - 使用按钮控制中间连接线的显示/隐藏")
        print("  - 初始状态：中间连接线已隐藏")
        
        # 显示窗口
        main_window.show()
        
        # 运行应用程序
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return 1
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    result = test_pending_lines_control()
    sys.exit(result) 