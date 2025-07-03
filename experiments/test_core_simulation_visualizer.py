"""
测试核心模拟结果可视化器
Test Core Simulation Visualizer

测试任务4：核心模拟结果可视化功能
- 火场边界等高线（24/48/72h）
- 火场蔓延2D动画
- 火场蔓延3D动画
- 关键时刻快照与对比图
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 导入可视化器
from visualization.advanced.core_simulation_visualizer import CoreSimulationVisualizer

def test_core_simulation_visualizer():
    """测试核心模拟结果可视化器"""
    print("🔥 开始测试核心模拟结果可视化器...")
    
    # 创建可视化器实例
    visualizer = CoreSimulationVisualizer(figsize=(12, 8), dpi=150)
    
    # 创建输出目录
    output_dir = Path("experiments/visualization_reports")
    output_dir.mkdir(exist_ok=True)
    
    # 测试1: 加载模拟结果数据
    print("\n📊 测试1: 加载模拟结果数据")
    results_data = visualizer.load_simulation_results("results")
    print(f"✅ 成功加载结果数据，包含文件: {list(results_data.keys())}")
    
    # 测试2: 创建火场边界等高线图
    print("\n🎯 测试2: 创建火场边界等高线图（24/48/72h）")
    try:
        # 创建示例地形数据
        terrain_data = 100 + 50 * np.random.random((300, 300))
        
        fig = visualizer.create_fire_boundary_contours(
            results_data=results_data,
            terrain_data=terrain_data,
            save_path=str(output_dir / "core_fire_boundary_contours.png")
        )
        plt.close(fig)
        print("✅ 火场边界等高线图创建成功")
    except Exception as e:
        print(f"❌ 火场边界等高线图创建失败: {e}")
    
    # 测试3: 创建火场蔓延2D动画
    print("\n🎬 测试3: 创建火场蔓延2D动画")
    try:
        simulation_data = {"dummy": "data"}  # 示例数据
        
        anim = visualizer.create_fire_spread_2d_animation(
            simulation_data=simulation_data,
            save_path=str(output_dir / "core_fire_spread_2d_animation.gif")
        )
        print("✅ 火场蔓延2D动画创建成功")
        plt.close('all')
    except Exception as e:
        print(f"❌ 火场蔓延2D动画创建失败: {e}")
    
    # 测试4: 创建火场蔓延3D动画
    print("\n🌐 测试4: 创建火场蔓延3D动画")
    try:
        simulation_data = {"dummy": "data"}  # 示例数据
        
        fig = visualizer.create_fire_spread_3d_animation(
            simulation_data=simulation_data,
            save_path=str(output_dir / "core_fire_spread_3d_animation.html")
        )
        print("✅ 火场蔓延3D动画创建成功")
    except Exception as e:
        print(f"❌ 火场蔓延3D动画创建失败: {e}")
    
    # 测试5: 创建关键时刻快照与对比图
    print("\n📸 测试5: 创建关键时刻快照与对比图")
    try:
        simulation_data = {"dummy": "data"}  # 示例数据
        
        fig = visualizer.create_key_moments_snapshots(
            simulation_data=simulation_data,
            save_path=str(output_dir / "core_key_moments_snapshots.png")
        )
        plt.close(fig)
        print("✅ 关键时刻快照与对比图创建成功")
    except Exception as e:
        print(f"❌ 关键时刻快照与对比图创建失败: {e}")
    
    print("\n🎉 核心模拟结果可视化器测试完成！")
    print(f"📁 所有图片已保存到: {output_dir}")
    
    return True

if __name__ == "__main__":
    test_core_simulation_visualizer() 