"""
显示界面，适用于large采集卡
顺便可以给small采集卡使用
"""

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QGraphicsSceneWheelEvent
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from interfaces.ordinary.layout.layout import Ui_Form
#
from usb.core import USBError
import sys
import numpy as np
from data_processing.data_handler import DataHandler
from backends.usb_driver import LargeUsbSensorDriver  # 或你的实际driver
#
from interfaces.public.utils import (set_logo,
                                     create_a_line, create_an_image,
                                     config, save_config, catch_exceptions,
                                     apply_swap)
import pyqtgraph as pg
#
# 导入切向力分析widget
from interfaces.ordinary.tangential_force_view import TangentialForceWidget
from interfaces.ordinary.EnhancedTangentialForceWidget import EnhancedTangentialForceWidget
# from interfaces.ordinary.morphological_analysis_widget import MorphologicalAnalysisWidget
#
# 导入现代化UI样式管理器
try:
    from interfaces.ordinary.ui_style_manager import UIStyleManager
    ui_style_manager = UIStyleManager()
    UI_STYLE_AVAILABLE = True
except ImportError:
    print("⚠️ UI样式管理器未找到，使用默认样式")
    UI_STYLE_AVAILABLE = False
#
LABEL_TIME = '时间/s'
LABEL_PRESSURE = '单点力/N'
LABEL_FORCE = '总力/N'
LABEL_VALUE = '值'
LABEL_RESISTANCE = '电阻/(kΩ)'
Y_LIM_INITIAL = config['y_lim']
AVAILABLE_FILTER_NAMES = ['无', '中值-0.2s', '中值-1s', '均值-0.2s', '均值-1s', '单向抵消-轻', '单向抵消-中', '单向抵消-重']

MINIMUM_Y_LIM = 0.0
MAXIMUM_Y_LIM = 5.5
assert Y_LIM_INITIAL.__len__() == 2
assert Y_LIM_INITIAL[0] >= MINIMUM_Y_LIM - 0.2
assert Y_LIM_INITIAL[1] <= MAXIMUM_Y_LIM + 0.2

from skimage import filters, measure

def log(v):
    return np.log(np.maximum(v, 1e-6)) / np.log(10)


class Window(QtWidgets.QWidget, Ui_Form):
    """
    主窗口
    """


    def __init__(self, mode='standard'):
        """

        :param mode: "standard" or "socket"
        """
        super().__init__()
        self.setupUi(self)
        
        # 应用现代化UI样式
        if UI_STYLE_AVAILABLE:
            try:
                ui_style_manager.apply_modern_theme(self)
                self._apply_component_styles()
                print("✅ 现代化UI样式已应用")
            except Exception as e:
                print(f"⚠️ 应用UI样式失败: {e}")
        
        # 重定向提示
        sys.excepthook = self._catch_exceptions
        #
        self.is_running = False
        #
        self.log_y_lim = Y_LIM_INITIAL
        self.line_maximum = create_a_line(self.fig_1, LABEL_TIME, LABEL_RESISTANCE)
        self.line_tracing = create_a_line(self.fig_2, LABEL_TIME, LABEL_RESISTANCE)
        # 添加第三个线条：每帧最大值
        self.line_frame_max = create_a_line(self.fig_3, LABEL_TIME, LABEL_RESISTANCE)
        self.plot = create_an_image(self.fig_image,
                                    self.__clicked_on_image,
                                    self.__on_mouse_wheel
                                    )
        
        # 初始化标签页激活状态管理
        self.current_active_tab = 0  # 默认第一个标签页激活
        self.tab_widgets = {}  # 存储标签页对应的widget
        self.tab_update_enabled = {}  # 存储每个标签页的更新状态
        
        # 集成切向力分析widget到第二个标签页
        self.tangential_force_widget = TangentialForceWidget()
        self.tab_tangential_force_layout.addWidget(self.tangential_force_widget)
        self.tab_widgets[1] = self.tangential_force_widget
        
        # 第三个标签页：增强切向力分析
        self.enhanced_force_widget = EnhancedTangentialForceWidget()
        self.tab_enhanced_force_layout.addWidget(self.enhanced_force_widget)
        self.tab_widgets[2] = self.enhanced_force_widget
        
        # # 第四个标签页：形态学方法分析（原来的第五个标签页）
        # self.morphological_widget = MorphologicalAnalysisWidget()
        # self.verticalLayout_6.addWidget(self.morphological_widget)
        # self.tab_widgets[3] = self.morphological_widget
        
        # 初始化所有标签页的更新状态
        for i in range(3):  # 现在只有4个标签页
            self.tab_update_enabled[i] = False  # 初始时都不激活
        
        # 根据不同mode构造数据接口
        if mode == 'standard':
            from backends.usb_driver import LargeUsbSensorDriver
            self.data_handler = DataHandler(LargeUsbSensorDriver, max_len=256)
        elif mode == 'zw':
            from backends.usb_driver import ZWUsbSensorDriver
            self.data_handler = DataHandler(ZWUsbSensorDriver)
        elif mode == 'socket':
            from server.socket_client import SocketClient
            self.data_handler = DataHandler(SocketClient)
        elif mode == 'serial':
            from backends.serial_driver import Serial16SensorDriver
            self.data_handler = DataHandler(Serial16SensorDriver)
        elif mode == 'can':
            from backends.can_driver import Can16SensorDriver
            self.data_handler = DataHandler(Can16SensorDriver)
        elif mode == 'low_framerate':
            # 为了向后兼容，保留模拟模式选项
            from backends.special_usb_driver import SimulatedLowFrameUsbSensorDriver
            self.data_handler = DataHandler(SimulatedLowFrameUsbSensorDriver)
            print("⚠️ 使用模拟传感器模式 - 仅用于测试")
        else:
            # 默认使用真实传感器
            print(f"⚠️ 未知模式 '{mode}'，使用默认真实传感器")
            from backends.usb_driver import LargeUsbSensorDriver
            self.data_handler = DataHandler(LargeUsbSensorDriver, max_len=256)
        self.scaling = log
        self.__set_using_calibration(False)
        # 界面初始配置
        self.pre_initialize()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.trigger)
        #
        
        # 连接标签页切换信号
        if hasattr(self, 'main_tabs'):
            self.main_tabs.currentChanged.connect(self.on_tab_changed)
        
        # 设置第一个标签页（热力图）始终激活
        self.tab_update_enabled[0] = True  # 标签页索引0（热力图）始终激活

        # 在 Window.__init__ 末尾加
        self.enhanced_force_widget.consensus_angle_changed.connect(
            self.tangential_force_widget.set_consensus_angle
        )
    def _on_enhanced_consensus_angle_changed(self, angle):
        print(f"[Window] 收到 Enhanced 的 consensus_angle_changed 信号: {angle}")
        self.tangential_force_widget.set_consensus_angle(angle)
        # 如果2D/3D tab当前激活，强制刷新
        if hasattr(self.tangential_force_widget, 'current_pressure_data') and self.tangential_force_widget.current_pressure_data is not None:
            self.tangential_force_widget.update_view(self.tangential_force_widget.current_pressure_data)


    def _apply_component_styles(self):
        """应用组件特定样式"""
        if not UI_STYLE_AVAILABLE:
            return
            
        try:
            # 设置按钮样式
            if hasattr(self, 'button_start'):
                self.button_start.setObjectName("successButton")
            if hasattr(self, 'button_stop'):
                self.button_stop.setObjectName("dangerButton")
            if hasattr(self, 'button_save_to'):
                self.button_save_to.setObjectName("secondaryButton")
            
            # 设置小型按钮样式
            if hasattr(self, 'button_set_zero'):
                self.button_set_zero.setObjectName("smallButton")
            if hasattr(self, 'button_abandon_zero'):
                self.button_abandon_zero.setObjectName("smallButton")
            if hasattr(self, 'button_load_calibration'):
                self.button_load_calibration.setObjectName("smallButton")
            if hasattr(self, 'button_exit_calibration'):
                self.button_exit_calibration.setObjectName("smallButton")
                
            # 设置标题标签样式
            if hasattr(self, 'label_3'):
                self.label_3.setObjectName("titleLabel")
            if hasattr(self, 'label_max_value'):
                self.label_max_value.setObjectName("titleLabel")
            if hasattr(self, 'label_2'):
                self.label_2.setObjectName("titleLabel")
                
            # 设置普通标签样式
            if hasattr(self, 'label_4'):
                self.label_4.setObjectName("captionLabel")
            if hasattr(self, 'label_6'):
                self.label_6.setObjectName("captionLabel")
            if hasattr(self, 'label_7'):
                self.label_7.setObjectName("captionLabel")
            if hasattr(self, 'label_8'):
                self.label_8.setObjectName("captionLabel")
            if hasattr(self, 'label_9'):
                self.label_9.setObjectName("captionLabel")
                
            print("✅ 组件样式已应用")
        except Exception as e:
            print(f"⚠️ 应用组件样式失败: {e}")

    def _catch_exceptions(self, ty, value, tb):
        catch_exceptions(self, ty, value, tb)

    def start(self):
        # 按开始键
        if not self.is_running:
            flag = self.data_handler.connect(self.com_port.text())
            config['port'] = self.com_port.text()
            save_config()
            if not flag:
                return
            self.is_running = True
            self.timer.start(config['trigger_time'])
            self.set_enable_state()
            self.com_port.setEnabled(False)

    def stop(self):
        # 按停止键
        config['y_lim'] = self.log_y_lim
        save_config()
        if self.is_running:
            self.is_running = False
            if self.timer.isActive():
                self.timer.stop()
            self.data_handler.disconnect()
            self.set_enable_state()

    def pre_initialize(self):
        set_logo(self)
        self.initialize_buttons()
        self.set_enable_state()
        self.__apply_y_lim()
        self.com_port.setEnabled(True)  # 一旦成功开始，就再也不能修改

    def __clicked_on_image(self, event: MouseClickEvent):
        # 图上选点
        size = [self.plot.width(), self.plot.height()]
        vb = self.plot.getView()
        vb_state = vb.state['viewRange']
        pix_offset = [-size[j] / (vb_state[j][1] - vb_state[j][0]) * vb_state[j][0] for j in range(2)]
        pix_unit = [size[j] / (vb_state[j][1] - vb_state[j][0]) for j in range(2)]
        x = (event.pos().x() - pix_offset[0]) / pix_unit[0]
        y = (event.pos().y() - pix_offset[1]) / pix_unit[1]
        xx = int(y / self.data_handler.interpolation.interp)
        yy = int(x / self.data_handler.interpolation.interp)
        if not vb.state['yInverted']:
            xx = self.data_handler.driver.SENSOR_SHAPE[0] - xx - 1
        if vb.state['xInverted']:
            yy = self.data_handler.driver.SENSOR_SHAPE[1] - yy - 1
        flag = 0 <= xx < self.data_handler.driver.SENSOR_SHAPE[0] and 0 <= yy < self.data_handler.driver.SENSOR_SHAPE[1]
        if flag:
            self.data_handler.set_tracing(xx, yy)
            print(xx, yy)

    def __on_mouse_wheel(self, event: QGraphicsSceneWheelEvent):
        if not config['fixed_range']:
            # 当鼠标滚轮滚动时，调整图像的显示范围
            if event.delta() > 0:
                if self.log_y_lim[1] < MAXIMUM_Y_LIM:
                    self.log_y_lim = (self.log_y_lim[0] + 0.1, self.log_y_lim[1] + 0.1)
            else:
                if self.log_y_lim[0] > MINIMUM_Y_LIM:
                    self.log_y_lim = (self.log_y_lim[0] - 0.1, self.log_y_lim[1] - 0.1)
            self.log_y_lim = (round(self.log_y_lim[0], 1), round(self.log_y_lim[1], 1))
            self.__apply_y_lim()

    @property
    def y_lim(self):
        if self.data_handler.using_calibration:
            return self.data_handler.calibration_adaptor.range()
        else:
            return [-self.log_y_lim[1], -self.log_y_lim[0]]

    def __apply_y_lim(self):
        for line in [self.line_maximum, self.line_tracing, self.line_frame_max]:
            if not (line is self.line_maximum and self.data_handler.using_calibration):
                line.getViewBox().setYRange(*self.y_lim)
            pass

    def __set_using_calibration(self, b):
        if b:
            for line in [self.line_maximum, self.line_tracing, self.line_frame_max]:
                ax = line.get_axis()
                ax.getAxis('left').tickStrings = lambda values, scale, spacing: \
                    [f'{_: .2f}' for _ in values]
                ax.getAxis('left').label.setPlainText(LABEL_PRESSURE)
                # 特殊处理：改为总力
                if line is self.line_maximum:
                    ax.getAxis('left').label.setPlainText(LABEL_FORCE)
                    self.label_3.setText("总值")
                    ax.getViewBox().setYRange(0, 0.1)
                    ax.enableAutoRange(axis=pg.ViewBox.YAxis)
                # 特殊处理：每帧最大值
                elif line is self.line_frame_max:
                    ax.getAxis('left').label.setPlainText(LABEL_PRESSURE)
                    self.label_max_value.setText("每帧最大值")
                    ax.getViewBox().setYRange(0, 0.1)
                    ax.enableAutoRange(axis=pg.ViewBox.YAxis)
            self.scaling = lambda x: x
            self.__apply_y_lim()
        else:
            for line in [self.line_maximum, self.line_tracing, self.line_frame_max]:
                ax = line.get_axis()
                ax.getAxis('left').tickStrings = lambda values, scale, spacing: \
                    [f'{10 ** (-_): .1f}' for _ in values]
                ax.getAxis('left').label.setPlainText(LABEL_RESISTANCE)
                if line is self.line_maximum:
                    self.label_3.setText("峰值")
                    ax.getViewBox().setYRange(-MAXIMUM_Y_LIM, -MINIMUM_Y_LIM)
                elif line is self.line_frame_max:
                    self.label_max_value.setText("每帧最大值")
                    ax.getViewBox().setYRange(-MAXIMUM_Y_LIM, -MINIMUM_Y_LIM)
            self.scaling = log
            self.__apply_y_lim()

    def set_enable_state(self):
        # 根据实际的开始/停止状态，设定各按钮是否激活
        self.button_start.setEnabled(not self.is_running)
        self.button_stop.setEnabled(self.is_running)
        self.button_save_to.setEnabled(self.is_running)
        if self.data_handler.output_file:
            self.button_save_to.setText("结束采集")
        else:
            self.button_save_to.setText("采集到...")
        if self.is_running:
            self.com_port.setEnabled(False)

    def __set_filter(self):
        # 为self.combo_filter_time逐项添加选项
        self.data_handler.set_filter("无", self.combo_filter_time.currentText())
        config['filter_time_index'] = self.combo_filter_time.currentIndex()
        save_config()

    def __set_interpolate_and_blur(self):
        interpolate = int(self.combo_interpolate.currentText())
        blur = float(self.combo_blur.currentText())
        self.data_handler.set_interpolation_and_blur(interpolate=interpolate, blur=blur)
        config['interpolate_index'] = self.combo_interpolate.currentIndex()
        config['blur_index'] = self.combo_blur.currentIndex()
        save_config()

    def __set_calibrator(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, "选择标定文件", "", "标定文件 (*.clb)")[0]
        if path:
            flag = self.data_handler.set_calibrator(path)
            if flag:
                self.__set_using_calibration(True)

    def __abandon_calibrator(self):
        self.data_handler.abandon_calibrator()
        self.__set_using_calibration(False)

    def initialize_buttons(self):
        self.button_start.clicked.connect(self.start)
        self.button_stop.clicked.connect(self.stop)
        for name in AVAILABLE_FILTER_NAMES:
            self.combo_filter_time.addItem(name)
        current_idx_filter_time = config.get('filter_time_index')
        if current_idx_filter_time < self.combo_filter_time.count():
            self.combo_filter_time.setCurrentIndex(current_idx_filter_time)
        self.combo_interpolate.setCurrentIndex(config.get('interpolate_index'))
        self.combo_blur.setCurrentIndex(config.get('blur_index'))
        self.__set_filter()
        self.__set_interpolate_and_blur()
        self.combo_filter_time.currentIndexChanged.connect(self.__set_filter)
        self.combo_interpolate.currentIndexChanged.connect(self.__set_interpolate_and_blur)
        self.combo_blur.currentIndexChanged.connect(self.__set_interpolate_and_blur)
        self.set_enable_state()
        self.button_set_zero.clicked.connect(self.data_handler.set_zero)
        self.button_abandon_zero.clicked.connect(self.data_handler.abandon_zero)
        self.button_save_to.clicked.connect(self.__trigger_save_button)

        str_port = config.get('port')
        if not isinstance(str_port, str):
            raise Exception('配置文件出错')
        self.com_port.setText(config['port'])
        # 标定功能
        self.button_load_calibration.clicked.connect(self.__set_calibrator)
        self.button_exit_calibration.clicked.connect(self.__abandon_calibrator)

    def __trigger_save_button(self):
        if self.data_handler.output_file:
            self.data_handler.close_output_file()
        else:
            file = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "选择输出路径",
                "",
                "数据库 (*.db)")
            if file[0]:
                self.data_handler.link_output_file(file[0])
        self.set_enable_state()

    def on_tab_changed(self, index):
        """标签页切换事件处理"""
        print(f"🔄 标签页切换: {self.current_active_tab} -> {index}")
        # 禁用之前的标签页更新（除了热力图标签页0）
        if self.current_active_tab != 0:
            self.tab_update_enabled[self.current_active_tab] = False
            print(f"🔇 标签页 {self.current_active_tab} 进入睡眠状态")
        # 激活当前标签页更新（除了热力图标签页0，它始终激活）
        self.current_active_tab = index
        if index != 0:
            self.tab_update_enabled[index] = True
            print(f"🔊 标签页 {index} 激活更新")
        # 如果当前有数据，立即更新新激活的标签页
        if (self.is_running and 
            hasattr(self.data_handler, 'value') and 
            self.data_handler.value and 
            index in self.tab_widgets):
            try:
                current_pressure_data = np.array(self.data_handler.value[-1])
                tangential_data = current_pressure_data
                # 只给所有分析标签页赋值，不触发分析
                for widget in self.tab_widgets.values():
                    if hasattr(widget, 'current_pressure_data'):
                        widget.current_pressure_data = tangential_data
                # 只有切换到增强切向力分析Tab时才重绘
                active_widget = self.tab_widgets.get(self.current_active_tab)
                if self.current_active_tab == 2 and active_widget is not None and hasattr(active_widget, 'update_view'):
                    active_widget.update_view(current_pressure_data)
                elif self.current_active_tab == 3 and active_widget is not None and hasattr(active_widget, 'update_view'):
                    active_widget.update_view(current_pressure_data)
                # 其它tab页只做轻量赋值，不做分析
            except Exception as e:
                print(f"⚠️ 立即更新标签页 {index} 失败: {e}")

    def detect_finger_press(self, pressure_data, min_area=10, min_pressure=0.01):
        """
        形态学方法检测是否有手指按压
        :param pressure_data: 当前帧压力矩阵 (numpy.ndarray)
        :param min_area: 有效区域最小面积
        :param min_pressure: 有效区域最小压力
        :return: bool, True=有手指, False=无手指
        """
        if pressure_data is None or pressure_data.size == 0:
            return False
        try:
            # 1. 阈值分割
            threshold = max(filters.threshold_otsu(pressure_data), min_pressure)
            binary_mask = pressure_data > threshold
            # 2. 连通区域分析
            labeled = measure.label(binary_mask)
            regions = measure.regionprops(labeled, intensity_image=pressure_data)
            for region in regions:
                if region.area >= min_area and region.max_intensity >= min_pressure:
                    return True  # 检测到有效手指按压
            return False
        except Exception as e:
            print(f"⚠️ detect_finger_press 错误: {e}")
            return False

    def trigger(self):
        """
        修改后的主触发器：
        1. 获取最新数据。
        2. 将数据分发给所有相关标签页（状态更新）。
        3. 仅对当前激活的标签页触发完整分析和重绘。
        """
        try:
            self.data_handler.trigger()
            with self.data_handler.lock:
                if not self.data_handler.value:
                    return
                # 获取当前帧的压力数据
                current_pressure_data = np.array(self.data_handler.value[-1])
                # 1. 更新始终激活的热力图和右侧图表
                self._update_heatmap_tab(current_pressure_data)
                # 2. 只给所有分析标签页赋值，不触发分析
                for widget in self.tab_widgets.values():
                    if hasattr(widget, 'current_pressure_data'):
                        widget.current_pressure_data = current_pressure_data
                # 3. 只有检测到有手指按压时才触发增强分析
                if hasattr(self, 'enhanced_force_widget'):
                    try:
                        if self.detect_finger_press(current_pressure_data):
                            if self.current_active_tab == 2:
                                # 只有增强切向力分析Tab激活时才重绘
                                self.enhanced_force_widget.update_view(current_pressure_data)
                            else:
                                # 其它情况下只分析不重绘
                                self.enhanced_force_widget.analyze_only(current_pressure_data)
                        else:
                            # 无手指，不分析
                            pass
                    except Exception as e:
                        print(f"⚠️ 在后台为 enhanced_force_widget 触发分析时出错: {e}")
                # 4. 仅重绘当前激活的标签页
                active_widget = self.tab_widgets.get(self.current_active_tab)
                if active_widget is not None:
                    try:
                        # 只有形态学分析页才做update_view
                        if self.current_active_tab == 3 and hasattr(active_widget, 'update_view'):
                            active_widget.update_view(current_pressure_data)
                        elif self.current_active_tab != 2 and hasattr(active_widget, 'update_view'):
                            # 其它tab页只做轻量赋值，不做分析
                            active_widget.current_pressure_data = current_pressure_data
                    except Exception as e:
                        print(f"⚠️ 更新激活的标签页 {self.current_active_tab} 时失败: {e}")
        except USBError:
            self.stop()
            QtWidgets.qApp.quit()
        except Exception as e:
            self.stop()
            raise e

    
    def _update_heatmap_tab(self, current_pressure_data):
        """更新热力图标签页"""
        self.plot.setImage(apply_swap(self.scaling(current_pressure_data.T)),
                          levels=self.y_lim)
        
        # 更新右侧的数据图表
        if self.data_handler.using_calibration:
            self.line_maximum.setData(self.data_handler.time, self.scaling(self.data_handler.summed))
        else:
            self.line_maximum.setData(self.data_handler.time, self.scaling(self.data_handler.maximum))
        
        self.line_tracing.setData(self.data_handler.t_tracing, self.scaling(self.data_handler.tracing))
        # 更新第三个图表：每帧最大值
        self.line_frame_max.setData(self.data_handler.time, self.scaling(self.data_handler.maximum))
    
    def _update_analysis_tabs(self, tangential_data):
        """按需更新分析标签页"""
        # 更新切向力分析标签页（索引1）
        if (self.tab_update_enabled.get(1, False) and 
            hasattr(self, 'tangential_force_widget')):
            try:
                self.tangential_force_widget.update_view(tangential_data)
            except Exception as e:
                print(f"⚠️ 更新切向力分析widget失败: {e}")
        
        # 更新增强切向力分析标签页（索引2）
        if (self.tab_update_enabled.get(2, False) and 
            hasattr(self, 'enhanced_force_widget')):
            try:
                self.enhanced_force_widget.update_view(tangential_data)
                print(f"✅ 更新增强切向力分析标签页 2")
            except Exception as e:
                print(f"⚠️ 更新增强切向力分析widget失败: {e}")
        
        # 更新形态学方法分析标签页（索引3，原来的索引4）
        if (self.tab_update_enabled.get(3, False) and 
            hasattr(self, 'morphological_widget')):
            try:
                self.morphological_widget.update_view(tangential_data)
                print(f"✅ 更新形态学分析标签页 3")
            except Exception as e:
                print(f"⚠️ 更新形态学分析widget失败: {e}")

    def trigger_null(self):
        self.plot.setImage(apply_swap(np.zeros(
            [_ * self.data_handler.interpolation.interp for _ in self.data_handler.driver.SENSOR_SHAPE]).T
                           - MAXIMUM_Y_LIM),
                           levels=self.y_lim)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.stop()
        super(Window, self).closeEvent(a0)
        sys.exit()


def start(mode='standard'):
    app = QtWidgets.QApplication(sys.argv)
    w = Window(mode)
    w.show()
    w.trigger_null()
    sys.exit(app.exec_())
