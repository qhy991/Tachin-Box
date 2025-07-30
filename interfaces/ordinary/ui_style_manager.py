# -*- coding: utf-8 -*-
"""
UI样式管理器 - 统一的现代化设计系统
提供一致的颜色主题、字体、间距和样式定义
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import QApplication


class ModernUITheme:
    """现代化UI主题配置"""
    
    # 主要颜色系统
    COLORS = {
        # 主色调 - 科技蓝
        'primary': '#2E86AB',
        'primary_light': '#A23B72',
        'primary_dark': '#1B5E7F',
        
        # 辅助色调
        'secondary': '#F18F01',
        'secondary_light': '#FFB347',
        'secondary_dark': '#C6720A',
        
        # 中性色系
        'background': '#F8F9FA',
        'surface': '#FFFFFF',
        'surface_variant': '#F1F3F4',
        'outline': '#E0E0E0',
        'outline_variant': '#C4C7C5',
        
        # 文本色系
        'on_primary': '#FFFFFF',
        'on_secondary': '#FFFFFF',
        'on_surface': '#1C1B1F',
        'on_surface_variant': '#49454F',
        'on_outline': '#79747E',
        
        # 状态色系
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'info': '#2196F3',
        
        # 数据可视化色系
        'chart_primary': '#2E86AB',
        'chart_secondary': '#A23B72',
        'chart_accent': '#F18F01',
        'chart_neutral': '#6C757D',
        
        # 暗色模式
        'dark_background': '#121212',
        'dark_surface': '#1E1E1E',
        'dark_surface_variant': '#2D2D2D',
        'dark_on_surface': '#E1E1E1',
    }
    
    # 字体系统 - 优化尺寸
    FONTS = {
        'primary_family': 'Microsoft YaHei UI',  # 主要字体
        'secondary_family': 'Segoe UI',          # 备选字体
        'monospace_family': 'Consolas',          # 等宽字体
        
        # 字体大小 - 调整为更大尺寸
        'display_large': 30,
        'display_medium': 26,
        'display_small': 22,
        'headline_large': 20,
        'headline_medium': 18,
        'headline_small': 16,
        'title_large': 22,
        'title_medium': 20,
        'title_small': 18,
        'label_large': 16,
        'label_medium': 14,
        'label_small': 12,
        'body_large': 15,
        'body_medium': 14,
        'body_small': 12,
    }
    
    # 间距系统 - 调整为更大间距
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 20,
        'xxl': 24,
        'xxxl': 32,
    }
    
    # 圆角系统
    RADIUS = {
        'none': 0,
        'sm': 4,
        'md': 8,
        'lg': 12,
        'xl': 16,
        'full': 9999,
    }
    
    # 阴影系统
    SHADOWS = {
        'none': 'none',
        'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px rgba(0, 0, 0, 0.1)',
        'xl': '0 20px 25px rgba(0, 0, 0, 0.15)',
    }


class StyleSheetGenerator:
    """样式表生成器"""
    
    @staticmethod
    def get_main_window_style():
        """主窗口样式"""
        return f"""
        QMainWindow, QWidget {{
            background-color: {ModernUITheme.COLORS['background']};
            color: {ModernUITheme.COLORS['on_surface']};
            font-family: '{ModernUITheme.FONTS['primary_family']}';
            font-size: {ModernUITheme.FONTS['body_medium']}px;
        }}
        
        QWidget#centralWidget {{
            background-color: {ModernUITheme.COLORS['surface']};
            border-radius: {ModernUITheme.RADIUS['lg']}px;
            margin: {ModernUITheme.SPACING['md']}px;
        }}
        """
    
    @staticmethod
    def get_button_style():
        """按钮样式 - 优化尺寸"""
        return f"""
        QPushButton {{
            background-color: {ModernUITheme.COLORS['primary']};
            color: {ModernUITheme.COLORS['on_primary']};
            border: none;
            border-radius: {ModernUITheme.RADIUS['sm']}px;
            padding: {ModernUITheme.SPACING['xs']}px {ModernUITheme.SPACING['sm']}px;
            font-weight: 500;
            font-size: {ModernUITheme.FONTS['label_medium']}px;
            min-height: 24px;
            max-height: 28px;
            min-width: 60px;
        }}
        
        QPushButton:hover {{
            background-color: {ModernUITheme.COLORS['primary_light']};
            transform: translateY(-1px);
        }}
        
        QPushButton:pressed {{
            background-color: {ModernUITheme.COLORS['primary_dark']};
            transform: translateY(0px);
        }}
        
        QPushButton:disabled {{
            background-color: {ModernUITheme.COLORS['outline']};
            color: {ModernUITheme.COLORS['on_outline']};
        }}
        
        QPushButton#secondaryButton {{
            background-color: {ModernUITheme.COLORS['surface_variant']};
            color: {ModernUITheme.COLORS['on_surface']};
            border: 1px solid {ModernUITheme.COLORS['outline']};
            padding: {ModernUITheme.SPACING['xs']}px {ModernUITheme.SPACING['sm']}px;
            min-height: 22px;
            max-height: 26px;
        }}
        
        QPushButton#secondaryButton:hover {{
            background-color: {ModernUITheme.COLORS['outline']};
        }}
        
        QPushButton#dangerButton {{
            background-color: {ModernUITheme.COLORS['error']};
            color: white;
        }}
        
        QPushButton#successButton {{
            background-color: {ModernUITheme.COLORS['success']};
            color: white;
        }}
        
        /* 小型按钮样式 */
        QPushButton#smallButton {{
            padding: {ModernUITheme.SPACING['xs']}px {ModernUITheme.SPACING['xs']}px;
            font-size: {ModernUITheme.FONTS['label_small']}px;
            min-height: 20px;
            max-height: 24px;
            min-width: 50px;
        }}
        """
    
    @staticmethod
    def get_groupbox_style():
        """分组框样式 - 优化间距"""
        return f"""
        QGroupBox {{
            font-weight: 600;
            font-size: {ModernUITheme.FONTS['title_small']}px;
            color: {ModernUITheme.COLORS['on_surface']};
            border: 1px solid {ModernUITheme.COLORS['outline']};
            border-radius: {ModernUITheme.RADIUS['md']}px;
            margin-top: {ModernUITheme.SPACING['md']}px;
            padding-top: {ModernUITheme.SPACING['lg']}px;
            background-color: {ModernUITheme.COLORS['surface']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {ModernUITheme.SPACING['sm']}px;
            padding: 0 {ModernUITheme.SPACING['xs']}px 0 {ModernUITheme.SPACING['xs']}px;
            background-color: {ModernUITheme.COLORS['surface']};
            color: {ModernUITheme.COLORS['primary']};
        }}
        """
    
    @staticmethod
    def get_input_style():
        """输入框样式 - 优化尺寸"""
        return f"""
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            border: 1px solid {ModernUITheme.COLORS['outline']};
            border-radius: {ModernUITheme.RADIUS['sm']}px;
            padding: {ModernUITheme.SPACING['xs']}px {ModernUITheme.SPACING['sm']}px;
            background-color: {ModernUITheme.COLORS['surface']};
            color: {ModernUITheme.COLORS['on_surface']};
            font-size: {ModernUITheme.FONTS['body_small']}px;
            min-height: 18px;
            max-height: 22px;
        }}
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
            border-color: {ModernUITheme.COLORS['primary']};
            outline: none;
        }}
        
        QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
            border-color: {ModernUITheme.COLORS['primary_light']};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 16px;
            border-left-width: 1px;
            border-left-color: {ModernUITheme.COLORS['outline']};
            border-left-style: solid;
            border-top-right-radius: {ModernUITheme.RADIUS['sm']}px;
            border-bottom-right-radius: {ModernUITheme.RADIUS['sm']}px;
            background-color: {ModernUITheme.COLORS['surface_variant']};
        }}
        
        QComboBox::down-arrow {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iIzQ5NDU0RiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
        }}
        """
    
    @staticmethod
    def get_slider_style():
        """滑块样式"""
        return f"""
        QSlider::groove:horizontal {{
            border: none;
            height: 6px;
            background: {ModernUITheme.COLORS['outline']};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {ModernUITheme.COLORS['primary']};
            border: 2px solid {ModernUITheme.COLORS['surface']};
            width: 20px;
            height: 20px;
            margin: -9px 0;
            border-radius: 10px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {ModernUITheme.COLORS['primary_light']};
            transform: scale(1.1);
        }}
        
        QSlider::sub-page:horizontal {{
            background: {ModernUITheme.COLORS['primary']};
            border-radius: 3px;
        }}
        """
    
    @staticmethod
    def get_checkbox_style():
        """复选框样式"""
        return f"""
        QCheckBox {{
            spacing: {ModernUITheme.SPACING['xs']}px;
            color: {ModernUITheme.COLORS['on_surface']};
            font-size: {ModernUITheme.FONTS['body_small']}px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: {ModernUITheme.RADIUS['sm']}px;
            border: 2px solid {ModernUITheme.COLORS['outline']};
            background-color: {ModernUITheme.COLORS['surface']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {ModernUITheme.COLORS['primary']};
            border-color: {ModernUITheme.COLORS['primary']};
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=);
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {ModernUITheme.COLORS['primary']};
        }}
        """
    
    @staticmethod
    def get_tab_style():
        """标签页样式 - 优化尺寸"""
        return f"""
        QTabWidget::pane {{
            border: 1px solid {ModernUITheme.COLORS['outline']};
            border-radius: {ModernUITheme.RADIUS['md']}px;
            background-color: {ModernUITheme.COLORS['surface']};
            margin-top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {ModernUITheme.COLORS['surface_variant']};
            color: {ModernUITheme.COLORS['on_surface_variant']};
            padding: {ModernUITheme.SPACING['xs']}px {ModernUITheme.SPACING['sm']}px;
            margin-right: 2px;
            border-top-left-radius: {ModernUITheme.RADIUS['sm']}px;
            border-top-right-radius: {ModernUITheme.RADIUS['sm']}px;
            font-weight: 500;
            font-size: {ModernUITheme.FONTS['body_small']}px;
            min-height: 20px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {ModernUITheme.COLORS['primary']};
            color: {ModernUITheme.COLORS['on_primary']};
            border-bottom: 2px solid {ModernUITheme.COLORS['primary']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {ModernUITheme.COLORS['primary_light']};
            color: {ModernUITheme.COLORS['on_primary']};
        }}
        """
    
    @staticmethod
    def get_label_style():
        """标签样式 - 优化字体大小"""
        return f"""
        QLabel {{
            color: {ModernUITheme.COLORS['on_surface']};
            font-size: {ModernUITheme.FONTS['body_small']}px;
            padding: {ModernUITheme.SPACING['xs']}px;
        }}
        
        QLabel#titleLabel {{
            font-weight: 600;
            font-size: {ModernUITheme.FONTS['title_small']}px;
            color: {ModernUITheme.COLORS['primary']};
            padding: {ModernUITheme.SPACING['xs']}px {ModernUITheme.SPACING['sm']}px;
        }}
        
        QLabel#subtitleLabel {{
            font-weight: 500;
            font-size: {ModernUITheme.FONTS['body_small']}px;
            color: {ModernUITheme.COLORS['on_surface_variant']};
        }}
        
        QLabel#captionLabel {{
            font-size: {ModernUITheme.FONTS['label_small']}px;
            color: {ModernUITheme.COLORS['on_outline']};
        }}
        
        QLabel#errorLabel {{
            color: {ModernUITheme.COLORS['error']};
            font-weight: 500;
        }}
        
        QLabel#successLabel {{
            color: {ModernUITheme.COLORS['success']};
            font-weight: 500;
        }}
        
        QLabel#warningLabel {{
            color: {ModernUITheme.COLORS['warning']};
            font-weight: 500;
        }}
        
        QLabel#infoLabel {{
            color: {ModernUITheme.COLORS['info']};
            font-weight: 500;
        }}
        """
    
    @staticmethod
    def get_scrollbar_style():
        """滚动条样式"""
        return f"""
        QScrollBar:vertical {{
            background: {ModernUITheme.COLORS['surface_variant']};
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {ModernUITheme.COLORS['outline']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {ModernUITheme.COLORS['primary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background: {ModernUITheme.COLORS['surface_variant']};
            height: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {ModernUITheme.COLORS['outline']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {ModernUITheme.COLORS['primary']};
        }}
        """
    
    @staticmethod
    def get_complete_style():
        """获取完整的样式表"""
        return "\n".join([
            StyleSheetGenerator.get_main_window_style(),
            StyleSheetGenerator.get_button_style(),
            StyleSheetGenerator.get_groupbox_style(),
            StyleSheetGenerator.get_input_style(),
            StyleSheetGenerator.get_slider_style(),
            StyleSheetGenerator.get_checkbox_style(),
            StyleSheetGenerator.get_tab_style(),
            StyleSheetGenerator.get_label_style(),
            StyleSheetGenerator.get_scrollbar_style(),
        ])


class UIStyleManager:
    """UI样式管理器"""
    
    def __init__(self):
        self.theme = ModernUITheme()
        self.style_generator = StyleSheetGenerator()
        self.dark_mode = False
    
    def apply_modern_theme(self, app_or_widget):
        """应用现代化主题"""
        style_sheet = self.style_generator.get_complete_style()
        
        if isinstance(app_or_widget, QApplication):
            app_or_widget.setStyleSheet(style_sheet)
        else:
            app_or_widget.setStyleSheet(style_sheet)
    
    def get_color(self, color_name):
        """获取主题颜色"""
        return self.theme.COLORS.get(color_name, '#000000')
    
    def get_font(self, font_type='body_medium'):
        """获取主题字体"""
        font = QFont(self.theme.FONTS['primary_family'])
        font.setPointSize(self.theme.FONTS.get(font_type, 11))
        return font
    
    def get_spacing(self, size='md'):
        """获取间距"""
        return self.theme.SPACING.get(size, 12)
    
    def toggle_dark_mode(self):
        """切换暗色模式"""
        self.dark_mode = not self.dark_mode
        # 这里可以添加暗色模式的样式切换逻辑
    
    def create_status_label_style(self, status_type='info'):
        """创建状态标签样式"""
        colors = {
            'success': self.theme.COLORS['success'],
            'error': self.theme.COLORS['error'],
            'warning': self.theme.COLORS['warning'],
            'info': self.theme.COLORS['info'],
        }
        
        color = colors.get(status_type, colors['info'])
        return f"""
        QLabel {{
            background-color: {color};
            color: white;
            padding: {self.theme.SPACING['xs']}px {self.theme.SPACING['sm']}px;
            border-radius: {self.theme.RADIUS['sm']}px;
            font-weight: 500;
        }}
        """
    
    def create_card_style(self, elevated=True):
        """创建卡片样式"""
        shadow = 'box-shadow: 0 2px 8px rgba(0,0,0,0.1);' if elevated else ''
        return f"""
        QFrame {{
            background-color: {self.theme.COLORS['surface']};
            border: 1px solid {self.theme.COLORS['outline']};
            border-radius: {self.theme.RADIUS['lg']}px;
            padding: {self.theme.SPACING['lg']}px;
            {shadow}
        }}
        """


# 全局样式管理器实例
ui_style_manager = UIStyleManager() 