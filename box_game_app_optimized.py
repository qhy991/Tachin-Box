# -*- coding: utf-8 -*-
"""
推箱子游戏核心引擎模块（高性能优化版）
Core Game Engine Module for Box Push Game (Optimized Version)

本模块基于 box_game_core.py，集成高性能 V2 切向力分析器，
并对分析流程、接口结构、数据桥接等做了进一步优化。
现在增加了路径规划功能，支持预设路径和自定义路径。
"""

import numpy as np
import time
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QSplitter, QApplication, QVBoxLayout, QFrame
from PyQt5.QtGui import QIcon
import sys
import os
from typing import Dict, Optional, Any

# 🎨 集成utils功能
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
    from utils import apply_dark_theme, catch_exceptions
    UTILS_AVAILABLE = True
    print("✅ utils功能已集成到主窗口")
except ImportError as e:
    print(f"⚠️ utils功能不可用: {e}")
    UTILS_AVAILABLE = False

# 🔍 检查真实传感器可用性
REAL_SENSOR_AVAILABLE = False
try:
    from data_processing.data_handler import DataHandler
    from backends.sensor_driver import LargeUsbSensorDriver
    REAL_SENSOR_AVAILABLE = True
    print("✅ 真实传感器驱动已加载")
except ImportError as e:
    print(f"⚠️ 真实传感器驱动不可用，将使用模拟传感器: {e}")

# 导入传感器接口 - 使用run_box_game_optimized.py中定义的接口
try:
    from interfaces.ordinary.BoxGame.run_box_game_optimized import (
        FrameRateConfig, 
        SensorDataThread
    )
    SENSOR_INTERFACES_AVAILABLE = True
    print("✅ 传感器接口已加载")
except ImportError as e:
    print(f"⚠️ 无法导入传感器接口: {e}")
    SENSOR_INTERFACES_AVAILABLE = False

# 导入路径规划模块
try:
    from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanningGameEnhancer
    PATH_PLANNING_AVAILABLE = True
    print("✅ 路径规划模块已加载")
except ImportError:
    print("⚠️ 无法导入路径规划模块")
    PATH_PLANNING_AVAILABLE = False


from interfaces.ordinary.BoxGame.contact_filter import is_special_idle_case

from interfaces.ordinary.BoxGame.box_smart_control_system import SmartControlSystem

class PerformanceMonitor:
    """性能监控器 - 跟踪各种处理时间"""
    
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.processing_times = deque(maxlen=window_size)
        self.render_times = deque(maxlen=window_size)
        self.physics_times = deque(maxlen=window_size)
        self.total_times = deque(maxlen=window_size)
        self.frame_count = 0
        
    def add_processing_time(self, time_ms):
        """添加数据处理时间"""
        self.processing_times.append(time_ms)
        self.frame_count += 1
        
    def add_render_time(self, time_ms):
        """添加渲染时间"""
        self.render_times.append(time_ms)
        
    def add_physics_time(self, time_ms):
        """添加物理更新时间"""
        self.physics_times.append(time_ms)
        
    def add_total_time(self, time_ms):
        """添加总处理时间"""
        self.total_times.append(time_ms)
        
    def get_statistics(self):
        """获取性能统计信息"""
        stats = {
            'frame_count': self.frame_count,
            'processing': {
                'current': self.processing_times[-1] if self.processing_times else 0,
                'avg': np.mean(self.processing_times) if self.processing_times else 0,
                'max': np.max(self.processing_times) if self.processing_times else 0,
                'min': np.min(self.processing_times) if self.processing_times else 0
            },
            'render': {
                'current': self.render_times[-1] if self.render_times else 0,
                'avg': np.mean(self.render_times) if self.render_times else 0,
                'max': np.max(self.render_times) if self.render_times else 0,
                'min': np.min(self.render_times) if self.render_times else 0
            },
            'physics': {
                'current': self.physics_times[-1] if self.physics_times else 0,
                'avg': np.mean(self.physics_times) if self.physics_times else 0,
                'max': np.max(self.physics_times) if self.physics_times else 0,
                'min': np.min(self.physics_times) if self.physics_times else 0
            },
            'total': {
                'current': self.total_times[-1] if self.total_times else 0,
                'avg': np.mean(self.total_times) if self.total_times else 0,
                'max': np.max(self.total_times) if self.total_times else 0,
                'min': np.min(self.total_times) if self.total_times else 0
            }
        }
        return stats
        
    def print_performance_summary(self):
        """打印性能汇总"""
        stats = self.get_statistics()
        print("\n" + "="*60)
        print("📊 性能监控汇总")
        print("="*60)
        print(f"📈 总帧数: {stats['frame_count']}")
        print(f"⏱️ 数据处理: 当前={stats['processing']['current']:.2f}ms, 平均={stats['processing']['avg']:.2f}ms, 最大={stats['processing']['max']:.2f}ms, 最小={stats['processing']['min']:.2f}ms")
        print(f"🎨 渲染时间: 当前={stats['render']['current']:.2f}ms, 平均={stats['render']['avg']:.2f}ms, 最大={stats['render']['max']:.2f}ms, 最小={stats['render']['min']:.2f}ms")
        print(f"⚙️ 物理更新: 当前={stats['physics']['current']:.2f}ms, 平均={stats['physics']['avg']:.2f}ms, 最大={stats['physics']['max']:.2f}ms, 最小={stats['physics']['min']:.2f}ms")
        print(f"📊 总处理时间: 当前={stats['total']['current']:.2f}ms, 平均={stats['total']['avg']:.2f}ms, 最大={stats['total']['max']:.2f}ms, 最小={stats['total']['min']:.2f}ms")
        
        # 计算理论FPS
        avg_total = stats['total']['avg']
        theoretical_fps = 1000 / avg_total if avg_total > 0 else 0
        print(f"🎯 理论FPS: {theoretical_fps:.1f} (基于平均总处理时间)")
        print("="*60)

class BoxGameDataBridgeOptimized(QObject):
    """游戏数据桥接器"""
    pressure_data_updated = pyqtSignal(np.ndarray)
    analysis_results_updated = pyqtSignal(dict)
    consensus_angle_updated = pyqtSignal(float, float)
    # 🆕 新增idle状态分析信号
    idle_analysis_updated = pyqtSignal(dict)
    # 🕐 新增物理时间信号
    physics_time_updated = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pressure_data = None
        self.analysis_results = None
        self.last_update_time = 0
        self.contact_start_time = None
        self.pressure_history = deque(maxlen=20)
        self.consensus_history = deque(maxlen=10)

    def set_pressure_data(self, pressure_data):
        if pressure_data is not None:
            self.pressure_data = pressure_data.copy()
            self.last_update_time = time.time()
            current_max_pressure = np.max(pressure_data)
            if current_max_pressure > 0.01:
                if self.contact_start_time is None:
                    self.contact_start_time = time.time()
            else:
                self.contact_start_time = None
            self.pressure_history.append(self.pressure_data)
            self.pressure_data_updated.emit(self.pressure_data)

    def set_analysis_results(self, analysis_results):
        if analysis_results is not None:
            self.analysis_results = analysis_results
            self.analysis_results_updated.emit(analysis_results)

    def set_consensus_angle(self, angle, confidence):
        if angle is not None:
            self.consensus_history.append((angle, confidence, time.time()))
            self.consensus_angle_updated.emit(angle, confidence)

    # 🆕 新增idle状态分析数据设置
    def set_idle_analysis(self, idle_analysis):
        if idle_analysis is not None:
            self.idle_analysis_updated.emit(idle_analysis)

    # 🕐 新增物理时间设置方法
    def set_physics_time(self, physics_time_ms):
        if physics_time_ms is not None:
            self.physics_time_updated.emit(physics_time_ms)

    def get_contact_time(self):
        if self.contact_start_time is None:
            return 0.0
        return time.time() - self.contact_start_time

    def get_last_consensus_angle(self):
        if self.consensus_history:
            return self.consensus_history[-1][0]
        return 0.0

    def get_consensus_confidence(self):
        if self.consensus_history:
            return self.consensus_history[-1][1]
        return 0.0

    def get_movement_distance(self):
        if hasattr(self, 'last_movement_distance'):
            return self.last_movement_distance
        return 0.0

    def update_pressure_data(self, pressure_data):
        self.set_pressure_data(pressure_data)

    def get_latest_data(self):
        return {
            'pressure_data': self.pressure_data,
            'analysis_results': self.analysis_results,
            'update_time': self.last_update_time
        }




class BoxGameCoreOptimized(QObject):
    """推箱子游戏核心引擎"""
    game_state_changed = pyqtSignal(dict)
    box_state_updated = pyqtSignal(dict)
    analysis_completed = pyqtSignal(dict)
    
    # 新增路径规划相关信号
    path_progress_updated = pyqtSignal(dict)
    path_target_reached = pyqtSignal(dict)
    path_completed = pyqtSignal(dict)
    navigation_info_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pressure_threshold = 0.001  # 降低压力阈值，从0.001改为0.0005
        self.sliding_threshold = 0.08 
        self.contact_area_threshold = 3  # 降低接触面积阈值，从3改为1
        self.tangential_analyzer = None
        self.setup_analyzers()
        self.data_bridge = None
        self.box_position = np.array([32.0, 32.0])
        self.box_original_position = np.array([32.0, 32.0])
        self.box_target_position = np.array([32.0, 32.0])
        self.box_size = 12.0  # 增大箱子尺寸，从6.0改为12.0
        
        # 🆕 添加游戏区域尺寸属性
        self.game_width = 64.0
        self.game_height = 64.0
        
        self.is_contact = False
        self.is_tangential = False
        self.is_sliding = False
        self.current_cop = None
        self.initial_cop = None
        self.movement_distance = 0.0
        self.consensus_history = deque(maxlen=10)
        self.confidence_history = deque(maxlen=10)
        self.analysis_frame_count = 0
        self.gradient_threshold = 5e-4  # 提高梯度阈值，从1e-4增加到5e-4，减少噪声影响
        
        # 🆕 新增IDLE检测开关
        self.enable_idle_detection = False
        
        # 🆕 新增时间稳定性检查参数
        self.idle_stability_frames = 3  # 需要连续3帧稳定才判定为idle
        self.idle_stability_history = deque(maxlen=5)  # 保存最近5帧的idle状态
        self.consecutive_idle_frames = 0  # 连续idle帧数
        
        # 🎮 集成智能控制系统
        self.smart_control = SmartControlSystem()
        print("🎮 智能双模式控制系统已集成")
        
        # 🗺️ 路径规划系统
        if PATH_PLANNING_AVAILABLE:
            self.path_enhancer = PathPlanningGameEnhancer(self)
            self.setup_path_connections()
        else:
            self.path_enhancer = None
        
        # ⏰ 物理更新定时器
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self.update_physics)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_physics)
        # 🚀 启动物理更新循环 - 使用FrameRateConfig中的配置
        interval_ms = FrameRateConfig.get_interval_ms("core_fps")
        self.update_timer.start(interval_ms)
        
        # 🆕 发送初始状态信息
        initial_fps = 1000 / interval_ms
        self.game_state_changed.emit({
            'status': f'游戏引擎已初始化 ({initial_fps:.1f} FPS)',
            'frame_rate': initial_fps,
            'performance_mode': FrameRateConfig.current_mode
        })

    def setup_path_connections(self):
        """设置路径规划信号连接"""
        if self.path_enhancer:
            # 连接路径规划信号
            self.path_enhancer.path_progress_updated.connect(self.path_progress_updated.emit)
            self.path_enhancer.target_reached.connect(self.path_target_reached.emit)
            self.path_enhancer.path_completed.connect(self.path_completed.emit)
            self.path_enhancer.navigation_updated.connect(self.navigation_info_updated.emit)
            print("🗺️ 路径规划信号连接完成")

    def setup_analyzers(self):

        self.tangential_analyzer = None

    # 🆕 新增idle状态分析函数
    def analyze_idle_factors(self, pressure_data, is_sliding, is_tangential, current_cop, previous_cop=None):
        """分析导致idle状态的具体因素"""
        idle_analysis = {
            'is_idle': False,
            'factors': {},
            'thresholds': {},
            'values': {},
            'reasons': []
        }
        
        # 设置阈值
        idle_analysis['thresholds'] = {
            'pressure_threshold': self.pressure_threshold,
            'contact_area_threshold': self.contact_area_threshold,
            'sliding_threshold': self.sliding_threshold,
            'gradient_threshold': self.gradient_threshold
        }
        
        # 检查接触检测
        if pressure_data is not None and pressure_data.size > 0:
            max_pressure = np.max(pressure_data)
            contact_mask = pressure_data > self.pressure_threshold
            contact_area = np.sum(contact_mask)
            
            idle_analysis['values']['max_pressure'] = max_pressure
            idle_analysis['values']['contact_area'] = contact_area
            
            # 检查压力阈值
            if max_pressure < self.pressure_threshold:
                idle_analysis['factors']['pressure_too_low'] = True
                idle_analysis['reasons'].append(f"压力过低: {max_pressure:.4f} < {self.pressure_threshold}")
            else:
                idle_analysis['factors']['pressure_too_low'] = False
            
            # 检查接触面积
            if contact_area < self.contact_area_threshold:
                idle_analysis['factors']['area_too_small'] = True
                idle_analysis['reasons'].append(f"接触面积过小: {contact_area} < {self.contact_area_threshold}")
            else:
                idle_analysis['factors']['area_too_small'] = False
            
            # 计算压力梯度
            grad_x, grad_y = np.gradient(pressure_data)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            grad_mean = np.mean(grad_magnitude)
            idle_analysis['values']['gradient_mean'] = grad_mean
            
            # 检查梯度阈值
            if grad_mean >= self.gradient_threshold:
                idle_analysis['factors']['gradient_too_high'] = True
                idle_analysis['reasons'].append(f"压力梯度过高: {grad_mean:.6f} >= {self.gradient_threshold}")
            else:
                idle_analysis['factors']['gradient_too_high'] = False
        else:
            idle_analysis['factors']['no_pressure_data'] = True
            idle_analysis['reasons'].append("无压力数据")
        
        # 检查滑动状态
        idle_analysis['factors']['is_sliding'] = is_sliding
        if is_sliding:
            idle_analysis['reasons'].append("检测到滑动")
        
        # 检查切向力状态
        idle_analysis['factors']['is_tangential'] = is_tangential
        if is_tangential:
            idle_analysis['reasons'].append("检测到切向力")
        
        # 检查COP位移
        if previous_cop is not None and current_cop is not None:
            displacement = np.sqrt(
                (current_cop[0] - previous_cop[0])**2 + 
                (current_cop[1] - previous_cop[1])**2
            )
            idle_analysis['values']['cop_displacement'] = displacement
            
            if displacement > self.sliding_threshold:
                idle_analysis['factors']['cop_displacement_too_large'] = True
                idle_analysis['reasons'].append(f"COP位移过大: {displacement:.3f} > {self.sliding_threshold}")
            else:
                idle_analysis['factors']['cop_displacement_too_large'] = False
        else:
            idle_analysis['values']['cop_displacement'] = 0.0
            idle_analysis['factors']['cop_displacement_too_large'] = False
        
        # 判断是否为idle状态
        is_idle = (
            not idle_analysis['factors'].get('pressure_too_low', False) and
            not idle_analysis['factors'].get('area_too_small', False) and
            not idle_analysis['factors'].get('gradient_too_high', False) and
            not idle_analysis['factors'].get('is_sliding', False) and
            not idle_analysis['factors'].get('is_tangential', False) and
            not idle_analysis['factors'].get('cop_displacement_too_large', False) and
            not idle_analysis['factors'].get('no_pressure_data', False)
        )
        
        # 🆕 添加时间稳定性检查
        self.idle_stability_history.append(is_idle)
        
        # 计算连续idle帧数
        if is_idle:
            self.consecutive_idle_frames += 1
        else:
            self.consecutive_idle_frames = 0
        
        # 只有连续稳定才判定为真正的idle状态
        final_is_idle = (self.consecutive_idle_frames >= self.idle_stability_frames)
        
        idle_analysis['is_idle'] = final_is_idle
        idle_analysis['consecutive_idle_frames'] = self.consecutive_idle_frames
        idle_analysis['stability_threshold'] = self.idle_stability_frames
        
        if final_is_idle:
            idle_analysis['reasons'].append(f"连续{self.consecutive_idle_frames}帧稳定，判定为idle状态")
        elif is_idle:
            idle_analysis['reasons'].append(f"当前帧满足idle条件，但需要连续{self.idle_stability_frames}帧稳定")
        else:
            idle_analysis['reasons'].append("当前帧不满足idle条件")
        
        # 🐛 调试输出：IDLE分析结果
        print(f"🔍 IDLE分析: 状态={'✅ Idle' if final_is_idle else '❌ 非Idle'}, 连续帧={self.consecutive_idle_frames}/{self.idle_stability_frames}, 原因数量={len(idle_analysis['reasons'])}")
        if idle_analysis['reasons']:
            print(f"   原因: {idle_analysis['reasons'][:2]}...")  # 只显示前2个原因
        
        return idle_analysis

    def process_pressure_data(self, pressure_data):
        if pressure_data is None or pressure_data.size == 0:
            return None
        try:
            # 🕐 开始测量数据处理时间
            processing_start_time = time.time()
            
            # 🆕 增加帧计数器
            self.analysis_frame_count += 1
            
            # print(f"🎮 游戏核心: 开始处理压力数据, 形状={pressure_data.shape}")
            
            contact_detected = self.detect_contact(pressure_data)
            current_cop = self.calculate_cop(pressure_data)
            is_sliding, movement_distance = self.detect_sliding(current_cop)
            
            print(f"🎮 游戏核心: 基础检测完成 - 接触={contact_detected}, 滑动={is_sliding}, COP={current_cop}")
            
            # 🎯 简化：只使用COP，完全跳过切向力分析
            consensus_angle = None
            consensus_confidence = 0.0
            analysis_results = {}  # 空的分析结果
            
            # 特殊idle判定：仅按压无切向/滑动且梯度低于阈值
            previous_cop = self.current_cop  # 保存前一帧的COP
            if contact_detected and is_special_idle_case(
                pressure_data, is_sliding, self.is_tangential, 
                gradient_threshold=self.gradient_threshold,
                previous_cop=previous_cop, current_cop=current_cop,
                sliding_threshold=self.sliding_threshold
            ):
                contact_detected = False

            # 🆕 只在启用IDLE检测时进行分析
            idle_analysis = None
            if self.enable_idle_detection:
                print(f"🎮 游戏核心: 准备调用IDLE分析函数...")
                
                # 🆕 分析idle状态因素
                idle_analysis = self.analyze_idle_factors(
                    pressure_data, is_sliding, self.is_tangential, 
                    current_cop, previous_cop
                )
                
                print(f"🎮 游戏核心: IDLE分析完成, 结果={'✅ Idle' if idle_analysis.get('is_idle', False) else '❌ 非Idle'}")
            else:
                print(f"🎮 游戏核心: IDLE检测已禁用，跳过分析")

            self.update_game_state(
                contact_detected, current_cop, is_sliding,
                movement_distance, consensus_angle, consensus_confidence,
                idle_analysis  # 🆕 传递idle分析结果
            )
            
            # �� 更新数据桥接器 - 传递idle分析结果
            if hasattr(self, 'data_bridge') and self.data_bridge:
                print(f"🎮 游戏核心: 准备发送IDLE分析到数据桥接器...")
                # 不传递分析结果，只传递COP信息
                if consensus_angle is not None:
                    self.data_bridge.set_consensus_angle(consensus_angle, consensus_confidence)
                # 🆕 传递idle分析结果（仅在启用时）
                if self.enable_idle_detection and idle_analysis:
                    self.data_bridge.set_idle_analysis(idle_analysis)
                    print(f"🎮 游戏核心: IDLE分析已发送到数据桥接器")
                else:
                    print(f"🎮 游戏核心: IDLE检测已禁用，不发送分析结果")
            else:
                print(f"❌ 游戏核心: 数据桥接器不可用")
            
            # 🕐 计算数据处理时间
            processing_time = (time.time() - processing_start_time) * 1000  # 转换为毫秒
            print(f"⏱️ 数据处理时间: {processing_time:.2f}ms (帧 {self.analysis_frame_count})")
            
            return {
                'contact_detected': contact_detected,
                'current_cop': current_cop,
                'is_sliding': is_sliding,
                'movement_distance': movement_distance,
                'consensus_angle': consensus_angle,
                'consensus_confidence': consensus_confidence,
                'analysis_results': analysis_results,
                'frame_count': self.analysis_frame_count,
                'system_mode': 'cop_only',  # 标记为仅使用COP模式
                'idle_analysis': idle_analysis,  # 🆕 包含idle分析结果
                'processing_time_ms': processing_time  # 🕐 添加处理时间
            }
        except Exception as e:
            print(f"❌ 压力数据处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def detect_contact(self, pressure_data):
        """检测接触状态 - 改进版，支持更灵活的阈值调整"""
        if pressure_data is None or pressure_data.size == 0:
            return False
        
        # 计算压力统计信息
        max_pressure = np.max(pressure_data)
        mean_pressure = np.mean(pressure_data)
        
        # 检查压力阈值
        if max_pressure < self.pressure_threshold:
            # 🐛 调试输出：压力过低
            if max_pressure > 0.001:  # 只在有一定压力时输出，避免过多日志
                print(f"🔍 接触检测: 压力过低 - 最大压力={max_pressure:.6f}, 阈值={self.pressure_threshold:.6f}")
            return False
        
        # 创建接触掩码
        contact_mask = pressure_data > self.pressure_threshold
        contact_area = np.sum(contact_mask)
        
        # 检查接触面积
        if contact_area < self.contact_area_threshold:
            # 🐛 调试输出：接触面积过小
            print(f"🔍 接触检测: 面积过小 - 接触面积={contact_area}, 阈值={self.contact_area_threshold}")
            return False
        
        # 🐛 调试输出：接触检测成功
        print(f"✅ 接触检测成功: 最大压力={max_pressure:.6f}, 平均压力={mean_pressure:.6f}, 接触面积={contact_area}")
        
        return True

    def calculate_cop(self, pressure_data):
        if pressure_data is None or pressure_data.size == 0:
            return None
        valid_mask = pressure_data > self.pressure_threshold
        if not np.any(valid_mask):
            return None
        rows, cols = pressure_data.shape
        y_indices, x_indices = np.mgrid[0:rows, 0:cols]
        total_pressure = np.sum(pressure_data[valid_mask])
        if total_pressure == 0:
            return None
        cop_x = np.sum(x_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
        cop_y = np.sum(y_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
        return (cop_x, cop_y)

    def detect_sliding(self, current_cop):
        if current_cop is None:
            return False, 0.0
        if self.initial_cop is None:
            self.initial_cop = current_cop
            return False, 0.0
        dx = current_cop[0] - self.initial_cop[0]
        dy = current_cop[1] - self.initial_cop[1]
        movement_distance = np.sqrt(dx*dx + dy*dy)
        is_sliding = movement_distance > self.sliding_threshold
        
        # 🐛 调试输出：滑动检测信息
        if movement_distance > 0.01:  # 只在有移动时输出
            print(f"🖱️ 滑动检测: 距离={movement_distance:.3f}, 阈值={self.sliding_threshold:.3f}, 是否滑动={is_sliding}")
            print(f"   COP: 初始=({self.initial_cop[0]:.2f}, {self.initial_cop[1]:.2f}), 当前=({current_cop[0]:.2f}, {current_cop[1]:.2f})")
        
        return is_sliding, movement_distance

    def calculate_comprehensive_consensus(self, analysis_results):
        try:
            grad_weights = {
                'global_weighted_average': 0.6,
                'weighted_min_variance': 0.55,
                'weighted_asymmetry': 0.7,
                'cop_weighted_gradient': 0.65,
                'peak_window_weighted': 0.5,
                'weighted_hessian': 0.45,
                'weighted_grid_analysis': 0.6,
                'weighted_axial_asymmetry': 0.65,
                'cop_window_weighted_asymmetry': 0.7,
                'basic_gradient': 0.3,
            }
            shape_weights = {
                'gabor_filter': 0.85,
                'shape_moments': 0.8,
                'covariance_analysis': 0.95,
                'multiscale_analysis': 0.9,
                'fourier_direction': 0.75,
                'gradient_guided': 0.88
            }
            valid_results = []
            for method, result in analysis_results.items():
                if isinstance(result, dict) and result.get('angle') is not None:
                    confidence = result.get('confidence', 0.0)
                    if confidence > 0.1:
                        if method in grad_weights:
                            weight = grad_weights.get(method, 0.5) * confidence
                        else:
                            weight = shape_weights.get(method, 0.5) * confidence
                        valid_results.append({
                            'angle': result['angle'],
                            'weight': weight,
                            'method': method,
                            'confidence': confidence
                        })
            if len(valid_results) < 1:
                return None, 0.0
            total_weight = sum(r['weight'] for r in valid_results)
            if total_weight <= 0:
                return None, 0.0
            cos_sum = sum(r['weight'] * np.cos(np.radians(r['angle'])) for r in valid_results)
            sin_sum = sum(r['weight'] * np.sin(np.radians(r['angle'])) for r in valid_results)
            consensus_angle = np.degrees(np.arctan2(sin_sum, cos_sum)) % 360
            consensus_strength = np.sqrt(cos_sum**2 + sin_sum**2) / total_weight
            final_confidence = min(1.0, consensus_strength)
            self.consensus_history.append(consensus_angle)
            self.confidence_history.append(final_confidence)
            return consensus_angle, final_confidence
        except Exception as e:
            print(f"❌ 共识角度计算失败: {e}")
            return None, 0.0

    def update_game_state(self, contact_detected, current_cop, is_sliding,
                         movement_distance, consensus_angle, consensus_confidence,
                         idle_analysis):
        self.is_contact = contact_detected
        self.current_cop = current_cop
        self.is_sliding = is_sliding
        self.movement_distance = movement_distance
        if hasattr(self, 'data_bridge') and self.data_bridge:
            self.data_bridge.last_movement_distance = movement_distance
            if consensus_angle is not None:
                self.data_bridge.set_consensus_angle(consensus_angle, consensus_confidence)
            # 🆕 传递idle分析结果
            self.data_bridge.set_idle_analysis(idle_analysis)
        self.is_tangential = contact_detected and not is_sliding
        
        # 🎮 使用智能控制系统计算目标位置
        target_position = self.smart_control.calculate_target_position(
            contact_detected, current_cop, self.initial_cop,
            self.box_position, self.box_original_position
        )
        
        # 🎯 应用边界限制
        target_position[0] = np.clip(target_position[0], self.box_size/2, 64 - self.box_size/2)
        target_position[1] = np.clip(target_position[1], self.box_size/2, 64 - self.box_size/2)
        self.box_target_position = target_position
        
        # 🔄 处理接触状态变化
        if not contact_detected:
            if self.is_contact:  # 如果之前有接触，现在没有接触，说明接触结束
                self.smart_control.reset_on_contact_end()  # 重置累积位移
            self.initial_cop = None
        elif contact_detected and self.initial_cop is None and current_cop is not None:
            # 刚开始接触时，记录初始COP
            self.initial_cop = current_cop
        
        # 📊 获取控制系统信息
        control_info = self.smart_control.get_control_info()
        
        state_info = {
            'is_contact': self.is_contact,
            'current_cop': self.current_cop,
            'initial_cop': self.initial_cop,
            'movement_distance': self.movement_distance,
            'consensus_angle': consensus_angle,
            'consensus_confidence': consensus_confidence,
            'box_position': self.box_position.copy(),
            'box_target_position': self.box_target_position.copy(),
            'frame_count': self.analysis_frame_count,
            # 🎮 控制系统状态信息
            'control_mode': control_info['mode'],
            'control_velocity': control_info['velocity'],
            'control_displacement': control_info['displacement'],
            'joystick_threshold': control_info['joystick_threshold'],
            'touchpad_threshold': control_info['touchpad_threshold'],
            # 🆕 IDLE分析结果
            'idle_analysis': idle_analysis,
            # 🆕 添加帧率信息
            'frame_rate': 1000 / FrameRateConfig.get_interval_ms("core_fps")
        }
        self.game_state_changed.emit(state_info)
        self.analysis_frame_count += 1

    def update_physics(self):
        """🎯 更新箱子位置朝向目标位置"""
        print(f"⚙️ update_physics被调用 (帧 {self.analysis_frame_count})")
        
        # 🕐 开始测量物理更新时间
        physics_start_time = time.time()
        
        # 检查路径规划是否启用
        if self.path_enhancer and self.path_enhancer.is_path_mode_enabled:
            # 🗺️ 路径模式：只更新路径进度，不覆盖用户控制
            # 路径规划只提供导航信息，不直接控制箱子移动
            self.path_enhancer.update_box_position(self.box_position)
            
            # 🎯 路径模式下的目标位置仍然由智能控制系统决定（用户手指控制）
            # 不覆盖 box_target_position，保持用户控制
            movement_factor = 0.15
        else:
            # 🎮 自由控制模式：使用原有逻辑
            movement_factor = 0.15
        
        # 🎯 更新箱子位置朝向目标位置（由用户手指控制决定）
        old_position = self.box_position.copy()
        self.box_position[0] += (self.box_target_position[0] - self.box_position[0]) * movement_factor
        self.box_position[1] += (self.box_target_position[1] - self.box_position[1]) * movement_factor
        
        # 📦 确保箱子在游戏区域内
        self.box_position[0] = np.clip(self.box_position[0], 5, 59)
        self.box_position[1] = np.clip(self.box_position[1], 5, 59)
        
        # 🔍 调试：检查位置是否变化
        position_changed = not np.allclose(old_position, self.box_position)
        if position_changed:
            print(f"📦 箱子位置已更新: {old_position} → {self.box_position}")
        else:
            print(f"📦 箱子位置未变化: {self.box_position} (目标: {self.box_target_position})")
        
        # 📡 发送状态更新
        box_state = {
            'position': self.box_position.copy(),
            'target_position': self.box_target_position.copy(),
            'control_mode': self.smart_control.current_mode,
            'path_enabled': self.path_enhancer.is_path_mode_enabled if self.path_enhancer else False
        }
        self.box_state_updated.emit(box_state)
        
        # 🕐 计算物理更新时间
        physics_time = (time.time() - physics_start_time) * 1000  # 转换为毫秒
        print(f"⚙️ 物理更新时间: {physics_time:.2f}ms (帧 {self.analysis_frame_count})")
        
        # 📊 通过数据桥接器发送物理更新时间
        if hasattr(self, 'data_bridge') and self.data_bridge:
            self.data_bridge.set_physics_time(physics_time)

    def reset_game(self):
        self.box_position = self.box_original_position.copy()
        self.box_target_position = self.box_original_position.copy()
        self.is_contact = False
        self.is_tangential = False
        self.is_sliding = False
        self.current_cop = None
        self.initial_cop = None
        self.movement_distance = 0.0
        self.consensus_history.clear()
        self.confidence_history.clear()
        self.analysis_frame_count = 0
        
        # 🎮 重置智能控制系统
        self.smart_control.reset()
        
        # 🗺️ 重置路径规划系统
        if self.path_enhancer:
            self.path_enhancer.reset_path()
        
        print("🔄 游戏状态已重置（含智能控制系统）")

    def update_parameters(self, params):
        """更新游戏参数"""
        # 更新基本参数
        if 'pressure_threshold' in params:
            self.pressure_threshold = params['pressure_threshold']
        if 'sliding_threshold' in params:
            self.sliding_threshold = params['sliding_threshold']
        if 'contact_area_threshold' in params:
            self.contact_area_threshold = params['contact_area_threshold']
        if 'gradient_threshold' in params:
            self.gradient_threshold = params['gradient_threshold']
        
        # 🆕 更新IDLE检测开关
        if 'enable_idle_detection' in params:
            self.enable_idle_detection = params['enable_idle_detection']
            print(f"🔍 IDLE检测开关: {'启用' if self.enable_idle_detection else '禁用'}")
        
        # 🎮 更新智能控制系统参数
        if self.smart_control:
            self.smart_control.update_parameters(params)

        print(f"🎮 游戏参数已更新: {list(params.keys())}")

    def set_contact_detection_thresholds(self, pressure_threshold=None, contact_area_threshold=None):
        """设置接触检测阈值 - 专门用于调整接触检测灵敏度"""
        if pressure_threshold is not None:
            old_threshold = self.pressure_threshold
            self.pressure_threshold = pressure_threshold
            print(f"🔍 压力阈值已调整: {old_threshold:.6f} -> {pressure_threshold:.6f}")
        
        if contact_area_threshold is not None:
            old_area_threshold = self.contact_area_threshold
            self.contact_area_threshold = contact_area_threshold
            print(f"🔍 接触面积阈值已调整: {old_area_threshold} -> {contact_area_threshold}")
        
        # 输出当前阈值状态
        print(f"🔍 当前接触检测阈值: 压力={self.pressure_threshold:.6f}, 面积={self.contact_area_threshold}")
        
        # 提供阈值调整建议
        if self.pressure_threshold < 0.002:
            print("💡 提示: 压力阈值较低，接触检测更敏感，但可能产生误判")
        elif self.pressure_threshold > 0.008:
            print("💡 提示: 压力阈值较高，接触检测更稳定，但可能错过轻微接触")
        else:
            print("💡 提示: 压力阈值适中，平衡了敏感度和稳定性")
    
    def get_contact_detection_info(self):
        """获取接触检测的详细信息"""
        return {
            'pressure_threshold': self.pressure_threshold,
            'contact_area_threshold': self.contact_area_threshold,
            'sliding_threshold': self.sliding_threshold,
            'gradient_threshold': self.gradient_threshold,
            'enable_idle_detection': self.enable_idle_detection
        }
    
    def test_contact_sensitivity(self, test_pressure_data):
        """测试接触检测灵敏度"""
        if test_pressure_data is None:
            print("❌ 测试数据为空")
            return None
        
        # 保存原始阈值
        original_pressure_threshold = self.pressure_threshold
        original_area_threshold = self.contact_area_threshold
        
        test_results = []
        
        # 测试不同的压力阈值
        test_pressure_thresholds = [0.001, 0.002, 0.003, 0.005, 0.008, 0.01]
        for threshold in test_pressure_thresholds:
            self.pressure_threshold = threshold
            contact_detected = self.detect_contact(test_pressure_data)
            max_pressure = np.max(test_pressure_data)
            contact_mask = test_pressure_data > threshold
            contact_area = np.sum(contact_mask)
            
            test_results.append({
                'pressure_threshold': threshold,
                'contact_detected': contact_detected,
                'max_pressure': max_pressure,
                'contact_area': contact_area,
                'sensitivity': 'high' if threshold <= 0.002 else 'medium' if threshold <= 0.005 else 'low'
            })
        
        # 恢复原始阈值
        self.pressure_threshold = original_pressure_threshold
        self.contact_area_threshold = original_area_threshold
        
        # 输出测试结果
        print("\n🔍 接触检测灵敏度测试结果:")
        print("阈值\t检测\t最大压力\t接触面积\t灵敏度")
        print("-" * 50)
        for result in test_results:
            status = "✅" if result['contact_detected'] else "❌"
            print(f"{result['pressure_threshold']:.3f}\t{status}\t{result['max_pressure']:.6f}\t{result['contact_area']}\t{result['sensitivity']}")
        
        return test_results

    def start_update_loop(self):
        try:
            interval_ms = FrameRateConfig.get_interval_ms("core_fps")
            self.update_timer.start(interval_ms)
            current_fps = 1000 / interval_ms
            print(f"🎮 游戏核心引擎启动，帧率: {current_fps:.1f} FPS")
            self.game_state_changed.emit({
                'status': f'游戏引擎运行中 ({current_fps:.1f} FPS)',
                'frame_rate': current_fps,
                'performance_mode': FrameRateConfig.current_mode
            })
        except Exception as e:
            print(f"❌ 游戏引擎启动失败: {e}")

    def stop_update_loop(self):
        self.update_timer.stop()
        print("🛑 游戏核心引擎已停止")
        self.game_state_changed.emit({'status': '游戏引擎已停止'})

    def update_frame_rate(self):
        try:
            interval_ms = FrameRateConfig.get_interval_ms("core_fps")
            self.update_timer.setInterval(interval_ms)
            current_fps = 1000 / interval_ms
            print(f"🎮 游戏核心帧率已更新: {current_fps:.1f} FPS")
            self.game_state_changed.emit({
                'status': f'游戏引擎运行中 ({current_fps:.1f} FPS)',
                'frame_rate': current_fps,
                'performance_mode': FrameRateConfig.current_mode
            })
        except Exception as e:
            print(f"❌ 游戏核心帧率更新失败: {e}")

    def set_data_bridge(self, data_bridge):
        self.data_bridge = data_bridge
        print("🌉 数据桥接器已连接到游戏核心 (高性能优化版)")

    def enable_path_mode(self, path_name: str) -> bool:
        """启用路径模式"""
        if self.path_enhancer:
            result = self.path_enhancer.enable_path_mode(path_name)
            if result:
                # 🗺️ 路径模式只提供导航信息，不自动控制箱子移动
                # 箱子移动仍然由用户的手指控制决定
                print(f"🗺️ 路径模式已启用: {path_name}")
                print(f"📍 当前路径信息: {self.path_enhancer.get_current_navigation_info()}")
                print("💡 提示：路径模式提供导航指引，箱子移动仍由手指控制")
                return result
        return False

    def disable_path_mode(self):
        """禁用路径模式"""
        if self.path_enhancer:
            self.path_enhancer.disable_path_mode()
            print("🛑 路径模式已禁用")

    def reset_path_progress(self):
        """重置当前路径进度"""
        if self.path_enhancer:
            self.path_enhancer.reset_current_path()
            print("🔄 路径进度已重置")

    def get_available_paths(self):
        """获取可用路径列表"""
        if self.path_enhancer:
            return self.path_enhancer.get_available_paths()
        return []

    def create_custom_path(self, name: str, points: list) -> bool:
        """创建自定义路径"""
        if self.path_enhancer:
            return self.path_enhancer.create_custom_path(name, points)
        return False

    def get_path_info(self):
        """获取当前路径信息"""
        if self.path_enhancer:
            return self.path_enhancer.get_current_navigation_info()
        return {'has_path': False, 'is_enabled': False}

    def get_completion_stats(self):
        """获取路径完成统计"""
        if self.path_enhancer:
            return self.path_enhancer.get_completion_stats()
        return {} 

    def handle_mouse_input(self, game_x, game_y):
        """处理鼠标输入"""
        try:
            # 将鼠标坐标转换为游戏坐标
            # 确保坐标在游戏区域内
            game_x = np.clip(game_x, 0, self.game_width)
            game_y = np.clip(game_y, 0, self.game_height)
            
            # 更新箱子目标位置
            self.box_target_position = np.array([game_x, game_y])
            
            print(f"🖱️ 鼠标输入处理: 坐标({game_x:.1f}, {game_y:.1f})")
            
        except Exception as e:
            print(f"❌ 鼠标输入处理失败: {e}")


class BoxGameMainWindow(QMainWindow):
    """推箱子游戏主窗口（高性能优化版）"""
    
    def __init__(self):
        super().__init__()
        self.game_core = None
        self.sensor_thread = None
        self.renderer = None
        self.control_panel = None
        
        # 🆕 新增IDLE弹窗管理
        self.idle_dialog = None
        
        # 🆕 新增帧率监控
        self.fps_monitor_timer = QTimer()
        self.fps_monitor_timer.timeout.connect(self.update_actual_fps)
        self.fps_monitor_timer.start(1000)  # 每秒更新一次
        self.last_frame_count = 0
        self.current_actual_fps = 0.0
        
        # 🕐 新增性能监控器
        self.performance_monitor = PerformanceMonitor()
        print("📊 性能监控器已初始化")
        
        # 🎨 应用深色主题
        if UTILS_AVAILABLE:
            apply_dark_theme(self)
            print("🎨 主窗口已应用深色主题")
        else:
            print("⚠️ utils不可用，使用默认主题")
        
        # 检查传感器接口可用性
        if not SENSOR_INTERFACES_AVAILABLE:
            print("❌ 传感器接口不可用，无法启动游戏")
            return
        
        self.init_ui()
        self.init_components()
        self.connect_signals()
        
        # 🚀 强制设置高性能模式
        self.set_performance_mode("高性能")
        
        self.update_initial_status()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("推箱子游戏")
        self.setGeometry(100, 100, 1400, 900)
        
        # 确保窗口有正常的边框和标题栏
        self.setWindowFlags(Qt.Window)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "utils", "tujian.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            print(f"✅ 窗口图标已设置: {icon_path}")
        else:
            print(f"⚠️ 未找到图标文件: {icon_path}")
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局 - 改为垂直布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建控制面板（顶部）
        try:
            from interfaces.ordinary.BoxGame.box_game_control_panel import BoxGameControlPanel
            self.control_panel = BoxGameControlPanel()
            main_layout.addWidget(self.control_panel)
            print("✅ 控制面板已创建")
        except ImportError as e:
            print(f"❌ 无法创建控制面板: {e}")
            self.control_panel = None
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: none;
                height: 2px;
                margin: 5px 0px;
            }
        """)
        main_layout.addWidget(separator)
        
        # 创建游戏渲染器（底部，占据剩余空间）
        try:
            from interfaces.ordinary.BoxGame.box_game_renderer import BoxGameRenderer
            self.renderer = BoxGameRenderer()
            main_layout.addWidget(self.renderer)
            print("✅ 游戏渲染器已创建")
        except ImportError as e:
            print(f"❌ 无法创建游戏渲染器: {e}")
            self.renderer = None
        
        # 设置布局比例 - 控制面板占20%，渲染器占80%
        main_layout.setStretch(0, 1)  # 控制面板
        main_layout.setStretch(1, 0)  # 分隔线（不拉伸）
        main_layout.setStretch(2, 4)  # 渲染器
        
    def init_components(self):
        """初始化游戏组件"""
        # 创建游戏核心
        self.game_core = BoxGameCoreOptimized()
        
        # 创建传感器线程 - 使用从run_box_game_optimized.py导入的类
        self.sensor_thread = SensorDataThread()
        
        # 连接数据桥接器
        self.data_bridge = BoxGameDataBridgeOptimized()
        self.game_core.set_data_bridge(self.data_bridge)
        
        # 🗺️ 初始化路径列表
        self.init_path_list()
        
    def init_path_list(self):
        """初始化路径列表"""
        if self.control_panel:
            available_paths = self.game_core.get_available_paths()
            self.control_panel.set_path_list(available_paths)
            print(f"🗺️ 初始化路径列表: {available_paths}")

    def connect_signals(self):
        """连接信号和槽"""
        # 传感器数据
        self.sensor_thread.data_received.connect(self.on_sensor_data_received)
        self.sensor_thread.status_changed.connect(self.on_sensor_status_changed)
        
        # 游戏核心信号
        self.game_core.game_state_changed.connect(self.on_game_state_changed)
        self.game_core.analysis_completed.connect(self.on_analysis_completed)
        
        # 渲染器信号
        if self.renderer:
            self.renderer.mouse_pressed.connect(self.on_renderer_mouse_pressed)
        
        # 控制面板信号
        if self.control_panel:
            self.control_panel.parameter_changed.connect(self.on_parameter_changed)
            self.control_panel.visualization_changed.connect(self.on_visualization_changed)
            # 🔌 添加传感器控制信号连接
            self.control_panel.sensor_connect_requested.connect(self.connect_sensor)
            self.control_panel.sensor_disconnect_requested.connect(self.disconnect_sensor)
            self.control_panel.data_stop_requested.connect(self.stop_data_collection)
            # 🗺️ 添加路径规划信号连接
            self.control_panel.path_mode_requested.connect(self.on_path_mode_requested)
            self.control_panel.path_reset_requested.connect(self.on_path_reset_requested)
        
        # 🆕 数据桥接器到渲染器的连接 - 修复压力数据显示
        if self.renderer:
            self.data_bridge.pressure_data_updated.connect(self.renderer.update_pressure_data)
            self.data_bridge.analysis_results_updated.connect(self.renderer.update_analysis_results)
            self.data_bridge.consensus_angle_updated.connect(self.renderer.update_consensus_angle)
            # 🆕 添加idle分析信号连接
            self.data_bridge.idle_analysis_updated.connect(self.on_idle_analysis_updated)
            # 🕐 添加物理时间信号连接
            self.data_bridge.physics_time_updated.connect(self.on_physics_time_updated)
        
        # 游戏核心到渲染器的连接
        if self.renderer:
            self.game_core.game_state_changed.connect(self.renderer.update_game_state)
            self.game_core.analysis_completed.connect(self.renderer.update_analysis_results)
        
        # 路径规划信号
        if PATH_PLANNING_AVAILABLE and self.renderer:
            self.game_core.navigation_info_updated.connect(self.renderer.update_navigation_info)
        
    def update_initial_status(self):
        """更新初始状态 - 只显示渲染帧率"""
        print("🎮 游戏已启动，等待连接传感器...")
        print("💡 提示：连接传感器后将自动开始数据采集")
        print("💡 提示：请确保传感器已正确连接并具有访问权限")
        
        # 🎨 只设置渲染帧率初始状态
        if self.control_panel:
            self.control_panel.update_status('renderer_fps', 0.0)
        
        # 📊 显示性能监控说明
        print("\n" + "="*50)
        print("📊 性能监控功能已启用")
        print("="*50)
        print("⏱️ 自动监控项目:")
        print("  - 数据处理时间 (压力数据分析)")
        print("  - 渲染时间 (图像更新)")
        print("  - 物理更新时间 (游戏逻辑)")
        print("  - 总处理时间")
        print("\n⌨️ 快捷键:")
        print("  P - 显示性能汇总")
        print("  R - 重置性能统计")
        print("  F - 显示帧率配置")
        print("  G - 强制刷新渲染器")
        print("  T - 测试渲染器性能")
        print("  H - 显示帮助信息")
        print("="*50)
        
        # 🕐 显示当前帧率配置
        self.show_current_frame_rate_config()
    
    def update_actual_fps(self):
        """更新实际帧率显示 - 只更新渲染帧率"""
        try:
            # 🎨 只获取渲染器的实际帧率并更新到控制面板
            if self.renderer:
                renderer_stats = self.renderer.get_performance_stats()
                renderer_fps = renderer_stats.get('current_fps', 0)
                
                # 更新控制面板的渲染器帧率显示
                if self.control_panel:
                    self.control_panel.update_status('renderer_fps', renderer_fps)
                
                if renderer_fps > 0:
                    print(f"🎨 渲染器实际帧率: {renderer_fps:.1f} FPS")
                    
        except Exception as e:
            print(f"❌ 更新渲染帧率失败: {str(e)}")
    
    def connect_sensor(self, port="0"):
        """连接传感器"""
        try:
            print(f"🔌 正在连接传感器: 端口={port}")
            
            # 更新连接状态
            self.control_panel.update_connection_status("连接中...", connected=False)
            
            # 连接传感器 - 始终使用真实传感器
            success = self.sensor_thread.connect_sensor(port, use_real=True)
            
            if success:
                status_msg = f"传感器已连接 (端口: {port})"
                print(f"✅ {status_msg}")
                self.control_panel.update_connection_status(status_msg, connected=True)
                
                # 🚀 连接成功后立即开始数据采集
                print("🚀 连接成功，立即开始数据采集...")
                self.start_data_collection()
                
            else:
                error_msg = f"传感器连接失败 (端口: {port})"
                print(f"❌ {error_msg}")
                self.control_panel.update_connection_status(error_msg, connected=False)
                
        except Exception as e:
            print(f"❌ 连接错误: {str(e)}")
            self.control_panel.update_connection_status(f"连接错误: {str(e)}", connected=False)
    
    def disconnect_sensor(self):
        """断开传感器"""
        try:
            print("🔌 正在断开传感器...")
            
            # 先停止数据采集
            self.stop_data_collection()
            
            # 断开传感器连接
            self.sensor_thread.disconnect_sensor()
            
            print("✅ 传感器断开完成")
            self.control_panel.update_connection_status("传感器已断开", connected=False)
            
        except Exception as e:
            print(f"❌ 断开错误: {str(e)}")
            self.control_panel.update_connection_status(f"断开错误: {str(e)}", connected=False)
    
    def get_available_sensor_ports(self):
        """获取可用传感器端口"""
        try:
            ports = self.sensor_thread.get_available_ports()
            print(f"📡 可用端口: {ports}")
            return ports
        except Exception as e:
            print(f"❌ 获取端口失败: {str(e)}")
            return []
    
    def test_sensor_connection(self):
        """测试传感器连接"""
        try:
            if self.sensor_thread.is_sensor_connected():
                print("✅ 传感器连接正常")
            else:
                print("❌ 传感器未连接")
        except Exception as e:
            print(f"❌ 测试连接失败: {str(e)}")
    
    def start_data_collection(self):
        """开始数据采集"""
        try:
            # 🚀 直接开始数据采集，不再检查传感器连接状态
            # 因为现在只有在连接成功后才会调用此方法
            self.sensor_thread.start_reading()
            self.game_core.start_update_loop()
            
            # 🎨 启动渲染循环
            if self.renderer:
                self.renderer.start_rendering()
            
            print("✅ 数据采集已开始")
            self.control_panel.update_connection_status("数据采集中...", connected=True, collecting=True)
            
            return True
        except Exception as e:
            print(f"❌ 开始数据采集失败: {str(e)}")
            return False
    
    def stop_data_collection(self):
        """停止数据采集"""
        try:
            self.sensor_thread.stop_reading()
            self.game_core.stop_update_loop()
            
            # 🎨 停止渲染循环
            if self.renderer:
                self.renderer.stop_rendering()
            
            print("✅ 数据采集已停止")
            self.control_panel.update_connection_status("已连接", connected=True, collecting=False)
        except Exception as e:
            print(f"❌ 停止数据采集失败: {str(e)}")
    
    def set_performance_mode(self, mode="高性能"):
        """设置性能模式 - 默认使用高性能模式"""
        try:
            # 默认使用高性能模式
            if FrameRateConfig.set_performance_mode("高性能"):
                # 更新各个组件的帧率
                self.sensor_thread.update_frame_rate()
                self.game_core.update_frame_rate()
                if self.renderer:
                    self.renderer.update_frame_rate()
                    # 🚀 更新渲染器性能模式
                    self.renderer.set_performance_mode("高性能")
                
                # 🕐 显示当前帧率配置
                config = FrameRateConfig.get_current_config()
                print(f"⚡ 性能模式已设置为: 高性能")
                print(f"📊 当前帧率配置:")
                print(f"  - 传感器采集: {config['sensor_fps']} FPS (间隔: {1000/config['sensor_fps']:.1f}ms)")
                print(f"  - 游戏核心: {config['core_fps']} FPS (间隔: {1000/config['core_fps']:.1f}ms)")
                print(f"  - 渲染器: {config['renderer_fps']} FPS (间隔: {1000/config['renderer_fps']:.1f}ms)")
                print(f"  - 模拟传感器: {config['simulation_fps']} FPS (间隔: {1000/config['simulation_fps']:.1f}ms)")
                
        except Exception as e:
            print(f"❌ 设置性能模式失败: {str(e)}")
    
    def show_current_frame_rate_config(self):
        """显示当前帧率配置"""
        try:
            config = FrameRateConfig.get_current_config()
            print(f"\n📊 当前帧率配置 ({FrameRateConfig.current_mode}模式):")
            print(f"  - 传感器采集: {config['sensor_fps']} FPS (间隔: {1000/config['sensor_fps']:.1f}ms)")
            print(f"  - 游戏核心: {config['core_fps']} FPS (间隔: {1000/config['core_fps']:.1f}ms)")
            print(f"  - 渲染器: {config['renderer_fps']} FPS (间隔: {1000/config['renderer_fps']:.1f}ms)")
            print(f"  - 模拟传感器: {config['simulation_fps']} FPS (间隔: {1000/config['simulation_fps']:.1f}ms)")
            
            # 计算理论最大帧率
            max_fps = min(config['sensor_fps'], config['core_fps'], config['renderer_fps'])
            print(f"🎯 理论最大帧率: {max_fps} FPS")
            
        except Exception as e:
            print(f"❌ 获取帧率配置失败: {str(e)}")
    
    @pyqtSlot(np.ndarray)
    def on_sensor_data_received(self, pressure_data):
        """处理传感器数据"""
        try:
            # 🕐 开始测量总处理时间
            total_start_time = time.time()
            
            # 更新数据桥接器
            self.data_bridge.set_pressure_data(pressure_data)
            
            # 调用游戏核心处理数据
            print("🖥️ 主窗口: 准备调用游戏核心处理压力数据...")
            result = self.game_core.process_pressure_data(pressure_data)
            print(f"🖥️ 主窗口: 游戏核心处理完成, 结果={result}")
            
            # 🕐 测量渲染时间
            render_start_time = time.time()
            
            # 更新渲染器
            if self.renderer:
                self.renderer.update_pressure_data(pressure_data)
            
            # 🕐 计算渲染时间
            render_time = (time.time() - render_start_time) * 1000  # 转换为毫秒
            total_time = (time.time() - total_start_time) * 1000  # 转换为毫秒
            
            # 获取数据处理时间
            processing_time = result.get('processing_time_ms', 0) if result else 0
            
            # 📊 记录到性能监控器
            self.performance_monitor.add_processing_time(processing_time)
            self.performance_monitor.add_render_time(render_time)
            self.performance_monitor.add_total_time(total_time)
            
            print(f"🎨 渲染时间: {render_time:.2f}ms")
            print(f"📊 总处理时间: {total_time:.2f}ms (数据处理: {processing_time:.2f}ms + 渲染: {render_time:.2f}ms)")
            print(f"📈 性能分析 - 帧 {result.get('frame_count', 0) if result else 0}: 处理={processing_time:.2f}ms, 渲染={render_time:.2f}ms, 总计={total_time:.2f}ms")
            
            # 🕐 每100帧打印一次性能汇总
            if self.performance_monitor.frame_count % 100 == 0 and self.performance_monitor.frame_count > 0:
                self.performance_monitor.print_performance_summary()
            
        except Exception as e:
            print(f"❌ 处理传感器数据失败: {str(e)}")
    
    @pyqtSlot(str)
    def on_sensor_status_changed(self, status):
        """处理传感器状态变化"""
        print(f"�� 传感器状态: {status}")
    
    @pyqtSlot(dict)
    def on_game_state_changed(self, state_info):
        """处理游戏状态变化 - 更新渲染器和控制面板"""
        try:
            # 🕐 测量游戏状态更新渲染时间
            state_render_start_time = time.time()
            
            # 更新渲染器
            if self.renderer:
                self.renderer.update_game_state(state_info)
            
            # 🕐 计算游戏状态渲染时间
            state_render_time = (time.time() - state_render_start_time) * 1000  # 转换为毫秒
            
            # 更新数据桥接器
            self.data_bridge.set_analysis_results(state_info)
            
            # 🎮 更新控制面板的控制模式显示
            if self.control_panel:
                control_mode = state_info.get('control_mode', 'unknown')
                self.control_panel.update_status('control_mode', control_mode)
            
            # 获取帧号和处理时间
            frame_count = state_info.get('frame_count', 0)
            processing_time = state_info.get('processing_time_ms', 0)
            
            print(f"🎮 游戏状态: {state_info.get('control_mode', 'unknown')}")
            print(f"🎨 游戏状态渲染时间: {state_render_time:.2f}ms (帧 {frame_count})")
            
            # 如果有处理时间信息，显示完整的性能分析
            if processing_time > 0:
                print(f"📈 完整性能分析 - 帧 {frame_count}: 数据处理={processing_time:.2f}ms, 状态渲染={state_render_time:.2f}ms")
            
        except Exception as e:
            print(f"❌ 处理游戏状态变化失败: {str(e)}")
    
    @pyqtSlot(dict)
    def on_idle_analysis_updated(self, idle_analysis):
        """处理IDLE分析结果"""
        try:
            # 更新数据桥接器
            self.data_bridge.set_idle_analysis(idle_analysis)
            
            # 更新渲染器
            if self.renderer:
                # 将idle分析结果添加到游戏状态中
                state_info = {'idle_analysis': idle_analysis}
                self.renderer.update_game_state(state_info)
            
            # 检查是否需要显示IDLE对话框
            if idle_analysis.get('is_idle', False):
                self.show_idle_dialog()
                
        except Exception as e:
            print(f"❌ 处理IDLE分析失败: {str(e)}")
    
    def show_idle_dialog(self):
        """显示IDLE状态对话框"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("IDLE状态检测")
            msg.setText("检测到IDLE状态")
            msg.setInformativeText("系统检测到当前处于空闲状态，可能需要调整参数或重新校准。")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except Exception as e:
            print(f"❌ 显示IDLE对话框失败: {str(e)}")
    
    def on_idle_threshold_changed(self, threshold_params):
        """处理IDLE阈值变化"""
        try:
            # 更新游戏核心的IDLE检测参数
            self.game_core.update_parameters(threshold_params)
            print(f"🔍 IDLE阈值已更新: {threshold_params}")
        except Exception as e:
            print(f"❌ 更新IDLE阈值失败: {str(e)}")
    
    @pyqtSlot(dict)
    def on_analysis_completed(self, analysis_info):
        """处理分析完成事件"""
        try:
            print(f"📊 分析完成: {analysis_info}")
        except Exception as e:
            print(f"❌ 处理分析完成事件失败: {str(e)}")
    
    @pyqtSlot(float, float)
    def on_renderer_mouse_pressed(self, x, y):
        """渲染器鼠标按下事件"""
        # 将鼠标坐标转换为游戏坐标
        game_x = x * self.game_core.game_width
        game_y = y * self.game_core.game_height
        self.game_core.handle_mouse_input(game_x, game_y)
    
    @pyqtSlot(dict)
    def on_parameter_changed(self, params):
        """处理参数变化"""
        try:
            print(f"⚙️ 参数已更新: {list(params.keys())}")
            
            # 更新游戏核心参数
            self.game_core.update_parameters(params)
            
            # 更新渲染器参数
            if self.renderer:
                # 处理可视化相关参数
                vis_params = {k: v for k, v in params.items() 
                            if k in ['show_trajectory', 'show_analysis_details', 'show_pressure_overlay']}
                if vis_params:
                    self.renderer.set_visualization_options(vis_params)
            
        except Exception as e:
            print(f"❌ 更新参数失败: {str(e)}")
    
    @pyqtSlot(dict)
    def on_visualization_changed(self, options):
        """处理可视化选项变化"""
        if self.renderer:
            # 🎨 处理热力图模式切换
            if 'toggle_heatmap_mode' in options:
                self.renderer.toggle_heatmap_mode()
                print("🎨 热力图模式已切换")
                return
            
            # 🎨 处理3D渲染选项
            if any(key in options for key in ['enable_3d_lighting', 'enable_3d_shadows', 'enable_3d_animation', 
                                            'elevation_3d', 'azimuth_3d', 'rotation_speed_3d', 
                                            'surface_alpha_3d', 'enable_wireframe', 'enable_anti_aliasing', 
                                            'enable_bloom_effect']):
                self.renderer.set_3d_rendering_options(options)
                print(f"🎨 3D渲染选项已更新: {list(options.keys())}")
            
            # 🎨 处理预处理选项
            if any(key in options for key in ['preprocessing_enabled', 'use_gaussian_blur', 'use_xy_swap', 'use_custom_colormap', 'log_y_lim', 'gaussian_sigma', 'gaussian_blur_sigma']):
                self.renderer.set_preprocessing_options(options)
                print(f"🎨 预处理选项已更新: {list(options.keys())}")
            
            # 处理其他可视化选项
            self.renderer.set_visualization_options(options)
    
    @pyqtSlot(str, bool)
    def on_path_mode_requested(self, path_name: str, enabled: bool):
        """处理路径模式请求"""
        try:
            if enabled:
                success = self.game_core.enable_path_mode(path_name)
                if success:
                    print(f"🗺️ 路径模式已启用: {path_name}")
                    # 🎨 设置渲染器路径引导模式
                    if self.renderer:
                        self.renderer.set_path_guide_mode(True)
                        # 🆕 启用引导模式，允许切换到2D
                        self.renderer.set_guide_mode(True)
                        print("🎨 引导模式已启用，可以切换到2D渲染")
                else:
                    print(f"❌ 路径模式启用失败: {path_name}")
            else:
                self.game_core.disable_path_mode()
                print("🗺️ 路径模式已禁用")
                # 🎨 关闭渲染器路径引导模式
                if self.renderer:
                    self.renderer.set_path_guide_mode(False)
                    # 🆕 禁用引导模式，保持当前渲染模式
                    self.renderer.set_guide_mode(False)
                    print("🎨 引导模式已禁用，保持当前渲染模式")
        except Exception as e:
            print(f"❌ 路径模式操作失败: {str(e)}")
    
    @pyqtSlot()
    def on_path_reset_requested(self):
        """处理路径重置请求"""
        try:
            self.game_core.reset_path_progress()
            print("🗺️ 路径进度已重置")
        except Exception as e:
            print(f"❌ 路径重置失败: {str(e)}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.disconnect_sensor()
        event.accept()
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        try:
            # 按 'P' 键显示性能汇总
            if event.key() == Qt.Key_P:
                print("\n🔍 手动触发性能汇总...")
                self.performance_monitor.print_performance_summary()
            # 按 'R' 键重置性能统计
            elif event.key() == Qt.Key_R:
                print("\n🔄 重置性能统计...")
                self.performance_monitor = PerformanceMonitor()
                print("✅ 性能统计已重置")
            # 按 'F' 键显示帧率配置
            elif event.key() == Qt.Key_F:
                print("\n📊 显示帧率配置...")
                self.show_current_frame_rate_config()
            # 按 'G' 键强制刷新渲染器
            elif event.key() == Qt.Key_G:
                print("\n🔄 强制刷新渲染器...")
                if self.renderer:
                    self.renderer.force_refresh()
                else:
                    print("❌ 渲染器不可用")
            # 按 'T' 键测试渲染器性能
            elif event.key() == Qt.Key_T:
                print("\n🧪 测试渲染器性能...")
                if self.renderer:
                    self.renderer.test_renderer_performance()
                else:
                    print("❌ 渲染器不可用")
            # 按 'H' 键显示帮助信息
            elif event.key() == Qt.Key_H:
                print("\n" + "="*50)
                print("🎮 推箱子游戏 - 性能监控快捷键")
                print("="*50)
                print("P - 显示性能汇总")
                print("R - 重置性能统计")
                print("F - 显示帧率配置")
                print("G - 强制刷新渲染器")
                print("T - 测试渲染器性能")
                print("H - 显示帮助信息")
                print("="*50)
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"❌ 键盘事件处理失败: {str(e)}")
            super().keyPressEvent(event)
    
    @pyqtSlot(float)
    def on_physics_time_updated(self, physics_time_ms):
        """处理物理时间更新"""
        try:
            # 📊 记录到性能监控器
            self.performance_monitor.add_physics_time(physics_time_ms)
            print(f"⚙️ 物理时间已记录: {physics_time_ms:.2f}ms")
        except Exception as e:
            print(f"❌ 处理物理时间更新失败: {str(e)}")

def main():
    """主函数"""
    print("🚀 推箱子游戏启动器 v2.0 (高性能优化)")
    print("=" * 50)
    
    # 检查传感器接口可用性
    if not SENSOR_INTERFACES_AVAILABLE:
        print("❌ 传感器接口不可用，无法启动游戏")
        return
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("推箱子游戏 - 高性能优化版")
    
    # 🎨 为整个应用程序应用深色主题
    if UTILS_AVAILABLE:
        apply_dark_theme(app)
        print("🎨 应用程序已应用深色主题")
    else:
        print("⚠️ utils不可用，使用默认主题")
    
    # 设置应用程序图标
    icon_path = os.path.join(os.path.dirname(__file__), "utils", "logo_dark.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        print(f"✅ 应用程序图标已设置: {icon_path}")
    else:
        print(f"⚠️ 未找到图标文件: {icon_path}")
    
    # 创建主窗口
    main_window = BoxGameMainWindow()
    main_window.show()
    
    # 🚫 不自动连接传感器，等待用户手动连接
    print("\n🎮 游戏已启动，等待连接传感器...")
    print("💡 提示：连接传感器后将自动开始数据采集")
    print("💡 提示：请确保传感器已正确连接并具有访问权限")
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 