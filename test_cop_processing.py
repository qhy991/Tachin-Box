#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COP处理间隔功能测试脚本
Test script for COP processing interval functionality
"""

import numpy as np
import time
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

def test_cop_processing_interval():
    """测试COP处理间隔功能"""
    print("🧪 测试COP处理间隔功能")
    print("=" * 50)
    
    try:
        # 导入游戏核心
        from box_game_app_optimized import BoxGameCoreOptimized
        
        # 创建游戏核心实例
        game_core = BoxGameCoreOptimized()
        
        # 测试不同的处理间隔
        test_intervals = [1, 2, 3, 5]
        
        for interval in test_intervals:
            print(f"\n🔍 测试间隔: {interval} 帧")
            
            # 设置处理间隔
            game_core.set_cop_processing_interval(interval)
            
            # 模拟处理10帧数据
            for frame in range(10):
                # 生成模拟压力数据
                pressure_data = np.random.random((32, 32)) * 0.01
                
                # 处理数据
                result = game_core.process_pressure_data(pressure_data)
                
                if result:
                    cop_processed = result.get('cop_processed', False)
                    frame_count = result.get('frame_count', 0)
                    print(f"  帧 {frame_count}: COP处理={'✅' if cop_processed else '❌'}")
        
        # 显示COP处理统计
        print("\n📊 COP处理统计:")
        game_core.print_cop_processing_stats()
        
        # 运行性能测试
        print("\n🧪 运行性能测试:")
        game_core.test_cop_processing_performance([1, 2, 3, 5])
        
        print("\n✅ COP处理间隔功能测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cop_processing_interval() 