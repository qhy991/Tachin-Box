# CPU优化渲染器使用指南

## 概述

CPU优化渲染器是专为CPU环境设计的高性能渲染解决方案，在保持3D渲染功能的同时，大幅提升渲染速度。

## 核心优化特性

### 1. 对象缓存和复用
- **渲染对象池**: 避免频繁创建销毁matplotlib对象
- **数据变化检测**: 只在数据真正变化时才重新渲染
- **缓存命中率监控**: 实时跟踪缓存效果

### 2. 智能帧跳跃
- **自适应跳帧**: 根据性能自动调整渲染频率
- **帧率限制**: 防止过度渲染导致的性能问题
- **最小帧间隔**: 确保渲染间隔不会过短

### 3. 数据预处理优化
- **简化预处理**: 只进行必要的坐标变换
- **禁用昂贵操作**: 默认禁用高斯模糊等耗时操作
- **快速插值**: 使用nearest插值方式提升速度

### 4. 3D渲染保持
- **保持3D功能**: 不强制切换到2D模式
- **简化3D效果**: 禁用抗锯齿和阴影以提升性能
- **引导模式控制**: 只有在引导模式下才允许切换到2D

## 性能模式

### CPU优化模式
- **目标FPS**: 15 FPS
- **跳帧率**: 2
- **特性**: 禁用轨迹显示、高斯模糊、抗锯齿
- **适用场景**: 低性能设备

### 标准模式
- **目标FPS**: 20 FPS
- **跳帧率**: 1
- **特性**: 启用轨迹显示，禁用高斯模糊
- **适用场景**: 一般性能设备

### 高性能模式
- **目标FPS**: 30 FPS
- **跳帧率**: 1
- **特性**: 启用所有效果
- **适用场景**: 高性能设备

## 引导模式控制

### 启用引导模式
```python
# 启用路径模式时自动启用引导模式
renderer.set_guide_mode(True)
```

### 检查引导模式状态
```python
# 检查是否处于引导模式
is_guide = renderer.is_guide_mode_enabled()

# 检查是否可以切换到2D
can_switch = renderer.can_switch_to_2d()
```

### 引导模式特性
- **3D渲染保持**: 非引导模式下保持3D渲染
- **2D切换权限**: 只有在引导模式下才允许切换到2D
- **性能优化**: 引导模式下自动优化渲染参数

## 使用方法

### 1. 启动测试
```bash
# 运行完整测试
python test_cpu_optimized_renderer.py

# 测试性能模式
python test_cpu_optimized_renderer.py performance

# 测试引导模式
python test_cpu_optimized_renderer.py guide

# 基准测试
python test_cpu_optimized_renderer.py benchmark
```

### 2. 性能监控
- **实时FPS**: 控制台每5秒输出一次
- **缓存命中率**: 显示数据缓存效果
- **渲染时间**: 监控单帧渲染耗时
- **性能警告**: 自动检测性能瓶颈

### 3. 快捷键
- **P**: 显示性能汇总
- **H**: 显示帮助信息
- **F11**: 切换全屏模式

## 性能优化建议

### 1. 硬件配置
- **CPU**: 建议4核心以上
- **内存**: 建议8GB以上
- **显卡**: 集成显卡即可，无需独立显卡

### 2. 软件配置
- **Python版本**: 3.7+
- **matplotlib**: 3.3+
- **PyQt5**: 5.15+

### 3. 运行时优化
- **关闭其他程序**: 释放CPU资源
- **降低分辨率**: 减少渲染负担
- **使用CPU优化模式**: 低性能设备首选

## 故障排除

### 1. 帧率过低
- 检查是否启用了CPU优化模式
- 确认没有其他程序占用CPU
- 尝试降低目标FPS

### 2. 3D渲染失败
- 检查matplotlib 3D支持
- 确认引导模式设置
- 查看控制台错误信息

### 3. 内存占用过高
- 检查对象池大小设置
- 确认历史数据长度限制
- 重启应用程序

## 技术细节

### 1. matplotlib优化
```python
# 路径简化
matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 0.1
matplotlib.rcParams['agg.path.chunksize'] = 10000
```

### 2. 数据变化检测
```python
# 使用哈希值检测数据变化
new_hash = hash(pressure_data.tobytes())
if new_hash != self.last_pressure_data_hash:
    # 数据发生变化，需要重新渲染
```

### 3. 对象复用
```python
# 复用matplotlib对象而不是重新创建
if self.cached_objects['pressure_image'] is None:
    # 首次创建
    im = self.ax_pressure.imshow(...)
    self.cached_objects['pressure_image'] = im
else:
    # 只更新数据
    self.cached_objects['pressure_image'].set_array(data)
```

## 更新日志

### v1.0.0
- 初始CPU优化版本
- 实现对象缓存和复用
- 添加智能帧跳跃
- 保持3D渲染功能
- 添加引导模式控制

## 联系信息

如有问题或建议，请联系开发团队。 