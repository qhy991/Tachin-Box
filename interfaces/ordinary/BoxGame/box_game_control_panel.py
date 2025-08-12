import numpy as np
import sys
import os

# PyQt5 相关导入
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QCheckBox, QComboBox
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QLineEdit, QRadioButton, QSlider
from PyQt5.QtCore import Qt

# Matplotlib 相关导入
import matplotlib.pyplot as plt

# 🎨 集成utils功能
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../utils'))
    from utils import apply_dark_theme
    UTILS_AVAILABLE = True
    print("✅ utils功能已集成到控制面板")
except ImportError as e:
    print(f"⚠️ utils功能不可用: {e}")
    UTILS_AVAILABLE = False


# 科学计算相关导入
from scipy import ndimage
from skimage import measure, morphology
try:
    from skimage.feature import peak_local_maxima
except ImportError:
    # 备用导入或自定义实现
    from scipy.ndimage import maximum_filter
    def peak_local_maxima(image, min_distance=1, threshold_abs=None):
        """简单的峰值检测实现"""
        if threshold_abs is None:
            threshold_abs = 0.1
        
        # 使用最大值滤波器找局部最大值
        local_maxima = maximum_filter(image, size=min_distance) == image
        local_maxima = local_maxima & (image > threshold_abs)
        
        # 返回峰值坐标
        peaks = np.where(local_maxima)
        return np.column_stack(peaks)



class BoxGameControlPanel(QWidget):
    """推箱子游戏控制面板"""
    
    # 信号定义
    parameter_changed = pyqtSignal(dict)
    visualization_changed = pyqtSignal(dict)
    # 新增路径规划信号
    path_mode_requested = pyqtSignal(str, bool)  # path_name, enabled
    path_reset_requested = pyqtSignal()
    custom_path_requested = pyqtSignal(str, list)  # name, points
    # 新增传感器控制信号
    sensor_connect_requested = pyqtSignal(str)  # port
    sensor_disconnect_requested = pyqtSignal()
    data_stop_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 🎛️ 控制参数
        self.parameters = {
            'pressure_threshold': 0.001,  # 提高压力阈值，减少噪声影响
            'contact_area_threshold': 3,  # 提高接触面积阈值，减少噪声影响
            'tangential_threshold': 0.05,
            'sliding_threshold': 0.08,
            'box_speed': 2.0,
            'friction': 0.8,
            'analysis_smoothing': 0.7
        }
        
        # 🎨 可视化选项
        self.visualization_options = {
            'show_pressure': True,
            'show_cop': True,
            'show_force_vector': True,
            'show_analysis_info': True,
            'show_debug_info': False,
            'pressure_colormap': 'hot',
            'force_scale': 1.0,
            'heatmap_mode': '2d'  # 默认使用2D模式以提高性能
        }
        
        # 🎨 3D渲染选项 - 新增保存机制
        self.three_d_rendering_options = {
            'enable_3d_lighting': True,
            'enable_3d_shadows': True,
            'enable_3d_animation': False,  # 禁用3D动画旋转
            'elevation_3d': 45.0,          # 固定45度仰角
            'azimuth_3d': 315.0,           # 修正为315度方位角（-45度）
            'rotation_speed_3d': 0.0,      # 旋转速度设为0
            'surface_alpha_3d': 0.8,
            'enable_wireframe': True,  # 默认启动网格
            'enable_anti_aliasing': True,
            'enable_bloom_effect': False
        }
        
        # 🎨 平滑选项 - 新增保存机制
        self.smoothing_options = {
            'preprocessing_enabled': True,
            'use_gaussian_blur': True,
            'use_xy_swap': False,
            'use_custom_colormap': True,
            'log_y_lim': [0.0, 0.1],  # 更新默认颜色范围为0.1
            'gaussian_sigma': 1.0
        }
        
        # 🆕 新增idle分析状态
        self.idle_analysis = None
        
        # 🎨 应用深色主题
        if UTILS_AVAILABLE:
            apply_dark_theme(self)
            print("🎨 控制面板已应用深色主题")
        else:
            print("⚠️ utils不可用，使用默认主题")
        
        self.init_ui()
        print("✅ BoxGameControlPanel 初始化完成")
    
    def init_ui(self):
        """初始化用户界面"""
        # self.setFixedWidth(350)  # 移除固定宽度，让面板自适应
        
        # 🎨 统一设置样式系统
        self.setStyleSheet("""
            QWidget {
                padding: 2px;
            }
            
            /* 统一按钮样式 */
            QPushButton {
                border: 2px solid #FFFFFF !important;
                border-radius: 6px !important;
                margin: 2px;
                padding: 8px 12px;
                font-size: 12px !important;
                font-weight: bold !important;
                font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif !important;
                min-height: 20px;
            }
            QPushButton:hover {
                border: 2px solid #E0E0E0 !important;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                border: 2px solid #CCCCCC !important;
                transform: translateY(0px);
            }
            QPushButton:disabled {
                border: 2px solid #666666 !important;
                background-color: #444444 !important;
                color: #888888 !important;
            }
            
            /* 统一下拉框样式 */
            QComboBox {
                border: 2px solid #FFFFFF !important;
                border-radius: 6px !important;
                margin: 2px;
                padding: 6px 10px;
                font-size: 12px !important;
                font-weight: bold !important;
                font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif !important;
                background-color: #333333;
                color: #FFFFFF;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 2px solid #E0E0E0 !important;
            }
            QComboBox:focus {
                border: 2px solid #4CAF50 !important;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
                margin-right: 5px;
            }
            
            /* 统一输入框样式 */
            QLineEdit {
                border: 2px solid #FFFFFF !important;
                border-radius: 6px !important;
                margin: 2px;
                padding: 6px 10px;
                font-size: 12px !important;
                font-weight: bold !important;
                font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif !important;
                background-color: #333333;
                color: #FFFFFF;
                min-height: 20px;
            }
            QLineEdit:hover {
                border: 2px solid #E0E0E0 !important;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50 !important;
            }
            
            /* 统一分组框样式 */
            QGroupBox {
                border: 2px solid #666666 !important;
                border-radius: 8px !important;
                margin: 5px !important;
                padding: 15px 5px 5px 5px !important;
                background-color: transparent !important;
                font-size: 12px !important;
                font-weight: bold !important;
                font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif !important;
            }
            QGroupBox::title {
                subcontrol-origin: border;
                subcontrol-position: top center;
                left: 0px;
                top: 8px;
                padding: 0px 8px 0px 8px;
                color: white !important;
                font-weight: bold !important;
                font-size: 12px !important;
                font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif !important;
                background-color: #000000;
                border: none !important;
                text-align: center;
            }
            
            /* 统一标签样式 */
            QLabel {
                color: white !important;
                font-size: 12px !important;
                font-weight: bold !important;
                font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif !important;
            }
            
            /* 统一复选框样式 */
            QCheckBox {
                color: #FFFFFF !important;
                font-size: 12px !important;
                font-weight: bold !important;
                font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif !important;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 4px;
                background-color: #333333;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4CAF50;
                background-color: #4CAF50;
            }
            QCheckBox::indicator:checked::after {
                content: "✓";
                color: white;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
                line-height: 18px;
            }
        """)
        
        # 📐 主布局 - 改为水平布局以适应顶部位置
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(5)  # 减少间距
        main_layout.setContentsMargins(25, 25, 25, 25)  # 进一步增加边距，确保边框不被遮挡
        
        # 🎨 Logo显示组
        self.create_logo_group(main_layout)
        
        # 路径引导分组
        self.create_path_planning_group(main_layout)
        
        # 🎛️ 传感器控制组
        self.create_sensor_control_group(main_layout)
        
        # 🎨 可视化控制组
        self.create_visualization_control_group(main_layout)
        
        # 📊 状态显示组 - 新增
        self.create_status_group(main_layout)
        
        # 🔄 添加弹性空间
        main_layout.addStretch()
        
        # 在主界面右上角添加设置按钮
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.clicked.connect(self.on_settings_clicked)
        main_layout.addWidget(self.settings_btn, alignment=Qt.AlignRight)
        # 移除分析参数设置按钮，现在所有选项都集成到主设置对话框中
    
    def create_logo_group(self, parent_layout):
        """创建Logo显示组"""
        # 🎨 直接使用QLabel，不使用GroupBox
        logo_label = QLabel()
        logo_label.setFixedSize(120, 120)  # 设置固定大小
        logo_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                padding: 5px;
            }
        """)
        
        # 尝试加载logo图片
        try:
            from PyQt5.QtGui import QPixmap
            logo_path = os.path.join(os.path.dirname(__file__), '../../../utils/logo_dark.png')
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                # 缩放图片以适应标签大小
                scaled_pixmap = pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                print(f"✅ Logo已加载: {logo_path}")
            else:
                # 如果找不到图片，显示文字
                logo_label.setText("KTACHIN")
                logo_label.setStyleSheet("""
                    QLabel {
                        background-color: transparent;
                        padding: 2px;
                        color: white;
                        font-weight: bold;
                        font-size: 14px;
                        text-align: center;
                    }
                """)
                print(f"⚠️ 未找到Logo图片: {logo_path}")
        except Exception as e:
            print(f"❌ 加载Logo失败: {e}")
            # 显示默认文字
            logo_label.setText("KTACHIN")
            logo_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    padding: 2px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    text-align: center;
                }
            """)
        
        parent_layout.addWidget(logo_label)
    
    def create_game_control_group(self, parent_layout):
        """创建游戏控制组"""
        group = QGroupBox("游戏控制")
        group.setFixedHeight(60)  # 固定高度，与其他组保持一致
        group.setMinimumWidth(100)  # 进一步减少最小宽度，因为移除了重置按钮
        layout = QHBoxLayout(group)  # 改为水平布局
        layout.setContentsMargins(5, 5, 5, 5)  # 减少内边距
        layout.setSpacing(5)  # 减少间距
        
        # 🎮 游戏控制组现在为空，只作为占位符
        # 如果需要添加其他游戏控制功能，可以在这里添加
        
        parent_layout.addWidget(group)
    
    def create_path_planning_group(self, parent_layout):
        group = QGroupBox("路径引导")
        group.setMaximumHeight(120)  # 限制高度以适应顶部布局
        group.setMinimumWidth(360)  # 增加最小宽度，确保所有控件都能显示
        layout = QHBoxLayout(group)  # 改为水平布局
        layout.setContentsMargins(5, 5, 5, 5)  # 减少内边距
        layout.setSpacing(5)  # 减少间距

        # 路径引导开关按钮
        self.path_guide_btn = QPushButton("🎮 开启游戏")
        self.path_guide_btn.setCheckable(True)  # 可切换的按钮
        self.path_guide_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:checked {
                background-color: #FF5722;
            }
            QPushButton:checked:hover {
                background-color: #E64A19;
            }
        """)
        self.path_guide_btn.clicked.connect(self.on_path_guide_toggled)
        layout.addWidget(self.path_guide_btn)

        # 路径选择
        self.path_combo = QComboBox()
        self.path_combo.addItem("请选择路径")
        self.path_combo.setMinimumWidth(120)  # 设置最小宽度
        layout.addWidget(self.path_combo)

        # 重置路径进度
        self.path_reset_btn = QPushButton("重置路径进度")
        self.path_reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(self.path_reset_btn)

        parent_layout.addWidget(group, 1)  # 添加拉伸权重1

        # 信号连接
        self.path_combo.currentTextChanged.connect(self.on_path_selected)
        self.path_reset_btn.clicked.connect(self.on_path_reset_clicked)

    def on_path_guide_toggled(self):
        """路径引导开关按钮点击事件"""
        is_checked = self.path_guide_btn.isChecked()
        path_name = self.path_combo.currentText()
        
        # 更新按钮文本和样式
        if is_checked:
            self.path_guide_btn.setText("🎮 关闭游戏")
            print("🗺️ 路径引导已开启")
            
            # 🎨 路径引导开启时自动切换到2D模式
            if self.heatmap_2d_3d_btn.text() == "3D热力图":
                print("🎨 路径引导模式：自动切换到2D热力图以提高性能")
                self.heatmap_2d_3d_btn.setText("2D热力图")
                self.heatmap_2d_3d_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                # 发送切换到2D模式的信号
                self.visualization_changed.emit({'toggle_heatmap_mode': True})
        else:
            self.path_guide_btn.setText("🎮 开启游戏")
            print("🗺️ 路径引导已关闭")
            # 关闭路径引导时保持当前的热力图模式，不自动切换
        
        # 如果有选择路径，发送路径模式请求
        if path_name and path_name != "请选择路径":
            self.path_mode_requested.emit(path_name, is_checked)
        else:
            # 如果没有选择路径，只发送开关状态
            self.path_mode_requested.emit("", is_checked)

    def on_path_selected(self, path_name):
        # 如果路径引导按钮已开启，自动启用路径模式
        if self.path_guide_btn.isChecked() and path_name != "请选择路径":
            # 🎨 路径引导开启且选择路径时，确保切换到2D模式
            if self.heatmap_2d_3d_btn.text() == "3D热力图":
                print("🎨 路径引导模式：自动切换到2D热力图以提高性能")
                self.heatmap_2d_3d_btn.setText("2D热力图")
                self.heatmap_2d_3d_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                # 发送切换到2D模式的信号
                self.visualization_changed.emit({'toggle_heatmap_mode': True})
            
            self.path_mode_requested.emit(path_name, True)

    def on_path_reset_clicked(self):
        self.path_reset_requested.emit()

    def set_path_list(self, path_list):
        self.path_combo.blockSignals(True)
        self.path_combo.clear()
        self.path_combo.addItem("请选择路径")
        self.path_combo.addItems(path_list)
        self.path_combo.blockSignals(False)
    
    
    def create_sensor_control_group(self, parent_layout):
        """创建传感器控制组"""
        group = QGroupBox("传感器控制")
        group.setMaximumHeight(120)  # 限制高度以适应顶部布局
        layout = QHBoxLayout(group)  # 改为水平布局
        layout.setContentsMargins(5, 5, 5, 5)  # 减少内边距
        layout.setSpacing(5)  # 减少间距
        
        # 端口输入
        port_label = QLabel("端口:")
        layout.addWidget(port_label)
        
        self.port_input = QLineEdit("0")
        self.port_input.setPlaceholderText("输入端口号")
        self.port_input.setMaximumWidth(60)
        layout.addWidget(self.port_input)
        
        # 连接控制按钮
        self.connect_btn = QPushButton("连接传感器")
        self.disconnect_btn = QPushButton("断开连接")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.disconnect_btn.clicked.connect(self.on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        
        # 设置按钮样式
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
        """)
        
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)
        
        # 数据采集控制 - 只保留停止采集按钮
        self.stop_data_btn = QPushButton("停止采集")
        self.stop_data_btn.clicked.connect(self.on_stop_data_clicked)
        self.stop_data_btn.setEnabled(False)
        self.stop_data_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        layout.addWidget(self.stop_data_btn)
        
        # 连接状态显示
        self.connection_status = QLabel("未连接")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.connection_status)
        
        parent_layout.addWidget(group)
    
    def create_visualization_control_group(self, parent_layout):
        """创建可视化控制组"""
        group = QGroupBox("可视化控制")
        group.setMaximumHeight(120)  # 与其他组保持一致的高度
        group.setMinimumWidth(120)  # 设置最小宽度，确保有足够空间
        layout = QHBoxLayout(group)  # 改为水平布局
        layout.setContentsMargins(5, 5, 5, 5)  # 减少内边距
        layout.setSpacing(5)  # 减少间距

        # 2D/3D热力图切换 - 初始状态为3D模式
        self.heatmap_2d_3d_btn = QPushButton("3D热力图")
        self.heatmap_2d_3d_btn.clicked.connect(self.on_heatmap_2d_3d_clicked)
        # 设置初始样式为3D模式
        self.heatmap_2d_3d_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        layout.addWidget(self.heatmap_2d_3d_btn)

        parent_layout.addWidget(group)

    def on_heatmap_2d_3d_clicked(self):
        """2D/3D热力图切换按钮点击事件"""
        # 发送切换信号给渲染器
        self.visualization_changed.emit({'toggle_heatmap_mode': True})
        
        # 更新按钮文本和样式
        if self.heatmap_2d_3d_btn.text() == "2D热力图":
            self.heatmap_2d_3d_btn.setText("3D热力图")
            self.heatmap_2d_3d_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            print("🎨 切换到3D热力图模式")
        else:
            self.heatmap_2d_3d_btn.setText("2D热力图")
            self.heatmap_2d_3d_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            print("🎨 切换到2D热力图模式")

    def update_visualization_option(self, key, value):
        """更新可视化选项"""
        self.visualization_options[key] = value
        self.visualization_changed.emit({key: value})
        print(f"🎨 可视化选项更新: {key} = {value}")
    
    def get_current_parameters(self):
        """获取当前参数"""
        return self.parameters.copy()
    
    def get_current_visualization_options(self):
        """获取当前可视化选项"""
        return self.visualization_options.copy()
    
    def get_current_3d_rendering_options(self):
        """获取当前3D渲染选项"""
        return self.three_d_rendering_options.copy()
    
    def get_current_smoothing_options(self):
        """获取当前平滑选项"""
        return self.smoothing_options.copy()
    
    def on_connect_clicked(self):
        """连接按钮点击事件"""
        port = self.port_input.text().strip()
        use_real = True # 只保留真实传感器
        
        if not port:
            port = "0"
        
        self.sensor_connect_requested.emit(port)
    
    def on_disconnect_clicked(self):
        """断开连接按钮点击事件"""
        self.sensor_disconnect_requested.emit()
    
    def on_stop_data_clicked(self):
        """停止采集按钮点击事件"""
        self.data_stop_requested.emit()
    
    def update_connection_status(self, status_text, connected=False, collecting=False):
        """更新连接状态"""
        self.connection_status.setText(status_text)
        
        # 同时更新状态显示区域
        if hasattr(self, 'status_widgets') and 'sensor_status' in self.status_widgets:
            if connected:
                if collecting:
                    self.status_widgets['sensor_status'].setText("采集中")
                    self.status_widgets['sensor_status'].setStyleSheet("color: #4CAF50; font-weight: bold;")
                else:
                    self.status_widgets['sensor_status'].setText("已连接")
                    self.status_widgets['sensor_status'].setStyleSheet("color: #FF9800; font-weight: bold;")
            else:
                self.status_widgets['sensor_status'].setText("未连接")
                self.status_widgets['sensor_status'].setStyleSheet("color: #F44336; font-weight: bold;")
        
        if connected:
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            
            # 连接成功后立即开始采集，所以停止按钮应该可用
            if collecting:
                self.stop_data_btn.setEnabled(True)
            else:
                # 如果连接了但还没开始采集，停止按钮也应该可用（准备状态）
                self.stop_data_btn.setEnabled(True)
        else:
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.stop_data_btn.setEnabled(False)
    
    def update_status(self, key, value):
        """更新状态栏信息 - 处理控制模式和渲染帧率"""
        if hasattr(self, 'status_widgets') and key in self.status_widgets:
            if key == 'control_mode':
                # 🎮 处理控制模式信息
                if value == 'joystick':
                    self.status_widgets[key].setText("🕹️ 摇杆模式")
                    self.status_widgets[key].setStyleSheet("color: #4CAF50; font-weight: bold;")
                elif value == 'touchpad':
                    self.status_widgets[key].setText("🖱️ 触控板模式")
                    self.status_widgets[key].setStyleSheet("color: #2196F3; font-weight: bold;")
                elif value == 'idle':
                    self.status_widgets[key].setText("⏸️ 空闲模式")
                    self.status_widgets[key].setStyleSheet("color: #FF9800; font-weight: bold;")
                else:
                    self.status_widgets[key].setText(f"🎮 {value}")
                    self.status_widgets[key].setStyleSheet("color: #9C27B0; font-weight: bold;")
            elif key == 'renderer_fps':
                # 🎨 处理渲染器帧率信息
                if isinstance(value, (int, float)):
                    if value > 0:
                        self.status_widgets[key].setText(f"{value:.1f} FPS")
                    else:
                        self.status_widgets[key].setText("0.0 FPS")
                else:
                    self.status_widgets[key].setText(str(value))
    
    def on_settings_clicked(self):
        from interfaces.ordinary.BoxGame.box_game_settings_dialog import BoxGameSettingsDialog
        dialog = BoxGameSettingsDialog(self)
        
        # 🎮 获取当前参数，包括COP阈值
        current_params = self.parameters.copy()
        current_params.update({
            'joystick_threshold': 0.05,  # 默认值
            'touchpad_threshold': 5.0   # 默认值
        })
        dialog.set_parameters(current_params)
        
        # �� 获取当前的可视化选项，包括预处理参数和3D渲染参数
        current_vis_options = self.visualization_options.copy()
        
        # 添加默认的预处理参数
        current_vis_options.update({
            'preprocessing_enabled': True,
            'use_gaussian_blur': True,
            'use_xy_swap': False,
            'use_custom_colormap': True,
            'log_y_lim': [0.0, 0.1],  # 更新默认颜色范围
            'gaussian_sigma': 1.0
        })
        
        # 🎨 添加3D渲染参数
        current_vis_options.update(self.three_d_rendering_options)
        
        # 🎨 添加平滑选项参数
        current_vis_options.update(self.smoothing_options)
        
        dialog.set_visualization_options(current_vis_options)
        if dialog.exec_():
            new_params = dialog.get_parameters()
            new_vis = dialog.get_visualization_options()
            
            # 更新内部状态
            self.parameters.update(new_params)
            self.visualization_options.update(new_vis)
            
            # 🎨 更新3D渲染选项
            three_d_keys = ['enable_3d_lighting', 'enable_3d_shadows', 'enable_3d_animation',
                           'elevation_3d', 'azimuth_3d', 'rotation_speed_3d',
                           'surface_alpha_3d', 'enable_wireframe', 'enable_anti_aliasing',
                           'enable_bloom_effect']
            for key in three_d_keys:
                if key in new_vis:
                    self.three_d_rendering_options[key] = new_vis[key]
            
            # 🎨 更新平滑选项
            smoothing_keys = ['preprocessing_enabled', 'use_gaussian_blur', 'use_xy_swap',
                             'use_custom_colormap', 'log_y_lim', 'gaussian_sigma']
            for key in smoothing_keys:
                if key in new_vis:
                    self.smoothing_options[key] = new_vis[key]
            
            # 发送信号
            self.parameter_changed.emit(new_params)
            self.visualization_changed.emit(new_vis)
            
            print(f"⚙️ 设置已更新: 参数={list(new_params.keys())}, 可视化={list(new_vis.keys())}")

    def on_analysis_settings_clicked(self):
        """分析设置按钮点击事件"""
        # 这个方法现在已不再需要，所有设置都集成到主设置对话框中
        print("🔧 分析设置功能已集成到主设置对话框中")
    
    # 移除on_3d_options_clicked和apply_3d_options方法
    # 移除on_smoothing_options_clicked和apply_smoothing_options方法
    # 这些功能现在都集成到主设置对话框中

    def create_status_group(self, parent_layout):
        """创建状态显示组 - 显示控制模式和渲染帧率"""
        group = QGroupBox("系统状态")
        group.setMaximumHeight(120)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 状态组件字典
        self.status_widgets = {}
        
        # 🎮 显示控制模式
        control_mode_label = QLabel("控制模式:")
        layout.addWidget(control_mode_label)
        
        self.status_widgets['control_mode'] = QLabel("⏸️ 空闲模式")
        self.status_widgets['control_mode'].setStyleSheet("color: #FF9800; font-weight: bold;")
        layout.addWidget(self.status_widgets['control_mode'])
        
        # 添加分隔符
        separator = QLabel("|")
        separator.setStyleSheet("color: #666666; font-weight: bold;")
        layout.addWidget(separator)
        
        # 🎨 显示渲染帧率
        renderer_fps_label = QLabel("渲染帧率:")
        layout.addWidget(renderer_fps_label)
        
        self.status_widgets['renderer_fps'] = QLabel("0.0 FPS")
        self.status_widgets['renderer_fps'].setStyleSheet("color: #96CEB4; font-weight: bold;")
        layout.addWidget(self.status_widgets['renderer_fps'])
        
        # 添加弹性空间
        layout.addStretch()
        
        parent_layout.addWidget(group)

# 导出主要类
__all__ = ['BoxGameControlPanel'] 