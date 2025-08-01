# -*- coding: utf-8 -*-
"""
快速路径渲染性能修复脚本
Quick Path Rendering Performance Fix Script

这个脚本可以直接应用到现有的推箱子游戏渲染器中，
快速解决复杂路径渲染性能问题。
"""

import time
from collections import deque

def apply_path_performance_fix(path_manager):
    """
    应用路径渲染性能修复
    
    Args:
        path_manager: 现有的PathVisualizationManager实例
    """
    
    print("🔧 开始应用路径渲染性能修复...")
    
    # 🎯 1. 添加性能优化属性
    if not hasattr(path_manager, 'performance_optimized'):
        path_manager.performance_optimized = True
        
        # 添加性能参数
        path_manager.max_points_to_render = 50      # 最大渲染点数
        path_manager.point_render_interval = 2      # 点渲染间隔
        path_manager.enable_debug_output = False    # 禁用调试输出
        path_manager.animation_update_interval = 0.1  # 动画更新间隔
        
        # 添加增量更新控制
        path_manager.last_path_hash = None
        path_manager.last_target_hash = None
        path_manager.last_progress_hash = None
        path_manager.needs_full_redraw = True
        
        # 添加性能监控
        path_manager.render_times = deque(maxlen=20)
        path_manager.last_render_start = 0
        
        print("✅ 性能优化属性已添加")
    
    # 🎯 2. 优化动画系统
    if hasattr(path_manager, 'animation_timer'):
        # 降低动画频率
        path_manager.animation_timer.setInterval(100)  # 从50ms改为100ms
        print("✅ 动画频率已优化 (20FPS -> 10FPS)")
    
    # 🎯 3. 替换关键方法
    _replace_render_methods(path_manager)
    
    print("✅ 路径渲染性能修复完成！")
    return path_manager

def _replace_render_methods(path_manager):
    """替换关键的渲染方法"""
    
    # 🎯 替换update_path_data方法
    def optimized_update_path_data(path_data):
        """优化版路径数据更新"""
        new_path_points = path_data.get('path_points', [])
        new_target = path_data.get('current_target')
        new_progress = path_data.get('progress', {})
        
        # 计算数据哈希值
        path_hash = hash(str(new_path_points))
        target_hash = hash(str(new_target))
        progress_hash = hash(str(new_progress))
        
        # 检查是否需要重绘
        needs_redraw = (
            path_manager.needs_full_redraw or
            path_hash != path_manager.last_path_hash or
            target_hash != path_manager.last_target_hash or
            progress_hash != path_manager.last_progress_hash
        )
        
        if needs_redraw:
            path_manager.current_path_points = new_path_points
            path_manager.current_target = new_target
            path_manager.next_target = path_data.get('next_target')
            path_manager.path_progress = new_progress
            path_manager.target_distance = path_data.get('target_distance', 0.0)
            path_manager.direction_angle = path_data.get('direction_angle', 0.0)
            path_manager.has_navigation = path_data.get('has_navigation', False)
            
            # 更新哈希值
            path_manager.last_path_hash = path_hash
            path_manager.last_target_hash = target_hash
            path_manager.last_progress_hash = progress_hash
            
            # 执行渲染
            path_manager.render_complete_path_visualization(None)
            path_manager.needs_full_redraw = False
    
    # 🎯 替换render_complete_path_visualization方法
    def optimized_render_complete_path_visualization(box_position):
        """优化版完整路径渲染"""
        path_manager.last_render_start = time.time()
        
        # 如果没有路径点或导航被禁用，清除显示
        if not path_manager.current_path_points or not path_manager.has_navigation:
            path_manager.clear_path_visualization()
            return
        
        # 优化：限制渲染的路径点数量
        if len(path_manager.current_path_points) > path_manager.max_points_to_render:
            # 采样路径点，保持起点和终点
            step = len(path_manager.current_path_points) // path_manager.max_points_to_render
            sampled_points = (
                [path_manager.current_path_points[0]] + 
                path_manager.current_path_points[1:-1:step] + 
                [path_manager.current_path_points[-1]]
            )
            points_to_render = sampled_points
        else:
            points_to_render = path_manager.current_path_points
        
        # 清除现有显示
        path_manager.clear_path_visualization()
        
        # 渲染路径线条 - 优化版
        _optimized_render_path_line(path_manager, points_to_render)
        
        # 渲染路径点 - 优化版
        _optimized_render_path_points(path_manager, points_to_render)
        
        # 渲染当前目标 - 优化版
        if path_manager.current_target:
            _optimized_render_current_target(path_manager, box_position)
        
        # 渲染进度信息 - 优化版
        _optimized_render_progress_info(path_manager)
        
        # 渲染导航信息 - 优化版
        if box_position is not None:
            _optimized_render_navigation_info(path_manager, box_position)
        
        # 记录渲染时间
        render_time = time.time() - path_manager.last_render_start
        path_manager.render_times.append(render_time)
        
        if path_manager.enable_debug_output and len(path_manager.render_times) % 10 == 0:
            avg_time = sum(path_manager.render_times) / len(path_manager.render_times)
            print(f"🎨 路径渲染性能: 当前={render_time*1000:.1f}ms, 平均={avg_time*1000:.1f}ms")
    
    # 🎯 替换update_animation方法
    def optimized_update_animation():
        """优化版动画更新"""
        current_time = time.time()
        if current_time - getattr(path_manager, 'last_animation_update', 0) >= path_manager.animation_update_interval:
            path_manager.animation_time += path_manager.animation_update_interval
            path_manager.last_animation_update = current_time
            
            # 只在需要时更新动画
            if (path_manager.has_navigation and 
                path_manager.current_path_points and 
                hasattr(path_manager, 'animation_enabled') and 
                path_manager.animation_enabled):
                _update_animation_only(path_manager)
    
    # 应用方法替换
    path_manager.update_path_data = optimized_update_path_data
    path_manager.render_complete_path_visualization = optimized_render_complete_path_visualization
    path_manager.update_animation = optimized_update_animation
    
    print("✅ 关键渲染方法已优化")

def _optimized_render_path_line(path_manager, points_to_render):
    """优化版路径线条渲染"""
    if len(points_to_render) < 2:
        return
    
    import pyqtgraph as pg
    from PyQt5.QtCore import Qt
    
    # 批量处理连线
    completed_lines = []
    pending_lines = []
    
    for i in range(len(points_to_render) - 1):
        point = points_to_render[i]
        next_point = points_to_render[i + 1]
        
        # 检查连接类型
        connection_type = point.get('connection_type', 'solid')
        if connection_type == 'none':
            continue
        
        is_completed = point.get('completed', False)
        
        if is_completed:
            completed_lines.append((point['x'], point['y'], next_point['x'], next_point['y']))
        else:
            pending_lines.append((point['x'], point['y'], next_point['x'], next_point['y']))
    
    # 批量渲染已完成的线条
    if completed_lines:
        _batch_render_lines(path_manager, completed_lines, (144, 238, 144), Qt.SolidLine, 0.8)
    
    # 批量渲染待完成的线条
    if pending_lines:
        _batch_render_lines(path_manager, pending_lines, (0, 255, 255), Qt.DashLine, 0.6)

def _batch_render_lines(path_manager, lines_data, color, style, alpha):
    """批量渲染线条"""
    import pyqtgraph as pg
    
    # 收集所有线条的坐标
    all_x = []
    all_y = []
    
    for x1, y1, x2, y2 in lines_data:
        all_x.extend([x1, x2, None])  # None用于分隔线条
        all_y.extend([y1, y2, None])
    
    if all_x:
        # 移除最后的None
        all_x.pop()
        all_y.pop()
        
        # 创建单个PlotDataItem对象
        line_item = pg.PlotDataItem(
            x=all_x, 
            y=all_y,
            pen=pg.mkPen(color=color, width=2, style=style, alpha=alpha),
            connect='finite'  # 使用None分隔的线条
        )
        path_manager.plot_widget.addItem(line_item)
        path_manager.path_items.append(line_item)

def _optimized_render_path_points(path_manager, points_to_render):
    """优化版路径点渲染"""
    import pyqtgraph as pg
    
    # 只渲染重要的点
    important_points = []
    
    for i, point in enumerate(points_to_render):
        point_type = point.get('type', 'waypoint')
        connection_type = point.get('connection_type', 'solid')
        is_completed = point.get('completed', False)
        is_current = point.get('is_current_target', False)
        
        # 只渲染重要的点
        if (point_type in ['target', 'checkpoint'] or 
            is_current or 
            connection_type == 'none' or
            i == 0 or 
            i == len(points_to_render) - 1 or
            i % path_manager.point_render_interval == 0):
            
            important_points.append((i, point))
    
    # 渲染重要点
    for i, point in important_points:
        _render_single_point_optimized(path_manager, i, point)

def _render_single_point_optimized(path_manager, index, point):
    """优化版单点渲染"""
    import pyqtgraph as pg
    
    point_x, point_y = point['x'], point['y']
    point_type = point.get('type', 'waypoint')
    connection_type = point.get('connection_type', 'solid')
    is_completed = point.get('completed', False)
    is_current = point.get('is_current_target', False)
    
    # 根据点类型选择样式
    if connection_type == 'none':
        marker_color = (255, 0, 0)
        marker_symbol = 'x'
        marker_size = 8
    elif is_completed:
        marker_color = (144, 238, 144)
        marker_symbol = 'o'
        marker_size = 6
    elif is_current:
        marker_color = (255, 255, 0)
        marker_symbol = 'o'
        marker_size = 8
    elif point_type == 'target':
        marker_color = (255, 0, 0)
        marker_symbol = 'x'
        marker_size = 10
    elif point_type == 'checkpoint':
        marker_color = (255, 165, 0)
        marker_symbol = 'd'
        marker_size = 8
    else:
        marker_color = (255, 255, 0)
        marker_symbol = 'o'
        marker_size = 6
    
    # 创建点标记
    point_item = pg.ScatterPlotItem(
        x=[point_x], 
        y=[point_y],
        symbol=marker_symbol,
        size=marker_size,
        brush=marker_color,
        pen=pg.mkPen(color=(0, 0, 0), width=1)
    )
    path_manager.plot_widget.addItem(point_item)
    path_manager.path_items.append(point_item)
    
    # 只为最重要的点添加标签
    if point_type in ['target', 'checkpoint'] or is_current or connection_type == 'none':
        label_text = point.get('name', f'点{index+1}')
        if is_current:
            label_text += ' 🎯'
        
        text_item = pg.TextItem(
            text=label_text,
            color=(255, 255, 255),
            anchor=(0.5, 0)
        )
        text_item.setPos(point_x, point_y + 3)
        path_manager.plot_widget.addItem(text_item)
        path_manager.path_items.append(text_item)

def _optimized_render_current_target(path_manager, box_position):
    """优化版当前目标渲染"""
    if not path_manager.current_target:
        return
    
    import pyqtgraph as pg
    import numpy as np
    
    target_x, target_y = path_manager.current_target['x'], path_manager.current_target['y']
    
    # 创建脉动圆圈
    pulse_scale = 1 + 0.2 * np.sin(path_manager.animation_time * path_manager.pulse_speed * 1.5)
    
    circle_item = pg.ScatterPlotItem(
        x=[target_x], 
        y=[target_y],
        symbol='o',
        size=int(16 * pulse_scale),
        brush=None,
        pen=pg.mkPen(color=(0, 255, 0), width=2, alpha=0.8)
    )
    path_manager.plot_widget.addItem(circle_item)
    path_manager.path_items.append(circle_item)
    
    # 简化导航箭头渲染
    if box_position is not None:
        _render_navigation_arrow_optimized(path_manager, box_position, target_x, target_y)

def _render_navigation_arrow_optimized(path_manager, box_position, target_x, target_y):
    """优化版导航箭头渲染"""
    import pyqtgraph as pg
    import numpy as np
    
    if hasattr(box_position, '__len__') and len(box_position) >= 2:
        box_x, box_y = box_position[0], box_position[1]
    else:
        box_x, box_y = box_position, box_position
    
    # 计算箭头方向
    dx = target_x - box_x
    dy = target_y - box_y
    distance = np.sqrt(dx*dx + dy*dy)
    
    if distance > 0:
        dx /= distance
        dy /= distance
        
        # 简化的箭头渲染
        arrow_start_x = box_x + dx * 15
        arrow_start_y = box_y + dy * 15
        arrow_end_x = target_x - dx * 5
        arrow_end_y = target_y - dy * 5
        
        arrow = pg.PlotDataItem(
            x=[arrow_start_x, arrow_end_x],
            y=[arrow_start_y, arrow_end_y],
            pen=pg.mkPen(color=(0, 255, 0), width=3, alpha=0.8)
        )
        path_manager.plot_widget.addItem(arrow)
        path_manager.path_items.append(arrow)

def _optimized_render_progress_info(path_manager):
    """优化版进度信息渲染"""
    if not path_manager.path_progress:
        return
    
    import pyqtgraph as pg
    
    # 简化的进度显示
    completed = path_manager.path_progress.get('completed_points', 0)
    total = path_manager.path_progress.get('total_points', 0)
    progress_text = f"进度: {completed}/{total}"
    
    if path_manager.path_progress.get('is_completed', False):
        progress_text += " ✅"
    
    progress_item = pg.TextItem(
        text=progress_text,
        color=(255, 255, 255),
        anchor=(1, 0)
    )
    
    # 设置位置
    view_range = path_manager.plot_widget.viewRange()
    if view_range and len(view_range) >= 2:
        progress_item.setPos(view_range[0][1] - 10, view_range[1][1] - 10)
    
    path_manager.plot_widget.addItem(progress_item)
    path_manager.path_items.append(progress_item)

def _optimized_render_navigation_info(path_manager, box_position):
    """优化版导航信息渲染"""
    if box_position is None:
        return
    
    import pyqtgraph as pg
    
    # 简化的导航信息
    info_text = f"距离: {path_manager.target_distance:.1f}cm"
    if path_manager.direction_angle != 0:
        info_text += f" | 方向: {path_manager.direction_angle:.1f}°"
    
    nav_item = pg.TextItem(
        text=info_text,
        color=(0, 255, 255),
        anchor=(0, 0)
    )
    nav_item.setPos(10, 10)
    path_manager.plot_widget.addItem(nav_item)
    path_manager.path_items.append(nav_item)

def _update_animation_only(path_manager):
    """只更新动画效果"""
    if not path_manager.current_target:
        return
    
    # 只更新当前目标的脉动效果
    target_x, target_y = path_manager.current_target['x'], path_manager.current_target['y']
    import numpy as np
    pulse_scale = 1 + 0.2 * np.sin(path_manager.animation_time * path_manager.pulse_speed * 1.5)
    
    # 查找并更新现有的圆圈对象
    for item in path_manager.path_items:
        if hasattr(item, '_is_current_target_circle') and item._is_current_target_circle:
            item.setSize(int(16 * pulse_scale))
            break

def get_performance_stats(path_manager):
    """获取性能统计"""
    if hasattr(path_manager, 'render_times') and path_manager.render_times:
        return {
            'avg_render_time_ms': sum(path_manager.render_times) / len(path_manager.render_times) * 1000,
            'max_render_time_ms': max(path_manager.render_times) * 1000,
            'min_render_time_ms': min(path_manager.render_times) * 1000,
            'render_count': len(path_manager.render_times),
            'current_path_points': len(path_manager.current_path_points),
            'rendered_points': len(path_manager.current_path_points) if len(path_manager.current_path_points) <= path_manager.max_points_to_render else path_manager.max_points_to_render
        }
    return {}

def set_performance_options(path_manager, options):
    """设置性能选项"""
    if 'max_points_to_render' in options:
        path_manager.max_points_to_render = options['max_points_to_render']
    if 'point_render_interval' in options:
        path_manager.point_render_interval = options['point_render_interval']
    if 'enable_debug_output' in options:
        path_manager.enable_debug_output = options['enable_debug_output']
    if 'animation_enabled' in options:
        path_manager.animation_enabled = options['animation_enabled']
        if hasattr(path_manager, 'animation_timer'):
            if not path_manager.animation_enabled:
                path_manager.animation_timer.stop()
            else:
                path_manager.animation_timer.start(100)

# 使用示例
if __name__ == "__main__":
    print("🔧 路径渲染性能修复脚本")
    print("使用方法:")
    print("1. 在渲染器中导入此脚本")
    print("2. 调用 apply_path_performance_fix(path_manager)")
    print("3. 可选：调用 set_performance_options() 调整参数")
    print("4. 可选：调用 get_performance_stats() 监控性能") 