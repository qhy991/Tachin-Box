#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化基于simple_test.py参考的TACHIN路径设计
Visualize reference-based TACHIN path design
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner

def visualize_reference_based_tachin():
    """可视化基于参考的TACHIN路径设计"""
    print("🎯 可视化基于simple_test.py参考的TACHIN路径设计")
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
    ax1.set_title("TACHIN - 基于参考的独立字母路径", fontsize=12)
    
    # 提取所有点
    points = [(p.x, p.y) for p in tachin_path.points]
    connection_types = [p.connection_type for p in tachin_path.points]
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    # 分别绘制solid和none连接
    solid_x, solid_y = [], []
    none_x, none_y = [], []
    
    # 按字母分组处理，避免断开点与连接点的连线
    letter_ranges = [
        ("T", 0, 3),     # T字母：点0-3（不含断开点）
        ("A", 5, 9),     # A字母：点5-9（不含断开点）
        ("C", 11, 15),   # C字母：点11-15（不含断开点）
        ("H", 17, 22),   # H字母：点17-22（不含断开点）
        ("I", 24, 29),   # I字母：点24-29（不含断开点）
        ("N", 31, 34),   # N字母：点31-34
    ]
    
    # 分别收集每个字母的solid点
    for letter, start, end in letter_ranges:
        for i in range(start, end + 1):
            if connection_types[i] == "solid":
                solid_x.append(x_coords[i])
                solid_y.append(y_coords[i])
    
    # 收集所有断开点
    for i, (x, y) in enumerate(points):
        if connection_types[i] == "none":
            none_x.append(x)
            none_y.append(y)
    
    # 绘制solid连接 - 按字母分组绘制，避免跨字母连线
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
    for i, (letter, start, end) in enumerate(letter_ranges):
        letter_solid_x, letter_solid_y = [], []
        for j in range(start, end + 1):
            if connection_types[j] == "solid":
                letter_solid_x.append(x_coords[j])
                letter_solid_y.append(y_coords[j])
        
        if letter_solid_x:
            ax1.plot(letter_solid_x, letter_solid_y, c=colors[i], linewidth=2, markersize=8, 
                    marker='o', alpha=0.8, label=f'{letter}字母')
    
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
    
    # 测试2：按字母分组显示（基于参考设计）
    ax2 = axes[1]
    ax2.set_title("TACHIN - 基于参考的字母独立绘制", fontsize=12)
    
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
    
    # 测试3：对比：参考设计 vs 原始设计
    ax3 = axes[2]
    ax3.set_title("参考设计 vs 原始设计", fontsize=12)
    
    # 参考设计（按字母分组绘制，避免跨字母连线）
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
    for i, (letter, start, end) in enumerate(letter_ranges):
        letter_solid_x, letter_solid_y = [], []
        for j in range(start, end + 1):
            if connection_types[j] == "solid":
                letter_solid_x.append(x_coords[j])
                letter_solid_y.append(y_coords[j])
        
        if letter_solid_x:
            ax3.plot(letter_solid_x, letter_solid_y, c=colors[i], linewidth=2, markersize=6, 
                    marker='o', alpha=0.8, label=f'{letter}(参考设计)')
    
    # 绘制断开点
    if none_x:
        ax3.scatter(none_x, none_y, c='red', s=80, marker='x', alpha=0.8, label='断开点')
    
    # 原始设计（红色虚线）- 假设的原始版本
    original_points = [
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
    
    orig_x = [p[0] for p in original_points]
    orig_y = [p[1] for p in original_points]
    ax3.plot(orig_x, orig_y, 'r--o', linewidth=1, markersize=4, alpha=0.6, label='连接设计(30点)')
    
    ax3.set_xlim(0, 64)
    ax3.set_ylim(0, 64)
    ax3.invert_yaxis()
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 测试4：设计分析
    ax4 = axes[3]
    ax4.set_title("基于参考的设计分析", fontsize=12)
    
    # 显示设计特点
    ax4.text(0.1, 0.9, "基于参考的设计特点:", transform=ax4.transAxes, fontsize=12, fontweight='bold')
    ax4.text(0.1, 0.8, "• 基于simple_test.py参考", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.72, "• 字母宽度6单位，高度40单位", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.64, "• 字母间距2单位", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.56, "• 完全在64x64范围内", transform=ax4.transAxes, fontsize=10)
    
    ax4.text(0.1, 0.45, "字母分布:", transform=ax4.transAxes, fontsize=11, fontweight='bold')
    ax4.text(0.1, 0.37, "• T: 点0-3 + 断开点4 (2-8区域)", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.29, "• A: 点5-9 + 断开点10 (12-18区域)", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.21, "• C: 点11-15 + 断开点16 (18-24区域)", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.13, "• H: 点17-22 + 断开点23 (30-36区域)", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.05, "• I: 点24-29 + 断开点30 (42-46区域)", transform=ax4.transAxes, fontsize=10)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('reference_based_tachin_design.png', dpi=300, bbox_inches='tight')
    print("✅ 基于参考的TACHIN设计可视化图已保存为: reference_based_tachin_design.png")
    
    # 打印详细信息
    print("\n📊 基于参考的TACHIN路径详细信息:")
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
    
    print("\n💡 基于参考的设计优势:")
    print("- 基于simple_test.py的简洁设计")
    print("- 字母宽度和间距更合理")
    print("- 完全在64x64范围内")
    print("- 保持字母清晰度和独立性")

if __name__ == "__main__":
    visualize_reference_based_tachin() 