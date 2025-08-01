#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化优化后的字母和表情路径
Visualize optimized letter and emoji paths
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanner
import matplotlib.pyplot as plt
import numpy as np

def visualize_paths():
    """可视化所有路径"""
    print("🎨 可视化优化后的字母和表情路径")
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 要可视化的路径
    paths_to_show = [
        "AI字母", "TACHIN字母", 
        "😊 笑脸", "😢 哭脸", "😎 酷脸", 
        "❤️ 爱心", "⭐ 星星"
    ]
    
    # 创建子图
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    for i, path_name in enumerate(paths_to_show):
        if i >= len(axes):
            break
            
        ax = axes[i]
        
        if path_name in planner.available_paths:
            planner.set_current_path(path_name)
            path = planner.get_current_path()
            
            # 提取路径点
            x_coords = [point.x for point in path.points]
            y_coords = [point.y for point in path.points]
            
            # 绘制路径
            ax.plot(x_coords, y_coords, 'b-', linewidth=2, alpha=0.7)
            ax.plot(x_coords, y_coords, 'ro', markersize=6, alpha=0.8)
            
            # 标记起点和终点
            ax.plot(x_coords[0], y_coords[0], 'go', markersize=10, label='起点')
            ax.plot(x_coords[-1], y_coords[-1], 'mo', markersize=10, label='终点')
            
            # 设置标题和标签
            ax.set_title(f'{path_name}\n({len(path.points)} 个点)', fontsize=12)
            ax.set_xlabel('X坐标')
            ax.set_ylabel('Y坐标')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # 设置坐标轴范围
            ax.set_xlim(0, 70)
            ax.set_ylim(0, 50)
            
            print(f"  ✅ {path_name}: {len(path.points)} 个点")
        else:
            ax.text(0.5, 0.5, f'路径未找到:\n{path_name}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(path_name)
            print(f"  ❌ {path_name}: 未找到")
    
    # 隐藏多余的子图
    for i in range(len(paths_to_show), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    plt.suptitle('🎯 优化后的字母和表情路径可视化', fontsize=16, y=1.02)
    
    # 保存图片
    plt.savefig('optimized_paths_visualization.png', dpi=300, bbox_inches='tight')
    print(f"\n📸 路径可视化已保存为: optimized_paths_visualization.png")
    
    # 显示图片
    plt.show()

def compare_path_complexity():
    """比较路径复杂度"""
    print("\n📊 路径复杂度比较:")
    print("=" * 50)
    
    planner = PathPlanner()
    
    # 获取所有路径
    all_paths = planner.get_path_names()
    
    # 分析每个路径
    path_stats = []
    for path_name in all_paths:
        planner.set_current_path(path_name)
        path = planner.get_current_path()
        
        # 计算路径总距离
        total_distance = path.get_total_distance()
        
        path_stats.append({
            'name': path_name,
            'points': len(path.points),
            'distance': total_distance,
            'avg_distance': total_distance / len(path.points) if len(path.points) > 0 else 0
        })
    
    # 按点数排序
    path_stats.sort(key=lambda x: x['points'])
    
    print(f"{'路径名称':<15} {'点数':<6} {'总距离':<8} {'平均距离':<8}")
    print("-" * 50)
    
    for stat in path_stats:
        print(f"{stat['name']:<15} {stat['points']:<6} {stat['distance']:<8.1f} {stat['avg_distance']:<8.1f}")
    
    # 找出最简洁和最复杂的路径
    simplest = min(path_stats, key=lambda x: x['points'])
    most_complex = max(path_stats, key=lambda x: x['points'])
    
    print(f"\n🎯 最简洁路径: {simplest['name']} ({simplest['points']} 个点)")
    print(f"🎯 最复杂路径: {most_complex['name']} ({most_complex['points']} 个点)")

if __name__ == "__main__":
    try:
        visualize_paths()
        compare_path_complexity()
        print("\n✅ 路径可视化完成!")
    except Exception as e:
        print(f"❌ 可视化过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 