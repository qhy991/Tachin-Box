#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在 64x64 的区域内绘制 "TACHIN" 的字样，每个字母独立绘制。
Draw the word "TACHIN" within a 64x64 area, with each letter as a separate path.
"""

import matplotlib.pyplot as plt
import numpy as np

def draw_tachin_in_64x64_area():
    """
    在 64x64 的画布上绘制 "TACHIN" 所有字母，每个字母的路径独立。
    """
    print("🎯 在 64x64 区域内绘制 TACHIN 字样...")
    print("=" * 50)

    # 1. 为 64x64 区域重新定义字母坐标
    # 每个字母宽度约为8个单位，高度约为40个单位
    letters = {
        'T': [ (0, 12), (8, 12), (4, 12), (4, 52) ],
        'A': [ (0, 52), (4, 12), (8, 52), (6, 32), (2, 32) ],
        'C': [ (8, 17), (2, 12), (0, 32), (2, 52), (8, 47) ],
        'H': [ (0, 12), (0, 52), (0, 32), (8, 32), (8, 12), (8, 52) ],
        'I': [ (2, 12), (6, 12), (4, 12), (4, 52), (2, 52), (6, 52) ],
        'N': [ (0, 52), (0, 12), (8, 52), (8, 12) ]
    }

    # 2. 创建一个正方形的画布
    fig, ax = plt.subplots(figsize=(8, 8))

    # 3. 计算布局参数以在64x64区域内居中
    num_letters = len(letters)
    letter_width = 8  # 每个字母的基础宽度
    space_between_letters = 2 # 字母间的空隙
    
    # 每个字母占据的总宽度（实体+空隙）
    total_letter_span = letter_width + space_between_letters
    
    # 计算所有字母绘制出来所需的总宽度
    total_width_needed = (num_letters * letter_width) + ((num_letters - 1) * space_between_letters)
    
    # 计算起始点的 x 坐标，以实现水平居中
    x_offset_start = (64 - total_width_needed) / 2
    x_offset = x_offset_start

    # 使用 Colormap 生成一组漂亮的颜色
    colors = plt.cm.plasma(np.linspace(0, 1, num_letters))

    # 4. 循环遍历每个字母，计算新位置并独立绘制
    for i, (letter, points) in enumerate(letters.items()):
        # 计算带有水平偏移量的新坐标
        offset_points = [(p[0] + x_offset, p[1]) for p in points]
        
        # 提取 x 和 y 坐标
        x_coords = [p[0] for p in offset_points]
        y_coords = [p[1] for p in offset_points]

        # 独立绘制每个字母
        ax.plot(x_coords, y_coords,
                '-o',
                color=colors[i],
                linewidth=2.5,
                markersize=8,
                markerfacecolor='white',
                markeredgewidth=1.5,
                label=f"'{letter}'")

        # 更新下一个字母的起始偏移量
        x_offset += total_letter_span

    # 5. 设置图表的关键样式和范围
    ax.set_title("在 64x64 区域内绘制 TACHIN", fontsize=16, pad=20)
    
    # --- 这是实现您要求的核心步骤 ---
    ax.set_xlim(0, 64)
    ax.set_ylim(0, 64)
    # --------------------------------

    ax.invert_yaxis()  # 反转Y轴，使(0,0)在左上角
    ax.set_aspect('equal', adjustable='box') # 保持长宽比，防止字母变形
    ax.grid(True, linestyle=':', alpha=0.7)
    
    # 显示图例
    ax.legend(fontsize=10, title="字母")

    # 在坐标轴上显示刻度，以验证 64x64 的范围
    ax.set_xticks(np.arange(0, 65, 8))
    ax.set_yticks(np.arange(0, 65, 8))
    ax.tick_params(axis='both', which='major', labelsize=8)

    # 调整布局
    plt.tight_layout()
    
    # 保存图像
    output_filename = 'tachin_64x64_plot.png'
    plt.savefig(output_filename, dpi=300)
    
    print(f"✅ 图像绘制完成，已保存为: {output_filename}")
    # 显示图像
    plt.show()

if __name__ == "__main__":
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Heiti TC', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False

    # 执行主函数
    draw_tachin_in_64x64_area()