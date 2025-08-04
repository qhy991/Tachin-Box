#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试颜色支持功能
Test Color Support Functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanner, GamePath

def test_color_support():
    """测试颜色支持功能"""
    print("🎨 测试颜色支持功能")
    print("=" * 50)
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 测试笑脸路径的颜色
    print("\n😊 测试笑脸路径颜色:")
    smile_path = planner.available_paths.get("😊 笑脸")
    if smile_path:
        print(f"路径名称: {smile_path.name}")
        print(f"总点数: {len(smile_path.points)}")
        
        # 检查前几个点的颜色
        for i, point in enumerate(smile_path.points[:5]):
            print(f"点{i}: ({point.x}, {point.y}) - 点颜色: {point.point_color}, 线颜色: {point.line_color}")
    
    # 测试TACHIN字母路径的颜色
    print("\n🎯 测试TACHIN字母路径颜色:")
    tachin_path = planner.available_paths.get("TACHIN字母")
    if tachin_path:
        print(f"路径名称: {tachin_path.name}")
        print(f"总点数: {len(tachin_path.points)}")
        
        # 检查前几个点的颜色
        for i, point in enumerate(tachin_path.points[:10]):
            print(f"点{i}: ({point.x}, {point.y}) - 点颜色: {point.point_color}, 线颜色: {point.line_color}")
    
    # 测试爱心路径的颜色
    print("\n❤️ 测试爱心路径颜色:")
    heart_path = planner.available_paths.get("❤️ 爱心")
    if heart_path:
        print(f"路径名称: {heart_path.name}")
        print(f"总点数: {len(heart_path.points)}")
        
        # 检查前几个点的颜色
        for i, point in enumerate(heart_path.points[:5]):
            print(f"点{i}: ({point.x}, {point.y}) - 点颜色: {point.point_color}, 线颜色: {point.line_color}")
    
    # 测试星星路径的颜色
    print("\n⭐ 测试星星路径颜色:")
    star_path = planner.available_paths.get("⭐ 星星")
    if star_path:
        print(f"路径名称: {star_path.name}")
        print(f"总点数: {len(star_path.points)}")
        
        # 检查前几个点的颜色
        for i, point in enumerate(star_path.points[:5]):
            print(f"点{i}: ({point.x}, {point.y}) - 点颜色: {point.point_color}, 线颜色: {point.line_color}")
    
    print("\n✅ 颜色支持测试完成!")

def test_color_conversion():
    """测试颜色转换功能"""
    print("\n🎨 测试颜色转换功能")
    print("=" * 50)
    
    # 颜色映射字典（与渲染器中的一致）
    color_map = {
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'green': (0, 255, 0),
        'yellow': (255, 255, 0),
        'purple': (128, 0, 128),
        'orange': (255, 165, 0),
        'brown': (139, 69, 19),
        'gold': (255, 215, 0),
        'darkblue': (0, 0, 139),
        'black': (0, 0, 0),
        'gray': (128, 128, 128),
        'default': (0, 255, 255)  # cyan
    }
    
    # 测试颜色转换
    test_colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'brown', 'gold', 'darkblue', 'black', 'gray']
    
    for color_name in test_colors:
        if color_name in color_map:
            rgb = color_map[color_name]
            print(f"{color_name:10} -> RGB{rgb}")
        else:
            print(f"{color_name:10} -> 未找到")
    
    print("\n✅ 颜色转换测试完成!")

if __name__ == "__main__":
    test_color_support()
    test_color_conversion() 