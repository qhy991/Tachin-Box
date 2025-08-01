# -*- coding: utf-8 -*-
"""
在主应用程序中应用路径渲染性能修复
Apply Path Rendering Performance Fix to Main Application

这个脚本可以直接在推箱子游戏主应用程序中应用性能修复。
"""

import sys
import os

# 添加路径以便导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

# 导入快速修复脚本
from quick_path_performance_fix import (
    apply_path_performance_fix, 
    get_performance_stats, 
    set_performance_options
)

def apply_fix_to_main_app():
    """在主应用程序中应用性能修复"""
    print("🔧 开始在主应用程序中应用路径渲染性能修复...")
    
    try:
        # 导入主应用程序
        from box_game_app_optimized import BoxGameMainWindow
        
        # 创建主窗口
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        main_window = BoxGameMainWindow()
        
        # 等待渲染器初始化完成
        import time
        time.sleep(1)
        
        # 应用性能修复到渲染器的路径管理器
        if hasattr(main_window, 'renderer') and main_window.renderer:
            if hasattr(main_window.renderer, 'path_manager') and main_window.renderer.path_manager:
                print("🔧 找到路径管理器，开始应用性能修复...")
                
                # 应用快速修复
                apply_path_performance_fix(main_window.renderer.path_manager)
                
                # 设置性能选项
                set_performance_options(main_window.renderer.path_manager, {
                    'max_points_to_render': 50,      # 最大渲染点数
                    'point_render_interval': 2,      # 点渲染间隔
                    'enable_debug_output': True,     # 启用调试输出以查看效果
                    'animation_enabled': True        # 启用动画
                })
                
                print("✅ 路径渲染性能修复已成功应用到主应用程序")
                
                # 显示初始性能统计
                stats = get_performance_stats(main_window.renderer.path_manager)
                if stats:
                    print(f"📊 初始性能统计: 平均渲染时间={stats.get('avg_render_time_ms', 0):.1f}ms")
                
                # 添加性能监控功能
                add_performance_monitoring(main_window)
                
                return main_window
            else:
                print("❌ 渲染器中没有找到路径管理器")
                return None
        else:
            print("❌ 主窗口中没有找到渲染器")
            return None
            
    except Exception as e:
        print(f"❌ 应用性能修复失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def add_performance_monitoring(main_window):
    """添加性能监控功能"""
    try:
        # 添加性能监控定时器
        from PyQt5.QtCore import QTimer
        
        def monitor_performance():
            """监控性能"""
            if (hasattr(main_window, 'renderer') and main_window.renderer and
                hasattr(main_window.renderer, 'path_manager') and main_window.renderer.path_manager):
                
                stats = get_performance_stats(main_window.renderer.path_manager)
                if stats and stats.get('render_count', 0) > 0:
                    avg_time = stats.get('avg_render_time_ms', 0)
                    
                    # 每10次渲染输出一次性能信息
                    if stats.get('render_count', 0) % 10 == 0:
                        print(f"🎨 路径渲染性能: {avg_time:.1f}ms (渲染{stats.get('render_count', 0)}次)")
                    
                    # 性能警告
                    if avg_time > 50:
                        print(f"⚠️ 路径渲染性能警告: {avg_time:.1f}ms > 50ms")
        
        # 创建监控定时器
        monitor_timer = QTimer()
        monitor_timer.timeout.connect(monitor_performance)
        monitor_timer.start(2000)  # 每2秒监控一次
        
        # 将定时器保存到主窗口，防止被垃圾回收
        main_window.performance_monitor_timer = monitor_timer
        
        print("✅ 性能监控已添加到主应用程序")
        
    except Exception as e:
        print(f"❌ 添加性能监控失败: {e}")

def create_test_path_data(main_window):
    """创建测试路径数据"""
    try:
        if (hasattr(main_window, 'renderer') and main_window.renderer and
            hasattr(main_window.renderer, 'path_manager') and main_window.renderer.path_manager):
            
            import numpy as np
            
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
            main_window.renderer.path_manager.update_path_data(nav_data)
            print(f"✅ 测试路径数据已创建: {len(path_points)}个点")
            
            return True
        else:
            print("❌ 无法创建测试路径数据：路径管理器不可用")
            return False
            
    except Exception as e:
        print(f"❌ 创建测试路径数据失败: {e}")
        return False

def show_performance_summary(main_window):
    """显示性能汇总"""
    try:
        if (hasattr(main_window, 'renderer') and main_window.renderer and
            hasattr(main_window.renderer, 'path_manager') and main_window.renderer.path_manager):
            
            stats = get_performance_stats(main_window.renderer.path_manager)
            if stats:
                print("\n" + "="*50)
                print("📊 路径渲染性能汇总")
                print("="*50)
                print(f"平均渲染时间: {stats.get('avg_render_time_ms', 0):.1f}ms")
                print(f"最大渲染时间: {stats.get('max_render_time_ms', 0):.1f}ms")
                print(f"最小渲染时间: {stats.get('min_render_time_ms', 0):.1f}ms")
                print(f"渲染次数: {stats.get('render_count', 0)}")
                print(f"当前路径点数: {stats.get('current_path_points', 0)}")
                print(f"实际渲染点数: {stats.get('rendered_points', 0)}")
                
                avg_time = stats.get('avg_render_time_ms', 0)
                if avg_time < 10:
                    print("✅ 优秀性能: 平均渲染时间 < 10ms")
                elif avg_time < 20:
                    print("✅ 良好性能: 平均渲染时间 < 20ms")
                elif avg_time < 50:
                    print("⚠️ 一般性能: 平均渲染时间 < 50ms")
                else:
                    print("❌ 性能较差: 平均渲染时间 >= 50ms")
                
                print("="*50)
            else:
                print("❌ 无法获取性能统计")
        else:
            print("❌ 路径管理器不可用")
            
    except Exception as e:
        print(f"❌ 显示性能汇总失败: {e}")

def main():
    """主函数"""
    print("🚀 在主应用程序中应用路径渲染性能修复")
    print("="*50)
    
    # 应用性能修复
    main_window = apply_fix_to_main_app()
    
    if main_window:
        print("✅ 性能修复已应用，主窗口已创建")
        
        # 创建测试路径数据
        if create_test_path_data(main_window):
            print("✅ 测试路径数据已创建")
        
        # 显示主窗口
        main_window.show()
        
        # 添加键盘快捷键
        def keyPressEvent(event):
            """键盘事件处理"""
            from PyQt5.QtCore import Qt
            
            if event.key() == Qt.Key_P:
                # 按P键显示性能汇总
                show_performance_summary(main_window)
            elif event.key() == Qt.Key_T:
                # 按T键创建新的测试路径
                create_test_path_data(main_window)
            elif event.key() == Qt.Key_H:
                # 按H键显示帮助
                print("\n" + "="*50)
                print("🎮 路径渲染性能测试快捷键")
                print("="*50)
                print("P - 显示性能汇总")
                print("T - 创建测试路径")
                print("H - 显示帮助信息")
                print("="*50)
            else:
                # 调用原有的键盘事件处理
                if hasattr(main_window, 'keyPressEvent'):
                    main_window.keyPressEvent(event)
        
        # 替换键盘事件处理
        main_window.keyPressEvent = keyPressEvent
        
        print("✅ 主应用程序已启动，性能修复已应用")
        print("💡 提示：按P键查看性能汇总，按T键创建测试路径，按H键查看帮助")
        
        # 运行应用程序
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        sys.exit(app.exec_())
    else:
        print("❌ 无法应用性能修复，程序退出")

if __name__ == "__main__":
    main() 