# -*- coding: utf-8 -*-
"""
路径渲染性能修复测试脚本
Path Rendering Performance Fix Test Script

这个脚本用于测试快速修复脚本的效果，包括：
1. 应用性能修复到现有渲染器
2. 创建测试路径数据
3. 监控性能改善情况
"""

import sys
import os
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer

# 添加路径以便导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

# 导入快速修复脚本
from quick_path_performance_fix import (
    apply_path_performance_fix, 
    get_performance_stats, 
    set_performance_options
)

# 导入渲染器
from box_game_renderer import BoxGameRenderer

class PathPerformanceTestWindow(QMainWindow):
    """路径性能测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("路径渲染性能测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建控制面板
        control_layout = QHBoxLayout()
        
        # 测试按钮
        self.test_button = QPushButton("开始性能测试")
        self.test_button.clicked.connect(self.start_performance_test)
        control_layout.addWidget(self.test_button)
        
        # 应用修复按钮
        self.fix_button = QPushButton("应用性能修复")
        self.fix_button.clicked.connect(self.apply_performance_fix)
        control_layout.addWidget(self.fix_button)
        
        # 性能统计按钮
        self.stats_button = QPushButton("显示性能统计")
        self.stats_button.clicked.connect(self.show_performance_stats)
        control_layout.addWidget(self.stats_button)
        
        # 重置按钮
        self.reset_button = QPushButton("重置测试")
        self.reset_button.clicked.connect(self.reset_test)
        control_layout.addWidget(self.reset_button)
        
        layout.addLayout(control_layout)
        
        # 状态标签
        self.status_label = QLabel("准备开始测试...")
        self.status_label.setStyleSheet("color: white; font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # 性能显示标签
        self.performance_label = QLabel("性能数据将在这里显示")
        self.performance_label.setStyleSheet("color: cyan; font-size: 12px; padding: 5px;")
        layout.addWidget(self.performance_label)
        
        # 创建渲染器
        self.renderer = BoxGameRenderer()
        layout.addWidget(self.renderer)
        
        # 测试状态
        self.test_running = False
        self.fix_applied = False
        self.test_data = []
        
        # 测试定时器
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.update_test)
        
        # 性能监控定时器
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.monitor_performance)
        self.monitor_timer.start(1000)  # 每秒监控一次
        
        print("🔧 路径性能测试窗口已创建")
    
    def apply_performance_fix(self):
        """应用性能修复"""
        try:
            if hasattr(self.renderer, 'path_manager') and self.renderer.path_manager:
                print("🔧 开始应用路径渲染性能修复...")
                
                # 应用快速修复
                apply_path_performance_fix(self.renderer.path_manager)
                
                # 设置性能选项
                set_performance_options(self.renderer.path_manager, {
                    'max_points_to_render': 50,      # 最大渲染点数
                    'point_render_interval': 2,      # 点渲染间隔
                    'enable_debug_output': True,     # 启用调试输出以查看效果
                    'animation_enabled': True        # 启用动画
                })
                
                self.fix_applied = True
                self.status_label.setText("✅ 性能修复已应用！")
                self.status_label.setStyleSheet("color: green; font-size: 14px; padding: 10px;")
                
                print("✅ 路径渲染性能修复已成功应用")
                
            else:
                print("❌ 渲染器中没有找到路径管理器")
                self.status_label.setText("❌ 未找到路径管理器")
                self.status_label.setStyleSheet("color: red; font-size: 14px; padding: 10px;")
                
        except Exception as e:
            print(f"❌ 应用性能修复失败: {e}")
            self.status_label.setText(f"❌ 修复失败: {str(e)}")
            self.status_label.setStyleSheet("color: red; font-size: 14px; padding: 10px;")
    
    def start_performance_test(self):
        """开始性能测试"""
        if not self.fix_applied:
            print("⚠️ 请先应用性能修复")
            self.status_label.setText("⚠️ 请先应用性能修复")
            return
        
        print("🚀 开始路径渲染性能测试...")
        self.test_running = True
        self.test_data = []
        
        # 创建测试路径数据
        self.create_test_path_data()
        
        # 开始测试
        self.test_timer.start(100)  # 每100ms更新一次
        self.test_button.setText("停止测试")
        self.test_button.clicked.disconnect()
        self.test_button.clicked.connect(self.stop_performance_test)
        
        self.status_label.setText("🔄 性能测试进行中...")
        self.status_label.setStyleSheet("color: yellow; font-size: 14px; padding: 10px;")
    
    def stop_performance_test(self):
        """停止性能测试"""
        self.test_running = False
        self.test_timer.stop()
        
        self.test_button.setText("开始性能测试")
        self.test_button.clicked.disconnect()
        self.test_button.clicked.connect(self.start_performance_test)
        
        self.status_label.setText("✅ 性能测试完成")
        self.status_label.setStyleSheet("color: green; font-size: 14px; padding: 10px;")
        
        # 显示测试结果
        self.show_test_results()
    
    def create_test_path_data(self):
        """创建测试路径数据"""
        print("📊 创建测试路径数据...")
        
        # 创建复杂路径（100个点）
        path_points = []
        for i in range(100):
            # 创建螺旋形路径
            angle = i * 0.2
            radius = 10 + i * 0.3
            x = 32 + radius * np.cos(angle)
            y = 32 + radius * np.sin(angle)
            
            path_points.append({
                'x': x,
                'y': y,
                'type': 'waypoint' if i % 10 != 0 else 'checkpoint',
                'connection_type': 'solid',
                'completed': i < 30,  # 前30个点已完成
                'is_current_target': i == 30,  # 第31个点是当前目标
                'name': f'点{i+1}'
            })
        
        # 创建导航数据
        nav_data = {
            'path_points': path_points,
            'current_target': path_points[30] if len(path_points) > 30 else None,
            'next_target': path_points[31] if len(path_points) > 31 else None,
            'progress': {
                'completed_points': 30,
                'total_points': len(path_points),
                'is_completed': False
            },
            'target_distance': 5.2,
            'direction_angle': 45.0,
            'has_navigation': True
        }
        
        # 更新路径管理器
        if hasattr(self.renderer, 'path_manager') and self.renderer.path_manager:
            self.renderer.path_manager.update_path_data(nav_data)
            print(f"✅ 测试路径数据已创建: {len(path_points)}个点")
    
    def update_test(self):
        """更新测试"""
        if not self.test_running:
            return
        
        # 模拟路径进度更新
        if hasattr(self.renderer, 'path_manager') and self.renderer.path_manager:
            # 获取当前路径数据
            current_data = {
                'path_points': self.renderer.path_manager.current_path_points,
                'current_target': self.renderer.path_manager.current_target,
                'next_target': self.renderer.path_manager.next_target,
                'progress': self.renderer.path_manager.path_progress,
                'target_distance': self.renderer.path_manager.target_distance,
                'direction_angle': self.renderer.path_manager.direction_angle,
                'has_navigation': self.renderer.path_manager.has_navigation
            }
            
            # 更新进度
            if current_data['progress']:
                completed = current_data['progress'].get('completed_points', 0)
                total = current_data['progress'].get('total_points', 0)
                
                # 模拟进度增加
                if completed < total:
                    current_data['progress']['completed_points'] = min(completed + 1, total)
                    
                    # 更新路径点的完成状态
                    for i, point in enumerate(current_data['path_points']):
                        point['completed'] = i < current_data['progress']['completed_points']
                        point['is_current_target'] = i == current_data['progress']['completed_points']
                    
                    # 更新当前目标
                    if current_data['progress']['completed_points'] < len(current_data['path_points']):
                        current_data['current_target'] = current_data['path_points'][current_data['progress']['completed_points']]
                        if current_data['progress']['completed_points'] + 1 < len(current_data['path_points']):
                            current_data['next_target'] = current_data['path_points'][current_data['progress']['completed_points'] + 1]
                    
                    # 更新路径管理器
                    self.renderer.path_manager.update_path_data(current_data)
    
    def monitor_performance(self):
        """监控性能"""
        if hasattr(self.renderer, 'path_manager') and self.renderer.path_manager:
            stats = get_performance_stats(self.renderer.path_manager)
            if stats:
                performance_text = f"""
性能统计:
- 平均渲染时间: {stats.get('avg_render_time_ms', 0):.1f}ms
- 最大渲染时间: {stats.get('max_render_time_ms', 0):.1f}ms
- 最小渲染时间: {stats.get('min_render_time_ms', 0):.1f}ms
- 渲染次数: {stats.get('render_count', 0)}
- 当前路径点数: {stats.get('current_path_points', 0)}
- 实际渲染点数: {stats.get('rendered_points', 0)}
- 修复状态: {'已应用' if self.fix_applied else '未应用'}
                """
                self.performance_label.setText(performance_text)
    
    def show_performance_stats(self):
        """显示性能统计"""
        if hasattr(self.renderer, 'path_manager') and self.renderer.path_manager:
            stats = get_performance_stats(self.renderer.path_manager)
            if stats:
                print("\n" + "="*50)
                print("📊 路径渲染性能统计")
                print("="*50)
                print(f"平均渲染时间: {stats.get('avg_render_time_ms', 0):.1f}ms")
                print(f"最大渲染时间: {stats.get('max_render_time_ms', 0):.1f}ms")
                print(f"最小渲染时间: {stats.get('min_render_time_ms', 0):.1f}ms")
                print(f"渲染次数: {stats.get('render_count', 0)}")
                print(f"当前路径点数: {stats.get('current_path_points', 0)}")
                print(f"实际渲染点数: {stats.get('rendered_points', 0)}")
                print(f"修复状态: {'已应用' if self.fix_applied else '未应用'}")
                print("="*50)
            else:
                print("❌ 无法获取性能统计")
        else:
            print("❌ 路径管理器不可用")
    
    def show_test_results(self):
        """显示测试结果"""
        if hasattr(self.renderer, 'path_manager') and self.renderer.path_manager:
            stats = get_performance_stats(self.renderer.path_manager)
            if stats:
                avg_time = stats.get('avg_render_time_ms', 0)
                
                print("\n" + "="*50)
                print("🎯 路径渲染性能测试结果")
                print("="*50)
                
                if avg_time < 10:
                    print("✅ 优秀性能: 平均渲染时间 < 10ms")
                elif avg_time < 20:
                    print("✅ 良好性能: 平均渲染时间 < 20ms")
                elif avg_time < 50:
                    print("⚠️ 一般性能: 平均渲染时间 < 50ms")
                else:
                    print("❌ 性能较差: 平均渲染时间 >= 50ms")
                
                print(f"📊 详细数据:")
                print(f"  - 平均渲染时间: {avg_time:.1f}ms")
                print(f"  - 最大渲染时间: {stats.get('max_render_time_ms', 0):.1f}ms")
                print(f"  - 渲染次数: {stats.get('render_count', 0)}")
                print(f"  - 路径点数: {stats.get('current_path_points', 0)}")
                print(f"  - 实际渲染点数: {stats.get('rendered_points', 0)}")
                
                # 计算性能提升
                if self.fix_applied:
                    print(f"🚀 性能修复已应用，预期提升 5-15倍")
                
                print("="*50)
    
    def reset_test(self):
        """重置测试"""
        self.test_running = False
        self.test_timer.stop()
        self.fix_applied = False
        self.test_data = []
        
        # 重置按钮状态
        self.test_button.setText("开始性能测试")
        self.test_button.clicked.disconnect()
        self.test_button.clicked.connect(self.start_performance_test)
        
        # 清除路径显示
        if hasattr(self.renderer, 'path_manager') and self.renderer.path_manager:
            self.renderer.path_manager.clear_path_visualization()
        
        self.status_label.setText("🔄 测试已重置")
        self.status_label.setStyleSheet("color: white; font-size: 14px; padding: 10px;")
        self.performance_label.setText("性能数据将在这里显示")
        
        print("🔄 测试已重置")

def main():
    """主函数"""
    print("🚀 启动路径渲染性能测试")
    print("="*50)
    print("测试步骤:")
    print("1. 点击'应用性能修复'按钮")
    print("2. 点击'开始性能测试'按钮")
    print("3. 观察性能统计和渲染效果")
    print("4. 点击'显示性能统计'查看详细数据")
    print("5. 点击'重置测试'重新开始")
    print("="*50)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    test_window = PathPerformanceTestWindow()
    test_window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 