# -*- coding: utf-8 -*-
"""
路径可视化管理器 - 高性能优化版
Path Visualization Manager - High Performance Optimized Version

解决复杂路径渲染性能问题，提供增量更新和对象复用机制。
"""

import pyqtgraph as pg
from PyQt5.QtCore import QTimer, Qt
import numpy as np
from collections import deque
import time

class PathVisualizationManagerOptimized:
    """高性能路径可视化管理器"""
    
    def __init__(self, plot_widget):
        self.plot_widget = plot_widget
        
        # 🎯 对象池管理 - 避免重复创建PyQtGraph对象
        self.path_items_pool = {
            'lines': deque(maxlen=100),      # 线条对象池
            'points': deque(maxlen=200),     # 点标记对象池
            'texts': deque(maxlen=100),      # 文本对象池
            'circles': deque(maxlen=50)      # 圆圈对象池
        }
        
        # 📊 当前渲染状态
        self.current_path_points = []
        self.current_target = None
        self.next_target = None
        self.path_progress = {}
        self.target_distance = 0.0
        self.direction_angle = 0.0
        self.has_navigation = False
        
        # 🔄 增量更新控制
        self.last_path_hash = None
        self.last_target_hash = None
        self.last_progress_hash = None
        self.needs_full_redraw = True
        
        # ⚡ 性能优化参数
        self.max_points_to_render = 50      # 最大渲染点数
        self.point_render_interval = 2      # 点渲染间隔（每隔N个点渲染一个）
        self.enable_debug_output = False    # 禁用调试输出
        self.animation_enabled = True       # 动画开关
        
        # 🎬 动画系统优化
        self.animation_time = 0.0
        self.pulse_speed = 2.0
        self.last_animation_update = time.time()
        self.animation_update_interval = 0.1  # 100ms更新一次动画
        
        # 🎯 动画定时器 - 降低频率
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(100)  # 10 FPS，降低动画频率
        
        # 📈 性能监控
        self.render_times = deque(maxlen=20)
        self.last_render_start = 0
        
    def update_animation(self):
        """更新动画时间 - 优化版"""
        current_time = time.time()
        if current_time - self.last_animation_update >= self.animation_update_interval:
            self.animation_time += self.animation_update_interval
            self.last_animation_update = current_time
            
            # 只在需要时更新动画
            if self.has_navigation and self.current_path_points and self.animation_enabled:
                self.update_animation_only()
    
    def update_animation_only(self):
        """只更新动画效果，不重绘整个路径"""
        if not self.current_target:
            return
            
        # 只更新当前目标的脉动效果
        target_x, target_y = self.current_target['x'], self.current_target['y']
        pulse_scale = 1 + 0.2 * np.sin(self.animation_time * self.pulse_speed * 1.5)
        
        # 查找并更新现有的圆圈对象
        for item in self.path_items_pool['circles']:
            if hasattr(item, '_is_current_target_circle') and item._is_current_target_circle:
                item.setSize(int(16 * pulse_scale))
                break
    
    def clear_path_visualization(self):
        """清除路径可视化项目 - 优化版"""
        if self.enable_debug_output:
            print(f"🗑️ 清除路径可视化")
        
        # 将对象放回池中而不是删除
        for category, items in self.path_items_pool.items():
            for item in items:
                try:
                    self.plot_widget.removeItem(item)
                except Exception:
                    pass  # 忽略已删除的对象
            items.clear()
    
    def update_path_data(self, path_data):
        """更新路径数据 - 优化版"""
        new_path_points = path_data.get('path_points', [])
        new_target = path_data.get('current_target')
        new_progress = path_data.get('progress', {})
        
        # 🔍 计算数据哈希值，判断是否需要重绘
        path_hash = hash(str(new_path_points))
        target_hash = hash(str(new_target))
        progress_hash = hash(str(new_progress))
        
        # 检查是否需要完全重绘
        needs_redraw = (
            self.needs_full_redraw or
            path_hash != self.last_path_hash or
            target_hash != self.last_target_hash or
            progress_hash != self.last_progress_hash
        )
        
        if needs_redraw:
            self.current_path_points = new_path_points
            self.current_target = new_target
            self.next_target = path_data.get('next_target')
            self.path_progress = new_progress
            self.target_distance = path_data.get('target_distance', 0.0)
            self.direction_angle = path_data.get('direction_angle', 0.0)
            self.has_navigation = path_data.get('has_navigation', False)
            
            # 更新哈希值
            self.last_path_hash = path_hash
            self.last_target_hash = target_hash
            self.last_progress_hash = progress_hash
            
            # 执行渲染
            self.render_complete_path_visualization(None)
            self.needs_full_redraw = False
    
    def render_complete_path_visualization(self, box_position):
        """渲染完整的路径可视化 - 高性能优化版"""
        self.last_render_start = time.time()
        
        # 🗑️ 如果没有路径点或导航被禁用，清除显示
        if not self.current_path_points or not self.has_navigation:
            self.clear_path_visualization()
            return
        
        # 🎯 优化：限制渲染的路径点数量
        if len(self.current_path_points) > self.max_points_to_render:
            # 采样路径点，保持起点和终点
            step = len(self.current_path_points) // self.max_points_to_render
            sampled_points = (
                [self.current_path_points[0]] + 
                self.current_path_points[1:-1:step] + 
                [self.current_path_points[-1]]
            )
            points_to_render = sampled_points
        else:
            points_to_render = self.current_path_points
        
        # 🎯 渲染路径线条 - 优化版
        self._render_path_line_optimized(points_to_render)
        
        # 🎯 渲染路径点 - 优化版
        self._render_path_points_optimized(points_to_render)
        
        # 🎯 渲染当前目标 - 优化版
        if self.current_target:
            self._render_current_target_optimized(box_position)
        
        # 🎯 渲染进度信息 - 优化版
        self._render_progress_info_optimized()
        
        # 🎯 渲染导航信息 - 优化版
        if box_position is not None:
            self._render_navigation_info_optimized(box_position)
        
        # 📊 记录渲染时间
        render_time = time.time() - self.last_render_start
        self.render_times.append(render_time)
        
        if self.enable_debug_output and len(self.render_times) % 10 == 0:
            avg_time = np.mean(self.render_times)
            print(f"🎨 路径渲染性能: 当前={render_time*1000:.1f}ms, 平均={avg_time*1000:.1f}ms")
    
    def _render_path_line_optimized(self, points_to_render):
        """渲染路径线条 - 优化版"""
        if len(points_to_render) < 2:
            return
        
        # 🎯 批量处理连线，减少PyQtGraph对象创建
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
        
        # 🎯 批量渲染已完成的线条
        if completed_lines:
            self._batch_render_lines(completed_lines, (144, 238, 144), Qt.SolidLine, 0.8)
        
        # 🎯 批量渲染待完成的线条
        if pending_lines:
            self._batch_render_lines(pending_lines, (0, 255, 255), Qt.DashLine, 0.6)
    
    def _batch_render_lines(self, lines_data, color, style, alpha):
        """批量渲染线条 - 减少对象创建"""
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
            self.plot_widget.addItem(line_item)
            self.path_items_pool['lines'].append(line_item)
    
    def _render_path_points_optimized(self, points_to_render):
        """渲染路径点 - 优化版"""
        # 🎯 只渲染重要的点，减少渲染负担
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
                i % self.point_render_interval == 0):
                
                important_points.append((i, point))
        
        # 🎯 批量渲染重要点
        for i, point in important_points:
            self._render_single_point_optimized(i, point)
    
    def _render_single_point_optimized(self, index, point):
        """渲染单个路径点 - 优化版"""
        point_x, point_y = point['x'], point['y']
        point_type = point.get('type', 'waypoint')
        connection_type = point.get('connection_type', 'solid')
        is_completed = point.get('completed', False)
        is_current = point.get('is_current_target', False)
        
        # 🎯 根据点类型选择样式
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
        self.plot_widget.addItem(point_item)
        self.path_items_pool['points'].append(point_item)
        
        # 🎯 只为最重要的点添加标签
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
            self.plot_widget.addItem(text_item)
            self.path_items_pool['texts'].append(text_item)
    
    def _render_current_target_optimized(self, box_position):
        """渲染当前目标 - 优化版"""
        if not self.current_target:
            return
        
        target_x, target_y = self.current_target['x'], self.current_target['y']
        
        # 创建脉动圆圈
        pulse_scale = 1 + 0.2 * np.sin(self.animation_time * self.pulse_speed * 1.5)
        
        circle_item = pg.ScatterPlotItem(
            x=[target_x], 
            y=[target_y],
            symbol='o',
            size=int(16 * pulse_scale),
            brush=None,
            pen=pg.mkPen(color=(0, 255, 0), width=2, alpha=0.8)
        )
        circle_item._is_current_target_circle = True  # 标记为当前目标圆圈
        self.plot_widget.addItem(circle_item)
        self.path_items_pool['circles'].append(circle_item)
        
        # 🎯 简化导航箭头渲染
        if box_position is not None:
            self._render_navigation_arrow_optimized(box_position, target_x, target_y)
    
    def _render_navigation_arrow_optimized(self, box_position, target_x, target_y):
        """渲染导航箭头 - 优化版"""
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
            self.plot_widget.addItem(arrow)
            self.path_items_pool['lines'].append(arrow)
    
    def _render_progress_info_optimized(self):
        """渲染进度信息 - 优化版"""
        if not self.path_progress:
            return
        
        # 简化的进度显示
        completed = self.path_progress.get('completed_points', 0)
        total = self.path_progress.get('total_points', 0)
        progress_text = f"进度: {completed}/{total}"
        
        if self.path_progress.get('is_completed', False):
            progress_text += " ✅"
        
        progress_item = pg.TextItem(
            text=progress_text,
            color=(255, 255, 255),
            anchor=(1, 0)
        )
        
        # 设置位置
        view_range = self.plot_widget.viewRange()
        if view_range and len(view_range) >= 2:
            progress_item.setPos(view_range[0][1] - 10, view_range[1][1] - 10)
        
        self.plot_widget.addItem(progress_item)
        self.path_items_pool['texts'].append(progress_item)
    
    def _render_navigation_info_optimized(self, box_position):
        """渲染导航信息 - 优化版"""
        if box_position is None:
            return
        
        # 简化的导航信息
        info_text = f"距离: {self.target_distance:.1f}cm"
        if self.direction_angle != 0:
            info_text += f" | 方向: {self.direction_angle:.1f}°"
        
        nav_item = pg.TextItem(
            text=info_text,
            color=(0, 255, 255),
            anchor=(0, 0)
        )
        nav_item.setPos(10, 10)
        self.plot_widget.addItem(nav_item)
        self.path_items_pool['texts'].append(nav_item)
    
    def set_performance_options(self, options):
        """设置性能选项"""
        if 'max_points_to_render' in options:
            self.max_points_to_render = options['max_points_to_render']
        if 'point_render_interval' in options:
            self.point_render_interval = options['point_render_interval']
        if 'enable_debug_output' in options:
            self.enable_debug_output = options['enable_debug_output']
        if 'animation_enabled' in options:
            self.animation_enabled = options['animation_enabled']
            if not self.animation_enabled:
                self.animation_timer.stop()
            else:
                self.animation_timer.start(100)
    
    def get_performance_stats(self):
        """获取性能统计"""
        if self.render_times:
            return {
                'avg_render_time_ms': np.mean(self.render_times) * 1000,
                'max_render_time_ms': np.max(self.render_times) * 1000,
                'min_render_time_ms': np.min(self.render_times) * 1000,
                'render_count': len(self.render_times),
                'current_path_points': len(self.current_path_points),
                'rendered_points': len(self.current_path_points) if len(self.current_path_points) <= self.max_points_to_render else self.max_points_to_render
            }
        return {}
    
    def force_redraw(self):
        """强制重绘"""
        self.needs_full_redraw = True
        self.last_path_hash = None
        self.last_target_hash = None
        self.last_progress_hash = None
    
    def cleanup(self):
        """清理资源"""
        if self.animation_timer:
            self.animation_timer.stop()
        self.clear_path_visualization() 