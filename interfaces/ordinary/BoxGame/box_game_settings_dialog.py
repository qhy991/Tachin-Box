from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QComboBox, QDoubleSpinBox, QPushButton, QHBoxLayout, QCheckBox, QGroupBox
from PyQt5.QtCore import Qt

class BoxGameSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedWidth(500)  # 增加宽度以容纳更多选项
        
        # 🎨 强制设置白色边框样式
        self.setStyleSheet("""
            QDialog { background-color: #23272e; color: #f0f0f0; }
            QLabel { color: #f0f0f0; font-size: 14px; }
            QComboBox, QDoubleSpinBox { 
                background-color: #313640; 
                color: #f0f0f0; 
                border: 2px solid #FFFFFF !important; 
                border-radius: 4px !important; 
                padding: 4px;
            }
            QComboBox:hover, QDoubleSpinBox:hover { 
                border: 2px solid #E0E0E0 !important; 
            }
            QPushButton { 
                background-color: #444c5c; 
                color: #f0f0f0; 
                border: 2px solid #FFFFFF !important; 
                border-radius: 4px !important; 
                padding: 6px 16px; 
            }
            QPushButton:hover { 
                background-color: #5a6270; 
                border: 2px solid #E0E0E0 !important; 
            }
            QGroupBox { 
                font-weight: bold; 
                color: #f0f0f0; 
                border: 2px solid #FFFFFF !important; 
                border-radius: 6px !important; 
                margin-top: 10px; 
                padding-top: 10px;
            }
            QCheckBox { 
                color: #f0f0f0; 
                font-size: 14px; 
                spacing: 8px;
            }
            QCheckBox::indicator { 
                width: 16px; 
                height: 16px; 
                border: 2px solid #FFFFFF !important; 
                border-radius: 3px;
            }
            QCheckBox::indicator:checked { 
                background-color: #4CAF50; 
                border: 2px solid #4CAF50 !important;
            }
            QCheckBox::indicator:unchecked { 
                background-color: #313640; 
                border: 2px solid #FFFFFF !important;
            }
        """)
        self.parameters = {}
        self.visualization_options = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 使用滚动区域来容纳更多内容
        from PyQt5.QtWidgets import QScrollArea, QWidget
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 🎨 数据预处理参数组
        preprocessing_group = QGroupBox("🎨 数据预处理参数")
        preprocessing_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: #4CAF50; }")
        preprocessing_layout = QGridLayout(preprocessing_group)
        
        # 预处理总开关
        self.preprocessing_enabled = QCheckBox("启用数据预处理")
        self.preprocessing_enabled.setChecked(True)
        preprocessing_layout.addWidget(self.preprocessing_enabled, 0, 0, 1, 2)
        
        # 高斯模糊选项
        self.use_gaussian_blur = QCheckBox("高斯模糊")
        self.use_gaussian_blur.setChecked(True)
        preprocessing_layout.addWidget(self.use_gaussian_blur, 1, 0, 1, 2)
        
        # 高斯模糊参数
        preprocessing_layout.addWidget(QLabel("模糊强度 (σ):"), 2, 0)
        self.gaussian_sigma = QDoubleSpinBox()
        self.gaussian_sigma.setRange(0.1, 5.0)
        self.gaussian_sigma.setValue(1.0)
        self.gaussian_sigma.setDecimals(1)
        self.gaussian_sigma.setSuffix(" σ")
        preprocessing_layout.addWidget(self.gaussian_sigma, 2, 1)
        
        # 坐标轴交换选项
        self.use_xy_swap = QCheckBox("坐标轴交换")
        self.use_xy_swap.setChecked(False)
        preprocessing_layout.addWidget(self.use_xy_swap, 3, 0, 1, 2)
        
        # 自定义颜色映射选项
        self.use_custom_colormap = QCheckBox("自定义颜色映射")
        self.use_custom_colormap.setChecked(True)
        preprocessing_layout.addWidget(self.use_custom_colormap, 4, 0, 1, 2)
        
        # 颜色范围控制
        preprocessing_layout.addWidget(QLabel("颜色范围最小值:"), 5, 0)
        self.color_min = QDoubleSpinBox()
        self.color_min.setRange(0.0, 10.0)
        self.color_min.setValue(0.0)
        self.color_min.setDecimals(3)
        preprocessing_layout.addWidget(self.color_min, 5, 1)
        
        preprocessing_layout.addWidget(QLabel("颜色范围最大值:"), 6, 0)
        self.color_max = QDoubleSpinBox()
        self.color_max.setRange(0.001, 0.2)
        self.color_max.setValue(0.1)  # 修改默认值为0.1
        self.color_max.setDecimals(3)
        preprocessing_layout.addWidget(self.color_max, 6, 1)
        
        scroll_layout.addWidget(preprocessing_group)
        
        # 🎨 3D渲染选项组
        three_d_group = QGroupBox("🎨 3D渲染选项")
        three_d_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: #9C27B0; }")
        three_d_layout = QGridLayout(three_d_group)
        
        # 光照选项
        self.enable_3d_lighting = QCheckBox("启用3D光照")
        self.enable_3d_lighting.setChecked(True)
        three_d_layout.addWidget(self.enable_3d_lighting, 0, 0, 1, 2)
        
        self.enable_3d_shadows = QCheckBox("启用3D阴影")
        self.enable_3d_shadows.setChecked(True)
        three_d_layout.addWidget(self.enable_3d_shadows, 1, 0, 1, 2)
        
        # 动画选项
        self.enable_3d_animation = QCheckBox("启用3D动画")
        self.enable_3d_animation.setChecked(False)  # 禁用3D动画
        three_d_layout.addWidget(self.enable_3d_animation, 2, 0, 1, 2)
        
        # 旋转速度
        three_d_layout.addWidget(QLabel("旋转速度:"), 3, 0)
        self.rotation_speed_3d = QDoubleSpinBox()
        self.rotation_speed_3d.setRange(0.0, 5.0)
        self.rotation_speed_3d.setValue(0.0)  # 旋转速度设为0
        self.rotation_speed_3d.setSingleStep(0.1)
        three_d_layout.addWidget(self.rotation_speed_3d, 3, 1)
        
        # 视角选项
        three_d_layout.addWidget(QLabel("仰角:"), 4, 0)
        self.elevation_3d = QDoubleSpinBox()
        self.elevation_3d.setRange(0, 90)
        self.elevation_3d.setValue(45.0)  # 固定45度仰角
        three_d_layout.addWidget(self.elevation_3d, 4, 1)
        
        three_d_layout.addWidget(QLabel("方位角:"), 5, 0)
        self.azimuth_3d = QDoubleSpinBox()
        self.azimuth_3d.setRange(0, 360)
        self.azimuth_3d.setValue(45.0)  # 固定45度方位角
        three_d_layout.addWidget(self.azimuth_3d, 5, 1)
        
        # 渲染选项
        three_d_layout.addWidget(QLabel("表面透明度:"), 6, 0)
        self.surface_alpha_3d = QDoubleSpinBox()
        self.surface_alpha_3d.setRange(0.1, 1.0)
        self.surface_alpha_3d.setValue(0.8)
        self.surface_alpha_3d.setSingleStep(0.1)
        three_d_layout.addWidget(self.surface_alpha_3d, 6, 1)
        
        self.enable_wireframe = QCheckBox("启用线框")
        self.enable_wireframe.setChecked(True)  # 默认启动网格
        three_d_layout.addWidget(self.enable_wireframe, 7, 0, 1, 2)
        
        self.enable_anti_aliasing = QCheckBox("启用抗锯齿")
        self.enable_anti_aliasing.setChecked(True)
        three_d_layout.addWidget(self.enable_anti_aliasing, 8, 0, 1, 2)
        
        self.enable_bloom_effect = QCheckBox("启用泛光效果")
        self.enable_bloom_effect.setChecked(False)
        three_d_layout.addWidget(self.enable_bloom_effect, 9, 0, 1, 2)
        
        scroll_layout.addWidget(three_d_group)
        
        # 📊 可视化选项组
        vis_group = QGroupBox("📊 可视化选项")
        vis_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: #2196F3; }")
        vis_layout = QGridLayout(vis_group)
        
        self.show_pressure = QCheckBox("显示压力")
        self.show_pressure.setChecked(True)
        vis_layout.addWidget(self.show_pressure, 0, 0, 1, 2)
        
        self.show_cop = QCheckBox("显示压力中心")
        self.show_cop.setChecked(True)
        vis_layout.addWidget(self.show_cop, 1, 0, 1, 2)
        
        self.show_force_vector = QCheckBox("显示力向量")
        self.show_force_vector.setChecked(True)
        vis_layout.addWidget(self.show_force_vector, 2, 0, 1, 2)
        
        self.show_analysis_info = QCheckBox("显示分析信息")
        self.show_analysis_info.setChecked(True)
        vis_layout.addWidget(self.show_analysis_info, 3, 0, 1, 2)
        
        self.show_debug_info = QCheckBox("显示调试信息")
        self.show_debug_info.setChecked(False)
        vis_layout.addWidget(self.show_debug_info, 4, 0, 1, 2)
        
        # 颜色和缩放
        vis_layout.addWidget(QLabel("压力色彩:"), 5, 0)
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(['hot', 'viridis', 'plasma', 'coolwarm', 'jet'])
        vis_layout.addWidget(self.colormap_combo, 5, 1)
        
        vis_layout.addWidget(QLabel("力缩放:"), 6, 0)
        self.force_scale = QDoubleSpinBox()
        self.force_scale.setRange(0.1, 5.0)
        self.force_scale.setSingleStep(0.1)
        self.force_scale.setDecimals(1)
        self.force_scale.setValue(1.0)
        vis_layout.addWidget(self.force_scale, 6, 1)
        
        scroll_layout.addWidget(vis_group)
        
        # 🎮 COP距离阈值控制组
        cop_group = QGroupBox("🎮 COP距离阈值控制")
        cop_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: #9C27B0; }")
        cop_layout = QGridLayout(cop_group)
        
        # 摇杆模式阈值
        cop_layout.addWidget(QLabel("摇杆阈值:"), 0, 0)
        self.joystick_threshold = QDoubleSpinBox()
        self.joystick_threshold.setRange(0.001, 8.0)
        self.joystick_threshold.setValue(0.05)
        self.joystick_threshold.setDecimals(3)
        self.joystick_threshold.setSingleStep(0.005)
        self.joystick_threshold.setSuffix(" m")
        cop_layout.addWidget(self.joystick_threshold, 0, 1)
        
        # 触控板模式阈值
        cop_layout.addWidget(QLabel("触控板阈值:"), 1, 0)
        self.touchpad_threshold = QDoubleSpinBox()
        self.touchpad_threshold.setRange(0.001, 5.0)
        self.touchpad_threshold.setValue(10)
        self.touchpad_threshold.setDecimals(3)
        self.touchpad_threshold.setSingleStep(0.5)
        self.touchpad_threshold.setSuffix(" m")
        cop_layout.addWidget(self.touchpad_threshold, 1, 1)
        
        # 说明文字
        cop_info = QLabel("💡 摇杆阈值 < 触控板阈值 (范围: 0.001-5.0)")
        cop_info.setStyleSheet("color: #666666; font-size: 10px; margin: 5px 0;")
        cop_layout.addWidget(cop_info, 2, 0, 1, 2)
        
        scroll_layout.addWidget(cop_group)
        
        # ⚙️ 算法参数组
        algo_group = QGroupBox("⚙️ 算法参数")
        algo_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: #FF9800; }")
        algo_layout = QGridLayout(algo_group)
        
        algo_layout.addWidget(QLabel("压力阈值:"), 0, 0)
        self.pressure_threshold = QDoubleSpinBox()
        self.pressure_threshold.setRange(0.01, 0.05)
        self.pressure_threshold.setSingleStep(0.01)
        self.pressure_threshold.setDecimals(4)
        self.pressure_threshold.setValue(0.001)
        algo_layout.addWidget(self.pressure_threshold, 0, 1)
        
        algo_layout.addWidget(QLabel("切向阈值:"), 1, 0)
        self.tangential_threshold = QDoubleSpinBox()
        self.tangential_threshold.setRange(0.01, 0.5)
        self.tangential_threshold.setSingleStep(0.01)
        self.tangential_threshold.setDecimals(3)
        self.tangential_threshold.setValue(0.05)
        algo_layout.addWidget(self.tangential_threshold, 1, 1)
        
        algo_layout.addWidget(QLabel("滑动阈值:"), 2, 0)
        self.sliding_threshold = QDoubleSpinBox()
        self.sliding_threshold.setRange(0.01, 0.5)
        self.sliding_threshold.setSingleStep(0.01)
        self.sliding_threshold.setDecimals(3)
        self.sliding_threshold.setValue(0.08)
        algo_layout.addWidget(self.sliding_threshold, 2, 1)
        
        algo_layout.addWidget(QLabel("箱子速度:"), 3, 0)
        self.box_speed = QDoubleSpinBox()
        self.box_speed.setRange(0.1, 10.0)
        self.box_speed.setSingleStep(0.1)
        self.box_speed.setDecimals(1)
        self.box_speed.setValue(2.0)
        algo_layout.addWidget(self.box_speed, 3, 1)
        
        algo_layout.addWidget(QLabel("摩擦系数:"), 4, 0)
        self.friction = QDoubleSpinBox()
        self.friction.setRange(0.1, 1.0)
        self.friction.setSingleStep(0.1)
        self.friction.setDecimals(1)
        self.friction.setValue(0.8)
        algo_layout.addWidget(self.friction, 4, 1)
        
        algo_layout.addWidget(QLabel("分析平滑:"), 5, 0)
        self.analysis_smoothing = QDoubleSpinBox()
        self.analysis_smoothing.setRange(0.1, 1.0)
        self.analysis_smoothing.setSingleStep(0.1)
        self.analysis_smoothing.setDecimals(1)
        self.analysis_smoothing.setValue(0.7)
        algo_layout.addWidget(self.analysis_smoothing, 5, 1)
        
        scroll_layout.addWidget(algo_group)
        
        # 设置滚动区域
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(600)
        layout.addWidget(scroll_area)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def set_parameters(self, params):
        """设置参数"""
        self.parameters = params.copy()
        self.pressure_threshold.setValue(params.get('pressure_threshold', 0.001))
        self.tangential_threshold.setValue(params.get('tangential_threshold', 0.05))
        self.sliding_threshold.setValue(params.get('sliding_threshold', 0.08))
        self.box_speed.setValue(params.get('box_speed', 2.0))
        self.friction.setValue(params.get('friction', 0.8))
        self.analysis_smoothing.setValue(params.get('analysis_smoothing', 0.7))
        
        # 🎮 设置COP阈值参数
        self.joystick_threshold.setValue(params.get('joystick_threshold', 0.05))
        self.touchpad_threshold.setValue(params.get('touchpad_threshold', 10))

    def set_visualization_options(self, vis):
        """设置可视化选项"""
        self.visualization_options = vis.copy()
        self.show_pressure.setChecked(vis.get('show_pressure', True))
        self.show_cop.setChecked(vis.get('show_cop', True))
        self.show_force_vector.setChecked(vis.get('show_force_vector', True))
        self.show_analysis_info.setChecked(vis.get('show_analysis_info', True))
        self.show_debug_info.setChecked(vis.get('show_debug_info', False))
        
        # 设置颜色映射
        colormap = vis.get('pressure_colormap', 'hot')
        index = self.colormap_combo.findText(colormap)
        if index >= 0:
            self.colormap_combo.setCurrentIndex(index)
        
        self.force_scale.setValue(vis.get('force_scale', 1.0))
        
        # 🎨 设置预处理参数
        self.preprocessing_enabled.setChecked(vis.get('preprocessing_enabled', True))
        self.use_gaussian_blur.setChecked(vis.get('use_gaussian_blur', True))
        self.use_xy_swap.setChecked(vis.get('use_xy_swap', False))
        self.use_custom_colormap.setChecked(vis.get('use_custom_colormap', True))
        
        # 设置颜色范围
        log_y_lim = vis.get('log_y_lim', [0.0, 0.1])
        self.color_min.setValue(log_y_lim[0])
        self.color_max.setValue(log_y_lim[1])
        
        # 设置高斯模糊参数
        self.gaussian_sigma.setValue(vis.get('gaussian_sigma', 1.0))
        
        # 🎨 设置3D渲染参数
        self.enable_3d_lighting.setChecked(vis.get('enable_3d_lighting', True))
        self.enable_3d_shadows.setChecked(vis.get('enable_3d_shadows', True))
        self.enable_3d_animation.setChecked(vis.get('enable_3d_animation', False)) # 使用设置的值
        self.elevation_3d.setValue(vis.get('elevation_3d', 45.0)) # 使用设置的值
        self.azimuth_3d.setValue(vis.get('azimuth_3d', 45.0)) # 使用设置的值
        self.rotation_speed_3d.setValue(vis.get('rotation_speed_3d', 0.0)) # 使用设置的值
        self.surface_alpha_3d.setValue(vis.get('surface_alpha_3d', 0.8))
        self.enable_wireframe.setChecked(vis.get('enable_wireframe', True))  # 默认启动网格
        self.enable_anti_aliasing.setChecked(vis.get('enable_anti_aliasing', True))
        self.enable_bloom_effect.setChecked(vis.get('enable_bloom_effect', False))

    def get_parameters(self):
        """获取参数"""
        return {
            'pressure_threshold': self.pressure_threshold.value(),
            'tangential_threshold': self.tangential_threshold.value(),
            'sliding_threshold': self.sliding_threshold.value(),
            'box_speed': self.box_speed.value(),
            'friction': self.friction.value(),
            'analysis_smoothing': self.analysis_smoothing.value(),
            # 🎮 COP阈值参数
            'joystick_threshold': self.joystick_threshold.value(),
            'touchpad_threshold': self.touchpad_threshold.value()
        }

    def get_visualization_options(self):
        """获取可视化选项"""
        return {
            'show_pressure': self.show_pressure.isChecked(),
            'show_cop': self.show_cop.isChecked(),
            'show_force_vector': self.show_force_vector.isChecked(),
            'show_analysis_info': self.show_analysis_info.isChecked(),
            'show_debug_info': self.show_debug_info.isChecked(),
            'pressure_colormap': self.colormap_combo.currentText(),
            'force_scale': self.force_scale.value(),
            # 🎨 预处理参数
            'preprocessing_enabled': self.preprocessing_enabled.isChecked(),
            'use_gaussian_blur': self.use_gaussian_blur.isChecked(),
            'use_xy_swap': self.use_xy_swap.isChecked(),
            'use_custom_colormap': self.use_custom_colormap.isChecked(),
            'log_y_lim': [self.color_min.value(), self.color_max.value()],
            'gaussian_sigma': self.gaussian_sigma.value(),
            # 🎨 3D渲染参数
            'enable_3d_lighting': self.enable_3d_lighting.isChecked(),
            'enable_3d_shadows': self.enable_3d_shadows.isChecked(),
            'enable_3d_animation': self.enable_3d_animation.isChecked(),
            'elevation_3d': self.elevation_3d.value(),
            'azimuth_3d': self.azimuth_3d.value(),
            'rotation_speed_3d': self.rotation_speed_3d.value(),
            'surface_alpha_3d': self.surface_alpha_3d.value(),
            'enable_wireframe': self.enable_wireframe.isChecked(),
            'enable_anti_aliasing': self.enable_anti_aliasing.isChecked(),
            'enable_bloom_effect': self.enable_bloom_effect.isChecked()
        }