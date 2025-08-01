#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化独立字母的TACHIN路径设计
Visualize independent letters TACHIN path design
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner

def visualize_independent_letters():
    """可视化独立字母的TACHIN路径设计"""
    print("🎯 可视化独立字母的TACHIN路径设计")
    print("=" * 50)
    
    # 创建路径规划器
    planner = PathPlanner()
    
    # 获取TACHIN路径
    tachin_path = planner.available_paths.get("TACHIN字母")
    if not tachin_path:
        print("❌ 未找到TACHIN字母路径")
        return
    
    # 创建图形
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()
    
    # 测试1：完整TACHIN路径（独立字母）
    ax1 = axes[0]
    ax1.set_title("TACHIN - 独立字母路径", fontsize=12)
    
    # 提取所有点
    points = [(p.x, p.y) for p in tachin_path.points]
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    # 绘制连线
    ax1.plot(x_coords, y_coords, 'b-o', linewidth=2, markersize=8, alpha=0.8)
    
    # 添加序号标签
    for i, (x, y) in enumerate(points):
        ax1.annotate(str(i), (x, y), xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, fontweight='bold', color='red')
    
    # 标记起点和终点
    ax1.scatter(x_coords[0], y_coords[0], c='green', s=120, marker='s', label='起点')
    ax1.scatter(x_coords[-1], y_coords[-1], c='red', s=120, marker='s', label='终点')
    
    ax1.set_xlim(0, 64)
    ax1.set_ylim(0, 64)
    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 测试2：按字母分组显示（独立绘制）
    ax2 = axes[1]
    ax2.set_title("TACHIN - 字母独立绘制", fontsize=12)
    
    # 定义每个字母的起始和结束索引
    letter_ranges = [
        ("T", 0, 3),     # T字母：点0-3
        ("A", 4, 8),     # A字母：点4-8
        ("C", 9, 13),    # C字母：点9-13
        ("H", 14, 19),   # H字母：点14-19
        ("I", 20, 25),   # I字母：点20-25
        ("N", 26, 29),   # N字母：点26-29
    ]
    
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
    
    for i, (letter, start, end) in enumerate(letter_ranges):
        letter_x = x_coords[start:end+1]
        letter_y = y_coords[start:end+1]
        ax2.plot(letter_x, letter_y, c=colors[i], linewidth=3, markersize=8, 
                marker='o', alpha=0.8, label=f'{letter}({start}-{end})')
        
        # 添加序号
        for j in range(start, end+1):
            ax2.annotate(str(j), (x_coords[j], y_coords[j]), xytext=(3, 3), 
                        textcoords='offset points', fontsize=7, fontweight='bold')
    
    ax2.set_xlim(0, 64)
    ax2.set_ylim(0, 64)
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 测试3：对比：独立字母 vs 连接字母
    ax3 = axes[2]
    ax3.set_title("独立字母 vs 连接字母", fontsize=12)
    
    # 独立字母设计（蓝色）
    ax3.plot(x_coords, y_coords, 'b-o', linewidth=2, markersize=6, alpha=0.8, label='独立字母(30点)')
    
    # 连接字母设计（红色虚线）- 假设的连接版本
    connected_points = [
        # T字母
        (8, 20), (16, 20), (12, 20), (12, 40),
        # 连接到A字母
        (20, 40), (24, 20), (28, 40), (26, 30), (22, 30),
        # 连接到C字母
        (36, 25), (28, 20), (24, 30), (28, 40), (36, 35),
        # 连接到H字母
        (40, 20), (40, 40), (40, 30), (48, 30), (48, 20), (48, 40),
        # 连接到I字母
        (52, 20), (60, 20), (56, 20), (56, 40), (52, 40), (60, 40),
        # 连接到N字母
        (64, 40), (64, 20), (60, 40), (60, 20)
    ]
    
    conn_x = [p[0] for p in connected_points]
    conn_y = [p[1] for p in connected_points]
    ax3.plot(conn_x, conn_y, 'r--o', linewidth=1, markersize=4, alpha=0.6, label='连接字母(30点)')
    
    ax3.set_xlim(0, 64)
    ax3.set_ylim(0, 64)
    ax3.invert_yaxis()
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 测试4：设计分析
    ax4 = axes[3]
    ax4.set_title("独立字母设计分析", fontsize=12)
    
    # 显示设计特点
    ax4.text(0.1, 0.9, "独立字母设计特点:", transform=ax4.transAxes, fontsize=12, fontweight='bold')
    ax4.text(0.1, 0.8, "• 每个字母独立绘制", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.72, "• 字母间无强制连接", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.64, "• 通过序号引导顺序", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.56, "• 更灵活的路径设计", transform=ax4.transAxes, fontsize=10)
    
    ax4.text(0.1, 0.45, "字母分布:", transform=ax4.transAxes, fontsize=11, fontweight='bold')
    ax4.text(0.1, 0.37, "• T: 点0-3 (8-16区域)", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.29, "• A: 点4-8 (20-28区域)", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.21, "• C: 点9-13 (28-36区域)", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.13, "• H: 点14-19 (40-48区域)", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.05, "• I: 点20-25 (52-60区域)", transform=ax4.transAxes, fontsize=10)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('independent_letters_design.png', dpi=300, bbox_inches='tight')
    print("✅ 独立字母设计可视化图已保存为: independent_letters_design.png")
    
    # 打印详细信息
    print("\n📊 独立字母TACHIN路径详细信息:")
    print("-" * 50)
    print(f"总点数: {len(points)}")
    print(f"起点: {points[0]}")
    print(f"终点: {points[-1]}")
    
    print("\n各字母独立分布:")
    for letter, start, end in letter_ranges:
        count = end - start + 1
        print(f"  {letter}: 点{start}-{end} ({count}个点)")
    
    print("\n💡 独立字母设计优势:")
    print("- 每个字母独立绘制，形状清晰")
    print("- 字母间无强制连接，更灵活")
    print("- 通过序号引导绘制顺序")
    print("- 适合游戏中的分步引导")

if __name__ == "__main__":
    visualize_independent_letters() 