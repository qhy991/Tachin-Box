#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试路径连接线修复
Test path connection line fix
"""

import sys
import os
import numpy as np

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner, PathPlanningGameEnhancer

def test_path_connection_fix():
    """测试路径连接线修复"""
    print("🔧 测试路径连接线修复")
    print("=" * 50)
    
    # 1. 创建路径规划器
    planner = PathPlanner()
    print("✅ 路径规划器创建成功")
    
    # 2. 获取TACHIN路径
    tachin_path = planner.available_paths.get("TACHIN字母")
    if not tachin_path:
        print("❌ 未找到TACHIN字母路径")
        return
    
    print(f"✅ 找到TACHIN路径: {tachin_path.name}")
    print(f"📊 路径点数: {len(tachin_path.points)}")
    
    # 3. 创建路径规划游戏增强器
    enhancer = PathPlanningGameEnhancer()
    print(f"✅ 路径规划游戏增强器创建成功")
    
    # 4. 启用路径模式
    success = enhancer.enable_path_mode("TACHIN字母")
    print(f"✅ 启用路径模式: {success}")
    
    # 5. 获取当前导航信息
    current_nav_info = enhancer.get_current_navigation_info()
    print(f"\n📊 增强器导航信息:")
    print(f"  has_path: {current_nav_info.get('has_path', False)}")
    print(f"  has_navigation: {current_nav_info.get('has_navigation', False)}")
    print(f"  path_name: {current_nav_info.get('path_name', 'N/A')}")
    print(f"  path_points: {len(current_nav_info.get('path_points', []))} 个点")
    
    # 6. 检查连接类型分布
    current_path_points = current_nav_info.get('path_points', [])
    solid_count = sum(1 for p in current_path_points if p.get('connection_type') == 'solid')
    none_count = sum(1 for p in current_path_points if p.get('connection_type') == 'none')
    
    print(f"\n📈 连接类型统计:")
    print(f"  Solid连接: {solid_count}")
    print(f"  断点(None): {none_count}")
    print(f"  总点数: {len(current_path_points)}")
    
    # 7. 检查断点位置
    break_positions = [i for i, p in enumerate(current_path_points) if p.get('connection_type') == 'none']
    print(f"🔗 断点位置: {break_positions}")
    
    # 8. 模拟路径可视化管理器的渲染逻辑
    print(f"\n🎨 模拟路径渲染逻辑:")
    expected_lines = 0
    if len(current_path_points) >= 2:
        for i in range(len(current_path_points) - 1):
            current_point = current_path_points[i]
            next_point = current_path_points[i + 1]
            
            current_type = current_point.get('connection_type', 'solid')
            next_type = next_point.get('connection_type', 'solid')
            
            if current_type == 'solid' and next_type == 'solid':
                print(f"  ✅ 点{i}到点{i+1}: 绘制连线 (solid -> solid)")
                expected_lines += 1
            else:
                print(f"  ❌ 点{i}到点{i+1}: 跳过连线 (存在断点)")
    else:
        print(f"  ❌ 路径点不足，无法绘制连线")
    
    print(f"\n📊 预期连线数量: {expected_lines}")
    
    # 9. 验证修复效果
    print(f"\n✅ 修复效果验证:")
    print(f"  - 路径数据正确: {'✅' if len(current_path_points) == 35 else '❌'}")
    print(f"  - Solid连接点: {'✅' if solid_count == 30 else '❌'} ({solid_count}/30)")
    print(f"  - 断点数量: {'✅' if none_count == 5 else '❌'} ({none_count}/5)")
    print(f"  - 预期连线: {'✅' if expected_lines > 0 else '❌'} ({expected_lines} 条)")
    print(f"  - 字母独立性: {'✅' if len(break_positions) == 5 else '❌'}")
    
    # 10. 检查字母分布
    letter_ranges = [
        ("T", 0, 3),     # T字母：点0-3
        ("A", 5, 9),     # A字母：点5-9
        ("C", 11, 15),   # C字母：点11-15
        ("H", 17, 22),   # H字母：点17-22
        ("I", 24, 29),   # I字母：点24-29
        ("N", 31, 34),   # N字母：点31-34
    ]
    
    print(f"\n🔤 字母分布检查:")
    for letter, start_idx, end_idx in letter_ranges:
        letter_points = current_path_points[start_idx:end_idx+1]
        solid_in_letter = sum(1 for p in letter_points if p.get('connection_type') == 'solid')
        none_in_letter = sum(1 for p in letter_points if p.get('connection_type') == 'none')
        
        print(f"  {letter}字母 (点{start_idx}-{end_idx}): {solid_in_letter}个solid, {none_in_letter}个断点")
        
        # 检查字母内部是否有连线
        letter_lines = 0
        for i in range(start_idx, end_idx):
            if i + 1 <= end_idx:
                current_type = current_path_points[i].get('connection_type', 'solid')
                next_type = current_path_points[i + 1].get('connection_type', 'solid')
                if current_type == 'solid' and next_type == 'solid':
                    letter_lines += 1
        
        print(f"    -> 内部连线: {letter_lines} 条")
    
    print(f"\n🔍 修复检查完成")
    print(f"💡 提示：现在路径模式启用时应该能看到字母内部的连线，字母间无连线")

if __name__ == "__main__":
    test_path_connection_fix() 