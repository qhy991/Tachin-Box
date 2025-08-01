#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化新的TACHIN路径设计
Visualize the new TACHIN path design
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner

def visualize_new_tachin():
    """可视化新的TACHIN路径设计"""
    print("🎯 可视化新的TACHIN路径设计")
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
    
    # 测试1：完整TACHIN路径
    ax1 = axes[0]
    ax1.set_title("TACHIN - 完整路径（新设计）", fontsize=12)
    
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
    
    # 测试2：按字母分组显示
    ax2 = axes[1]
    ax2.set_title("TACHIN - 按字母分组", fontsize=12)
    
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
    
    # 测试3：对比：新设计 vs 原设计思路
    ax3 = axes[2]
    ax3.set_title("新设计 vs 原设计思路", fontsize=12)
    
    # 新设计（蓝色）
    ax3.plot(x_coords, y_coords, 'b-o', linewidth=2, markersize=6, alpha=0.8, label='新设计(30点)')
    
    # 原设计思路（红色虚线）- 基于之前的复杂设计
    original_points = [
        # T字母（复杂版）
        (8, 30), (12, 30), (16, 30), (14, 32), (12, 30), (12, 50),
        # A字母（复杂版）
        (18, 35), (20, 50), (24, 30), (22, 35), (20, 50), (28, 50), (24, 40),
        # C字母（复杂版）
        (30, 35), (32, 30), (32, 40), (32, 50), (36, 50),
        # H字母（复杂版）
        (38, 35), (40, 50), (40, 40), (40, 30), (44, 40), (48, 30), (48, 40), (48, 50),
        # I字母（复杂版）
        (50, 35), (52, 50), (52, 40), (52, 30),
        # N字母（复杂版）
        (54, 35), (56, 50), (56, 40), (56, 30), (60, 50), (60, 40), (60, 30)
    ]
    
    orig_x = [p[0] for p in original_points]
    orig_y = [p[1] for p in original_points]
    ax3.plot(orig_x, orig_y, 'r--o', linewidth=1, markersize=4, alpha=0.6, label='原设计(37点)')
    
    ax3.set_xlim(0, 64)
    ax3.set_ylim(0, 64)
    ax3.invert_yaxis()
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 测试4：设计分析
    ax4 = axes[3]
    ax4.set_title("新设计分析", fontsize=12)
    
    # 显示设计特点
    ax4.text(0.1, 0.9, "新设计特点:", transform=ax4.transAxes, fontsize=12, fontweight='bold')
    ax4.text(0.1, 0.8, "• 基于test_path_with_returns.py设计", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.72, "• 每个字母独立清晰", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.64, "• 减少不必要的回头路", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.56, "• 连线更平滑自然", transform=ax4.transAxes, fontsize=10)
    
    ax4.text(0.1, 0.45, "字母设计:", transform=ax4.transAxes, fontsize=11, fontweight='bold')
    ax4.text(0.1, 0.37, "• T: 横线+竖线", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.29, "• A: 两条斜线+横线", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.21, "• C: 五点曲线", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.13, "• H: 左竖线+横线+右竖线", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.05, "• I: 顶部横线+竖线+底部横线", transform=ax4.transAxes, fontsize=10)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('new_tachin_design.png', dpi=300, bbox_inches='tight')
    print("✅ 新设计可视化图已保存为: new_tachin_design.png")
    
    # 打印详细信息
    print("\n📊 新TACHIN路径详细信息:")
    print("-" * 50)
    print(f"总点数: {len(points)}")
    print(f"起点: {points[0]}")
    print(f"终点: {points[-1]}")
    
    print("\n各字母点分布:")
    for letter, start, end in letter_ranges:
        count = end - start + 1
        print(f"  {letter}: 点{start}-{end} ({count}个点)")
    
    print("\n💡 新设计优势:")
    print("- 基于test_path_with_returns.py的简洁设计")
    print("- 每个字母形状清晰可识别")
    print("- 连线路径更自然流畅")
    print("- 适合游戏使用")

if __name__ == "__main__":
    visualize_new_tachin() 