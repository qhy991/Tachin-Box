#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爱心路径居中检查脚本
Test script for heart path centering check
"""

import sys
import os
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanner

def test_heart_centering():
    """检查爱心路径的居中情况"""
    print("❤️ 爱心路径居中检查")
    print("=" * 50)
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 获取爱心路径
    heart_path = planner.available_paths.get("❤️ 爱心")
    if not heart_path:
        print("❌ 未找到爱心路径")
        return
    
    print(f"✅ 找到路径: {heart_path.name}")
    print(f"📊 路径点数量: {len(heart_path.points)}")
    
    # 分析坐标范围
    x_coords = [point.x for point in heart_path.points]
    y_coords = [point.y for point in heart_path.points]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    
    print(f"\n📍 当前坐标范围分析:")
    print(f"   X范围: {min_x:.1f} - {max_x:.1f}")
    print(f"   Y范围: {min_y:.1f} - {max_y:.1f}")
    print(f"   当前中心点: ({center_x:.1f}, {center_y:.1f})")
    print(f"   游戏区域中心: (32, 32)")
    
    # 检查居中情况
    x_offset = abs(center_x - 32)
    y_offset = abs(center_y - 32)
    
    print(f"\n🎯 居中情况检查:")
    print(f"   X轴偏移: {x_offset:.1f}")
    print(f"   Y轴偏移: {y_offset:.1f}")
    
    if x_offset < 1 and y_offset < 1:
        print("   ✅ 完美居中！")
    elif x_offset < 2 and y_offset < 2:
        print("   ✅ 基本居中")
    else:
        print("   ⚠️ 需要居中调整")
    
    # 计算需要的偏移量
    dx = 32 - center_x
    dy = 32 - center_y
    
    print(f"\n🔧 需要的调整:")
    print(f"   X轴偏移量: {dx:.1f}")
    print(f"   Y轴偏移量: {dy:.1f}")
    
    # 显示所有路径点
    print(f"\n📋 当前路径点详情:")
    for i, point in enumerate(heart_path.points):
        print(f"   {i+1:2d}. ({point.x:5.1f}, {point.y:5.1f}) - {point.point_type:8s} - {point.connection_type}")
    
    print(f"\n🎉 检查完成！")

if __name__ == "__main__":
    test_heart_centering() 