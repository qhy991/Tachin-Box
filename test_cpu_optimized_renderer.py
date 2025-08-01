# -*- coding: utf-8 -*-
"""
CPU优化渲染器测试脚本
Test script for CPU optimized renderer
"""

import sys
import os
import numpy as np
import time
from PyQt5.QtWidgets import QApplication

# 添加路径
sys.path.append(os.path.dirname(__file__))

def test_cpu_optimized_renderer():
    """测试CPU优化渲染器"""
    print("🚀 测试CPU优化渲染器")
    print("=" * 50)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    try:
        # 导入主窗口
        from box_game_app_optimized import BoxGameMainWindow
        
        # 创建主窗口
        main_window = BoxGameMainWindow()
        main_window.show()
        
        print("✅ CPU优化渲染器测试已启动")
        print("📊 性能优化特性:")
        print("  - 对象缓存和复用")
        print("  - 智能帧跳跃")
        print("  - 数据变化检测")
        print("  - 简化预处理")
        print("  - 保持3D渲染")
        print("  - 引导模式控制")
        print("  - 自适应性能调整")
        print("\n💡 使用说明:")
        print("  1. 连接传感器开始测试")
        print("  2. 观察控制台输出的性能数据")
        print("  3. 启用路径模式测试引导模式")
        print("  4. 按 'P' 键查看性能汇总")
        print("  5. 按 'H' 键查看帮助信息")
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_performance_modes():
    """测试不同性能模式"""
    print("🧪 测试性能模式")
    print("=" * 30)
    
    app = QApplication(sys.argv)
    
    try:
        from box_game_app_optimized import BoxGameMainWindow
        
        main_window = BoxGameMainWindow()
        
        # 测试不同性能模式
        modes = ["CPU优化", "标准", "高性能"]
        
        for mode in modes:
            print(f"\n🎯 测试模式: {mode}")
            if main_window.renderer:
                main_window.renderer.set_performance_mode(mode)
                stats = main_window.renderer.get_performance_stats()
                print(f"  - 目标FPS: {stats['target_fps']:.1f}")
                print(f"  - 跳帧率: {stats['frame_skip_rate']}")
                print(f"  - 性能模式: {stats['performance_mode']}")
        
        print("\n✅ 性能模式测试完成")
        
    except Exception as e:
        print(f"❌ 性能模式测试失败: {e}")

def test_guide_mode():
    """测试引导模式"""
    print("🗺️ 测试引导模式")
    print("=" * 30)
    
    app = QApplication(sys.argv)
    
    try:
        from box_game_app_optimized import BoxGameMainWindow
        
        main_window = BoxGameMainWindow()
        
        if main_window.renderer:
            # 测试引导模式启用
            print("🔍 测试引导模式启用...")
            main_window.renderer.set_guide_mode(True)
            print(f"  引导模式状态: {main_window.renderer.is_guide_mode_enabled()}")
            print(f"  可切换到2D: {main_window.renderer.can_switch_to_2d()}")
            
            # 测试引导模式禁用
            print("\n🔍 测试引导模式禁用...")
            main_window.renderer.set_guide_mode(False)
            print(f"  引导模式状态: {main_window.renderer.is_guide_mode_enabled()}")
            print(f"  可切换到2D: {main_window.renderer.can_switch_to_2d()}")
        
        print("\n✅ 引导模式测试完成")
        
    except Exception as e:
        print(f"❌ 引导模式测试失败: {e}")

def benchmark_renderer():
    """基准测试渲染器性能"""
    print("📊 渲染器性能基准测试")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    try:
        from box_game_app_optimized import BoxGameMainWindow
        
        main_window = BoxGameMainWindow()
        
        if main_window.renderer:
            # 生成测试数据
            test_pressure_data = np.random.random((64, 64)) * 0.01
            
            # 测试渲染性能
            print("🎨 测试渲染性能...")
            start_time = time.time()
            
            for i in range(100):
                main_window.renderer.update_pressure_data(test_pressure_data)
                main_window.renderer.optimized_update_display()
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / 100 * 1000  # 转换为毫秒
            
            print(f"  总时间: {total_time:.3f}秒")
            print(f"  平均渲染时间: {avg_time:.2f}ms")
            print(f"  理论FPS: {1000/avg_time:.1f}")
            
            # 获取性能统计
            stats = main_window.renderer.get_performance_stats()
            print(f"  缓存命中率: {stats['cache_hit_rate']:.2%}")
            print(f"  跳帧率: {stats['frame_skip_rate']}")
        
        print("\n✅ 基准测试完成")
        
    except Exception as e:
        print(f"❌ 基准测试失败: {e}")

if __name__ == "__main__":
    print("🚀 CPU优化渲染器测试套件")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "performance":
            test_performance_modes()
        elif test_type == "guide":
            test_guide_mode()
        elif test_type == "benchmark":
            benchmark_renderer()
        else:
            print("❌ 未知测试类型")
            print("可用测试类型: performance, guide, benchmark")
    else:
        # 默认运行完整测试
        test_cpu_optimized_renderer() 