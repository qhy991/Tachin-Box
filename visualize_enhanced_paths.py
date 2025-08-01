#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化增强后的字母和表情路径
Visualize enhanced letter and emoji paths with different connection types
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces.ordinary.BoxGame.box_game_path_planning import PathPlanner
import matplotlib.pyplot as plt
import numpy as np

def visualize_enhanced_paths():
    """可视化增强后的路径，包括不同的连接类型"""
    print("🎨 可视化增强后的字母和表情路径")
    
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
            if solid_points:
                ax.plot(solid_points[0][0], solid_points[0][1], 'go', markersize=12, label='起点')
                ax.plot(solid_points[-1][0], solid_points[-1][1], 'mo', markersize=12, label='终点')
            
            # 设置标题和标签
            total_points = len(path.points)
            solid_count = len(solid_points)
            dashed_count = len(dashed_points)
            none_count = len(none_points)
            
            title = f'{path_name}\n总点数: {total_points}'
            if solid_count > 0:
                title += f'\n实线: {solid_count}'
            if dashed_count > 0:
                title += f'\n虚线: {dashed_count}'
            if none_count > 0:
                title += f'\n装饰: {none_count}'
            
            ax.set_title(title, fontsize=10)
            ax.set_xlabel('X坐标')
            ax.set_ylabel('Y坐标')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8)
            
            # 设置坐标轴范围
            ax.set_xlim(0, 80)
            ax.set_ylim(0, 50)
            
            print(f"  ✅ {path_name}: {total_points} 个点 (实线:{solid_count}, 虚线:{dashed_count}, 装饰:{none_count})")
        else:
            ax.text(0.5, 0.5, f'路径未找到:\n{path_name}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(path_name)
            print(f"  ❌ {path_name}: 未找到")
    
    # 隐藏多余的子图
    for i in range(len(paths_to_show), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    plt.suptitle('🎯 增强后的字母和表情路径可视化\n(实线=主要路径, 虚线=引导路径, 装饰点=不连接)', fontsize=14, y=1.02)
    
    # 保存图片
    plt.savefig('enhanced_paths_visualization.png', dpi=300, bbox_inches='tight')
    print(f"\n📸 增强路径可视化已保存为: enhanced_paths_visualization.png")
    
    # 显示图片
    plt.show()

def analyze_connection_types():
    """分析连接类型分布"""
    print("\n📊 连接类型分析:")
    print("=" * 60)
    
    planner = PathPlanner()
    
    # 获取所有路径
    all_paths = planner.get_path_names()
    
    # 分析每个路径的连接类型
    path_analysis = []
    for path_name in all_paths:
        planner.set_current_path(path_name)
        path = planner.get_current_path()
        
        # 统计连接类型
        solid_count = sum(1 for p in path.points if p.connection_type == "solid")
        dashed_count = sum(1 for p in path.points if p.connection_type == "dashed")
        none_count = sum(1 for p in path.points if p.connection_type == "none")
        
        path_analysis.append({
            'name': path_name,
            'total': len(path.points),
            'solid': solid_count,
            'dashed': dashed_count,
            'none': none_count
        })
    
    # 按总点数排序
    path_analysis.sort(key=lambda x: x['total'])
    
    print(f"{'路径名称':<15} {'总点数':<6} {'实线':<6} {'虚线':<6} {'装饰':<6}")
    print("-" * 60)
    
    for analysis in path_analysis:
        print(f"{analysis['name']:<15} {analysis['total']:<6} {analysis['solid']:<6} {analysis['dashed']:<6} {analysis['none']:<6}")
    
    # 统计总体分布
    total_solid = sum(a['solid'] for a in path_analysis)
    total_dashed = sum(a['dashed'] for a in path_analysis)
    total_none = sum(a['none'] for a in path_analysis)
    total_points = sum(a['total'] for a in path_analysis)
    
    print("-" * 60)
    print(f"{'总计':<15} {total_points:<6} {total_solid:<6} {total_dashed:<6} {total_none:<6}")
    print(f"比例: {total_solid/total_points*100:.1f}% 实线, {total_dashed/total_points*100:.1f}% 虚线, {total_none/total_points*100:.1f}% 装饰")

if __name__ == "__main__":
    try:
        visualize_enhanced_paths()
        analyze_connection_types()
        print("\n✅ 增强路径可视化完成!")
    except Exception as e:
        print(f"❌ 可视化过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 