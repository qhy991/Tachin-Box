# -*- coding: utf-8 -*-
"""
测试优化后的路径可视化管理器
Test script for optimized path visualization manager
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

def test_optimized_path_manager():
    """测试优化后的路径可视化管理器"""
    print("🧪 开始测试优化后的路径可视化管理器...")
    
    # 创建PyQt应用程序
    app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("路径可视化管理器测试 - 优化版")
    main_window.setGeometry(100, 100, 800, 600)
    
    # 创建中央部件
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # 创建布局
    layout = QVBoxLayout(central_widget)
    
    # 创建PyQtGraph绘图部件
    plot_widget = pg.PlotWidget()
    plot_widget.setAspectLocked(True)
    plot_widget.setRange(xRange=[0, 64], yRange=[0, 64])
    plot_widget.setLabel('left', 'Y轴')
    plot_widget.setLabel('bottom', 'X轴')
    plot_widget.setTitle('路径可视化测试 - 优化版')
    layout.addWidget(plot_widget)
    
    try:
        # 导入优化后的路径可视化管理器
        from path_visualization_manager_optimized import PathVisualizationManagerOptimized
        
        # 创建路径可视化管理器实例
        path_manager = PathVisualizationManagerOptimized(plot_widget)
        print("✅ 路径可视化管理器创建成功")
        
        # 测试性能选项设置
        print("\n🔧 测试性能选项设置...")
        path_manager.set_performance_options({
            'max_points_to_render': 30,
            'point_render_interval': 2,
            'enable_debug_output': True,
            'animation_enabled': True,
            'show_pending_lines': False  # 禁用中间连接线
        })
        print("✅ 性能选项设置成功")
        
        # 创建测试路径数据
        print("\n🗺️ 创建测试路径数据...")
        test_path_data = {
            'path_points': [
                {'x': 10, 'y': 10, 'type': 'start', 'completed': True},
                {'x': 20, 'y': 15, 'type': 'waypoint', 'completed': True},
                {'x': 30, 'y': 25, 'type': 'checkpoint', 'completed': False},
                {'x': 40, 'y': 35, 'type': 'waypoint', 'completed': False},
                {'x': 50, 'y': 45, 'type': 'target', 'completed': False}
            ],
            'current_target': {'x': 30, 'y': 25, 'name': '检查点1'},
            'next_target': {'x': 40, 'y': 35, 'name': '路径点2'},
            'progress': {
                'completed_points': 2,
                'total_points': 5,
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
        
        # 渲染路径可视化
        print("🎨 渲染路径可视化...")
        box_position = np.array([15.0, 12.0])
        path_manager.render_complete_path_visualization(box_position)
        print("✅ 路径可视化渲染成功")
        
        # 获取性能统计
        print("\n📈 获取性能统计...")
        stats = path_manager.get_performance_stats()
        if stats:
            print(f"✅ 性能统计: {stats}")
        else:
            print("⚠️ 暂无性能统计数据")
        
        # 测试动画更新
        print("\n🎬 测试动画更新...")
        for i in range(5):
            path_manager.update_animation()
            print(f"  动画帧 {i+1}/5")
        
        # 测试强制重绘
        print("\n🔄 测试强制重绘...")
        path_manager.force_redraw()
        print("✅ 强制重绘成功")
        
        # 测试清理
        print("\n🧹 测试清理功能...")
        path_manager.clear_path_visualization()
        print("✅ 清理成功")
        
        # 重新渲染以验证清理效果
        path_manager.render_complete_path_visualization(box_position)
        print("✅ 重新渲染成功")
        
        print("\n🎉 所有测试通过！优化后的路径可视化管理器工作正常")
        
        # 显示窗口
        main_window.show()
        
        # 运行应用程序
        print("\n💡 提示：窗口已显示，请查看路径可视化效果")
        print("💡 提示：按任意键退出测试")
        
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
    result = test_optimized_path_manager()
    sys.exit(result) 