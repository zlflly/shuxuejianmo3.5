"""
林火蔓延模型可视化系统综合演示
Comprehensive Demo for Fire Spread Model Visualization System

展示PLAN-3可视化升级项目的全部功能：
- 阶段1: 数据质量检查
- 阶段2: 静态环境可视化  
- 阶段3: 敏感性与不确定性分析
- 阶段4: 核心模拟结果可视化
- 阶段5: 高级特征与多层耦合可视化
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import numpy as np
import matplotlib.pyplot as plt
import json

# 导入所有可视化器
from visualization.advanced import (
    DataQualityAnalyzer,
    EnhancedTerrainVisualizer,
    SensitivityAnalyzer,
    CoreSimulationVisualizer,
    AdvancedFeaturesVisualizer
)

def run_comprehensive_demo():
    """运行可视化系统综合演示"""
    print("🚀 开始林火蔓延模型可视化系统综合演示")
    print("=" * 60)
    
    # 创建输出目录
    output_dir = Path("experiments/visualization_reports/comprehensive_demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成示例数据
    surface_cells = generate_sample_terrain_data()
    simulation_data = {"demo": "data"}
    
    # 阶段1: 数据质量检查
    print("\n📊 阶段1: 数据质量检查与预处理")
    print("-" * 40)
    
    try:
        analyzer = DataQualityAnalyzer()
        
        fig = analyzer.analyze_terrain_data_quality(
            surface_cells, 
            save_path=str(output_dir / "stage1_data_quality.png")
        )
        plt.close(fig)
        
        print("✅ 数据质量分析完成")
        
        # 生成CSV报告
        analyzer.generate_data_quality_report(
            surface_cells,
            save_path=str(output_dir / "stage1_quality_report.csv")
        )
        print("✅ 数据质量CSV报告生成完成")
        
    except Exception as e:
        print(f"❌ 阶段1执行失败: {e}")
    
    # 阶段2: 静态环境可视化
    print("\n🌄 阶段2: 静态环境可视化")
    print("-" * 40)
    
    try:
        terrain_viz = EnhancedTerrainVisualizer()
        
        fig = terrain_viz.create_comprehensive_terrain_analysis(
            surface_cells,
            save_path=str(output_dir / "stage2_terrain_analysis.png")
        )
        plt.close(fig)
        
        print("✅ 地形环境分析完成")
        
        # 生成3D地形图
        fig_3d = terrain_viz.create_3d_terrain_matplotlib(
            surface_cells,
            save_path=str(output_dir / "stage2_terrain_3d.png")
        )
        plt.close(fig_3d)
        
        print("✅ 3D地形可视化完成")
        
    except Exception as e:
        print(f"❌ 阶段2执行失败: {e}")
    
    # 阶段3: 敏感性与不确定性分析
    print("\n📈 阶段3: 敏感性与不确定性分析")
    print("-" * 40)
    
    try:
        sensitivity_viz = SensitivityAnalyzer()
        
        # 生成示例参数数据
        params, outputs = generate_sample_sensitivity_data()
        
        fig = sensitivity_viz.create_single_parameter_sensitivity(
            params, outputs,
            save_path=str(output_dir / "stage3_sensitivity.png")
        )
        plt.close(fig)
        
        print("✅ 单参数敏感性分析完成")
        
        fig = sensitivity_viz.create_monte_carlo_uncertainty_analysis(
            params, outputs,
            save_path=str(output_dir / "stage3_uncertainty.png")
        )
        plt.close(fig)
        
        print("✅ 蒙特卡洛不确定性分析完成")
        
    except Exception as e:
        print(f"❌ 阶段3执行失败: {e}")
    
    # 阶段4: 核心模拟结果可视化
    print("\n🔥 阶段4: 核心模拟结果可视化")
    print("-" * 40)
    
    try:
        core_viz = CoreSimulationVisualizer()
        
        # 加载模拟结果
        results_data = load_sample_results()
        
        fig = core_viz.create_fire_boundary_contours(
            results_data,
            save_path=str(output_dir / "stage4_fire_boundaries.png")
        )
        plt.close(fig)
        
        print("✅ 火场边界等高线分析完成")
        
        anim = core_viz.create_fire_spread_2d_animation(
            simulation_data,
            save_path=str(output_dir / "stage4_fire_animation_2d.gif")
        )
        plt.close('all')
        
        print("✅ 2D火场蔓延动画完成")
        
        fig_3d = core_viz.create_fire_spread_3d_animation(
            simulation_data,
            save_path=str(output_dir / "stage4_fire_animation_3d.html")
        )
        
        print("✅ 3D火场蔓延动画完成")
        
        fig = core_viz.create_key_moments_snapshots(
            simulation_data,
            save_path=str(output_dir / "stage4_key_moments.png")
        )
        plt.close(fig)
        
        print("✅ 关键时刻快照分析完成")
        
    except Exception as e:
        print(f"❌ 阶段4执行失败: {e}")
    
    # 阶段5: 高级特征与多层耦合可视化
    print("\n🚀 阶段5: 高级特征与多层耦合可视化")
    print("-" * 40)
    
    try:
        advanced_viz = AdvancedFeaturesVisualizer()
        
        fig = advanced_viz.create_layered_fire_comparison(
            simulation_data,
            save_path=str(output_dir / "stage5_layered_fire.png")
        )
        plt.close(fig)
        
        print("✅ 分层火场对比分析完成")
        
        fig = advanced_viz.create_dynamic_area_stacking(
            simulation_data,
            save_path=str(output_dir / "stage5_dynamic_stacking.png")
        )
        plt.close(fig)
        
        print("✅ 动态堆叠面积分析完成")
        
        fig = advanced_viz.create_spotting_events_visualization(
            simulation_data,
            save_path=str(output_dir / "stage5_spotting_events.png")
        )
        plt.close(fig)
        
        print("✅ 飞火事件可视化完成")
        
        fig = advanced_viz.create_multiscale_perspective(
            simulation_data,
            save_path=str(output_dir / "stage5_multiscale.png")
        )
        plt.close(fig)
        
        print("✅ 多尺度视角分析完成")
        
    except Exception as e:
        print(f"❌ 阶段5执行失败: {e}")
    
    # 生成演示总结
    print("\n📋 生成演示总结报告")
    print("-" * 40)
    
    generate_demo_summary(output_dir)
    
    print("\n🎉 林火蔓延模型可视化系统综合演示完成！")
    print("=" * 60)
    print(f"📁 所有结果已保存到: {output_dir}")
    print("\n📊 生成的文件包括:")
    print("  - 静态分析图表 (PNG格式)")
    print("  - 动态动画文件 (GIF/HTML格式)")
    print("  - 数据统计报告 (CSV格式)")
    print("  - 演示总结报告 (Markdown格式)")

def generate_sample_terrain_data():
    """生成示例地形数据"""
    # 创建100x100的网格
    size = 100
    surface_cells = []
    
    for i in range(size):
        for j in range(size):
            # 模拟地形和燃料数据
            elevation = 100 + 50 * np.sin(i/20) * np.cos(j/20) + np.random.normal(0, 5)
            slope = abs(np.random.normal(15, 8))
            aspect = np.random.uniform(0, 360)
            fuel_load = np.random.uniform(1.0, 3.0)
            moisture = np.random.uniform(0.1, 0.4)
            
            cell_data = {
                'position': (i*10, j*10),  # 10米网格
                'elevation': elevation,
                'slope': slope,
                'aspect': aspect,
                'fuel_load': fuel_load,
                'moisture_content': moisture,
                'vegetation_type': np.random.choice([1, 2, 3, 4]),
                'temperature': np.random.uniform(15, 35),
                'wind_speed': np.random.uniform(2, 12)
            }
            
            surface_cells.append(cell_data)
    
    return surface_cells

def generate_sample_sensitivity_data():
    """生成示例敏感性分析数据"""
    n_samples = 1000
    
    # 参数数据
    params = {
        'wind_speed': np.random.uniform(2, 15, n_samples),
        'humidity': np.random.uniform(0.1, 0.8, n_samples),
        'slope': np.random.uniform(0, 45, n_samples),
        'fuel_load': np.random.uniform(0.5, 4.0, n_samples)
    }
    
    # 输出数据（模拟火蔓延速度）
    outputs = (
        0.5 * params['wind_speed'] +
        -0.8 * params['humidity'] +
        0.3 * params['slope'] +
        0.4 * params['fuel_load'] +
        np.random.normal(0, 0.2, n_samples)
    )
    
    return params, outputs

def load_sample_results():
    """加载示例结果数据"""
    try:
        results_path = Path("results")
        results_data = {}
        
        for json_file in results_path.glob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                results_data[json_file.stem] = json.load(f)
        
        return results_data
    except:
        # 如果没有实际数据，返回示例数据
        return {
            'point_A_solution': {
                '24h': {'area_hectares': 450, 'boundary_points': [[0,0], [500,0], [500,500], [0,500]]},
                '48h': {'area_hectares': 720, 'boundary_points': [[0,0], [600,0], [600,600], [0,600]]},
                '72h': {'area_hectares': 900, 'boundary_points': [[0,0], [700,0], [700,700], [0,700]]}
            },
            'point_B_solution': {
                '24h': {'area_hectares': 380, 'boundary_points': [[0,0], [450,0], [450,450], [0,450]]},
                '48h': {'area_hectares': 650, 'boundary_points': [[0,0], [580,0], [580,580], [0,580]]},
                '72h': {'area_hectares': 820, 'boundary_points': [[0,0], [680,0], [680,680], [0,680]]}
            }
        }

def generate_demo_summary(output_dir):
    """生成演示总结报告"""
    summary_content = f"""# 林火蔓延模型可视化系统演示总结

## 演示概况

**演示时间**: {np.datetime64('now')}
**输出目录**: {output_dir}

## 完成的可视化阶段

### ✅ 阶段1: 数据质量检查
- 数据完整性分析
- 异常值检测
- 相关性分析
- 质量统计报告

### ✅ 阶段2: 静态环境可视化
- 地形高程分析
- 坡度坡向分布
- 3D地形渲染
- 环境要素集成

### ✅ 阶段3: 敏感性与不确定性分析
- 参数敏感性排序
- 蒙特卡洛不确定性量化
- 置信区间分析
- 方差贡献分解

### ✅ 阶段4: 核心模拟结果可视化
- 火场边界时间演化
- 2D/3D火场蔓延动画
- 关键时刻对比分析
- 蔓延统计信息

### ✅ 阶段5: 高级特征与多层耦合可视化
- 地表火/树冠火分层分析
- 动态状态统计
- 飞火事件建模
- 多尺度视角集成

## 技术特色

1. **模块化设计**: 每个分析器独立开发，可单独使用
2. **多格式输出**: 支持PNG、GIF、HTML、CSV等多种格式
3. **交互式功能**: 3D可视化支持旋转、缩放、动画控制
4. **专业配色**: 针对林火分析优化的配色方案
5. **中文支持**: 完整的中文标签和说明

## 应用价值

- **科研支持**: 为火行为研究提供可视化工具
- **决策辅助**: 为应急管理提供直观分析
- **教学演示**: 为林火教育提供可视化教材
- **系统开发**: 为模型开发提供调试工具

## 后续扩展

系统还可继续扩展决策支持和应急输出功能，实现更完整的林火管理可视化解决方案。

---
*自动生成的演示报告*
"""
    
    with open(output_dir / "demo_summary.md", 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print("✅ 演示总结报告生成完成")

if __name__ == "__main__":
    run_comprehensive_demo() 