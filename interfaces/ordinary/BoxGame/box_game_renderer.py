# -*- coding: utf-8 -*-
"""
推箱子游戏渲染器模块（PyQtGraph优化版）
Renderer Module for Box Push Game (PyQtGraph Optimized Version)

本模块负责游戏状态的可视化渲染，包括压力分布、游戏区域、COP点等。
现在使用PyQtGraph替代matplotlib，提供更好的性能和交互性。
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.opengl import GLViewWidget, GLSurfacePlotItem, GLGridItem, GLLinePlotItem
from pyqtgraph import GraphicsLayoutWidget, PlotWidget
import pyqtgraph.opengl as gl  # 添加别名导入
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QSizePolicy
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

# PyQtGraph 相关导入
import pyqtgraph as pg
from pyqtgraph.opengl import GLViewWidget, GLSurfacePlotItem, GLGridItem, GLLinePlotItem
from pyqtgraph import GraphicsLayoutWidget, PlotWidget

try:
    from .path_visualization_manager import PathVisualizationManager
except ImportError:
    from path_visualization_manager import PathVisualizationManager

# 🆕 导入帧级性能分析器
try:
    from .frame_performance_analyzer import (
        FramePerformanceAnalyzer, 
        start_frame_measurement, 
        end_frame_measurement, 
        stage_timer,
        get_global_analyzer
    )
    PERFORMANCE_ANALYZER_AVAILABLE = True
    print("✅ 帧级性能分析器已集成")
except ImportError as e:
    print(f"⚠️ 帧级性能分析器不可用: {e}")
    PERFORMANCE_ANALYZER_AVAILABLE = False

class BoxGameRenderer(QWidget):
    """推箱子游戏渲染器 - PyQtGraph优化版"""
    
    # 信号定义
    mouse_pressed = pyqtSignal(float, float)
    animation_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 🎮 游戏状态数据
        self.box_position = np.array([32.0, 32.0])  # 修改为游戏区域中心
        self.box_target_position = np.array([50.0, 50.0])  # 修改目标位置
        self.box_size = 3.2  # 增大4倍，从0.8改为3.2（虽然不影响渲染）
        self.current_cop = None
        self.initial_cop = None
        self.movement_distance = 0.0
        
        # 🎮 控制状态
        self.current_control_mode = 'idle'
        self.current_system_mode = 'touchpad_only'  # 默认触控板模式
        
        # 🗺️ 路径引导模式状态
        self.is_path_guide_mode = False  # 新增：路径引导模式标志
        
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
        
        # 🔄 渲染对象 - PyQtGraph版本
        self.game_plot_widget = None
        self.pressure_3d_widget = None
        self.pressure_2d_widget = None
        self.pressure_surface_item = None
        self.pressure_image_item = None
        
        # 📈 历史轨迹 - 删除轨迹相关代码
        # self.cop_history = deque(maxlen=50)  # 删除轨迹历史
        # self.angle_history = deque(maxlen=20)  # 删除角度历史
        # self.trajectory_lines = None  # 删除轨迹线条
        
        # ⚙️ 可视化参数 - 删除轨迹显示选项
        # self.show_trajectory = True  # 删除轨迹显示开关
        self.show_analysis_details = True
        self.show_pressure_overlay = True
        self.animation_speed = 0.1
        self.force_scale = 1.0
        
        # 🗺️ 路径可视化管理器 - 在setup_layout之后初始化
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
        self.log_y_lim = [0.0, 0.005]  # 固定为0-0.005范围
        self.minimum_y_lim = 0.0
        self.maximum_y_lim = 0.005  # 固定最大值为0.005
        
        # 🎨 高斯模糊参数
        self.gaussian_sigma = 1.0  # 高斯模糊的标准差
        
        # 🆕 3D显示参数 - 增强版
        self.show_3d_heatmap = True  # 默认显示3D
        self.heatmap_view_mode = '3d'  # '2d' 或 '3d'
        
        # 🔇 噪声过滤参数 - 新增
        self.noise_filter_threshold = 0.0005  # 默认噪声阈值
        self.noise_filter_sigma = 0.8  # 默认高斯模糊强度
        
        # 🎨 3D渲染增强参数
        self.enable_3d_lighting = True  # 启用3D光照
        self.enable_3d_shadows = True   # 启用3D阴影
        self.enable_3d_animation = False # 禁用3D动画旋转
        self.elevation_3d = 45          # 3D视角仰角 - 固定45度
        self.azimuth_3d = 315            # 3D视角方位角 - 修正为315度（-45度）
        self.rotation_speed_3d = 0.0    # 3D旋转速度 - 设为0禁用旋转
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
        
        # 🚀 性能优化相关变量
        self.performance_mode = "高性能"         # 当前性能模式
        self.pressure_data_changed = False     # 压力数据变化标志
        self.game_state_changed = False        # 游戏状态变化标志
        self.render_start_time = 0             # 渲染开始时间
        self.last_render_time = 0              # 上次渲染时间
        self.render_time_history = deque(maxlen=10)  # 渲染时间历史
        
        # 🎯 3D渲染缓存
        self._3d_surface = None                # 3D表面缓存
        self._pressure_data_changed = False    # 压力数据变化标志
        self._preprocessed_cache = None        # 预处理缓存
        
        # 🆕 性能分析器集成
        if PERFORMANCE_ANALYZER_AVAILABLE:
            self.performance_analyzer = get_global_analyzer()
            # 连接性能分析器信号
            self.performance_analyzer.performance_updated.connect(self.on_performance_updated)
            self.performance_analyzer.bottleneck_detected.connect(self.on_bottleneck_detected)
            self.performance_analyzer.performance_warning.connect(self.on_performance_warning)
            print("✅ 渲染器性能分析器已连接")
        else:
            self.performance_analyzer = None
            print("⚠️ 渲染器性能分析器不可用")
        
        # 🎨 设置布局
        self.setup_layout()
        
        # 🗺️ 初始化路径可视化管理器
        try:
            self.path_manager = PathVisualizationManager(self.game_plot_widget)
        except Exception as e:
            print(f"⚠️ 路径可视化管理器初始化失败: {e}")
            self.path_manager = None
        
        # 🖱️ 鼠标事件 - 在布局设置后立即设置
        self.setup_mouse_events()
        
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
        
        # 🎨 设置PyQtGraph样式
        self.setup_pyqtgraph_style()
        
        # 🔄 启动渲染循环
        self.start_rendering()
        
        # 🧪 添加测试压力数据以确保渲染器正常工作
        self.add_test_pressure_data()
        
        # 🔄 延迟强制刷新显示，确保PyQtGraph组件完全加载
        QTimer.singleShot(100, self.force_refresh_display)
        
        print("✅ BoxGameRenderer (PyQtGraph版) 初始化完成")
        
        # 🔧 设置y轴方向 - 确保y轴朝下
        self.force_set_y_axis_direction()
        
        # 🎨 设置3D显示选项 - 使用新的参数让3D区域更大
        self.set_3d_display_options(
            grid_scale=5.0,      # 进一步增大到50.0让3D区域更大
            camera_distance=200,    # 进一步减小到8让视角更近
            camera_elevation=25,  # 相机仰角
            camera_azimuth=45,    # 相机方位角
            enhancement_factor=3000  # 增强因子
        )
        
        # 🎨 设置2D热力图平滑参数
        self.set_2d_smoothing_options(gaussian_sigma=1.0)
        
        # 🎨 重置3D相机位置到最佳视角
        self.reset_3d_camera_position()
        
        # 🔄 强制刷新状态文本显示
        print("🔄 强制刷新状态文本显示")
        self.render_status_text()
    
    def force_refresh_display(self):
        """强制刷新显示"""
        try:
            print("🔄 强制刷新显示")
            
            # 检查视图状态
            print(f"🔍 当前视图状态:")
            print(f"  - 热力图模式: {self.heatmap_view_mode}")
            print(f"  - 3D视图可见: {self.pressure_3d_widget.isVisible()}")
            print(f"  - 2D视图可见: {self.pressure_2d_widget.isVisible()}")
            print(f"  - 压力数据: {self.pressure_data is not None}")
            if self.pressure_data is not None:
                print(f"  - 压力数据形状: {self.pressure_data.shape}")
                print(f"  - 压力数据范围: [{self.pressure_data.min():.6f}, {self.pressure_data.max():.6f}]")
            
            # 强制更新压力视图可见性
            self.update_pressure_view_visibility()
            
            # 🖱️ 重新设置鼠标事件，确保传感器连接后缩放功能正常
            self.setup_mouse_events()
            
            # 如果有压力数据，强制重新渲染
            if self.pressure_data is not None:
                print("🔄 强制重新渲染压力数据")
                self.pressure_data_changed = True
                self._pressure_data_changed = True
                # 立即更新一次
                self.update_pressure_only()
                
                # 强制刷新视图
                if self.heatmap_view_mode == '3d':
                    self.pressure_3d_widget.update()
                else:
                    self.pressure_2d_widget.update()
            
            # 强制更新游戏区域
            self.game_state_changed = True
            self.update_game_area_only()
            
            # 强制更新布局
            self.update()
            
            print("✅ 强制刷新显示完成")
            
        except Exception as e:
            print(f"⚠️ 强制刷新显示失败: {e}")
            import traceback
            traceback.print_exc()
    
    def add_test_pressure_data(self):
        """添加测试压力数据以确保渲染器正常工作"""
        try:
            # 创建一个64x64的测试压力数据
            test_data = np.zeros((64, 64))
            
            # 在中心区域添加一些压力
            center_x, center_y = 32, 32  # 改回32，因为数据是64x64
            for i in range(64):
                for j in range(64):
                    distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
                    if distance < 15:
                        test_data[i, j] = 0.003 * np.exp(-distance / 10)
            
            print("🧪 添加测试压力数据")
            print(f"🧪 测试数据范围: [{test_data.min():.6f}, {test_data.max():.6f}]")
            self.update_pressure_data(test_data)
            
            # 强制刷新显示
            QTimer.singleShot(200, self.force_refresh_display)
            
        except Exception as e:
            print(f"⚠️ 测试压力数据添加失败: {e}")
    
    # 🆕 性能分析器回调函数
    def on_performance_updated(self, performance_data):
        """处理性能数据更新"""
        if self.debug_level >= 2:
            print(f"📊 性能更新: 帧{performance_data['frame_id']}, "
                  f"FPS={performance_data['metrics']['current_fps']:.1f}, "
                  f"渲染={performance_data['timing']['rendering']*1000:.2f}ms")
    
    def on_bottleneck_detected(self, stage, time_value):
        """处理瓶颈检测"""
        print(f"⚠️ 性能瓶颈检测: {stage} 阶段耗时 {time_value*1000:.2f}ms")
    
    def on_performance_warning(self, stage, time_value):
        """处理性能警告"""
        print(f"🚨 性能警告: {stage} 阶段耗时 {time_value*1000:.2f}ms 超过阈值")
    
    def keyPressEvent(self, event):
        """键盘事件处理 - 集成F11全屏切换和热力图模式切换"""
        if UTILS_AVAILABLE:
            # 检查是否是F11键
            if event.key() == Qt.Key_F11 and not event.isAutoRepeat():
                self.toggle_fullscreen()
            # 检查是否是H键（切换热力图模式）
            elif event.key() == Qt.Key_H and not event.isAutoRepeat():
                print("🎨 用户按下H键，切换热力图模式")
                self.toggle_heatmap_mode()
            # 检查是否是R键（重置视图）
            elif event.key() == Qt.Key_R and not event.isAutoRepeat():
                print("🔄 用户按下R键，重置视图")
                self.reset_view()
            else:
                # 确保事件正确传递
                super().keyPressEvent(event)
        else:
            # 检查是否是H键（切换热力图模式）
            if event.key() == Qt.Key_H and not event.isAutoRepeat():
                print("🎨 用户按下H键，切换热力图模式")
                self.toggle_heatmap_mode()
            # 检查是否是R键（重置视图）
            elif event.key() == Qt.Key_R and not event.isAutoRepeat():
                print("🔄 用户按下R键，重置视图")
                self.reset_view()
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
    
    def setup_layout(self):
        """设置PyQtGraph布局"""
        # 创建主布局
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # 🔥 主游戏区域 - 使用PyQtGraph PlotWidget
        game_layout = QVBoxLayout()
        game_label = QLabel("推箱子游戏 - 实时传感器")
        game_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        game_layout.addWidget(game_label)
        
        self.game_plot_widget = pg.PlotWidget()
        self.game_plot_widget.setBackground('k')
        self.game_plot_widget.setAspectLocked(True)
        # 参考test_y_axis.py的方式设置y轴
        self.game_plot_widget.invertY(True)  # Y轴朝下
        self.game_plot_widget.setXRange(0, 63, padding=0)
        self.game_plot_widget.setYRange(0, 63, padding=0)  # 范围改为0-63，无padding
        self.game_plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        game_layout.addWidget(self.game_plot_widget)
        
        main_layout.addLayout(game_layout, 2)  # 游戏区域占2/5
        
        # 📊 压力分布区域
        pressure_layout = QVBoxLayout()
        pressure_label = QLabel("压力分布")
        pressure_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        pressure_layout.addWidget(pressure_label)
        
        # 创建压力视图容器 - 用于切换2D/3D视图
        self.pressure_container = QWidget()
        self.pressure_container_layout = QVBoxLayout()
        self.pressure_container.setLayout(self.pressure_container_layout)
        
        # 3D压力视图
        self.pressure_3d_widget = GLViewWidget()
        self.pressure_3d_widget.setBackgroundColor('k')  # 改为黑色背景
        self.pressure_3d_widget.setMinimumSize(600, 450)  # 增大最小尺寸
        self.pressure_3d_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许扩展
        # 调整相机位置以显示完整的64x64数据区域 - 使用更近的距离
        self.pressure_3d_widget.setCameraPosition(distance=8, elevation=25, azimuth=45)
        # 确保3D视图嵌入在主界面中，不弹出独立窗口
        self.pressure_3d_widget.setParent(self.pressure_container)
        self.pressure_3d_widget.setWindowFlags(Qt.Widget)  # 确保不是独立窗口
        print("🎨 3D压力视图已创建")
        
        # 2D压力视图
        self.pressure_2d_widget = pg.PlotWidget()
        self.pressure_2d_widget.setBackground('k')
        self.pressure_2d_widget.setMinimumSize(600, 450)  # 增大最小尺寸
        self.pressure_2d_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许扩展
        self.pressure_2d_widget.setAspectLocked(True)
        # 参考test_y_axis.py的方式设置y轴
        self.pressure_2d_widget.invertY(True)  # Y轴朝下
        self.pressure_2d_widget.setXRange(0, 63, padding=0)
        self.pressure_2d_widget.setYRange(0, 63, padding=0)  # 范围改为0-63，无padding
        # 确保2D视图嵌入在主界面中
        self.pressure_2d_widget.setParent(self.pressure_container)
        
        print("🎨 2D压力视图已创建")
        
        # 将容器添加到压力布局
        pressure_layout.addWidget(self.pressure_container,1)
        
        # 根据初始模式设置可见性 - 默认使用3D模式
        self.heatmap_view_mode = '3d'  # 强制使用3D模式
        self.update_pressure_view_visibility()
        
        # 🧪 强制刷新压力视图
        self.force_refresh_pressure_view()
        
        main_layout.addLayout(pressure_layout, 3)  # 压力分布占3/5
        
        # 设置样式
        self.setup_pyqtgraph_style()
        
        print("✅ PyQtGraph布局设置完成")
        print(f"🎨 初始热力图模式: {self.heatmap_view_mode}")
        print(f"🎨 3D视图可见: {self.pressure_3d_widget.isVisible()}")
        print(f"🎨 2D视图可见: {self.pressure_2d_widget.isVisible()}")
        
        # 🔧 强制设置y轴方向 - 确保y轴值越往上越小
        self.force_set_y_axis_direction()
    
    def force_set_y_axis_direction(self):
        """强制设置y轴方向 - 确保y轴朝下，范围0-63"""
        try:
            print("🔧 强制设置y轴方向")
            
            # 设置游戏区域y轴方向 - 参考test_y_axis.py的方式
            self.game_plot_widget.invertY(True)  # Y轴朝下
            self.game_plot_widget.setXRange(0, 63, padding=0)
            self.game_plot_widget.setYRange(0, 63, padding=0)  # 范围改为0-63，无padding
            
            # 🔧 强制锁定游戏区域的Y轴范围，防止被其他代码修改
            self.game_plot_widget.getViewBox().setLimits(yMin=0, yMax=63)
            self.game_plot_widget.getViewBox().setYRange(0, 63, padding=0)
            
            print(f"🔧 游戏区域y轴设置: {self.game_plot_widget.getViewBox().viewRange()}")
            
            # 设置2D压力视图y轴方向 - 确保与游戏区域一致
            self.pressure_2d_widget.invertY(True)  # Y轴朝下，与游戏区域一致
            self.pressure_2d_widget.setXRange(0, 63, padding=0)
            self.pressure_2d_widget.setYRange(0, 63, padding=0)
            # 🔧 强制锁定2D压力视图的Y轴范围，防止被其他代码修改
            self.pressure_2d_widget.getViewBox().setLimits(yMin=0, yMax=63)
            self.pressure_2d_widget.getViewBox().setYRange(0, 63, padding=0)
            
            print(f"🔧 2D压力视图y轴设置: {self.pressure_2d_widget.getViewBox().viewRange()}")
        except Exception as e:
            print(f"❌ 强制设置y轴方向失败: {e}")
    
    def force_refresh_pressure_view(self):
        """强制刷新压力视图"""
        try:
            print("🔄 强制刷新压力视图")
            
            # 确保视图可见
            if self.heatmap_view_mode == '3d':
                self.pressure_3d_widget.setVisible(True)
                self.pressure_2d_widget.setVisible(False)
            else:
                self.pressure_3d_widget.setVisible(False)
                self.pressure_2d_widget.setVisible(True)
            
            # 强制设置y轴方向
            self.force_set_y_axis_direction()
            
            # 强制更新布局
            self.pressure_container.update()
            
            # 如果有压力数据，强制重新渲染
            if self.pressure_data is not None:
                print("🔄 强制重新渲染压力数据")
                self.pressure_data_changed = True
                self._pressure_data_changed = True
                # 立即更新一次
                self.update_pressure_only()
            
            print("✅ 压力视图强制刷新完成")
            
        except Exception as e:
            print(f"⚠️ 强制刷新压力视图失败: {e}")
    
    def update_pressure_view_visibility(self):
        """更新压力视图的可见性"""
        print(f"🔍 更新压力视图可见性: 当前模式={self.heatmap_view_mode}")
        
        # 清除容器中的所有视图
        while self.pressure_container_layout.count():
            child = self.pressure_container_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # 根据模式添加相应的视图到同一个位置
        if self.heatmap_view_mode == '3d':
            print("🎨 切换到3D视图")
            # 确保3D视图正确嵌入
            self.pressure_3d_widget.setParent(self.pressure_container)
            self.pressure_3d_widget.setVisible(True)
            self.pressure_2d_widget.setVisible(False)
            self.pressure_container_layout.addWidget(self.pressure_3d_widget)
            
            # 强制设置3D视图大小和属性
            self.pressure_3d_widget.setMinimumSize(400, 300)
            self.pressure_3d_widget.resize(400, 300)
            self.pressure_3d_widget.setWindowFlags(Qt.Widget)  # 确保不是独立窗口
        else:
            print("🎨 切换到2D视图")
            # 确保2D视图正确嵌入
            self.pressure_2d_widget.setParent(self.pressure_container)
            self.pressure_3d_widget.setVisible(False)
            self.pressure_2d_widget.setVisible(True)
            self.pressure_container_layout.addWidget(self.pressure_2d_widget)
            
            # 强制设置2D视图大小
            self.pressure_2d_widget.setMinimumSize(400, 300)
            self.pressure_2d_widget.resize(400, 300)
        
        print(f"🎨 3D视图可见: {self.pressure_3d_widget.isVisible()}")
        print(f"🎨 2D视图可见: {self.pressure_2d_widget.isVisible()}")
        
        # 强制重新渲染压力分布
        if self.pressure_data is not None:
            print("🔄 强制重新渲染压力分布")
            self.pressure_data_changed = True
            self._pressure_data_changed = True
            
            # 立即更新一次
            self.update_pressure_only()
        
        # 强制更新布局
        self.pressure_container.update()
        self.update()
    
    def setup_pyqtgraph_style(self):
        """设置PyQtGraph样式"""
        # 设置PyQtGraph全局样式
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', 'w')
        
        # 设置游戏区域样式
        if self.game_plot_widget:
            self.game_plot_widget.setBackground('k')
            self.game_plot_widget.getAxis('left').setTextPen('w')
            self.game_plot_widget.getAxis('bottom').setTextPen('w')
            self.game_plot_widget.getAxis('left').setPen('w')
            self.game_plot_widget.getAxis('bottom').setPen('w')
        
        # 设置2D压力区域样式
        if self.pressure_2d_widget:
            self.pressure_2d_widget.setBackground('k')
            self.pressure_2d_widget.getAxis('left').setTextPen('w')
            self.pressure_2d_widget.getAxis('bottom').setTextPen('w')
            self.pressure_2d_widget.getAxis('left').setPen('w')
            self.pressure_2d_widget.getAxis('bottom').setPen('w')
    
    def setup_mouse_events(self):
        """设置鼠标事件 - 2D视图支持交互，3D视图在首次创建时设置"""
        if self.game_plot_widget:
            # 启用2D游戏区域的鼠标交互
            view_box = self.game_plot_widget.getViewBox()
            view_box.setMouseEnabled(x=True, y=True)
            view_box.setMouseMode(view_box.RectMode)  # 启用矩形选择模式，支持拖拽缩放
            # 连接鼠标点击事件
            self.game_plot_widget.scene().sigMouseClicked.connect(self.on_mouse_press)
            print("✅ 游戏区域鼠标事件已设置: 支持拖拽缩放")
        
        # 为2D压力视图也启用鼠标交互
        if self.pressure_2d_widget:
            view_box = self.pressure_2d_widget.getViewBox()
            view_box.setMouseEnabled(x=True, y=True)
            view_box.setMouseMode(view_box.RectMode)  # 启用矩形选择模式，支持拖拽缩放
            print("✅ 2D压力视图鼠标事件已设置: 支持拖拽缩放")
    
    def ensure_mouse_interaction_enabled(self):
        """确保鼠标交互设置不被覆盖 - 2D视图保持交互，3D视图保持稳定"""
        try:
            # 检查并确保游戏区域的鼠标交互保持启用
            if self.game_plot_widget:
                view_box = self.game_plot_widget.getViewBox()
                if not view_box.mouseEnabled()[0] or not view_box.mouseEnabled()[1]:
                    print("🖱️ 重新启用游戏区域鼠标交互")
                    view_box.setMouseEnabled(x=True, y=True)
                    view_box.setMouseMode(view_box.RectMode)
            
            # 检查并确保2D压力视图的鼠标交互保持启用
            if self.pressure_2d_widget:
                view_box = self.pressure_2d_widget.getViewBox()
                if not view_box.mouseEnabled()[0] or not view_box.mouseEnabled()[1]:
                    print("🖱️ 重新启用2D压力视图鼠标交互")
                    view_box.setMouseEnabled(x=True, y=True)
                    view_box.setMouseMode(view_box.RectMode)
                    
        except Exception as e:
            print(f"⚠️ 确保鼠标交互启用失败: {e}")
    
    def on_mouse_press(self, event):
        """处理鼠标点击事件"""
        if event.button() == 1:  # 左键点击
            pos = self.game_plot_widget.getViewBox().mapSceneToView(event.scenePos())
            self.mouse_pressed.emit(pos.x(), pos.y())
    
    def on_view_range_changed(self, view_box, ranges):
        """处理游戏区域视图范围变化"""
        try:
            x_range, y_range = ranges
            print(f"🎮 游戏区域视图范围变化: X=[{x_range[0]:.1f}-{x_range[1]:.1f}], Y=[{y_range[0]:.1f}-{y_range[1]:.1f}]")
        except Exception as e:
            print(f"⚠️ 处理游戏区域视图范围变化失败: {e}")
    
    def on_pressure_view_range_changed(self, view_box, ranges):
        """处理压力视图范围变化"""
        try:
            x_range, y_range = ranges
            print(f"📊 压力视图范围变化: X=[{x_range[0]:.1f}-{x_range[1]:.1f}], Y=[{y_range[0]:.1f}-{y_range[1]:.1f}]")
        except Exception as e:
            print(f"⚠️ 处理压力视图范围变化失败: {e}")
    
    def on_mouse_wheel(self, event):
        """处理游戏区域的鼠标滚轮事件"""
        # 获取滚轮增量
        delta = event.delta()
        if delta == 0:
            return
        
        # 获取当前视图范围
        view_box = self.game_plot_widget.getViewBox()
        current_range = view_box.viewRange()
        
        # 计算缩放因子
        zoom_factor = 0.1 if delta > 0 else -0.1
        
        # 计算新的视图范围
        x_range = current_range[0]
        y_range = current_range[1]
        
        # 计算中心点
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        
        # 计算新的范围
        x_span = x_range[1] - x_range[0]
        y_span = y_range[1] - y_range[0]
        
        new_x_span = x_span * (1 + zoom_factor)
        new_y_span = y_span * (1 + zoom_factor)
        
        # 限制最小和最大范围
        new_x_span = max(5, min(new_x_span, 100))  # 最小5个单位，最大100个单位
        new_y_span = max(5, min(new_y_span, 100))
        
        # 设置新的视图范围
        new_x_range = [x_center - new_x_span/2, x_center + new_x_span/2]
        new_y_range = [y_center - new_y_span/2, y_center + new_y_span/2]
        
        # 确保范围在有效区域内
        new_x_range[0] = max(-10, new_x_range[0])
        new_x_range[1] = min(73, new_x_range[1])
        new_y_range[0] = max(-10, new_y_range[0])
        new_y_range[1] = min(73, new_y_range[1])
        
        # 应用新的视图范围
        view_box.setRange(xRange=new_x_range, yRange=new_y_range)
        
        print(f"🎮 游戏区域缩放: 范围=[{new_x_range[0]:.1f}-{new_x_range[1]:.1f}, {new_y_range[0]:.1f}-{new_y_range[1]:.1f}]")
    
    def on_pressure_mouse_wheel(self, event):
        """处理压力视图的鼠标滚轮事件"""
        # 获取滚轮增量
        delta = event.delta()
        if delta == 0:
            return
        
        # 获取当前视图范围
        view_box = self.pressure_2d_widget.getViewBox()
        current_range = view_box.viewRange()
        
        # 计算缩放因子
        zoom_factor = 0.1 if delta > 0 else -0.1
        
        # 计算新的视图范围
        x_range = current_range[0]
        y_range = current_range[1]
        
        # 计算中心点
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        
        # 计算新的范围
        x_span = x_range[1] - x_range[0]
        y_span = y_range[1] - y_range[0]
        
        new_x_span = x_span * (1 + zoom_factor)
        new_y_span = y_span * (1 + zoom_factor)
        
        # 限制最小和最大范围
        new_x_span = max(10, min(new_x_span, 100))  # 最小10个单位，最大100个单位
        new_y_span = max(10, min(new_y_span, 100))
        
        # 设置新的视图范围
        new_x_range = [x_center - new_x_span/2, x_center + new_x_span/2]
        new_y_range = [y_center - new_y_span/2, y_center + new_y_span/2]
        
        # 确保范围在有效区域内
        new_x_range[0] = max(-10, new_x_range[0])
        new_x_range[1] = min(73, new_x_range[1])
        new_y_range[0] = max(-10, new_y_range[0])
        new_y_range[1] = min(73, new_y_range[1])
        
        # 应用新的视图范围
        view_box.setRange(xRange=new_x_range, yRange=new_y_range)
        
        print(f"📊 压力视图缩放: 范围=[{new_x_range[0]:.1f}-{new_x_range[1]:.1f}, {new_y_range[0]:.1f}-{new_y_range[1]:.1f}]")
    
    def update_interface_layout(self, system_mode):
        """根据系统模式更新界面布局 - PyQtGraph版本"""
        # PyQtGraph布局相对简单，主要调整大小比例
        layout = self.layout()
        if layout:
            # 调整游戏区域和压力区域的比例
            layout.setStretch(0, 2)  # 游戏区域
            layout.setStretch(1, 3)  # 压力区域
        
        print(f"🎨 界面布局已更新为PyQtGraph版本")
    
    def update_game_state(self, state_info: Dict):
        """更新游戏状态"""
        print(f"🎮 收到游戏状态更新: {state_info}")
        
        # 🆕 开始游戏状态更新阶段测量
        if PERFORMANCE_ANALYZER_AVAILABLE:
            self.performance_analyzer.start_stage('game_update')
        
        # 更新基本状态
        if 'box_position' in state_info:
            old_position = self.box_position.copy()
            self.box_position = np.array(state_info['box_position'])
            print(f"📦 箱子位置更新: {old_position} → {self.box_position}")
        if 'box_target_position' in state_info:
            old_target = self.box_target_position.copy()
            self.box_target_position = np.array(state_info['box_target_position'])
            print(f"🎯 目标位置更新: {old_target} → {self.box_target_position}")
        if 'current_cop' in state_info:
            self.current_cop = state_info['current_cop']
        if 'initial_cop' in state_info:
            self.initial_cop = state_info['initial_cop']
        if 'movement_distance' in state_info:
            self.movement_distance = state_info['movement_distance']
        if 'is_contact' in state_info:
            self.is_contact = state_info['is_contact']
        if 'is_tangential' in state_info:
            self.is_tangential = state_info['is_tangential']
        if 'is_sliding' in state_info:
            self.is_sliding = state_info['is_sliding']
        if 'consensus_angle' in state_info:
            self.consensus_angle = state_info['consensus_angle']
        if 'consensus_confidence' in state_info:
            self.consensus_confidence = state_info['consensus_confidence']
        if 'control_mode' in state_info:
            self.current_control_mode = state_info['control_mode']
        if 'current_system_mode' in state_info:
            self.current_system_mode = state_info['current_system_mode']
        
        # 🚀 设置游戏状态变化标志
        self.game_state_changed = True
        
        # 检查目标达成
        self.check_target_reached()
        
        # 🖱️ 确保鼠标交互设置不被覆盖
        self.ensure_mouse_interaction_enabled()
        
        # 🆕 结束游戏状态更新阶段测量
        if PERFORMANCE_ANALYZER_AVAILABLE:
            self.performance_analyzer.end_stage('game_update')
    
    def update_pressure_data(self, pressure_data: np.ndarray):
        """更新压力数据并计算COP点"""
        # 🆕 开始压力数据更新阶段测量
        if PERFORMANCE_ANALYZER_AVAILABLE:
            self.performance_analyzer.start_stage('pressure_update')
        
        if pressure_data is not None:
            print(f"📊 收到压力数据: 形状={pressure_data.shape}, 范围=[{pressure_data.min():.6f}, {pressure_data.max():.6f}]")
            self.pressure_data = pressure_data.copy()
            self.pressure_data_changed = True  # 🚀 设置变化标志
            self._pressure_data_changed = True  # 🎯 设置3D缓存变化标志
            
            # 🎯 计算COP点（压力中心）
            self.calculate_cop_from_pressure_data(pressure_data)
            
            print(f"✅ 压力数据已更新，COP点已计算")
            
            # 🖱️ 确保鼠标交互设置不被覆盖
            self.ensure_mouse_interaction_enabled()
        else:
            print("⚠️ 收到空的压力数据")
        
        # 🆕 结束压力数据更新阶段测量
        if PERFORMANCE_ANALYZER_AVAILABLE:
            self.performance_analyzer.end_stage('pressure_update')
    
    def calculate_cop_from_pressure_data(self, pressure_data: np.ndarray):
        """从压力数据计算COP点（压力中心）"""
        try:
            if pressure_data is None or pressure_data.size == 0:
                return
            
            # 找到压力数据的最大值位置
            max_pressure = np.max(pressure_data)
            if max_pressure <= 0:
                return
            
            # 找到最大压力值的坐标
            max_indices = np.where(pressure_data == max_pressure)
            if len(max_indices[0]) == 0:
                return
            
            # 取第一个最大值位置作为COP点
            cop_y = max_indices[0][0]  # 行索引（Y坐标）
            cop_x = max_indices[1][0]  # 列索引（X坐标）
            
            # 更新当前COP点
            self.current_cop = [cop_x, cop_y]
            
            # 如果是第一次计算，设置为初始COP点
            if self.initial_cop is None:
                self.initial_cop = [cop_x, cop_y]
            
            # 设置游戏状态变化标志
            self.game_state_changed = True
            
            print(f"🎯 COP点已计算: ({cop_x:.1f}, {cop_y:.1f})")
            
        except Exception as e:
            print(f"❌ COP点计算失败: {e}")
            import traceback
            traceback.print_exc()
    
    def update_consensus_angle(self, angle: float, confidence: float):
        """更新共识角度"""
        self.consensus_angle = angle
        self.consensus_confidence = confidence
        self.game_state_changed = True  # 🚀 设置变化标志
    
    def update_analysis_results(self, analysis_results: Dict):
        """更新分析结果"""
        self.analysis_results = analysis_results
        self.game_state_changed = True  # 🚀 设置变化标志
    
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
    
    def set_path_guide_mode(self, enabled: bool):
        """设置路径引导模式状态"""
        self.is_path_guide_mode = enabled
        if enabled:
            print("🗺️ 渲染器：路径引导模式已启用，将优化渲染性能")
            # 路径引导模式下强制使用2D模式
            if self.heatmap_view_mode == '3d':
                print("🎨 路径引导模式：自动切换到2D热力图")
                self.heatmap_view_mode = '2d'
        else:
            print("🗺️ 渲染器：路径引导模式已禁用")
    
    def is_in_path_guide_mode(self) -> bool:
        """检查是否处于路径引导模式"""
        return self.is_path_guide_mode
    
    def update_display(self):
        """更新显示内容 - PyQtGraph优化版"""
        # 🆕 开始帧测量
        if PERFORMANCE_ANALYZER_AVAILABLE:
            start_frame_measurement()
        
        try:
            # 🚀 记录渲染开始时间
            self.render_start_time = time.time()
            
            # 🔍 每30帧检查一次y轴设置
            if hasattr(self, '_debug_frame_count') and self._debug_frame_count % 30 == 0:
                self.check_y_axis_settings()
            
            # 🆕 开始显示更新阶段测量
            if PERFORMANCE_ANALYZER_AVAILABLE:
                self.performance_analyzer.start_stage('display_update')
            
            # 🔍 强制调试输出
            if hasattr(self, '_debug_frame_count'):
                self._debug_frame_count += 1
            else:
                self._debug_frame_count = 1
            
            # 每30帧输出一次调试信息
            if self._debug_frame_count % 30 == 0:
                print(f"🔍 渲染帧 {self._debug_frame_count}: 压力数据={self.pressure_data is not None}, "
                      f"压力变化={self.pressure_data_changed}, 游戏变化={self.game_state_changed}")
                if self.pressure_data is not None:
                    print(f"🔍 压力数据形状: {self.pressure_data.shape}, 范围: [{self.pressure_data.min():.6f}, {self.pressure_data.max():.6f}]")
            
            # 🎯 增量渲染：只在必要时更新
            if self.pressure_data_changed:
                print(f"🔄 检测到压力数据变化，开始更新压力分布")
                self.update_pressure_only()
                self.pressure_data_changed = False
            else:
                # 即使没有变化，也检查是否需要初始化渲染
                if self.pressure_data is not None and self.pressure_image_item is None and self.pressure_surface_item is None:
                    print(f"🔄 检测到压力数据但未初始化渲染，强制更新")
                    self.update_pressure_only()
            
            # 🔧 修复：确保游戏状态变化时游戏区域也会被更新
            if self.game_state_changed:
                print(f"🔄 检测到游戏状态变化，开始更新游戏区域")
                self.update_game_area_only()
                self.game_state_changed = False
            else:
                # 🔧 新增：即使没有游戏状态变化，也检查是否需要初始化游戏区域
                if not hasattr(self, '_box_item') or self._box_item is None:
                    print(f"🔄 检测到游戏区域未初始化，强制更新")
                    self.update_game_area_only()
            
            # 🔧 新增：强制初始化游戏区域（如果还没有初始化）
            if not hasattr(self, '_game_area_initialized') or not self._game_area_initialized:
                print(f"🔄 强制初始化游戏区域")
                self.update_game_area_only()
                self._game_area_initialized = True
            
            # 🔧 新增：调试信息
            if hasattr(self, '_debug_frame_count') and self._debug_frame_count % 60 == 0:
                print(f"🔍 调试信息: game_state_changed={self.game_state_changed}, "
                      f"has_box_item={hasattr(self, '_box_item')}, "
                      f"box_item={getattr(self, '_box_item', None)}, "
                      f"game_area_initialized={getattr(self, '_game_area_initialized', False)}")
            
            # 🔄 PyQtGraph自动更新，无需手动调用draw()
            
            # 🆕 结束显示更新阶段测量
            if PERFORMANCE_ANALYZER_AVAILABLE:
                self.performance_analyzer.end_stage('display_update')
            
            # 📊 更新帧率统计
            self.update_frame_rate_stats()
            
            # 🚀 性能监控
            self.monitor_render_performance()
            
            # 🆕 结束帧测量
            if PERFORMANCE_ANALYZER_AVAILABLE:
                end_frame_measurement()
            
        except Exception as e:
            print(f"⚠️ 渲染更新时出错: {e}")
            import traceback
            traceback.print_exc()
            
            # 🆕 确保在异常情况下也结束帧测量
            if PERFORMANCE_ANALYZER_AVAILABLE:
                end_frame_measurement()
    
    def update_pressure_only(self):
        """只更新压力分布图 - PyQtGraph版本"""
        # 🆕 开始渲染阶段测量
        if PERFORMANCE_ANALYZER_AVAILABLE:
            self.performance_analyzer.start_stage('rendering')
        
        if self.pressure_data is None:
            print("❌ 压力数据为空，跳过渲染")
            if PERFORMANCE_ANALYZER_AVAILABLE:
                self.performance_analyzer.end_stage('rendering')
            return
        
        try:
            print(f"🎨 开始更新压力分布，模式={self.heatmap_view_mode}")
            print(f"🎨 压力数据形状: {self.pressure_data.shape}")
            print(f"🎨 压力数据范围: [{self.pressure_data.min():.6f}, {self.pressure_data.max():.6f}]")
            
            # 预处理数据
            processed_data = self.preprocess_pressure_data_optimized(self.pressure_data)
            if processed_data is None:
                print("❌ 数据预处理失败")
                if PERFORMANCE_ANALYZER_AVAILABLE:
                    self.performance_analyzer.end_stage('rendering')
                return
            
            display_data = processed_data['data']
            print(f"🎨 预处理完成，显示数据形状={display_data.shape}, 范围=[{display_data.min():.6f}, {display_data.max():.6f}]")
            
            # 根据模式选择渲染方式
            if self.heatmap_view_mode == '3d':
                print("🎨 调用3D热力图渲染")
                self.render_3d_heatmap_optimized(display_data)
            else:
                print("🎨 调用2D热力图渲染")
                self.render_2d_heatmap_optimized(display_data)
            
            print("✅ 压力分布更新完成")
            
        except Exception as e:
            print(f"❌ 压力分布更新失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 🆕 结束渲染阶段测量
            if PERFORMANCE_ANALYZER_AVAILABLE:
                self.performance_analyzer.end_stage('rendering')
    
    def update_game_area_only(self):
        """只更新游戏区域 - PyQtGraph版本"""
        try:
            # 🧹 清除游戏区域
            self.game_plot_widget.clear()
            
            # 🗺️ 渲染路径可视化
            if PATH_PLANNING_AVAILABLE:
                print(f"🎨 路径引导模式状态: {self.is_path_guide_mode}")
                self.path_manager.render_complete_path_visualization(self.box_position)
            
            # 📦 渲染箱子
            self.render_box()
            
            # 🎯 渲染COP点
            self.render_cop_and_trajectory()
            
            # 🎆 更新和渲染烟花效果
            self.update_fireworks()
            self.render_fireworks()
            
            # 📊 渲染状态文本
            self.render_status_text()
            
        except Exception as e:
            print(f"❌ 游戏区域更新失败: {e}")
    
    def monitor_render_performance(self):
        """监控渲染性能"""
        render_time = time.time() - self.render_start_time
        self.render_time_history.append(render_time)
        
        # 计算平均渲染时间
        avg_render_time = np.mean(self.render_time_history)
        
        # 性能警告
        if render_time > 0.033:  # 超过33ms (30 FPS)
            print(f"⚠️ 渲染性能警告: {render_time*1000:.1f}ms")
        
        # 自适应性能调整
        if len(self.render_time_history) >= 5:
            if avg_render_time > 0.05:  # 平均超过50ms
                self.adaptive_performance_adjustment()
    
    def adaptive_performance_adjustment(self):
        """自适应性能调整 - 简化版"""
        # 简化为空函数，不再进行复杂的性能调整
        pass
    
    def set_performance_mode(self, mode):
        """设置性能模式 - 增加稳定性控制"""
        if mode in ["低性能", "标准", "高性能", "极限"]:
            # 记录之前的模式
            previous_mode = self.performance_mode
            
            # 更新模式
            self.performance_mode = mode
            
            # 如果模式发生变化，强制重新创建3D表面并提示用户
            if previous_mode != mode:
                self._pressure_data_changed = True
                print(f"🔄 性能模式已切换: {previous_mode} → {mode}")
                print(f"💡 提示：颜色和网格效果可能会发生变化")
                print(f"💡 建议：如需稳定效果，请在控制面板中手动选择性能模式")
            
            print(f"�� 渲染器性能模式已设置为: {mode}")
            self.update_frame_rate()
        else:
            print(f"❌ 无效的性能模式: {mode}")
    
    def filter_noise_3d(self, pressure_data, noise_threshold=0.0005, gaussian_sigma=0.8):
        """
        抑制3D热力图中的噪声
        
        Args:
            pressure_data: 原始压力数据
            noise_threshold: 噪声阈值，低于此值的数据将被抑制
            gaussian_sigma: 高斯模糊的sigma值，用于平滑数据
            
        Returns:
            过滤后的数据
        """
        try:
            if pressure_data is None:
                return None
                
            # 确保数据是numpy数组
            if not isinstance(pressure_data, np.ndarray):
                pressure_data = np.array(pressure_data)
            
            # 1. 应用高斯模糊平滑数据
            filtered_data = self.gaussian_blur(pressure_data, sigma=gaussian_sigma)
            
            # 2. 计算噪声基线（使用数据的最小值或百分位数）
            noise_baseline = np.percentile(filtered_data, 10)  # 使用10%分位数作为噪声基线
            
            # 3. 设置动态噪声阈值
            dynamic_threshold = max(noise_threshold, noise_baseline * 1.5)
            
            # 4. 抑制低于阈值的数据
            # 使用软阈值方法：低于阈值的数据逐渐衰减，而不是直接置零
            mask = filtered_data > dynamic_threshold
            filtered_data = np.where(
                mask,
                filtered_data - dynamic_threshold,  # 减去噪声基线
                filtered_data * 0.1  # 保留10%的低值，避免完全消失
            )
            
            # 5. 确保数据非负
            filtered_data = np.maximum(filtered_data, 0.0)
            
            # 6. 可选：应用额外的平滑处理
            if gaussian_sigma > 0:
                filtered_data = self.gaussian_blur(filtered_data, sigma=gaussian_sigma * 0.5)
            
            print(f"🔇 噪声过滤 - 原始范围: [{pressure_data.min():.6f}, {pressure_data.max():.6f}]")
            print(f"🔇 噪声过滤 - 过滤后范围: [{filtered_data.min():.6f}, {filtered_data.max():.6f}]")
            print(f"🔇 噪声过滤 - 使用阈值: {dynamic_threshold:.6f}")
            
            return filtered_data
            
        except Exception as e:
            print(f"❌ 噪声过滤失败: {e}")
            return pressure_data  # 失败时返回原始数据
    
    def set_noise_filter_options(self, noise_threshold=0.0005, gaussian_sigma=0.8):
        """设置噪声过滤参数"""
        self.noise_filter_threshold = noise_threshold
        self.noise_filter_sigma = gaussian_sigma
        print(f"🔇 噪声过滤参数已设置 - 阈值: {noise_threshold:.6f}, 高斯模糊: {gaussian_sigma}")
    
    def set_2d_smoothing_options(self, gaussian_sigma=1.0):
        """设置2D热力图平滑参数"""
        self.gaussian_sigma = gaussian_sigma
        print(f"🎨 2D热力图平滑参数已设置 - 高斯模糊sigma: {gaussian_sigma}")
        
        # 🔄 如果有当前压力数据，强制重新渲染2D热力图
        if self.pressure_data is not None and self.heatmap_view_mode == '2d':
            print("🔄 强制重新渲染2D热力图以应用新的平滑参数")
            self.pressure_data_changed = True
            self.update_pressure_only()
    
    def set_3d_display_options(self, grid_scale=50.0, camera_distance=8, camera_elevation=25, camera_azimuth=45, enhancement_factor=3000):
        """
        设置3D显示参数
        
        Args:
            grid_scale: 网格缩放比例 - 进一步增大到50.0让3D区域更大
            camera_distance: 相机距离 - 进一步减小到8让视角更近
            camera_elevation: 相机仰角
            camera_azimuth: 相机方位角
            enhancement_factor: 3D增强因子
        """
        self.grid_scale = grid_scale
        self.camera_distance = camera_distance
        self.camera_elevation = camera_elevation
        self.camera_azimuth = camera_azimuth
        self.enhancement_factor = enhancement_factor
        print(f"🎨 3D显示参数已设置:")
        print(f"   - 网格缩放: {grid_scale}")
        print(f"   - 相机距离: {camera_distance}")
        print(f"   - 相机仰角: {camera_elevation}")
        print(f"   - 相机方位角: {camera_azimuth}")
        print(f"   - 增强因子: {enhancement_factor}")
        
        # 🔄 强制重新创建3D表面以应用新参数
        if self.pressure_surface_item is not None:
            print("🔄 强制重新创建3D表面以应用新参数...")
            self.pressure_surface_item = None
            # 清除3D视图
            if self.pressure_3d_widget:
                self.pressure_3d_widget.clear()
            # 立即重置相机位置
            self.reset_3d_camera_position()
    
    def preprocess_pressure_data_optimized(self, pressure_data):
        """简化的数据预处理 - 直接返回原始数据"""
        if pressure_data is None:
            return None
        
        try:
            # 直接返回原始数据，不进行任何预处理
            result = {
                'data': pressure_data,
                'colormap': 'plasma'
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 数据预处理失败: {e}")
            return None
    
    def clear_all_plots(self):
        """清空所有子图 - PyQtGraph版本"""
        try:
            # 清空游戏区域
            self.game_plot_widget.clear()
            
            # 清空压力区域
            if self.heatmap_view_mode == '3d':
                self.pressure_3d_widget.clear()
            else:
                self.pressure_2d_widget.clear()
            
        except Exception as e:
            print(f"⚠️ 清除图形时出错: {e}")
    
    def setup_subplot_properties(self):
        """重新设置子图属性"""
        # 游戏区域
        self.game_plot_widget.setTitle("推箱子游戏 - 实时传感器", color='white', size='14pt')
        self.game_plot_widget.getAxis('bottom').setLabel('X', color='white')
        self.game_plot_widget.getAxis('left').setLabel('Y', color='white')
        self.game_plot_widget.getAxis('bottom').setTicks([[(i, str(i)) for i in range(64)]])
        self.game_plot_widget.getAxis('left').setTicks([[(i, str(i)) for i in range(64)]])
        
        # 压力分布图 - GLViewWidget没有getViewBox方法
        self.pressure_3d_widget.setTitle("压力分布 (3D)", color='white', size='12pt')
        # self.pressure_3d_widget.getViewBox().setCameraPosition(distance=200)  # GLViewWidget没有getViewBox方法
        # self.pressure_3d_widget.getViewBox().setBackgroundColor('black')  # GLViewWidget没有getViewBox方法
        # self.pressure_3d_widget.getViewBox().addItem(GLGridItem(size=np.array([64, 64])))  # GLViewWidget没有getViewBox方法
        
        # 压力分布图
        self.pressure_2d_widget.setTitle("压力分布 (2D 2:3比例布局)", color='white', size='12pt')
        self.pressure_2d_widget.getAxis('bottom').setLabel('X', color='white')
        self.pressure_2d_widget.getAxis('left').setLabel('Y', color='white')
        self.pressure_2d_widget.getAxis('bottom').setTicks([[(i, str(i)) for i in range(64)]])
        self.pressure_2d_widget.getAxis('left').setTicks([[(i, str(i)) for i in range(64)]])
        
        # 统一样式
        # self.pressure_3d_widget.getViewBox().setXRange(0, 63, padding=0)  # GLViewWidget没有getViewBox方法
        # self.pressure_3d_widget.getViewBox().setYRange(0, 63, padding=0)  # GLViewWidget没有getViewBox方法
        self.pressure_2d_widget.getAxis('bottom').setRange(0, 63)
        self.pressure_2d_widget.getAxis('left').setRange(0, 63)  # Y轴正常：0在顶部，63在底部
        
        # 设置PyQtGraph样式
        self.setup_pyqtgraph_style()
    
    def render_game_area(self):
        """渲染游戏区域 - PyQtGraph版本"""
        # 🗺️ 渲染路径可视化
        if PATH_PLANNING_AVAILABLE:
            print(f"🎨 路径引导模式状态: {self.is_path_guide_mode}")
            self.path_manager.render_complete_path_visualization(self.box_position)
        
        # 📦 确保箱子在路径可视化之后渲染
        self.render_box()
    
    def render_box(self):
        """渲染箱子 - PyQtGraph版本"""
        try:
            # 清除之前的箱子
            if hasattr(self, '_box_item'):
                try:
                    self.game_plot_widget.removeItem(self._box_item)
                except:
                    pass
            
            if hasattr(self, '_box_center_item'):
                try:
                    self.game_plot_widget.removeItem(self._box_center_item)
                except:
                    pass
            
            if hasattr(self, '_box_target_item'):
                try:
                    self.game_plot_widget.removeItem(self._box_target_item)
                except:
                    pass
            
            # 🎨 确定箱子颜色
            if self.is_sliding:
                box_color = (0, 255, 0)  # lime RGB
                edge_color = (0, 128, 0)  # green RGB
                alpha = 0.8
            elif self.is_tangential:
                box_color = (255, 165, 0)  # orange RGB
                edge_color = (255, 140, 0)  # darkorange RGB
                alpha = 0.7
            elif self.is_contact:
                box_color = (255, 255, 0)  # yellow RGB
                edge_color = (255, 215, 0)  # gold RGB
                alpha = 0.6
            else:
                box_color = (173, 216, 230)  # lightblue RGB
                edge_color = (0, 0, 255)     # blue RGB
                alpha = 0.5
            
            # 📦 绘制箱子 - 使用PyQtGraph的ScatterPlotItem
            box_size = 64.0  # 增大箱子尺寸4倍，从16.0改为64.0
            self._box_item = pg.ScatterPlotItem(
                x=[self.box_position[0]], 
                y=[self.box_position[1]],
                symbol='s',  # 正方形
                size=box_size,
                brush=box_color,
                pen=pg.mkPen(color=edge_color, width=2)
            )
            
            # 添加到游戏区域
            self.game_plot_widget.addItem(self._box_item)
            
            # 📦 箱子中心标记
            self._box_center_item = pg.ScatterPlotItem(
                x=[self.box_position[0]], 
                y=[self.box_position[1]],
                symbol='+',
                size=6,
                pen=pg.mkPen('k', width=2),
                brush=None
            )
            self.game_plot_widget.addItem(self._box_center_item)
            
            # 🎯 目标位置标记（如果不同于当前位置）
            if np.linalg.norm(self.box_target_position - self.box_position) > 1:
                self._box_target_item = pg.ScatterPlotItem(
                    x=[self.box_target_position[0]], 
                    y=[self.box_target_position[1]],
                    symbol='s',
                    size=box_size,
                    brush=None,
                    pen=pg.mkPen(color=(255, 0, 0), width=2, style=pg.QtCore.Qt.DashLine)  # red RGB
                )
                self.game_plot_widget.addItem(self._box_target_item)
                
                # 🏹 绘制移动方向箭头
                self.render_movement_direction_arrow()
            
            print(f"📦 箱子已渲染在位置: ({self.box_position[0]:.1f}, {self.box_position[1]:.1f})")
            print(f"📦 目标位置: ({self.box_target_position[0]:.1f}, {self.box_target_position[1]:.1f})")
            print(f"📦 游戏状态变化: {getattr(self, 'game_state_changed', False)}")
            
        except Exception as e:
            print(f"❌ 箱子渲染失败: {e}")
            import traceback
            traceback.print_exc()
    
    def render_cop_and_trajectory(self):
        """渲染压力中心 - 删除轨迹渲染功能"""
        # 🎯 绘制当前压力中心
        if self.current_cop is not None and self.current_cop[0] is not None and self.current_cop[1] is not None:
            cop_item = pg.ScatterPlotItem(
                x=[self.current_cop[0]], 
                y=[self.current_cop[1]],
                symbol='o',
                size=8,
                pen=pg.mkPen('darkred', width=2),
                brush=pg.mkBrush('red')
            )
            self.game_plot_widget.addItem(cop_item)
        
        # 🎯 绘制初始压力中心
        if self.initial_cop is not None and self.initial_cop[0] is not None and self.initial_cop[1] is not None:
            initial_cop_item = pg.ScatterPlotItem(
                x=[self.initial_cop[0]], 
                y=[self.initial_cop[1]],
                symbol='o',
                size=6,
                pen=pg.mkPen('darkgreen', width=1),
                brush=pg.mkBrush('green')
            )
            self.game_plot_widget.addItem(initial_cop_item)
        
        # 📈 绘制轨迹 - 删除轨迹渲染功能
        # if self.show_trajectory and len(self.cop_history) > 1:
        #     # 过滤掉包含None的轨迹点
        #     valid_trajectory = []
        #     for point in self.cop_history:
        #         if point is not None and len(point) >= 2 and point[0] is not None and point[1] is not None:
        #             valid_trajectory.append(point)
        #     
        #     if len(valid_trajectory) > 1:
        #         trajectory = np.array(valid_trajectory)
        #         
        #         # 🎨 添加轨迹平滑处理
        #         smoothed_trajectory = self.smooth_trajectory(trajectory)
        #         
        #         trajectory_item = pg.PlotDataItem(
        #             x=smoothed_trajectory[:, 0],
        #             y=smoothed_trajectory[:, 1],
        #             pen=pg.mkPen('blue', width=2, alpha=0.6)
        #         )
        #         self.game_plot_widget.addItem(trajectory_item)
    
    def render_movement_direction_arrow(self):
        """绘制从箱子到目标位置的移动方向箭头和角度 - PyQtGraph版本"""
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
            
            # 使用PyQtGraph的箭头
            arrow_item = pg.ArrowItem(
                pos=(arrow_end_x, arrow_end_y),
                angle=angle_deg,
                tipAngle=30,
                baseAngle=0,
                headLen=10,
                tailLen=0,
                pen=pg.mkPen('yellow', width=3),
                brush=pg.mkBrush('yellow')
            )
            self.game_plot_widget.addItem(arrow_item)
            
            # 显示距离和角度信息
            text_item = pg.TextItem(
                text=f"距离: {distance:.1f}\n角度: {angle_deg:.1f}°",
                color='yellow',
                anchor=(0, 0)
            )
            text_item.setPos(arrow_end_x + 2, arrow_end_y + 2)
            self.game_plot_widget.addItem(text_item)
    
    def render_fireworks(self):
        """渲染烟花粒子 - PyQtGraph版本"""
        for firework in self.fireworks:
            # 计算透明度（基于生命值）
            alpha = firework['lifetime'] / self.firework_lifetime
            
            # 绘制粒子
            particle_item = pg.ScatterPlotItem(
                x=[firework['x']], 
                y=[firework['y']],
                symbol='o',
                size=firework['size'],
                pen=pg.mkPen('white', width=1),
                brush=pg.mkBrush(firework['color'])
            )
            particle_item.setOpacity(alpha)
            self.game_plot_widget.addItem(particle_item)
    
    def render_status_text(self):
        """渲染状态文本 - PyQtGraph版本，在右上角显示控制模式"""
        # 🎮 显示控制模式
        control_mode_text = ""
        if hasattr(self, 'current_control_mode'):
            if self.current_control_mode == 'joystick':
                control_mode_text = "🕹️ 摇杆模式"
            elif self.current_control_mode == 'touchpad':
                control_mode_text = "🖱️ 触控板模式"
            elif self.current_control_mode == 'idle':
                control_mode_text = "⏸️ 空闲模式"
            else:
                control_mode_text = f"🎮 {self.current_control_mode}"
        
        # 在游戏区域右上角添加文本 - 修复TextItem参数
        if control_mode_text:
            print(f"🎨 渲染状态文本: {control_mode_text}")
            # 使用HTML格式来设置字体大小
            html_text = f'<div style="font-size: 19px; color: white;">{control_mode_text}</div>'
            control_text_item = pg.TextItem(
                html=html_text,
                anchor=(1, 0)  # 右对齐
            )
            # 使用更保守的位置
            control_text_item.setPos(58, 3)  # 右上角位置
            self.game_plot_widget.addItem(control_text_item)
            print(f"✅ 状态文本已添加到位置 (58, 5)")
        else:
            print(f"⚠️ 没有控制模式文本可显示")
    
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
                self.render_3d_heatmap_optimized(display_data)
            else:
                self.render_2d_heatmap_optimized(display_data)
            
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
        self.pressure_2d_widget.getPlotItem().addItem(pg.TextItem(text=detail_text, anchor=(1, 0), color='white', font={'size': '8pt'}))

    def reset_view(self):
        """重置所有视图到默认状态"""
        try:
            print("🔄 重置所有视图...")
            
            # 重置2D游戏区域视图
            if self.game_plot_widget:
                self.game_plot_widget.setXRange(0, 63, padding=0)
                self.game_plot_widget.setYRange(0, 63, padding=0)
                # 🔧 强制锁定游戏区域的Y轴范围，防止被其他代码修改
                self.game_plot_widget.getViewBox().setLimits(yMin=0, yMax=63)
                self.game_plot_widget.getViewBox().setYRange(0, 63, padding=0)
                # 🔧 确保Y轴方向正确
                self.game_plot_widget.invertY(True)
                print("✅ 游戏区域视图已重置")
            
            # 重置2D压力视图
            if self.pressure_2d_widget:
                self.pressure_2d_widget.setXRange(0, 63, padding=0)
                self.pressure_2d_widget.setYRange(0, 63, padding=0)
                # 🔧 强制锁定2D压力视图的Y轴范围，防止被其他代码修改
                self.pressure_2d_widget.getViewBox().setLimits(yMin=0, yMax=63)
                self.pressure_2d_widget.getViewBox().setYRange(0, 63, padding=0)
                # 🔧 确保Y轴方向正确，与游戏区域一致
                self.pressure_2d_widget.invertY(True)
                print("✅ 2D压力视图已重置")

            # 重置3D压力视图相机位置
            if self.pressure_3d_widget:
                self.reset_3d_camera_position()
                
        except Exception as e:
            print(f"⚠️ 重置视图失败: {e}")
    
    def reset_visualization(self):
        """重置可视化 - PyQtGraph版本"""
        # 清空历史数据 - 删除轨迹历史清除
        # if hasattr(self, 'cop_history') and len(self.cop_history) > 0:
        #     self.cop_history.clear()
        # if hasattr(self, 'angle_history') and len(self.angle_history) > 0:
        #     self.angle_history.clear()
        
        # 重置游戏状态
        self.current_cop = None
        self.initial_cop = None
        self.is_contact = False
        self.is_tangential = False
        self.is_sliding = False
        self.consensus_angle = None
        self.consensus_confidence = 0.0
        self.movement_distance = 0.0
        
        # 🔄 重置idle计数器
        self.idle_frame_count = 0
        
        # 🎆 清空烟花效果
        self.fireworks.clear()
        self.last_target_reached = False
        
        # 重置路径可视化
        if self.path_manager:
            self.path_manager.clear_path_visualization()
        
        # 🎨 重置3D视角到固定45度
        self.reset_3d_view_to_fixed_45()
        
        # 清空所有图形
        self.clear_all_plots()
        
        print("�� PyQtGraph可视化已重置")
    
    def set_visualization_options(self, options: Dict):
        """设置可视化选项"""
        try:
            # 🚀 处理性能模式设置
            if 'performance_mode' in options:
                self.set_performance_mode(options['performance_mode'])
            
            # 🆕 处理2D/3D热力图切换
            if 'toggle_heatmap_mode' in options:
                self.toggle_heatmap_mode()
                return
            
            # 处理其他可视化选项
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
            print(f"🎯 渲染器配置: 间隔={interval_ms}ms, 目标FPS={target_fps:.1f}")
        except ImportError:
            # 回退到默认配置
            target_fps = 30
            interval_ms = int(1000 / target_fps)
            print(f"⚠️ 使用默认配置: 间隔={interval_ms}ms, 目标FPS={target_fps:.1f}")
        
        # 🕐 记录启动时间
        self.render_start_time = time.time()
        self.frame_count = 0
        self.last_fps_time = self.render_start_time
        
        # 🚀 启动定时器
        self.update_timer.start(interval_ms)
        print(f"🚀 渲染循环已启动 (目标FPS: {target_fps:.1f})")
        
        # 🖱️ 启动鼠标交互保护定时器
        if not hasattr(self, 'mouse_protection_timer'):
            self.mouse_protection_timer = QTimer()
            self.mouse_protection_timer.timeout.connect(self.ensure_mouse_interaction_enabled)
        self.mouse_protection_timer.start(2000)  # 每2秒检查一次
        print("🖱️ 鼠标交互保护定时器已启动")
        
        # 🔍 检查定时器状态
        print(f"🔍 定时器状态: 活跃={self.update_timer.isActive()}, 间隔={self.update_timer.interval()}ms")
        
        # 🔧 强制设置y轴方向
        self.force_set_y_axis_direction()
        
        # 🎨 重置3D相机位置到最佳视角
        self.reset_3d_camera_position()
    
    def stop_rendering(self):
        """停止渲染循环"""
        self.update_timer.stop()
        
        # 🖱️ 停止鼠标交互保护定时器
        if hasattr(self, 'mouse_protection_timer'):
            self.mouse_protection_timer.stop()
            print("🖱️ 鼠标交互保护定时器已停止")
        
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
            'target_fps': 1000 / self.update_timer.interval(),
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
        """切换热力图显示模式（2D/3D）"""
        try:
            if self.heatmap_view_mode == '3d':
                self.heatmap_view_mode = '2d'
                print("🎨 切换到2D热力图模式")
            else:
                self.heatmap_view_mode = '3d'
                print("🎨 切换到3D热力图模式")
                # 强制重新创建3D表面以应用新的增强效果
                self.pressure_surface_item = None
                print("🔄 强制重新创建3D表面以应用增强效果")
            
            self.update_pressure_view_visibility()
            self.pressure_data_changed = True
            print(f"✅ 热力图模式已切换为: {self.heatmap_view_mode}")
            
        except Exception as e:
            print(f"⚠️ 切换热力图模式失败: {e}")
    
    def render_3d_heatmap_optimized(self, pressure_data):
        """优化的3D热力图渲染 - 修复了相机重置问题，增强3D效果"""
        try:
            if not self.pressure_3d_widget.isVisible():
                return

            # --- 🔴 关键修改: 逻辑分离 ---
            # 仅在 surface item 不存在时才创建它并设置相机
            if self.pressure_surface_item is None:
                print("🎨 首次创建3D表面...")
                self.pressure_3d_widget.clear()
                
                # 预处理压力数据 - 注意：pressure_data可能是字典格式
                if isinstance(pressure_data, dict):
                    processed_data = pressure_data['data']
                    print(f"🎨 使用预处理数据，形状: {processed_data.shape}")
                else:
                    processed_data = self.preprocess_pressure_data_optimized(pressure_data)
                    if processed_data is None:
                        print("❌ 数据预处理失败")
                        return
                    processed_data = processed_data['data']
                
                # 🔇 应用噪声过滤
                if hasattr(self, 'noise_filter_threshold') and hasattr(self, 'noise_filter_sigma'):
                    processed_data = self.filter_noise_3d(
                        processed_data, 
                        noise_threshold=self.noise_filter_threshold,
                        gaussian_sigma=self.noise_filter_sigma
                    )
                else:
                    # 使用默认参数进行噪声过滤
                    processed_data = self.filter_noise_3d(processed_data)
                
                # 🎨 增强3D效果：对数据进行缩放
                # 使用动态的最大压力值，基于实际数据范围
                actual_max = np.max(processed_data)
                max_pressure = max(actual_max, 0.001)  # 至少0.001，避免除零
                enhanced_data = np.clip(processed_data, 0.0, max_pressure)
                
                # 🎨 使用更强的非线性映射增强效果：创建明显的山峰
                # 使用指数映射让高值更突出，放大3000倍（从2000增加到3000）
                enhancement_factor = getattr(self, 'enhancement_factor', 3000)
                enhanced_data = np.power(enhanced_data / max_pressure, 0.15) * max_pressure * enhancement_factor
                
                print(f"🎨 原始数据范围: [{processed_data.min():.6f}, {processed_data.max():.6f}]")
                print(f"🎨 使用最大压力: {max_pressure:.6f}")
                print(f"🎨 增强后数据范围: [{enhanced_data.min():.6f}, {enhanced_data.max():.6f}]")
                
                # 创建颜色映射 - 使用更鲜艳的颜色映射
                color_map = pg.colormap.get('plasma')  # 使用plasma颜色映射
                colors = color_map.map(np.clip(processed_data, 0.0, max_pressure) / max_pressure, mode='float')
                
                # 创建3D表面
                self.pressure_surface_item = gl.GLSurfacePlotItem(
                    z=enhanced_data,  # 使用增强后的数据
                    colors=colors.reshape(processed_data.shape + (4,)),
                    shader='shaded',
                    smooth=True
                )
                self.pressure_3d_widget.addItem(self.pressure_surface_item)
                
                # 🎨 调整网格大小和位置 - 进一步增大3D显示区域
                grid = gl.GLGridItem()
                # 使用可配置的网格缩放 - 进一步增大到50.0让3D区域更大
                grid_scale = getattr(self, 'grid_scale', 50.0)
                grid.scale(grid_scale, grid_scale, 5)  # 进一步增大Z轴缩放到5
                # 调整网格位置，让3D区域更居中且更大
                grid.translate(31.5, 31.5, -2)  # 进一步向下移动网格
                self.pressure_3d_widget.addItem(grid)

                # 只在第一次创建时重置相机！
                self.reset_3d_camera_position()
                print("✅ 3D表面已创建，相机已设置。")

            # 在所有后续帧中，只更新数据，不碰相机
            else:
                # print("🎨 正在更新3D表面数据...") # 注释掉以避免刷屏
                
                # 处理数据格式
                if isinstance(pressure_data, dict):
                    processed_data = pressure_data['data']
                else:
                    processed_data = pressure_data
                
                # 🔇 应用噪声过滤
                if hasattr(self, 'noise_filter_threshold') and hasattr(self, 'noise_filter_sigma'):
                    processed_data = self.filter_noise_3d(
                        processed_data, 
                        noise_threshold=self.noise_filter_threshold,
                        gaussian_sigma=self.noise_filter_sigma
                    )
                else:
                    # 使用默认参数进行噪声过滤
                    processed_data = self.filter_noise_3d(processed_data)
                
                # 🎨 增强3D效果：对数据进行缩放 - 使用与初始创建完全相同的算法
                # 使用动态的最大压力值，基于实际数据范围
                actual_max = np.max(processed_data)
                max_pressure = max(actual_max, 0.001)  # 至少0.001，避免除零
                enhanced_data = np.clip(processed_data, 0.0, max_pressure)
                
                # 🎨 使用更强的非线性映射增强效果：创建明显的山峰
                # 使用指数映射让高值更突出，使用可配置的增强因子
                enhancement_factor = getattr(self, 'enhancement_factor', 3000)
                enhanced_data = np.power(enhanced_data / max_pressure, 0.15) * max_pressure * enhancement_factor
                
                color_map = pg.colormap.get('plasma')
                colors = color_map.map(np.clip(processed_data, 0.0, 0.005) / 0.005, mode='float')
                
                self.pressure_surface_item.setData(
                    z=enhanced_data,  # 使用增强后的数据
                    colors=colors.reshape(processed_data.shape + (4,))
                )
                
                print(f"🎨 后续帧 - 原始数据范围: [{processed_data.min():.6f}, {processed_data.max():.6f}]")
                print(f"🎨 后续帧 - 使用最大压力: {max_pressure:.6f}")
                print(f"🎨 后续帧 - 增强后数据范围: [{enhanced_data.min():.6f}, {enhanced_data.max():.6f}]")
                
        except Exception as e:
            print(f"❌ 3D热力图渲染失败: {e}")
            import traceback
            traceback.print_exc()
            self.pressure_surface_item = None # 渲染失败时重置，以便下次重建
    
    def reset_3d_camera_position(self):
        """重置3D相机位置到最佳视角 - 优化3D效果"""
        try:
            if self.pressure_3d_widget:
                # 🎨 调整相机位置，让3D显示区域更大更明显
                camera_distance = getattr(self, 'camera_distance', 8)  # 进一步减小默认距离
                camera_elevation = getattr(self, 'camera_elevation', 25)
                camera_azimuth = getattr(self, 'camera_azimuth', 45)
                
                self.pressure_3d_widget.setCameraPosition(
                    distance=camera_distance,  # 减小距离，让3D效果更明显
                    elevation=camera_elevation,  # 增加仰角，让高度差异更明显
                    azimuth=camera_azimuth    # 调整方位角，获得更好的视角
                )
                print(f"🎨 3D相机位置已重置 - 距离:{camera_distance}, 仰角:{camera_elevation}, 方位角:{camera_azimuth}")
        except Exception as e:
            print(f"⚠️ 重置3D相机位置失败: {e}")
    
    def render_2d_heatmap_optimized(self, pressure_data):
        """优化的2D热力图渲染 - PyQtGraph版本，添加平滑处理，去掉坐标轴"""
        try:
            print(f"🎨 开始渲染2D热力图，数据形状: {pressure_data.shape}")
            print(f"🎨 2D视图可见性: {self.pressure_2d_widget.isVisible()}")
            
            # 确保2D视图可见
            if not self.pressure_2d_widget.isVisible():
                print("⚠️ 2D视图不可见，尝试设置为可见")
                self.pressure_2d_widget.setVisible(True)
            
            # 清除当前2D视图
            self.pressure_2d_widget.clear()
            
            # 创建PyQtGraph图像项
            self.pressure_image_item = pg.ImageItem()
            self.pressure_2d_widget.addItem(self.pressure_image_item)
            
            # 处理数据格式
            if isinstance(pressure_data, dict):
                display_data = pressure_data['data']
                print(f"🎨 使用预处理数据，形状: {display_data.shape}")
            else:
                display_data = pressure_data
            
            # 🔧 修复坐标映射问题：转置数据确保正确的显示方向
            # numpy数组的索引是 [行, 列]，对应 [Y, X]
            # PyQtGraph的ImageItem期望数据格式为 [Y, X]，但我们的数据生成方式需要转置
            # 转置数据：从 [64, 64] 变为 [64, 64]，但交换行列的含义
            display_data = display_data.T  # 转置数据
            print(f"🎨 转置后数据形状: {display_data.shape}")
            print(f"🎨 数据范围: [{display_data.min():.6f}, {display_data.max():.6f}]")
            
            # 🎨 添加平滑处理 - 使用高斯模糊
            if hasattr(self, 'gaussian_sigma') and self.gaussian_sigma > 0:
                from scipy.ndimage import gaussian_filter
                display_data = gaussian_filter(display_data, sigma=self.gaussian_sigma)
                print(f"🎨 应用高斯平滑，sigma={self.gaussian_sigma}")
            
            # 🎨 使用固定的颜色范围 0-0.005
            color_min, color_max = 0.0, 0.005
            print(f"🎨 使用固定颜色范围: [{color_min}, {color_max}]")
            
            # 设置图像数据 - 使用转置后的数据
            print(f"🎨 设置图像数据，颜色范围: [{color_min:.6f}, {color_max:.6f}]")
            self.pressure_image_item.setImage(
                display_data,
                levels=(color_min, color_max)
            )
            
            # 🎨 设置颜色映射 - 使用plasma颜色映射
            self.pressure_image_item.setColorMap(pg.colormap.get('plasma'))
            
            # 🎨 添加色条
            try:
                # 创建色条
                colorbar = pg.ColorBarItem(
                    values=(color_min, color_max),
                    colorMap=pg.colormap.get('plasma')
                )
                colorbar.setImageItem(self.pressure_image_item)
                print("✅ 色条已添加")
            except Exception as e:
                print(f"⚠️ 色条添加失败: {e}")
            
            # 设置标题
            self.pressure_2d_widget.setTitle("压力分布 (2D)", color='w', size='12pt')
            
            # 🎨 去掉坐标轴 - 设置64x64显示区域
            # 隐藏坐标轴标签
            self.pressure_2d_widget.setLabel('left', '', color='w')
            self.pressure_2d_widget.setLabel('bottom', '', color='w')
            
            # 隐藏坐标轴刻度
            self.pressure_2d_widget.getAxis('left').setTicks([])
            self.pressure_2d_widget.getAxis('bottom').setTicks([])
            
            # 隐藏坐标轴线
            self.pressure_2d_widget.getAxis('left').setPen(None)
            self.pressure_2d_widget.getAxis('bottom').setPen(None)
            
            # 🔧 确保坐标轴范围正确 - 64x64显示区域
            self.pressure_2d_widget.setXRange(0, 63, padding=0)
            self.pressure_2d_widget.setYRange(0, 63, padding=0)
            
            # 🎨 设置图像项的位置和大小，确保完全填充64x64区域
            self.pressure_image_item.setRect(pg.QtCore.QRectF(0, 0, 64, 64))
            
            print("✅ 2D热力图渲染完成 - 已添加平滑处理，去掉坐标轴")
            
        except Exception as e:
            print(f"❌ 2D热力图渲染失败: {e}")
            import traceback
            traceback.print_exc()
    
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
    
    def check_y_axis_settings(self):
        """检查当前y轴设置"""
        try:
            print("🔍 检查当前y轴设置:")
            
            # 检查游戏区域y轴设置
            game_y_inverted = self.game_plot_widget.getViewBox().yInverted()
            game_y_range = self.game_plot_widget.getViewBox().viewRange()[1]
            print(f"🔍 游戏区域y轴方向: {'向下' if game_y_inverted else '向上'}")
            print(f"🔍 游戏区域y轴范围: {game_y_range[0]:.1f} 到 {game_y_range[1]:.1f}")
            
            # 检查2D压力视图y轴设置
            pressure_y_inverted = self.pressure_2d_widget.getViewBox().yInverted()
            pressure_y_range = self.pressure_2d_widget.getViewBox().viewRange()[1]
            print(f"🔍 2D压力视图y轴方向: {'向下' if pressure_y_inverted else '向上'}")
            print(f"🔍 2D压力视图y轴范围: {pressure_y_range[0]:.1f} 到 {pressure_y_range[1]:.1f}")
            
            # 判断设置是否正确 - 参考test_y_axis.py的检查逻辑
            if game_y_inverted and game_y_range[0] == 0 and game_y_range[1] == 63:
                print("✅ 游戏区域y轴设置正确: 向下，0在顶部，63在底部")
            else:
                print("❌ 游戏区域y轴设置错误")
                
            if pressure_y_inverted and pressure_y_range[0] == 0 and pressure_y_range[1] == 63:
                print("✅ 2D压力视图y轴设置正确: 向下，0在顶部，63在底部")
            else:
                print("❌ 2D压力视图y轴设置错误")
                
        except Exception as e:
            print(f"⚠️ 检查y轴设置失败: {e}")
    