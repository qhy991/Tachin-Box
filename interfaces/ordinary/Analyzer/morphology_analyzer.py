"""
形态学分析模块 - morphology_analyzer.py
包含所有形态学方法的分析实现
"""

import numpy as np
from functools import lru_cache
from typing import Dict, List
from .config import AnalysisConfig, CV2_AVAILABLE, SCIPY_AVAILABLE
from .core_functions import fast_moments_calculation

if CV2_AVAILABLE:
    import cv2

class MorphologyAnalyzer:
    """完整形态学分析器 - 保留所有原版方法，应用性能优化"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        
        # 压力质量评估参数
        self.pressure_quality_params = {
            'min_effective_pressure_ratio': config.min_effective_pressure_ratio,
            'noise_estimation_method': config.noise_estimation_method,
            'gradient_consistency_weight': config.gradient_consistency_weight,
            'pressure_distribution_weight': config.pressure_distribution_weight,
            'shape_clarity_weight': config.shape_clarity_weight
        }
        
        # 缓存
        self._gabor_kernel_cache = {} if config.enable_result_caching else None
    
    def analyze(self, smoothed_matrix):
        """执行所有基于形态学的压力加权方法"""
        results = {}
        
        print(f"🔬 [形态学分析器] 开始分析，数据范围: {smoothed_matrix.min():.4f} - {smoothed_matrix.max():.4f}")
        
        # 0. 压力质量预评估
        pressure_quality = self._assess_pressure_quality(smoothed_matrix)
        print(f"📊 压力质量评估: {pressure_quality:.3f}")
        
        # 1. 压力加权Gabor滤波方法
        results['gabor_filter'] = self._pressure_weighted_gabor_analysis(smoothed_matrix, pressure_quality)
        
        # 2. 压力加权形状矩方法
        results['shape_moments'] = self._pressure_weighted_moments_analysis(smoothed_matrix, pressure_quality)
        
        # 3. 增强协方差分析方法
        results['covariance_analysis'] = self._enhanced_covariance_analysis(smoothed_matrix, pressure_quality)
        
        # 4. 压力加权多尺度分析方法
        results['multiscale_analysis'] = self._pressure_weighted_multiscale_analysis(smoothed_matrix, pressure_quality)
        
        # 5. 压力分布傅里叶方向分析方法
        results['fourier_direction'] = self._pressure_distribution_fourier_analysis(smoothed_matrix, pressure_quality)
        
        # 6. 梯度引导形态学方法
        results['gradient_guided_morphology'] = self._gradient_guided_morphology_analysis(smoothed_matrix, pressure_quality)
        
        return results
    
    def _assess_pressure_quality(self, pressure_matrix):
        """评估压力数据质量"""
        try:
            total_pressure = np.sum(pressure_matrix)
            max_pressure = np.max(pressure_matrix)
            
            if total_pressure == 0 or max_pressure == 0:
                return 0.0
            
            # 1. 有效压力比例
            effective_threshold = max_pressure * self.pressure_quality_params['min_effective_pressure_ratio']
            effective_ratio = np.sum(pressure_matrix > effective_threshold) / pressure_matrix.size
            
            # 2. 信噪比估计
            if self.pressure_quality_params['noise_estimation_method'] == 'mad':
                edge_width = 2
                edges = np.concatenate([
                    pressure_matrix[:edge_width, :].flatten(),
                    pressure_matrix[-edge_width:, :].flatten(),
                    pressure_matrix[:, :edge_width].flatten(),
                    pressure_matrix[:, -edge_width:].flatten()
                ])
                noise_level = 1.4826 * np.median(np.abs(edges - np.median(edges)))
            else:
                noise_level = np.std(pressure_matrix[pressure_matrix < effective_threshold])
            
            snr = max_pressure / (noise_level + 1e-8)
            snr_score = min(1.0, snr / 10.0)
            
            # 3. 压力分布均匀性
            pressure_variance = np.var(pressure_matrix[pressure_matrix > effective_threshold])
            pressure_mean = np.mean(pressure_matrix[pressure_matrix > effective_threshold])
            distribution_score = max(0, 1 - (pressure_variance / (pressure_mean**2 + 1e-8)))
            
            # 综合质量分数
            quality_score = (
                effective_ratio * 0.4 + 
                snr_score * 0.4 + 
                distribution_score * 0.2
            )
            
            return min(1.0, quality_score)
            
        except Exception as e:
            print(f"⚠️ 压力质量评估失败: {e}")
            return 0.5
    
    def _pressure_weighted_gabor_analysis(self, pressure_matrix, pressure_quality):
        """压力加权Gabor滤波分析 - 完整版"""
        try:
            print(f"🔍 [Gabor] 开始压力加权Gabor分析...")
            
            if not CV2_AVAILABLE:
                return self._gabor_fallback_analysis(pressure_matrix, pressure_quality)
            
            coarse_angles = np.arange(0, 180, 15)
            pressure_float = pressure_matrix.astype(np.float32)
            
            # 第一轮：粗糙扫描
            coarse_responses = []
            for angle in coarse_angles:
                gabor_kernel = self._create_adaptive_gabor_kernel(pressure_matrix.shape, angle)
                response = cv2.filter2D(pressure_float, -1, gabor_kernel)
                weighted_response = np.sum(response * pressure_matrix)
                coarse_responses.append(weighted_response)
            
            if not coarse_responses or max(np.abs(coarse_responses)) == 0:
                return {'angle': None, 'confidence': 0}
            
            max_idx = np.argmax(np.abs(coarse_responses))
            dominant_coarse_angle = coarse_angles[max_idx]
            
            # 第二轮：精细扫描
            fine_angles = np.arange(dominant_coarse_angle - 15, dominant_coarse_angle + 16, 2)
            fine_angles = fine_angles % 180
            
            fine_responses = []
            for angle in fine_angles:
                gabor_kernel = self._create_adaptive_gabor_kernel(pressure_matrix.shape, angle)
                response = cv2.filter2D(pressure_float, -1, gabor_kernel)
                weighted_response = np.sum(response * pressure_matrix)
                fine_responses.append(weighted_response)
            
            if not fine_responses:
                return {'angle': None, 'confidence': 0}
            
            max_fine_idx = np.argmax(np.abs(fine_responses))
            dominant_angle = fine_angles[max_fine_idx]
            max_response = abs(fine_responses[max_fine_idx])
            
            # 计算置信度
            total_pressure = np.sum(pressure_matrix)
            response_strength = max_response / (total_pressure + 1e-8)
            response_consistency = self._calculate_angular_consistency(fine_responses, fine_angles)
            
            base_confidence = min(1.0, response_strength * 5)
            quality_adjusted_confidence = base_confidence * (0.5 + 0.5 * pressure_quality)
            final_confidence = quality_adjusted_confidence * response_consistency
            
            print(f"✅ [Gabor] 角度: {dominant_angle:.1f}°, 置信度: {final_confidence:.3f}")
            
            return {
                'angle': float(dominant_angle),
                'confidence': float(final_confidence),
                'response_strength': float(response_strength),
                'pressure_quality': float(pressure_quality),
                'method': 'pressure_weighted_gabor'
            }
            
        except Exception as e:
            print(f"❌ [Gabor] 压力加权Gabor分析失败: {e}")
            return {'angle': None, 'confidence': 0}
    
    def _gabor_fallback_analysis(self, pressure_matrix, pressure_quality):
        """Gabor分析的备用实现（不依赖OpenCV）"""
        try:
            # 简化的方向分析
            grad_y, grad_x = np.gradient(pressure_matrix)
            
            # 使用压力加权的梯度方向
            weights = pressure_matrix
            valid_mask = weights > self.config.pressure_threshold
            
            if not np.any(valid_mask):
                return {'angle': None, 'confidence': 0}
            
            weighted_grad_x = np.sum(grad_x[valid_mask] * weights[valid_mask])
            weighted_grad_y = np.sum(grad_y[valid_mask] * weights[valid_mask])
            
            if abs(weighted_grad_x) < 1e-10 and abs(weighted_grad_y) < 1e-10:
                return {'angle': None, 'confidence': 0}
            
            angle = np.degrees(np.arctan2(weighted_grad_y, weighted_grad_x)) % 180
            magnitude = np.sqrt(weighted_grad_x**2 + weighted_grad_y**2)
            total_weight = np.sum(weights[valid_mask])
            confidence = min(1.0, magnitude / (total_weight + 1e-8) * 5) * (0.5 + 0.5 * pressure_quality)
            
            return {
                'angle': float(angle),
                'confidence': float(confidence),
                'method': 'gabor_fallback'
            }
            
        except Exception as e:
            print(f"❌ Gabor备用分析失败: {e}")
            return {'angle': None, 'confidence': 0}
    
    @lru_cache(maxsize=32)
    def _create_adaptive_gabor_kernel(self, pressure_matrix_shape, angle_deg, size=15):
        """创建自适应Gabor核 - 缓存版本"""
        try:
            rows, cols = pressure_matrix_shape
            
            # 基于数据特征自适应调整参数
            characteristic_size = min(rows, cols)
            base_frequency = 0.1
            frequency = base_frequency * (15.0 / characteristic_size)
            
            sigma = 3.0
            theta = np.radians(angle_deg)
            gamma = 0.5
            
            # 创建Gabor核
            x = np.arange(-size//2, size//2+1)
            y = np.arange(-size//2, size//2+1)
            X, Y = np.meshgrid(x, y)
            
            x_rot = X * np.cos(theta) + Y * np.sin(theta)
            y_rot = -X * np.sin(theta) + Y * np.cos(theta)
            
            gaussian = np.exp(-(x_rot**2 + gamma**2 * y_rot**2) / (2 * sigma**2))
            sinusoid = np.cos(2 * np.pi * frequency * x_rot)
            gabor_kernel = gaussian * sinusoid
            
            return gabor_kernel.astype(np.float32)
            
        except Exception as e:
            print(f"⚠️ 创建Gabor核失败: {e}")
            return self._create_simple_gabor_kernel(angle_deg, size)
    
    def _create_simple_gabor_kernel(self, angle_deg, size=15):
        """创建简单Gabor核（备用方案）"""
        sigma = 3.0
        frequency = 0.1
        theta = np.radians(angle_deg)
        
        x = np.arange(-size//2, size//2+1)
        y = np.arange(-size//2, size//2+1)
        X, Y = np.meshgrid(x, y)
        
        x_rot = X * np.cos(theta) + Y * np.sin(theta)
        y_rot = -X * np.sin(theta) + Y * np.cos(theta)
        
        gaussian = np.exp(-(x_rot**2 + y_rot**2) / (2 * sigma**2))
        sinusoid = np.cos(2 * np.pi * frequency * x_rot)
        
        return (gaussian * sinusoid).astype(np.float32)
    
    def _calculate_angular_consistency(self, responses, angles):
        """计算角度响应的一致性"""
        try:
            if len(responses) < 3:
                return 1.0
            
            responses = np.array(responses)
            max_response = np.max(np.abs(responses))
            
            if max_response == 0:
                return 0.0
            
            normalized_responses = responses / max_response
            response_variance = np.var(normalized_responses)
            consistency_score = min(1.0, response_variance * 2)
            
            return consistency_score
            
        except Exception as e:
            print(f"⚠️ 角度一致性计算失败: {e}")
            return 0.5
    
    def _pressure_weighted_moments_analysis(self, pressure_matrix, pressure_quality):
        """压力加权形状矩分析 - 完整版"""
        try:
            print(f"🔍 [Moments] 开始压力加权形状矩分析...")
            
            # 使用优化的矩计算
            cx, cy, nu20, nu02, nu11 = fast_moments_calculation(
                pressure_matrix, self.config.pressure_threshold)
            
            if cx == 0 and cy == 0:
                return {'angle': None, 'confidence': 0}
            
            # 计算主轴方向
            if abs(nu20 - nu02) < 1e-10 and abs(nu11) < 1e-10:
                return {'angle': None, 'confidence': 0}
            
            if abs(nu20 - nu02) < 1e-10:
                angle = 45.0 if nu11 > 0 else -45.0
            else:
                angle = 0.5 * np.degrees(np.arctan2(2 * nu11, nu20 - nu02))
            
            angle = angle % 180
            
            # 计算置信度
            lambda1 = (nu20 + nu02 + np.sqrt((nu20 - nu02)**2 + 4*nu11**2)) / 2
            lambda2 = (nu20 + nu02 - np.sqrt((nu20 - nu02)**2 + 4*nu11**2)) / 2
            
            if lambda1 > 1e-10:
                eccentricity = np.sqrt(1 - lambda2/(lambda1 + 1e-10))
            else:
                eccentricity = 0
            
            pressure_directional_strength = np.sqrt((nu20 - nu02)**2 + 4*nu11**2)
            pressure_concentration = self._calculate_pressure_concentration(pressure_matrix, cx, cy)
            
            base_confidence = min(1.0, eccentricity * 2)
            directional_confidence = min(1.0, pressure_directional_strength * 10)
            concentration_confidence = pressure_concentration
            
            final_confidence = (
                base_confidence * 0.4 + 
                directional_confidence * 0.4 + 
                concentration_confidence * 0.2
            ) * (0.5 + 0.5 * pressure_quality)
            
            print(f"✅ [Moments] 角度: {angle:.1f}°, 偏心度: {eccentricity:.3f}, 置信度: {final_confidence:.3f}")
            
            return {
                'angle': float(angle),
                'confidence': float(final_confidence),
                'eccentricity': float(eccentricity),
                'pressure_concentration': float(pressure_concentration),
                'directional_strength': float(pressure_directional_strength),
                'method': 'pressure_weighted_moments'
            }
            
        except Exception as e:
            print(f"❌ [Moments] 压力加权形状矩分析失败: {e}")
            return {'angle': None, 'confidence': 0}
    
    def _calculate_pressure_concentration(self, pressure_matrix, cx, cy):
        """计算压力集中度"""
        try:
            rows, cols = pressure_matrix.shape
            y_indices, x_indices = np.mgrid[0:rows, 0:cols]
            
            distances = np.sqrt((x_indices - cx)**2 + (y_indices - cy)**2)
            
            total_pressure = np.sum(pressure_matrix)
            if total_pressure == 0:
                return 0
            
            weighted_avg_distance = np.sum(pressure_matrix * distances) / total_pressure
            max_possible_distance = np.sqrt(rows**2 + cols**2) / 2
            concentration = max(0, 1 - weighted_avg_distance / max_possible_distance)
            
            return concentration
            
        except Exception as e:
            print(f"⚠️ 压力集中度计算失败: {e}")
            return 0.5
    
    def _enhanced_covariance_analysis(self, pressure_matrix, pressure_quality):
        """增强协方差分析 - 完整版"""
        try:
            print(f"🔍 [Covariance] 开始增强协方差分析...")
            
            max_pressure = np.max(pressure_matrix)
            adaptive_threshold = max_pressure * 0.15
            
            valid_mask = pressure_matrix > adaptive_threshold
            
            if np.sum(valid_mask) < 5:
                return {'angle': None, 'confidence': 0}
            
            rows, cols = pressure_matrix.shape
            y_indices, x_indices = np.mgrid[0:rows, 0:cols]
            
            valid_y = y_indices[valid_mask]
            valid_x = x_indices[valid_mask]
            weights = pressure_matrix[valid_mask]
            
            total_weight = np.sum(weights)
            mean_x = np.sum(valid_x * weights) / total_weight
            mean_y = np.sum(valid_y * weights) / total_weight
            
            dx = valid_x - mean_x
            dy = valid_y - mean_y
            
            cov_xx = np.sum(weights * dx * dx) / total_weight
            cov_yy = np.sum(weights * dy * dy) / total_weight
            cov_xy = np.sum(weights * dx * dy) / total_weight
            
            # 特征值分解
            trace = cov_xx + cov_yy
            det = cov_xx * cov_yy - cov_xy**2
            
            discriminant = trace**2 - 4*det
            if discriminant < 0:
                return {'angle': None, 'confidence': 0}
            
            lambda1 = (trace + np.sqrt(discriminant)) / 2
            lambda2 = (trace - np.sqrt(discriminant)) / 2
            
            # 主方向角度
            if abs(cov_xy) < 1e-10:
                angle = 0 if cov_xx > cov_yy else 90
            else:
                angle = np.degrees(np.arctan2(lambda1 - cov_xx, cov_xy))
            
            angle = angle % 180
            
            # 置信度计算
            if lambda1 > 1e-10:
                eccentricity = np.sqrt(1 - lambda2/(lambda1 + 1e-10))
            else:
                eccentricity = 0
            
            gradient_consistency = self._check_gradient_consistency(pressure_matrix, angle)
            distribution_quality = self._assess_pressure_distribution_quality(pressure_matrix, valid_mask)
            
            base_confidence = min(1.0, eccentricity * 1.5)
            final_confidence = (
                base_confidence * 0.5 + 
                gradient_consistency * 0.3 + 
                distribution_quality * 0.2
            ) * (0.6 + 0.4 * pressure_quality)
            
            print(f"✅ [Covariance] 角度: {angle:.1f}°, 偏心度: {eccentricity:.3f}, 置信度: {final_confidence:.3f}")
            
            return {
                'angle': float(angle),
                'confidence': float(final_confidence),
                'eccentricity': float(eccentricity),
                'gradient_consistency': float(gradient_consistency),
                'distribution_quality': float(distribution_quality),
                'method': 'enhanced_covariance'
            }
            
        except Exception as e:
            print(f"❌ [Covariance] 增强协方差分析失败: {e}")
            return {'angle': None, 'confidence': 0}
    
    def _check_gradient_consistency(self, pressure_matrix, estimated_angle):
        """检查梯度一致性"""
        try:
            grad_y, grad_x = np.gradient(pressure_matrix)
            
            gradient_angles = np.arctan2(grad_y, grad_x)
            gradient_angles_deg = np.degrees(gradient_angles) % 180
            
            angle_diffs = np.abs(gradient_angles_deg - estimated_angle)
            angle_diffs = np.minimum(angle_diffs, 180 - angle_diffs)
            
            weights = pressure_matrix / (np.sum(pressure_matrix) + 1e-10)
            weighted_consistency = np.sum(weights * np.exp(-angle_diffs / 30))
            
            return min(1.0, weighted_consistency)
            
        except Exception as e:
            print(f"⚠️ 梯度一致性检查失败: {e}")
            return 0.5
    
    def _assess_pressure_distribution_quality(self, pressure_matrix, valid_mask):
        """评估压力分布质量"""
        try:
            valid_pressures = pressure_matrix[valid_mask]
            
            if len(valid_pressures) == 0:
                return 0
            
            # 1. 压力动态范围
            pressure_range = np.max(valid_pressures) - np.min(valid_pressures)
            pressure_mean = np.mean(valid_pressures)
            dynamic_range_score = min(1.0, pressure_range / (pressure_mean + 1e-10))
            
            # 2. 压力平滑性
            smoothness_score = self._calculate_pressure_smoothness(pressure_matrix)
            
            # 3. 有效区域连通性
            connectivity_score = self._calculate_region_connectivity(valid_mask)
            
            quality = (
                dynamic_range_score * 0.4 + 
                smoothness_score * 0.3 + 
                connectivity_score * 0.3
            )
            
            return min(1.0, quality)
            
        except Exception as e:
            print(f"⚠️ 压力分布质量评估失败: {e}")
            return 0.5
    
    def _calculate_pressure_smoothness(self, pressure_matrix):
        """计算压力平滑性"""
        try:
            diff_h = np.abs(np.diff(pressure_matrix, axis=1))
            diff_v = np.abs(np.diff(pressure_matrix, axis=0))
            
            avg_diff = (np.mean(diff_h) + np.mean(diff_v)) / 2
            avg_pressure = np.mean(pressure_matrix[pressure_matrix > 0])
            smoothness = max(0, 1 - avg_diff / (avg_pressure + 1e-10))
            
            return smoothness
            
        except Exception as e:
            print(f"⚠️ 压力平滑性计算失败: {e}")
            return 0.5
    
    def _calculate_region_connectivity(self, valid_mask):
        """计算区域连通性"""
        try:
            if SCIPY_AVAILABLE:
                from scipy import ndimage
                labeled_array, num_features = ndimage.label(valid_mask)
                
                if num_features == 0:
                    return 0
                
                largest_component_size = 0
                for i in range(1, num_features + 1):
                    component_size = np.sum(labeled_array == i)
                    largest_component_size = max(largest_component_size, component_size)
                
                total_valid_pixels = np.sum(valid_mask)
                connectivity = largest_component_size / (total_valid_pixels + 1e-10)
                
                return connectivity
            else:
                # 简化的连通性计算
                return 0.8  # 假设合理的连通性
            
        except Exception as e:
            print(f"⚠️ 区域连通性计算失败: {e}")
            return 0.5
    
    def _pressure_weighted_multiscale_analysis(self, pressure_matrix, pressure_quality):
        """压力加权多尺度分析 - 完整版"""
        try:
            print(f"🔍 [Multiscale] 开始压力加权多尺度分析...")
            
            matrix_size = min(pressure_matrix.shape)
            scales = [
                matrix_size / 32,
                matrix_size / 16,
                matrix_size / 8,
                matrix_size / 4
            ]
            scales = [max(0.5, s) for s in scales]
            
            scale_results = []
            
            for scale in scales:
                smoothed = self._apply_gaussian_smoothing(pressure_matrix, scale)
                scale_analysis = self._single_scale_pressure_analysis(smoothed, scale)
                
                if scale_analysis['angle'] is not None:
                    scale_results.append({
                        'angle': scale_analysis['angle'],
                        'confidence': scale_analysis['confidence'],
                        'scale': scale,
                        'magnitude': scale_analysis.get('magnitude', 0)
                    })
            
            if not scale_results:
                return {'angle': None, 'confidence': 0}
            
            # 尺度加权融合
            scale_weights = []
            for result in scale_results:
                scale = result['scale']
                optimal_scale = matrix_size / 12
                weight = np.exp(-((scale - optimal_scale) / optimal_scale)**2)
                scale_weights.append(weight * result['confidence'])
            
            if sum(scale_weights) == 0:
                return {'angle': None, 'confidence': 0}
            
            # 加权角度平均（圆形平均）
            total_weight = sum(scale_weights)
            angles_rad = [np.radians(r['angle']) for r in scale_results]
            weights_norm = [w / total_weight for w in scale_weights]
            
            cos_sum = sum(w * np.cos(a) for w, a in zip(weights_norm, angles_rad))
            sin_sum = sum(w * np.sin(a) for w, a in zip(weights_norm, angles_rad))
            
            final_angle = np.degrees(np.arctan2(sin_sum, cos_sum)) % 180
            
            # 多尺度一致性评估
            angles = [r['angle'] for r in scale_results]
            angle_consistency = self._calculate_multiscale_consistency(angles, scale_weights)
            
            avg_confidence = sum(r['confidence'] * w for r, w in zip(scale_results, weights_norm))
            final_confidence = avg_confidence * angle_consistency * (0.7 + 0.3 * pressure_quality)
            
            print(f"✅ [Multiscale] 角度: {final_angle:.1f}°, 尺度数: {len(scale_results)}, 置信度: {final_confidence:.3f}")
            
            return {
                'angle': float(final_angle),
                'confidence': float(final_confidence),
                'scale_count': len(scale_results),
                'angle_consistency': float(angle_consistency),
                'method': 'pressure_weighted_multiscale'
            }
            
        except Exception as e:
            print(f"❌ [Multiscale] 压力加权多尺度分析失败: {e}")
            return {'angle': None, 'confidence': 0}
    
    def _apply_gaussian_smoothing(self, pressure_matrix, sigma):
        """应用高斯平滑"""
        if SCIPY_AVAILABLE:
            from scipy import ndimage
            return ndimage.gaussian_filter(pressure_matrix.astype(float), sigma=sigma)
        else:
            # 简单平滑替代
            from .core_functions import create_simple_gaussian_filter
            return create_simple_gaussian_filter(pressure_matrix, sigma)
    
    def _single_scale_pressure_analysis(self, smoothed_matrix, scale):
        """单尺度压力分析"""
        try:
            grad_y, grad_x = np.gradient(smoothed_matrix)
            
            weights = smoothed_matrix + 1e-10
            total_weight = np.sum(weights)
            
            if total_weight == 0:
                return {'angle': None, 'confidence': 0}
            
            avg_gx = np.sum(grad_x * weights) / total_weight
            avg_gy = np.sum(grad_y * weights) / total_weight
            
            magnitude = np.sqrt(avg_gx**2 + avg_gy**2)
            angle = np.degrees(np.arctan2(avg_gy, avg_gx)) % 180
            
            max_pressure = np.max(smoothed_matrix)
            confidence = min(1.0, magnitude / (max_pressure + 1e-10) * 5)
            
            return {
                'angle': angle,
                'confidence': confidence,
                'magnitude': magnitude
            }
            
        except Exception as e:
            print(f"⚠️ 单尺度分析失败: {e}")
            return {'angle': None, 'confidence': 0}
    
    def _calculate_multiscale_consistency(self, angles, weights):
        """计算多尺度角度一致性"""
        try:
            if len(angles) < 2:
                return 1.0
            
            total_weight = sum(weights)
            weighted_angles = []
            
            for i, angle1 in enumerate(angles):
                for j, angle2 in enumerate(angles[i+1:], i+1):
                    diff = min(abs(angle1 - angle2), 180 - abs(angle1 - angle2))
                    weight = (weights[i] + weights[j]) / (2 * total_weight)
                    weighted_angles.append(diff * weight)
            
            avg_diff = sum(weighted_angles)
            consistency = max(0, 1 - avg_diff / 30)
            
            return consistency
            
        except Exception as e:
            print(f"⚠️ 多尺度一致性计算失败: {e}")
            return 0.5
    
    def _pressure_distribution_fourier_analysis(self, pressure_matrix, pressure_quality):
        """压力分布傅里叶方向分析 - 完整版"""
        try:
            print(f"🔍 [Fourier] 开始压力分布傅里叶分析...")
            
            pressure_centered = pressure_matrix - np.mean(pressure_matrix)
            
            # 应用窗口函数减少边缘效应
            rows, cols = pressure_matrix.shape
            window_r = np.hanning(rows).reshape(-1, 1)
            window_c = np.hanning(cols).reshape(1, -1)
            window_2d = window_r * window_c
            
            windowed_pressure = pressure_centered * window_2d
            
            # 2D FFT分析
            fft_result = np.fft.fft2(windowed_pressure)
            fft_magnitude = np.abs(np.fft.fftshift(fft_result))
            
            # 移除DC分量
            center_r, center_c = rows // 2, cols // 2
            fft_magnitude[center_r, center_c] = 0
            
            # 径向-角度分析
            directional_energy = self._calculate_directional_energy(fft_magnitude)
            
            if not directional_energy or max(directional_energy) == 0:
                return {'angle': None, 'confidence': 0}
            
            # 找到主导方向
            max_energy_idx = np.argmax(directional_energy)
            num_directions = len(directional_energy)
            dominant_angle = (max_energy_idx * 180.0 / num_directions) % 180
            
            # 能量集中度置信度
            max_energy = directional_energy[max_energy_idx]
            total_energy = sum(directional_energy)
            energy_concentration = max_energy / (total_energy + 1e-10)
            
            # 频谱质量评估
            spectral_quality = self._assess_spectral_quality(fft_magnitude)
            
            base_confidence = min(1.0, energy_concentration * 3)
            quality_adjusted_confidence = base_confidence * spectral_quality * (0.6 + 0.4 * pressure_quality)
            
            print(f"✅ [Fourier] 角度: {dominant_angle:.1f}°, 能量集中度: {energy_concentration:.3f}, 置信度: {quality_adjusted_confidence:.3f}")
            
            return {
                'angle': float(dominant_angle),
                'confidence': float(quality_adjusted_confidence),
                'energy_concentration': float(energy_concentration),
                'spectral_quality': float(spectral_quality),
                'method': 'pressure_fourier'
            }
            
        except Exception as e:
            print(f"❌ [Fourier] 压力分布傅里叶分析失败: {e}")
            return {'angle': None, 'confidence': 0}
    
    def _calculate_directional_energy(self, fft_magnitude):
        """计算方向能量分布"""
        try:
            rows, cols = fft_magnitude.shape
            center_r, center_c = rows // 2, cols // 2
            
            y, x = np.ogrid[:rows, :cols]
            y, x = y - center_r, x - center_c
            angles = np.arctan2(y, x)
            
            radii = np.sqrt(x**2 + y**2)
            
            valid_mask = (radii > 2) & (radii < min(rows, cols) // 4)
            
            num_directions = 90
            direction_step = np.pi / num_directions
            directional_energy = []
            
            for i in range(num_directions):
                angle_start = -np.pi/2 + i * direction_step
                angle_end = angle_start + direction_step
                
                angle_mask = ((angles >= angle_start) & (angles < angle_end)) | \
                            ((angles >= angle_start + np.pi) & (angles < angle_end + np.pi))
                
                combined_mask = valid_mask & angle_mask
                energy = np.sum(fft_magnitude[combined_mask]) if np.any(combined_mask) else 0
                directional_energy.append(energy)
            
            return directional_energy
            
        except Exception as e:
            print(f"⚠️ 方向能量计算失败: {e}")
            return []
    
    def _assess_spectral_quality(self, fft_magnitude):
        """评估频谱质量"""
        try:
            max_magnitude = np.max(fft_magnitude)
            min_magnitude = np.min(fft_magnitude[fft_magnitude > 0])
            dynamic_range = max_magnitude / (min_magnitude + 1e-10)
            dynamic_range_score = min(1.0, np.log10(dynamic_range) / 3)
            
            total_energy = np.sum(fft_magnitude**2)
            sorted_energies = np.sort(fft_magnitude.flatten())**2
            cumulative_energy = np.cumsum(sorted_energies[::-1])
            energy_90_idx = np.where(cumulative_energy >= 0.9 * total_energy)[0]
            if len(energy_90_idx) > 0:
                concentration = 1.0 - energy_90_idx[0] / len(sorted_energies)
            else:
                concentration = 0.5
            
            spectral_quality = (dynamic_range_score + concentration) / 2
            
            return min(1.0, spectral_quality)
            
        except Exception as e:
            print(f"⚠️ 频谱质量评估失败: {e}")
            return 0.5
    
    def _gradient_guided_morphology_analysis(self, pressure_matrix, pressure_quality):
        """梯度引导形态学分析 - 完整版"""
        try:
            print(f"🔍 [Gradient-Guided] 开始梯度引导形态学分析...")
            
            grad_y, grad_x = np.gradient(pressure_matrix)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            gradient_direction = np.arctan2(grad_y, grad_x)
            
            magnitude_threshold = np.percentile(gradient_magnitude, 75)
            strong_gradient_mask = gradient_magnitude > magnitude_threshold
            
            if np.sum(strong_gradient_mask) < 5:
                return {'angle': None, 'confidence': 0}
            
            valid_directions = gradient_direction[strong_gradient_mask]
            valid_magnitudes = gradient_magnitude[strong_gradient_mask]
            valid_pressures = pressure_matrix[strong_gradient_mask]
            
            pressure_weights = valid_pressures / (np.sum(valid_pressures) + 1e-10)
            
            cos_sum = np.sum(pressure_weights * np.cos(valid_directions))
            sin_sum = np.sum(pressure_weights * np.sin(valid_directions))
            
            dominant_gradient_angle = np.arctan2(sin_sum, cos_sum)
            dominant_gradient_angle_deg = np.degrees(dominant_gradient_angle) % 180
            
            morphology_consistency = self._verify_with_morphology(pressure_matrix, dominant_gradient_angle_deg)
            
            direction_consistency = self._calculate_gradient_direction_consistency(
                valid_directions, pressure_weights, dominant_gradient_angle)
            
            base_confidence = min(1.0, np.sqrt(cos_sum**2 + sin_sum**2) * 2)
            consistency_confidence = (morphology_consistency + direction_consistency) / 2
            final_confidence = base_confidence * consistency_confidence * (0.7 + 0.3 * pressure_quality)
            
            print(f"✅ [Gradient-Guided] 角度: {dominant_gradient_angle_deg:.1f}°, 形态学一致性: {morphology_consistency:.3f}, 置信度: {final_confidence:.3f}")
            
            return {
                'angle': float(dominant_gradient_angle_deg),
                'confidence': float(final_confidence),
                'morphology_consistency': float(morphology_consistency),
                'direction_consistency': float(direction_consistency),
                'strong_gradient_ratio': float(np.sum(strong_gradient_mask) / strong_gradient_mask.size),
                'method': 'gradient_guided_morphology'
            }
            
        except Exception as e:
            print(f"❌ [Gradient-Guided] 梯度引导形态学分析失败: {e}")
            return {'angle': None, 'confidence': 0}
    
    def _verify_with_morphology(self, pressure_matrix, gradient_angle):
        """用形态学方法验证梯度角度"""
        try:
            moments_result = self._pressure_weighted_moments_analysis(pressure_matrix, 1.0)
            
            if moments_result['angle'] is None:
                return 0.5
            
            angle_diff = abs(gradient_angle - moments_result['angle'])
            angle_diff = min(angle_diff, 180 - angle_diff)
            
            consistency = max(0, 1 - angle_diff / 45)
            
            return consistency
            
        except Exception as e:
            print(f"⚠️ 形态学验证失败: {e}")
            return 0.5
    
    def _calculate_gradient_direction_consistency(self, directions, weights, dominant_direction):
        """计算梯度方向一致性"""
        try:
            direction_diffs = np.abs(directions - dominant_direction)
            direction_diffs = np.minimum(direction_diffs, 2*np.pi - direction_diffs)
            
            consistency_scores = np.exp(-direction_diffs / (np.pi/6))
            weighted_consistency = np.sum(weights * consistency_scores)
            
            return min(1.0, weighted_consistency)
            
        except Exception as e:
            print(f"⚠️ 方向一致性计算失败: {e}")
            return 0.5

# 导出接口
__all__ = ['MorphologyAnalyzer']