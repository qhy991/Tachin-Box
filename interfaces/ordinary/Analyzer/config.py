"""
配置模块 - config.py
定义所有分析器的配置参数
"""

from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# 检查可用库
try:
    from numba import jit
    NUMBA_AVAILABLE = True
    print("✅ Numba加速可用")
except ImportError:
    NUMBA_AVAILABLE = False
    print("⚠️ Numba不可用，使用NumPy实现")
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

try:
    from scipy.ndimage import gaussian_filter, sobel
    from scipy.linalg import eigh
    SCIPY_AVAILABLE = True
    print("✅ SciPy完整功能可用")
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️ SciPy不可用，使用备用实现")

try:
    import cv2
    CV2_AVAILABLE = True
    print("✅ OpenCV可用")
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV不可用，使用NumPy实现")

@dataclass
class AnalysisConfig:
    """完整分析配置类"""
    # 基础参数
    cell_spacing_x: float = 1.0
    cell_spacing_y: float = 1.0
    pressure_threshold: float = 0.005
    smoothing_sigma: float = 0.5
    min_grad_magnitude: float = 0.01
    gradient_operator: str = "sobel"
    gradient_epsilon: float = 1e-10
    
    # 窗口参数
    adaptive_peak_window_enabled: bool = True
    adaptive_peak_window_min_size: int = 7
    adaptive_peak_window_max_size: int = 21
    adaptive_peak_window_scale_factor: float = 1.0
    adaptive_peak_window_base_offset: int = 3
    fixed_peak_window_size: int = 11
    
    # 压力质量评估参数
    min_effective_pressure_ratio: float = 0.1
    noise_estimation_method: str = 'mad'
    gradient_consistency_weight: float = 0.3
    pressure_distribution_weight: float = 0.4
    shape_clarity_weight: float = 0.3
    
    # 性能优化参数
    enable_numba_acceleration: bool = True
    enable_result_caching: bool = True
    enable_parallel_methods: bool = False
    cache_size: int = 64

@dataclass
class WindowConfig:
    """窗口配置类"""
    peak_window_size: int = 7
    cop_window_size: int = 5
    grid_window_size: int = 3

# 全局库可用性标志
__all__ = [
    'AnalysisConfig', 
    'WindowConfig', 
    'NUMBA_AVAILABLE', 
    'SCIPY_AVAILABLE', 
    'CV2_AVAILABLE', 
    'jit'
]