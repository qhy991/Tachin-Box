# -*- coding: utf-8 -*-
"""
快速3D可视化性能对比测试
Quick Performance Comparison Test for 3D Visualization

简化版本，专注于核心性能指标对比
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
from PyQt5.QtCore import QTimer
import psutil
import sys

# 设置matplotlib后端
import matplotlib
matplotlib.use('Qt5Agg', force=True)

class QuickPerformanceTest:
    """快速性能测试类"""
    
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        # 创建窗口
        self.window = QWidget()
        self.window.setWindowTitle('快速3D性能对比测试')
        self.window.setGeometry(100, 100, 1000, 600)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 控制按钮
        control_layout = QHBoxLayout()
        self.test_btn = QPushButton('开始测试')
        self.test_btn.clicked.connect(self.run_test)
        control_layout.addWidget(self.test_btn)
        
        self.result_label = QLabel('点击开始测试按钮进行性能对比')
        control_layout.addWidget(self.result_label)
        layout.addLayout(control_layout)
        
        # 结果显示
        self.result_text = QTextEdit()
        layout.addWidget(self.result_text)
        
        self.window.setLayout(layout)
        
        # 测试数据
        self.test_data = self.generate_test_data()
        
    def generate_test_data(self):
        """生成测试数据"""
        size = (64, 64)
        rows, cols = size
        
        # 创建压力分布数据
        x = np.linspace(-2, 2, cols)
        y = np.linspace(-2, 2, rows)
        X, Y = np.meshgrid(x, y)
        
        # 多个压力中心
        centers = [
            (0, 0, 1.0),
            (-1, -1, 0.8),
            (1, 1, 0.6),
            (-0.5, 1, 0.4),
            (1, -0.5, 0.3)
        ]
        
        data = np.zeros((rows, cols))
        for cx, cy, intensity in centers:
            r_squared = (X - cx)**2 + (Y - cy)**2
            data += intensity * np.exp(-r_squared / 0.5)
        
        # 添加噪声
        noise = np.random.normal(0, 0.05, (rows, cols))
        data += noise
        data = np.clip(data, 0, 1)
        
        return data
    
    def test_matplotlib_performance(self):
        """测试Matplotlib性能"""
        self.log_message("测试Matplotlib 3D渲染性能...")
        
        # 创建matplotlib图形
        fig = Figure(figsize=(6, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111, projection='3d')
        
        # 设置样式
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        times = []
        memory_usage = []
        
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024
        
        # 进行多次渲染测试
        for i in range(10):
            start_time = time.time()
            
            # 清除之前的表面
            ax.clear()
            ax.set_facecolor('black')
            
            # 创建网格
            rows, cols = self.test_data.shape
            x = np.arange(cols)
            y = np.arange(rows)
            X, Y = np.meshgrid(x, y)
            
            # 添加一些变化
            noise = np.random.normal(0, 0.02, self.test_data.shape)
            current_data = self.test_data + noise
            current_data = np.clip(current_data, 0, 1)
            
            # 绘制3D表面
            surface = ax.plot_surface(
                X, Y, current_data,
                cmap='plasma',
                alpha=0.8,
                linewidth=0,
                antialiased=True
            )
            
            # 更新画布
            canvas.draw()
            
            end_time = time.time()
            render_time = (end_time - start_time) * 1000  # 毫秒
            times.append(render_time)
            
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_usage.append(current_memory - start_memory)
            
            self.log_message(f"  第{i+1}次渲染: {render_time:.2f}ms")
        
        # 计算统计结果
        avg_time = np.mean(times)
        max_time = np.max(times)
        min_time = np.min(times)
        avg_memory = np.mean(memory_usage)
        
        self.log_message(f"Matplotlib结果:")
        self.log_message(f"  平均渲染时间: {avg_time:.2f}ms")
        self.log_message(f"  最大渲染时间: {max_time:.2f}ms")
        self.log_message(f"  最小渲染时间: {min_time:.2f}ms")
        self.log_message(f"  平均内存使用: {avg_memory:.2f}MB")
        
        return {
            'avg_time': avg_time,
            'max_time': max_time,
            'min_time': min_time,
            'avg_memory': avg_memory
        }
    
    def test_pyqtgraph_performance(self):
        """测试PyQtGraph性能"""
        self.log_message("测试PyQtGraph 3D渲染性能...")
        
        # 创建PyQtGraph视图
        view = GLViewWidget()
        view.setBackgroundColor('k')
        
        # 添加网格
        grid = pg.opengl.GLGridItem()
        view.addItem(grid)
        
        times = []
        memory_usage = []
        
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024
        
        surface = None
        
        # 进行多次渲染测试
        for i in range(10):
            start_time = time.time()
            
            # 移除之前的表面
            if surface is not None:
                view.removeItem(surface)
            
            # 添加一些变化
            noise = np.random.normal(0, 0.02, self.test_data.shape)
            current_data = self.test_data + noise
            current_data = np.clip(current_data, 0, 1)
            
            # 创建新的表面
            surface = GLSurfacePlotItem(
                z=current_data,
                color=(1, 1, 1, 0.3),
                shader='shaded',
                glOptions='additive'
            )
            
            # 添加到视图
            view.addItem(surface)
            
            end_time = time.time()
            render_time = (end_time - start_time) * 1000  # 毫秒
            times.append(render_time)
            
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_usage.append(current_memory - start_memory)
            
            self.log_message(f"  第{i+1}次渲染: {render_time:.2f}ms")
        
        # 计算统计结果
        avg_time = np.mean(times)
        max_time = np.max(times)
        min_time = np.min(times)
        avg_memory = np.mean(memory_usage)
        
        self.log_message(f"PyQtGraph结果:")
        self.log_message(f"  平均渲染时间: {avg_time:.2f}ms")
        self.log_message(f"  最大渲染时间: {max_time:.2f}ms")
        self.log_message(f"  最小渲染时间: {min_time:.2f}ms")
        self.log_message(f"  平均内存使用: {avg_memory:.2f}MB")
        
        return {
            'avg_time': avg_time,
            'max_time': max_time,
            'min_time': min_time,
            'avg_memory': avg_memory
        }
    
    def run_test(self):
        """运行性能测试"""
        self.log_message("=" * 50)
        self.log_message("开始3D可视化性能对比测试")
        self.log_message("=" * 50)
        
        # 测试Matplotlib
        mpl_results = self.test_matplotlib_performance()
        
        self.log_message("")
        
        # 测试PyQtGraph
        pg_results = self.test_pyqtgraph_performance()
        
        # 性能对比
        self.log_message("")
        self.log_message("=" * 50)
        self.log_message("性能对比结果:")
        self.log_message("=" * 50)
        
        # 渲染时间对比
        time_ratio = mpl_results['avg_time'] / pg_results['avg_time']
        self.log_message(f"渲染时间对比:")
        self.log_message(f"  Matplotlib平均: {mpl_results['avg_time']:.2f}ms")
        self.log_message(f"  PyQtGraph平均: {pg_results['avg_time']:.2f}ms")
        self.log_message(f"  性能比率: {time_ratio:.2f}")
        
        if time_ratio > 1.5:
            self.log_message("  🏆 PyQtGraph性能明显更优")
        elif time_ratio > 1.1:
            self.log_message("  ✅ PyQtGraph性能略优")
        else:
            self.log_message("  ⚖️ 两者性能相近")
        
        # 内存使用对比
        memory_ratio = mpl_results['avg_memory'] / pg_results['avg_memory']
        self.log_message(f"内存使用对比:")
        self.log_message(f"  Matplotlib平均: {mpl_results['avg_memory']:.2f}MB")
        self.log_message(f"  PyQtGraph平均: {pg_results['avg_memory']:.2f}MB")
        self.log_message(f"  内存比率: {memory_ratio:.2f}")
        
        # 理论FPS对比
        mpl_fps = 1000 / mpl_results['avg_time'] if mpl_results['avg_time'] > 0 else 0
        pg_fps = 1000 / pg_results['avg_time'] if pg_results['avg_time'] > 0 else 0
        
        self.log_message(f"理论最大FPS:")
        self.log_message(f"  Matplotlib: {mpl_fps:.1f} FPS")
        self.log_message(f"  PyQtGraph: {pg_fps:.1f} FPS")
        
        # 更新结果标签
        if time_ratio > 1.2:
            self.result_label.setText(f"PyQtGraph更快 ({time_ratio:.1f}x)")
        elif time_ratio < 0.8:
            self.result_label.setText(f"Matplotlib更快 ({1/time_ratio:.1f}x)")
        else:
            self.result_label.setText("两者性能相近")
        
        self.log_message("")
        self.log_message("测试完成!")
    
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
    print("🚀 启动快速3D性能对比测试...")
    
    # 创建测试应用
    app = QuickPerformanceTest()
    
    # 运行应用
    result = app.run()
    
    print("✅ 测试完成")
    return result

if __name__ == "__main__":
    main() 