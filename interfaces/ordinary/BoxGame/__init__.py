# -*- coding: utf-8 -*-
"""
BoxGame 模块初始化文件
推箱子游戏相关模块
"""

__version__ = "1.0.0"
__author__ = "BoxGame Team"

# 导出主要类
from .box_game_renderer import BoxGameRenderer
from .box_game_control_panel import BoxGameControlPanel
from .box_game_path_planning import PathPlanningGameEnhancer
from .path_visualization_manager import PathVisualizationManager

__all__ = [
    'BoxGameRenderer', 
    'BoxGameControlPanel',
    'PathPlanningGameEnhancer',
    'PathVisualizationManager'
] 