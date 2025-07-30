from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QDoubleSpinBox, QSpinBox, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

class BoxGameAnalysisSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("分析设置")
        self.setFixedWidth(400)
        
        # 🎨 强制设置白色边框样式
        self.setStyleSheet("""
            QDialog { background-color: #23272e; color: #f0f0f0; }
            QLabel { color: #f0f0f0; font-size: 14px; }
            QDoubleSpinBox, QSpinBox { 
                background-color: #313640; 
                color: #f0f0f0; 
                border: 2px solid #FFFFFF !important; 
                border-radius: 4px !important; 
                padding: 4px;
            }
            QDoubleSpinBox:hover, QSpinBox:hover { 
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
        """)
        self.parameters = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        grid = QGridLayout()
        row = 0
        # 压力阈值
        grid.addWidget(QLabel("压力阈值:"), row, 0)
        self.pressure_threshold = QDoubleSpinBox()
        self.pressure_threshold.setRange(0.001, 0.1)
        self.pressure_threshold.setSingleStep(0.001)
        self.pressure_threshold.setDecimals(4)
        grid.addWidget(self.pressure_threshold, row, 1)
        row += 1
        # 时序窗口大小
        grid.addWidget(QLabel("时序窗口大小:"), row, 0)
        self.temporal_window_size = QSpinBox()
        self.temporal_window_size.setRange(1, 100)
        grid.addWidget(self.temporal_window_size, row, 1)
        row += 1
        # 平滑因子
        grid.addWidget(QLabel("平滑因子:"), row, 0)
        self.smoothing_factor = QDoubleSpinBox()
        self.smoothing_factor.setRange(0.0, 1.0)
        self.smoothing_factor.setSingleStep(0.01)
        self.smoothing_factor.setDecimals(2)
        grid.addWidget(self.smoothing_factor, row, 1)
        row += 1
        # COP移动阈值
        grid.addWidget(QLabel("COP移动阈值:"), row, 0)
        self.cop_movement_threshold = QDoubleSpinBox()
        self.cop_movement_threshold.setRange(0.1, 20.0)
        self.cop_movement_threshold.setSingleStep(0.1)
        self.cop_movement_threshold.setDecimals(2)
        grid.addWidget(self.cop_movement_threshold, row, 1)
        row += 1
        # 梯度阈值
        grid.addWidget(QLabel("梯度阈值:"), row, 0)
        self.gradient_threshold = QDoubleSpinBox()
        self.gradient_threshold.setRange(1e-7, 1e-2)
        self.gradient_threshold.setSingleStep(1e-6)
        self.gradient_threshold.setDecimals(7)
        grid.addWidget(self.gradient_threshold, row, 1)
        row += 1
        layout.addLayout(grid)
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
        self.parameters = params.copy()
        self.pressure_threshold.setValue(params.get('pressure_threshold', 0.001))
        self.temporal_window_size.setValue(params.get('temporal_window_size', 10))
        self.smoothing_factor.setValue(params.get('smoothing_factor', 0.3))
        self.cop_movement_threshold.setValue(params.get('cop_movement_threshold', 5.0))
        self.gradient_threshold.setValue(params.get('gradient_threshold', 1e-5))

    def get_parameters(self):
        return {
            'pressure_threshold': self.pressure_threshold.value(),
            'temporal_window_size': self.temporal_window_size.value(),
            'smoothing_factor': self.smoothing_factor.value(),
            'cop_movement_threshold': self.cop_movement_threshold.value(),
            'gradient_threshold': self.gradient_threshold.value()
        }