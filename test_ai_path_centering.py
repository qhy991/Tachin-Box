#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI路径居中效果测试脚本
Test script for AI path centering effect
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanner

def test_ai_path_centering():
    """测试AI路径居中效果"""
    print("🤖 AI路径居中效果测试")
    print("=" * 50)
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 获取AI智能路径
    ai_path = planner.available_paths.get("AI智能路径")
    if not ai_path:
        print("❌ 未找到AI智能路径")
        return
    
    print(f"✅ 找到路径: {ai_path.name}")
    print(f"📊 路径点数量: {len(ai_path.points)}")
    
    # 分析坐标范围
    x_coords = [point.x for point in ai_path.points]
    y_coords = [point.y for point in ai_path.points]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    
    print(f"\n📍 坐标范围分析:")
    print(f"   X范围: {min_x} - {max_x}")
    print(f"   Y范围: {min_y} - {max_y}")
    print(f"   中心点: ({center_x:.1f}, {center_y:.1f})")
    print(f"   游戏区域中心: (32, 32)")
    
    # 检查是否居中
    x_offset = abs(center_x - 32)
    y_offset = abs(center_y - 32)
    
    print(f"\n🎯 居中效果检查:")
    print(f"   X轴偏移: {x_offset:.1f}")
    print(f"   Y轴偏移: {y_offset:.1f}")
    
    if x_offset < 1 and y_offset < 1:
        print("   ✅ 完美居中！")
    elif x_offset < 2 and y_offset < 2:
        print("   ✅ 基本居中")
    else:
        print("   ⚠️ 需要进一步调整")
    
    # 检查边界安全
    print(f"\n🔒 边界安全检查:")
    if min_x >= 0 and max_x <= 64 and min_y >= 0 and max_y <= 64:
        print("   ✅ 所有坐标都在游戏区域内 (0-64)")
    else:
        print("   ❌ 存在超出边界的坐标")
    
    # 显示所有路径点
    print(f"\n📋 路径点详情:")
    for i, point in enumerate(ai_path.points):
        print(f"   {i+1:2d}. ({point.x:2.0f}, {point.y:2.0f}) - {point.point_type:8s} - {point.connection_type}")
    
    print(f"\n🎉 测试完成！")

if __name__ == "__main__":
    test_ai_path_centering() 