"""
interfaces/ordinary/SlidingDetector.py
滑动检测器 - 扩展现有分析能力
"""

import numpy as np
from collections import deque
from scipy.ndimage import center_of_mass

class SlidingDetector:
    """滑动检测器 - 基于重心移动分析"""
    
    def __init__(self, sliding_threshold=5.0, temporal_window=10, pressure_threshold=0.005):
        self.sliding_threshold = sliding_threshold  # 重心移动阈值（像素）
        self.temporal_window = temporal_window
        self.pressure_threshold = pressure_threshold
        
        # 历史数据
        self.cop_history = deque(maxlen=temporal_window)
        self.pressure_history = deque(maxlen=temporal_window)
        
        # 状态
        self.is_contact = False
        self.is_sliding = False
        self.is_tangential = False
        self.initial_cop = None
        self.current_cop = None
        self.movement_distance = 0.0
        
    def calculate_center_of_pressure(self, pressure_data):
        """计算压力中心"""
        if pressure_data is None or pressure_data.size == 0:
            return None
            
        # 过滤低压力点
        valid_mask = pressure_data > self.pressure_threshold
        if not np.any(valid_mask):
            return None
        
        # 计算加权中心
        total_pressure = np.sum(pressure_data[valid_mask])
        if total_pressure == 0:
            return None
        
        rows, cols = pressure_data.shape
        y_indices, x_indices = np.mgrid[0:rows, 0:cols]
        
        cop_x = np.sum(x_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
        cop_y = np.sum(y_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
        
        return (cop_x, cop_y)
    
    def detect_contact(self, pressure_data):
        """检测接触状态"""
        if pressure_data is None:
            return False
            
        max_pressure = np.max(pressure_data)
        contact_area = np.sum(pressure_data > self.pressure_threshold)
        
        return max_pressure > self.pressure_threshold and contact_area >= 5
    
    def update_state(self, pressure_data):
        """更新检测状态"""
        # 检测接触
        new_contact = self.detect_contact(pressure_data)
        
        if not new_contact:
            # 无接触时重置状态
            self.is_contact = False
            self.is_tangential = False
            self.is_sliding = False
            self.current_cop = None
            self.initial_cop = None
            self.movement_distance = 0.0
            return
        
        # 计算压力中心
        current_cop = self.calculate_center_of_pressure(pressure_data)
        if current_cop is None:
            return
        
        # 更新接触状态
        if not self.is_contact:
            # 新接触
            self.is_contact = True
            self.initial_cop = current_cop
            self.current_cop = current_cop
            self.movement_distance = 0.0
            self.is_tangential = True
            self.is_sliding = False
        else:
            # 持续接触，计算移动
            self.current_cop = current_cop
            
            if self.initial_cop is not None:
                dx = current_cop[0] - self.initial_cop[0]
                dy = current_cop[1] - self.initial_cop[1]
                self.movement_distance = np.sqrt(dx*dx + dy*dy)
                
                # 判断是否滑动
                if self.movement_distance > self.sliding_threshold:
                    self.is_sliding = True
                    self.is_tangential = False
                else:
                    self.is_sliding = False
                    self.is_tangential = True
        
        # 更新历史记录
        self.cop_history.append(current_cop)
        self.pressure_history.append(pressure_data.copy())
    
    def get_state_info(self):
        """获取状态信息"""
        return {
            'is_contact': self.is_contact,
            'is_tangential': self.is_tangential,
            'is_sliding': self.is_sliding,
            'current_cop': self.current_cop,
            'initial_cop': self.initial_cop,
            'movement_distance': self.movement_distance,
            'sliding_threshold': self.sliding_threshold
        }
