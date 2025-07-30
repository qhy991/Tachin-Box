# -*- coding: utf-8 -*-
"""
推箱子游戏核心引擎模块 V2 - 两段式滑动检测
Core Game Engine Module for Box Push Game V2

本模块基于 box_game_core_optimized.py，集成V2智能控制系统，
实现两段式滑动检测：Stick模式和滑动模式。
"""

import numpy as np
import time
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget

# 导入路径规划模块
try:
    from .box_game_path_planning import PathPlanningGameEnhancer
    PATH_PLANNING_AVAILABLE = True
    print("✅ 路径规划模块已加载")
except ImportError:
    print("⚠️ 无法导入路径规划模块")
    PATH_PLANNING_AVAILABLE = False

# 导入V2智能控制系统
from .box_smart_control_system_v2 import SmartControlSystemV2

from .contact_filter import is_special_idle_case

class BoxGameDataBridgeV2(QObject):
    """游戏数据桥接器 V2"""
    pressure_data_updated = pyqtSignal(np.ndarray)
    analysis_results_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pressure_data = None
        self.analysis_results = None
        self.last_update_time = 0
        self.contact_start_time = None
        self.pressure_history = deque(maxlen=20)

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

    def get_contact_time(self):
        if self.contact_start_time is None:
            return 0.0
        return time.time() - self.contact_start_time

    def update_pressure_data(self, pressure_data):
        self.set_pressure_data(pressure_data)

    def get_latest_data(self):
        return {
            'pressure_data': self.pressure_data,
            'analysis_results': self.analysis_results,
            'update_time': self.last_update_time
        }

class BoxGameCoreV2(QObject):
    """推箱子游戏核心引擎 V2 - 两段式滑动检测"""
    game_state_changed = pyqtSignal(dict)
    box_state_updated = pyqtSignal(dict)
    analysis_completed = pyqtSignal(dict)
    
    # 路径规划相关信号
    path_progress_updated = pyqtSignal(dict)
    path_target_reached = pyqtSignal(dict)
    path_completed = pyqtSignal(dict)
    navigation_info_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pressure_threshold = 0.01
        self.contact_area_threshold = 5
        self.data_bridge = None
        self.box_position = np.array([32.0, 32.0])
        self.box_original_position = np.array([32.0, 32.0])
        self.box_target_position = np.array([32.0, 32.0])
        self.box_size = 6.0
        self.is_contact = False
        self.current_cop = None
        self.initial_cop = None
        self.movement_distance = 0.0
        self.analysis_frame_count = 0
        self.gradient_threshold = 1e-5
        
        # 🎮 集成V2智能控制系统
        self.smart_control = SmartControlSystemV2()
        print("🎮 V2智能双模式控制系统已集成")
        
        # 🗺️ 路径规划系统
        if PATH_PLANNING_AVAILABLE:
            self.path_enhancer = PathPlanningGameEnhancer(self)
            self.setup_path_connections()
        else:
            self.path_enhancer = None
        
        # ⏰ 物理更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_physics)
        self.update_timer.start(50)

    def setup_path_connections(self):
        """设置路径规划信号连接"""
        if self.path_enhancer:
            self.path_enhancer.path_progress_updated.connect(self.path_progress_updated.emit)
            self.path_enhancer.target_reached.connect(self.path_target_reached.emit)
            self.path_enhancer.path_completed.connect(self.path_completed.emit)
            self.path_enhancer.navigation_updated.connect(self.navigation_info_updated.emit)
            print("🗺️ 路径规划信号连接完成")

    def process_pressure_data(self, pressure_data):
        """处理压力数据 - 简化为只使用COP位移逻辑"""
        if pressure_data is None or pressure_data.size == 0:
            return None
        
        try:
            # 🔍 接触检测
            contact_detected = self.detect_contact(pressure_data)
            
            # 📍 COP计算
            current_cop = self.calculate_cop(pressure_data)
            
            # 🎯 使用V2智能控制系统计算目标位置
            target_position = self.smart_control.calculate_target_position(
                contact_detected, current_cop, self.initial_cop, self.box_position
            )
            
            # 🎯 应用边界限制
            target_position[0] = np.clip(target_position[0], self.box_size/2, 64 - self.box_size/2)
            target_position[1] = np.clip(target_position[1], self.box_size/2, 64 - self.box_size/2)
            self.box_target_position = target_position
            
            # 🔄 处理接触状态变化
            if not contact_detected:
                if self.is_contact:  # 接触结束
                    self.smart_control.reset_on_contact_end()
                self.initial_cop = None
            elif contact_detected and self.initial_cop is None and current_cop is not None:
                # 刚开始接触时，记录初始COP
                self.initial_cop = current_cop
            
            # 📊 获取控制系统信息
            control_info = self.smart_control.get_control_info()
            
            # 🎮 更新游戏状态
            self.update_game_state(contact_detected, current_cop, control_info)
            
            return {
                'contact_detected': contact_detected,
                'current_cop': current_cop,
                'control_mode': control_info['mode'],
                'frame_count': self.analysis_frame_count
            }
            
        except Exception as e:
            print(f"❌ 压力数据处理失败: {e}")
            return None

    def detect_contact(self, pressure_data):
        """接触检测"""
        if pressure_data is None or pressure_data.size == 0:
            return False
        max_pressure = np.max(pressure_data)
        if max_pressure < self.pressure_threshold:
            return False
        contact_mask = pressure_data > self.pressure_threshold
        contact_area = np.sum(contact_mask)
        return contact_area >= self.contact_area_threshold

    def calculate_cop(self, pressure_data):
        """计算压力中心点"""
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

    def update_game_state(self, contact_detected, current_cop, control_info):
        """更新游戏状态"""
        self.is_contact = contact_detected
        self.current_cop = current_cop
        
        # 📊 计算移动距离（用于调试）
        if current_cop is not None and self.initial_cop is not None:
            dx = current_cop[0] - self.initial_cop[0]
            dy = current_cop[1] - self.initial_cop[1]
            self.movement_distance = np.sqrt(dx*dx + dy*dy)
        else:
            self.movement_distance = 0.0
        
        # 📡 发送状态信息
        state_info = {
            'is_contact': self.is_contact,
            'current_cop': self.current_cop,
            'initial_cop': self.initial_cop,
            'movement_distance': self.movement_distance,
            'box_position': self.box_position.copy(),
            'box_target_position': self.box_target_position.copy(),
            'frame_count': self.analysis_frame_count,
            # 🎮 控制系统状态信息
            'control_mode': control_info['mode'],
            'system_mode': control_info['system_mode'],
            'control_displacement': control_info['displacement'],
            'stick_threshold': control_info['stick_threshold'],
            'sliding_threshold': control_info['sliding_threshold']
        }
        self.game_state_changed.emit(state_info)
        self.analysis_frame_count += 1

    def update_physics(self):
        """更新箱子位置"""
        # 检查路径规划是否启用
        if self.path_enhancer and self.path_enhancer.is_path_mode_enabled:
            # 🗺️ 路径模式：只更新路径进度，不覆盖用户控制
            self.path_enhancer.update_box_position(self.box_position)
            movement_factor = 0.15
        else:
            # 🎮 自由控制模式
            movement_factor = 0.15
        
        # 🎯 更新箱子位置朝向目标位置
        self.box_position[0] += (self.box_target_position[0] - self.box_position[0]) * movement_factor
        self.box_position[1] += (self.box_target_position[1] - self.box_position[1]) * movement_factor
        
        # 📦 确保箱子在游戏区域内
        self.box_position[0] = np.clip(self.box_position[0], 5, 59)
        self.box_position[1] = np.clip(self.box_position[1], 5, 59)
        
        # 📡 发送状态更新
        box_state = {
            'position': self.box_position.copy(),
            'target_position': self.box_target_position.copy(),
            'control_mode': self.smart_control.current_mode,
            'path_enabled': self.path_enhancer.is_path_mode_enabled if self.path_enhancer else False
        }
        self.box_state_updated.emit(box_state)

    def reset_game(self):
        """重置游戏状态"""
        self.box_position = self.box_original_position.copy()
        self.box_target_position = self.box_original_position.copy()
        self.is_contact = False
        self.current_cop = None
        self.initial_cop = None
        self.movement_distance = 0.0
        self.analysis_frame_count = 0
        
        # 🎮 重置智能控制系统
        self.smart_control.reset()
        
        # 🗺️ 重置路径规划系统
        if self.path_enhancer:
            self.path_enhancer.reset_path()
        
        print("🔄 游戏状态已重置（含V2智能控制系统）")

    def update_parameters(self, params):
        """更新游戏参数"""
        # 更新基本参数
        if 'pressure_threshold' in params:
            self.pressure_threshold = params['pressure_threshold']
        if 'contact_area_threshold' in params:
            self.contact_area_threshold = params['contact_area_threshold']
        if 'gradient_threshold' in params:
            self.gradient_threshold = params['gradient_threshold']
        
        # 🎮 更新V2智能控制系统参数
        if self.smart_control:
            self.smart_control.update_parameters(params)
        
        print(f"🎮 游戏参数已更新: {list(params.keys())}")

    def set_data_bridge(self, data_bridge):
        self.data_bridge = data_bridge
        print("🌉 数据桥接器已连接到游戏核心 V2")

    def enable_path_mode(self, path_name: str) -> bool:
        """启用路径模式"""
        if self.path_enhancer:
            result = self.path_enhancer.enable_path_mode(path_name)
            if result:
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