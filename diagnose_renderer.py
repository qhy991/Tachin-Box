#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断渲染器问题
"""

import sys
import os
import traceback

# 添加路径
sys.path.append(os.path.dirname(__file__))

def diagnose_renderer():
    """诊断渲染器问题"""
    print("🔍 开始诊断渲染器问题...")
    print("=" * 50)
    
    # 1. 检查基本依赖
    print("1. 检查基本依赖...")
    try:
        import numpy as np
        print("✅ numpy 已安装")
    except ImportError as e:
        print(f"❌ numpy 导入失败: {e}")
        return False
    
    try:
        import matplotlib
        print(f"✅ matplotlib 已安装 (版本: {matplotlib.__version__})")
    except ImportError as e:
        print(f"❌ matplotlib 导入失败: {e}")
        return False
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 已安装")
    except ImportError as e:
        print(f"❌ PyQt5 导入失败: {e}")
        return False
    
    # 2. 检查渲染器模块
    print("\n2. 检查渲染器模块...")
    try:
        from interfaces.ordinary.BoxGame.box_game_renderer_optimized import BoxGameRendererOptimized
        print("✅ 优化渲染器模块导入成功")
    except ImportError as e:
        print(f"❌ 优化渲染器模块导入失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False
    
    # 3. 检查渲染器类
    print("\n3. 检查渲染器类...")
    try:
        renderer = BoxGameRendererOptimized()
        print("✅ 渲染器实例创建成功")
    except Exception as e:
        print(f"❌ 渲染器实例创建失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False
    
    # 4. 检查渲染器组件
    print("\n4. 检查渲染器组件...")
    try:
        if hasattr(renderer, 'game_renderer'):
            print("✅ 游戏渲染器组件存在")
        else:
            print("❌ 游戏渲染器组件不存在")
            return False
        
        if hasattr(renderer, 'pressure_canvas'):
            print("✅ 压力画布组件存在")
        else:
            print("❌ 压力画布组件不存在")
            return False
        
        if hasattr(renderer, 'pressure_renderer_thread'):
            print("✅ 压力渲染线程存在")
        else:
            print("❌ 压力渲染线程不存在")
            return False
        
    except Exception as e:
        print(f"❌ 检查渲染器组件失败: {e}")
        return False
    
    # 5. 测试渲染器方法
    print("\n5. 测试渲染器方法...")
    try:
        renderer.start_rendering()
        print("✅ 渲染器启动成功")
        
        import numpy as np
        test_pressure = np.random.rand(64, 64) * 0.1
        renderer.update_pressure_data(test_pressure)
        print("✅ 压力数据更新成功")
        
        test_state = {
            'is_contact': True,
            'is_sliding': False,
            'current_cop': (32, 32),
            'box_position': np.array([32.0, 32.0]),
            'box_target_position': np.array([35.0, 35.0])
        }
        renderer.update_game_state(test_state)
        print("✅ 游戏状态更新成功")
        
        renderer.stop_rendering()
        print("✅ 渲染器停止成功")
        
    except Exception as e:
        print(f"❌ 测试渲染器方法失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("✅ 渲染器诊断完成，所有检查都通过")
    return True

if __name__ == "__main__":
    diagnose_renderer() 