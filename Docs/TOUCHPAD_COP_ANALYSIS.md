# Touchpad模式下COP距离计算与初始COP确定机制分析 📊

## 概述

本文档详细分析了推箱子游戏中touchpad模式下的COP（Center of Pressure，压力中心）距离计算机制和初始COP的确定过程。这是理解箱子位置变化控制逻辑的核心。

## 🎯 核心概念

### COP（压力中心）
- **定义**：传感器上压力分布的中心点，基于压力分布的加权平均计算
- **坐标系**：64x64网格，(0,0)在左上角，X向右，Y向下
- **计算方式**：`COP = Σ(位置 × 压力) / Σ(压力)`

### 初始COP（Initial COP）
- **定义**：手指刚接触传感器时的COP位置
- **作用**：作为后续COP位移计算的参考基准点
- **生命周期**：从接触开始到接触结束

## 🔄 COP距离计算流程

### 1. COP计算实现

```python
def calculate_cop(self, pressure_data):
    """计算压力中心"""
    if pressure_data is None or pressure_data.size == 0:
        return None
    
    # 过滤低压力点
    valid_mask = pressure_data > self.pressure_threshold
    if not np.any(valid_mask):
        return None
    
    # 计算加权中心
    rows, cols = pressure_data.shape
    y_indices, x_indices = np.mgrid[0:rows, 0:cols]
    
    total_pressure = np.sum(pressure_data[valid_mask])
    if total_pressure == 0:
        return None
    
    # COP计算公式：加权平均
    cop_x = np.sum(x_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
    cop_y = np.sum(y_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
    
    return (cop_x, cop_y)
```

**计算原理**：
- 使用压力阈值过滤有效压力点
- 对每个有效点计算：`位置 × 压力值`
- 求和后除以总压力得到加权平均位置

### 2. 初始COP确定机制

```python
def detect_sliding(self, current_cop):
    """检测滑动状态并确定初始COP"""
    if current_cop is None:
        return False, 0.0
    
    # 🔑 关键：第一次检测到COP时记录为初始COP
    if self.initial_cop is None:
        self.initial_cop = current_cop
        return False, 0.0
    
    # 计算COP位移距离
    dx = current_cop[0] - self.initial_cop[0]
    dy = current_cop[1] - self.initial_cop[1]
    movement_distance = np.sqrt(dx*dx + dy*dy)
    is_sliding = movement_distance > self.sliding_threshold
    
    return is_sliding, movement_distance
```

**初始COP确定逻辑**：
1. **首次接触**：当`self.initial_cop`为`None`时，将当前COP设为初始COP
2. **持续接触**：使用已确定的初始COP计算位移
3. **接触结束**：重置`initial_cop`为`None`

### 3. 接触状态管理

```python
def update_game_state(self, contact_detected, current_cop, is_sliding,
                     movement_distance, consensus_angle, consensus_confidence):
    # ... 其他代码 ...
    
    # 🔄 处理接触状态变化
    if not contact_detected:
        if self.is_contact:  # 接触结束
            self.smart_control.reset_on_contact_end()  # 重置累积位移
        self.initial_cop = None  # 🔑 重置初始COP
    elif contact_detected and self.initial_cop is None and current_cop is not None:
        # 🔑 刚开始接触时，记录初始COP
        self.initial_cop = current_cop
```

**状态管理逻辑**：
- **接触开始**：`initial_cop = None` → 记录当前COP为初始COP
- **接触持续**：使用已记录的初始COP计算位移
- **接触结束**：`initial_cop = None` → 为下次接触做准备

## 📏 COP距离计算详解

### 1. 距离计算公式

```python
# 计算COP位移向量
dx = current_cop[0] - initial_cop[0]  # X方向位移
dy = current_cop[1] - initial_cop[1]  # Y方向位移

# 计算欧几里得距离
movement_distance = np.sqrt(dx*dx + dy*dy)
```

### 2. 坐标系说明

```
传感器坐标系 (64x64):
(0,0) ──────────────→ X (63,0)
  │
  │
  │
  ↓
Y (0,63) ───────────→ (63,63)

COP位移方向：
- 向右滑动：dx > 0
- 向下滑动：dy > 0  
- 向左滑动：dx < 0
- 向上滑动：dy < 0
```

### 3. 距离阈值判断

```python
def detect_cop_distance_mode(self, current_cop, initial_cop):
    """基于COP距离检测控制模式"""
    if current_cop is None or initial_cop is None:
        return self.IDLE_MODE, 0.0
    
    # 计算COP位移距离
    dx = current_cop[0] - initial_cop[0]
    dy = current_cop[1] - initial_cop[1]
    distance = np.sqrt(dx*dx + dy*dy)
    
    # 基于距离分段判断
    epsilon = 1e-10  # 处理浮点数精度
    if distance < self.joystick_threshold - epsilon:  # 0.05
        return self.IDLE_MODE, distance
    elif distance < self.touchpad_threshold - epsilon:  # 0.12
        return self.JOYSTICK_MODE, distance
    else:
        return self.TOUCHPAD_MODE, distance  # 🖱️ 触控板模式激活
```

## 🖱️ Touchpad模式控制计算

### 1. 目标位置计算

```python
def calculate_touchpad_control(self, current_cop, initial_cop, box_position):
    """触控板模式控制计算 - 相对控制"""
    if current_cop is None or initial_cop is None:
        return box_position
    
    # 🖱️ 计算COP位移 - 传感器坐标系
    cop_displacement = np.array([
        current_cop[0] - initial_cop[0],  # X方向位移（右为正）
        current_cop[1] - initial_cop[1]   # Y方向位移（下为正）
    ])
    
    # 🎯 限制位移范围
    displacement_magnitude = np.linalg.norm(cop_displacement)
    if displacement_magnitude > self.touchpad_max_range:  # 20.0
        cop_displacement = cop_displacement * (self.touchpad_max_range / displacement_magnitude)
    
    # 🖱️ 应用触控板灵敏度和阻尼
    scaled_displacement = cop_displacement * self.touchpad_sensitivity  # 1.2
    self.accumulated_displacement = (self.accumulated_displacement * self.touchpad_damping + 
                                   scaled_displacement * (1 - self.touchpad_damping))
    
    # 📍 计算目标位置 - 相对控制
    target_position = box_position + self.accumulated_displacement
    
    return target_position
```

### 2. 控制参数说明

```python
# 触控板模式参数
self.touchpad_sensitivity = 1.2   # 灵敏度：放大COP位移
self.touchpad_damping = 0.3       # 阻尼：平滑移动，减少抖动
self.touchpad_max_range = 20.0    # 最大范围：限制最大移动距离
self.touchpad_threshold = 0.12    # 触发阈值：激活触控板模式的最小距离
```

### 3. 累积位移机制

```python
# 累积位移更新公式
new_accumulated = old_accumulated * damping + new_displacement * (1 - damping)

# 示例：
# damping = 0.3, new_displacement = [1.0, 0.0]
# new_accumulated = [0.0, 0.0] * 0.3 + [1.0, 0.0] * 0.7 = [0.7, 0.0]
```

## 🔄 物理更新机制

### 1. 箱子位置更新

```python
def update_physics(self):
    """更新箱子位置朝向目标位置"""
    # 平滑移动因子
    movement_factor = 0.15
    
    # 更新箱子位置朝向目标位置
    self.box_position[0] += (self.box_target_position[0] - self.box_position[0]) * movement_factor
    self.box_position[1] += (self.box_target_position[1] - self.box_position[1]) * movement_factor
    
    # 边界限制
    self.box_position[0] = np.clip(self.box_position[0], 5, 59)
    self.box_position[1] = np.clip(self.box_position[1], 5, 59)
```

### 2. 平滑移动原理

```python
# 平滑移动公式
new_position = current_position + (target_position - current_position) * factor

# 示例：
# current = 10.0, target = 20.0, factor = 0.15
# new = 10.0 + (20.0 - 10.0) * 0.15 = 11.5
# 每次更新移动目标距离的15%，实现平滑移动
```

## 📊 调试信息输出

### 1. 滑动检测调试

```python
# 调试输出：滑动检测信息
if movement_distance > 0.01:  # 只在有移动时输出
    print(f"🖱️ 滑动检测: 距离={movement_distance:.3f}, 阈值={self.sliding_threshold:.3f}, 是否滑动={is_sliding}")
    print(f"   COP: 初始=({self.initial_cop[0]:.2f}, {self.initial_cop[1]:.2f}), 当前=({current_cop[0]:.2f}, {current_cop[1]:.2f})")
```

### 2. 调试信息含义

- **距离**：当前COP与初始COP的欧几里得距离
- **阈值**：滑动检测阈值（默认0.08）
- **是否滑动**：距离是否超过阈值
- **初始COP**：手指刚接触时的COP位置
- **当前COP**：当前帧的COP位置

## 🎯 关键特性总结

### 1. 初始COP确定
- **时机**：手指刚接触传感器时
- **条件**：`initial_cop is None` 且 `current_cop is not None`
- **重置**：接触结束时重置为`None`

### 2. COP距离计算
- **公式**：`distance = √((dx)² + (dy)²)`
- **基准**：相对于初始COP的位移
- **精度**：使用epsilon处理浮点数精度问题

### 3. 触控板模式激活
- **条件**：COP距离 ≥ 触控板阈值（0.12）
- **控制**：相对控制，基于当前箱子位置
- **平滑**：使用阻尼系数实现平滑移动

### 4. 状态管理
- **接触开始**：记录初始COP
- **接触持续**：计算COP位移
- **接触结束**：重置初始COP和累积位移

## 🔧 参数调优建议

### 1. 阈值调整
```python
# 更敏感的触控板模式
self.touchpad_threshold = 0.08  # 降低触发阈值

# 更稳定的触控板模式  
self.touchpad_threshold = 0.15  # 提高触发阈值
```

### 2. 灵敏度调整
```python
# 更快的响应
self.touchpad_sensitivity = 1.5  # 提高灵敏度

# 更平滑的移动
self.touchpad_damping = 0.5      # 提高阻尼
```

### 3. 移动范围调整
```python
# 更大的移动范围
self.touchpad_max_range = 30.0   # 增加最大范围

# 更精确的控制
self.touchpad_max_range = 15.0   # 减小最大范围
```

这个分析文档详细解释了touchpad模式下COP距离计算和初始COP确定的完整机制，包括实现细节、参数说明和调优建议。 