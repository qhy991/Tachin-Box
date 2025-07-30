"""
主分析器模块 - main_analyzer.py
集成所有分析模块的主控制器
"""

import numpy as np
import time
from typing import Dict, Optional, Tuple, List
from .config import AnalysisConfig, NUMBA_AVAILABLE, SCIPY_AVAILABLE, CV2_AVAILABLE
from .core_functions import preprocess_pressure_matrix
from .gradient_analyzer import GradientAnalyzer
from .morphology_analyzer import MorphologyAnalyzer
from interfaces.ordinary.Analyzer.main_analyzer import CompleteTangentialForceAnalyzer

def resolve_morphology_direction(morph_angle, grad_angle):
    """根据梯度方法的方向，修正形态学主轴方向为有向主轴"""
    if morph_angle is None or grad_angle is None:
        return None
    morph_angle = morph_angle % 180
    grad_angle = grad_angle % 360
    morph_angle_1 = morph_angle
    morph_angle_2 = (morph_angle + 180) % 360
    delta1 = min(abs(grad_angle - morph_angle_1), 360 - abs(grad_angle - morph_angle_1))
    delta2 = min(abs(grad_angle - morph_angle_2), 360 - abs(grad_angle - morph_angle_2))
    if delta2 < delta1:
        return morph_angle_2
    else:
        return morph_angle_1

class CompleteTangentialForceAnalyzer:
    """
    完整切向力分析器 - 模块化版本
    保留所有原版功能，应用V2优化策略，代码结构清晰
    """
    
    def __init__(self, config: AnalysisConfig = None):
        self.config = config or AnalysisConfig()
        
        # 窗口参数设置
        self.current_peak_window_size = self.config.fixed_peak_window_size
        self.current_peak_window_half_size = self.config.fixed_peak_window_size // 2
        
        # 初始化子分析器
        self.gradient_analyzer = GradientAnalyzer(self.config)
        self.morphology_analyzer = MorphologyAnalyzer(self.config)
        
        # 性能统计
        self.performance_stats = {
            'total_frames': 0,
            'total_time': 0.0,
            'avg_time_per_frame': 0.0,
            'method_times': {}
        }
        
        self._print_initialization_info()
    
    def _print_initialization_info(self):
        """打印初始化信息"""
        print(f"🚀 完整切向力分析器初始化完成")
        print(f"📊 Numba加速: {'✅' if NUMBA_AVAILABLE else '❌'}")
        print(f"📊 SciPy完整: {'✅' if SCIPY_AVAILABLE else '❌'}")
        print(f"📊 OpenCV可用: {'✅' if CV2_AVAILABLE else '❌'}")
        
        # 显示可用的分析方法
        summary = self.gradient_analyzer.get_method_summary()
        gradient_count = sum(len(methods) for methods in summary.values())
        morphology_count = 6  # 6个形态学方法
        print(f"📈 可用方法总数: {gradient_count + morphology_count} 个")
        print(f"   - 梯度方法: {gradient_count} 个")
        print(f"   - 形态学方法: {morphology_count} 个")
    
    def process_frame(self, pressure_matrix: np.ndarray, 
                     analysis_window_size: int = None, 
                     enable_timing: bool = False) -> Dict:
        """
        处理单帧 - 完整功能版本
        
        参数:
            pressure_matrix: 压力矩阵
            analysis_window_size: 分析窗口大小（可选）
            enable_timing: 是否启用性能计时
            
        返回:
            完整的分析结果字典
        """
        start_time = time.time() if enable_timing else None
        
        try:
            # 1. 平滑处理
            smoothed_matrix = preprocess_pressure_matrix(
                pressure_matrix, 
                self.config.smoothing_sigma, 
                use_scipy=SCIPY_AVAILABLE
            )
            
            # 2. 获取接触点
            contact_mask = smoothed_matrix > self.config.pressure_threshold
            contact_indices = np.argwhere(contact_mask)

            # 诊断信息
            if enable_timing:
                max_pressure = np.max(smoothed_matrix) if smoothed_matrix.size > 0 else 0
                num_contact_points = len(contact_indices)
                print(f"🔬 [完整分析器] 阈值: {self.config.pressure_threshold:.4f}, "
                      f"最大压力: {max_pressure:.4f}, 接触点: {num_contact_points}")

            if len(contact_indices) == 0:
                if enable_timing:
                    print("⚠️ [完整分析器] 没有找到接触点，分析中止。")
                return self._empty_result()
            
            # 3. 计算全局基本信息
            basic_info = self._calculate_basic_info(smoothed_matrix, contact_mask, contact_indices)
            cop_position = basic_info.get('cop_raw')
            
            # 4. 执行窗口定位与提取
            peak_row, peak_col, _ = self._find_peak_pressure_location(smoothed_matrix, contact_mask)
            peak_position = (peak_row, peak_col) if peak_row is not None else None
        
            focused_window = None
            if peak_row is not None and peak_col is not None:
                if analysis_window_size is not None:
                    ws = analysis_window_size
                    self.current_peak_window_size = ws + 1 if ws % 2 == 0 else ws
                    self.current_peak_window_half_size = self.current_peak_window_size // 2
                else:
                    self._calculate_and_set_current_peak_window_size(contact_indices)
                
                focused_window = self._extract_window_with_padding(smoothed_matrix, peak_row, peak_col)

            # 5. 梯度分析 - 完整版
            gradient_results = {}
            if focused_window is not None and focused_window.max() > self.config.pressure_threshold:
                gradient_results = self.gradient_analyzer.analyze(
                    focused_window, 
                    pressure_threshold=self.config.pressure_threshold,
                    full_matrix=smoothed_matrix,
                    cop_position=cop_position,
                    peak_position=peak_position
                )
            
            # 6. 形态学分析 - 完整版
            shape_results = self.morphology_analyzer.analyze(smoothed_matrix)

            # 7. 融合主轴方向（有向主轴）
            grad_angle = None
            if 'weighted_min_variance' in gradient_results:
                grad_angle = gradient_results['weighted_min_variance'].get('angle')
            
            for method, result in shape_results.items():
                morph_angle = result.get('angle')
                if morph_angle is not None and grad_angle is not None:
                    directed_angle = resolve_morphology_direction(morph_angle, grad_angle)
                    result['directed_angle'] = directed_angle

            # 8. 综合结果
            results = {
                'basic_info': basic_info,
                'gradient_methods': gradient_results,
                'shape_methods': shape_results,
                'analysis_window_details': (peak_row, peak_col, self.current_peak_window_size) if peak_row is not None else None,
                'processing_mode': 'complete_modular',
                'library_availability': {
                    'numba': NUMBA_AVAILABLE,
                    'scipy': SCIPY_AVAILABLE,
                    'opencv': CV2_AVAILABLE
                },
                'config_summary': {
                    'pressure_threshold': self.config.pressure_threshold,
                    'smoothing_sigma': self.config.smoothing_sigma,
                    'gradient_operator': self.config.gradient_operator,
                    'adaptive_window': self.config.adaptive_peak_window_enabled
                }
            }
            
            # 9. 性能统计
            if enable_timing:
                self._update_performance_stats(start_time)
            
            return results
            
        except Exception as e:
            print(f"❌ 完整分析过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_result()
    
    def process_batch(self, pressure_matrices: List[np.ndarray], 
                     enable_timing: bool = True) -> List[Dict]:
        """
        批量处理多帧数据
        
        参数:
            pressure_matrices: 压力矩阵列表
            enable_timing: 是否启用性能计时
            
        返回:
            分析结果列表
        """
        print(f"🔄 开始批量处理 {len(pressure_matrices)} 帧...")
        
        start_time = time.time()
        results = []
        
        # 简单的串行处理，避免进程/线程创建开销
        for i, matrix in enumerate(pressure_matrices):
            if enable_timing and i % 10 == 0:
                print(f"   处理进度: {i+1}/{len(pressure_matrices)}")
            
            result = self.process_frame(matrix, enable_timing=False)
            results.append(result)
        
        total_time = time.time() - start_time
        
        if enable_timing:
            print(f"✅ 批量处理完成:")
            print(f"   总时间: {total_time:.3f}s")
            print(f"   平均每帧: {total_time/len(pressure_matrices)*1000:.2f}ms")
            print(f"   处理速度: {len(pressure_matrices)/total_time:.1f} FPS")
        
        return results
    
    def _calculate_basic_info(self, smoothed_matrix, contact_mask, contact_indices):
        """计算基本信息"""
        contact_pressures = smoothed_matrix[contact_mask]
        total_pressure = np.sum(contact_pressures)

        if total_pressure == 0:
            return {
                'cop_phys': (None, None),
                'peak_phys': (None, None),
                'cop_raw': (None, None),
                'peak_raw': (None, None),
                'total_pressure': 0,
                'max_pressure': np.max(smoothed_matrix) if smoothed_matrix.size > 0 else 0,
                'contact_area': 0,
                'contact_indices': [],
                'contact_mask': contact_mask
            }
        
        cop_row = np.sum(contact_indices[:, 0] * contact_pressures) / total_pressure
        cop_col = np.sum(contact_indices[:, 1] * contact_pressures) / total_pressure
        
        max_pressure_idx = np.unravel_index(np.argmax(smoothed_matrix), smoothed_matrix.shape)
        peak_row, peak_col = max_pressure_idx
        
        return {
            'cop_phys': (cop_row * self.config.cell_spacing_y, cop_col * self.config.cell_spacing_x),
            'peak_phys': (peak_row * self.config.cell_spacing_y, peak_col * self.config.cell_spacing_x),
            'cop_raw': (cop_row, cop_col),
            'peak_raw': (peak_row, peak_col),
            'total_pressure': float(total_pressure),
            'max_pressure': float(np.max(smoothed_matrix)),
            'contact_area': len(contact_indices),
            'contact_indices': contact_indices,
            'contact_mask': contact_mask
        }

    def _find_peak_pressure_location(self, pressure_matrix, contact_mask):
        """查找峰值压力位置"""
        masked_pressure = pressure_matrix * contact_mask
        if not np.any(masked_pressure): 
            return None, None, None
        peak_idx = np.unravel_index(np.argmax(masked_pressure), pressure_matrix.shape)
        return peak_idx[0], peak_idx[1], pressure_matrix[peak_idx]

    def _calculate_and_set_current_peak_window_size(self, contact_indices):
        """计算并设置当前峰值窗口大小"""
        if self.config.adaptive_peak_window_enabled and contact_indices is not None and len(contact_indices) > 0:
            min_r, max_r = np.min(contact_indices[:, 0]), np.max(contact_indices[:, 0])
            min_c, max_c = np.min(contact_indices[:, 1]), np.max(contact_indices[:, 1])
            char_len = max(max_r - min_r + 1, max_c - min_c + 1)
            size = int(self.config.adaptive_peak_window_base_offset + self.config.adaptive_peak_window_scale_factor * char_len)
            size = size + 1 if size % 2 == 0 else size
            self.current_peak_window_size = np.clip(size, 
                                                  self.config.adaptive_peak_window_min_size, 
                                                  self.config.adaptive_peak_window_max_size)
        else:
            self.current_peak_window_size = self.config.fixed_peak_window_size
        self.current_peak_window_half_size = self.current_peak_window_size // 2

    def _extract_window_with_padding(self, matrix, center_row, center_col):
        """提取窗口并填充"""
        half = self.current_peak_window_half_size
        window_size = self.current_peak_window_size
        padded_matrix = np.pad(matrix, half, mode='constant', constant_values=0)
        padded_center_row, padded_center_col = center_row + half, center_col + half
        return padded_matrix[padded_center_row-half : padded_center_row+half+1, 
                             padded_center_col-half : padded_center_col+half+1]
    
    def _update_performance_stats(self, start_time: float):
        """更新性能统计"""
        frame_time = time.time() - start_time
        self.performance_stats['total_frames'] += 1
        self.performance_stats['total_time'] += frame_time
        self.performance_stats['avg_time_per_frame'] = (
            self.performance_stats['total_time'] / self.performance_stats['total_frames']
        )
    
    def _empty_result(self) -> Dict:
        """返回空结果"""
        return {
            'basic_info': {
                'cop_phys': (None, None),
                'peak_phys': (None, None),
                'cop_raw': (None, None),
                'peak_raw': (None, None),
                'total_pressure': 0,
                'max_pressure': 0,
                'contact_area': 0,
                'contact_indices': np.array([]),
                'contact_mask': None
            },
            'gradient_methods': {},
            'shape_methods': {},
            'processing_mode': 'complete_modular'
        }
    
    def get_performance_report(self) -> Dict:
        """获取性能报告"""
        return {
            'frames_processed': self.performance_stats['total_frames'],
            'total_time_seconds': self.performance_stats['total_time'],
            'average_time_per_frame_ms': self.performance_stats['avg_time_per_frame'] * 1000,
            'frames_per_second': 1.0 / self.performance_stats['avg_time_per_frame'] if self.performance_stats['avg_time_per_frame'] > 0 else 0,
            'config': {
                'pressure_threshold': self.config.pressure_threshold,
                'numba_available': NUMBA_AVAILABLE,
                'scipy_available': SCIPY_AVAILABLE,
                'opencv_available': CV2_AVAILABLE
            }
        }
    
    def get_method_summary(self) -> Dict:
        """获取所有可用方法的摘要"""
        gradient_summary = self.gradient_analyzer.get_method_summary()
        
        morphology_methods = [
            'gabor_filter',
            'shape_moments', 
            'covariance_analysis',
            'multiscale_analysis',
            'fourier_direction',
            'gradient_guided_morphology'
        ]
        
        return {
            'gradient_methods': gradient_summary,
            'morphology_methods': morphology_methods,
            'total_gradient_methods': sum(len(methods) for methods in gradient_summary.values()),
            'total_morphology_methods': len(morphology_methods),
            'library_status': {
                'numba': NUMBA_AVAILABLE,
                'scipy': SCIPY_AVAILABLE,
                'opencv': CV2_AVAILABLE
            }
        }
    
    def print_analysis_summary(self, results: Dict):
        """打印分析结果摘要"""
        if not results or 'basic_info' not in results:
            print("❌ 无有效分析结果")
            return
        
        print("\n" + "="*60)
        print("📊 切向力分析结果摘要")
        print("="*60)
        
        # 基本信息
        basic_info = results['basic_info']
        cop = basic_info.get('cop_phys', (None, None))
        peak = basic_info.get('peak_phys', (None, None))
        
        print(f"📍 基本信息:")
        print(f"   压力中心 (CoP): ({cop[0]:.2f}, {cop[1]:.2f})" if cop[0] is not None else "   压力中心: 无效")
        print(f"   峰值位置: ({peak[0]:.2f}, {peak[1]:.2f})" if peak[0] is not None else "   峰值位置: 无效")
        print(f"   总压力: {basic_info.get('total_pressure', 0):.3f}")
        print(f"   接触面积: {basic_info.get('contact_area', 0)} 像素")
        
        # 梯度方法结果
        gradient_methods = results.get('gradient_methods', {})
        if gradient_methods:
            print(f"\n🔍 梯度方法 ({len(gradient_methods)} 个):")
            for method, data in gradient_methods.items():
                angle = data.get('angle')
                conf = data.get('confidence', 0)
                if angle is not None:
                    print(f"   {method:<30}: {angle:6.1f}° (置信度: {conf:.3f})")
                else:
                    print(f"   {method:<30}: 无效")
        
        # 形态学方法结果
        shape_methods = results.get('shape_methods', {})
        if shape_methods:
            print(f"\n🔬 形态学方法 ({len(shape_methods)} 个):")
            for method, data in shape_methods.items():
                angle = data.get('angle')
                directed_angle = data.get('directed_angle')
                conf = data.get('confidence', 0)
                if angle is not None:
                    angle_str = f"{angle:6.1f}°"
                    if directed_angle is not None:
                        angle_str += f" (有向: {directed_angle:6.1f}°)"
                    print(f"   {method:<30}: {angle_str} (置信度: {conf:.3f})")
                else:
                    print(f"   {method:<30}: 无效")
        
        # 处理信息
        processing_mode = results.get('processing_mode', 'unknown')
        library_availability = results.get('library_availability', {})
        
        print(f"\n⚙️ 处理信息:")
        print(f"   处理模式: {processing_mode}")
        print(f"   库可用性: Numba={library_availability.get('numba', False)}, "
              f"SciPy={library_availability.get('scipy', False)}, "
              f"OpenCV={library_availability.get('opencv', False)}")
        
        print("="*60)

# 导出接口
__all__ = ['CompleteTangentialForceAnalyzer', 'resolve_morphology_direction']