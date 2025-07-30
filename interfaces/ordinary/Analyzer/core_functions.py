"""
核心计算函数模块 - core_functions.py
包含所有高性能优化的核心计算函数
"""

import numpy as np
from .config import NUMBA_AVAILABLE, SCIPY_AVAILABLE, jit, sobel

# ==============================================================================
# Numba优化的核心计算函数
# ==============================================================================

if NUMBA_AVAILABLE:
    @jit(nopython=True, cache=True)
    def fast_gradient_sobel(matrix):
        """Numba优化的Sobel梯度计算"""
        rows, cols = matrix.shape
        grad_x = np.zeros_like(matrix)
        grad_y = np.zeros_like(matrix)
        
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                # Sobel X
                grad_x[i, j] = (
                    -matrix[i-1, j-1] - 2*matrix[i, j-1] - matrix[i+1, j-1] +
                    matrix[i-1, j+1] + 2*matrix[i, j+1] + matrix[i+1, j+1]
                ) / 8.0
                
                # Sobel Y  
                grad_y[i, j] = (
                    -matrix[i-1, j-1] - 2*matrix[i-1, j] - matrix[i-1, j+1] +
                    matrix[i+1, j-1] + 2*matrix[i+1, j] + matrix[i+1, j+1]
                ) / 8.0
        
        return grad_x, grad_y

    @jit(nopython=True, cache=True)
    def fast_weighted_gradient_sum(grad_x, grad_y, weights, mask):
        """快速加权梯度求和"""
        total_weight = 0.0
        sum_gx = 0.0
        sum_gy = 0.0
        
        rows, cols = grad_x.shape
        for i in range(rows):
            for j in range(cols):
                if mask[i, j]:
                    w = weights[i, j]
                    total_weight += w
                    sum_gx += grad_x[i, j] * w
                    sum_gy += grad_y[i, j] * w
        
        if total_weight > 0:
            return sum_gx / total_weight, sum_gy / total_weight
        return 0.0, 0.0

    @jit(nopython=True, cache=True)
    def fast_moments_calculation(pressure_matrix, threshold):
        """快速矩计算"""
        rows, cols = pressure_matrix.shape
        m00 = 0.0
        m10 = 0.0
        m01 = 0.0
        
        for i in range(rows):
            for j in range(cols):
                if pressure_matrix[i, j] > threshold:
                    p = pressure_matrix[i, j]
                    m00 += p
                    m10 += j * p
                    m01 += i * p
        
        if m00 == 0:
            return 0.0, 0.0, 0.0, 0.0, 0.0
        
        cx = m10 / m00
        cy = m01 / m00
        
        # 二阶中心矩
        mu20 = 0.0
        mu02 = 0.0
        mu11 = 0.0
        
        for i in range(rows):
            for j in range(cols):
                if pressure_matrix[i, j] > threshold:
                    p = pressure_matrix[i, j]
                    dx = j - cx
                    dy = i - cy
                    mu20 += p * dx * dx
                    mu02 += p * dy * dy
                    mu11 += p * dx * dy
        
        return cx, cy, mu20/m00, mu02/m00, mu11/m00

    @jit(nopython=True, cache=True)
    def fast_axial_asymmetry(gx_matrix, gy_matrix):
        """快速轴向不对称计算"""
        rows, cols = gx_matrix.shape
        if rows == 0 or cols == 0:
            return 0.0, 0.0
        
        # 水平不对称
        mid_col = cols // 2
        sum_abs_gx_left = 0.0
        sum_abs_gx_right = 0.0
        
        for i in range(rows):
            for j in range(mid_col):
                sum_abs_gx_left += abs(gx_matrix[i, j])
            right_start = mid_col + (1 if cols % 2 == 1 else 0)
            for j in range(right_start, cols):
                sum_abs_gx_right += abs(gx_matrix[i, j])
        
        hor_asymmetry = sum_abs_gx_left - sum_abs_gx_right
        
        # 垂直不对称
        mid_row = rows // 2
        sum_abs_gy_top = 0.0
        sum_abs_gy_bottom = 0.0
        
        for i in range(mid_row):
            for j in range(cols):
                sum_abs_gy_top += abs(gy_matrix[i, j])
        
        bottom_start = mid_row + (1 if rows % 2 == 1 else 0)
        for i in range(bottom_start, rows):
            for j in range(cols):
                sum_abs_gy_bottom += abs(gy_matrix[i, j])
        
        vert_asymmetry = sum_abs_gy_top - sum_abs_gy_bottom
        
        return hor_asymmetry, vert_asymmetry

    @jit(nopython=True, cache=True)
    def fast_grid_gradient_analysis(gx_matrix, gy_matrix):
        """快速网格梯度分析 - 返回9个网格的梯度和"""
        rows, cols = gx_matrix.shape
        if rows < 3 or cols < 3:
            return np.zeros(18)  # 9个网格，每个2个值
        
        grid_rows = max(1, rows // 3)
        grid_cols = max(1, cols // 3)
        
        grid_sums = np.zeros(18)
        
        for r_idx in range(3):
            for c_idx in range(3):
                start_row = r_idx * grid_rows
                end_row = (r_idx + 1) * grid_rows if r_idx < 2 else rows
                start_col = c_idx * grid_cols
                end_col = (c_idx + 1) * grid_cols if c_idx < 2 else cols
                
                if start_row < rows and start_col < cols:
                    sum_gx = 0.0
                    sum_gy = 0.0
                    for i in range(start_row, end_row):
                        for j in range(start_col, end_col):
                            sum_gx += gx_matrix[i, j]
                            sum_gy += gy_matrix[i, j]
                    
                    idx = r_idx * 3 + c_idx
                    grid_sums[idx * 2] = sum_gx
                    grid_sums[idx * 2 + 1] = sum_gy
        
        return grid_sums

else:
    # NumPy备用实现
    def fast_gradient_sobel(matrix):
        """NumPy版本的梯度计算"""
        if SCIPY_AVAILABLE:
            grad_x = sobel(matrix, axis=1)
            grad_y = sobel(matrix, axis=0)
            return grad_x, grad_y
        else:
            grad_y, grad_x = np.gradient(matrix)
            return grad_x, grad_y
    
    def fast_weighted_gradient_sum(grad_x, grad_y, weights, mask):
        """NumPy版本的加权梯度求和"""
        valid_weights = weights[mask]
        valid_gx = grad_x[mask]
        valid_gy = grad_y[mask]
        
        if len(valid_weights) == 0:
            return 0.0, 0.0
        
        total_weight = np.sum(valid_weights)
        sum_gx = np.sum(valid_gx * valid_weights)
        sum_gy = np.sum(valid_gy * valid_weights)
        
        return sum_gx / total_weight, sum_gy / total_weight
    
    def fast_moments_calculation(pressure_matrix, threshold):
        """NumPy版本的矩计算"""
        valid_mask = pressure_matrix > threshold
        if not np.any(valid_mask):
            return 0.0, 0.0, 0.0, 0.0, 0.0
        
        y_indices, x_indices = np.mgrid[:pressure_matrix.shape[0], :pressure_matrix.shape[1]]
        valid_pressures = pressure_matrix[valid_mask]
        valid_x = x_indices[valid_mask]
        valid_y = y_indices[valid_mask]
        
        m00 = np.sum(valid_pressures)
        cx = np.sum(valid_x * valid_pressures) / m00
        cy = np.sum(valid_y * valid_pressures) / m00
        
        dx = valid_x - cx
        dy = valid_y - cy
        
        mu20 = np.sum(valid_pressures * dx * dx) / m00
        mu02 = np.sum(valid_pressures * dy * dy) / m00
        mu11 = np.sum(valid_pressures * dx * dy) / m00
        
        return cx, cy, mu20, mu02, mu11
    
    def fast_axial_asymmetry(gx_matrix, gy_matrix):
        """NumPy版本的轴向不对称计算"""
        rows, cols = gx_matrix.shape
        
        mid_col = cols // 2
        left_sum = np.sum(np.abs(gx_matrix[:, :mid_col])) if mid_col > 0 else 0
        right_start = mid_col + (1 if cols % 2 == 1 else 0)
        right_sum = np.sum(np.abs(gx_matrix[:, right_start:])) if right_start < cols else 0
        hor_asymmetry = left_sum - right_sum
        
        mid_row = rows // 2
        top_sum = np.sum(np.abs(gy_matrix[:mid_row, :])) if mid_row > 0 else 0
        bottom_start = mid_row + (1 if rows % 2 == 1 else 0)
        bottom_sum = np.sum(np.abs(gy_matrix[bottom_start:, :])) if bottom_start < rows else 0
        vert_asymmetry = top_sum - bottom_sum
        
        return hor_asymmetry, vert_asymmetry
    
    def fast_grid_gradient_analysis(gx_matrix, gy_matrix):
        """NumPy版本的网格梯度分析"""
        rows, cols = gx_matrix.shape
        if rows < 3 or cols < 3:
            return np.zeros(18)
        
        grid_rows = max(1, rows // 3)
        grid_cols = max(1, cols // 3)
        
        grid_sums = []
        for r_idx in range(3):
            for c_idx in range(3):
                start_row = r_idx * grid_rows
                end_row = (r_idx + 1) * grid_rows if r_idx < 2 else rows
                start_col = c_idx * grid_cols
                end_col = (c_idx + 1) * grid_cols if c_idx < 2 else cols
                
                sum_gx = np.sum(gx_matrix[start_row:end_row, start_col:end_col])
                sum_gy = np.sum(gy_matrix[start_row:end_row, start_col:end_col])
                grid_sums.extend([sum_gx, sum_gy])
        
        return np.array(grid_sums)

# ==============================================================================
# 通用工具函数
# ==============================================================================

def create_simple_gaussian_filter(matrix, sigma):
    """简单的高斯滤波实现（当SciPy不可用时）"""
    if sigma <= 0:
        return matrix.astype(np.float32)
    
    kernel_size = max(1, int(sigma * 6))
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # 创建高斯核
    x = np.arange(kernel_size) - kernel_size // 2
    kernel_1d = np.exp(-0.5 * (x / sigma) ** 2)
    kernel_1d /= np.sum(kernel_1d)
    
    # 分离卷积
    result = matrix.astype(np.float32)
    
    # 水平卷积
    pad_width = kernel_size // 2
    padded = np.pad(result, pad_width, mode='edge')
    temp = np.zeros_like(result)
    
    for i in range(result.shape[0]):
        for j in range(result.shape[1]):
            temp[i, j] = np.sum(padded[i + pad_width, j:j + kernel_size] * kernel_1d)
    
    # 垂直卷积
    padded = np.pad(temp, pad_width, mode='edge')
    for i in range(result.shape[0]):
        for j in range(result.shape[1]):
            result[i, j] = np.sum(padded[i:i + kernel_size, j + pad_width] * kernel_1d)
    
    return result

def preprocess_pressure_matrix(pressure_matrix, sigma, use_scipy=True):
    """预处理压力矩阵"""
    if use_scipy and SCIPY_AVAILABLE:
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(
            pressure_matrix.astype(np.float32, copy=False), 
            sigma=sigma,
            mode='nearest'
        )
    else:
        return create_simple_gaussian_filter(pressure_matrix, sigma)

# 导出接口
__all__ = [
    'fast_gradient_sobel',
    'fast_weighted_gradient_sum', 
    'fast_moments_calculation',
    'fast_axial_asymmetry',
    'fast_grid_gradient_analysis',
    'preprocess_pressure_matrix'
]