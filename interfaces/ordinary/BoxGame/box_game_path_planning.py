# -*- coding: utf-8 -*-
"""
推箱子游戏路线规划模块
Box Game Path Planning Module

为推箱子游戏添加路线设计、目标设置和路径导航功能
"""

import numpy as np
import time
from typing import List, Tuple, Optional, Dict
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Arrow
import matplotlib.patches as patches

class PathPoint:
    """路径点类"""
    
    def __init__(self, x: float, y: float, point_type: str = "waypoint", radius: float = 3.0, connection_type: str = "solid"):
        self.x = x
        self.y = y
        self.point_type = point_type  # "start", "waypoint", "target", "checkpoint"
        self.radius = radius
        self.reached = False
        self.reach_time = None
        self.connection_type = connection_type  # "solid", "dashed", "none"
        
    def distance_to(self, other_x: float, other_y: float) -> float:
        """计算到指定坐标的距离"""
        return np.sqrt((self.x - other_x)**2 + (self.y - other_y)**2)
    
    def is_near(self, x: float, y: float, tolerance: float = 5.0) -> bool:
        """判断是否接近该点"""
        return self.distance_to(x, y) <= tolerance
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'x': self.x,
            'y': self.y,
            'type': self.point_type,
            'radius': self.radius,
            'reached': self.reached,
            'reach_time': self.reach_time,
            'connection_type': self.connection_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """从字典创建路径点"""
        point = cls(data['x'], data['y'], data['type'], data.get('radius', 3.0), data.get('connection_type', 'solid'))
        point.reached = data.get('reached', False)
        point.reach_time = data.get('reach_time', None)
        return point


class GamePath:
    """游戏路径类"""
    
    def __init__(self, name: str = "默认路径"):
        self.name = name
        self.points: List[PathPoint] = []
        self.current_target_index = 0
        self.total_time = 0.0
        self.completion_times: List[float] = []
        self.is_completed = False
        self.start_time = None
        
    def add_point(self, x: float, y: float, point_type: str = "waypoint", connection_type: str = "solid") -> PathPoint:
        """添加路径点"""
        point = PathPoint(x, y, point_type, connection_type=connection_type)
        self.points.append(point)
        return point
    
    def get_current_target(self) -> Optional[PathPoint]:
        """获取当前目标点"""
        if 0 <= self.current_target_index < len(self.points):
            return self.points[self.current_target_index]
        return None
    
    def get_next_target(self) -> Optional[PathPoint]:
        """获取下一个目标点"""
        next_index = self.current_target_index + 1
        if next_index < len(self.points):
            return self.points[next_index]
        return None
    
    def check_target_reached(self, box_x: float, box_y: float, tolerance: float = 5.0) -> bool:
        """检查当前目标是否已达到"""
        current_target = self.get_current_target()
        if current_target and not current_target.reached:
            if current_target.is_near(box_x, box_y, tolerance):
                current_target.reached = True
                current_target.reach_time = time.time()
                
                # 记录完成时间
                if self.start_time:
                    elapsed_time = current_target.reach_time - self.start_time
                    self.completion_times.append(elapsed_time)
                
                # 移动到下一个目标
                self.current_target_index += 1
                
                # 检查是否完成整个路径
                if self.current_target_index >= len(self.points):
                    self.is_completed = True
                    self.total_time = time.time() - self.start_time if self.start_time else 0
                
                return True
        return False
    
    def reset_progress(self):
        """重置路径进度"""
        self.current_target_index = 0
        self.completion_times.clear()
        self.is_completed = False
        self.start_time = time.time()
        
        for point in self.points:
            point.reached = False
            point.reach_time = None
    
    def get_progress_info(self) -> Dict:
        """获取进度信息"""
        total_points = len(self.points)
        completed_points = sum(1 for p in self.points if p.reached)
        
        return {
            'total_points': total_points,
            'completed_points': completed_points,
            'current_target_index': self.current_target_index,
            'progress_percentage': (completed_points / total_points * 100) if total_points > 0 else 0,
            'is_completed': self.is_completed,
            'total_time': self.total_time,
            'completion_times': self.completion_times.copy()
        }
    
    def get_total_distance(self) -> float:
        """计算路径总距离"""
        if len(self.points) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(self.points) - 1):
            current = self.points[i]
            next_point = self.points[i + 1]
            total_distance += current.distance_to(next_point.x, next_point.y)
        
        return total_distance
    
    def to_dict(self) -> Dict:
        """转换为字典格式，用于保存"""
        return {
            'name': self.name,
            'points': [point.to_dict() for point in self.points],
            'current_target_index': self.current_target_index,
            'total_time': self.total_time,
            'completion_times': self.completion_times,
            'is_completed': self.is_completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """从字典加载路径"""
        path = cls(data['name'])
        path.points = [PathPoint.from_dict(point_data) for point_data in data['points']]
        path.current_target_index = data.get('current_target_index', 0)
        path.total_time = data.get('total_time', 0.0)
        path.completion_times = data.get('completion_times', [])
        path.is_completed = data.get('is_completed', False)
        return path


class PathPlanner:
    """路径规划器"""
    
    def __init__(self):
        self.available_paths: Dict[str, GamePath] = {}
        self.current_path: Optional[GamePath] = None
        self.setup_preset_paths()
    
    def setup_preset_paths(self):
        """设置预设路径"""
        
        # 🎯 简单直线路径
        simple_path = GamePath("简单直线")
        simple_path.add_point(20, 32, "start")
        simple_path.add_point(32, 32, "target")
        self.available_paths["简单直线"] = simple_path
        
        # 🔄 L型路径
        l_path = GamePath("L型路径")
        l_path.add_point(15, 15, "start")
        l_path.add_point(15, 32, "waypoint")
        l_path.add_point(32, 32, "target")
        self.available_paths["L型路径"] = l_path
        
        # 🌟 之字形路径
        zigzag_path = GamePath("之字形挑战")
        zigzag_path.add_point(10, 10, "start")
        zigzag_path.add_point(30, 15, "waypoint")
        zigzag_path.add_point(15, 25, "waypoint")
        zigzag_path.add_point(35, 30, "waypoint")
        zigzag_path.add_point(32, 32, "target")
        self.available_paths["之字形挑战"] = zigzag_path
        
        # 🎪 圆形路径
        circle_path = GamePath("圆形巡游")
        center_x, center_y = 32, 32
        radius = 15
        for i in range(8):
            angle = i * 2 * np.pi / 8
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            point_type = "start" if i == 0 else ("target" if i == 7 else "waypoint")
            circle_path.add_point(x, y, point_type)
        self.available_paths["圆形巡游"] = circle_path
        
        # 🏁 精确挑战路径
        precision_path = GamePath("精确挑战")
        precision_path.add_point(8, 8, "start")
        precision_path.add_point(16, 8, "checkpoint")
        precision_path.add_point(24, 16, "checkpoint")
        precision_path.add_point(32, 24, "checkpoint")
        precision_path.add_point(40, 32, "checkpoint")
        precision_path.add_point(48, 40, "checkpoint")
        precision_path.add_point(56, 48, "checkpoint")
        precision_path.add_point(32, 32, "target")
        self.available_paths["精确挑战"] = precision_path
        
        # 🤖 AI字母路径 - 优化版本，只连接关键点
        ai_path = GamePath("AI字母")
        # A字母 - 只连接关键点
        ai_path.add_point(15, 10, "start")  # A的左底部
        ai_path.add_point(20, 20, "waypoint")  # A的顶部
        ai_path.add_point(25, 10, "waypoint")  # A的右底部
        ai_path.add_point(20, 15, "waypoint")  # A的横线中点
        # I字母 - 只连接关键点
        ai_path.add_point(30, 10, "waypoint")  # I的底部
        ai_path.add_point(30, 20, "waypoint")  # I的顶部
        ai_path.add_point(30, 10, "target")  # 回到I的底部
        self.available_paths["AI字母"] = ai_path
        
        # 🎯 TACHIN字母路径 - 基于simple_test.py参考，简洁清晰的独立字母设计
        tachin_path = GamePath("TACHIN字母")
        
        # 基于simple_test.py的坐标设计，每个字母独立绘制
        # 字母宽度6单位，高度40单位，字母间距2单位，确保在64x64范围内
        
        # T字母 - 横线+竖线
        tachin_path.add_point(2, 12, "start", "solid")  # T的顶部左端
        tachin_path.add_point(8, 12, "waypoint", "solid")  # T的顶部右端
        tachin_path.add_point(5, 12, "waypoint", "solid")  # 回到中点
        tachin_path.add_point(5, 52, "waypoint", "solid")  # T的底部
        
        # 断开连接 - 不连接到A字母
        tachin_path.add_point(12, 52, "waypoint", "none")  # 断开点
        
        # A字母 - 两条斜线+横线
        tachin_path.add_point(12, 52, "waypoint", "solid")  # A的左底部
        tachin_path.add_point(15, 12, "waypoint", "solid")  # A的顶部
        tachin_path.add_point(18, 52, "waypoint", "solid")  # A的右底部
        tachin_path.add_point(16, 32, "waypoint", "solid")  # A的横线右端
        tachin_path.add_point(14, 32, "waypoint", "solid")  # A的横线左端
        
        # 断开连接 - 不连接到C字母
        tachin_path.add_point(24, 17, "waypoint", "none")  # 断开点
        
        # C字母 - 五点曲线
        tachin_path.add_point(24, 17, "waypoint", "solid")  # C的右端
        tachin_path.add_point(20, 12, "waypoint", "solid")  # C的顶部
        tachin_path.add_point(18, 32, "waypoint", "solid")  # C的左端
        tachin_path.add_point(20, 52, "waypoint", "solid")  # C的底部
        tachin_path.add_point(24, 47, "waypoint", "solid")  # C的右端底部
        
        # 断开连接 - 不连接到H字母
        tachin_path.add_point(30, 12, "waypoint", "none")  # 断开点
        
        # H字母 - 左竖线+横线+右竖线
        tachin_path.add_point(30, 12, "waypoint", "solid")  # H的左顶部
        tachin_path.add_point(30, 52, "waypoint", "solid")  # H的左底部
        tachin_path.add_point(30, 32, "waypoint", "solid")  # H的左中部
        tachin_path.add_point(36, 32, "waypoint", "solid")  # H的横线右端
        tachin_path.add_point(36, 12, "waypoint", "solid")  # H的右顶部
        tachin_path.add_point(36, 52, "waypoint", "solid")  # H的右底部
        
        # 断开连接 - 不连接到I字母
        tachin_path.add_point(42, 12, "waypoint", "none")  # 断开点
        
        # I字母 - 顶部横线+竖线+底部横线
        tachin_path.add_point(42, 12, "waypoint", "solid")  # I的顶部左端
        tachin_path.add_point(46, 12, "waypoint", "solid")  # I的顶部右端
        tachin_path.add_point(44, 12, "waypoint", "solid")  # I的顶部中点
        tachin_path.add_point(44, 52, "waypoint", "solid")  # I的底部中点
        tachin_path.add_point(42, 52, "waypoint", "solid")  # I的底部左端
        tachin_path.add_point(46, 52, "waypoint", "solid")  # I的底部右端
        
        # 断开连接 - 不连接到N字母
        tachin_path.add_point(52, 52, "waypoint", "none")  # 断开点
        
        # N字母 - 左竖线+对角线+右竖线
        tachin_path.add_point(52, 52, "waypoint", "solid")  # N的左底部
        tachin_path.add_point(52, 12, "waypoint", "solid")  # N的左顶部
        tachin_path.add_point(58, 52, "waypoint", "solid")  # N的对角线底部
        tachin_path.add_point(58, 12, "target", "solid")  # N的右顶部
        
        self.available_paths["TACHIN字母"] = tachin_path
        
        # 😊 笑脸表情路径 - 考虑Y轴向下，放大版本，去掉装饰点
        smile_path = GamePath("😊 笑脸")
        # 外圆 - 主要路径（实线），放大
        center_x, center_y = 32, 32
        radius = 16  # 增大半径
        # 只取8个关键点形成圆形
        for i in range(8):
            angle = i * 2 * np.pi / 8
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            point_type = "start" if i == 0 else ("waypoint" if i < 7 else "target")
            smile_path.add_point(x, y, point_type, "solid")
        
        # 左眼 - 简单的点（考虑Y轴向下）
        smile_path.add_point(24, 24, "waypoint", "none")
        
        # 右眼 - 简单的点（考虑Y轴向下）
        smile_path.add_point(40, 24, "waypoint", "none")
        
        # 嘴巴（弧形）- 简单的弧线（考虑Y轴向下，嘴巴向上）
        smile_path.add_point(24, 40, "waypoint", "solid")  # 左嘴角
        smile_path.add_point(32, 42, "waypoint", "solid")  # 嘴巴中点
        smile_path.add_point(40, 40, "waypoint", "solid")  # 右嘴角
        
        smile_path.add_point(32, 32, "target", "solid")  # 回到中心
        self.available_paths["😊 笑脸"] = smile_path
        
        # 😢 哭脸表情路径 - 考虑Y轴向下，放大版本，去掉装饰点
        cry_path = GamePath("😢 哭脸")
        # 外圆 - 主要路径（实线），放大
        for i in range(8):
            angle = i * 2 * np.pi / 8
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            point_type = "start" if i == 0 else ("waypoint" if i < 7 else "target")
            cry_path.add_point(x, y, point_type, "solid")
        
        # 左眼 - 简单的点（考虑Y轴向下）
        cry_path.add_point(24, 24, "waypoint", "none")
        
        # 右眼 - 简单的点（考虑Y轴向下）
        cry_path.add_point(40, 24, "waypoint", "none")
        
        # 眼泪（左）- 简单的线（考虑Y轴向下，眼泪向下）
        cry_path.add_point(24, 36, "waypoint", "solid")
        cry_path.add_point(24, 44, "waypoint", "solid")
        
        # 眼泪（右）- 简单的线（考虑Y轴向下，眼泪向下）
        cry_path.add_point(40, 36, "waypoint", "solid")
        cry_path.add_point(40, 44, "waypoint", "solid")
        
        # 嘴巴（倒弧形）- 简单的弧线（考虑Y轴向下，嘴巴向下）
        cry_path.add_point(24, 40, "waypoint", "solid")  # 左嘴角
        cry_path.add_point(32, 44, "waypoint", "solid")  # 嘴巴中点
        cry_path.add_point(40, 40, "waypoint", "solid")  # 右嘴角
        
        cry_path.add_point(32, 32, "target", "solid")  # 回到中心
        self.available_paths["😢 哭脸"] = cry_path
        
        # 😎 酷脸表情路径 - 考虑Y轴向下，放大版本，去掉装饰点
        cool_path = GamePath("😎 酷脸")
        # 外圆 - 主要路径（实线），放大
        for i in range(8):
            angle = i * 2 * np.pi / 8
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            point_type = "start" if i == 0 else ("waypoint" if i < 7 else "target")
            cool_path.add_point(x, y, point_type, "solid")
        
        # 左眼 - 简单的点（考虑Y轴向下）
        cool_path.add_point(24, 24, "waypoint", "none")
        
        # 右眼 - 简单的点（考虑Y轴向下）
        cool_path.add_point(40, 24, "waypoint", "none")
        
        # 墨镜（弧形）- 简单的线（考虑Y轴向下）
        cool_path.add_point(24, 28, "waypoint", "solid")  # 左墨镜
        cool_path.add_point(32, 30, "waypoint", "solid")  # 墨镜中点
        cool_path.add_point(40, 28, "waypoint", "solid")  # 右墨镜
        
        # 嘴巴（直线）- 简单的线（考虑Y轴向下）
        cool_path.add_point(24, 40, "waypoint", "solid")
        cool_path.add_point(40, 40, "waypoint", "solid")
        
        cool_path.add_point(32, 32, "target", "solid")  # 回到中心
        self.available_paths["😎 酷脸"] = cool_path
        
        # ❤️ 爱心路径 - 放大版本，去掉装饰点
        heart_path = GamePath("❤️ 爱心")
        # 爱心的数学公式：r = a(1-sin(θ)) - 主要路径（实线），放大
        a = 12  # 增大参数
        # 只取12个关键点形成爱心
        for i in range(12):
            angle = i * 2 * np.pi / 12
            r = a * (1 - np.sin(angle))
            x = center_x + r * np.cos(angle)
            y = center_y + r * np.sin(angle)
            point_type = "start" if i == 0 else ("target" if i == 11 else "waypoint")
            heart_path.add_point(x, y, point_type, "solid")
        
        # 爱心内部装饰点 - 去掉装饰点
        # heart_path.add_point(32, 28, "waypoint", "none")  # 中心装饰
        # heart_path.add_point(30, 30, "waypoint", "none")  # 左装饰
        # heart_path.add_point(34, 30, "waypoint", "none")  # 右装饰
        
        # 爱心外部装饰线 - 去掉装饰线
        # heart_path.add_point(28, 24, "waypoint", "dashed")  # 左上装饰
        # heart_path.add_point(36, 24, "waypoint", "dashed")  # 右上装饰
        self.available_paths["❤️ 爱心"] = heart_path
        
        # ⭐ 星星路径 - 放大版本，去掉装饰点
        star_path = GamePath("⭐ 星星")
        # 五角星的数学公式 - 主要路径（实线），放大
        for i in range(10):
            angle = i * 2 * np.pi / 10
            r = 16 if i % 2 == 0 else 8  # 交替使用外半径和内半径，增大
            x = center_x + r * np.cos(angle)
            y = center_y + r * np.sin(angle)
            point_type = "start" if i == 0 else ("target" if i == 9 else "waypoint")
            star_path.add_point(x, y, point_type, "solid")
        
        # 星星内部装饰点 - 去掉装饰点
        # star_path.add_point(32, 32, "waypoint", "none")  # 中心点
        # star_path.add_point(32, 28, "waypoint", "none")  # 下装饰
        # star_path.add_point(32, 36, "waypoint", "none")  # 上装饰
        # star_path.add_point(28, 32, "waypoint", "none")  # 左装饰
        # star_path.add_point(36, 32, "waypoint", "none")  # 右装饰
        
        star_path.add_point(center_x, center_y, "target", "solid")  # 回到中心
        self.available_paths["⭐ 星星"] = star_path
        
        print(f"📍 已加载 {len(self.available_paths)} 条预设路径")
    
    def set_current_path(self, path_name: str) -> bool:
        """设置当前路径"""
        if path_name in self.available_paths:
            self.current_path = self.available_paths[path_name]
            self.current_path.reset_progress()
            print(f"🎯 当前路径设置为: {path_name}")
            return True
        return False
    
    def get_current_path(self) -> Optional[GamePath]:
        """获取当前路径"""
        return self.current_path
    
    def create_custom_path(self, name: str, points: List[Tuple[float, float]]) -> GamePath:
        """创建自定义路径"""
        custom_path = GamePath(name)
        
        for i, (x, y) in enumerate(points):
            if i == 0:
                point_type = "start"
            elif i == len(points) - 1:
                point_type = "target"
            else:
                point_type = "waypoint"
            
            custom_path.add_point(x, y, point_type)
        
        self.available_paths[name] = custom_path
        print(f"🎨 创建自定义路径: {name} ({len(points)} 个点)")
        return custom_path
    
    def get_path_names(self) -> List[str]:
        """获取所有路径名称"""
        return list(self.available_paths.keys())
    
    def get_navigation_info(self, box_position: np.ndarray) -> Dict:
        """获取导航信息"""
        if not self.current_path:
            return {
                'has_path': False,
                'path_points': [],
                'current_target': None,
                'next_target': None,
                'target_distance': 0.0,
                'target_direction': 0.0,
                'direction_vector': (0.0, 0.0),
                'progress': {}
            }
        
        current_target = self.current_path.get_current_target()
        next_target = self.current_path.get_next_target()
        
        info = {
            'has_path': True,
            'path_name': self.current_path.name,
            'current_target': current_target.to_dict() if current_target else None,
            'next_target': next_target.to_dict() if next_target else None,
            'progress': self.current_path.get_progress_info(),
            'total_distance': self.current_path.get_total_distance(),
            'path_points': [p.to_dict() for p in self.current_path.points]
        }
        
        # 计算到当前目标的距离和方向
        if current_target:
            dx = current_target.x - box_position[0]
            dy = current_target.y - box_position[1]
            distance = np.sqrt(dx*dx + dy*dy)
            angle = np.degrees(np.arctan2(dy, dx)) % 360
            
            info['target_distance'] = distance
            info['target_direction'] = angle
            info['direction_vector'] = (dx, dy)
        
        return info


class PathPlanningGameEnhancer(QObject):
    """路径规划游戏增强器"""
    
    # 信号定义
    path_progress_updated = pyqtSignal(dict)
    target_reached = pyqtSignal(dict)
    path_completed = pyqtSignal(dict)
    navigation_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.path_planner = PathPlanner()
        self.is_path_mode_enabled = False
        self.last_box_position = np.array([32.0, 32.0])
        self.navigation_history = deque(maxlen=50)
        
        # 路径完成统计
        self.completion_stats = {
            'paths_completed': 0,
            'total_time': 0.0,
            'best_times': {},
            'average_times': {}
        }
        
        print("🗺️ 路径规划游戏增强器初始化完成")
    
    def enable_path_mode(self, path_name: str) -> bool:
        """启用路径模式"""
        if self.path_planner.set_current_path(path_name):
            self.is_path_mode_enabled = True
            self.emit_navigation_update()
            print(f"🎯 路径模式已启用: {path_name}")
            return True
        return False
    
    def disable_path_mode(self):
        """禁用路径模式"""
        self.is_path_mode_enabled = False
        self.path_planner.current_path = None
        
        # 🗑️ 发送空的导航信息来清除渲染器中的路径显示
        empty_nav_info = {
            'has_navigation': False,
            'is_enabled': False,
            'path_points': [],
            'current_target': None,
            'next_target': None,
            'target_distance': 0.0,
            'direction_angle': 0.0,
            'progress': {}
        }
        self.navigation_updated.emit(empty_nav_info)
        
        print("🛑 路径模式已禁用")
    
    def update_box_position(self, box_position: np.ndarray):
        """更新箱子位置，检查路径进度"""
        self.last_box_position = box_position.copy()
        
        if not self.is_path_mode_enabled or not self.path_planner.current_path:
            return None
        
        current_path = self.path_planner.current_path
        
        # 检查是否到达当前目标
        if current_path.check_target_reached(box_position[0], box_position[1]):
            target_info = {
                'target_index': current_path.current_target_index - 1,
                'path_name': current_path.name,
                'completion_time': current_path.completion_times[-1] if current_path.completion_times else 0
            }
            
            self.target_reached.emit(target_info)
            
            # 检查是否完成整个路径
            if current_path.is_completed:
                completion_info = {
                    'path_name': current_path.name,
                    'total_time': current_path.total_time,
                    'completion_times': current_path.completion_times,
                    'total_points': len(current_path.points)
                }
                
                self.update_completion_stats(current_path)
                self.path_completed.emit(completion_info)
                print(f"🎉 路径完成: {current_path.name} (用时: {current_path.total_time:.2f}秒)")
        
        # 更新导航信息
        self.emit_navigation_update()
        
        # 发送进度更新
        progress_info = current_path.get_progress_info()
        self.path_progress_updated.emit(progress_info)
        
        # 🗺️ 路径模式只提供导航信息，不返回目标位置
        # 箱子移动由用户手指控制决定
        return None
    
    def get_current_target_position(self) -> np.ndarray:
        """获取当前目标位置"""
        if not self.is_path_mode_enabled or not self.path_planner.current_path:
            return None
        
        current_path = self.path_planner.current_path
        if current_path.is_completed:
            return None
        
        current_target = current_path.get_current_target()
        if current_target:
            return np.array([current_target.x, current_target.y])
        
        return None
    
    def emit_navigation_update(self):
        """发送导航更新信号"""
        nav_info = self.path_planner.get_navigation_info(self.last_box_position)
        nav_info['is_enabled'] = self.is_path_mode_enabled
        nav_info['has_navigation'] = self.is_path_mode_enabled and nav_info.get('has_path', False)
        self.navigation_updated.emit(nav_info)
    
    def update_completion_stats(self, completed_path: GamePath):
        """更新完成统计"""
        self.completion_stats['paths_completed'] += 1
        self.completion_stats['total_time'] += completed_path.total_time
        
        path_name = completed_path.name
        
        # 更新最佳时间
        if path_name not in self.completion_stats['best_times'] or \
           completed_path.total_time < self.completion_stats['best_times'][path_name]:
            self.completion_stats['best_times'][path_name] = completed_path.total_time
        
        # 更新平均时间
        if path_name not in self.completion_stats['average_times']:
            self.completion_stats['average_times'][path_name] = []
        
        self.completion_stats['average_times'][path_name].append(completed_path.total_time)
    
    def get_available_paths(self) -> List[str]:
        """获取可用路径列表"""
        return self.path_planner.get_path_names()
    
    def create_custom_path(self, name: str, points: List[Tuple[float, float]]) -> bool:
        """创建自定义路径"""
        try:
            self.path_planner.create_custom_path(name, points)
            return True
        except Exception as e:
            print(f"❌ 创建自定义路径失败: {e}")
            return False
    
    def get_current_navigation_info(self) -> Dict:
        """获取当前导航信息"""
        nav_info = self.path_planner.get_navigation_info(self.last_box_position)
        nav_info['is_enabled'] = self.is_path_mode_enabled
        nav_info['has_navigation'] = self.is_path_mode_enabled and nav_info.get('has_path', False)
        nav_info['completion_stats'] = self.completion_stats.copy()
        return nav_info
    
    def reset_current_path(self):
        """重置当前路径进度"""
        if self.path_planner.current_path:
            self.path_planner.current_path.reset_progress()
            self.emit_navigation_update()
            print(f"🔄 路径进度已重置: {self.path_planner.current_path.name}")
    
    def get_completion_stats(self) -> Dict:
        """获取完成统计"""
        stats = self.completion_stats.copy()
        
        # 计算平均时间
        for path_name, times in self.completion_stats['average_times'].items():
            if times:
                stats['average_times'][path_name] = sum(times) / len(times)
        
        return stats 