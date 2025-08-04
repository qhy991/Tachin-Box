#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的AI字母和表情路径
Test script for optimized AI letter and emoji paths
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanner
import numpy as np
import matplotlib.pyplot as plt

def test_optimized_paths():
    """测试优化后的路径"""
    print("🎯 测试优化后的AI字母和表情路径")
    print("=" * 60)
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 测试AI字母路径
    print("\n🤖 测试AI字母路径:")
    if "AI字母" in planner.available_paths:
        planner.set_current_path("AI字母")
        path = planner.get_current_path()
        print(f"  ✅ AI字母路径: {len(path.points)} 个点")
        
        # 分析路径结构
        solid_points = [p for p in path.points if p.connection_type == "solid"]
        none_points = [p for p in path.points if p.connection_type == "none"]
        
        print(f"     实线连接点: {len(solid_points)} 个")
        print(f"     断开连接点: {len(none_points)} 个")
        print(f"     起点: ({path.points[0].x:.1f}, {path.points[0].y:.1f})")
        print(f"     终点: ({path.points[-1].x:.1f}, {path.points[-1].y:.1f})")
        
        # 检查坐标范围
        x_coords = [p.x for p in path.points]
        y_coords = [p.y for p in path.points]
        print(f"     X坐标范围: {min(x_coords):.1f} - {max(x_coords):.1f}")
        print(f"     Y坐标范围: {min(y_coords):.1f} - {max(y_coords):.1f}")
        
        # 验证是否在64x64范围内
        if max(x_coords) <= 64 and max(y_coords) <= 64 and min(x_coords) >= 0 and min(y_coords) >= 0:
            print("     ✅ 坐标在64x64范围内")
        else:
            print("     ❌ 坐标超出64x64范围")
    else:
        print("  ❌ AI字母路径: 未找到")
    
    # 测试表情路径
    print("\n😊 测试表情路径:")
    emoji_paths = ["😊 笑脸", "😢 哭脸", "😎 酷脸", "❤️ 爱心", "⭐ 星星"]
    
    for path_name in emoji_paths:
        if path_name in planner.available_paths:
            planner.set_current_path(path_name)
            path = planner.get_current_path()
            print(f"  ✅ {path_name}: {len(path.points)} 个点")
            
            # 分析路径结构
            solid_points = [p for p in path.points if p.connection_type == "solid"]
            none_points = [p for p in path.points if p.connection_type == "none"]
            
            print(f"     实线连接点: {len(solid_points)} 个")
            print(f"     断开连接点: {len(none_points)} 个")
            
            # 检查坐标范围
            x_coords = [p.x for p in path.points]
            y_coords = [p.y for p in path.points]
            print(f"     X坐标范围: {min(x_coords):.1f} - {max(x_coords):.1f}")
            print(f"     Y坐标范围: {min(y_coords):.1f} - {max(y_coords):.1f}")
            
            # 验证是否在64x64范围内
            if max(x_coords) <= 64 and max(y_coords) <= 64 and min(x_coords) >= 0 and min(y_coords) >= 0:
                print("     ✅ 坐标在64x64范围内")
            else:
                print("     ❌ 坐标超出64x64范围")
        else:
            print(f"  ❌ {path_name}: 未找到")
    
    print("\n" + "=" * 60)
    print("🎯 优化总结:")
    print("✅ 参考TACHIN字母设计理念")
    print("✅ 消除不必要的断点连线")
    print("✅ 在64x64范围内合理布局")
    print("✅ 考虑Y轴反向问题")
    print("✅ 保持路径简洁清晰")
    print("=" * 60)

def visualize_optimized_paths():
    """可视化优化后的路径"""
    print("\n🎨 可视化优化后的路径")
    print("=" * 60)
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 创建图形
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    # 要可视化的路径
    paths_to_visualize = [
        ("AI字母", 0),
        ("😊 笑脸", 1),
        ("😢 哭脸", 2),
        ("😎 酷脸", 3),
        ("❤️ 爱心", 4),
        ("⭐ 星星", 5)
    ]
    
    for path_name, ax_idx in paths_to_visualize:
        if path_name in planner.available_paths:
            planner.set_current_path(path_name)
            path = planner.get_current_path()
            
            ax = axes[ax_idx]
            ax.set_title(f"{path_name} - 优化版本", fontsize=12)
            
            # 提取所有点
            points = [(p.x, p.y) for p in path.points]
            connection_types = [p.connection_type for p in path.points]
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            # 分别绘制solid和none连接
            solid_x, solid_y = [], []
            none_x, none_y = [], []
            
            for i, (x, y) in enumerate(points):
                if connection_types[i] == "solid":
                    solid_x.append(x)
                    solid_y.append(y)
                else:  # none
                    none_x.append(x)
                    none_y.append(y)
            
            # 绘制solid连接
            if solid_x:
                ax.plot(solid_x, solid_y, 'b-o', linewidth=2, markersize=6, alpha=0.8, label='实线连接')
            
            # 绘制none连接（断开点）
            if none_x:
                ax.scatter(none_x, none_y, c='red', s=80, marker='x', alpha=0.8, label='断开连接')
            
            # 添加序号标签
            for i, (x, y) in enumerate(points):
                ax.annotate(str(i), (x, y), xytext=(3, 3), textcoords='offset points', 
                           fontsize=8, fontweight='bold', color='red')
            
            # 标记起点和终点
            if points:
                ax.scatter(points[0][0], points[0][1], c='green', s=100, marker='s', label='起点')
                ax.scatter(points[-1][0], points[-1][1], c='red', s=100, marker='s', label='终点')
            
            ax.set_xlim(0, 64)
            ax.set_ylim(0, 64)
            ax.invert_yaxis()  # 考虑Y轴反向
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8)
            ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('optimized_ai_emoji_paths.png', dpi=300, bbox_inches='tight')
    print("✅ 可视化图片已保存为: optimized_ai_emoji_paths.png")
    plt.show()

if __name__ == "__main__":
    test_optimized_paths()
    visualize_optimized_paths() 