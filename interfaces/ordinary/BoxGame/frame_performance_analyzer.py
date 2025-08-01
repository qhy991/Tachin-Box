# -*- coding: utf-8 -*-
"""
帧级性能分析器模块
Frame Performance Analyzer Module

本模块提供详细的帧级性能分析功能，包括：
1. 数据运算时间测量
2. 渲染时间测量
3. 各阶段性能统计
4. 性能瓶颈识别
5. 实时性能监控
"""

import time
import numpy as np
from collections import deque, defaultdict
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import threading
import json
import os
from datetime import datetime

@dataclass
class FrameTiming:
    """单帧时间记录"""
    frame_id: int
    timestamp: float
    total_time: float = 0.0
    data_processing_time: float = 0.0
    analysis_time: float = 0.0
    rendering_time: float = 0.0
    pressure_update_time: float = 0.0
    game_update_time: float = 0.0
    display_update_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0

@dataclass
class PerformanceMetrics:
    """性能指标统计"""
    total_frames: int = 0
    avg_fps: float = 0.0
    avg_data_processing_time: float = 0.0
    avg_analysis_time: float = 0.0
    avg_rendering_time: float = 0.0
    avg_total_time: float = 0.0
    max_data_processing_time: float = 0.0
    max_analysis_time: float = 0.0
    max_rendering_time: float = 0.0
    max_total_time: float = 0.0
    min_data_processing_time: float = float('inf')
    min_analysis_time: float = float('inf')
    min_rendering_time: float = float('inf')
    min_total_time: float = float('inf')
    bottleneck_stage: str = "unknown"
    performance_score: float = 0.0

class FramePerformanceAnalyzer(QObject):
    """帧级性能分析器"""
    
    # 信号定义
    performance_updated = pyqtSignal(dict)  # 性能数据更新信号
    bottleneck_detected = pyqtSignal(str, float)  # 瓶颈检测信号
    performance_warning = pyqtSignal(str, float)  # 性能警告信号
    
    def __init__(self, max_history_size=1000):
        super().__init__()
        
        # 📊 性能数据存储
        self.frame_history = deque(maxlen=max_history_size)
        self.current_frame = None
        self.frame_counter = 0
        
        # ⏱️ 时间测量变量
        self.stage_timers = {}
        self.stage_start_times = {}
        
        # 📈 性能统计
        self.performance_metrics = PerformanceMetrics()
        self.real_time_metrics = {
            'current_fps': 0.0,
            'avg_fps_1s': 0.0,
            'avg_fps_5s': 0.0,
            'avg_fps_10s': 0.0
        }
        
        # 🎯 性能阈值设置
        self.performance_thresholds = {
            'target_fps': 30.0,
            'warning_fps': 20.0,
            'critical_fps': 10.0,
            'max_data_processing_time': 0.016,  # 16ms
            'max_analysis_time': 0.016,         # 16ms
            'max_rendering_time': 0.016,        # 16ms
            'max_total_time': 0.033             # 33ms (30 FPS)
        }
        
        # 🔍 瓶颈检测
        self.bottleneck_history = deque(maxlen=50)
        self.performance_warnings = deque(maxlen=20)
        
        # 📊 实时监控
        self.monitoring_enabled = True
        self.detailed_logging = False
        self.auto_save = True
        self.save_interval = 60  # 每60秒保存一次
        
        # 🗂️ 数据保存
        self.log_directory = "performance_logs"
        self.ensure_log_directory()
        
        # 🔄 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_real_time_metrics)
        self.update_timer.start(1000)  # 每秒更新一次
        
        print("✅ 帧级性能分析器已初始化")
    
    def ensure_log_directory(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
            print(f"📁 创建性能日志目录: {self.log_directory}")
    
    def start_frame(self, frame_id: Optional[int] = None):
        """开始新帧的性能测量"""
        if frame_id is None:
            frame_id = self.frame_counter
        
        self.frame_counter += 1
        self.current_frame = FrameTiming(
            frame_id=frame_id,
            timestamp=time.time()
        )
        
        # 记录系统资源使用情况
        try:
            import psutil
            process = psutil.Process()
            self.current_frame.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            self.current_frame.cpu_usage = process.cpu_percent()
        except ImportError:
            self.current_frame.memory_usage = 0.0
            self.current_frame.cpu_usage = 0.0
        
        # 重置阶段计时器
        self.stage_timers.clear()
        self.stage_start_times.clear()
        
        if self.detailed_logging:
            print(f"🎬 开始帧 {frame_id} 性能测量")
    
    def start_stage(self, stage_name: str):
        """开始特定阶段的计时"""
        self.stage_start_times[stage_name] = time.time()
        
        if self.detailed_logging:
            print(f"  ⏱️ 开始阶段: {stage_name}")
    
    def end_stage(self, stage_name: str):
        """结束特定阶段的计时"""
        if stage_name in self.stage_start_times:
            stage_time = time.time() - self.stage_start_times[stage_name]
            self.stage_timers[stage_name] = stage_time
            
            # 更新当前帧的对应时间
            if self.current_frame:
                if stage_name == 'data_processing':
                    self.current_frame.data_processing_time = stage_time
                elif stage_name == 'analysis':
                    self.current_frame.analysis_time = stage_time
                elif stage_name == 'rendering':
                    self.current_frame.rendering_time = stage_time
                elif stage_name == 'pressure_update':
                    self.current_frame.pressure_update_time = stage_time
                elif stage_name == 'game_update':
                    self.current_frame.game_update_time = stage_time
                elif stage_name == 'display_update':
                    self.current_frame.display_update_time = stage_time
            
            if self.detailed_logging:
                print(f"  ✅ 结束阶段: {stage_name} ({stage_time*1000:.2f}ms)")
    
    def end_frame(self):
        """结束当前帧的性能测量"""
        if self.current_frame:
            # 计算总时间
            self.current_frame.total_time = (
                self.current_frame.data_processing_time +
                self.current_frame.analysis_time +
                self.current_frame.rendering_time
            )
            
            # 添加到历史记录
            self.frame_history.append(self.current_frame)
            
            # 更新性能统计
            self.update_performance_metrics()
            
            # 检测性能瓶颈
            self.detect_bottlenecks()
            
            # 发送性能更新信号
            self.emit_performance_update()
            
            if self.detailed_logging:
                print(f"🎬 帧 {self.current_frame.frame_id} 完成: "
                      f"总时间={self.current_frame.total_time*1000:.2f}ms, "
                      f"FPS={1/self.current_frame.total_time:.1f}")
            
            # 清空当前帧
            self.current_frame = None
    
    def update_performance_metrics(self):
        """更新性能指标统计"""
        if len(self.frame_history) == 0:
            return
        
        # 计算基本统计
        total_frames = len(self.frame_history)
        total_times = [f.total_time for f in self.frame_history]
        data_times = [f.data_processing_time for f in self.frame_history]
        analysis_times = [f.analysis_time for f in self.frame_history]
        rendering_times = [f.rendering_time for f in self.frame_history]
        
        # 更新指标
        self.performance_metrics.total_frames = total_frames
        self.performance_metrics.avg_total_time = np.mean(total_times)
        self.performance_metrics.avg_data_processing_time = np.mean(data_times)
        self.performance_metrics.avg_analysis_time = np.mean(analysis_times)
        self.performance_metrics.avg_rendering_time = np.mean(rendering_times)
        self.performance_metrics.avg_fps = 1.0 / self.performance_metrics.avg_total_time if self.performance_metrics.avg_total_time > 0 else 0
        
        # 最大最小值
        self.performance_metrics.max_total_time = np.max(total_times)
        self.performance_metrics.max_data_processing_time = np.max(data_times)
        self.performance_metrics.max_analysis_time = np.max(analysis_times)
        self.performance_metrics.max_rendering_time = np.max(rendering_times)
        
        self.performance_metrics.min_total_time = np.min(total_times)
        self.performance_metrics.min_data_processing_time = np.min(data_times)
        self.performance_metrics.min_analysis_time = np.min(analysis_times)
        self.performance_metrics.min_rendering_time = np.min(rendering_times)
        
        # 识别瓶颈阶段
        avg_times = {
            'data_processing': self.performance_metrics.avg_data_processing_time,
            'analysis': self.performance_metrics.avg_analysis_time,
            'rendering': self.performance_metrics.avg_rendering_time
        }
        self.performance_metrics.bottleneck_stage = max(avg_times, key=avg_times.get)
        
        # 计算性能评分 (0-100)
        target_fps = self.performance_thresholds['target_fps']
        actual_fps = self.performance_metrics.avg_fps
        self.performance_metrics.performance_score = min(100, (actual_fps / target_fps) * 100)
    
    def detect_bottlenecks(self):
        """检测性能瓶颈"""
        if not self.current_frame:
            return
        
        # 检查各阶段时间是否超过阈值
        warnings = []
        
        if self.current_frame.data_processing_time > self.performance_thresholds['max_data_processing_time']:
            warnings.append(('data_processing', self.current_frame.data_processing_time))
        
        if self.current_frame.analysis_time > self.performance_thresholds['max_analysis_time']:
            warnings.append(('analysis', self.current_frame.analysis_time))
        
        if self.current_frame.rendering_time > self.performance_thresholds['max_rendering_time']:
            warnings.append(('rendering', self.current_frame.rendering_time))
        
        if self.current_frame.total_time > self.performance_thresholds['max_total_time']:
            warnings.append(('total', self.current_frame.total_time))
        
        # 发送警告信号
        for stage, time_value in warnings:
            self.performance_warnings.append({
                'frame_id': self.current_frame.frame_id,
                'stage': stage,
                'time': time_value,
                'timestamp': time.time()
            })
            self.performance_warning.emit(stage, time_value)
        
        # 检测瓶颈
        if warnings:
            bottleneck_stage = max(warnings, key=lambda x: x[1])[0]
            self.bottleneck_history.append({
                'frame_id': self.current_frame.frame_id,
                'stage': bottleneck_stage,
                'timestamp': time.time()
            })
            self.bottleneck_detected.emit(bottleneck_stage, self.current_frame.total_time)
    
    def update_real_time_metrics(self):
        """更新实时性能指标"""
        if len(self.frame_history) < 2:
            return
        
        # 计算不同时间窗口的FPS
        current_time = time.time()
        
        # 1秒窗口
        recent_1s = [f for f in self.frame_history if current_time - f.timestamp <= 1.0]
        if recent_1s:
            self.real_time_metrics['avg_fps_1s'] = len(recent_1s)
        
        # 5秒窗口
        recent_5s = [f for f in self.frame_history if current_time - f.timestamp <= 5.0]
        if recent_5s:
            self.real_time_metrics['avg_fps_5s'] = len(recent_5s) / 5.0
        
        # 10秒窗口
        recent_10s = [f for f in self.frame_history if current_time - f.timestamp <= 10.0]
        if recent_10s:
            self.real_time_metrics['avg_fps_10s'] = len(recent_10s) / 10.0
        
        # 当前FPS (基于最近几帧)
        if len(self.frame_history) >= 2:
            recent_frames = list(self.frame_history)[-5:]  # 最近5帧
            if len(recent_frames) >= 2:
                time_span = recent_frames[-1].timestamp - recent_frames[0].timestamp
                if time_span > 0:
                    self.real_time_metrics['current_fps'] = (len(recent_frames) - 1) / time_span
    
    def emit_performance_update(self):
        """发送性能更新信号"""
        if not self.current_frame:
            return
        
        performance_data = {
            'frame_id': self.current_frame.frame_id,
            'timestamp': self.current_frame.timestamp,
            'timing': {
                'total': self.current_frame.total_time,
                'data_processing': self.current_frame.data_processing_time,
                'analysis': self.current_frame.analysis_time,
                'rendering': self.current_frame.rendering_time,
                'pressure_update': self.current_frame.pressure_update_time,
                'game_update': self.current_frame.game_update_time,
                'display_update': self.current_frame.display_update_time
            },
            'metrics': {
                'current_fps': self.real_time_metrics['current_fps'],
                'avg_fps_1s': self.real_time_metrics['avg_fps_1s'],
                'avg_fps_5s': self.real_time_metrics['avg_fps_5s'],
                'avg_fps_10s': self.real_time_metrics['avg_fps_10s'],
                'performance_score': self.performance_metrics.performance_score
            },
            'system': {
                'memory_usage': self.current_frame.memory_usage,
                'cpu_usage': self.current_frame.cpu_usage
            },
            'bottleneck': self.performance_metrics.bottleneck_stage
        }
        
        self.performance_updated.emit(performance_data)
    
    def get_performance_summary(self) -> Dict:
        """获取性能总结报告"""
        return {
            'total_frames': self.performance_metrics.total_frames,
            'avg_fps': self.performance_metrics.avg_fps,
            'current_fps': self.real_time_metrics['current_fps'],
            'performance_score': self.performance_metrics.performance_score,
            'bottleneck_stage': self.performance_metrics.bottleneck_stage,
            'timing_breakdown': {
                'data_processing': {
                    'avg': self.performance_metrics.avg_data_processing_time,
                    'max': self.performance_metrics.max_data_processing_time,
                    'min': self.performance_metrics.min_data_processing_time
                },
                'analysis': {
                    'avg': self.performance_metrics.avg_analysis_time,
                    'max': self.performance_metrics.max_analysis_time,
                    'min': self.performance_metrics.min_analysis_time
                },
                'rendering': {
                    'avg': self.performance_metrics.avg_rendering_time,
                    'max': self.performance_metrics.max_rendering_time,
                    'min': self.performance_metrics.min_rendering_time
                },
                'total': {
                    'avg': self.performance_metrics.avg_total_time,
                    'max': self.performance_metrics.max_total_time,
                    'min': self.performance_metrics.min_total_time
                }
            },
            'recent_warnings': list(self.performance_warnings)[-5:],
            'bottleneck_history': list(self.bottleneck_history)[-10:]
        }
    
    def save_performance_log(self, filename: Optional[str] = None):
        """保存性能日志到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_log_{timestamp}.json"
        
        filepath = os.path.join(self.log_directory, filename)
        
        try:
            # 准备保存数据
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'performance_summary': self.get_performance_summary(),
                'frame_history': [
                    {
                        'frame_id': f.frame_id,
                        'timestamp': f.timestamp,
                        'total_time': f.total_time,
                        'data_processing_time': f.data_processing_time,
                        'analysis_time': f.analysis_time,
                        'rendering_time': f.rendering_time,
                        'pressure_update_time': f.pressure_update_time,
                        'game_update_time': f.game_update_time,
                        'display_update_time': f.display_update_time,
                        'memory_usage': f.memory_usage,
                        'cpu_usage': f.cpu_usage
                    }
                    for f in self.frame_history
                ],
                'performance_warnings': list(self.performance_warnings),
                'bottleneck_history': list(self.bottleneck_history)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"📊 性能日志已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ 保存性能日志失败: {e}")
            return None
    
    def load_performance_log(self, filepath: str) -> bool:
        """从文件加载性能日志"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            # 清空当前数据
            self.frame_history.clear()
            self.performance_warnings.clear()
            self.bottleneck_history.clear()
            
            # 加载帧历史
            for frame_data in log_data.get('frame_history', []):
                frame = FrameTiming(
                    frame_id=frame_data['frame_id'],
                    timestamp=frame_data['timestamp'],
                    total_time=frame_data['total_time'],
                    data_processing_time=frame_data['data_processing_time'],
                    analysis_time=frame_data['analysis_time'],
                    rendering_time=frame_data['rendering_time'],
                    pressure_update_time=frame_data['pressure_update_time'],
                    game_update_time=frame_data['game_update_time'],
                    display_update_time=frame_data['display_update_time'],
                    memory_usage=frame_data['memory_usage'],
                    cpu_usage=frame_data['cpu_usage']
                )
                self.frame_history.append(frame)
            
            # 更新性能指标
            self.update_performance_metrics()
            
            print(f"📊 性能日志已加载: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 加载性能日志失败: {e}")
            return False
    
    def clear_history(self):
        """清空性能历史数据"""
        self.frame_history.clear()
        self.performance_warnings.clear()
        self.bottleneck_history.clear()
        self.frame_counter = 0
        self.performance_metrics = PerformanceMetrics()
        print("🗑️ 性能历史数据已清空")
    
    def set_detailed_logging(self, enabled: bool):
        """设置详细日志输出"""
        self.detailed_logging = enabled
        print(f"📝 详细日志输出: {'启用' if enabled else '禁用'}")
    
    def set_performance_thresholds(self, thresholds: Dict):
        """设置性能阈值"""
        self.performance_thresholds.update(thresholds)
        print(f"🎯 性能阈值已更新: {thresholds}")
    
    def get_recent_frames(self, count: int = 10) -> List[FrameTiming]:
        """获取最近的帧数据"""
        return list(self.frame_history)[-count:]
    
    def get_stage_performance(self, stage_name: str) -> Dict:
        """获取特定阶段的性能统计"""
        if len(self.frame_history) == 0:
            return {}
        
        stage_times = []
        if stage_name == 'data_processing':
            stage_times = [f.data_processing_time for f in self.frame_history]
        elif stage_name == 'analysis':
            stage_times = [f.analysis_time for f in self.frame_history]
        elif stage_name == 'rendering':
            stage_times = [f.rendering_time for f in self.frame_history]
        elif stage_name == 'total':
            stage_times = [f.total_time for f in self.frame_history]
        else:
            return {}
        
        return {
            'avg': np.mean(stage_times),
            'max': np.max(stage_times),
            'min': np.min(stage_times),
            'std': np.std(stage_times),
            'count': len(stage_times)
        }

# 全局性能分析器实例
_global_analyzer = None

def get_global_analyzer() -> FramePerformanceAnalyzer:
    """获取全局性能分析器实例"""
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = FramePerformanceAnalyzer()
    return _global_analyzer

def start_frame_measurement(frame_id: Optional[int] = None):
    """开始帧测量（便捷函数）"""
    analyzer = get_global_analyzer()
    analyzer.start_frame(frame_id)

def end_frame_measurement():
    """结束帧测量（便捷函数）"""
    analyzer = get_global_analyzer()
    analyzer.end_frame()

def measure_stage(stage_name: str):
    """阶段测量装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            analyzer = get_global_analyzer()
            analyzer.start_stage(stage_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                analyzer.end_stage(stage_name)
        return wrapper
    return decorator

# 便捷的上下文管理器
class StageTimer:
    """阶段计时器上下文管理器"""
    
    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.analyzer = get_global_analyzer()
    
    def __enter__(self):
        self.analyzer.start_stage(self.stage_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.analyzer.end_stage(self.stage_name)

def stage_timer(stage_name: str):
    """阶段计时器工厂函数"""
    return StageTimer(stage_name) 