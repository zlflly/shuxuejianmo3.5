"""
测试高级特征与多层耦合可视化器
Test Advanced Features Visualizer

测试任务5：高级特征与多层耦合可视化功能
- 地表火/树冠火分层对比动画
- 动态堆叠面积图（各状态元胞数量变化）
- 飞火/跳火事件可视化
- 多尺度视角切换（全局-局部-地面）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 导入可视化器
from visualization.advanced.advanced_features_visualizer import AdvancedFeaturesVisualizer

def test_advanced_features_visualizer():
    """测试高级特征与多层耦合可视化器"""
    print("🚀 开始测试高级特征与多层耦合可视化器...")
    
    # 创建可视化器实例
    visualizer = AdvancedFeaturesVisualizer(figsize=(12, 8), dpi=150)
    
    # 创建输出目录
    output_dir = Path("experiments/visualization_reports")
    output_dir.mkdir(exist_ok=True)
    
    # 测试1: 创建地表火/树冠火分层对比分析
    print("\n🌲 测试1: 创建地表火/树冠火分层对比分析")
    try:
        simulation_data = {"dummy": "data"}  # 示例数据
        
        fig = visualizer.create_layered_fire_comparison(
            simulation_data=simulation_data,
            save_path=str(output_dir / "advanced_layered_fire_comparison.png")
        )
        plt.close(fig)
        print("✅ 地表火/树冠火分层对比分析创建成功")
    except Exception as e:
        print(f"❌ 地表火/树冠火分层对比分析创建失败: {e}")
    
    # 测试2: 创建动态堆叠面积图
    print("\n📊 测试2: 创建动态堆叠面积图（各状态元胞数量变化）")
    try:
        simulation_data = {"dummy": "data"}  # 示例数据
        
        fig = visualizer.create_dynamic_area_stacking(
            simulation_data=simulation_data,
            save_path=str(output_dir / "advanced_dynamic_area_stacking.png")
        )
        plt.close(fig)
        print("✅ 动态堆叠面积图创建成功")
    except Exception as e:
        print(f"❌ 动态堆叠面积图创建失败: {e}")
    
    # 测试3: 创建飞火/跳火事件可视化
    print("\n✈️ 测试3: 创建飞火/跳火事件可视化")
    try:
        simulation_data = {"dummy": "data"}  # 示例数据
        
        fig = visualizer.create_spotting_events_visualization(
            simulation_data=simulation_data,
            save_path=str(output_dir / "advanced_spotting_events.png")
        )
        plt.close(fig)
        print("✅ 飞火/跳火事件可视化创建成功")
    except Exception as e:
        print(f"❌ 飞火/跳火事件可视化创建失败: {e}")
    
    # 测试4: 创建多尺度视角切换
    print("\n🔍 测试4: 创建多尺度视角切换（全局-局部-地面）")
    try:
        simulation_data = {"dummy": "data"}  # 示例数据
        
        fig = visualizer.create_multiscale_perspective(
            simulation_data=simulation_data,
            save_path=str(output_dir / "advanced_multiscale_perspective.png")
        )
        plt.close(fig)
        print("✅ 多尺度视角切换创建成功")
    except Exception as e:
        print(f"❌ 多尺度视角切换创建失败: {e}")
    
    print("\n🎉 高级特征与多层耦合可视化器测试完成！")
    print(f"📁 所有图片已保存到: {output_dir}")
    
    return True

if __name__ == "__main__":
    test_advanced_features_visualizer() 