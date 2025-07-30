#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接触检测阈值调整使用示例
Example usage for contact detection threshold adjustment
"""

import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from box_game_app_optimized import BoxGameMainWindow, BoxGameCoreOptimized

def example_contact_threshold_adjustment():
    """接触检测阈值调整示例"""
    
    print("🎯 接触检测阈值调整示例")
    print("=" * 50)
    
    # 创建游戏核心
    game_core = BoxGameCoreOptimized()
    
    # 生成测试数据
    test_data = np.random.exponential(0.001, (64, 64))
    test_data[25:35, 25:35] += 0.003  # 添加接触区域
    
    print(f"📊 测试数据: 最大压力={np.max(test_data):.6f}, 平均压力={np.mean(test_data):.6f}")
    
    # 示例1: 获取当前配置
    print("\n1️⃣ 获取当前配置:")
    config_info = game_core.get_contact_detection_info()
    print(f"   压力阈值: {config_info['pressure_threshold']:.6f}")
    print(f"   接触面积阈值: {config_info['contact_area_threshold']}")
    
    # 示例2: 测试当前设置
    print("\n2️⃣ 测试当前设置:")
    contact_detected = game_core.detect_contact(test_data)
    print(f"   接触检测结果: {'✅ 检测到' if contact_detected else '❌ 未检测到'}")
    
    # 示例3: 调整灵敏度
    print("\n3️⃣ 调整灵敏度:")
    sensitivity_levels = ['very_high', 'high', 'medium', 'low', 'very_low']
    
    for level in sensitivity_levels:
        print(f"\n   测试 {level} 灵敏度:")
        game_core.set_contact_detection_thresholds(
            pressure_threshold={'very_high': 0.001, 'high': 0.002, 'medium': 0.003, 'low': 0.005, 'very_low': 0.008}[level],
            contact_area_threshold={'very_high': 1, 'high': 2, 'medium': 3, 'low': 4, 'very_low': 5}[level]
        )
        
        contact_detected = game_core.detect_contact(test_data)
        status = "✅ 检测到" if contact_detected else "❌ 未检测到"
        print(f"   {level}: {status}")
    
    # 示例4: 使用便捷方法
    print("\n4️⃣ 使用便捷方法调整:")
    if hasattr(game_core, 'adjust_contact_sensitivity'):
        game_core.adjust_contact_sensitivity('high')
        contact_detected = game_core.detect_contact(test_data)
        print(f"   高灵敏度设置: {'✅ 检测到' if contact_detected else '❌ 未检测到'}")
    
    # 示例5: 灵敏度分析
    print("\n5️⃣ 灵敏度分析:")
    test_results = game_core.test_contact_sensitivity(test_data)
    
    print("\n✅ 示例完成！")
    print("💡 使用提示:")
    print("   - 使用 set_contact_detection_thresholds() 精确调整")
    print("   - 使用 adjust_contact_sensitivity() 快速调整")
    print("   - 使用 test_contact_sensitivity() 分析效果")

def example_main_window_usage():
    """主窗口使用示例"""
    
    print("\n🖥️ 主窗口使用示例")
    print("=" * 50)
    
    # 注意：这里只是示例，实际使用时需要QApplication
    print("📝 在主窗口中使用接触检测调整:")
    print("""
    # 创建主窗口
    main_window = BoxGameMainWindow()
    
    # 调整接触检测灵敏度
    main_window.adjust_contact_sensitivity('high')
    
    # 获取当前灵敏度信息
    info = main_window.get_contact_sensitivity_info()
    print(f"当前灵敏度: {info['level']}")
    
    # 测试灵敏度
    if hasattr(main_window, 'test_contact_sensitivity'):
        test_data = np.random.exponential(0.001, (64, 64))
        results = main_window.test_contact_sensitivity(test_data)
    """)

def example_real_time_adjustment():
    """实时调整示例"""
    
    print("\n🔄 实时调整示例")
    print("=" * 50)
    
    game_core = BoxGameCoreOptimized()
    
    # 模拟实时压力数据
    pressure_data_sequence = [
        np.random.exponential(0.001, (64, 64)),  # 低压力
        np.random.exponential(0.002, (64, 64)),  # 中等压力
        np.random.exponential(0.004, (64, 64)),  # 高压力
    ]
    
    # 添加接触区域
    for i, data in enumerate(pressure_data_sequence):
        data[25:35, 25:35] += 0.001 * (i + 1)
    
    print("📊 实时调整测试:")
    for i, pressure_data in enumerate(pressure_data_sequence):
        print(f"\n   数据帧 {i+1}: 最大压力={np.max(pressure_data):.6f}")
        
        # 根据压力数据动态调整阈值
        max_pressure = np.max(pressure_data)
        if max_pressure < 0.002:
            # 低压力数据，使用高灵敏度
            game_core.set_contact_detection_thresholds(0.001, 2)
            print("   -> 调整为高灵敏度")
        elif max_pressure < 0.004:
            # 中等压力数据，使用中等灵敏度
            game_core.set_contact_detection_thresholds(0.003, 3)
            print("   -> 调整为中等灵敏度")
        else:
            # 高压力数据，使用低灵敏度
            game_core.set_contact_detection_thresholds(0.005, 4)
            print("   -> 调整为低灵敏度")
        
        contact_detected = game_core.detect_contact(pressure_data)
        status = "✅ 检测到" if contact_detected else "❌ 未检测到"
        print(f"   检测结果: {status}")

if __name__ == "__main__":
    print("🚀 接触检测阈值调整使用示例")
    print("=" * 60)
    
    example_contact_threshold_adjustment()
    example_main_window_usage()
    example_real_time_adjustment()
    
    print("\n🎯 所有示例完成！")
    print("💡 实际使用时:")
    print("   1. 根据传感器特性调整阈值")
    print("   2. 根据用户习惯调整灵敏度")
    print("   3. 根据环境条件动态调整")
    print("   4. 定期测试和优化设置") 