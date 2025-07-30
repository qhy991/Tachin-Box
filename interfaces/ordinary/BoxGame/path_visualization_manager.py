# -*- coding: utf-8 -*-
"""
推箱子游戏渲染模块 - 优化版
Box Game Renderer Module - Optimized Version

负责游戏界面显示和可视化渲染，消除重复代码，优化路径可视化
"""

import numpy as np


# Matplotlib 相关导入
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Arrow, Polygon

from typing import Dict

# 导入路径规划模块
try:
    from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanningGameEnhancer
    PATH_PLANNING_AVAILABLE = True
except ImportError:
    PATH_PLANNING_AVAILABLE = False
    print("⚠️ 路径规划模块未找到，禁用路径功能")

import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']  # 任选其一
matplotlib.rcParams['axes.unicode_minus'] = False  # 负号正常显示

class PathVisualizationManager:
    """路径可视化管理器 - 专门处理路径相关的可视化"""
    
    def __init__(self, ax_game):
        self.ax_game = ax_game
        
        # 路径数据
        self.current_path_points = []
        self.current_target = None
        self.next_target = None
        self.path_progress = {}
        self.target_distance = 0.0
        self.direction_angle = 0.0
        self.has_navigation = False
        
        # 路径可视化选项
        self.show_path_line = True
        self.show_path_points = True
        self.show_target_markers = True
        self.show_progress_info = True
        self.show_navigation_arrows = True
        self.show_prediction_line = False
        
        # 动画相关
        self.animation_time = 0.0
        self.pulse_speed = 2.0
        
        # 渲染对象缓存
        self.path_artists = []
    
    def clear_path_visualization(self):
        """清除所有路径可视化元素"""
        for artist in self.path_artists:
            try:
                artist.remove()
            except:
                pass
        self.path_artists.clear()
    
    def update_path_data(self, path_data: Dict):
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
        # 🗑️ 如果没有路径点，清除所有路径可视化
        if not self.current_path_points:
            self.clear_path_visualization()
            return
        
        # 🗑️ 如果导航被禁用，清除所有路径可视化
        if not self.has_navigation:
            self.clear_path_visualization()
            return
        
        self.clear_path_visualization()
        self.animation_time += 0.1
        
        # 🗺️ 绘制完整路径线条
        if self.show_path_line and len(self.current_path_points) > 1:
            self._render_path_line()
        
        # 🎯 绘制路径点
        if self.show_path_points:
            self._render_path_points()
        
        # 🎯 高亮当前目标
        if self.show_target_markers and self.current_target:
            self._render_current_target(box_position)
        
        # 🔮 绘制下一个目标（预览）
        if self.show_target_markers and self.next_target:
            self._render_next_target()
        
        # 📈 绘制进度信息
        if self.show_progress_info and self.path_progress:
            self._render_progress_info()
        
        # 🧭 绘制导航信息
        if self.show_navigation_arrows:
            self._render_navigation_info(box_position)
        
        # 🔮 绘制预测轨迹
        if self.show_prediction_line:
            self._render_prediction_trajectory(box_position)
    
    def _render_path_line(self):
        """渲染路径线条"""
        path_x = [point['x'] for point in self.current_path_points]
        path_y = [point['y'] for point in self.current_path_points]
        
        # 根据完成状态绘制不同颜色的线段
        for i in range(len(path_x) - 1):
            point = self.current_path_points[i]
            is_completed = point.get('completed', False)
            
            if is_completed:
                line_color = 'lightgreen'
                line_alpha = 0.8
                line_style = '-'
            else:
                line_color = 'cyan'
                line_alpha = 0.6
                line_style = '--'
            
            line = self.ax_game.plot([path_x[i], path_x[i+1]], [path_y[i], path_y[i+1]], 
                                   line_style, color=line_color, linewidth=2, 
                                   alpha=line_alpha, zorder=3)[0]
            self.path_artists.append(line)
    
    def _render_path_points(self):
        """渲染路径点"""
        for i, point in enumerate(self.current_path_points):
            point_x, point_y = point['x'], point['y']
            point_type = point.get('type', 'waypoint')
            is_completed = point.get('completed', False)
            is_current = point.get('is_current_target', False)
            
            # 根据点类型和状态选择样式
            if is_completed:
                marker_color = 'lightgreen'
                marker_symbol = 'o'
                marker_size = 6
                edge_color = 'darkgreen'
            elif is_current:
                # 当前目标点使用脉动效果
                pulse_scale = 1 + 0.3 * np.sin(self.animation_time * self.pulse_speed)
                marker_color = 'yellow'
                marker_symbol = 'o'
                marker_size = 8 * pulse_scale
                edge_color = 'orange'
            elif point_type == 'target':
                marker_color = 'red'
                marker_symbol = 'X'
                marker_size = 10
                edge_color = 'darkred'
            elif point_type == 'checkpoint':
                marker_color = 'orange'
                marker_symbol = 'D'
                marker_size = 8
                edge_color = 'darkorange'
            else:  # waypoint
                marker_color = 'yellow'
                marker_symbol = 'o'
                marker_size = 6
                edge_color = 'gold'
            
            # 绘制路径点
            point_artist = self.ax_game.plot(point_x, point_y, marker_symbol, 
                                           color=marker_color, markersize=marker_size,
                                           markeredgecolor=edge_color, markeredgewidth=1.5,
                                           zorder=6)[0]
            self.path_artists.append(point_artist)
            
            # 为重要的点添加标签
            if point_type in ['target', 'checkpoint'] or i == 0 or is_current:
                label_text = point.get('name', f'点{i+1}')
                if is_current:
                    label_text += ' 🎯'
                text_artist = self.ax_game.text(point_x, point_y + 3, label_text,
                                              ha='center', va='bottom', color='white',
                                              fontsize=8, fontweight='bold',
                                              bbox=dict(boxstyle="round,pad=0.2", 
                                                       facecolor='black', alpha=0.8))
                self.path_artists.append(text_artist)
    
    def _render_current_target(self, box_position):
        """渲染当前目标的高亮效果"""
        target_x, target_y = self.current_target['x'], self.current_target['y']
        
        # 脉动效果圆圈
        pulse_scale = 1 + 0.2 * np.sin(self.animation_time * self.pulse_speed * 1.5)
        
        circle1 = Circle((target_x, target_y), 8 * pulse_scale, fill=False, 
                        color='lime', linewidth=2, alpha=0.8, zorder=7)
        circle2 = Circle((target_x, target_y), 12, fill=False, 
                        color='lime', linewidth=1, alpha=0.4, zorder=7)
        
        self.ax_game.add_patch(circle1)
        self.ax_game.add_patch(circle2)
        self.path_artists.extend([circle1, circle2])
        
        # 绘制指向目标的导航箭头
        if box_position is not None:
            box_x, box_y = box_position
            dx = target_x - box_x
            dy = target_y - box_y
            distance = np.sqrt(dx*dx + dy*dy)
            
            if distance > 8:  # 只在距离足够远时显示箭头
                # 标准化方向向量
                dx_norm = dx / distance * 6
                dy_norm = dy / distance * 6
                
                # 绘制导航箭头 - 使用更好的箭头样式
                arrow_props = dict(arrowstyle='->', lw=2, color='cyan', alpha=0.8)
                arrow_artist = self.ax_game.annotate('', 
                                                   xy=(box_x + dx_norm*3, box_y + dy_norm*3),
                                                   xytext=(box_x + dx_norm, box_y + dy_norm),
                                                   arrowprops=arrow_props, zorder=8)
                self.path_artists.append(arrow_artist)
                
                # 显示距离信息
                distance_text = self.ax_game.text(target_x, target_y + 8, f'{distance:.1f}',
                                                ha='center', va='bottom', color='white',
                                                fontsize=8, fontweight='bold',
                                                bbox=dict(boxstyle="round,pad=0.2", 
                                                         facecolor='black', alpha=0.7))
                self.path_artists.append(distance_text)
    
    def _render_next_target(self):
        """渲染下一个目标（预览）"""
        next_x, next_y = self.next_target['x'], self.next_target['y']
        next_type = self.next_target.get('type', 'waypoint')
        
        if next_type == 'target':
            next_color, next_marker = 'darkred', 'X'
        elif next_type == 'checkpoint':
            next_color, next_marker = 'darkorange', 'D'
        else:
            next_color, next_marker = 'gold', 'o'
        
        # 绘制下一个目标（半透明）
        next_artist = self.ax_game.plot(next_x, next_y, next_marker, color=next_color,
                                      markersize=6, markeredgecolor='white',
                                      markeredgewidth=1, alpha=0.5, zorder=5)[0]
        self.path_artists.append(next_artist)
        
        # 添加"下一个"标签
        next_text = self.ax_game.text(next_x, next_y - 3, '下一个',
                                    ha='center', va='top', color='white',
                                    fontsize=7, alpha=0.7,
                                    bbox=dict(boxstyle="round,pad=0.2", 
                                             facecolor='gray', alpha=0.6))
        self.path_artists.append(next_text)
    
    def _render_progress_info(self):
        """渲染路径进度信息"""
        total_points = self.path_progress.get('total_points', 0)
        completed_points = self.path_progress.get('completed_points', 0)
        progress_pct = self.path_progress.get('progress_percentage', 0)
        
        # 在右上角绘制进度信息
        progress_text = f"路径进度: {completed_points}/{total_points} ({progress_pct:.1f}%)"
        
        if self.path_progress.get('is_completed', False):
            progress_color = 'lime'
            progress_text += " ✅"
        else:
            progress_color = 'cyan'
        
        progress_artist = self.ax_game.text(60, 58, progress_text, ha='right', va='top',
                                          color=progress_color, fontsize=9, fontweight='bold',
                                          bbox=dict(boxstyle="round,pad=0.3", 
                                                   facecolor='black', alpha=0.8))
        self.path_artists.append(progress_artist)
        
        # 绘制进度条
        bar_width = 50
        bar_height = 3
        bar_x = 60 - bar_width
        bar_y = 53
        
        # 背景条
        bg_rect = Rectangle((bar_x, bar_y), bar_width, bar_height,
                           facecolor='gray', alpha=0.5)
        self.ax_game.add_patch(bg_rect)
        self.path_artists.append(bg_rect)
        
        # 进度条
        if total_points > 0:
            progress_width = bar_width * (completed_points / total_points)
            progress_rect = Rectangle((bar_x, bar_y), progress_width, bar_height,
                                    facecolor=progress_color, alpha=0.8)
            self.ax_game.add_patch(progress_rect)
            self.path_artists.append(progress_rect)
    
    def _render_navigation_info(self, box_position):
        """渲染导航信息"""
        if self.target_distance > 0 and box_position is not None:
            # 在左下角显示导航信息
            nav_text = f"🧭 距离: {self.target_distance:.1f}\n📐 方向: {self.direction_angle:.1f}°"
            nav_artist = self.ax_game.text(5, 8, nav_text, ha='left', va='bottom',
                                         color='cyan', fontsize=8, fontweight='bold',
                                         bbox=dict(boxstyle="round,pad=0.3", 
                                                  facecolor='black', alpha=0.8))
            self.path_artists.append(nav_artist)
    
    def _render_prediction_trajectory(self, box_position):
        """渲染预测轨迹"""
        if box_position is None or not self.current_target:
            return
        
        # 计算从当前位置到目标的预测轨迹
        box_x, box_y = box_position
        target_x, target_y = self.current_target['x'], self.current_target['y']
        
        # 简单的直线预测（可以根据需要改进为更复杂的轨迹预测）
        pred_x = [box_x, target_x]
        pred_y = [box_y, target_y]
        
        pred_line = self.ax_game.plot(pred_x, pred_y, ':', color='yellow', 
                                    linewidth=1, alpha=0.6, zorder=2)[0]
        self.path_artists.append(pred_line)
    
    def set_visualization_options(self, options: Dict):
        """设置可视化选项"""
        self.show_path_line = options.get('show_path_line', True)
        self.show_path_points = options.get('show_path_points', True)
        self.show_target_markers = options.get('show_target_markers', True)
        self.show_progress_info = options.get('show_progress_info', True)
        self.show_navigation_arrows = options.get('show_navigation_arrows', True)
        self.show_prediction_line = options.get('show_prediction_line', False)
        self.pulse_speed = options.get('pulse_speed', 2.0)




__all__ = [ 'PathVisualizationManager'] 