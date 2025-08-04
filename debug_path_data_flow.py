#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试路径数据流
Debug path data flow
"""

import sys
import os
import numpy as np

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner, PathPlanningGameEnhancer

def debug_path_data_flow():
    """调试路径数据流"""
    print("🔍 调试路径数据流")
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
    
    # 3. 设置当前路径
    success = planner.set_current_path("TACHIN字母")
    print(f"✅ 设置当前路径: {success}")
    
    # 4. 模拟box_position
    box_position = np.array([32.0, 32.0])
    print(f"📍 模拟箱子位置: {box_position}")
    
    # 5. 获取导航信息
    nav_info = planner.get_navigation_info(box_position)
    print(f"\n📊 导航信息:")
    print(f"  has_path: {nav_info.get('has_path', False)}")
    print(f"  has_navigation: {nav_info.get('has_navigation', False)}")
    print(f"  path_name: {nav_info.get('path_name', 'N/A')}")
    print(f"  path_points: {len(nav_info.get('path_points', []))} 个点")
    print(f"  current_target: {nav_info.get('current_target', 'N/A')}")
    print(f"  next_target: {nav_info.get('next_target', 'N/A')}")
    print(f"  target_distance: {nav_info.get('target_distance', 0.0)}")
    print(f"  direction_angle: {nav_info.get('direction_angle', 0.0)}")
    print(f"  progress: {nav_info.get('progress', {})}")
    
    # 6. 检查路径点数据
    path_points = nav_info.get('path_points', [])
    print(f"\n📊 路径点数据检查:")
    for i, point in enumerate(path_points[:10]):  # 只显示前10个点
        connection_type = point.get('connection_type', 'N/A')
        point_type = point.get('type', 'N/A')
        x, y = point.get('x', 0), point.get('y', 0)
        print(f"  点{i}: ({x}, {y}) - 类型:{point_type} - 连接:{connection_type}")
    
    if len(path_points) > 10:
        print(f"  ... 还有 {len(path_points) - 10} 个点")
    
    # 7. 创建路径规划游戏增强器
    enhancer = PathPlanningGameEnhancer()
    print(f"\n✅ 路径规划游戏增强器创建成功")
    
    # 8. 启用路径模式
    success = enhancer.enable_path_mode("TACHIN字母")
    print(f"✅ 启用路径模式: {success}")
    
    # 9. 获取当前导航信息
    current_nav_info = enhancer.get_current_navigation_info()
    print(f"\n📊 增强器导航信息:")
    print(f"  has_path: {current_nav_info.get('has_path', False)}")
    print(f"  has_navigation: {current_nav_info.get('has_navigation', False)}")
    print(f"  path_name: {current_nav_info.get('path_name', 'N/A')}")
    print(f"  path_points: {len(current_nav_info.get('path_points', []))} 个点")
    
    # 10. 检查连接类型分布
    current_path_points = current_nav_info.get('path_points', [])
    solid_count = sum(1 for p in current_path_points if p.get('connection_type') == 'solid')
    none_count = sum(1 for p in current_path_points if p.get('connection_type') == 'none')
    
    print(f"\n📈 连接类型统计:")
    print(f"  Solid连接: {solid_count}")
    print(f"  断点(None): {none_count}")
    print(f"  总点数: {len(current_path_points)}")
    
    # 11. 检查是否有足够的solid连接来绘制线条
    if solid_count >= 2:
        print(f"✅ 有足够的solid连接点来绘制线条")
    else:
        print(f"❌ solid连接点不足，无法绘制线条")
    
    # 12. 检查断点位置
    break_positions = [i for i, p in enumerate(current_path_points) if p.get('connection_type') == 'none']
    print(f"🔗 断点位置: {break_positions}")
    
    # 13. 模拟路径可视化管理器的渲染逻辑
    print(f"\n🎨 模拟路径渲染逻辑:")
    if len(current_path_points) >= 2:
        for i in range(len(current_path_points) - 1):
            current_point = current_path_points[i]
            next_point = current_path_points[i + 1]
            
            current_type = current_point.get('connection_type', 'solid')
            next_type = next_point.get('connection_type', 'solid')
            
            if current_type == 'solid' and next_type == 'solid':
                print(f"  ✅ 点{i}到点{i+1}: 绘制连线 (solid -> solid)")
            else:
                print(f"  ❌ 点{i}到点{i+1}: 跳过连线 (存在断点)")
    else:
        print(f"  ❌ 路径点不足，无法绘制连线")
    
    print(f"\n🔍 数据流检查完成")

if __name__ == "__main__":
    debug_path_data_flow() 