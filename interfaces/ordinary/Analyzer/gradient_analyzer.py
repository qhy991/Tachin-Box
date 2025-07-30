"""
梯度分析模块 - gradient_analyzer.py
包含所有梯度方法的分析实现
"""

import numpy as np
from functools import lru_cache
from typing import Dict, Optional, Tuple
from .config import AnalysisConfig
from .core_functions import (
    fast_gradient_sobel, 
    fast_weighted_gradient_sum,
    fast_axial_asymmetry,
    fast_grid_gradient_analysis
)

class GradientAnalyzer:
    """完整梯度分析器 - 保留原版所有方法，应用性能优化"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        
        # 性能优化相关
        self._gradient_cache = {} if config.enable_result_caching else None
        self._method_cache = {}
        
        # 窗口配置
        self.window_sizes = {
            'peak': config.fixed_peak_window_size,
            'cop': 5,
            'grid': 3
        }
        
    @lru_cache(maxsize=32)
    def _get_cached_sobel_kernel(self):
        """缓存Sobel算子"""
        return np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    
    def calculate_gradients(self, matrix):
        """计算梯度 - 自动选择最优方法"""
        cache_key = None
        if self._gradient_cache is not None:
            cache_key = (matrix.shape, matrix.dtype, self.config.gradient_operator)
            if cache_key in self._gradient_cache:
                return self._gradient_cache[cache_key]
        
        # 选择梯度计算方法
        if self.config.gradient_operator == "sobel":
            grad_x, grad_y = fast_gradient_sobel(matrix)
            # 应用spacing
            grad_x = grad_x / self.config.cell_spacing_x
            grad_y = grad_y / self.config.cell_spacing_y
        else:
            grad_y, grad_x = np.gradient(matrix, self.config.cell_spacing_y, self.config.cell_spacing_x)
        
        if self._gradient_cache is not None and cache_key is not None:
            self._gradient_cache[cache_key] = (grad_x, grad_y)
        
        return grad_x, grad_y
    
    def analyze(self, focused_window, pressure_threshold=None, 
                full_matrix=None, cop_position=None, peak_position=None):
        """
        完整分析方法 - 保留原版所有功能
        """
        if focused_window is None or focused_window.size == 0:
            return {}
        
        if pressure_threshold is None:
            pressure_threshold = self.config.pressure_threshold
        
        print(f"🔍 [梯度分析器] 开始分析...")
        print(f"    窗口形状: {focused_window.shape}")
        print(f"    阈值: {pressure_threshold:.6f}")
        
        results = {}
        
        # 1. 基础梯度计算
        grad_x, grad_y = self.calculate_gradients(focused_window)
        
        # 2. 接触点分析
        contact_mask = focused_window > pressure_threshold
        contact_points = np.sum(contact_mask)
        
        if contact_points == 0:
            print("⚠️ [梯度分析器] 窗口内没有接触点")
            return {}
        
        # 3. 传统方法分析
        results.update(self._analyze_traditional_methods(
            focused_window, grad_x, grad_y, contact_mask))
        
        # 4. 加权梯度路径分析
        weighted_grad_x, weighted_grad_y = self._create_weighted_gradients(
            focused_window, grad_x, grad_y)
        
        results.update(self._analyze_weighted_path_metrics(
            weighted_grad_x, weighted_grad_y, focused_window, contact_mask))
        
        # 5. 全局分析（如果提供了完整矩阵）
        if full_matrix is not None:
            results.update(self._analyze_global_methods(full_matrix))
        
        # 6. 多窗口分析
        if full_matrix is not None and (cop_position is not None or peak_position is not None):
            results.update(self._analyze_multi_window_methods(
                full_matrix, cop_position, peak_position))
        
        # 7. 网格分析
        results.update(self._analyze_grid_methods(weighted_grad_x, weighted_grad_y))
        
        print(f"✅ [梯度分析器] 分析完成，生成 {len(results)} 个结果")
        return results
    
    def _create_weighted_gradients(self, pressure_matrix, grad_x, grad_y):
        """创建加权梯度"""
        pressure_safe = np.maximum(pressure_matrix, 0) + self.config.gradient_epsilon
        weighted_grad_x = grad_x * pressure_safe
        weighted_grad_y = grad_y * pressure_safe
        return weighted_grad_x, weighted_grad_y
    
    def _analyze_traditional_methods(self, window_matrix, grad_x, grad_y, contact_mask):
        """分析传统方法"""
        results = {}
        
        # 1. 全局加权平均 (优化版)
        try:
            contact_pressures = window_matrix[contact_mask]
            if len(contact_pressures) > 0:
                avg_grad_x, avg_grad_y = fast_weighted_gradient_sum(
                    grad_x, grad_y, window_matrix, contact_mask)
                
                magnitude = np.sqrt(avg_grad_x**2 + avg_grad_y**2)
                if magnitude > self.config.min_grad_magnitude:
                    angle = np.degrees(np.arctan2(-avg_grad_y, -avg_grad_x)) % 360
                    confidence = min(1.0, magnitude * 2)
                    
                    results['global_weighted_average'] = {
                        'angle': float(angle),
                        'confidence': float(confidence),
                        'magnitude': float(magnitude),
                        'method_type': 'traditional'
                    }
        except Exception as e:
            print(f"⚠️ 全局加权平均计算失败: {e}")
        
        # 2. 加权最小方差方法 (优化版)
        results['weighted_min_variance'] = self._weighted_min_variance_method(
            grad_x, grad_y, contact_mask, window_matrix)
        
        # 3. 加权不对称方法 (优化版)
        results['weighted_asymmetry'] = self._weighted_asymmetry_method(
            window_matrix, grad_x, grad_y)
        
        return results
    
    def _analyze_weighted_path_metrics(self, grad_x_weighted, grad_y_weighted, 
                                       pressure_matrix, contact_mask):
        """加权梯度路径分析"""
        results = {}
        
        # M1W: 峰值窗口内平均加权梯度
        try:
            if np.any(contact_mask):
                avg_gx_weighted = np.mean(grad_x_weighted[contact_mask])
                avg_gy_weighted = np.mean(grad_y_weighted[contact_mask])
                
                if not (np.isnan(avg_gx_weighted) or np.isnan(avg_gy_weighted)):
                    magnitude_weighted = np.sqrt(avg_gx_weighted**2 + avg_gy_weighted**2)
                    if magnitude_weighted > self.config.min_grad_magnitude:
                        angle_weighted = np.degrees(np.arctan2(-avg_gy_weighted, -avg_gx_weighted)) % 360
                        confidence_weighted = min(1.0, magnitude_weighted / np.sum(pressure_matrix) * 5)
                        
                        results['m1_weighted_gradient'] = {
                            'angle': float(angle_weighted),
                            'confidence': float(confidence_weighted),
                            'magnitude': float(magnitude_weighted),
                            'method_type': 'dual_path_weighted'
                        }
        except Exception as e:
            print(f"⚠️ M1加权梯度计算失败: {e}")
        
        # 轴向不对称分析 - 加权路径
        try:
            hor_asym_weighted, vert_asym_weighted = fast_axial_asymmetry(
                grad_x_weighted, grad_y_weighted)
            
            if not (np.isclose(hor_asym_weighted, 0) and np.isclose(vert_asym_weighted, 0)):
                angle_asym_weighted = np.degrees(np.arctan2(-vert_asym_weighted, -hor_asym_weighted)) % 360
                asym_magnitude_weighted = np.sqrt(hor_asym_weighted**2 + vert_asym_weighted**2)
                
                total_gradient_sum = np.sum(np.abs(grad_x_weighted)) + np.sum(np.abs(grad_y_weighted))
                confidence_asym_weighted = min(1.0, asym_magnitude_weighted / (total_gradient_sum + 1e-6))
                
                results['axial_asymmetry_weighted'] = {
                    'angle': float(angle_asym_weighted),
                    'confidence': float(confidence_asym_weighted),
                    'horizontal_asymmetry': float(hor_asym_weighted),
                    'vertical_asymmetry': float(vert_asym_weighted),
                    'method_type': 'asymmetry_weighted'
                }
        except Exception as e:
            print(f"⚠️ 轴向不对称分析失败: {e}")
        
        return results
    
    def _analyze_global_methods(self, full_matrix):
        """全局方法分析"""
        results = {}
        
        try:
            # CoP窗口分析
            if cop_position is not None:
                cop_row, cop_col = cop_position
                cop_window = self._extract_window(full_matrix, cop_row, cop_col, 
                                                self.window_sizes['cop'])
                
                if cop_window.size > 0:
                    cop_grad_x, cop_grad_y = self.calculate_gradients(cop_window)
                    cop_weighted_grad_x, cop_weighted_grad_y = self._create_weighted_gradients(
                        cop_window, cop_grad_x, cop_grad_y)
                    
                    # CoP窗口加权梯度不对称
                    hor_cop, vert_cop = fast_axial_asymmetry(cop_weighted_grad_x, cop_weighted_grad_y)
                    
                    if not (np.isclose(hor_cop, 0) and np.isclose(vert_cop, 0)):
                        cop_angle_weighted = np.degrees(np.arctan2(-vert_cop, -hor_cop)) % 360
                        
                        results['cop_window_asymmetry_weighted'] = {
                            'angle': float(cop_angle_weighted),
                            'confidence': 0.55,
                            'method_type': 'cop_window_weighted'
                        }
        except Exception as e:
            print(f"⚠️ 多窗口分析失败: {e}")
        
        return results
    
    def _analyze_grid_methods(self, grad_x_weighted, grad_y_weighted):
        """网格方法分析"""
        results = {}
        
        try:
            # 加权梯度网格分析
            grid_data = fast_grid_gradient_analysis(grad_x_weighted, grad_y_weighted)
            grid_sums = {}
            
            # 重新组织网格数据
            for r_idx in range(3):
                for c_idx in range(3):
                    idx = r_idx * 3 + c_idx
                    grid_sums[(r_idx, c_idx)] = (grid_data[idx * 2], grid_data[idx * 2 + 1])
            
            grid_angle_weighted = self._calculate_grid_dominant_direction(grid_sums)
            if grid_angle_weighted is not None:
                results['grid_analysis_weighted'] = {
                    'angle': float(grid_angle_weighted),
                    'confidence': 0.55,
                    'method_type': 'grid_weighted'
                }
        except Exception as e:
            print(f"⚠️ 网格分析失败: {e}")
        
        return results
    
    def _calculate_grid_dominant_direction(self, grid_sums):
        """计算网格主导方向"""
        if not grid_sums:
            return None
        
        # 定义方向向量组合
        directions = {
            "main_diagonal": [(0,0), (1,1), (2,2)],
            "anti_diagonal": [(2,0), (1,1), (0,2)],
            "middle_row": [(1,0), (1,1), (1,2)],
            "middle_col": [(0,1), (1,1), (2,1)]
        }
        
        max_magnitude = -1.0
        dominant_vector = (0.0, 0.0)
        
        for direction_name, positions in directions.items():
            sum_x = sum(grid_sums.get(pos, (0,0))[0] for pos in positions)
            sum_y = sum(grid_sums.get(pos, (0,0))[1] for pos in positions)
            
            magnitude = np.sqrt(sum_x**2 + sum_y**2)
            if magnitude > max_magnitude:
                max_magnitude = magnitude
                dominant_vector = (sum_x, sum_y)
        
        if max_magnitude <= 1e-9:
            return None
        
        angle = np.degrees(np.arctan2(dominant_vector[1], dominant_vector[0])) % 360
        return angle
    
    def _extract_window(self, matrix, center_row, center_col, window_size):
        """提取窗口"""
        if matrix is None or matrix.size == 0:
            return np.array([])
        
        rows, cols = matrix.shape
        if window_size <= 0:
            return np.array([])
        
        ws = window_size + 1 if window_size % 2 == 0 else window_size
        hs = ws // 2
        
        cr, cc = int(round(center_row)), int(round(center_col))
        
        window = np.zeros((ws, ws), dtype=matrix.dtype)
        
        r_start = max(0, cr - hs)
        r_end = min(rows, cr + hs + 1)
        c_start = max(0, cc - hs)
        c_end = min(cols, cc + hs + 1)
        
        win_r_start = max(0, hs - (cr - r_start))
        win_r_end = win_r_start + (r_end - r_start)
        win_c_start = max(0, hs - (cc - c_start))
        win_c_end = win_c_start + (c_end - c_start)
        
        if r_start < r_end and c_start < c_end:
            window[win_r_start:win_r_end, win_c_start:win_c_end] = matrix[r_start:r_end, c_start:c_end]
        
        return window
    
    def _weighted_min_variance_method(self, grad_x, grad_y, contact_mask, pressure_matrix):
        """加权最小方差方法 - 优化版"""
        try:
            magnitudes = np.sqrt(grad_x**2 + grad_y**2)
            angles_rad = np.arctan2(grad_y, grad_x)
            
            valid_mask = (magnitudes > self.config.min_grad_magnitude) & contact_mask
            if not np.any(valid_mask):
                return {'angle': None, 'confidence': 0, 'variance': float('inf')}
            
            valid_angles = angles_rad[valid_mask]
            valid_magnitudes = magnitudes[valid_mask]
            valid_pressures = pressure_matrix[valid_mask]
            
            # 使用压力作为权重
            weights = valid_pressures / (np.sum(valid_pressures) + 1e-10)
            
            mean_cos = np.sum(weights * np.cos(valid_angles))
            mean_sin = np.sum(weights * np.sin(valid_angles))
            
            mean_angle = np.arctan2(mean_sin, mean_cos)
            R = np.sqrt(mean_cos**2 + mean_sin**2)
            variance = 1.0 - R
            
            force_angle = (mean_angle + np.pi) % (2 * np.pi)
            
            return {
                'angle': float(np.degrees(force_angle) % 360),
                'confidence': float(max(0, 1.0 - variance)),
                'variance': float(variance),
                'method_type': 'traditional'
            }
        except Exception as e:
            print(f"⚠️ 加权最小方差方法错误: {e}")
            return {'angle': None, 'confidence': 0, 'variance': float('inf')}
    
    def _weighted_asymmetry_method(self, smoothed_matrix, grad_x, grad_y):
        """加权不对称方法 - 优化版"""
        try:
            rows, cols = smoothed_matrix.shape
            center_row = rows // 2
            center_col = cols // 2
            
            if not (0 <= center_row < rows and 0 <= center_col < cols):
                return {'angle': None, 'confidence': 0, 'magnitude': 0}

            # 左右不对称
            left_grads = np.abs(grad_x[center_row, :center_col]) if center_col > 0 else np.array([])
            right_grads = np.abs(grad_x[center_row, center_col+1:]) if center_col < cols - 1 else np.array([])
            avg_left = np.mean(left_grads) if len(left_grads) > 0 else 0
            avg_right = np.mean(right_grads) if len(right_grads) > 0 else 0
            force_x = avg_left - avg_right

            # 上下不对称
            top_grads = np.abs(grad_y[:center_row, center_col]) if center_row > 0 else np.array([])
            bottom_grads = np.abs(grad_y[center_row+1:, center_col]) if center_row < rows - 1 else np.array([])
            avg_top = np.mean(top_grads) if len(top_grads) > 0 else 0
            avg_bottom = np.mean(bottom_grads) if len(bottom_grads) > 0 else 0
            force_y = avg_top - avg_bottom
            
            magnitude = np.sqrt(force_x**2 + force_y**2)
            if magnitude > 1e-6:
                angle = np.arctan2(force_y, force_x)
                return {
                    'angle': float(np.degrees(angle) % 360),
                    'confidence': float(min(1.0, magnitude)),
                    'magnitude': float(magnitude),
                    'force_vector': (float(force_x), float(force_y)),
                    'method_type': 'traditional'
                }
            return {'angle': None, 'confidence': 0, 'magnitude': 0}
        except Exception as e:
            print(f"⚠️ 加权不对称方法错误: {e}")
            return {'angle': None, 'confidence': 0, 'magnitude': 0}
    
    def get_method_summary(self):
        """获取方法摘要"""
        return {
            'traditional_methods': [
                'global_weighted_average',
                'weighted_min_variance', 
                'weighted_asymmetry'
            ],
            'weighted_path_methods': [
                'm1_weighted_gradient',
                'axial_asymmetry_weighted'
            ],
            'global_methods': [
                'global_asymmetry_weighted'
            ],
            'window_methods': [
                'cop_window_asymmetry_weighted'
            ],
            'grid_methods': [
                'grid_analysis_weighted'
            ]
        }

# 导出接口
__all__ = ['GradientAnalyzer'] 