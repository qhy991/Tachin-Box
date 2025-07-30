# 触控板模式下箱子位置移动逻辑分析 📊

## 概述

触控板模式是推箱子游戏中的一种控制模式，它基于COP（Center of Pressure，压力中心）的位移来控制箱子的移动。本文档详细分析了触控板模式下的移动逻辑和与COP的关系。

## 🎯 核心概念

### COP（压力中心）
- **定义**：传感器上压力分布的中心点
- **坐标系**：64x64网格，(0,0)在左上角，X向右，Y向下
- **计算方式**：基于压力分布的加权平均

### 触控板模式特点
- **触发条件**：COP位移距离 ≥ 触控板阈值（默认0.12）
- **控制方式**：相对控制（基于当前箱子位置）
- **响应特性**：实时跟随手指滑动

## 🔄 移动逻辑流程

### 1. 数据输入阶段
```
传感器压力数据 → COP计算 → 滑动检测 → 智能控制系统
```

**COP计算**：
```python
def calculate_cop(self, pressure_data):
    valid_mask = pressure_data > self.pressure_threshold
    total_pressure = np.sum(pressure_data[valid_mask])
    cop_x = np.sum(x_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
    cop_y = np.sum(y_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
    return (cop_x, cop_y)
```

**滑动检测**：
```python
def detect_sliding(self, current_cop):
    dx = current_cop[0] - self.initial_cop[0]
    dy = current_cop[1] - self.initial_cop[1]
    movement_distance = np.sqrt(dx*dx + dy*dy)
    is_sliding = movement_distance > self.sliding_threshold
    return is_sliding, movement_distance
```

### 2. 模式判断阶段
```
COP位移距离 → 模式选择 → 触控板模式激活
```

**模式判断逻辑**：
```python
def detect_cop_distance_mode(self, current_cop, initial_cop):
    dx = current_cop[0] - initial_cop[0]
    dy = current_cop[1] - initial_cop[1]
    distance = np.sqrt(dx*dx + dy*dy)
    
    if distance < self.joystick_threshold:  # 0.05
        return self.IDLE_MODE
    elif distance < self.touchpad_threshold:  # 0.12
        return self.JOYSTICK_MODE
    else:
        return self.TOUCHPAD_MODE  # 触控板模式激活
```

### 3. 目标位置计算阶段
```
COP位移 → 相对控制计算 → 目标位置
```

**触控板控制计算**：
```python
def calculate_touchpad_control(self, current_cop, initial_cop, box_position):
    # 1. 计算COP位移
    cop_displacement = np.array([
        current_cop[0] - initial_cop[0],  # X方向位移
        current_cop[1] - initial_cop[1]   # Y方向位移
    ])
    
    # 2. 限制位移范围
    if displacement_magnitude > self.touchpad_max_range:
        cop_displacement = cop_displacement * (self.touchpad_max_range / displacement_magnitude)
    
    # 3. 应用灵敏度和阻尼
    scaled_displacement = cop_displacement * self.touchpad_sensitivity
    self.accumulated_displacement = (self.accumulated_displacement * self.touchpad_damping + 
                                   scaled_displacement * (1 - self.touchpad_damping))
    
    # 4. 计算目标位置（相对控制）
    target_position = box_position + self.accumulated_displacement
    
    return target_position
```

### 4. 物理更新阶段
```
目标位置 → 平滑移动 → 箱子新位置
```

**物理更新**：
```python
def update_physics(self):
    # 平滑移动因子
    movement_factor = 0.15
    
    # 更新箱子位置朝向目标位置
    self.box_position[0] += (self.box_target_position[0] - self.box_position[0]) * movement_factor
    self.box_position[1] += (self.box_target_position[1] - self.box_position[1]) * movement_factor
    
    # 边界限制
    self.box_position[0] = np.clip(self.box_position[0], 5, 59)
    self.box_position[1] = np.clip(self.box_position[1], 5, 59)
```

## 📊 COP与箱子移动的关系

### 1. 直接映射关系
```
手指滑动方向 ↔ 箱子移动方向
手指滑动距离 ↔ 箱子移动距离（经过灵敏度调节）
```

### 2. 坐标系对应
- **传感器坐标系**：(0,0)在左上角，X向右，Y向下
- **游戏坐标系**：与传感器坐标系相同
- **移动映射**：
  - 手指向右滑动 → 箱子向右移动
  - 手指向下滑动 → 箱子向下移动
  - 手指向左滑动 → 箱子向左移动
  - 手指向上滑动 → 箱子向上移动

### 3. 位移计算
```
COP位移 = 当前COP - 初始COP
箱子目标位置 = 当前箱子位置 + 累积位移
```

## ⚙️ 关键参数

### 触控板模式参数
```python
# 触发阈值
self.touchpad_threshold = 0.12    # 触控板模式激活阈值

# 控制参数
self.touchpad_sensitivity = 1.2   # 触控板灵敏度
self.touchpad_damping = 0.3       # 阻尼系数
self.touchpad_max_range = 20.0    # 最大移动范围

# 物理参数
movement_factor = 0.15            # 平滑移动因子
```

### 参数作用
- **touchpad_threshold**：决定何时激活触控板模式
- **touchpad_sensitivity**：控制移动响应速度
- **touchpad_damping**：平滑移动，减少抖动
- **touchpad_max_range**：限制最大移动范围
- **movement_factor**：控制箱子移动的平滑程度

## 🔄 状态管理

### 接触状态变化
```python
# 接触开始
if contact_detected and self.initial_cop is None and current_cop is not None:
    self.initial_cop = current_cop  # 记录初始COP

# 接触结束
if not contact_detected:
    self.smart_control.reset_on_contact_end()  # 重置累积位移
    self.initial_cop = None
```

### 累积位移管理
```python
def reset_on_contact_end(self):
    """接触结束时重置累积位移"""
    self.accumulated_displacement = np.array([0.0, 0.0])
```

## 🎮 用户体验特点

### 优势
1. **直观性**：手指滑动方向直接对应箱子移动方向
2. **精确性**：基于COP的精确位置控制
3. **实时性**：实时响应手指移动
4. **平滑性**：阻尼和平滑因子提供流畅体验

### 限制
1. **阈值依赖**：需要达到触控板阈值才激活
2. **范围限制**：有最大移动范围限制
3. **精度要求**：需要稳定的手指接触

## 🔧 调试信息

### 滑动检测调试
```python
if movement_distance > 0.01:
    print(f"🖱️ 滑动检测: 距离={movement_distance:.3f}, 阈值={self.sliding_threshold:.3f}, 是否滑动={is_sliding}")
    print(f"   COP: 初始=({self.initial_cop[0]:.2f}, {self.initial_cop[1]:.2f}), 当前=({current_cop[0]:.2f}, {current_cop[1]:.2f})")
```

### 控制模式调试
```python
control_info = self.smart_control.get_control_info()
print(f"控制模式: {control_info['mode']}")
print(f"系统模式: {control_info['system_mode']}")
print(f"累积位移: {control_info['displacement']}")
```

## 📈 性能优化

### 计算优化
1. **向量化计算**：使用NumPy进行高效的向量运算
2. **条件判断优化**：只在必要时进行复杂计算
3. **内存管理**：使用deque限制历史数据大小

### 响应优化
1. **实时更新**：每帧都更新COP和箱子位置
2. **平滑处理**：使用阻尼和平滑因子减少抖动
3. **边界检查**：确保箱子始终在有效范围内

## 总结

触控板模式通过以下核心机制实现箱子控制：

1. **COP跟踪**：实时计算和跟踪压力中心位置
2. **位移计算**：基于COP位移计算箱子目标位置
3. **相对控制**：箱子位置相对于当前位置进行移动
4. **平滑处理**：通过阻尼和平滑因子提供流畅体验
5. **状态管理**：正确处理接触开始和结束的状态变化

这种设计使得用户可以通过直观的手指滑动来控制箱子移动，提供了良好的用户体验。 