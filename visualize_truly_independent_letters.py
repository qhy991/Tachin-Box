#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化真正的独立字母TACHIN路径设计
Visualize truly independent letters TACHIN path design
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner

def visualize_truly_independent_letters():
    """可视化真正的独立字母TACHIN路径设计"""
    print("🎯 可视化真正的独立字母TACHIN路径设计")
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
    
    # 测试1：完整TACHIN路径（显示断开连接）
    ax1 = axes[0]
    ax1.set_title("TACHIN - 真正独立字母路径", fontsize=12)
    
    # 提取所有点
    points = [(p.x, p.y) for p in tachin_path.points]
    connection_types = [p.connection_type for p in tachin_path.points]
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
        ax1.plot(solid_x, solid_y, 'b-o', linewidth=2, markersize=8, alpha=0.8, label='字母内部连接')
    
    # 绘制none连接（断开点）
    if none_x:
        ax1.scatter(none_x, none_y, c='red', s=100, marker='x', alpha=0.8, label='断开连接点')
    
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
    
    # 测试2：按字母分组显示（真正独立）
    ax2 = axes[1]
    ax2.set_title("TACHIN - 字母真正独立绘制", fontsize=12)
    
    # 定义每个字母的起始和结束索引（包含断开点）
    letter_ranges = [
        ("T", 0, 4),     # T字母：点0-3 + 断开点4
        ("A", 5, 10),    # A字母：点5-9 + 断开点10
        ("C", 11, 16),   # C字母：点11-15 + 断开点16
        ("H", 17, 23),   # H字母：点17-22 + 断开点23
        ("I", 24, 30),   # I字母：点24-29 + 断开点30
        ("N", 31, 34),   # N字母：点31-34
    ]
    
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
    
    for i, (letter, start, end) in enumerate(letter_ranges):
        letter_x = x_coords[start:end+1]
        letter_y = y_coords[start:end+1]
        letter_connections = connection_types[start:end+1]
        
        # 分别绘制solid和none
        solid_x, solid_y = [], []
        none_x, none_y = [], []
        
        for j, (x, y, conn_type) in enumerate(zip(letter_x, letter_y, letter_connections)):
            if conn_type == "solid":
                solid_x.append(x)
                solid_y.append(y)
            else:
                none_x.append(x)
                none_y.append(y)
        
        # 绘制solid连接
        if solid_x:
            ax2.plot(solid_x, solid_y, c=colors[i], linewidth=3, markersize=8, 
                    marker='o', alpha=0.8, label=f'{letter}(solid)')
        
        # 绘制none连接（断开点）
        if none_x:
            ax2.scatter(none_x, none_y, c=colors[i], s=80, marker='x', alpha=0.8)
        
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
    
    # 独立字母设计（蓝色，显示断开）
    ax3.plot(solid_x, solid_y, 'b-o', linewidth=2, markersize=6, alpha=0.8, label='独立字母(35点)')
    if none_x:
        ax3.scatter(none_x, none_y, c='red', s=80, marker='x', alpha=0.8, label='断开点')
    
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
    ax4.set_title("真正独立字母设计分析", fontsize=12)
    
    # 显示设计特点
    ax4.text(0.1, 0.9, "真正独立字母设计特点:", transform=ax4.transAxes, fontsize=12, fontweight='bold')
    ax4.text(0.1, 0.8, "• 每个字母独立绘制", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.72, "• 字母间有断开点", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.64, "• 通过序号引导顺序", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.56, "• 无强制连接线", transform=ax4.transAxes, fontsize=10)
    
    ax4.text(0.1, 0.45, "字母分布:", transform=ax4.transAxes, fontsize=11, fontweight='bold')
    ax4.text(0.1, 0.37, "• T: 点0-3 + 断开点4", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.29, "• A: 点5-9 + 断开点10", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.21, "• C: 点11-15 + 断开点16", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.13, "• H: 点17-22 + 断开点23", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.05, "• I: 点24-29 + 断开点30", transform=ax4.transAxes, fontsize=10)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('truly_independent_letters_design.png', dpi=300, bbox_inches='tight')
    print("✅ 真正独立字母设计可视化图已保存为: truly_independent_letters_design.png")
    
    # 打印详细信息
    print("\n📊 真正独立字母TACHIN路径详细信息:")
    print("-" * 50)
    print(f"总点数: {len(points)}")
    print(f"起点: {points[0]}")
    print(f"终点: {points[-1]}")
    
    print(f"\n连接类型统计:")
    solid_count = connection_types.count("solid")
    none_count = connection_types.count("none")
    print(f"  solid连接: {solid_count}个点")
    print(f"  none断开: {none_count}个点")
    
    print("\n各字母独立分布:")
    for letter, start, end in letter_ranges:
        count = end - start + 1
        solid_in_range = sum(1 for i in range(start, end+1) if connection_types[i] == "solid")
        none_in_range = sum(1 for i in range(start, end+1) if connection_types[i] == "none")
        print(f"  {letter}: 点{start}-{end} ({count}个点, {solid_in_range}个solid, {none_in_range}个none)")
    
    print("\n💡 真正独立字母设计优势:")
    print("- 每个字母独立绘制，形状清晰")
    print("- 字母间有明确的断开点")
    print("- 通过序号引导绘制顺序")
    print("- 无强制连接线，更灵活")

if __name__ == "__main__":
    visualize_truly_independent_letters() 