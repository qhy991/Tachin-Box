#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化简化后的路径
Visualize Simplified Paths
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner
import matplotlib.pyplot as plt
import numpy as np

def visualize_simplified_paths():
    """可视化简化后的路径"""
    print("🎨 可视化简化后的路径")
    print("=" * 50)
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 要显示的路径
    paths_to_show = [
        "TACHIN字母",
        "😊 笑脸", 
        "😢 哭脸",
        "😎 酷脸",
        "❤️ 爱心",
        "⭐ 星星"
    ]
    
    # 创建子图
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, path_name in enumerate(paths_to_show):
        if path_name not in planner.available_paths:
            print(f"❌ 路径不存在: {path_name}")
            continue
            
        path = planner.available_paths[path_name]
        ax = axes[i]
        
        # 分离不同类型的点
        solid_points = []
        dashed_points = []
        none_points = []
        
        for point in path.points:
            if point.connection_type == "solid":
                solid_points.append((point.x, point.y))
            elif point.connection_type == "dashed":
                dashed_points.append((point.x, point.y))
            elif point.connection_type == "none":
                none_points.append((point.x, point.y))
        
        # 绘制实线路径
        if len(solid_points) > 1:
            solid_x = [p[0] for p in solid_points]
            solid_y = [p[1] for p in solid_points]
            ax.plot(solid_x, solid_y, 'b-', linewidth=3, alpha=0.8, label='主要路径')
            ax.plot(solid_x, solid_y, 'ro', markersize=6, alpha=0.8)
        
        # 绘制虚线路径
        if len(dashed_points) > 1:
            dashed_x = [p[0] for p in dashed_points]
            dashed_y = [p[1] for p in dashed_points]
            ax.plot(dashed_x, dashed_y, 'g--', linewidth=2, alpha=0.6, label='引导路径')
            ax.plot(dashed_x, dashed_y, 'go', markersize=5, alpha=0.7)
        
        # 绘制不连接的点
        if none_points:
            none_x = [p[0] for p in none_points]
            none_y = [p[1] for p in none_points]
            ax.plot(none_x, none_y, 'mo', markersize=8, alpha=0.9, label='装饰点')
        
        # 标记起点和终点
        if path.points:
            start = path.points[0]
            end = path.points[-1]
            ax.plot(start.x, start.y, 'gs', markersize=10, label='起点')
            ax.plot(end.x, end.y, 'rs', markersize=10, label='终点')
        
        # 设置坐标轴
        ax.set_xlim(0, 64)
        ax.set_ylim(0, 64)
        ax.invert_yaxis()  # Y轴向下
        ax.grid(True, alpha=0.3)
        ax.set_title(f'{path_name}\n({len(path.points)} 个点)', fontsize=12)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        # 统计信息
        solid_count = len(solid_points)
        dashed_count = len(dashed_points)
        none_count = len(none_points)
        
        info_text = f'实线: {solid_count}\n虚线: {dashed_count}\n装饰: {none_count}'
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                verticalalignment='top', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('simplified_paths.png', dpi=300, bbox_inches='tight')
    print("✅ 简化路径可视化已保存为: simplified_paths.png")
    
    # 打印统计信息
    print("\n📊 简化后的路径统计:")
    print("-" * 40)
    for path_name in paths_to_show:
        if path_name in planner.available_paths:
            path = planner.available_paths[path_name]
            solid_count = sum(1 for p in path.points if p.connection_type == "solid")
            dashed_count = sum(1 for p in path.points if p.connection_type == "dashed")
            none_count = sum(1 for p in path.points if p.connection_type == "none")
            
            print(f"{path_name}:")
            print(f"  总点数: {len(path.points)}")
            print(f"  实线点: {solid_count}")
            print(f"  虚线点: {dashed_count}")
            print(f"  装饰点: {none_count}")
            print()

if __name__ == "__main__":
    visualize_simplified_paths() 