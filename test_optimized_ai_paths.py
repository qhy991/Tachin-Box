# -*- coding: utf-8 -*-
"""
测试优化后的AI路径
Test Optimized AI Paths

验证AI智能路径和TACHIN字母路径的优化效果
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanner
import matplotlib.pyplot as plt
import numpy as np

def test_optimized_paths():
    """测试优化后的路径"""
    print("🧪 测试优化后的AI路径")
    print("=" * 50)
    
    # 创建路径规划器
    planner = PathPlanner()
    planner.setup_preset_paths()
    
    # 测试AI智能路径
    print("\n🎯 测试AI智能路径:")
    ai_path = planner.available_paths.get("AI智能路径")
    if ai_path:
        print(f"✅ 找到AI智能路径，包含 {len(ai_path.points)} 个点")
        
        # 检查坐标范围
        x_coords = [p.x for p in ai_path.points]
        y_coords = [p.y for p in ai_path.points]
        
        print(f"X坐标范围: {min(x_coords):.1f} - {max(x_coords):.1f}")
        print(f"Y坐标范围: {min(y_coords):.1f} - {max(y_coords):.1f}")
        
        # 验证是否在64x64范围内
        if max(x_coords) <= 64 and max(y_coords) <= 64:
            print("✅ 坐标范围符合64x64要求")
        else:
            print("❌ 坐标超出64x64范围")
        
        # 显示路径点
        print("\n路径点详情:")
        for i, point in enumerate(ai_path.points):
            print(f"  点{i+1}: ({point.x:.1f}, {point.y:.1f}) - {point.point_type} - {point.connection_type}")
    else:
        print("❌ 未找到AI智能路径")
    
    # 测试TACHIN字母路径
    print("\n🎯 测试TACHIN字母路径:")
    tachin_path = planner.available_paths.get("TACHIN字母")
    if tachin_path:
        print(f"✅ 找到TACHIN字母路径，包含 {len(tachin_path.points)} 个点")
        
        # 检查坐标范围
        x_coords = [p.x for p in tachin_path.points]
        y_coords = [p.y for p in tachin_path.points]
        
        print(f"X坐标范围: {min(x_coords):.1f} - {max(x_coords):.1f}")
        print(f"Y坐标范围: {min(y_coords):.1f} - {max(y_coords):.1f}")
        
        # 验证是否在64x64范围内
        if max(x_coords) <= 64 and max(y_coords) <= 64:
            print("✅ 坐标范围符合64x64要求")
        else:
            print("❌ 坐标超出64x64范围")
        
        # 显示路径点
        print("\n路径点详情:")
        for i, point in enumerate(tachin_path.points):
            print(f"  点{i+1}: ({point.x:.1f}, {point.y:.1f}) - {point.point_type} - {point.connection_type}")
    else:
        print("❌ 未找到TACHIN字母路径")
    
    # 计算路径总距离
    print("\n📏 路径距离分析:")
    if ai_path:
        ai_distance = ai_path.get_total_distance()
        print(f"AI智能路径总距离: {ai_distance:.2f}")
    
    if tachin_path:
        tachin_distance = tachin_path.get_total_distance()
        print(f"TACHIN字母路径总距离: {tachin_distance:.2f}")

def visualize_optimized_paths():
    """可视化优化后的路径"""
    print("\n🎨 可视化优化后的路径")
    print("=" * 50)
    
    planner = PathPlanner()
    planner.setup_preset_paths()
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 绘制AI智能路径
    ai_path = planner.available_paths.get("AI智能路径")
    if ai_path:
        ax1.set_title("AI Smart Path (Optimized)", fontsize=14, fontweight='bold')
        ax1.set_xlim(0, 64)
        ax1.set_ylim(64, 0)  # Y轴向下
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 绘制路径点和连接线
        for i in range(len(ai_path.points) - 1):
            current = ai_path.points[i]
            next_point = ai_path.points[i + 1]
            
            # 根据连接类型绘制不同的线型
            if current.connection_type == "solid":
                ax1.plot([current.x, next_point.x], [current.y, next_point.y], 
                        'b-', linewidth=2, alpha=0.8)
            elif current.connection_type == "dashed":
                ax1.plot([current.x, next_point.x], [current.y, next_point.y], 
                        'b--', linewidth=1, alpha=0.6)
            elif current.connection_type == "none":
                # 不绘制连接线
                pass
        
        # 绘制路径点
        for i, point in enumerate(ai_path.points):
            if point.point_type == "start":
                ax1.plot(point.x, point.y, 'go', markersize=8, label='Start' if i == 0 else "")
            elif point.point_type == "target":
                ax1.plot(point.x, point.y, 'ro', markersize=8, label='End' if i == len(ai_path.points)-1 else "")
            else:
                ax1.plot(point.x, point.y, 'bo', markersize=4, alpha=0.7)
        
        ax1.legend()
    
    # 绘制TACHIN字母路径
    tachin_path = planner.available_paths.get("TACHIN字母")
    if tachin_path:
        ax2.set_title("TACHIN Letters Path (Optimized)", fontsize=14, fontweight='bold')
        ax2.set_xlim(0, 64)
        ax2.set_ylim(64, 0)  # Y轴向下
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal')
        
        # 绘制路径点和连接线
        for i in range(len(tachin_path.points) - 1):
            current = tachin_path.points[i]
            next_point = tachin_path.points[i + 1]
            
            # 根据连接类型绘制不同的线型
            if current.connection_type == "solid":
                ax2.plot([current.x, next_point.x], [current.y, next_point.y], 
                        'g-', linewidth=2, alpha=0.8)
            elif current.connection_type == "dashed":
                ax2.plot([current.x, next_point.x], [current.y, next_point.y], 
                        'g--', linewidth=1, alpha=0.6)
            elif current.connection_type == "none":
                # 不绘制连接线
                pass
        
        # 绘制路径点
        for i, point in enumerate(tachin_path.points):
            if point.point_type == "start":
                ax2.plot(point.x, point.y, 'go', markersize=8, label='Start' if i == 0 else "")
            elif point.point_type == "target":
                ax2.plot(point.x, point.y, 'ro', markersize=8, label='End' if i == len(tachin_path.points)-1 else "")
            else:
                ax2.plot(point.x, point.y, 'go', markersize=4, alpha=0.7)
        
        ax2.legend()
    
    plt.tight_layout()
    plt.show()

def test_path_continuity():
    """测试路径连续性"""
    print("\n🔗 测试路径连续性")
    print("=" * 50)
    
    planner = PathPlanner()
    planner.setup_preset_paths()
    
    for path_name in ["AI智能路径", "TACHIN字母"]:
        path = planner.available_paths.get(path_name)
        if path:
            print(f"\n📋 {path_name}:")
            
            # 检查连接类型
            solid_connections = 0
            dashed_connections = 0
            none_connections = 0
            
            for i in range(len(path.points) - 1):
                current = path.points[i]
                next_point = path.points[i + 1]
                
                if current.connection_type == "solid":
                    solid_connections += 1
                elif current.connection_type == "dashed":
                    dashed_connections += 1
                elif current.connection_type == "none":
                    none_connections += 1
                
                # 计算距离
                distance = current.distance_to(next_point.x, next_point.y)
                print(f"  点{i+1}到点{i+2}: 距离={distance:.2f}, 连接类型={current.connection_type}")
            
            print(f"  实线连接: {solid_connections}")
            print(f"  虚线连接: {dashed_connections}")
            print(f"  无连接: {none_connections}")

if __name__ == "__main__":
    print("🚀 开始测试优化后的AI路径")
    
    # 测试路径
    test_optimized_paths()
    
    # 测试连续性
    test_path_continuity()
    
    # 可视化路径
    try:
        visualize_optimized_paths()
    except Exception as e:
        print(f"⚠️ 可视化失败: {e}")
    
    print("\n✅ 测试完成") 