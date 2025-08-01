# -*- coding: utf-8 -*-
"""
3D可视化性能对比测试
Performance Comparison Test for 3D Visualization

本脚本对比PyQtGraph和matplotlib在3D可视化方面的性能差异
包括渲染速度、内存使用、交互性能等指标
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import pyqtgraph as pg
from pyqtgraph.opengl import GLViewWidget, GLSurfacePlotItem
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import QTimer, pyqtSignal
import psutil
import threading
import gc
import sys
import os

# 设置matplotlib后端
import matplotlib
matplotlib.use('Qt5Agg', force=True)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_memory = None
    
    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
    
    def end_monitoring(self):
        """结束监控并返回结果"""
        if self.start_time is None:
            return None
        
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        duration = end_time - self.start_time
        memory_used = end_memory - self.start_memory
        
        return {
            'duration': duration,
            'memory_used': memory_used,
            'peak_memory': end_memory
        }

class Matplotlib3DRenderer:
    """Matplotlib 3D渲染器"""
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.surface = None
        self.monitor = PerformanceMonitor()
        
        # 设置样式
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
    
    def render_3d_surface(self, data):
        """渲染3D表面"""
        self.monitor.start_monitoring()
        
        try:
            # 清除之前的表面
            if self.surface is not None:
                self.surface.remove()
            
            # 创建网格
            rows, cols = data.shape
            x = np.arange(cols)
            y = np.arange(rows)
            X, Y = np.meshgrid(x, y)
            
            # 绘制3D表面
            self.surface = self.ax.plot_surface(
                X, Y, data,
                cmap='plasma',
                alpha=0.8,
                linewidth=0,
                antialiased=True
            )
            
            # 设置标题和标签
            self.ax.set_title('Matplotlib 3D压力分布', color='white', fontsize=12)
            self.ax.set_xlabel('X', color='white')
            self.ax.set_ylabel('Y', color='white')
            self.ax.set_zlabel('压力值', color='white')
            
            # 更新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"Matplotlib渲染错误: {e}")
        
        finally:
            result = self.monitor.end_monitoring()
            return result
    
    def update_data(self, data):
        """更新数据"""
        return self.render_3d_surface(data)
    
    def get_widget(self):
        """获取widget"""
        return self.canvas

class PyQtGraph3DRenderer:
    """PyQtGraph 3D渲染器"""
    
    def __init__(self, parent=None):
        self.view = GLViewWidget()
        self.surface = None
        self.monitor = PerformanceMonitor()
        
        # 设置背景色
        self.view.setBackgroundColor('k')
        
        # 添加网格
        grid = pg.opengl.GLGridItem()
        self.view.addItem(grid)
    
    def render_3d_surface(self, data):
        """渲染3D表面"""
        self.monitor.start_monitoring()
        
        try:
            # 移除之前的表面
            if self.surface is not None:
                self.view.removeItem(self.surface)
            
            # 创建PyQtGraph表面
            self.surface = GLSurfacePlotItem(
                z=data,
                color=(1, 1, 1, 0.3),
                shader='shaded',
                glOptions='additive'
            )
            
            # 添加到视图
            self.view.addItem(self.surface)
            
        except Exception as e:
            print(f"PyQtGraph渲染错误: {e}")
        
        finally:
            result = self.monitor.end_monitoring()
            return result
    
    def update_data(self, data):
        """更新数据"""
        return self.render_3d_surface(data)
    
    def get_widget(self):
        """获取widget"""
        return self.view

class PerformanceTestApp:
    """性能测试应用"""
    
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        # 创建主窗口
        self.window = QWidget()
        self.window.setWindowTitle('3D可视化性能对比测试')
        self.window.setGeometry(100, 100, 1200, 800)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 创建控制面板
        control_layout = QHBoxLayout()
        
        # 测试按钮
        self.test_btn = QPushButton('开始性能测试')
        self.test_btn.clicked.connect(self.run_performance_test)
        control_layout.addWidget(self.test_btn)
        
        # 数据大小选择
        self.size_label = QLabel('数据大小:')
        control_layout.addWidget(self.size_label)
        
        self.size_combo = QPushButton('64x64')
        self.size_combo.clicked.connect(self.cycle_data_size)
        control_layout.addWidget(self.size_combo)
        
        # 更新频率选择
        self.freq_label = QLabel('更新频率(Hz):')
        control_layout.addWidget(self.freq_label)
        
        self.freq_combo = QPushButton('30Hz')
        self.freq_combo.clicked.connect(self.cycle_update_frequency)
        control_layout.addWidget(self.freq_combo)
        
        layout.addLayout(control_layout)
        
        # 创建渲染器
        self.matplotlib_renderer = Matplotlib3DRenderer()
        self.pyqtgraph_renderer = PyQtGraph3DRenderer()
        
        # 创建显示区域
        display_layout = QHBoxLayout()
        
        # Matplotlib区域
        matplotlib_layout = QVBoxLayout()
        matplotlib_layout.addWidget(QLabel('Matplotlib 3D'))
        matplotlib_layout.addWidget(self.matplotlib_renderer.get_widget())
        display_layout.addLayout(matplotlib_layout)
        
        # PyQtGraph区域
        pyqtgraph_layout = QVBoxLayout()
        pyqtgraph_layout.addWidget(QLabel('PyQtGraph 3D'))
        pyqtgraph_layout.addWidget(self.pyqtgraph_renderer.get_widget())
        display_layout.addLayout(pyqtgraph_layout)
        
        layout.addLayout(display_layout)
        
        # 结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(200)
        layout.addWidget(self.result_text)
        
        self.window.setLayout(layout)
        
        # 测试参数
        self.data_sizes = [(32, 32), (64, 64), (128, 128)]
        self.current_size_index = 1
        self.update_frequencies = [10, 30, 60]
        self.current_freq_index = 1
        
        # 测试状态
        self.is_testing = False
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.update_test_data)
        
        # 测试数据
        self.test_data = None
        self.frame_count = 0
        self.test_results = {
            'matplotlib': {'times': [], 'memory': [], 'fps': []},
            'pyqtgraph': {'times': [], 'memory': [], 'fps': []}
        }
    
    def cycle_data_size(self):
        """循环切换数据大小"""
        self.current_size_index = (self.current_size_index + 1) % len(self.data_sizes)
        size = self.data_sizes[self.current_size_index]
        self.size_combo.setText(f'{size[0]}x{size[1]}')
    
    def cycle_update_frequency(self):
        """循环切换更新频率"""
        self.current_freq_index = (self.current_freq_index + 1) % len(self.update_frequencies)
        freq = self.update_frequencies[self.current_freq_index]
        self.freq_combo.setText(f'{freq}Hz')
    
    def generate_test_data(self, size):
        """生成测试数据"""
        rows, cols = size
        
        # 创建基础压力分布
        x = np.linspace(-2, 2, cols)
        y = np.linspace(-2, 2, rows)
        X, Y = np.meshgrid(x, y)
        
        # 创建多个压力中心
        centers = [
            (0, 0, 1.0),
            (-1, -1, 0.8),
            (1, 1, 0.6),
            (-0.5, 1, 0.4),
            (1, -0.5, 0.3)
        ]
        
        data = np.zeros((rows, cols))
        for cx, cy, intensity in centers:
            # 高斯分布
            r_squared = (X - cx)**2 + (Y - cy)**2
            data += intensity * np.exp(-r_squared / 0.5)
        
        # 添加噪声
        noise = np.random.normal(0, 0.05, (rows, cols))
        data += noise
        
        # 确保数据在合理范围内
        data = np.clip(data, 0, 1)
        
        return data
    
    def run_performance_test(self):
        """运行性能测试"""
        if self.is_testing:
            self.stop_test()
            return
        
        # 获取测试参数
        data_size = self.data_sizes[self.current_size_index]
        update_freq = self.update_frequencies[self.current_freq_index]
        
        # 生成测试数据
        self.test_data = self.generate_test_data(data_size)
        
        # 重置测试结果
        self.test_results = {
            'matplotlib': {'times': [], 'memory': [], 'fps': []},
            'pyqtgraph': {'times': [], 'memory': [], 'fps': []}
        }
        self.frame_count = 0
        
        # 开始测试
        self.is_testing = True
        self.test_btn.setText('停止测试')
        
        # 设置定时器
        interval = int(1000 / update_freq)  # 毫秒
        self.test_timer.start(interval)
        
        # 显示测试信息
        self.log_message(f"开始性能测试:")
        self.log_message(f"数据大小: {data_size[0]}x{data_size[1]}")
        self.log_message(f"更新频率: {update_freq}Hz")
        self.log_message(f"测试时长: 10秒")
        self.log_message("=" * 50)
    
    def stop_test(self):
        """停止测试"""
        self.is_testing = False
        self.test_timer.stop()
        self.test_btn.setText('开始性能测试')
        
        # 分析结果
        self.analyze_results()
    
    def update_test_data(self):
        """更新测试数据"""
        if not self.is_testing:
            return
        
        # 添加一些变化
        noise = np.random.normal(0, 0.02, self.test_data.shape)
        current_data = self.test_data + noise
        current_data = np.clip(current_data, 0, 1)
        
        # 测试Matplotlib
        try:
            matplotlib_result = self.matplotlib_renderer.update_data(current_data)
            if matplotlib_result:
                self.test_results['matplotlib']['times'].append(matplotlib_result['duration'])
                self.test_results['matplotlib']['memory'].append(matplotlib_result['memory_used'])
        except Exception as e:
            self.log_message(f"Matplotlib更新错误: {e}")
        
        # 测试PyQtGraph
        try:
            pyqtgraph_result = self.pyqtgraph_renderer.update_data(current_data)
            if pyqtgraph_result:
                self.test_results['pyqtgraph']['times'].append(pyqtgraph_result['duration'])
                self.test_results['pyqtgraph']['memory'].append(pyqtgraph_result['memory_used'])
        except Exception as e:
            self.log_message(f"PyQtGraph更新错误: {e}")
        
        self.frame_count += 1
        
        # 10秒后停止测试
        if self.frame_count >= 10 * self.update_frequencies[self.current_freq_index]:
            self.stop_test()
    
    def analyze_results(self):
        """分析测试结果"""
        self.log_message("\n" + "=" * 50)
        self.log_message("性能测试结果:")
        self.log_message("=" * 50)
        
        for renderer_name, results in self.test_results.items():
            if not results['times']:
                self.log_message(f"{renderer_name}: 无有效数据")
                continue
            
            times = np.array(results['times'])
            memory = np.array(results['memory'])
            
            avg_time = np.mean(times) * 1000  # 转换为毫秒
            max_time = np.max(times) * 1000
            min_time = np.min(times) * 1000
            std_time = np.std(times) * 1000
            
            avg_memory = np.mean(memory)
            max_memory = np.max(memory)
            
            theoretical_fps = 1.0 / avg_time * 1000 if avg_time > 0 else 0
            
            self.log_message(f"\n{renderer_name.upper()}:")
            self.log_message(f"  平均渲染时间: {avg_time:.2f}ms")
            self.log_message(f"  最大渲染时间: {max_time:.2f}ms")
            self.log_message(f"  最小渲染时间: {min_time:.2f}ms")
            self.log_message(f"  时间标准差: {std_time:.2f}ms")
            self.log_message(f"  平均内存使用: {avg_memory:.2f}MB")
            self.log_message(f"  最大内存使用: {max_memory:.2f}MB")
            self.log_message(f"  理论最大FPS: {theoretical_fps:.1f}")
        
        # 性能对比
        self.log_message("\n性能对比:")
        if (self.test_results['matplotlib']['times'] and 
            self.test_results['pyqtgraph']['times']):
            
            mpl_avg = np.mean(self.test_results['matplotlib']['times']) * 1000
            pg_avg = np.mean(self.test_results['pyqtgraph']['times']) * 1000
            
            if mpl_avg > 0 and pg_avg > 0:
                speed_ratio = mpl_avg / pg_avg
                self.log_message(f"  PyQtGraph比Matplotlib快 {speed_ratio:.2f}倍")
                
                if speed_ratio > 1.5:
                    self.log_message("  🏆 PyQtGraph性能明显更优")
                elif speed_ratio > 1.1:
                    self.log_message("  ✅ PyQtGraph性能略优")
                else:
                    self.log_message("  ⚖️ 两者性能相近")
    
    def log_message(self, message):
        """记录消息"""
        self.result_text.append(message)
        # 滚动到底部
        scrollbar = self.result_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def run(self):
        """运行应用"""
        self.window.show()
        return self.app.exec_()

def main():
    """主函数"""
    print("🚀 启动3D可视化性能对比测试...")
    
    # 创建测试应用
    app = PerformanceTestApp()
    
    # 运行应用
    result = app.run()
    
    print("✅ 测试完成")
    return result

if __name__ == "__main__":
    main() 