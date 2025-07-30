#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
切向力检测系统标定工具
用于对切向力检测算法进行性能评估和参数优化
"""

import sys
import os
import json
import time
from datetime import datetime
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QLabel, QTabWidget, QGroupBox,
                            QProgressBar, QTextEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QComboBox, QSpinBox, QDoubleSpinBox,
                            QCheckBox, QMessageBox, QFileDialog, QGridLayout,
                            QRadioButton)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QFont, QPixmap

# 添加项目路径以便导入
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'interfaces', 'ordinary'))
sys.path.insert(0, os.path.join(current_dir, 'backends'))

# 导入现有组件
from tangential_force_detection_system import TangentialForceDetectionEngine
from data_processing.data_handler import DataHandler
from interfaces.ordinary.unified_tangential_force_detector import UnifiedTangentialForceDetector


class CalibrationTask:
    """标定任务定义"""
    
    def __init__(self, name, angles, repetitions=5):
        self.name = name
        self.angles = angles  # 要测试的角度列表
        self.repetitions = repetitions  # 每个角度重复次数
        self.results = {}  # 存储结果
        self.completed = False
    
    def get_total_tests(self):
        """获取总测试次数"""
        return len(self.angles) * self.repetitions
    
    def add_result(self, angle, detected_angle, confidence):
        """添加检测结果"""
        if angle not in self.results:
            self.results[angle] = []
        self.results[angle].append({
            'detected_angle': detected_angle,
            'confidence': confidence,
            'error': abs(detected_angle - angle)
        })
    
    def get_statistics(self):
        """获取统计信息"""
        if not self.results:
            return {}
        
        stats = {}
        for angle, results in self.results.items():
            if results:
                errors = [r['error'] for r in results]
                confidences = [r['confidence'] for r in results]
                stats[angle] = {
                    'mean_error': np.mean(errors),
                    'std_error': np.std(errors),
                    'mean_confidence': np.mean(confidences),
                    'success_rate': sum(1 for e in errors if e < 15) / len(errors) * 100  # 15度内为成功
                }
        
        # 整体统计
        all_errors = [r['error'] for results in self.results.values() for r in results]
        all_confidences = [r['confidence'] for results in self.results.values() for r in results]
        
        stats['overall'] = {
            'mean_error': np.mean(all_errors),
            'std_error': np.std(all_errors),
            'mean_confidence': np.mean(all_confidences),
            'success_rate': sum(1 for e in all_errors if e < 15) / len(all_errors) * 100
        }
        
        return stats


class CalibrationWorker(QObject):
    """标定工作线程"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    test_completed = pyqtSignal(dict)
    calibration_finished = pyqtSignal(dict)
    
    def __init__(self, detection_engine, calibration_task, use_real_sensor=False, sensor_port=None):
        super().__init__()
        self.detection_engine = detection_engine
        self.calibration_task = calibration_task
        self.use_real_sensor = use_real_sensor
        self.sensor_port = sensor_port
        self.is_running = False
        self.data_handler = None
        
        # 如果使用真实传感器，初始化数据处理器
        if self.use_real_sensor:
            self._init_real_sensor()
        
    def _init_real_sensor(self):
        """初始化真实传感器"""
        try:
            from interfaces.ordinary.data_handler import DataHandler
            from backends.usb_driver import LargeUsbSensorDriver
            
            self.data_handler = DataHandler(LargeUsbSensorDriver, max_len=256)
            print("✅ 真实传感器数据处理器已初始化")
        except ImportError as e:
            print(f"❌ 无法初始化真实传感器: {e}")
            self.use_real_sensor = False
        
    def start_calibration(self):
        """开始标定过程"""
        self.is_running = True
        self.current_test = 0
        total_tests = self.calibration_task.get_total_tests()
        
        if self.use_real_sensor:
            self.status_updated.emit("连接真实传感器...")
            if not self._connect_real_sensor():
                self.status_updated.emit("❌ 传感器连接失败，切换到模拟模式")
                self.use_real_sensor = False
        
        self.status_updated.emit("标定开始...")
        
        if self.use_real_sensor:
            self._real_sensor_calibration_process(total_tests)
        else:
            self._simulate_calibration_process(total_tests)
    
    def _connect_real_sensor(self):
        """连接真实传感器"""
        if self.data_handler:
            try:
                success = self.data_handler.connect(self.sensor_port or 'USB0')
                if success:
                    print(f"✅ 传感器已连接: {self.sensor_port}")
                    return True
                else:
                    print(f"❌ 传感器连接失败: {self.sensor_port}")
                    return False
            except Exception as e:
                print(f"❌ 传感器连接错误: {e}")
                return False
        return False
    
    def _real_sensor_calibration_process(self, total_tests):
        """真实传感器标定过程"""
        import time
        
        for angle in self.calibration_task.angles:
            if not self.is_running:
                break
                
            self.status_updated.emit(f"请将传感器调整到 {angle}° 方向，然后施加切向力")
            
            # 等待用户准备
            time.sleep(2)
            
            for rep in range(self.calibration_task.repetitions):
                if not self.is_running:
                    break
                
                self.status_updated.emit(f"角度 {angle}°, 第 {rep+1}/{self.calibration_task.repetitions} 次测试")
                
                # 从真实传感器获取数据
                detected_result = self._get_real_sensor_data()
                
                if detected_result:
                    detected_angle = detected_result.get('angle', angle)
                    confidence = detected_result.get('confidence', 0.5)
                else:
                    # 如果获取失败，使用默认值
                    detected_angle = angle
                    confidence = 0.1
                    self.status_updated.emit("⚠️ 数据获取失败，使用默认值")
                
                # 添加结果
                self.calibration_task.add_result(angle, detected_angle, confidence)
                
                # 发出测试完成信号
                test_result = {
                    'angle': angle,
                    'detected_angle': detected_angle,
                    'confidence': confidence,
                    'repetition': rep + 1
                }
                self.test_completed.emit(test_result)
                
                # 更新进度
                self.current_test += 1
                progress = int(self.current_test / total_tests * 100)
                self.progress_updated.emit(progress)
                
                # 测试间隔
                time.sleep(1)
        
        # 断开传感器连接
        if self.data_handler:
            self.data_handler.disconnect()
        
        # 标定完成
        if self.is_running:
            stats = self.calibration_task.get_statistics()
            self.calibration_finished.emit(stats)
            self.status_updated.emit("标定完成!")
    
    def _get_real_sensor_data(self):
        """从真实传感器获取数据"""
        try:
            if not self.data_handler:
                return None
            
            # 触发数据读取
            self.data_handler.trigger()
            
            if not self.data_handler.value:
                return None
            
            # 获取最新压力矩阵
            latest_pressure = np.array(self.data_handler.value[-1])
            
            # 使用检测引擎进行分析
            if self.detection_engine:
                result = self.detection_engine.process_pressure_data(latest_pressure)
                if result and result.get('consensus'):
                    consensus = result['consensus']
                    return {
                        'angle': consensus.get('consensus_angle', 0),
                        'confidence': consensus.get('consensus_confidence', 0)
                    }
            
            return None
            
        except Exception as e:
            print(f"⚠️ 真实传感器数据获取错误: {e}")
            return None
    
    def _simulate_calibration_process(self, total_tests):
        """模拟标定过程（在实际应用中应该替换为真实的测试流程）"""
        import time
        
        for angle in self.calibration_task.angles:
            if not self.is_running:
                break
                
            self.status_updated.emit(f"模拟测试角度: {angle}°")
            
            for rep in range(self.calibration_task.repetitions):
                if not self.is_running:
                    break
                
                # 模拟检测过程
                time.sleep(0.1)  # 模拟检测时间
                
                # 生成模拟的检测结果（添加一些噪声）
                noise = np.random.normal(0, 5)  # 5度标准差的噪声
                detected_angle = angle + noise
                confidence = np.random.uniform(0.7, 0.95)
                
                # 添加结果
                self.calibration_task.add_result(angle, detected_angle, confidence)
                
                # 发出测试完成信号
                test_result = {
                    'angle': angle,
                    'detected_angle': detected_angle,
                    'confidence': confidence,
                    'repetition': rep + 1
                }
                self.test_completed.emit(test_result)
                
                # 更新进度
                self.current_test += 1
                progress = int(self.current_test / total_tests * 100)
                self.progress_updated.emit(progress)
        
        # 标定完成
        if self.is_running:
            stats = self.calibration_task.get_statistics()
            self.calibration_finished.emit(stats)
            self.status_updated.emit("标定完成!")
    
    def stop_calibration(self):
        """停止标定过程"""
        self.is_running = False
        if self.data_handler:
            self.data_handler.disconnect()
        self.status_updated.emit("标定已停止")


class CalibrationInterface(QWidget):
    """标定界面"""
    
    calibration_started = pyqtSignal()
    calibration_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.calibration_tasks = self._create_default_tasks()
        self.current_task = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 任务选择组
        task_group = QGroupBox("标定任务")
        task_layout = QVBoxLayout(task_group)
        
        # 任务选择
        task_select_layout = QHBoxLayout()
        task_select_layout.addWidget(QLabel("选择任务:"))
        self.task_combo = QComboBox()
        self.task_combo.addItems([
            "8方向基础标定",
            "16方向精确标定", 
            "自定义角度标定",
            "重复性测试"
        ])
        task_select_layout.addWidget(self.task_combo)
        task_layout.addLayout(task_select_layout)
        
        # 参数设置
        params_layout = QGridLayout()
        
        # 重复次数
        params_layout.addWidget(QLabel("重复次数:"), 0, 0)
        self.repetitions_spin = QSpinBox()
        self.repetitions_spin.setRange(1, 20)
        self.repetitions_spin.setValue(5)
        params_layout.addWidget(self.repetitions_spin, 0, 1)
        
        # 角度容差
        params_layout.addWidget(QLabel("成功容差:"), 1, 0)
        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setRange(1.0, 45.0)
        self.tolerance_spin.setValue(15.0)
        self.tolerance_spin.setSuffix("°")
        params_layout.addWidget(self.tolerance_spin, 1, 1)
        
        # 在参数设置区域添加数据源选择
        data_source_group = QGroupBox("数据源选择")
        data_source_layout = QVBoxLayout(data_source_group)
        
        self.real_sensor_radio = QRadioButton("真实传感器数据")
        self.simulated_radio = QRadioButton("模拟数据 (用于测试)")
        self.simulated_radio.setChecked(True)  # 默认选择模拟数据
        
        data_source_layout.addWidget(self.real_sensor_radio)
        data_source_layout.addWidget(self.simulated_radio)
        
        # 端口设置 (仅在使用真实传感器时可用)
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("传感器端口:"))
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        self.port_combo.addItems(['COM1', 'COM2', 'COM3', 'USB0', 'USB1'])
        self.port_combo.setEnabled(False)  # 默认禁用
        port_layout.addWidget(self.port_combo)
        data_source_layout.addLayout(port_layout)
        
        # 连接信号
        self.real_sensor_radio.toggled.connect(self.on_data_source_changed)
        
        task_layout.addWidget(data_source_group)
        
        task_layout.addLayout(params_layout)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始标定")
        self.start_btn.setObjectName("successButton")
        self.start_btn.clicked.connect(self.calibration_started.emit)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止标定")
        self.stop_btn.setObjectName("dangerButton")
        self.stop_btn.clicked.connect(self.calibration_stopped.emit)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        task_layout.addLayout(control_layout)
        layout.addWidget(task_group)
        
        # 进度显示组
        progress_group = QGroupBox("标定进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.status_label = QLabel("准备就绪")
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.current_test_label = QLabel("当前测试: -")
        progress_layout.addWidget(self.current_test_label)
        
        layout.addWidget(progress_group)
        
        # 实时结果组
        results_group = QGroupBox("实时结果")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(['目标角度', '检测角度', '误差', '置信度'])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_layout.addWidget(self.results_table)
        
        layout.addWidget(results_group)
    
    def _create_default_tasks(self):
        """创建默认标定任务"""
        tasks = [
            CalibrationTask("8方向基础", [0, 45, 90, 135, 180, 225, 270, 315]),
            CalibrationTask("16方向精确", [i * 22.5 for i in range(16)]),
            CalibrationTask("自定义", [0, 30, 60, 90, 120, 150]),
            CalibrationTask("重复性", [0, 90, 180, 270], repetitions=10)
        ]
        return tasks
    
    def get_current_task(self):
        """获取当前选择的任务"""
        task_index = self.task_combo.currentIndex()
        task = self.calibration_tasks[task_index]
        task.repetitions = self.repetitions_spin.value()
        return task
    
    def update_progress(self, progress):
        """更新进度"""
        self.progress_bar.setValue(progress)
    
    def update_status(self, message):
        """更新状态"""
        self.status_label.setText(message)
    
    def update_current_test(self, test_info):
        """更新当前测试信息"""
        angle = test_info['angle']
        rep = test_info['repetition']
        self.current_test_label.setText(f"当前测试: {angle}° (第{rep}次)")
    
    def add_result_row(self, result):
        """添加结果行"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        self.results_table.setItem(row, 0, QTableWidgetItem(f"{result['angle']:.1f}°"))
        self.results_table.setItem(row, 1, QTableWidgetItem(f"{result['detected_angle']:.1f}°"))
        
        error = abs(result['detected_angle'] - result['angle'])
        self.results_table.setItem(row, 2, QTableWidgetItem(f"{error:.1f}°"))
        self.results_table.setItem(row, 3, QTableWidgetItem(f"{result['confidence']:.3f}"))
        
        # 滚动到最新行
        self.results_table.scrollToBottom()
    
    def set_calibration_active(self, active):
        """设置标定状态"""
        self.start_btn.setEnabled(not active)
        self.stop_btn.setEnabled(active)
        self.task_combo.setEnabled(not active)
        self.repetitions_spin.setEnabled(not active)
        
        if not active:
            self.progress_bar.setValue(0)
            self.current_test_label.setText("当前测试: -")

    def on_data_source_changed(self):
        """处理数据源选择的改变"""
        if self.real_sensor_radio.isChecked():
            self.port_combo.setEnabled(True)
        else:
            self.port_combo.setEnabled(False)


class CalibrationResultsWidget(QWidget):
    """标定结果分析组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 统计摘要组
        summary_group = QGroupBox("标定摘要")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_table = QTableWidget(5, 2)
        self.summary_table.setHorizontalHeaderLabels(['指标', '数值'])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        summary_items = [
            ('平均误差', '-'),
            ('误差标准差', '-'),
            ('平均置信度', '-'),
            ('成功率', '-'),
            ('推荐阈值', '-')
        ]
        
        for i, (metric, value) in enumerate(summary_items):
            self.summary_table.setItem(i, 0, QTableWidgetItem(metric))
            self.summary_table.setItem(i, 1, QTableWidgetItem(value))
        
        summary_layout.addWidget(self.summary_table)
        layout.addWidget(summary_group)
        
        # 详细结果组
        details_group = QGroupBox("详细分析")
        details_layout = QVBoxLayout(details_group)
        
        self.details_table = QTableWidget(0, 5)
        self.details_table.setHorizontalHeaderLabels(['角度', '平均误差', '误差标准差', '平均置信度', '成功率'])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        details_layout.addWidget(self.details_table)
        
        layout.addWidget(details_group)
        
        # 操作按钮
        actions_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存结果")
        save_btn.clicked.connect(self.save_results)
        actions_layout.addWidget(save_btn)
        
        export_btn = QPushButton("导出报告")
        export_btn.clicked.connect(self.export_report)
        actions_layout.addWidget(export_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        self.calibration_stats = None
    
    def update_results(self, stats):
        """更新标定结果"""
        self.calibration_stats = stats
        
        if 'overall' in stats:
            overall = stats['overall']
            
            # 更新摘要表
            self.summary_table.setItem(0, 1, QTableWidgetItem(f"{overall['mean_error']:.1f}°"))
            self.summary_table.setItem(1, 1, QTableWidgetItem(f"{overall['std_error']:.1f}°"))
            self.summary_table.setItem(2, 1, QTableWidgetItem(f"{overall['mean_confidence']:.3f}"))
            self.summary_table.setItem(3, 1, QTableWidgetItem(f"{overall['success_rate']:.1f}%"))
            
            # 推荐阈值 (平均误差 + 2倍标准差)
            recommended_threshold = overall['mean_error'] + 2 * overall['std_error']
            self.summary_table.setItem(4, 1, QTableWidgetItem(f"{recommended_threshold:.1f}°"))
        
        # 更新详细表
        self.details_table.setRowCount(0)
        for angle, angle_stats in stats.items():
            if angle != 'overall':
                row = self.details_table.rowCount()
                self.details_table.insertRow(row)
                
                self.details_table.setItem(row, 0, QTableWidgetItem(f"{angle}°"))
                self.details_table.setItem(row, 1, QTableWidgetItem(f"{angle_stats['mean_error']:.1f}°"))
                self.details_table.setItem(row, 2, QTableWidgetItem(f"{angle_stats['std_error']:.1f}°"))
                self.details_table.setItem(row, 3, QTableWidgetItem(f"{angle_stats['mean_confidence']:.3f}"))
                self.details_table.setItem(row, 4, QTableWidgetItem(f"{angle_stats['success_rate']:.1f}%"))
    
    def save_results(self):
        """保存标定结果"""
        if not self.calibration_stats:
            QMessageBox.warning(self, "警告", "没有可保存的标定结果")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存标定结果", 
            f"calibration_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.calibration_stats, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "成功", f"标定结果已保存到:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败:\n{e}")
    
    def export_report(self):
        """导出标定报告"""
        if not self.calibration_stats:
            QMessageBox.warning(self, "警告", "没有可导出的标定结果")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出标定报告",
            f"calibration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            try:
                self._generate_report(filename)
                QMessageBox.information(self, "成功", f"标定报告已导出到:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败:\n{e}")
    
    def _generate_report(self, filename):
        """生成标定报告"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("切向力检测系统标定报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if 'overall' in self.calibration_stats:
                overall = self.calibration_stats['overall']
                f.write("整体性能摘要:\n")
                f.write(f"  平均误差: {overall['mean_error']:.1f}°\n")
                f.write(f"  误差标准差: {overall['std_error']:.1f}°\n")
                f.write(f"  平均置信度: {overall['mean_confidence']:.3f}\n")
                f.write(f"  成功率: {overall['success_rate']:.1f}%\n\n")
            
            f.write("各角度详细结果:\n")
            f.write("-" * 50 + "\n")
            for angle, stats in self.calibration_stats.items():
                if angle != 'overall':
                    f.write(f"角度 {angle}°:\n")
                    f.write(f"  平均误差: {stats['mean_error']:.1f}°\n")
                    f.write(f"  误差标准差: {stats['std_error']:.1f}°\n")
                    f.write(f"  平均置信度: {stats['mean_confidence']:.3f}\n")
                    f.write(f"  成功率: {stats['success_rate']:.1f}%\n\n")


class CalibrationTool(QMainWindow):
    """标定工具主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("切向力检测系统标定工具 v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        self.setup_backend()
        self.setup_connections()
        
        self.calibration_worker = None
        
    def setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建标签页
        self.tabs = QTabWidget()
        
        # 标定执行标签页
        self.calibration_interface = CalibrationInterface()
        self.tabs.addTab(self.calibration_interface, "标定执行")
        
        # 结果分析标签页
        self.results_widget = CalibrationResultsWidget()
        self.tabs.addTab(self.results_widget, "结果分析")
        
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tabs)
        
    def setup_backend(self):
        """设置后端组件"""
        # 初始化检测引擎
        self.detection_engine = TangentialForceDetectionEngine()
        
    def setup_connections(self):
        """设置信号连接"""
        self.calibration_interface.calibration_started.connect(self.start_calibration)
        self.calibration_interface.calibration_stopped.connect(self.stop_calibration)
        
    def start_calibration(self):
        """启动标定过程"""
        # 获取标定参数
        task_index = self.calibration_interface.task_combo.currentIndex()
        repetitions = self.calibration_interface.repetitions_spin.value()
        tolerance = self.calibration_interface.tolerance_spin.value()
        
        # 获取数据源选择
        use_real_sensor = self.calibration_interface.real_sensor_radio.isChecked()
        sensor_port = self.calibration_interface.port_combo.currentText() if use_real_sensor else None
        
        # 创建标定任务
        task = self.calibration_interface.calibration_tasks[task_index]
        task.repetitions = repetitions
        task.tolerance = tolerance
        
        # 显示开始信息
        source_info = f"真实传感器 ({sensor_port})" if use_real_sensor else "模拟数据"
        print(f"🚀 启动标定 - 数据源: {source_info}")
        
        # 在结果表中添加系统信息（自定义格式）
        start_info = {
            'angle': 0,
            'detected_angle': 0,
            'confidence': 1.0,
            'source': source_info,
            'task': task.name
        }
        
        # 创建并启动标定工作器
        self.calibration_worker = CalibrationWorker(
            self.detection_engine, 
            task, 
            use_real_sensor=use_real_sensor,
            sensor_port=sensor_port
        )
        
        # 连接信号
        self.calibration_worker.progress_updated.connect(self.calibration_interface.update_progress)
        self.calibration_worker.status_updated.connect(self.calibration_interface.update_status)
        self.calibration_worker.test_completed.connect(self.on_test_completed)
        self.calibration_worker.calibration_finished.connect(self.on_calibration_finished)
        
        # 启动标定
        self.calibration_worker.start_calibration()
        
        # 更新UI状态
        self.calibration_interface.set_calibration_active(True)
        
    def stop_calibration(self):
        """停止标定"""
        if self.calibration_worker:
            self.calibration_worker.stop_calibration()
        
        self.calibration_interface.set_calibration_active(False)
        
    def on_test_completed(self, result):
        """处理单次测试完成"""
        self.calibration_interface.update_current_test(result)
        self.calibration_interface.add_result_row(result)
        
    def on_calibration_finished(self, stats):
        """处理标定完成"""
        self.calibration_interface.set_calibration_active(False)
        
        # 切换到结果分析页
        self.tabs.setCurrentIndex(1)
        
        # 更新结果显示
        self.results_widget.update_results(stats)
        
        QMessageBox.information(self, "标定完成", 
                              f"标定任务已完成!\n"
                              f"平均误差: {stats['overall']['mean_error']:.1f}°\n"
                              f"成功率: {stats['overall']['success_rate']:.1f}%")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    app.setApplicationName("切向力检测标定工具")
    app.setApplicationVersion("1.0")
    
    main_window = CalibrationTool()
    main_window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 