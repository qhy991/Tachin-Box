#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过连线方式单独绘制 "TACHIN" 的每个字母。
Draw each letter of "TACHIN" separately by connecting points.
"""

import matplotlib.pyplot as plt
import numpy as np

def draw_tachin_letters_separately():
    """
    为 "TACHIN" 的每个字母创建独立的连线图。
    Creates individual plots for each letter of "TACHIN".
    """
    print("🎯 开始绘制 TACHIN 的每个字母...")
    print("=" * 50)

    # 定义每个字母的点序列
    # 每组点都经过精心设计，以便通过单次连线绘制出清晰的字母形状
    letters = {
        'T': [
            (10, 20), (30, 20), # 绘制顶部横线
            (20, 20), (20, 40)  # 回到中点并绘制竖线
        ],
        'A': [
            (10, 40), (20, 20), (30, 40), # 绘制两条斜线
            (25, 30), (15, 30)  # 回到斜线上并绘制中间的横线
        ],
        'C': [
            (30, 25), (15, 20), (10, 30), (15, 40), (30, 35) # 用五点近似绘制曲线
        ],
        'H': [
            (10, 20), (10, 40), # 绘制左侧竖线
            (10, 30), (30, 30), # 绘制中间横线
            (30, 20), (30, 40)  # 绘制右侧竖线
        ],
        'I': [
            (15, 20), (25, 20), # 顶部横线
            (20, 20), (20, 40), # 竖线
            (15, 40), (25, 40)  # 底部横线
        ],
        'N': [
            (10, 40), (10, 20), # 左侧竖线
            (30, 40),          # 对角线
            (30, 20)           # 右侧竖线
        ]
    }

    # 创建一个 2x3 的子图网格
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    # 将二维子图数组展平为一维，方便遍历
    axes = axes.flatten()

    # 遍历每个字母并进行绘制
    for i, (letter, points) in enumerate(letters.items()):
        ax = axes[i]
        
        # 提取 x 和 y 坐标
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

        # 绘制连线路径
        ax.plot(x_coords, y_coords, 'b-o', linewidth=2.5, markersize=10, markerfacecolor='lightblue')

        # 标记起点和终点
        ax.plot(x_coords[0], y_coords[0], 'gs', markersize=12, label=f'起点 ({points[0]})')
        ax.plot(x_coords[-1], y_coords[-1], 'rs', markersize=12, label=f'终点 ({points[-1]})')
        
        # 设置子图标题和样式
        ax.set_title(f"字母 '{letter}' 的绘制路径", fontsize=14)
        ax.set_xlim(0, 40)
        ax.set_ylim(0, 50)
        ax.invert_yaxis()  # 反转Y轴，使(0,0)在左上角
        ax.set_aspect('equal', adjustable='box') # 保证x和y轴比例相同，字母不会变形
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        
        # 在每个点旁边显示其坐标，方便调试
        for j, (x, y) in enumerate(points):
            ax.annotate(f'P{j}', (x, y), xytext=(5, -10), textcoords='offset points', fontsize=9, color='gray')


    # 调整整体布局，防止标题重叠
    plt.tight_layout(pad=3.0)
    
    # 保存图像
    output_filename = 'tachin_letters_plot.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    
    print(f"✅ 所有字母绘制完成，图像已保存为: {output_filename}")
    # 显示图像
    plt.show()


if __name__ == "__main__":
    # 解决中文显示问题（在支持中文的系统和环境中）
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Heiti TC', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    # 执行主函数
    draw_tachin_letters_separately()