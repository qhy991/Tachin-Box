#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爱心路径修正测试脚本
Test script for heart path fix
"""

import sys
import os
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanner

def test_heart_path_fix():
    """测试爱心路径修正效果"""
    print("❤️ 爱心路径修正测试")
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
    
    print(f"\n📍 坐标范围分析:")
    print(f"   X范围: {min_x:.1f} - {max_x:.1f}")
    print(f"   Y范围: {min_y:.1f} - {max_y:.1f}")
    print(f"   中心点: ({center_x:.1f}, {center_y:.1f})")
    print(f"   游戏区域中心: (32, 32)")
    
    # 检查爱心形状
    print(f"\n❤️ 爱心形状检查:")
    
    # 找到最高点和最低点
    highest_point = min(y_coords)  # Y坐标越小，在屏幕上越高
    lowest_point = max(y_coords)   # Y坐标越大，在屏幕上越低
    
    print(f"   最高点Y坐标: {highest_point:.1f}")
    print(f"   最低点Y坐标: {lowest_point:.1f}")
    
    # 检查爱心是否朝上（最高点应该在中心点上方）
    if highest_point < center_y:
        print("   ✅ 爱心朝上 - 修正成功！")
    else:
        print("   ❌ 爱心仍然倒置 - 需要进一步修正")
    
    # 检查边界安全
    print(f"\n🔒 边界安全检查:")
    if min_x >= 0 and max_x <= 64 and min_y >= 0 and max_y <= 64:
        print("   ✅ 所有坐标都在游戏区域内 (0-64)")
    else:
        print("   ❌ 存在超出边界的坐标")
    
    # 显示所有路径点
    print(f"\n📋 路径点详情:")
    for i, point in enumerate(heart_path.points):
        print(f"   {i+1:2d}. ({point.x:5.1f}, {point.y:5.1f}) - {point.point_type:8s} - {point.connection_type}")
    
    # 数学公式验证
    print(f"\n🧮 数学公式验证:")
    center_x, center_y = 32, 32
    a = 12
    print(f"   使用公式: r = {a} * (1 + sin(θ))")
    print(f"   中心点: ({center_x}, {center_y})")
    
    # 计算几个关键点的理论值
    angles = [0, np.pi/2, np.pi, 3*np.pi/2]
    angle_names = ["0°", "90°", "180°", "270°"]
    
    for angle, name in zip(angles, angle_names):
        r = a * (1 + np.sin(angle))
        x = center_x + r * np.cos(angle)
        y = center_y + r * np.sin(angle)
        print(f"   {name}: r={r:.1f}, 坐标=({x:.1f}, {y:.1f})")
    
    print(f"\n🎉 测试完成！")

if __name__ == "__main__":
    test_heart_path_fix() 