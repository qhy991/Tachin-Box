# -*- coding: utf-8 -*-
import pyqtgraph as pg
from PyQt5.QtCore import QTimer, Qt
import numpy as np

class PathVisualizationManager:
    def __init__(self, plot_widget):
        self.plot_widget = plot_widget
        self.path_items = []
        
        # 路径数据
        self.current_path_points = []
        self.current_target = None
        self.next_target = None
        self.path_progress = {}
        self.target_distance = 0.0
        self.direction_angle = 0.0
        self.has_navigation = False
        
        # 动画相关
        self.animation_time = 0.0
        self.pulse_speed = 2.0
        
        # 动画定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 FPS
    
    def update_animation(self):
        """更新动画时间"""
        self.animation_time += 0.05
        if self.has_navigation and self.current_path_points:
            self.render_complete_path_visualization(None)
    
    def clear_path_visualization(self):
        """清除路径可视化项目"""
        print(f"🗑️ 清除路径可视化，当前项目数量: {len(self.path_items)}")
        for item in self.path_items:
            try:
                self.plot_widget.removeItem(item)
                print(f"🗑️ 已移除路径项目: {type(item).__name__}")
            except Exception as e:
                print(f"⚠️ 移除路径项目失败: {e}")
        self.path_items.clear()
        print(f"🗑️ 路径可视化清除完成")
    
    def update_path_data(self, path_data):
        """更新路径数据"""
        print("路径点：", path_data.get('path_points', []))
        self.current_path_points = path_data.get('path_points', [])
        self.current_target = path_data.get('current_target')
        self.next_target = path_data.get('next_target')
        self.path_progress = path_data.get('progress', {})
        self.target_distance = path_data.get('target_distance', 0.0)
        self.direction_angle = path_data.get('direction_angle', 0.0)
        self.has_navigation = path_data.get('has_navigation', False)
        
        # 🔍 添加调试信息
        print(f"🔍 路径管理器更新 - 进度数据: {self.path_progress}")
        print(f"🔍 导航状态: {self.has_navigation}")
        if self.path_progress:
            print(f"🔍 是否完成: {self.path_progress.get('is_completed', False)}")
            print(f"🔍 完成点数: {self.path_progress.get('completed_points', 0)}/{self.path_progress.get('total_points', 0)}")
    
    def render_complete_path_visualization(self, box_position):
        """渲染完整的路径可视化"""
        print(f"🎨 开始渲染路径可视化，路径点数: {len(self.current_path_points)}, 导航状态: {self.has_navigation}")
        
        # 🗑️ 如果没有路径点，清除所有路径可视化
        if not self.current_path_points:
            self.clear_path_visualization()
            return
        
        # 🗑️ 如果导航被禁用，清除所有路径可视化
        if not self.has_navigation:
            self.clear_path_visualization()
            return
        
        self.clear_path_visualization()
        
        # 渲染路径线条
        self._render_path_line()
        
        # 渲染路径点
        self._render_path_points()
        
        # 渲染当前目标
        if self.current_target:
            self._render_current_target(box_position)
        
        # 渲染下一个目标
        if self.next_target:
            self._render_next_target()
        
        # 渲染进度信息
        self._render_progress_info()
        
        # 渲染导航信息
        if box_position is not None:
            self._render_navigation_info(box_position)
    
    def _render_path_line(self):
        """渲染路径线条"""
        if len(self.current_path_points) < 2:
            return
            
        path_x = [point['x'] for point in self.current_path_points]
        path_y = [point['y'] for point in self.current_path_points]
        
        print(f"🔗 开始渲染路径线条，总点数: {len(self.current_path_points)}")
        
        # 预先分析连接类型，找出所有断点位置
        break_points = []
        for i, point in enumerate(self.current_path_points):
            connection_type = point.get('connection_type', 'solid')
            if connection_type == 'none':
                break_points.append(i)
                print(f"🔗 发现断点: 点{i} ({point['x']}, {point['y']})")
        
        print(f"🔗 断点位置: {break_points}")
        
        # 根据完成状态和连接类型绘制不同颜色的线段
        for i in range(len(path_x) - 1):
            point = self.current_path_points[i]
            next_point = self.current_path_points[i + 1]
            is_completed = point.get('completed', False)
            
            # 🆕 检查连接类型 - 如果当前点的连接类型为"none"，则不绘制连线
            connection_type = point.get('connection_type', 'solid')
            next_connection_type = next_point.get('connection_type', 'solid')
            
            print(f"🔗 检查点{i}到点{i+1}的连接: 当前类型={connection_type}, 下一点类型={next_connection_type}")
            
            # 🆕 增强断点处理逻辑
            skip_line = False
            skip_reason = ""
            
            # 情况1：当前点是断点
            if connection_type == 'none':
                skip_line = True
                skip_reason = "当前点是断点"
            # 情况2：下一个点是断点
            elif next_connection_type == 'none':
                skip_line = True
                skip_reason = "下一个点是断点"
            # 情况3：当前点和下一个点都是断点
            elif connection_type == 'none' and next_connection_type == 'none':
                skip_line = True
                skip_reason = "当前点和下一个点都是断点"
            # 情况4：检查是否跨越断点（当前点不是断点，但下一个点是断点）
            elif i + 1 in break_points:
                skip_line = True
                skip_reason = "跨越断点"
            
            if skip_line:
                print(f"🔗 跳过连线: 点{i}到点{i+1} - {skip_reason}")
                continue
            
            print(f"🔗 绘制连线: 点{i}到点{i+1} (类型={connection_type})")
            
            if is_completed:
                line_color = (144, 238, 144)  # lightgreen RGB
                line_alpha = 0.8
                line_style = Qt.SolidLine
            else:
                line_color = (0, 255, 255)    # cyan RGB
                line_alpha = 0.6
                line_style = Qt.DashLine
            
            # 创建线段
            line = pg.PlotDataItem(
                x=[path_x[i], path_x[i+1]], 
                y=[path_y[i], path_y[i+1]],
                pen=pg.mkPen(color=line_color, width=2, style=line_style, alpha=line_alpha)
            )
            self.plot_widget.addItem(line)
            self.path_items.append(line)
        
        # 统计绘制的连线数量
        drawn_lines = len([i for i in range(len(self.current_path_points)-1) 
                          if self.current_path_points[i].get('connection_type', 'solid') != 'none' and
                          self.current_path_points[i+1].get('connection_type', 'solid') != 'none'])
        
        print(f"🔗 路径线条渲染完成，共绘制了 {drawn_lines} 条连线")
        print(f"🔗 断点数量: {len(break_points)}, 断点位置: {break_points}")
    
    def _render_path_points(self):
        """渲染路径点"""
        for i, point in enumerate(self.current_path_points):
            point_x, point_y = point['x'], point['y']
            point_type = point.get('type', 'waypoint')
            connection_type = point.get('connection_type', 'solid')
            is_completed = point.get('completed', False)
            is_current = point.get('is_current_target', False)
            
            # 🆕 根据连接类型和点类型选择样式
            if connection_type == 'none':
                # 断开点使用红色X标记
                marker_color = (255, 0, 0)      # red RGB
                marker_symbol = 'x'
                marker_size = 8
                edge_color = (139, 0, 0)        # darkred RGB
                print(f"🔗 绘制断开点: 点{i} ({point_x}, {point_y})")
            elif is_completed:
                marker_color = (144, 238, 144)  # lightgreen RGB
                marker_symbol = 'o'
                marker_size = 6
                edge_color = (0, 100, 0)        # darkgreen RGB
            elif is_current:
                # 当前目标点使用脉动效果
                pulse_scale = 1 + 0.3 * np.sin(self.animation_time * self.pulse_speed)
                marker_color = (255, 255, 0)    # yellow RGB
                marker_symbol = 'o'
                marker_size = int(8 * pulse_scale)
                edge_color = (255, 165, 0)      # orange RGB
            elif point_type == 'target':
                marker_color = (255, 0, 0)      # red RGB
                marker_symbol = 'x'
                marker_size = 10
                edge_color = (139, 0, 0)        # darkred RGB
            elif point_type == 'checkpoint':
                marker_color = (255, 165, 0)    # orange RGB
                marker_symbol = 'd'
                marker_size = 8
                edge_color = (255, 140, 0)      # darkorange RGB
            else:  # waypoint
                marker_color = (255, 255, 0)    # yellow RGB
                marker_symbol = 'o'
                marker_size = 6
                edge_color = (255, 215, 0)      # gold RGB
            
            # 绘制路径点
            point_item = pg.ScatterPlotItem(
                x=[point_x], 
                y=[point_y],
                symbol=marker_symbol,
                size=marker_size,
                brush=marker_color,
                pen=pg.mkPen(color=edge_color, width=1.5)
            )
            self.plot_widget.addItem(point_item)
            self.path_items.append(point_item)
            
            # 为重要的点添加标签
            if point_type in ['target', 'checkpoint'] or i == 0 or is_current or connection_type == 'none':
                label_text = point.get('name', f'点{i+1}')
                if is_current:
                    label_text += ' 🎯'
                if connection_type == 'none':
                    label_text += ' 🔗'
                
                # 创建文本项
                text_item = pg.TextItem(
                    text=label_text,
                    color=(255, 255, 255),  # white RGB
                    anchor=(0.5, 0)
                )
                text_item.setPos(point_x, point_y + 3)
                self.plot_widget.addItem(text_item)
                self.path_items.append(text_item)
    
    def _render_current_target(self, box_position):
        """渲染当前目标的高亮效果"""
        if not self.current_target:
            return
            
        target_x, target_y = self.current_target['x'], self.current_target['y']
        
        # 脉动效果圆圈
        pulse_scale = 1 + 0.2 * np.sin(self.animation_time * self.pulse_speed * 1.5)
        
        # 创建圆圈效果（使用ScatterPlotItem模拟）
        circle_item = pg.ScatterPlotItem(
            x=[target_x], 
            y=[target_y],
            symbol='o',
            size=int(16 * pulse_scale),
            brush=None,
            pen=pg.mkPen(color=(0, 255, 0), width=2, alpha=0.8)  # lime RGB
        )
        self.plot_widget.addItem(circle_item)
        self.path_items.append(circle_item)
        
        # 绘制指向目标的导航箭头
        if box_position is not None:
            # 确保box_position是数组时正确提取坐标
            if hasattr(box_position, '__len__') and len(box_position) >= 2:
                box_x, box_y = box_position[0], box_position[1]
            else:
                box_x, box_y = box_position, box_position
            
            # 计算箭头方向
            dx = target_x - box_x
            dy = target_y - box_y
            distance = np.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # 归一化方向向量
                dx /= distance
                dy /= distance
                
                # 箭头起点和终点
                arrow_start_x = box_x + dx * 15
                arrow_start_y = box_y + dy * 15
                arrow_end_x = target_x - dx * 5
                arrow_end_y = target_y - dy * 5
                
                # 创建箭头
                arrow = pg.PlotDataItem(
                    x=[arrow_start_x, arrow_end_x],
                    y=[arrow_start_y, arrow_end_y],
                    pen=pg.mkPen(color=(0, 255, 0), width=3, alpha=0.8)  # lime RGB
                )
                self.plot_widget.addItem(arrow)
                self.path_items.append(arrow)
    
    def _render_next_target(self):
        """渲染下一个目标"""
        if not self.next_target:
            return
            
        next_x, next_y = self.next_target['x'], self.next_target['y']
        
        # 创建下一个目标标记
        next_target_item = pg.ScatterPlotItem(
            x=[next_x], 
            y=[next_y],
            symbol='s',
            size=8,
            brush=(0, 0, 255),      # blue RGB
            pen=pg.mkPen(color=(0, 0, 139), width=1.5)  # darkblue RGB
        )
        self.plot_widget.addItem(next_target_item)
        self.path_items.append(next_target_item)
        
        # 添加标签
        text_item = pg.TextItem(
            text="下一个目标",
            color=(0, 0, 255),  # blue RGB
            anchor=(0.5, 0)
        )
        text_item.setPos(next_x, next_y + 3)
        self.plot_widget.addItem(text_item)
        self.path_items.append(text_item)
    
    def _render_progress_info(self):
        """渲染进度信息"""
        if not self.path_progress:
            return
            
        # 在右上角显示进度信息
        progress_text = f"进度: {self.path_progress.get('completed_points', 0)}/{self.path_progress.get('total_points', 0)}"
        if self.path_progress.get('is_completed', False):
            progress_text += " ✅"
        
        # 创建进度文本
        progress_item = pg.TextItem(
            text=progress_text,
            color=(255, 255, 255),  # white RGB
            anchor=(1, 0)
        )
        # 设置位置在右上角
        progress_item.setPos(self.plot_widget.viewRange()[0][1] - 10, 
                           self.plot_widget.viewRange()[1][1] - 10)
        self.plot_widget.addItem(progress_item)
        self.path_items.append(progress_item)
    
    def _render_navigation_info(self, box_position):
        """渲染导航信息"""
        if box_position is None:
            return
            
        # 显示距离和方向信息
        info_text = f"距离: {self.target_distance:.1f}cm"
        if self.direction_angle != 0:
            info_text += f" | 方向: {self.direction_angle:.1f}°"
        
        # 创建导航信息文本
        nav_item = pg.TextItem(
            text=info_text,
            color=(0, 255, 255),  # cyan RGB
            anchor=(0, 0)
        )
        nav_item.setPos(10, 10)
        self.plot_widget.addItem(nav_item)
        self.path_items.append(nav_item)
    
    def cleanup(self):
        """清理资源"""
        if self.animation_timer:
            self.animation_timer.stop()
        self.clear_path_visualization()