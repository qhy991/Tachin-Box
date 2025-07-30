# -*- coding: utf-8 -*-
"""
推箱子游戏渲染器模块（高性能解耦版）
Renderer Module for Box Push Game (Decoupled High Performance Version)

本模块将2D游戏区域和3D压力分布解耦，使用独立渲染线程和缓存机制，
大幅提升渲染性能，解决3D渲染拖累2D渲染的问题。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import LinearSegmentedColormap
from PyQt5.QtCore import QTimer, pyqtSignal, Qt, QThread, QMutex, QWaitCondition
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QSplitter
from PyQt5.QtGui import QFont, QPalette, QColor
import sys
import os
import time
from typing import Dict, Optional, Any, Tuple
from collections import deque

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

try:
    from .path_visualization_manager import PathVisualizationManager
except ImportError:
    from path_visualization_manager import PathVisualizationManager

class RenderCache:
    """渲染缓存管理器"""
    
    def __init__(self, max_cache_size=10):
        self.max_cache_size = max_cache_size
        self.cache = {}
        self.access_times = {}
        self.mutex = QMutex()
    
    def get(self, key):
        """获取缓存项"""
        self.mutex.lock()
        try:
            if key in self.cache:
                self.access_times[key] = time.time()
                return self.cache[key]
            return None
        finally:
            self.mutex.unlock()
    
    def set(self, key, value):
        """设置缓存项"""
        self.mutex.lock()
        try:
            # 如果缓存已满，删除最旧的项
            if len(self.cache) >= self.max_cache_size:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            self.cache[key] = value
            self.access_times[key] = time.time()
        finally:
            self.mutex.unlock()
    
    def clear(self):
        """清空缓存"""
        self.mutex.lock()
        try:
            self.cache.clear()
            self.access_times.clear()
        finally:
            self.mutex.unlock()

class PressureRendererThread(QThread):
    """压力分布渲染线程 - 独立处理3D渲染"""
    
    render_completed = pyqtSignal(object)  # 发送渲染结果
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pressure_data = None
        self.render_options = {}
        self.running = True
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.cache = RenderCache(max_cache_size=5)
    
    def set_pressure_data(self, pressure_data, options=None):
        """设置压力数据和渲染选项"""
        self.mutex.lock()
        try:
            self.pressure_data = pressure_data.copy() if pressure_data is not None else None
            if options:
                self.render_options.update(options)
            self.condition.wakeAll()
        finally:
            self.mutex.unlock()
    
    def stop(self):
        """停止渲染线程"""
        self.running = False
        self.condition.wakeAll()
        self.wait()
    
    def run(self):
        """渲染线程主循环"""
        print("🎨 压力渲染线程已启动")
        while self.running:
            self.mutex.lock()
            try:
                if self.pressure_data is None:
                    self.condition.wait(self.mutex, 100)  # 等待100ms
                    continue
                
                # 执行渲染
                render_result = self._render_pressure_distribution()
                if render_result:
                    print(f"🎨 压力渲染完成: {render_result.get('type', 'unknown')}")
                    self.render_completed.emit(render_result)
                
                # 等待一段时间再渲染下一帧
                self.condition.wait(self.mutex, 100)  # 等待100ms
                
            except Exception as e:
                print(f"❌ 压力渲染线程错误: {e}")
                import traceback
                traceback.print_exc()
            finally:
                self.mutex.unlock()
        
        print("🎨 压力渲染线程已停止")
    
    def _generate_cache_key(self):
        """生成缓存键"""
        if self.pressure_data is None:
            return None
        
        # 基于数据哈希和渲染选项生成键
        data_hash = hash(self.pressure_data.tobytes())
        options_hash = hash(str(sorted(self.render_options.items())))
        return f"{data_hash}_{options_hash}"
    
    def _render_pressure_distribution(self):
        """渲染压力分布"""
        try:
            if self.pressure_data is None:
                print("❌ 压力数据为空")
                return None
            
            print(f"🎨 开始渲染压力分布，数据形状: {self.pressure_data.shape}")
            
            # 预处理数据
            processed_data = self._preprocess_pressure_data(self.pressure_data)
            if processed_data is None:
                print("❌ 数据预处理失败")
                return None
            
            display_data = processed_data['data']
            view_mode = self.render_options.get('heatmap_view_mode', '2d')
            
            print(f"🎨 渲染模式: {view_mode}, 数据范围: {np.min(display_data):.6f} - {np.max(display_data):.6f}")
            
            # 根据模式选择渲染方式
            if view_mode == '3d':
                result = self._render_3d_heatmap(display_data)
            else:
                result = self._render_2d_heatmap(display_data)
            
            if result:
                print(f"✅ {view_mode.upper()}渲染成功")
            else:
                print(f"❌ {view_mode.upper()}渲染失败")
            
            return result
                
        except Exception as e:
            print(f"❌ 压力分布渲染失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _preprocess_pressure_data(self, pressure_data):
        """预处理压力数据"""
        if pressure_data is None or pressure_data.size == 0:
            print("❌ 输入压力数据为空")
            return None
        
        try:
            print(f"🔧 预处理压力数据，原始形状: {pressure_data.shape}")
            
            # 复制数据避免修改原始数据
            processed_data = pressure_data.copy()
            
            # 应用高斯模糊
            if self.render_options.get('use_gaussian_blur', False):
                sigma = self.render_options.get('gaussian_sigma', 1.0)
                processed_data = self._gaussian_blur(processed_data, sigma)
                print(f"🔧 应用高斯模糊，sigma={sigma}")
            
            # 应用X/Y轴交换
            if self.render_options.get('use_xy_swap', False):
                processed_data = processed_data.T
                print("🔧 应用X/Y轴交换")
            
            # 确保数据不为空
            if processed_data.size == 0:
                print("❌ 处理后数据为空")
                return None
            
            # 计算数据范围
            data_min = np.min(processed_data)
            data_max = np.max(processed_data)
            
            # 如果数据全为0，设置一个小的非零值
            if data_max <= 0:
                data_max = 0.001
                print("🔧 数据全为0，设置默认最大值")
            
            print(f"🔧 预处理完成，数据范围: {data_min:.6f} - {data_max:.6f}")
            
            return {
                'data': processed_data,
                'vmin': data_min,
                'vmax': data_max
            }
            
        except Exception as e:
            print(f"❌ 数据预处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _gaussian_blur(self, data, sigma=1.0):
        """高斯模糊"""
        try:
            from scipy.ndimage import gaussian_filter
            return gaussian_filter(data, sigma=sigma)
        except ImportError:
            return data
    
    def _get_custom_colormap(self):
        """获取自定义颜色映射"""
        if self.render_options.get('use_custom_colormap', False):
            import matplotlib.colors as mcolors
            colors = np.array(COLORS) / 255.0
            pos = np.linspace(0, 1, len(colors))
            return mcolors.LinearSegmentedColormap.from_list('custom_pressure', list(zip(pos, colors)))
        else:
            return plt.cm.viridis
    
    def _render_2d_heatmap(self, data):
        """渲染2D热力图"""
        try:
            print(f"🎨 开始渲染2D热力图，数据形状: {data.shape}")
            
            # 计算数据范围
            data_min = np.min(data)
            data_max = np.max(data)
            if data_max <= data_min:
                data_max = data_min + 0.001
            
            print(f"🎨 2D数据范围: {data_min:.6f} - {data_max:.6f}")
            
            # 创建独立的图形对象
            fig = Figure(figsize=(8, 6), facecolor='black')
            ax = fig.add_subplot(111)
            
            # 设置样式
            ax.set_facecolor('black')
            ax.set_title("压力分布 (2D)", color='white', fontsize=12)
            
            # 渲染热力图
            im = ax.imshow(data, cmap=plt.cm.viridis, aspect='auto', 
                          interpolation='bilinear', origin='upper',
                          vmin=data_min, vmax=data_max)
            
            # 添加颜色条
            fig.colorbar(im, ax=ax, label='压力值')
            
            # 设置轴标签
            ax.set_xlabel('X', color='white')
            ax.set_ylabel('Y', color='white')
            ax.tick_params(colors='white')
            
            print("✅ 2D热力图渲染完成")
            
            return {
                'type': '2d_heatmap',
                'figure': fig,
                'data': data,
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"❌ 2D热力图渲染失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _render_3d_heatmap(self, data):
        """渲染3D热力图"""
        try:
            print(f"🎨 开始渲染3D热力图，数据形状: {data.shape}")
            
            # 计算数据范围
            data_min = np.min(data)
            data_max = np.max(data)
            if data_max <= data_min:
                data_max = data_min + 0.001
            
            print(f"🎨 3D数据范围: {data_min:.6f} - {data_max:.6f}")
            
            # 创建独立的图形对象
            fig = Figure(figsize=(8, 6), facecolor='black')
            ax = fig.add_subplot(111, projection='3d')
            
            # 设置样式
            ax.set_facecolor('black')
            ax.set_title("压力分布 (3D)", color='white', fontsize=12)
            
            # 创建网格
            rows, cols = data.shape
            x = np.arange(cols)
            y = np.arange(rows)
            X, Y = np.meshgrid(x, y)
            
            # 渲染3D表面
            surf = ax.plot_surface(X, Y, data, cmap=plt.cm.viridis, 
                                 linewidth=0, antialiased=True, alpha=0.8,
                                 vmin=data_min, vmax=data_max)
            
            # 设置轴标签
            ax.set_xlabel('X', color='white')
            ax.set_ylabel('Y', color='white')
            ax.set_zlabel('压力', color='white')
            ax.tick_params(colors='white')
            
            print("✅ 3D热力图渲染完成")
            
            return {
                'type': '3d_heatmap',
                'figure': fig,
                'data': data,
                'X': X,
                'Y': Y,
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"❌ 3D热力图渲染失败: {e}")
            import traceback
            traceback.print_exc()
            return None

class GameAreaRenderer(FigureCanvas):
    """2D游戏区域渲染器 - 独立处理游戏区域渲染"""
    
    mouse_pressed = pyqtSignal(float, float)
    
    def __init__(self, parent=None):
        # 创建独立的图形
        self.fig = Figure(figsize=(8, 6), facecolor='black')
        super().__init__(self.fig)
        
        # 设置图形属性
        self.fig.patch.set_facecolor('black')
        
        # 创建轴
        self.ax = self.fig.add_subplot(111)
        
        # 初始化游戏状态
        self.is_contact = False
        self.is_sliding = False
        self.current_cop = None
        self.initial_cop = None
        self.movement_distance = 0.0
        self.box_position = np.array([32.0, 32.0])
        self.box_target_position = np.array([32.0, 32.0])
        self.box_size = 6.0
        self.consensus_angle = None
        self.consensus_confidence = 0.0
        self.cop_history = []
        
        # 性能统计
        self.frame_count = 0
        self.last_update_time = time.time()
        self.current_fps = 0.0
        
        # 设置游戏区域
        self.setup_game_area()
        
        # 连接鼠标事件
        self.connect_mouse_events()
        
        # 创建渲染定时器
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update_display)
        
        # 设置默认帧率
        try:
            from interfaces.ordinary.BoxGame.run_box_game_optimized import FrameRateConfig
            interval_ms = FrameRateConfig.get_interval_ms("renderer_fps")
        except ImportError:
            interval_ms = 33  # 30 FPS
        
        self.render_timer.setInterval(interval_ms)
        
        print("✅ 游戏区域渲染器已初始化")
    
    def setup_game_area(self):
        """设置游戏区域"""
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("推箱子游戏 - 实时传感器", fontsize=14, color='white', fontweight='bold')
        self.ax.set_xlim(0, 63)
        self.ax.set_ylim(63, 0)  # Y轴反转
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3, color='gray')
        self.ax.set_facecolor('black')
        
        # 设置轴样式
        self.ax.tick_params(colors='white', labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color('white')
        
        # 优化布局
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    
    def connect_mouse_events(self):
        """连接鼠标事件"""
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
    
    def on_mouse_press(self, event):
        """处理鼠标点击"""
        if event.inaxes == self.ax:
            self.mouse_pressed.emit(event.xdata, event.ydata)
    
    def update_game_state(self, state_info):
        """更新游戏状态"""
        # 更新基本状态
        self.is_contact = state_info.get('is_contact', False)
        self.is_sliding = state_info.get('is_sliding', False)
        
        # 更新位置信息
        self.current_cop = state_info.get('current_cop')
        self.initial_cop = state_info.get('initial_cop')
        self.movement_distance = state_info.get('movement_distance', 0.0)
        
        # 更新箱子位置
        box_pos = state_info.get('box_position')
        box_target = state_info.get('box_target_position')
        if box_pos is not None:
            self.box_position = np.array(box_pos)
        if box_target is not None:
            self.box_target_position = np.array(box_target)
        
        # 更新COP历史
        if self.current_cop is not None:
            self.cop_history.append(self.current_cop)
        
        # 更新角度信息
        consensus_angle = state_info.get('consensus_angle')
        if consensus_angle is not None:
            self.consensus_angle = consensus_angle
            self.consensus_confidence = state_info.get('consensus_confidence', 0.0)
            # self.angle_history.append(consensus_angle) # This line was removed from __init__
    
    def update_display(self):
        """更新显示"""
        try:
            # 清空画布
            self.ax.clear()
            
            # 重新设置基本属性
            self.ax.set_title("推箱子游戏 - 实时传感器", fontsize=14, color='white', fontweight='bold')
            self.ax.set_xlim(0, 63)
            self.ax.set_ylim(63, 0)
            self.ax.set_aspect('equal')
            self.ax.grid(True, alpha=0.3, color='gray')
            self.ax.set_facecolor('black')
            self.ax.tick_params(colors='white', labelsize=8)
            for spine in self.ax.spines.values():
                spine.set_color('white')
            
            # 渲染游戏元素
            self.render_box()
            self.render_cop_and_trajectory()
            self.render_status_text()
            
            # 强制更新画布
            self.draw()
            self.flush_events()
            
            # 强制重绘整个窗口
            self.update()
            
            # 更新性能统计
            self.update_performance_stats()
            
        except Exception as e:
            print(f"❌ 游戏区域渲染失败: {e}")
            import traceback
            traceback.print_exc()
    
    def render_box(self):
        """渲染箱子"""
        # 确定箱子颜色
        if self.is_sliding:
            box_color = 'red'
        elif self.is_contact:
            box_color = 'yellow'
        else:
            box_color = 'blue'
        
        # 绘制箱子
        box = plt.Rectangle(
            (self.box_position[0] - self.box_size/2, self.box_position[1] - self.box_size/2),
            self.box_size, self.box_size,
            facecolor=box_color, edgecolor='white', linewidth=2, alpha=0.8
        )
        self.ax.add_patch(box)
        
        # 绘制目标位置
        target = plt.Circle(
            (self.box_target_position[0], self.box_target_position[1]),
            self.box_size/4, facecolor='none', edgecolor='green', 
            linewidth=2, linestyle='--', alpha=0.6
        )
        self.ax.add_patch(target)
    
    def render_cop_and_trajectory(self):
        """渲染COP和轨迹"""
        if self.current_cop is not None:
            # 绘制当前COP
            cop_color = 'red' if self.is_sliding else 'yellow'
            self.ax.plot(self.current_cop[0], self.current_cop[1], 'o', 
                        color=cop_color, markersize=8, markeredgecolor='white', markeredgewidth=2)
            
            # 绘制COP轨迹
            if len(self.cop_history) > 1:
                cop_x = [cop[0] for cop in self.cop_history]
                cop_y = [cop[1] for cop in self.cop_history]
                self.ax.plot(cop_x, cop_y, '-', color='cyan', linewidth=2, alpha=0.6)
            
            # 绘制初始COP
            if self.initial_cop is not None:
                self.ax.plot(self.initial_cop[0], self.initial_cop[1], 's', 
                           color='green', markersize=6, markeredgecolor='white', markeredgewidth=1)
    
    def render_status_text(self):
        """渲染状态文本"""
        status_lines = []
        
        # 基本状态
        contact_status = "✅ 接触" if self.is_contact else "❌ 未接触"
        sliding_status = "🔄 滑动" if self.is_sliding else "⏹️ 静止"
        status_lines.append(f"状态: {contact_status} | {sliding_status}")
        
        # 位置信息
        if self.current_cop is not None:
            status_lines.append(f"COP: ({self.current_cop[0]:.1f}, {self.current_cop[1]:.1f})")
        
        # 移动距离
        status_lines.append(f"移动距离: {self.movement_distance:.2f}")
        
        # 角度信息
        if self.consensus_angle is not None:
            status_lines.append(f"角度: {self.consensus_angle:.1f}° (置信度: {self.consensus_confidence:.2f})")
        
        # 渲染文本
        status_text = '\n'.join(status_lines)
        self.ax.text(0.02, 0.98, status_text, transform=self.ax.transAxes,
                    color='white', fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.8))
    
    def update_performance_stats(self):
        """更新性能统计"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_update_time >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_update_time)
            self.frame_count = 0
            self.last_update_time = current_time
    
    def start_rendering(self):
        """开始渲染"""
        try:
            print("🎨 游戏区域渲染器开始渲染...")
            
            # 启动渲染定时器
            self.render_timer.start()
            
            # 立即更新一次显示
            self.update_display()
            
            print("✅ 游戏区域渲染器已启动")
            
        except Exception as e:
            print(f"❌ 游戏区域渲染器启动失败: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_rendering(self):
        """停止渲染"""
        self.render_timer.stop()
        print("⏹️ 游戏区域渲染已停止")
    
    def get_performance_stats(self):
        """获取性能统计"""
        return {
            'current_fps': self.current_fps,
            'frame_count': self.frame_count
        }
    
    def reset_visualization(self):
        """重置可视化"""
        # 清空历史数据
        self.cop_history.clear()
        # self.angle_history.clear() # This line was removed from __init__
        
        # 重置状态
        self.is_contact = False
        self.is_sliding = False
        self.consensus_angle = None
        self.consensus_confidence = 0.0
        self.current_cop = None
        self.initial_cop = None
        self.movement_distance = 0.0
        
        print("🔄 游戏区域可视化已重置")
    
    def update_frame_rate(self):
        """更新帧率设置"""
        try:
            from interfaces.ordinary.BoxGame.run_box_game_optimized import FrameRateConfig
            interval_ms = FrameRateConfig.get_interval_ms("renderer_fps")
            self.render_timer.setInterval(interval_ms)
            print(f"🎨 游戏区域渲染器帧率已更新: {1000/interval_ms:.1f} FPS")
        except ImportError:
            print("⚠️ 无法导入FrameRateConfig，使用默认帧率")

class BoxGameRendererOptimized(QWidget):
    """推箱子游戏渲染器（高性能解耦版）"""
    
    mouse_pressed = pyqtSignal(float, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化组件
        self.game_renderer = None
        self.pressure_renderer_thread = None
        self.pressure_canvas = None
        
        # 渲染选项
        self.render_options = {
            'heatmap_view_mode': '2d',  # 默认2D模式
            'use_gaussian_blur': False,
            'use_xy_swap': False,
            'use_custom_colormap': False,
            'gaussian_sigma': 1.0
        }
        
        # 性能统计
        self.game_fps = 0.0
        self.pressure_fps = 0.0
        
        self.init_ui()
        self.init_renderers()
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QHBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建游戏区域渲染器
        self.game_renderer = GameAreaRenderer()
        splitter.addWidget(self.game_renderer)
        
        # 创建压力分布画布
        self.pressure_canvas = FigureCanvas(Figure(figsize=(8, 6), facecolor='black'))
        splitter.addWidget(self.pressure_canvas)
        
        # 设置分割器比例 (2:3)
        splitter.setSizes([400, 600])
        
        # 初始化压力分布画布显示
        self.init_pressure_display()
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
        """)
    
    def init_pressure_display(self):
        """初始化压力分布显示"""
        try:
            print("🎨 初始化压力分布显示...")
            
            # 清空画布
            self.pressure_canvas.figure.clear()
            
            # 创建轴
            ax = self.pressure_canvas.figure.add_subplot(111)
            
            # 创建空的压力数据
            empty_data = np.zeros((64, 64))
            
            # 显示空的热力图
            im = ax.imshow(empty_data, cmap=plt.cm.viridis, aspect='auto', 
                          interpolation='bilinear', origin='upper')
            
            # 添加颜色条
            self.pressure_canvas.figure.colorbar(im, ax=ax, label='压力值')
            
            # 设置轴标签
            ax.set_xlabel('X', color='white')
            ax.set_ylabel('Y', color='white')
            ax.tick_params(colors='white')
            ax.set_title("压力分布 (等待数据...)", color='white', fontsize=12)
            ax.set_facecolor('black')
            
            # 强制更新画布
            self.pressure_canvas.draw()
            self.pressure_canvas.flush_events()
            
            # 强制重绘整个窗口
            self.pressure_canvas.update()
            self.update()
            
            print("✅ 压力分布显示初始化完成")
            
        except Exception as e:
            print(f"❌ 初始化压力分布显示失败: {e}")
            import traceback
            traceback.print_exc()
    
    def init_renderers(self):
        """初始化渲染器"""
        # 创建压力渲染线程
        self.pressure_renderer_thread = PressureRendererThread()
        self.pressure_renderer_thread.render_completed.connect(self.on_pressure_render_completed)
        self.pressure_renderer_thread.start()
        
        print("✅ 渲染器初始化完成")
    
    def connect_signals(self):
        """连接信号"""
        # 游戏区域鼠标事件
        self.game_renderer.mouse_pressed.connect(self.mouse_pressed.emit)
    
    def update_game_state(self, state_info):
        """更新游戏状态"""
        # 更新游戏区域渲染器
        self.game_renderer.update_game_state(state_info)
    
    def update_pressure_data(self, pressure_data):
        """更新压力数据"""
        if self.pressure_renderer_thread:
            self.pressure_renderer_thread.set_pressure_data(pressure_data, self.render_options)
    
    def update_analysis_results(self, analysis_results):
        """更新分析结果 - 兼容性方法"""
        # 优化渲染器不需要单独处理分析结果，已集成到游戏状态中
        pass
    
    def update_consensus_angle(self, angle, confidence):
        """更新共识角度 - 兼容性方法"""
        # 优化渲染器不需要单独处理角度，已集成到游戏状态中
        pass
    
    def update_navigation_info(self, nav_info):
        """更新导航信息 - 兼容性方法"""
        # 优化渲染器不需要单独处理导航信息，已集成到游戏状态中
        pass
    
    def on_pressure_render_completed(self, render_result):
        """处理压力渲染完成"""
        try:
            print(f"🎨 收到压力渲染结果: {render_result.get('type', 'unknown') if render_result else 'None'}")
            
            if render_result and 'data' in render_result:
                # 清空当前画布
                self.pressure_canvas.figure.clear()
                
                # 获取渲染数据
                data = render_result['data']
                render_type = render_result.get('type', '2d_heatmap')
                
                print(f"🎨 处理渲染结果: 类型={render_type}, 数据形状={data.shape}")
                
                # 计算数据范围
                data_min = np.min(data)
                data_max = np.max(data)
                if data_max <= data_min:
                    data_max = data_min + 0.001
                
                if render_type == '3d_heatmap':
                    # 创建3D轴
                    ax = self.pressure_canvas.figure.add_subplot(111, projection='3d')
                    
                    # 获取网格数据
                    X = render_result.get('X')
                    Y = render_result.get('Y')
                    
                    if X is not None and Y is not None:
                        # 渲染3D表面
                        surf = ax.plot_surface(X, Y, data, cmap=plt.cm.viridis, 
                                             linewidth=0, antialiased=True, alpha=0.8,
                                             vmin=data_min, vmax=data_max)
                        
                        # 设置轴标签
                        ax.set_xlabel('X', color='white')
                        ax.set_ylabel('Y', color='white')
                        ax.set_zlabel('压力', color='white')
                        ax.tick_params(colors='white')
                        ax.set_title("压力分布 (3D)", color='white', fontsize=12)
                        ax.set_facecolor('black')
                        
                        print("✅ 3D表面已绘制到画布")
                    else:
                        print("❌ 3D网格数据缺失")
                        return
                else:
                    # 创建2D轴
                    ax = self.pressure_canvas.figure.add_subplot(111)
                    
                    # 渲染2D热力图
                    im = ax.imshow(data, cmap=plt.cm.viridis, aspect='auto', 
                                 interpolation='bilinear', origin='upper',
                                 vmin=data_min, vmax=data_max)
                    
                    # 添加颜色条
                    self.pressure_canvas.figure.colorbar(im, ax=ax, label='压力值')
                    
                    # 设置轴标签
                    ax.set_xlabel('X', color='white')
                    ax.set_ylabel('Y', color='white')
                    ax.tick_params(colors='white')
                    ax.set_title("压力分布 (2D)", color='white', fontsize=12)
                    ax.set_facecolor('black')
                    
                    print("✅ 2D热力图已绘制到画布")
                
                # 强制更新画布
                self.pressure_canvas.draw()
                self.pressure_canvas.flush_events()
                
                # 强制重绘整个窗口
                self.pressure_canvas.update()
                self.update()
                
                print("✅ 画布已更新并强制刷新")
                
                # 更新性能统计
                current_time = time.time()
                render_time = render_result.get('timestamp', current_time)
                if current_time > render_time:
                    self.pressure_fps = 1.0 / (current_time - render_time)
                    print(f"📊 压力渲染FPS: {self.pressure_fps:.1f}")
                
            else:
                print("❌ 渲染结果无效或缺少数据")
                
        except Exception as e:
            print(f"❌ 压力渲染结果处理失败: {e}")
            import traceback
            traceback.print_exc()
    
    def start_rendering(self):
        """开始渲染"""
        self.game_renderer.start_rendering()
        print("🚀 优化渲染器已启动")
    
    def stop_rendering(self):
        """停止渲染"""
        self.game_renderer.stop_rendering()
        if self.pressure_renderer_thread:
            self.pressure_renderer_thread.stop()
        print("⏹️ 优化渲染器已停止")
    
    def update_frame_rate(self):
        """更新帧率"""
        self.game_renderer.update_frame_rate()
    
    def get_performance_stats(self):
        """获取性能统计"""
        game_stats = self.game_renderer.get_performance_stats()
        return {
            'game_fps': game_stats['current_fps'],
            'pressure_fps': self.pressure_fps,
            'total_fps': (game_stats['current_fps'] + self.pressure_fps) / 2
        }
    
    def set_visualization_options(self, options):
        """设置可视化选项"""
        self.render_options.update(options)
        print(f"🎨 渲染选项已更新: {list(options.keys())}")
    
    def set_3d_rendering_options(self, options):
        """设置3D渲染选项"""
        # 更新视图模式
        if 'heatmap_view_mode' in options:
            self.render_options['heatmap_view_mode'] = options['heatmap_view_mode']
        print(f"🎨 3D渲染选项已更新: {list(options.keys())}")
    
    def set_preprocessing_options(self, options):
        """设置预处理选项"""
        self.render_options.update(options)
        print(f"🎨 预处理选项已更新: {list(options.keys())}")
    
    def reset_visualization(self):
        """重置可视化"""
        self.game_renderer.reset_visualization()
        print("🔄 可视化已重置")
    
    def closeEvent(self, event):
        """关闭事件"""
        self.stop_rendering()
        event.accept() 