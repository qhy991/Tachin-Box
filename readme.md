# 基于压力传感器的推箱子游戏系统

## 📖 项目简介

这是一个基于压力传感器的智能推箱子游戏系统，采用模块化分层架构设计，集成了高性能传感器数据处理、智能双模式控制系统、路径规划功能和实时可视化界面。

### 🎯 核心特性

- **智能双模式控制**：摇杆模式和触控板模式自动切换
- **路径规划系统**：预设路径和自定义路径支持
- **高性能优化**：多线程架构，支持多种性能模式
- **传感器兼容**：支持USB、串口、CAN、蓝牙等多种接口
- **实时可视化**：基于PyQt5的高性能图形界面

## 🏗️ 系统架构

### 核心架构层次

```
┌─────────────────────────────────────┐
│           主程序层                    │  ← box_game_app_optimized.py
├─────────────────────────────────────┤
│           游戏核心层                  │  ← BoxGameCoreOptimized
├─────────────────────────────────────┤
│           传感器接口层                │  ← SensorDataThread, RealSensorInterface
├─────────────────────────────────────┤
│           UI渲染层                   │  ← BoxGameRenderer, BoxGameControlPanel
├─────────────────────────────────────┤
│           路径规划层                  │  ← PathPlanningGameEnhancer
├─────────────────────────────────────┤
│           智能控制层                  │  ← SmartControlSystem
└─────────────────────────────────────┘
```

### 数据流架构

```
传感器硬件 → 驱动层 → 数据处理器 → 游戏核心 → UI渲染
     ↓           ↓         ↓         ↓        ↓
  压力矩阵 → 原始数据 → 预处理数据 → 游戏状态 → 可视化
```

## 📦 主要依赖模块

### 1. 核心依赖库

| 模块 | 版本要求 | 用途 |
|------|----------|------|
| PyQt5 | >=5.15.0 | GUI框架 |
| numpy | >=1.21.0 | 数值计算和数组操作 |
| scipy | >=1.7.0 | 科学计算 |
| pandas | >=1.3.0 | 数据处理 |
| matplotlib | >=3.5.0 | 图表绘制 |
| seaborn | >=0.11.0 | 统计图表 |
| opencv-python | >=4.5.0 | 图像处理 |
| Pillow | >=8.3.0 | 图像操作 |
| scikit-image | >=0.18.0 | 图像分析 |

### 2. 传感器驱动模块

```
backends/
├── sensor_driver.py          # 传感器驱动抽象层
├── usb_driver.py            # USB传感器驱动
├── serial_driver_v1.py      # 串口传感器驱动
├── can_driver.py            # CAN总线传感器驱动
└── ble_driver.py            # 蓝牙传感器驱动
```

### 3. 数据处理模块

```
data_processing/
├── data_handler.py          # 数据处理器
├── preprocessing.py         # 数据预处理
├── sensor_calibrate.py      # 传感器校准
└── interpolation.py         # 数据插值
```

### 4. 游戏核心模块

```
interfaces/ordinary/BoxGame/
├── box_game_app_optimized.py     # 主程序入口
├── run_box_game_optimized.py     # 游戏启动器
├── box_game_core_v2.py           # 游戏核心引擎
├── box_game_renderer.py          # 游戏渲染器
├── box_game_control_panel.py     # 控制面板
├── box_smart_control_system.py   # 智能控制系统
├── box_game_path_planning.py     # 路径规划系统
└── contact_filter.py             # 接触检测过滤器
```

## 🔧 关键技术特性

### 1. 智能双模式控制系统

- **摇杆模式**：轻微滑动时，基于COP位移方向的相对控制
- **触控板模式**：明显滑动时，基于COP位移的相对控制
- **自动模式切换**：根据COP距离阈值自动切换控制模式

### 2. 路径规划系统

- **预设路径**：提供多种预设游戏路径
- **自定义路径**：支持用户创建自定义路径
- **实时导航**：提供路径进度和导航信息
- **完成统计**：记录路径完成时间和统计数据

### 3. 高性能优化

- **帧率配置**：支持低性能、标准、高性能、极限四种模式
- **多线程架构**：传感器数据采集、游戏逻辑、UI渲染分离
- **COP专用模式**：简化切向力分析，专注于COP控制

### 4. 传感器接口抽象

- **真实传感器**：支持USB、串口、CAN、蓝牙等多种接口
- **模拟传感器**：提供鼠标控制的模拟数据
- **统一接口**：抽象化传感器操作，便于扩展

## 🚀 安装指南

### 系统要求

- **Python版本**：>= 3.7
- **操作系统**：Windows/Linux/macOS
- **硬件要求**：支持USB/串口/CAN/蓝牙的压力传感器
- **内存要求**：建议4GB以上
- **存储空间**：约500MB（包含依赖库）

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd box-demo
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **验证安装**
```bash
python box_game_app_optimized.py
```

## 🎮 使用指南

### 启动游戏

```bash
python box_game_app_optimized.py
```

### 基本操作

1. **连接传感器**
   - 点击控制面板中的"连接传感器"按钮
   - 选择正确的传感器端口
   - 等待连接成功提示

2. **开始游戏**
   - 连接成功后自动开始数据采集
   - 在传感器上按压并滑动手指控制箱子移动
   - 观察实时压力数据和游戏状态

3. **路径模式**
   - 在控制面板中选择预设路径
   - 启用路径模式获得导航指引
   - 按照路径点移动箱子完成任务

4. **参数调整**
   - 在控制面板中调整压力阈值、滑动阈值等参数
   - 实时观察参数变化对游戏体验的影响

### 控制模式说明

#### 摇杆模式（轻微滑动）
- **触发条件**：COP位移距离 < 4.5单位
- **控制方式**：基于COP位移方向的相对控制
- **适用场景**：精确控制，小幅度移动

#### 触控板模式（明显滑动）
- **触发条件**：COP位移距离 >= 4.5单位
- **控制方式**：基于COP位移的相对控制
- **适用场景**：快速移动，大幅度操作

## 🔬 核心算法

### 1. COP计算
```python
def calculate_cop(self, pressure_data):
    # 基于压力加权平均计算压力中心
    valid_mask = pressure_data > self.pressure_threshold
    total_pressure = np.sum(pressure_data[valid_mask])
    cop_x = np.sum(x_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
    cop_y = np.sum(y_indices[valid_mask] * pressure_data[valid_mask]) / total_pressure
```

### 2. 接触检测
```python
def detect_contact(self, pressure_data):
    # 基于压力阈值和接触面积判断接触状态
    max_pressure = np.max(pressure_data)
    contact_mask = pressure_data > self.pressure_threshold
    contact_area = np.sum(contact_mask)
    return contact_area >= self.contact_area_threshold
```

### 3. 滑动检测
```python
def detect_sliding(self, current_cop):
    # 基于COP位移距离判断滑动状态
    dx = current_cop[0] - self.initial_cop[0]
    dy = current_cop[1] - self.initial_cop[1]
    movement_distance = np.sqrt(dx*dx + dy*dy)
    return movement_distance > self.sliding_threshold
```

## 📊 性能模式配置

| 模式 | 传感器FPS | 渲染FPS | 核心FPS | 适用场景 |
|------|-----------|---------|---------|----------|
| 低性能 | 15 | 15 | 15 | 省电模式，低配置设备 |
| 标准 | 30 | 30 | 30 | 平衡模式，标准体验 |
| 高性能 | 60 | 60 | 60 | 高帧率模式，流畅体验 |
| 极限 | 120 | 120 | 120 | 极限性能，高配置设备 |

## 🛠️ 开发指南

### 项目结构
```
box-demo/
├── box_game_app_optimized.py      # 主程序入口
├── requirements.txt               # 依赖配置
├── README.md                      # 项目文档
├── backends/                      # 传感器驱动
├── data_processing/               # 数据处理
├── interfaces/                    # 界面模块
│   └── ordinary/
│       └── BoxGame/              # 游戏核心模块
├── config/                        # 配置文件
└── utils/                         # 工具模块
```

### 扩展开发

1. **添加新的传感器驱动**
   - 在`backends/`目录下创建新的驱动文件
   - 继承`AbstractSensorDriver`基类
   - 实现必要的接口方法

2. **自定义路径规划**
   - 在`PathPlanningGameEnhancer`中添加新的路径类型
   - 实现路径生成算法
   - 更新UI界面支持

3. **优化控制算法**
   - 修改`SmartControlSystem`中的控制逻辑
   - 调整阈值参数和灵敏度设置
   - 测试不同场景下的控制效果

## 🐛 故障排除

### 常见问题

1. **传感器连接失败**
   - 检查传感器硬件连接
   - 确认驱动程序已正确安装
   - 验证端口权限设置

2. **游戏运行缓慢**
   - 降低性能模式设置
   - 关闭不必要的后台程序
   - 检查系统资源使用情况

3. **控制响应异常**
   - 调整压力阈值参数
   - 重新校准传感器
   - 检查接触检测逻辑

### 调试模式

启用详细日志输出：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues：[GitHub Issues](https://github.com/your-repo/issues)
- 邮箱：your-email@example.com

---

**注意**：本项目仅供学习和研究使用，请确保遵守相关法律法规和传感器使用规范。#   T a c h i n - B o x  
 #   T a c h i n - B o x  
 