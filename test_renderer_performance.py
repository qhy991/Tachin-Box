# -*- coding: utf-8 -*-
"""
渲染器性能测试脚本
Renderer Performance Test Script

用于比较原版渲染器和优化渲染器的性能差异
"""

import sys
import os
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer

# 添加路径
sys.path.append(os.path.dirname(__file__))

def generate_test_pressure_data():
    """生成测试压力数据"""
    # 创建一个64x64的测试数据
    data = np.zeros((64, 64))
    
    # 添加一些模拟的压力点
    center_x, center_y = 32, 32
    for i in range(64):
        for j in range(64):
            distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
            if distance < 15:
                data[i, j] = 0.005 * np.exp(-distance / 5)
    
    # 添加一些噪声
    noise = np.random.normal(0, 0.0001, (64, 64))
    data += noise
    
    return data

def test_original_renderer():
    """测试原版渲染器性能"""
    print("🧪 开始测试原版渲染器...")
    
    try:
        from interfaces.ordinary.BoxGame.box_game_renderer import BoxGameRenderer
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建渲染器
        renderer = BoxGameRenderer()
        renderer.show()
        
        # 生成测试数据
        test_data = generate_test_pressure_data()
        
        # 测试参数
        test_frames = 100
        frame_times = []
        
        print(f"📊 测试 {test_frames} 帧...")
        
        # 开始测试
        start_time = time.time()
        
        for i in range(test_frames):
            frame_start = time.time()
            
            # 更新压力数据
            renderer.update_pressure_data(test_data)
            
            # 更新游戏状态
            state_info = {
                'is_contact': True,
                'is_sliding': False,
                'current_cop': (32.0, 32.0),
                'initial_cop': (30.0, 30.0),
                'movement_distance': 2.0,
                'box_position': np.array([32.0, 32.0]),
                'box_target_position': np.array([35.0, 35.0]),
                'consensus_angle': 45.0,
                'consensus_confidence': 0.8
            }
            renderer.update_game_state(state_info)
            
            # 强制更新显示
            renderer.update_display()
            
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)
            
            if i % 20 == 0:
                print(f"  帧 {i}: {frame_time*1000:.1f}ms")
        
        total_time = time.time() - start_time
        
        # 计算统计信息
        avg_frame_time = np.mean(frame_times)
        min_frame_time = np.min(frame_times)
        max_frame_time = np.max(frame_times)
        avg_fps = 1.0 / avg_frame_time
        
        print(f"✅ 原版渲染器测试完成:")
        print(f"   总时间: {total_time:.2f}s")
        print(f"   平均帧时间: {avg_frame_time*1000:.1f}ms")
        print(f"   平均FPS: {avg_fps:.1f}")
        print(f"   最小帧时间: {min_frame_time*1000:.1f}ms")
        print(f"   最大帧时间: {max_frame_time*1000:.1f}ms")
        
        # 清理
        renderer.close()
        
        return {
            'total_time': total_time,
            'avg_frame_time': avg_frame_time,
            'avg_fps': avg_fps,
            'min_frame_time': min_frame_time,
            'max_frame_time': max_frame_time
        }
        
    except Exception as e:
        print(f"❌ 原版渲染器测试失败: {e}")
        return None

def test_optimized_renderer():
    """测试优化渲染器性能"""
    print("🧪 开始测试优化渲染器...")
    
    try:
        from interfaces.ordinary.BoxGame.box_game_renderer_optimized import BoxGameRendererOptimized
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建渲染器
        renderer = BoxGameRendererOptimized()
        renderer.show()
        
        # 生成测试数据
        test_data = generate_test_pressure_data()
        
        # 测试参数
        test_frames = 100
        frame_times = []
        
        print(f"📊 测试 {test_frames} 帧...")
        
        # 开始测试
        start_time = time.time()
        
        for i in range(test_frames):
            frame_start = time.time()
            
            # 更新压力数据
            renderer.update_pressure_data(test_data)
            
            # 更新游戏状态
            state_info = {
                'is_contact': True,
                'is_sliding': False,
                'current_cop': (32.0, 32.0),
                'initial_cop': (30.0, 30.0),
                'movement_distance': 2.0,
                'box_position': np.array([32.0, 32.0]),
                'box_target_position': np.array([35.0, 35.0]),
                'consensus_angle': 45.0,
                'consensus_confidence': 0.8
            }
            renderer.update_game_state(state_info)
            
            # 强制更新显示
            renderer.game_renderer.update_display()
            
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)
            
            if i % 20 == 0:
                print(f"  帧 {i}: {frame_time*1000:.1f}ms")
        
        total_time = time.time() - start_time
        
        # 计算统计信息
        avg_frame_time = np.mean(frame_times)
        min_frame_time = np.min(frame_times)
        max_frame_time = np.max(frame_times)
        avg_fps = 1.0 / avg_frame_time
        
        print(f"✅ 优化渲染器测试完成:")
        print(f"   总时间: {total_time:.2f}s")
        print(f"   平均帧时间: {avg_frame_time*1000:.1f}ms")
        print(f"   平均FPS: {avg_fps:.1f}")
        print(f"   最小帧时间: {min_frame_time*1000:.1f}ms")
        print(f"   最大帧时间: {max_frame_time*1000:.1f}ms")
        
        # 清理
        renderer.close()
        
        return {
            'total_time': total_time,
            'avg_frame_time': avg_frame_time,
            'avg_fps': avg_fps,
            'min_frame_time': min_frame_time,
            'max_frame_time': max_frame_time
        }
        
    except Exception as e:
        print(f"❌ 优化渲染器测试失败: {e}")
        return None

class PerformanceTestWindow(QMainWindow):
    """性能测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("渲染器性能测试")
        self.setGeometry(100, 100, 600, 400)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建按钮
        self.test_original_btn = QPushButton("测试原版渲染器")
        self.test_original_btn.clicked.connect(self.run_original_test)
        layout.addWidget(self.test_original_btn)
        
        self.test_optimized_btn = QPushButton("测试优化渲染器")
        self.test_optimized_btn.clicked.connect(self.run_optimized_test)
        layout.addWidget(self.test_optimized_btn)
        
        self.compare_btn = QPushButton("比较性能")
        self.compare_btn.clicked.connect(self.compare_performance)
        layout.addWidget(self.compare_btn)
        
        # 创建结果显示标签
        self.result_label = QLabel("点击按钮开始测试...")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
        
        # 存储测试结果
        self.original_results = None
        self.optimized_results = None
    
    def run_original_test(self):
        """运行原版渲染器测试"""
        self.test_original_btn.setEnabled(False)
        self.result_label.setText("正在测试原版渲染器...")
        
        # 使用定时器延迟执行，避免阻塞UI
        QTimer.singleShot(100, self._run_original_test)
    
    def _run_original_test(self):
        """实际运行原版测试"""
        try:
            self.original_results = test_original_renderer()
            if self.original_results:
                self.result_label.setText(f"原版渲染器测试完成:\n"
                                        f"平均FPS: {self.original_results['avg_fps']:.1f}\n"
                                        f"平均帧时间: {self.original_results['avg_frame_time']*1000:.1f}ms")
            else:
                self.result_label.setText("原版渲染器测试失败")
        except Exception as e:
            self.result_label.setText(f"原版渲染器测试出错: {str(e)}")
        finally:
            self.test_original_btn.setEnabled(True)
    
    def run_optimized_test(self):
        """运行优化渲染器测试"""
        self.test_optimized_btn.setEnabled(False)
        self.result_label.setText("正在测试优化渲染器...")
        
        # 使用定时器延迟执行，避免阻塞UI
        QTimer.singleShot(100, self._run_optimized_test)
    
    def _run_optimized_test(self):
        """实际运行优化测试"""
        try:
            self.optimized_results = test_optimized_renderer()
            if self.optimized_results:
                self.result_label.setText(f"优化渲染器测试完成:\n"
                                        f"平均FPS: {self.optimized_results['avg_fps']:.1f}\n"
                                        f"平均帧时间: {self.optimized_results['avg_frame_time']*1000:.1f}ms")
            else:
                self.result_label.setText("优化渲染器测试失败")
        except Exception as e:
            self.result_label.setText(f"优化渲染器测试出错: {str(e)}")
        finally:
            self.test_optimized_btn.setEnabled(True)
    
    def compare_performance(self):
        """比较性能"""
        if not self.original_results or not self.optimized_results:
            self.result_label.setText("请先运行两个测试")
            return
        
        # 计算性能提升
        fps_improvement = (self.optimized_results['avg_fps'] - self.original_results['avg_fps']) / self.original_results['avg_fps'] * 100
        time_improvement = (self.original_results['avg_frame_time'] - self.optimized_results['avg_frame_time']) / self.original_results['avg_frame_time'] * 100
        
        comparison_text = f"性能比较结果:\n\n"
        comparison_text += f"原版渲染器:\n"
        comparison_text += f"  平均FPS: {self.original_results['avg_fps']:.1f}\n"
        comparison_text += f"  平均帧时间: {self.original_results['avg_frame_time']*1000:.1f}ms\n\n"
        comparison_text += f"优化渲染器:\n"
        comparison_text += f"  平均FPS: {self.optimized_results['avg_fps']:.1f}\n"
        comparison_text += f"  平均帧时间: {self.optimized_results['avg_frame_time']*1000:.1f}ms\n\n"
        comparison_text += f"性能提升:\n"
        comparison_text += f"  FPS提升: {fps_improvement:+.1f}%\n"
        comparison_text += f"  帧时间减少: {time_improvement:+.1f}%"
        
        self.result_label.setText(comparison_text)

def main():
    """主函数"""
    print("🧪 渲染器性能测试工具")
    print("=" * 30)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = PerformanceTestWindow()
    window.show()
    
    print("💡 提示：在窗口中点击按钮进行性能测试")
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 