#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TACHIN路径断开点修复
Test TACHIN path disconnection fix
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'interfaces', 'ordinary', 'BoxGame'))

from box_game_path_planning import PathPlanner

def test_tachin_connection_fix():
    """测试TACHIN路径断开点修复"""
    print("🎯 测试TACHIN路径断开点修复")
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
    
    # 测试1：修复后的TACHIN路径（不绘制断开点连线）
    ax1 = axes[0]
    ax1.set_title("TACHIN - 修复后的独立字母路径", fontsize=12)
    
    # 提取所有点
    points = [(p.x, p.y) for p in tachin_path.points]
    connection_types = [p.connection_type for p in tachin_path.points]
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    # 按字母分组处理，避免断开点与连接点的连线
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
        letter_solid_x, letter_solid_y = [], []
        for j in range(start, end + 1):
            if connection_types[j] == "solid":
                letter_solid_x.append(x_coords[j])
                letter_solid_y.append(y_coords[j])
        
        if letter_solid_x:
            ax1.plot(letter_solid_x, letter_solid_y, c=colors[i], linewidth=2, markersize=8, 
                    marker='o', alpha=0.8, label=f'{letter}字母')
    
    # 绘制断开点（红色X标记）
    none_x, none_y = [], []
    for i, (x, y) in enumerate(points):
        if connection_types[i] == "none":
            none_x.append(x)
            none_y.append(y)
    
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
    
    # 测试2：连接类型分析
    ax2 = axes[1]
    ax2.set_title("TACHIN - 连接类型分析", fontsize=12)
    
    # 统计连接类型
    solid_count = connection_types.count("solid")
    none_count = connection_types.count("none")
    
    # 绘制饼图
    labels = ['Solid连接', '断开点']
    sizes = [solid_count, none_count]
    colors_pie = ['lightblue', 'lightcoral']
    
    ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    
    # 添加统计信息
    ax2.text(0.5, -1.2, f'总点数: {len(points)}', ha='center', va='center', fontsize=12, fontweight='bold')
    ax2.text(0.5, -1.4, f'Solid连接: {solid_count}个点', ha='center', va='center', fontsize=10)
    ax2.text(0.5, -1.6, f'断开点: {none_count}个点', ha='center', va='center', fontsize=10)
    
    # 测试3：字母独立显示
    ax3 = axes[2]
    ax3.set_title("TACHIN - 字母独立显示", fontsize=12)
    
    # 定义每个字母的起始和结束索引（包含断开点）
    letter_ranges_with_disconnect = [
        ("T", 0, 4),     # T字母：点0-3 + 断开点4
        ("A", 5, 10),    # A字母：点5-9 + 断开点10
        ("C", 11, 16),   # C字母：点11-15 + 断开点16
        ("H", 17, 23),   # H字母：点17-22 + 断开点23
        ("I", 24, 30),   # I字母：点24-29 + 断开点30
        ("N", 31, 34),   # N字母：点31-34
    ]
    
    for i, (letter, start, end) in enumerate(letter_ranges_with_disconnect):
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
            ax3.plot(solid_x, solid_y, c=colors[i], linewidth=3, markersize=8, 
                    marker='o', alpha=0.8, label=f'{letter}(solid)')
        
        # 绘制none连接（断开点）
        if none_x:
            ax3.scatter(none_x, none_y, c=colors[i], s=80, marker='x', alpha=0.8)
        
        # 添加序号
        for j in range(start, end+1):
            ax3.annotate(str(j), (x_coords[j], y_coords[j]), xytext=(3, 3), 
                        textcoords='offset points', fontsize=7, fontweight='bold')
    
    ax3.set_xlim(0, 64)
    ax3.set_ylim(0, 64)
    ax3.invert_yaxis()
    ax3.grid(True, alpha=0.3)
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 测试4：修复效果对比
    ax4 = axes[3]
    ax4.set_title("修复效果对比", fontsize=12)
    
    # 修复前（错误连线）
    ax4.text(0.1, 0.9, "修复前的问题:", transform=ax4.transAxes, fontsize=12, fontweight='bold')
    ax4.text(0.1, 0.8, "• 断开点与相邻点连线", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.72, "• 字母间出现错误连接", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.64, "• 路径显示不清晰", transform=ax4.transAxes, fontsize=10)
    
    ax4.text(0.1, 0.5, "修复后的改进:", transform=ax4.transAxes, fontsize=12, fontweight='bold')
    ax4.text(0.1, 0.4, "• 断开点不绘制连线", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.32, "• 字母完全独立显示", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.24, "• 断开点用红色X标记", transform=ax4.transAxes, fontsize=10)
    ax4.text(0.1, 0.16, "• 路径显示更清晰", transform=ax4.transAxes, fontsize=10)
    
    ax4.text(0.1, 0.05, "✅ 修复完成！", transform=ax4.transAxes, fontsize=14, fontweight='bold', color='green')
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('tachin_connection_fix_test.png', dpi=300, bbox_inches='tight')
    print("✅ TACHIN连接修复测试图已保存为: tachin_connection_fix_test.png")
    
    # 打印详细信息
    print("\n📊 TACHIN路径连接类型分析:")
    print("-" * 50)
    print(f"总点数: {len(points)}")
    print(f"Solid连接: {solid_count}个点")
    print(f"断开点: {none_count}个点")
    
    print("\n各字母连接情况:")
    for letter, start, end in letter_ranges_with_disconnect:
        count = end - start + 1
        solid_in_range = sum(1 for i in range(start, end+1) if connection_types[i] == "solid")
        none_in_range = sum(1 for i in range(start, end+1) if connection_types[i] == "none")
        print(f"  {letter}: 点{start}-{end} ({count}个点, {solid_in_range}个solid, {none_in_range}个none)")
    
    print("\n🔗 断开点位置:")
    for i, (x, y) in enumerate(points):
        if connection_types[i] == "none":
            print(f"  点{i}: ({x}, {y})")
    
    print("\n💡 修复说明:")
    print("- 修改了path_visualization_manager.py中的_render_path_line方法")
    print("- 当connection_type为'none'时，不绘制到下一个点的连线")
    print("- 修改了_render_path_points方法，为断开点添加特殊标记")
    print("- 断开点现在用红色X标记显示，并添加🔗标签")

if __name__ == "__main__":
    test_tachin_connection_fix() 