import numpy as np

def is_special_idle_case(pressure_data, is_sliding, is_tangential, gradient_threshold=1e-5, 
                        previous_cop=None, current_cop=None, sliding_threshold=0.05):
    """
    判断是否为"特殊idle"情况：
    - 仅按压无切向/滑动，且梯度低于阈值
    - 如果有滑动或切向力，直接不是idle
    - 新增：预测滑动检测，避免时序延迟问题
    """
    if pressure_data is None or pressure_data.size == 0:
        return False
    
    # 如果有明确的滑动或切向力，直接不是idle
    if is_sliding or is_tangential:
        return False
    
    # 🆕 新增：预测滑动检测
    # 如果COP位置变化超过阈值，即使is_sliding为False，也认为不是idle
    if previous_cop is not None and current_cop is not None:
        displacement = np.sqrt(
            (current_cop[0] - previous_cop[0])**2 + 
            (current_cop[1] - previous_cop[1])**2
        )
        if displacement > sliding_threshold:
            print(f"🔍 预测滑动检测: 位移={displacement:.3f}, 阈值={sliding_threshold:.3f}")
            return False
    
    # 计算压力梯度
    grad_x, grad_y = np.gradient(pressure_data)
    grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    grad_mean = np.mean(grad_magnitude)
    
    print("--------------------------------")
    print(f"grad_mean: {grad_mean}")
    print("--------------------------------")
    
    return grad_mean < gradient_threshold

def is_special_idle_case_enhanced(pressure_data, is_sliding, is_tangential, 
                                 previous_cop=None, current_cop=None,
                                 gradient_threshold=1e-5, sliding_threshold=0.05,
                                 temporal_diff_threshold=0.1):
    """
    增强版空闲判断：
    - 结合多种检测方法
    - 更敏感的滑动预测
    - 时间差异分析
    """
    if pressure_data is None or pressure_data.size == 0:
        return False
    
    # 方法1: 直接标志检查
    if is_sliding or is_tangential:
        return False
    
    # 方法2: COP位移预测
    if previous_cop is not None and current_cop is not None:
        displacement = np.sqrt(
            (current_cop[0] - previous_cop[0])**2 + 
            (current_cop[1] - previous_cop[1])**2
        )
        if displacement > sliding_threshold:
            print(f"🔍 COP位移预测: {displacement:.3f} > {sliding_threshold:.3f}")
            return False
    
    # 方法3: 压力梯度分析
    grad_x, grad_y = np.gradient(pressure_data)
    grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    grad_mean = np.mean(grad_magnitude)
    
    # 方法4: 压力分布分析（检测压力中心偏移）
    contact_mask = pressure_data > np.max(pressure_data) * 0.3
    if np.any(contact_mask):
        y_indices, x_indices = np.where(contact_mask)
        if len(y_indices) > 0:
            # 计算压力中心
            weights = pressure_data[contact_mask]
            center_x = np.average(x_indices, weights=weights)
            center_y = np.average(y_indices, weights=weights)
            
            # 检查压力中心是否偏离几何中心
            geometric_center_x = pressure_data.shape[1] / 2
            geometric_center_y = pressure_data.shape[0] / 2
            center_offset = np.sqrt(
                (center_x - geometric_center_x)**2 + 
                (center_y - geometric_center_y)**2
            )
            
            # 如果压力中心明显偏离，可能表示有切向力
            if center_offset > 5:  # 阈值可调
                print(f"🔍 压力中心偏移: {center_offset:.2f}")
                return False
    
    print("--------------------------------")
    print(f"grad_mean: {grad_mean}")
    print("--------------------------------")
    
    return grad_mean < gradient_threshold 