# -*- coding: utf-8 -*-
"""
推箱子游戏渲染器模块（高性能优化版）
Renderer Module for Box Push Game (Optimized Version)

本模块负责游戏状态的可视化渲染，包括压力分布、游戏区域、COP轨迹等。
现在集成了utils.py的功能，提供更好的颜色映射和主题支持。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import LinearSegmentedColormap
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox
from PyQt5.QtGui import QFont, QPalette, QColor
import sys
import os
from typing import Dict, Optional, Any, Tuple

# 🎨 集成utils功能
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../utils'))
    from utils import COLORS, apply_dark_theme, catch_exceptions
    UTILS_AVAILABLE = True
    print("✅ utils功能已集成")
except ImportError as e:
    print(f"⚠️ utils功能不可用: {e}")
    UTILS_AVAILABLE = False
    # 定义默认颜色映射
    COLORS = [[15, 15, 15], [48, 18, 59], [71, 118, 238], [27, 208, 213], 
              [97, 252, 108], [210, 233, 53], [254, 155, 45], [218, 57, 7], [122, 4, 3]]

import numpy as np
import time
from collections import deque
from typing import Dict, Optional, Any, List

# PyQt5 相关导入
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

# 导入路径规划模块
try:
    try:
        from .box_game_path_planning import PathPlanningGameEnhancer
    except ImportError:
        from box_game_path_planning import PathPlanningGameEnhancer
    PATH_PLANNING_AVAILABLE = True
except ImportError:
    PATH_PLANNING_AVAILABLE = False
    print("⚠️ 路径规划模块未找到，禁用路径功能")

# Matplotlib 相关导入
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Arrow, Polygon
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.animation import FuncAnimation

try:
    from .path_visualization_manager import PathVisualizationManager
except ImportError:
    from path_visualization_manager import PathVisualizationManager

class BoxGameRenderer(FigureCanvas):
    """推箱子游戏渲染器 - 高性能优化版"""
    
    # 信号定义
    mouse_pressed = pyqtSignal(float, float)
    animation_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        # 🔧 初始化 matplotlib 画布
        self.fig = Figure(figsize=(12, 8), facecolor='black')
        super().__init__(self.fig)
        self.setParent(parent)
        
        # 🎮 游戏状态数据
        self.box_position = np.array([0.0, 0.0])
        self.box_target_position = np.array([0.0, 0.0])
        self.box_size = 0.8
        self.current_cop = None
        self.initial_cop = None
        self.movement_distance = 0.0
        
        # 🎮 控制状态
        self.current_control_mode = 'idle'
        self.current_system_mode = 'touchpad_only'  # 默认触控板模式
        
        # 🔄 Idle状态计数器 - 用于清除路径痕迹
        self.idle_frame_count = 0
        self.max_idle_frames = 10  # 连续10帧idle后清除路径
        
        # 🎆 烟花效果系统
        self.fireworks = []
        self.firework_lifetime = 60  # 烟花存活帧数
        self.max_fireworks = 30
        self.last_target_reached = False  # 记录上一次是否达成目标
        
        #  分析状态
        self.is_contact = False
        self.is_tangential = False
        self.is_sliding = False
        self.consensus_angle = None
        self.consensus_confidence = 0.0
        self.analysis_results = None
        
        # 📊 压力数据
        self.pressure_data = None
        self.pressure_colormap = 'plasma'
        
        # 🔄 渲染对象 - 添加压力图像和颜色条的引用
        self.box_patch = None
        self.cop_marker = None
        self.initial_cop_marker = None
        self.force_arrow = None
        self.pressure_image = None
        self.pressure_colorbar = None
        
        # 📈 历史轨迹
        self.cop_history = deque(maxlen=50)
        self.angle_history = deque(maxlen=20)
        self.trajectory_lines = None
        
        # ⚙️ 可视化参数
        self.show_trajectory = True
        self.show_analysis_details = True
        self.show_pressure_overlay = True
        self.animation_speed = 0.1
        self.force_scale = 1.0
        
        # 🗺️ 路径可视化管理器 - 在setup_subplots之后初始化
        self.path_manager = None
        
        # 🔄 更新定时器 - 使用动态帧率配置
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        
        # 📊 帧率统计变量
        self.frame_count = 0
        self.current_fps = 0.0
        self.last_fps_time = time.time()
        
        # 🎨 数据预处理参数 - 参考user_interface.py
        self.preprocessing_enabled = True
        self.use_gaussian_blur = True  # 改为高斯模糊
        self.use_xy_swap = False
        self.use_custom_colormap = True
        self.custom_colors = [
            [15, 15, 15],    # 黑色
            [48, 18, 59],    # 深紫色
            [71, 118, 238],  # 蓝色
            [27, 208, 213],  # 青色
            [97, 252, 108],  # 绿色
            [210, 233, 53],  # 黄色
            [254, 155, 45],  # 橙色
            [218, 57, 7],    # 红色
            [122, 4, 3]      # 深红色
        ]
        
        # 📊 颜色范围控制
        self.log_y_lim = [0.0, 0.005]  # 调整为更小的压力范围，提高精度
        self.minimum_y_lim = 0.0
        self.maximum_y_lim = 0.005  # 调整最大值为0.005
        
        # 🎨 高斯模糊参数
        self.gaussian_sigma = 1.0  # 高斯模糊的标准差
        
        # 🆕 3D显示参数 - 增强版
        self.show_3d_heatmap = True  # 默认显示3D
        self.heatmap_view_mode = '3d'  # '2d' 或 '3d'
        
        # 🎨 3D渲染增强参数
        self.enable_3d_lighting = True  # 启用3D光照效果
        self.enable_3d_shadows = True   # 启用3D阴影
        self.enable_3d_animation = True # 启用3D动画
        self.elevation_3d = 30          # 3D视角仰角
        self.azimuth_3d = 45            # 3D视角方位角
        self.rotation_speed_3d = 0.5    # 3D旋转速度
        self.surface_alpha_3d = 0.8     # 3D表面透明度
        self.wireframe_alpha_3d = 0.3   # 3D线框透明度
        self.enable_wireframe = True    # 默认启动网格
        
        # 🎨 平滑动画参数
        self.enable_smooth_transitions = True  # 启用平滑过渡
        self.transition_frames = 10            # 过渡帧数
        self.current_transition_frame = 0      # 当前过渡帧
        self.previous_pressure_data = None     # 前一帧压力数据
        
        # 🎨 高级渲染参数
        self.enable_anti_aliasing = True       # 启用抗锯齿
        self.enable_bloom_effect = False       # 启用泛光效果
        self.enable_depth_of_field = False     # 启用景深效果
        self.enable_motion_blur = False        # 启用运动模糊
        
        # 🎨 子图配置
        self.setup_subplots()
        
        # 🗺️ 初始化路径可视化管理器
        try:
            self.path_manager = PathVisualizationManager(self.ax_game)
        except Exception as e:
            print(f"⚠️ 路径可视化管理器初始化失败: {e}")
            self.path_manager = None
        
        # 🖱️ 鼠标事件
        self.mpl_connect('button_press_event', self.on_mouse_press)
        
        # 🔄 初始化界面布局为简化模式
        self.update_interface_layout('simplified')
        
        # 🎨 集成utils功能
        if UTILS_AVAILABLE:
            # 应用深色主题
            apply_dark_theme(self)
            print("🎨 已应用utils深色主题")
            
            # 设置异常处理
            sys.excepthook = lambda ty, value, tb: catch_exceptions(self, ty, value, tb)
            print("🛡️ 已设置utils异常处理")
        
        # 🔧 调试控制
        self.debug_level = 0  # 0=无调试, 1=重要事件, 2=详细信息, 3=全部调试
        self.debug_counter = 0  # 用于控制调试输出频率
        
        # 🔧 初始化子图
        self.setup_subplots()
        
        # 🗺️ 初始化路径可视化管理器
        if PATH_PLANNING_AVAILABLE:
            self.path_manager = PathVisualizationManager(self.ax_game)
        
        # 🎨 设置子图属性
        self.setup_subplot_properties()
        
        # 🔄 启动渲染循环
        self.start_rendering()
        
        print("✅ BoxGameRenderer 初始化完成")
    
    def keyPressEvent(self, event):
        """键盘事件处理 - 集成F11全屏切换"""
        if UTILS_AVAILABLE:
            # 检查是否是F11键
            if event.key() == Qt.Key_F11 and not event.isAutoRepeat():
                self.toggle_fullscreen()
            else:
                # 确保事件正确传递
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
    
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if hasattr(self, '_title_bar_hidden'):
            if not self._title_bar_hidden:
                # 隐藏标题栏
                self._saved_geometry = self.geometry()
                self.setWindowFlags(Qt.FramelessWindowHint)
                self.show()
                self._title_bar_hidden = True
                print("🖥️ 已切换到全屏模式")
            else:
                # 恢复标题栏
                self.setWindowFlags(Qt.Window)
                self.show()
                if self._saved_geometry:
                    self.setGeometry(self._saved_geometry)
                self._title_bar_hidden = False
                print("🖥️ 已退出全屏模式")
        else:
            # 初始化全屏状态
            self._title_bar_hidden = False
            self._saved_geometry = None
            self._title_bar_height = int(self.style().pixelMetric(Qt.PM_TitleBarHeight) * 1.3)
            self.toggle_fullscreen()
    
    def debug_print(self, message, level=1, frequency=1):
        """智能调试输出 - 控制输出频率和级别"""
        if self.debug_level >= level:
            # 控制输出频率
            if frequency == 1 or self.debug_counter % frequency == 0:
                print(message)
            self.debug_counter += 1
    
    def set_debug_level(self, level):
        """设置调试级别"""
        self.debug_level = max(0, min(3, level))
        print(f"🔧 调试级别已设置为: {self.debug_level}")
    
    def setup_subplots(self):
        """设置子图布局 - 扩大压力分布显示区域"""
        self.fig.clear()
        
        # 🔥 主游戏区域 - 使用64x64传感器原始坐标系
        self.ax_game = self.fig.add_subplot(1, 5, (1, 2))  # 改为1行5列，游戏区域占2/5
        self.ax_game.set_title("推箱子游戏 - 实时传感器", fontsize=14, color='white', fontweight='bold')
        self.ax_game.set_xlim(0, 63)
        self.ax_game.set_ylim(63, 0)  # 🔄 Y轴反转：传感器坐标系Y轴向下
        self.ax_game.set_aspect('equal')
        self.ax_game.grid(True, alpha=0.3, color='gray')
        self.ax_game.set_facecolor('black')
        
        # 📊 压力分布子图 - 扩大显示区域
        self.ax_pressure = self.fig.add_subplot(1, 5, (3, 5))  # 压力分布占3/5宽度
        self.ax_pressure.set_title("压力分布", fontsize=12, fontweight='bold')
        # 🎨 去除轴标签，因为2D模式不需要显示坐标轴
        # self.ax_pressure.set_xlabel("X")
        # self.ax_pressure.set_ylabel("Y")
        
        # 🎨 统一样式
        for ax in [self.ax_game, self.ax_pressure]:
            ax.tick_params(colors='white', labelsize=8)
            for spine in ax.spines.values():
                spine.set_color('white')
        
        # 🔧 优化布局 - 调整间距和比例
        self.fig.subplots_adjust(
            left=0.03,      # 减少左边距
            right=0.97,     # 减少右边距
            top=0.92,       # 减少上边距
            bottom=0.08,    # 减少下边距
            wspace=0.25     # 减少子图间距
        )
    
    def update_interface_layout(self, system_mode):
        """根据系统模式更新界面布局 - 2:3比例布局"""
        # 🔧 使用新的布局设置
        self.fig.subplots_adjust(
            left=0.03,      # 减少左边距
            right=0.97,     # 减少右边距
            top=0.92,       # 减少上边距
            bottom=0.08,    # 减少下边距
            wspace=0.25     # 减少子图间距
        )
        
        # 更新标题
        self.ax_game.set_title("推箱子游戏 - 实时传感器", fontsize=14, color='white', fontweight='bold')
        self.ax_pressure.set_title("压力分布 (2:3比例布局)", fontsize=12, color='white')
        
        # 强制重绘
        self.fig.canvas.draw()
        print(f"�� 界面布局已更新为2:3比例布局")
    
    def update_game_state(self, state_info: Dict):
        try:
            # 🎮 更新游戏状态
            self.is_contact = state_info.get('is_contact', False)
            self.is_tangential = state_info.get('is_tangential', False)
            self.is_sliding = state_info.get('is_sliding', False)
            
            # 📍 更新位置信息
            self.current_cop = state_info.get('current_cop')
            self.initial_cop = state_info.get('initial_cop')
            self.movement_distance = state_info.get('movement_distance', 0.0)
            
            # 🎯 更新分析结果
            self.consensus_angle = state_info.get('consensus_angle')
            self.consensus_confidence = state_info.get('consensus_confidence', 0.0)
            
            # 🎮 更新控制模式信息
            self.current_control_mode = state_info.get('control_mode', 'idle')
            new_system_mode = state_info.get('system_mode', 'touchpad_only')
            
            # 📏 更新阈值信息
            self.joystick_threshold = state_info.get('joystick_threshold', 0.05)  # 更新默认值
            self.touchpad_threshold = state_info.get('touchpad_threshold', 10)  # 更新默认值
            
            # 🆕 更新idle分析结果
            self.idle_analysis = state_info.get('idle_analysis')
            
            # 🔄 检查系统模式是否发生变化
            if new_system_mode != self.current_system_mode:
                self.current_system_mode = new_system_mode
                self.update_interface_layout(new_system_mode)
            
            # 📦 更新箱子位置
            box_pos = state_info.get('box_position')
            box_target = state_info.get('box_target_position')
            if box_pos is not None:
                if hasattr(box_pos, 'copy'):
                    self.box_position = box_pos.copy()
                else:
                    self.box_position = np.array(box_pos)
            if box_target is not None:
                if hasattr(box_target, 'copy'):
                    self.box_target_position = box_target.copy()
                else:
                    self.box_target_position = np.array(box_target)
            
            # 📈 更新轨迹历史
            if self.current_cop is not None:
                self.cop_history.append(np.array(self.current_cop))
            
            if self.consensus_angle is not None:
                self.angle_history.append(self.consensus_angle)
            
            # 🆕 idle状态下清空分析数据
            if self.current_control_mode == 'idle':
                self.consensus_angle = None
                self.consensus_confidence = 0.0
                self.analysis_results = None
                
                # 🔄 增加idle帧计数器
                self.idle_frame_count += 1
                
                # 🗺️ 检查是否需要清除COP轨迹历史
                if self.idle_frame_count >= self.max_idle_frames:
                    print(f"🧹 连续{self.max_idle_frames}帧idle，清除COP轨迹历史")
                    self.cop_history.clear()  # 清除COP轨迹历史
                    self.angle_history.clear()  # 清除角度历史
                    self.idle_frame_count = 0  # 重置计数器
            else:
                # 🔄 非idle状态，重置计数器
                self.idle_frame_count = 0
        except Exception as e:
            print(f"⚠️ 更新游戏状态时出错: {e}")
    
    def update_pressure_data(self, pressure_data: np.ndarray):
        """更新压力数据"""
        if pressure_data is not None and pressure_data.size > 0:
            self.pressure_data = pressure_data.copy()
            # print(f"🔥 渲染器收到压力数据: 形状={self.pressure_data.shape}, 最大值={np.max(self.pressure_data):.4f}")
        else:
            self.pressure_data = None
            print("⚠️ 渲染器收到空压力数据")
    
    def update_consensus_angle(self, angle: float, confidence: float):
        """更新共识角度"""
        self.consensus_angle = angle
        self.consensus_confidence = confidence
        print(f"🧭 渲染器收到共识角度: {angle:.1f}°, 置信度: {confidence:.2f}")
    
    def update_analysis_results(self, analysis_results: Dict):
        """更新分析结果 - 简化版：只记录，不显示"""
        self.analysis_results = analysis_results
        # 🎯 简化：不再显示分析结果调试信息，专注于COP显示
        # print('[调试] analysis_results:', self.analysis_results)  # 注释掉调试输出
        
        # 从分析结果中提取额外信息
        if analysis_results:
            # 可以从这里提取更多有用的可视化信息
            pass
    
    def update_navigation_info(self, nav_info: Dict):
        print("收到导航信息：", nav_info)
        if PATH_PLANNING_AVAILABLE:
            self.path_manager.update_path_data(nav_info)
            # 🔍 添加调试信息
            print(f"🔍 路径数据已更新到管理器")
            print(f"🔍 路径进度: {getattr(self.path_manager, 'path_progress', 'N/A')}")
            print(f"🔍 导航状态: {getattr(self.path_manager, 'has_navigation', 'N/A')}")
        else:
            print("⚠️ 路径规划模块不可用")
    
    def update_display(self):
        """更新显示内容"""
        try:
            # 🧹 清空所有子图
            self.clear_all_plots()
            
            # 🎮 渲染游戏区域
            self.render_game_area()
            
            # 📦 渲染箱子
            self.render_box()
            
            # 🎯 渲染COP和轨迹
            self.render_cop_and_trajectory()
            
            # 🎆 更新和渲染烟花效果
            self.update_fireworks()
            self.render_fireworks()
            
            # 📊 渲染状态文本
            self.render_status_text()
            
            # 🔥 渲染压力分布
            self.render_pressure_distribution()
            
            # 🎨 应用子图属性
            self.setup_subplot_properties()
            
            # 🔄 更新画布
            self.draw()
            
            # 📊 更新帧率统计
            self.update_frame_rate_stats()
            
        except Exception as e:
            print(f"⚠️ 渲染更新时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def clear_all_plots(self):
        """清空所有子图"""
        try:
            # 简化布局，只清空游戏区域和压力分布
            self.ax_game.clear()
            
            # 压力子图特殊处理
            if self.pressure_image is not None:
                # 保留压力图像，只清除其他绘制元素
                for artist in list(self.ax_pressure.get_children()):
                    try:
                        if artist != self.pressure_image and hasattr(artist, 'remove'):
                            artist.remove()
                    except Exception as e:
                        # 忽略无法删除的艺术家对象
                        pass
            else:
                self.ax_pressure.clear()
            
            # 重新设置基本属性
            self.setup_subplot_properties()
            
        except Exception as e:
            print(f"⚠️ 清除图形时出错: {e}")
            # 如果清除失败，尝试重新创建子图
            try:
                self.setup_subplots()
                print("✅ 子图已重新创建")
            except Exception as e2:
                print(f"❌ 重新创建子图失败: {e2}")
    
    def setup_subplot_properties(self):
        """重新设置子图属性"""
        # 游戏区域
        self.ax_game.set_title("推箱子游戏 - 实时传感器", fontsize=14, color='white', fontweight='bold')
        self.ax_game.set_xlim(0, 63)
        self.ax_game.set_ylim(63, 0)  # 🔄 Y轴反转：传感器坐标系Y轴向下
        self.ax_game.set_aspect('equal')
        self.ax_game.grid(True, alpha=0.3, color='gray')
        self.ax_game.set_facecolor('black')
        
        # 压力分布图
        self.ax_pressure.set_title("压力分布", fontsize=12, color='white')
        self.ax_pressure.set_facecolor('black')
        
        # 统一样式
        for ax in [self.ax_game, self.ax_pressure]:
            ax.tick_params(colors='white', labelsize=8)
            for spine in ax.spines.values():
                spine.set_color('white')
    
    def render_game_area(self):
        """渲染游戏区域"""
        # 🗺️ 渲染路径可视化
        if PATH_PLANNING_AVAILABLE:
            self.path_manager.render_complete_path_visualization(self.box_position)
    
    def render_box(self):
        """渲染箱子"""
        # 🎨 确定箱子颜色
        if self.is_sliding:
            box_color = 'lime'
            edge_color = 'green'
            alpha = 0.8
        elif self.is_tangential:
            box_color = 'orange'
            edge_color = 'darkorange'
            alpha = 0.7
        elif self.is_contact:
            box_color = 'yellow'
            edge_color = 'gold'
            alpha = 0.6
        else:
            box_color = 'lightblue'
            edge_color = 'blue'
            alpha = 0.5
        
        # 📦 绘制箱子
        box_size = 6.0
        box_rect = FancyBboxPatch(
            (self.box_position[0] - box_size/2, self.box_position[1] - box_size/2),
            box_size, box_size,
            boxstyle="round,pad=0.5",
            linewidth=3,
            edgecolor=edge_color,
            facecolor=box_color,
            alpha=alpha
        )
        self.ax_game.add_patch(box_rect)
        
        # 📦 箱子中心标记
        self.ax_game.plot(self.box_position[0], self.box_position[1], 
                         'k+', markersize=8, markeredgewidth=2)
        
        # 🎯 目标位置标记（如果不同于当前位置）
        if np.linalg.norm(self.box_target_position - self.box_position) > 1:
            target_rect = Rectangle(
                (self.box_target_position[0] - box_size/2, self.box_target_position[1] - box_size/2),
                box_size, box_size,
                linewidth=2,
                edgecolor='red',
                facecolor='none',
                linestyle='--',
                alpha=0.6
            )
            self.ax_game.add_patch(target_rect)
            
            # 🏹 绘制移动方向箭头
            self.render_movement_direction_arrow()
        
        # 🎮 检查目标达成
        self.check_target_reached()
    
    def render_cop_and_trajectory(self):
        """渲染压力中心和轨迹"""
        # 🎯 绘制当前压力中心
        if self.current_cop is not None and self.current_cop[0] is not None and self.current_cop[1] is not None:
            self.ax_game.plot(self.current_cop[0], self.current_cop[1], 
                             'ro', markersize=8, markeredgewidth=2, 
                             markeredgecolor='darkred', alpha=0.8)
        
        # 🎯 绘制初始压力中心
        if self.initial_cop is not None and self.initial_cop[0] is not None and self.initial_cop[1] is not None:
            self.ax_game.plot(self.initial_cop[0], self.initial_cop[1], 
                             'go', markersize=6, markeredgewidth=1, 
                             markeredgecolor='darkgreen', alpha=0.6)
        
        # 📈 绘制轨迹
        if self.show_trajectory and len(self.cop_history) > 1:
            # 过滤掉包含None的轨迹点
            valid_trajectory = []
            for point in self.cop_history:
                if point is not None and len(point) >= 2 and point[0] is not None and point[1] is not None:
                    valid_trajectory.append(point)
            
            if len(valid_trajectory) > 1:
                trajectory = np.array(valid_trajectory)
                self.ax_game.plot(trajectory[:, 0], trajectory[:, 1], 
                                 'b-', linewidth=2, alpha=0.6)
    
    def render_movement_direction_arrow(self):
        """绘制从箱子到目标位置的移动方向箭头和角度"""
        if np.linalg.norm(self.box_target_position - self.box_position) > 1:
            # 计算方向向量
            direction = self.box_target_position - self.box_position
            distance = np.linalg.norm(direction)
            
            # 计算角度（弧度转度）
            angle_rad = np.arctan2(direction[1], direction[0])
            angle_deg = np.degrees(angle_rad)
            
            # 绘制箭头
            arrow_length = min(distance * 0.8, 15)  # 箭头长度，不超过距离的80%或15像素
            arrow_end_x = self.box_position[0] + arrow_length * np.cos(angle_rad)
            arrow_end_y = self.box_position[1] + arrow_length * np.sin(angle_rad)
            
            # 使用annotate绘制箭头
            self.ax_game.annotate('', 
                                 xy=(arrow_end_x, arrow_end_y), 
                                 xytext=(self.box_position[0], self.box_position[1]),
                                 arrowprops=dict(arrowstyle='->', lw=3, 
                                               color='yellow', alpha=0.8,
                                               mutation_scale=6))
            
            # 显示距离和角度信息
            info_text = f"距离: {distance:.1f}\n角度: {angle_deg:.1f}°"
            self.ax_game.text(arrow_end_x + 2, arrow_end_y + 2, info_text,
                             fontsize=8, color='yellow', 
                             bbox=dict(boxstyle="round,pad=0.3", 
                                      facecolor='black', alpha=0.7))
    
    def check_target_reached(self):
        """检查目标是否达成并触发烟花效果"""
        # 🎯 优化：只在有路径数据时才进行详细检查
        if (hasattr(self, 'path_manager') and self.path_manager and 
            hasattr(self.path_manager, 'path_progress') and 
            self.path_manager.path_progress):
            
            progress = self.path_manager.path_progress
            
            # 检查是否在路径模式下且已完成所有路径点
            is_path_mode = self.path_manager.has_navigation
            is_completed = progress.get('is_completed', False)
            
            # 🎯 优化：使用智能调试输出
            self.debug_print(f"🔍 路径状态: 模式={is_path_mode}, 完成={is_completed}", level=2, frequency=30)
            
            if is_path_mode and is_completed:
                # 检查箱子是否到达最终目标位置
                distance_to_target = np.linalg.norm(self.box_position - self.box_target_position)
                
                if distance_to_target < 0.5:
                    # 只在首次达成时触发烟花
                    if not self.last_target_reached:
                        self.debug_print("🎆 目标达成！触发烟花效果", level=1)
                        self.add_firework_effect()
                        self.last_target_reached = True
                else:
                    # 如果箱子离开目标位置，重置触发状态
                    if self.last_target_reached:
                        self.debug_print(f"🔍 箱子离开目标位置，重置烟花触发状态", level=2)
                    self.last_target_reached = False
            else:
                # 重置触发状态
                if self.last_target_reached:
                    self.debug_print(f"🔍 路径未完成，重置烟花触发状态", level=2)
                self.last_target_reached = False
        else:
            # 没有路径数据，重置触发状态
            if self.last_target_reached:
                self.debug_print(f"🔍 无路径数据，重置烟花触发状态", level=2)
            self.last_target_reached = False
    
    def add_firework_effect(self):
        """在目标位置添加烟花效果"""
        if len(self.fireworks) >= self.max_fireworks:
            return
        
        # 在目标位置生成15个烟花粒子
        for _ in range(15):
            # 随机角度和距离
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(2, 8)
            
            # 计算粒子位置
            x = self.box_target_position[0] + distance * np.cos(angle)
            y = self.box_target_position[1] + distance * np.sin(angle)
            
            # 随机速度
            vx = np.random.uniform(-2, 2)
            vy = np.random.uniform(-3, -1)  # 向上飞
            
            # 随机颜色
            colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'white']
            color = np.random.choice(colors)
            
            # 随机大小
            size = np.random.uniform(3, 8)
            
            # 创建烟花粒子
            firework = {
                'x': x, 'y': y,
                'vx': vx, 'vy': vy,
                'color': color,
                'size': size,
                'lifetime': self.firework_lifetime
            }
            
            self.fireworks.append(firework)
        
        # 🎯 优化：只在首次触发时输出信息
        self.debug_print(f"🎆 烟花效果已触发 ({len(self.fireworks)}个粒子)", level=1)
    
    def update_fireworks(self):
        """更新烟花粒子状态"""
        for firework in self.fireworks[:]:  # 使用切片复制避免修改迭代列表
            # 更新位置
            firework['x'] += firework['vx']
            firework['y'] += firework['vy']
            
            # 添加重力效果
            firework['vy'] -= 0.1
            
            # 减少生命值
            firework['lifetime'] -= 1
            
            # 移除死亡的粒子
            if firework['lifetime'] <= 0:
                self.fireworks.remove(firework)
    
    def render_fireworks(self):
        """渲染烟花粒子"""
        for firework in self.fireworks:
            # 计算透明度（基于生命值）
            alpha = firework['lifetime'] / self.firework_lifetime
            
            # 绘制粒子
            self.ax_game.plot(firework['x'], firework['y'], 
                             'o', color=firework['color'], 
                             markersize=firework['size'],
                             alpha=alpha,
                             markeredgecolor='white',
                             markeredgewidth=1)
    
    def render_force_vector(self):
        """渲染力矢量"""
        if (self.consensus_angle is not None and 
            self.current_cop is not None and 
            self.current_cop[0] is not None and 
            self.current_cop[1] is not None):
            # 计算力矢量的终点
            angle_rad = np.radians(self.consensus_angle)
            force_length = 10 * self.consensus_confidence  # 根据置信度调整长度
            
            end_x = self.current_cop[0] + force_length * np.cos(angle_rad)
            end_y = self.current_cop[1] + force_length * np.sin(angle_rad)
            
            # 绘制力矢量箭头
            self.ax_game.annotate('', 
                                 xy=(end_x, end_y), 
                                 xytext=(self.current_cop[0], self.current_cop[1]),
                                 arrowprops=dict(arrowstyle='->', lw=2, 
                                               color='red', alpha=0.8))
    
    def render_status_text(self):
        """渲染状态文本 - 只显示实际渲染帧率"""
        # 🎨 只显示实际渲染帧率
        fps_text = f"渲染帧率: {self.current_fps:.1f} FPS"
        
        # 🖼️ 显示帧率文本
        self.ax_game.text(2, 60, fps_text, 
                         fontsize=12, color='white', fontweight='bold',
                         verticalalignment='top',
                         bbox=dict(boxstyle="round,pad=0.5", 
                                  facecolor='black', alpha=0.8,
                                  edgecolor='white', linewidth=1))
    
    def render_prominent_status_indicator(self):
        """在右上方渲染突出显示的状态指示器 - 已移除，只显示帧率"""
        pass
    
    def render_pressure_distribution(self):
        """渲染压力分布 - 支持2D/3D切换"""
        if self.pressure_data is None:
            return
        
        try:
            # 预处理数据
            processed_data = self.preprocess_pressure_data(self.pressure_data)
            if processed_data is None:
                return
            
            display_data = processed_data['data']
            
            # 根据模式选择渲染方式
            if self.heatmap_view_mode == '3d':
                self.render_3d_heatmap(display_data)
            else:
                self.render_2d_heatmap(display_data)
            
            # 更新画布
            self.draw()
            
        except Exception as e:
            print(f"❌ 压力分布渲染失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 🆕 新增idle分析详情渲染函数
    def render_idle_analysis_details(self):
        """在压力图右侧渲染idle分析详情"""
        if not hasattr(self, 'idle_analysis') or not self.idle_analysis:
            return
        
        # 获取分析数据
        factors = self.idle_analysis.get('factors', {})
        values = self.idle_analysis.get('values', {})
        thresholds = self.idle_analysis.get('thresholds', {})
        
        # 在压力图右侧显示详细信息
        detail_lines = []
        detail_lines.append("🔍 Idle分析详情:")
        
        # 显示关键指标
        if 'max_pressure' in values:
            pressure_threshold = thresholds.get('pressure_threshold', 0.01)
            pressure_status = "✅" if values['max_pressure'] >= pressure_threshold else "❌"
            detail_lines.append(f"{pressure_status} 压力: {values['max_pressure']:.4f}/{pressure_threshold}")
        
        if 'contact_area' in values:
            area_threshold = thresholds.get('contact_area_threshold', 5)
            area_status = "✅" if values['contact_area'] >= area_threshold else "❌"
            detail_lines.append(f"{area_status} 面积: {values['contact_area']}/{area_threshold}")
        
        if 'gradient_mean' in values:
            grad_threshold = thresholds.get('gradient_threshold', 1e-5)
            grad_status = "✅" if values['gradient_mean'] < grad_threshold else "❌"
            detail_lines.append(f"{grad_status} 梯度: {values['gradient_mean']:.6f}/{grad_threshold}")
        
        if 'cop_displacement' in values:
            slide_threshold = thresholds.get('sliding_threshold', 0.08)
            slide_status = "✅" if values['cop_displacement'] <= slide_threshold else "❌"
            detail_lines.append(f"{slide_status} 位移: {values['cop_displacement']:.3f}/{slide_threshold}")
        
        # 显示状态标志
        detail_lines.append("")
        detail_lines.append("状态标志:")
        detail_lines.append(f"  滑动: {'❌' if factors.get('is_sliding', False) else '✅'}")
        detail_lines.append(f"  切向力: {'❌' if factors.get('is_tangential', False) else '✅'}")
        
        # 渲染详细信息
        detail_text = '\n'.join(detail_lines)
        self.ax_pressure.text(0.98, 0.02, detail_text, 
                             color='white', fontsize=8, 
                             va='bottom', ha='right',
                             transform=self.ax_pressure.transAxes,
                             bbox=dict(boxstyle="round,pad=0.3", 
                                      facecolor='black', alpha=0.8))

    def on_mouse_press(self, event):
        """处理鼠标点击事件"""
        if event.inaxes == self.ax_game:
            self.mouse_pressed.emit(event.xdata, event.ydata)
    
    def reset_visualization(self):
        """重置可视化"""
        # 清空历史数据
        self.cop_history.clear()
        self.angle_history.clear()
        
        # 重置状态
        self.is_contact = False
        self.is_tangential = False
        self.is_sliding = False
        self.consensus_angle = None
        self.consensus_confidence = 0.0
        self.current_cop = None
        self.initial_cop = None
        self.movement_distance = 0.0
        
        # 🔄 重置idle计数器
        self.idle_frame_count = 0
        
        # 🎆 清空烟花效果
        self.fireworks.clear()
        self.last_target_reached = False
        
        # 重置路径可视化
        self.path_manager.clear_path_visualization()
        
        print("🔄 可视化已重置")
    
    def set_visualization_options(self, options: Dict):
        """设置可视化选项"""
        try:
            # 🆕 处理2D/3D热力图切换
            if 'toggle_heatmap_mode' in options:
                self.toggle_heatmap_mode()
                return
            
            # 处理其他可视化选项
            if 'show_trajectory' in options:
                self.show_trajectory = options['show_trajectory']
            if 'show_analysis_details' in options:
                self.show_analysis_details = options['show_analysis_details']
            if 'show_pressure_overlay' in options:
                self.show_pressure_overlay = options['show_pressure_overlay']
            if 'pressure_colormap' in options:
                self.pressure_colormap = options['pressure_colormap']
            if 'force_scale' in options:
                self.force_scale = options['force_scale']
            
            print(f"🎨 可视化选项已更新: {list(options.keys())}")
            
        except Exception as e:
            print(f"❌ 设置可视化选项失败: {e}")
    
    def start_rendering(self):
        """开始渲染循环"""
        # 🚀 使用动态帧率配置
        try:
            from interfaces.ordinary.BoxGame.run_box_game_optimized import FrameRateConfig
            interval_ms = FrameRateConfig.get_interval_ms("renderer_fps")
            target_fps = 1000 / interval_ms
        except ImportError:
            # 回退到默认配置
            target_fps = 30
            interval_ms = int(1000 / target_fps)
        
        self.update_timer.start(interval_ms)
        print(f"🚀 渲染循环已启动 (目标FPS: {target_fps:.1f})")
    
    def stop_rendering(self):
        """停止渲染循环"""
        self.update_timer.stop()
        print("⏹️ 渲染循环已停止")
    
    def update_frame_rate(self):
        """更新帧率设置"""
        try:
            from interfaces.ordinary.BoxGame.run_box_game_optimized import FrameRateConfig
            interval_ms = FrameRateConfig.get_interval_ms("renderer_fps")
            target_fps = 1000 / interval_ms
            self.update_timer.setInterval(interval_ms)
            print(f"🎨 渲染器帧率已更新: {target_fps:.1f} FPS")
        except ImportError:
            print("⚠️ 无法导入FrameRateConfig，使用默认帧率")
    
    def update_frame_rate_stats(self):
        """更新帧率统计"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:  # 每秒更新一次
            self.current_fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
            
            # 🆕 输出实际渲染帧率
            print(f"🎨 渲染器实际帧率: {self.current_fps:.1f} FPS")
            
            # 在标题中显示FPS（可选）
            # self.ax_game.set_title(f"推箱子游戏 - 实时传感器 (FPS: {self.current_fps:.1f})")
    
    def get_performance_stats(self):
        """获取性能统计"""
        return {
            'current_fps': self.current_fps,
            'target_fps': 30,
            'frame_count': self.frame_count
        }

    # 🎨 数据预处理方法 - 参考user_interface.py
    def gaussian_blur(self, data, sigma=1.0):
        """高斯模糊 - 平滑压力数据"""
        try:
            from scipy.ndimage import gaussian_filter
            return gaussian_filter(data, sigma=sigma)
        except ImportError:
            # 如果没有scipy，使用简单的均值滤波作为备选
            from scipy.ndimage import uniform_filter
            return uniform_filter(data, size=3)
    
    def apply_xy_swap(self, data):
        """应用X/Y轴交换 - 集成utils功能"""
        if self.use_xy_swap:
            if UTILS_AVAILABLE:
                # 使用utils的apply_swap功能
                try:
                    from utils import apply_swap
                    return apply_swap(data)
                except ImportError:
                    # 回退到本地实现
                    return data.T
            else:
                # 本地实现
                return data.T
        return data
    
    def get_custom_colormap(self):
        """获取自定义颜色映射 - 参考user_interface.py的颜色配置"""
        if self.use_custom_colormap:
            import matplotlib.colors as mcolors
            colors = np.array(self.custom_colors) / 255.0  # 归一化到0-1
            pos = np.linspace(0, 1, len(colors))
            cmap = mcolors.LinearSegmentedColormap.from_list('custom_pressure', list(zip(pos, colors)))
            return cmap
        else:
            return self.pressure_colormap
    
    @property
    def y_lim(self):
        """获取颜色范围 - 直接使用设置的范围"""
        return self.log_y_lim  # 直接返回设置的颜色范围
    
    def preprocess_pressure_data(self, pressure_data):
        """预处理压力数据 - 综合应用各种变换"""
        if pressure_data is None or pressure_data.size == 0:
            return None
        
        try:
            # 复制数据避免修改原始数据
            processed_data = pressure_data.copy()
            
            # 1. 高斯模糊
            if self.use_gaussian_blur:
                processed_data = self.gaussian_blur(processed_data, sigma=self.gaussian_sigma)
                # print(f"🔄 应用高斯模糊: 原始范围[{pressure_data.min():.3f}, {pressure_data.max():.3f}] "
                #       f"-> 平滑后[{processed_data.min():.3f}, {processed_data.max():.3f}]")
            
            # 2. 坐标轴交换
            processed_data = self.apply_xy_swap(processed_data)
            
            # 3. 获取颜色范围
            vmin, vmax = self.y_lim
            
            return {
                'data': processed_data,
                'vmin': vmin,
                'vmax': vmax,
                'colormap': self.get_custom_colormap()
            }
            
        except Exception as e:
            print(f"❌ 数据预处理失败: {e}")
            # 返回原始数据
            return {
                'data': pressure_data,
                'vmin': 0,
                'vmax': np.max(pressure_data) if np.max(pressure_data) > 0 else 0.01,
                'colormap': self.pressure_colormap
            }
    
    # 🎨 预处理参数控制方法
    def set_preprocessing_options(self, options):
        """设置预处理选项"""
        if 'preprocessing_enabled' in options:
            self.preprocessing_enabled = options['preprocessing_enabled']
        if 'use_gaussian_blur' in options:
            self.use_gaussian_blur = options['use_gaussian_blur']
        if 'use_xy_swap' in options:
            self.use_xy_swap = options['use_xy_swap']
        if 'use_custom_colormap' in options:
            self.use_custom_colormap = options['use_custom_colormap']
        if 'log_y_lim' in options:
            self.log_y_lim = options['log_y_lim']
        if 'gaussian_sigma' in options:
            self.gaussian_sigma = options['gaussian_sigma']
        if 'gaussian_blur_sigma' in options:
            self.gaussian_sigma = options['gaussian_blur_sigma']
        
        print(f"🎨 预处理选项已更新: {options}")
    
    def get_preprocessing_options(self):
        """获取当前预处理选项"""
        return {
            'preprocessing_enabled': self.preprocessing_enabled,
            'use_gaussian_blur': self.use_gaussian_blur,
            'use_xy_swap': self.use_xy_swap,
            'use_custom_colormap': self.use_custom_colormap,
            'log_y_lim': self.log_y_lim.copy(),
            'gaussian_sigma': self.gaussian_sigma
        }
    
    def toggle_preprocessing(self, enabled=None):
        """切换预处理功能"""
        if enabled is None:
            self.preprocessing_enabled = not self.preprocessing_enabled
        else:
            self.preprocessing_enabled = enabled
        
        print(f"🎨 预处理功能: {'启用' if self.preprocessing_enabled else '禁用'}")
    
    def toggle_gaussian_blur(self, enabled=None):
        """切换高斯模糊"""
        if enabled is None:
            self.use_gaussian_blur = not self.use_gaussian_blur
        else:
            self.use_gaussian_blur = enabled
        
        print(f"🎨 高斯模糊: {'启用' if self.use_gaussian_blur else '禁用'}")
    
    def toggle_xy_swap(self, enabled=None):
        """切换坐标轴交换"""
        if enabled is None:
            self.use_xy_swap = not self.use_xy_swap
        else:
            self.use_xy_swap = enabled
        
        print(f"🎨 坐标轴交换: {'启用' if self.use_xy_swap else '禁用'}")
    
    def toggle_custom_colormap(self, enabled=None):
        """切换自定义颜色映射"""
        if enabled is None:
            self.use_custom_colormap = not self.use_custom_colormap
        else:
            self.use_custom_colormap = enabled
        
        print(f"🎨 自定义颜色映射: {'启用' if self.use_custom_colormap else '禁用'}")
    
    def set_color_range(self, y_min, y_max):
        """设置颜色范围"""
        self.log_y_lim = [y_min, y_max]
        print(f"🎨 颜色范围已设置: [{y_min}, {y_max}]")
    
    def set_precise_pressure_range(self, max_pressure=0.005):
        """设置精确的压力范围 - 从0到指定最大值"""
        self.log_y_lim = [0.0, max_pressure]
        self.minimum_y_lim = 0.0
        self.maximum_y_lim = max_pressure
        print(f"🎨 精确压力范围已设置: [0.0, {max_pressure}]")
        
        # 如果当前有压力数据，立即重新渲染
        if self.pressure_data is not None:
            self.render_pressure_distribution()
    
    def set_adaptive_pressure_range(self, data_percentile=95):
        """根据当前压力数据自适应设置压力范围"""
        if self.pressure_data is not None:
            # 计算指定百分位数的压力值作为最大值
            max_pressure = np.percentile(self.pressure_data, data_percentile)
            # 确保最小值不为0，避免显示问题
            min_pressure = np.percentile(self.pressure_data, 5)  # 5%分位数作为最小值
            
            self.log_y_lim = [min_pressure, max_pressure]
            self.minimum_y_lim = min_pressure
            self.maximum_y_lim = max_pressure
            print(f"🎨 自适应压力范围已设置: [{min_pressure:.6f}, {max_pressure:.6f}] (基于{data_percentile}%分位数)")
            
            # 立即重新渲染
            self.render_pressure_distribution()
        else:
            print("⚠️ 没有压力数据，无法设置自适应范围")
    
    def reset_preprocessing(self):
        """重置预处理参数为默认值"""
        self.preprocessing_enabled = True
        self.use_gaussian_blur = True
        self.use_xy_swap = False
        self.use_custom_colormap = True
        self.log_y_lim = [0.0, 0.005]  # 调整为更小的压力范围
        self.gaussian_sigma = 1.0
        print("🎨 预处理参数已重置为默认值")

    def toggle_heatmap_mode(self):
        """切换2D/3D热力图显示模式"""
        if self.heatmap_view_mode == '2d':
            self.heatmap_view_mode = '3d'
            self.heatmap_mode_btn.setText("切换到2D")
            self.heatmap_mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: 2px solid #FFFFFF !important;
                    padding: 5px;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                    border: 2px solid #E0E0E0 !important;
                }
            """)
            print("🎨 切换到3D热力图显示")
        else:
            self.heatmap_view_mode = '2d'
            self.heatmap_mode_btn.setText("切换到3D")
            self.heatmap_mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: 2px solid #FFFFFF !important;
                    padding: 5px;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                    border: 2px solid #E0E0E0 !important;
                }
            """)
            print("🎨 切换到2D热力图显示")
        
        # 重新渲染压力分布
        if self.pressure_data is not None:
            self.render_pressure_distribution()
    
    def render_3d_heatmap(self, pressure_data):
        """渲染3D热力图 - 增强版，支持更多美观效果"""
        try:
            # 清除当前子图并重新创建3D子图
            self.ax_pressure.remove()
            from mpl_toolkits.mplot3d import Axes3D
            # 🔄 修改为1行5列布局，压力分布占据3/5宽度
            self.ax_pressure = self.fig.add_subplot(1, 5, (3, 5), projection='3d')
            
            # 创建网格
            rows, cols = pressure_data.shape
            x = np.arange(cols)
            y = np.arange(rows)
            X, Y = np.meshgrid(x, y)
            
            # 🎨 应用平滑处理
            smoothed_data = self.apply_3d_smoothing(pressure_data)
            
            # 🎨 创建增强的颜色映射
            enhanced_colormap = self.create_enhanced_colormap()
            
            # 🎨 获取当前设置的颜色范围
            vmin, vmax = self.y_lim
            
            # 绘制3D表面 - 增强版，使用设置的颜色范围
            surf = self.ax_pressure.plot_surface(
                X, Y, smoothed_data, 
                cmap=enhanced_colormap,
                alpha=self.surface_alpha_3d,
                linewidth=0,
                antialiased=self.enable_anti_aliasing,
                vmin=vmin,  # 使用设置的颜色范围
                vmax=vmax,
                shade=self.enable_3d_shadows,  # 启用阴影
                lightsource=None if not self.enable_3d_lighting else plt.matplotlib.colors.LightSource(azdeg=315, altdeg=45)
            )
            
            # 🎨 添加线框效果（可选）
            if self.enable_wireframe:
                wire = self.ax_pressure.plot_wireframe(
                    X, Y, smoothed_data,
                    alpha=self.wireframe_alpha_3d,
                    color='white',
                    linewidth=0.5
                )
            
            # 🎨 添加等高线投影（只在XY平面）
            if self.enable_3d_shadows:
                # 在XY平面上添加等高线投影
                contour = self.ax_pressure.contour(
                    X, Y, smoothed_data,
                    levels=10,
                    alpha=0.3,
                    colors='white',
                    linewidths=0.5,
                    zdir='z',
                    offset=0.0  # 投影到z=0平面
                )
            
            # 设置标签和标题
            self.ax_pressure.set_title("压力分布 (3D 2:3比例布局)", fontsize=12, fontweight='bold', color='white')
            
            # 🎨 去除轴标签
            self.ax_pressure.set_xlabel("", color='white')
            self.ax_pressure.set_ylabel("", color='white')
            self.ax_pressure.set_zlabel("", color='white')
            
            # 🎨 设置Z轴范围 - 使用设置的颜色范围
            self.ax_pressure.set_zlim(vmin, vmax)
            
            # 🎨 动态视角设置
            if self.enable_3d_animation:
                # 添加轻微的自动旋转
                self.azimuth_3d += self.rotation_speed_3d
                if self.azimuth_3d > 360:
                    self.azimuth_3d -= 360
            
            # 设置视角
            self.ax_pressure.view_init(elev=self.elevation_3d, azim=self.azimuth_3d)
            
            # 🎨 添加颜色条 - 扩大版
            if hasattr(self, 'pressure_colorbar') and self.pressure_colorbar is not None:
                try:
                    self.pressure_colorbar.remove()
                except:
                    pass
            
            self.pressure_colorbar = self.fig.colorbar(
                surf, 
                ax=self.ax_pressure, 
                shrink=0.9,  # 增加颜色条大小
                aspect=25,   # 调整颜色条比例
                pad=0.15     # 增加颜色条间距
            )
            self.pressure_colorbar.set_label('压力值', rotation=270, labelpad=20, color='white', fontsize=10)
            self.pressure_colorbar.ax.tick_params(colors='white', labelsize=9)
            
            # 🎨 设置3D样式 - 去除网格和轴
            self.setup_3d_style_clean()
            
            # 🎨 添加泛光效果（如果启用）
            if self.enable_bloom_effect:
                self.apply_bloom_effect(smoothed_data)
            
            # print(f"🎨 3D热力图渲染完成 (2:3比例布局) - 颜色范围: [{vmin:.6f}, {vmax:.6f}]")
            
        except Exception as e:
            print(f"❌ 3D热力图渲染失败: {e}")
            import traceback
            traceback.print_exc()
            # 如果3D渲染失败，回退到2D
            self.heatmap_view_mode = '2d'
            self.heatmap_mode_btn.setText("切换到3D")
            self.render_2d_heatmap(pressure_data)
    
    def apply_3d_smoothing(self, data):
        """应用3D平滑处理"""
        try:
            from scipy.ndimage import gaussian_filter
            # 应用更强的平滑
            smoothed = gaussian_filter(data, sigma=1.5)
            
            # 应用双边滤波（如果可用）
            try:
                from scipy.ndimage import uniform_filter
                # 简单的边缘保持平滑
                edge_preserved = uniform_filter(smoothed, size=2)
                return edge_preserved
            except:
                return smoothed
        except ImportError:
            # 如果没有scipy，使用简单的均值滤波
            from scipy.ndimage import uniform_filter
            return uniform_filter(data, size=3)
    
    def create_enhanced_colormap(self):
        """创建增强的颜色映射 - 集成utils颜色方案"""
        if self.use_custom_colormap:
            # 🎨 使用utils的颜色映射方案
            if UTILS_AVAILABLE:
                # 使用utils的9级颜色映射
                enhanced_colors = []
                for color in COLORS:
                    # 将RGB值转换为0-1范围
                    enhanced_colors.append([c/255.0 for c in color])
                
                # 创建颜色映射位置
                pos = np.linspace(0, 1, len(enhanced_colors))
                
                # 创建LinearSegmentedColormap
                cmap = LinearSegmentedColormap.from_list('utils_enhanced', list(zip(pos, enhanced_colors)))
                print(f"🎨 使用utils颜色映射: {len(enhanced_colors)}级")
                return cmap
            else:
                # 回退到原来的颜色映射
                enhanced_colors = [
                    [0, 0, 0],        # 纯黑
                    [20, 20, 60],     # 深蓝黑
                    [40, 40, 120],    # 深蓝
                    [60, 120, 200],   # 蓝色
                    [100, 180, 255],  # 浅蓝
                    [150, 220, 255],  # 天蓝
                    [200, 240, 255],  # 极浅蓝
                    [255, 255, 200],  # 浅黄
                    [255, 220, 100],  # 黄色
                    [255, 180, 50],   # 橙色
                    [255, 120, 20],   # 红橙
                    [255, 60, 10],    # 红色
                    [200, 20, 5],     # 深红
                    [120, 10, 2]      # 暗红
                ]
                
                # 归一化颜色
                enhanced_colors = np.array(enhanced_colors) / 255.0
                
                # 创建颜色映射
                pos = np.linspace(0, 1, len(enhanced_colors))
                cmap = LinearSegmentedColormap.from_list('enhanced_pressure', list(zip(pos, enhanced_colors)))
                print(f"🎨 使用默认颜色映射: {len(enhanced_colors)}级")
                return cmap
        else:
            return self.pressure_colormap
    
    def setup_3d_style_clean(self):
        """设置3D样式 - 去除网格和轴"""
        # 设置背景色
        self.ax_pressure.set_facecolor('black')
        
        # 🎨 去除所有网格
        self.ax_pressure.grid(False)
        
        # 🎨 去除xoz和yoz面的格子
        self.ax_pressure.xaxis.pane.fill = False
        self.ax_pressure.yaxis.pane.fill = False
        self.ax_pressure.zaxis.pane.fill = False
        
        # 🎨 去除轴线边缘
        self.ax_pressure.xaxis.pane.set_edgecolor('none')
        self.ax_pressure.yaxis.pane.set_edgecolor('none')
        self.ax_pressure.zaxis.pane.set_edgecolor('none')
        
        # 🎨 去除刻度线
        self.ax_pressure.set_xticks([])
        self.ax_pressure.set_yticks([])
        self.ax_pressure.set_zticks([])
        
        # 🎨 去除刻度标签
        self.ax_pressure.set_xticklabels([])
        self.ax_pressure.set_yticklabels([])
        self.ax_pressure.set_zticklabels([])
        
        # 🎨 去除轴线标签
        self.ax_pressure.xaxis.label.set_text("")
        self.ax_pressure.yaxis.label.set_text("")
        self.ax_pressure.zaxis.label.set_text("")
        
        # 🎨 去除轴线
        self.ax_pressure.xaxis.line.set_color('none')
        self.ax_pressure.yaxis.line.set_color('none')
        self.ax_pressure.zaxis.line.set_color('none')
        
        # 🎨 去除刻度线
        self.ax_pressure.xaxis.set_tick_params(length=0)
        self.ax_pressure.yaxis.set_tick_params(length=0)
        self.ax_pressure.zaxis.set_tick_params(length=0)
    
    def apply_bloom_effect(self, data):
        """应用泛光效果"""
        try:
            # 创建高亮区域
            threshold = np.percentile(data, 95)  # 95%分位数作为阈值
            bright_areas = data > threshold
            
            # 在高亮区域添加额外的发光效果
            if np.any(bright_areas):
                # 这里可以添加更复杂的泛光效果
                pass
        except Exception as e:
            print(f"⚠️ 泛光效果应用失败: {e}")
    
    def render_2d_heatmap(self, pressure_data):
        """渲染2D热力图 - 扩大显示区域版"""
        try:
            # 清除当前子图并重新创建2D子图
            self.ax_pressure.remove()
            self.ax_pressure = self.fig.add_subplot(1, 5, (3, 5))  # 使用新的布局：占3/5宽度
            
            # 🎨 应用平滑处理
            smoothed_data = self.apply_2d_smoothing(pressure_data)
            
            # 🎨 创建增强的颜色映射
            enhanced_colormap = self.create_enhanced_colormap()
            
            # 绘制2D热力图 - 扩大显示区域版
            im = self.ax_pressure.imshow(
                smoothed_data, 
                cmap=enhanced_colormap,
                aspect='equal',
                origin='upper',
                vmin=self.y_lim[0],
                vmax=self.y_lim[1],
                interpolation='gaussian' if self.enable_anti_aliasing else 'nearest'
            )
            
            # 🎨 添加等高线 - 2D模式不需要等高线
            # if self.enable_3d_shadows:
            #     contour = self.ax_pressure.contour(
            #         smoothed_data,
            #         levels=8,
            #         colors='white',
            #         alpha=0.3,
            #         linewidths=0.5
            #     )
            
            # 设置标签和标题
            self.ax_pressure.set_title("压力分布 (2D 2:3比例布局)", fontsize=12, fontweight='bold', color='white')
            # 🎨 去除轴标签，因为已经去除了坐标轴
            # self.ax_pressure.set_xlabel("X", color='white')
            # self.ax_pressure.set_ylabel("Y", color='white')
            
            # 🎨 添加颜色条 - 扩大版
            if hasattr(self, 'pressure_colorbar') and self.pressure_colorbar is not None:
                try:
                    self.pressure_colorbar.remove()
                except:
                    pass
            
            self.pressure_colorbar = self.fig.colorbar(
                im, 
                ax=self.ax_pressure,
                shrink=0.9,  # 增加颜色条大小
                aspect=25,   # 调整颜色条比例
                pad=0.15     # 增加颜色条间距
            )
            self.pressure_colorbar.set_label('压力值', rotation=270, labelpad=20, color='white', fontsize=10)
            self.pressure_colorbar.ax.tick_params(colors='white', labelsize=9)
            
            # 🎨 设置2D样式 - 去除坐标轴
            self.setup_2d_style()
            
            print("🎨 2D热力图渲染完成 (2:3比例布局)")
            
        except Exception as e:
            print(f"❌ 2D热力图渲染失败: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_2d_smoothing(self, data):
        """应用2D平滑处理"""
        try:
            from scipy.ndimage import gaussian_filter
            # 应用高斯平滑
            smoothed = gaussian_filter(data, sigma=1.2)
            
            # 应用边缘保持滤波
            try:
                from scipy.ndimage import uniform_filter
                edge_preserved = uniform_filter(smoothed, size=2)
                return edge_preserved
            except:
                return smoothed
        except ImportError:
            # 如果没有scipy，使用简单的均值滤波
            from scipy.ndimage import uniform_filter
            return uniform_filter(data, size=3)
    
    def setup_2d_style(self):
        """设置2D样式 - 去除坐标轴"""
        # 设置背景色
        self.ax_pressure.set_facecolor('black')
        
        # 🎨 去除所有坐标轴
        self.ax_pressure.set_xticks([])
        self.ax_pressure.set_yticks([])
        
        # 🎨 去除刻度标签
        self.ax_pressure.set_xticklabels([])
        self.ax_pressure.set_yticklabels([])
        
        # 🎨 去除轴线
        for spine in self.ax_pressure.spines.values():
            spine.set_visible(False)
        
        # 🎨 去除网格
        self.ax_pressure.grid(False)
    
    def set_3d_rendering_options(self, options):
        """设置3D渲染选项"""
        if 'enable_3d_lighting' in options:
            self.enable_3d_lighting = options['enable_3d_lighting']
        if 'enable_3d_shadows' in options:
            self.enable_3d_shadows = options['enable_3d_shadows']
        if 'enable_3d_animation' in options:
            self.enable_3d_animation = options['enable_3d_animation']
        if 'elevation_3d' in options:
            self.elevation_3d = options['elevation_3d']
        if 'azimuth_3d' in options:
            self.azimuth_3d = options['azimuth_3d']
        if 'rotation_speed_3d' in options:
            self.rotation_speed_3d = options['rotation_speed_3d']
        if 'surface_alpha_3d' in options:
            self.surface_alpha_3d = options['surface_alpha_3d']
        if 'enable_wireframe' in options:
            self.enable_wireframe = options['enable_wireframe']
        if 'enable_anti_aliasing' in options:
            self.enable_anti_aliasing = options['enable_anti_aliasing']
        if 'enable_bloom_effect' in options:
            self.enable_bloom_effect = options['enable_bloom_effect']
        
        print(f"🎨 3D渲染选项已更新: {list(options.keys())}")
    
    def get_3d_rendering_options(self):
        """获取当前3D渲染选项"""
        return {
            'enable_3d_lighting': self.enable_3d_lighting,
            'enable_3d_shadows': self.enable_3d_shadows,
            'enable_3d_animation': self.enable_3d_animation,
            'elevation_3d': self.elevation_3d,
            'azimuth_3d': self.azimuth_3d,
            'rotation_speed_3d': self.rotation_speed_3d,
            'surface_alpha_3d': self.surface_alpha_3d,
            'enable_wireframe': self.enable_wireframe,
            'enable_anti_aliasing': self.enable_anti_aliasing,
            'enable_bloom_effect': self.enable_bloom_effect
        }
    
    def setup_3d_style(self):
        """设置3D样式 - 原始版本（保留兼容性）"""
        # 设置背景色
        self.ax_pressure.set_facecolor('black')
        
        # 设置刻度颜色
        self.ax_pressure.tick_params(colors='white', labelsize=8)
        
        # 设置轴线颜色
        self.ax_pressure.xaxis.pane.fill = False
        self.ax_pressure.yaxis.pane.fill = False
        self.ax_pressure.zaxis.pane.fill = False
        
        # 设置轴线边缘颜色
        self.ax_pressure.xaxis.pane.set_edgecolor('white')
        self.ax_pressure.yaxis.pane.set_edgecolor('white')
        self.ax_pressure.zaxis.pane.set_edgecolor('white')
        
        # 设置网格
        self.ax_pressure.grid(True, alpha=0.3, color='gray')
        
        # 设置轴线标签颜色
        self.ax_pressure.xaxis.label.set_color('white')
        self.ax_pressure.yaxis.label.set_color('white')
        self.ax_pressure.zaxis.label.set_color('white')
        
        # 设置刻度标签颜色
        self.ax_pressure.xaxis.set_tick_params(labelcolor='white')
        self.ax_pressure.yaxis.set_tick_params(labelcolor='white')
        self.ax_pressure.zaxis.set_tick_params(labelcolor='white')

