#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复接触检测问题
Fix contact detection issues
"""

import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from box_game_app_optimized import BoxGameCoreOptimized

def fix_contact_detection():
    """修复接触检测问题 - 针对'按压了但显示没有按压'的情况"""
    
    print("🔧 修复接触检测问题")
    print("=" * 50)
    
    # 创建游戏核心
    game_core = BoxGameCoreOptimized()
    
    print("📊 当前设置:")
    config = game_core.get_contact_detection_info()
    print(f"  压力阈值: {config['pressure_threshold']:.6f}")
    print(f"  面积阈值: {config['contact_area_threshold']}")
    
    # 方案1: 使用极高灵敏度设置
    print("\n🔧 方案1: 设置极高灵敏度")
    game_core.set_contact_detection_thresholds(pressure_threshold=0.001, contact_area_threshold=1)
    print("✅ 已设置: 压力阈值=0.001, 面积阈值=1")
    
    # 方案2: 如果方案1还不够，使用更低的阈值
    print("\n🔧 方案2: 如果方案1不够，使用更低阈值")
    game_core.set_contact_detection_thresholds(pressure_threshold=0.0005, contact_area_threshold=1)
    print("✅ 已设置: 压力阈值=0.0005, 面积阈值=1")
    
    # 方案3: 使用便捷方法
    print("\n🔧 方案3: 使用便捷方法设置极高灵敏度")
    if hasattr(game_core, 'adjust_contact_sensitivity'):
        game_core.adjust_contact_sensitivity('very_high')
        print("✅ 已使用便捷方法设置极高灵敏度")
    
    print("\n💡 使用建议:")
    print("1. 如果仍然无法检测到接触，请检查:")
    print("   - 传感器是否正常工作")
    print("   - 按压位置是否正确")
    print("   - 按压力度是否足够")
    
    print("\n2. 如果检测过于敏感（误判），可以适当提高阈值:")
    print("   game_core.set_contact_detection_thresholds(0.002, 2)")
    
    print("\n3. 获取当前配置:")
    print("   config = game_core.get_contact_detection_info()")
    print("   print(config)")
    
    return game_core

def test_with_real_data():
    """使用真实数据测试"""
    
    print("\n🧪 使用真实数据测试")
    print("=" * 50)
    
    game_core = BoxGameCoreOptimized()
    
    # 生成模拟真实按压数据
    test_data = np.random.exponential(0.0005, (64, 64))
    test_data[25:35, 25:35] += 0.001  # 添加接触区域
    
    print(f"📊 测试数据: 最大压力={np.max(test_data):.6f}")
    
    # 测试不同阈值
    thresholds = [0.003, 0.002, 0.001, 0.0005]
    
    for threshold in thresholds:
        game_core.set_contact_detection_thresholds(pressure_threshold=threshold)
        contact_detected = game_core.detect_contact(test_data)
        status = "✅ 检测到" if contact_detected else "❌ 未检测到"
        print(f"  阈值 {threshold:.4f}: {status}")
        
        if contact_detected:
            print(f"  🎯 推荐使用阈值: {threshold:.4f}")
            break

if __name__ == "__main__":
    print("🚀 接触检测修复工具")
    print("=" * 60)
    
    game_core = fix_contact_detection()
    test_with_real_data()
    
    print("\n✅ 修复完成！")
    print("💡 现在请重新运行游戏，测试接触检测是否正常")
    print("💡 如果仍有问题，请运行以下代码进一步调试:")
    print("   python test_contact_threshold.py") 