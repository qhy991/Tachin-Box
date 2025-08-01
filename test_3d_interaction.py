# -*- coding: utf-8 -*-
"""
一个独立的PyQtGraph 3D绘图示例，
演示了如何使用视觉增强技术来显示数值范围很小的数据。
"""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
import pyqtgraph.opengl as gl

def main():
    # 1. 初始化Qt应用
    app = QApplication(sys.argv)

    # 2. 创建一个3D视图控件
    view = gl.GLViewWidget()
    view.setWindowTitle('3D视觉增强示例')
    view.setGeometry(100, 100, 800, 600)
    view.show()

    # 3. 生成模拟的原始数据
    # 假设这是你的传感器数据，X和Y轴范围是0-99，但Z轴（高度）的值非常小
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    
    # 一个中心有微小凸起的高斯函数，最大值仅为0.008
    raw_z_data = 0.008 * np.exp(-(X**2 + Y**2) / 4)
    print(f"原始数据Z轴范围: [{raw_z_data.min():.4f}, {raw_z_data.max():.4f}]")

    # --- 核心视觉增强逻辑 (基于你选择的代码) ---
    
    # 4. 定义数据的预期最大值
    max_value = 0.008

    # 5. 准备用于“着色”的数据
    # 我们将数据裁剪到预期范围内，以确保颜色映射的稳定性
    clipped_for_color = np.clip(raw_z_data, 0.0, max_value)

    # 6. 准备用于“高度”的数据 (进行非线性放大)
    #    a. (clipped_for_color / max_value): 将数据归一化到 0-1 范围
    #    b. np.power(..., 0.3): 应用立方根变换，这会不成比例地抬高较小的值，让图形轮廓更清晰
    #    c. * max_value * 50: 将变换后的数据重新缩放到一个较大的范围，这里是原始最大值的50倍
    enhanced_data = np.power(clipped_for_color / max_value, 0.3) * max_value * 900
    print(f"增强后数据Z轴范围: [{enhanced_data.min():.4f}, {enhanced_data.max():.4f}]")

    # 7. 根据“原始”数据生成颜色
    # 这一步确保了虽然图形的高度被夸大了，但颜色依然忠实地反映了原始数据的真实大小
    color_map = pg.colormap.get('plasma')
    colors = color_map.map(clipped_for_color / max_value, mode='float')
    
    # --- 渲染 ---

    # 8. 创建3D表面图元
    #    - z=enhanced_data: 使用被夸大高度的数据来构建几何形状
    #    - colors=colors: 使用基于原始数据生成的颜色来着色
    surface = gl.GLSurfacePlotItem(
        z=enhanced_data,
        colors=colors.reshape(raw_z_data.shape + (4,)),
        shader='shaded',
        smooth=True
    )

    # 9. 创建一个参考网格
    grid = gl.GLGridItem()
    grid.scale(10, 10, 1) # 缩放网格以匹配数据平面大小
    
    # 10. 将图元添加到视图中
    view.addItem(grid)
    view.addItem(surface)
    
    # 11. 设置一个合适的相机初始视角
    view.setCameraPosition(distance=100, elevation=30, azimuth=45)

    # 12. 启动应用
    print("✅ 示例已启动。请使用鼠标拖拽旋转和缩放。")
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
