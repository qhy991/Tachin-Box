#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新添加的字母和表情路径
Test script for new letter and emoji paths
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanner
import numpy as np

def test_new_paths():
    """测试新添加的路径"""
    print("🎯 测试新添加的字母和表情路径")
    print("=" * 50)
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 获取所有可用路径
    available_paths = planner.get_path_names()
    print(f"📋 可用路径数量: {len(available_paths)}")
    print("📋 所有路径:")
    for i, path_name in enumerate(available_paths, 1):
        print(f"  {i:2d}. {path_name}")
    
    # 测试字母路径
    print("\n🤖 测试字母路径:")
    letter_paths = ["AI字母", "TACHIN字母"]
    for path_name in letter_paths:
        if path_name in available_paths:
            planner.set_current_path(path_name)
            path = planner.get_current_path()
            print(f"  ✅ {path_name}: {len(path.points)} 个点")
            print(f"     起点: ({path.points[0].x:.1f}, {path.points[0].y:.1f})")
            print(f"     终点: ({path.points[-1].x:.1f}, {path.points[-1].y:.1f})")
        else:
            print(f"  ❌ {path_name}: 未找到")
    
    # 测试表情路径
    print("\n😊 测试表情路径:")
    emoji_paths = ["😊 笑脸", "😢 哭脸", "😎 酷脸", "❤️ 爱心", "⭐ 星星"]
    for path_name in emoji_paths:
        if path_name in available_paths:
            planner.set_current_path(path_name)
            path = planner.get_current_path()
            print(f"  ✅ {path_name}: {len(path.points)} 个点")
            print(f"     起点: ({path.points[0].x:.1f}, {path.points[0].y:.1f})")
            print(f"     终点: ({path.points[-1].x:.1f}, {path.points[-1].y:.1f})")
        else:
            print(f"  ❌ {path_name}: 未找到")
    
    # 测试路径导航
    print("\n🧭 测试路径导航:")
    test_path = "AI字母"
    if test_path in available_paths:
        planner.set_current_path(test_path)
        path = planner.get_current_path()
        
        # 模拟箱子位置
        box_position = np.array([15.0, 10.0])  # 起点位置
        
        # 获取导航信息
        nav_info = planner.get_navigation_info(box_position)
        print(f"  📍 当前路径: {test_path}")
        print(f"  🎯 当前目标: {nav_info.get('current_target', 'None')}")
        print(f"  📏 目标距离: {nav_info.get('target_distance', 0):.2f}")
        print(f"  🧭 方向角度: {nav_info.get('direction_angle', 0):.1f}°")
        print(f"  📊 进度: {nav_info.get('progress', {}).get('percentage', 0):.1f}%")
    
    print("\n✅ 路径测试完成!")

if __name__ == "__main__":
    test_new_paths() 