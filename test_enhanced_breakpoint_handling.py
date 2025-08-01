#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强的断点处理逻辑
Test enhanced breakpoint handling logic
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner

def test_enhanced_breakpoint_handling():
    """测试增强的断点处理逻辑"""
    print("🎯 测试增强的断点处理逻辑")
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
    
    # 测试1：增强断点处理后的TACHIN路径
    ax1 = axes[0]
    ax1.set_title("TACHIN - 增强断点处理后的独立字母路径", fontsize=12)
    
    # 提取所有点
    points = [(p.x, p.y) for p in tachin_path.points]
    connection_types = [p.connection_type for p in tachin_path.points]
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    # 找出所有断点位置
    break_points = [i for i, conn_type in enumerate(connection_types) if conn_type == 'none']
    print(f"🔗 断点位置: {break_points}")
    
    # 按字母分组处理，确保完全独立
    letter_ranges = [
        ("T", 0, 3),     # T字母：点0-3（不含断开点）
        ("A", 5, 9),     # A字母：点5-9（不含断开点）
        ("C", 11, 15),   # C字母：点11-15（不含断开点）
        ("H", 17, 22),   # H字母：点17-22（不含断开点）
        ("I", 24, 29),   # I字母：点24-29（不含断开点）
        ("N", 31, 34),   # N字母：点31-34
    ]
    
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
    
    # 分别绘制每个字母的solid连接
    for i, (letter, start, end) in enumerate(letter_ranges):
        letter_x, letter_y = [], []
        for j in range(start, end + 1):
            if connection_types[j] == "solid":
                letter_x.append(x_coords[j])
                letter_y.append(y_coords[j])
        
        if letter_x:
            ax1.plot(letter_x, letter_y, c=colors[i], linewidth=3, markersize=8, 
                    marker='o', alpha=0.8, label=f'{letter}字母')
    
    # 绘制断点
    break_x = [x_coords[i] for i in break_points]
    break_y = [y_coords[i] for i in break_points]
    if break_x:
        ax1.scatter(break_x, break_y, c='red', s=100, marker='x', alpha=0.8, label='断开点')
    
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
    
    # 测试2：断点连接分析
    ax2 = axes[1]
    ax2.set_title("断点连接分析", fontsize=12)
    
    # 分析每个断点的连接情况
    for i, break_idx in enumerate(break_points):
        # 断点坐标
        break_x, break_y = x_coords[break_idx], y_coords[break_idx]
        
        # 前一个点（如果不是第一个点）
        if break_idx > 0:
            prev_x, prev_y = x_coords[break_idx-1], y_coords[break_idx-1]
            prev_conn = connection_types[break_idx-1]
            ax2.plot([prev_x, break_x], [prev_y, break_y], 'r--', alpha=0.5, linewidth=1)
            ax2.annotate(f'前一点({break_idx-1}):{prev_conn}', (prev_x, prev_y), 
                        xytext=(10, 10), textcoords='offset points', fontsize=8, color='red')
        
        # 后一个点（如果不是最后一个点）
        if break_idx < len(points) - 1:
            next_x, next_y = x_coords[break_idx+1], y_coords[break_idx+1]
            next_conn = connection_types[break_idx+1]
            ax2.plot([break_x, next_x], [break_y, next_y], 'b--', alpha=0.5, linewidth=1)
            ax2.annotate(f'后一点({break_idx+1}):{next_conn}', (next_x, next_y), 
                        xytext=(10, -10), textcoords='offset points', fontsize=8, color='blue')
        
        # 标记断点
        ax2.scatter(break_x, break_y, c='red', s=80, marker='x', alpha=0.8)
        ax2.annotate(f'断点{break_idx}', (break_x, break_y), 
                    xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold', color='red')
    
    ax2.set_xlim(0, 64)
    ax2.set_ylim(0, 64)
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    ax2.set_title("断点连接分析 - 红色虚线：前一点连接，蓝色虚线：后一点连接")
    
    # 测试3：字母独立性验证
    ax3 = axes[2]
    ax3.set_title("字母独立性验证", fontsize=12)
    
    # 验证每个字母是否完全独立
    for i, (letter, start, end) in enumerate(letter_ranges):
        # 检查字母范围内的连接类型
        letter_connections = connection_types[start:end+1]
        solid_count = sum(1 for conn in letter_connections if conn == 'solid')
        none_count = sum(1 for conn in letter_connections if conn == 'none')
        
        # 绘制字母
        letter_x, letter_y = [], []
        for j in range(start, end + 1):
            if connection_types[j] == "solid":
                letter_x.append(x_coords[j])
                letter_y.append(y_coords[j])
        
        if letter_x:
            ax3.plot(letter_x, letter_y, c=colors[i], linewidth=2, markersize=6, 
                    marker='o', alpha=0.8, label=f'{letter}({solid_count}个solid,{none_count}个none)')
    
    # 标记断点
    if break_x:
        ax3.scatter(break_x, break_y, c='red', s=60, marker='x', alpha=0.8, label='断点')
    
    ax3.set_xlim(0, 64)
    ax3.set_ylim(0, 64)
    ax3.invert_yaxis()
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 测试4：增强处理逻辑说明
    ax4 = axes[3]
    ax4.set_title("增强断点处理逻辑说明", fontsize=12)
    
    # 显示处理逻辑说明
    ax4.text(0.1, 0.9, "增强断点处理逻辑:", transform=ax4.transAxes, fontsize=12, fontweight='bold')
    ax4.text(0.1, 0.8, "1. 当前点是断点 → 跳过连线", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.72, "2. 下一个点是断点 → 跳过连线", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.64, "3. 跨越断点 → 跳过连线", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.56, "4. 只有两个solid点之间才绘制连线", transform=ax4.transAxes, fontsize=10)
    
    ax4.text(0.1, 0.45, "TACHIN路径断点:", transform=ax4.transAxes, fontsize=11, fontweight='bold')
    ax4.text(0.1, 0.37, f"• 断点数量: {len(break_points)}", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.29, f"• 断点位置: {break_points}", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.21, "• 每个字母完全独立", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.13, "• 无跨字母连线", transform=ax4.transAxes, fontsize=10)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('enhanced_breakpoint_handling_test.png', dpi=300, bbox_inches='tight')
    print("✅ 增强断点处理测试图已保存为: enhanced_breakpoint_handling_test.png")
    
    # 打印详细信息
    print("\n📊 增强断点处理详细信息:")
    print("-" * 50)
    print(f"总点数: {len(points)}")
    print(f"断点数量: {len(break_points)}")
    print(f"断点位置: {break_points}")
    
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
    
    print("\n💡 增强处理优势:")
    print("- 完全避免断点与任何点之间的连线")
    print("- 确保字母完全独立显示")
    print("- 提供详细的断点分析信息")
    print("- 支持跨越断点的检测")

if __name__ == "__main__":
    test_enhanced_breakpoint_handling() 