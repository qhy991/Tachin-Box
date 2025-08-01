#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试路径连接数据
Debug path connection data
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner

def debug_path_connection_data():
    """调试路径连接数据"""
    print("🔍 调试路径连接数据")
    print("=" * 50)
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 获取TACHIN路径
    tachin_path = planner.available_paths.get("TACHIN字母")
    if not tachin_path:
        print("❌ 未找到TACHIN字母路径")
        return
    
    # 设置当前路径
    planner.set_current_path("TACHIN字母")
    
    # 模拟box_position
    box_position = np.array([32.0, 32.0])
    
    # 获取导航信息
    nav_info = planner.get_navigation_info(box_position)
    
    print("📊 导航信息结构:")
    print(f"  has_path: {nav_info.get('has_path', False)}")
    print(f"  path_name: {nav_info.get('path_name', 'N/A')}")
    print(f"  has_navigation: {nav_info.get('has_navigation', False)}")
    
    # 检查路径点数据
    path_points = nav_info.get('path_points', [])
    print(f"\n📊 路径点数据 ({len(path_points)} 个点):")
    
    for i, point in enumerate(path_points):
        connection_type = point.get('connection_type', 'N/A')
        point_type = point.get('type', 'N/A')
        x, y = point.get('x', 0), point.get('y', 0)
        
        print(f"  点{i}: ({x}, {y}) - 类型:{point_type} - 连接:{connection_type}")
        
        # 特别标记断开点
        if connection_type == 'none':
            print(f"    🔗 这是断开点！")
    
    # 统计连接类型
    solid_count = sum(1 for p in path_points if p.get('connection_type') == 'solid')
    none_count = sum(1 for p in path_points if p.get('connection_type') == 'none')
    missing_count = sum(1 for p in path_points if 'connection_type' not in p)
    
    print(f"\n📊 连接类型统计:")
    print(f"  solid连接: {solid_count}个点")
    print(f"  none断开: {none_count}个点")
    print(f"  缺失connection_type: {missing_count}个点")
    
    # 检查是否有缺失的connection_type
    if missing_count > 0:
        print(f"\n⚠️ 发现问题：有{missing_count}个点缺失connection_type信息")
        print("这可能是导致UI中仍然显示连线的原因")
        
        # 显示缺失connection_type的点
        for i, point in enumerate(path_points):
            if 'connection_type' not in point:
                print(f"  点{i}: ({point.get('x', 0)}, {point.get('y', 0)}) - 缺失connection_type")
    else:
        print(f"\n✅ 所有点都有connection_type信息")
    
    # 检查原始路径点
    print(f"\n📊 原始路径点数据:")
    for i, point in enumerate(tachin_path.points):
        print(f"  点{i}: ({point.x}, {point.y}) - 类型:{point.point_type} - 连接:{point.connection_type}")
    
    # 检查to_dict()方法
    print(f"\n📊 测试to_dict()方法:")
    test_point = tachin_path.points[0]
    test_dict = test_point.to_dict()
    print(f"  原始点: connection_type={test_point.connection_type}")
    print(f"  to_dict(): connection_type={test_dict.get('connection_type', 'N/A')}")
    
    return nav_info

if __name__ == "__main__":
    import numpy as np
    debug_path_connection_data() 