"""
可视化功能演示脚本
Visualization Demo Script - Demonstrate Plotting Capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from pathlib import Path
from visualization.fire_visualizer import FireVisualizer
from visualization.terrain_visualizer import TerrainVisualizer
from core.terrain import TerrainGenerator

def load_config(config_path: str):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def create_sample_fire_boundaries():
    """创建示例火场边界数据（用于演示）"""
    return {
        '24h': {
            'center': [1500.0, 1500.0],
            'radius': 346.4,
            'area_m2': 377011.3,
            'area_hectares': 37.7,
            'x_range': 692.8,
            'y_range': 692.8
        },
        '48h': {
            'center': [1500.0, 1500.0],
            'radius': 489.9,
            'area_m2': 754057.8,
            'area_hectares': 75.4,
            'x_range': 979.8,
            'y_range': 979.8
        },
        '72h': {
            'center': [1500.0, 1500.0],
            'radius': 600.0,
            'area_m2': 1130973.4,
            'area_hectares': 113.1,
            'x_range': 1200.0,
            'y_range': 1200.0
        }
    }

def create_sample_wind_scenarios():
    """创建示例风效应情景数据"""
    return {
        '无风': {
            'point_A': {
                'fire_boundaries': {
                    '72h': {
                        'center': [1500.0, 1500.0],
                        'area_hectares': 113.1,
                        'x_range': 1200.0,
                        'y_range': 1200.0
                    }
                }
            }
        },
        '3m/s东风': {
            'point_A': {
                'fire_boundaries': {
                    '72h': {
                        'center': [1520.0, 1500.0],
                        'area_hectares': 135.6,
                        'x_range': 1400.0,
                        'y_range': 1000.0
                    }
                }
            }
        },
        '5m/s东北风': {
            'point_A': {
                'fire_boundaries': {
                    '72h': {
                        'center': [1530.0, 1520.0],
                        'area_hectares': 142.8,
                        'x_range': 1500.0,
                        'y_range': 950.0
                    }
                }
            }
        }
    }

def create_sample_stats_history():
    """创建示例统计历史数据"""
    import numpy as np
    
    # 模拟72小时的数据，每小时一个记录点
    time_points = np.arange(0, 72*60 + 1, 60)  # 每60分钟记录一次
    
    stats_history = []
    for i, time_min in enumerate(time_points):
        # 模拟面积增长（平方米）
        # 使用S型增长曲线模拟火灾蔓延
        progress = i / len(time_points)
        area_m2 = 1000000 * (1 / (1 + np.exp(-8 * (progress - 0.5))))
        
        # 模拟火线强度变化
        intensity = 500 + 300 * np.sin(2 * np.pi * progress) * np.exp(-2 * progress)
        
        stats_history.append({
            'time': time_min,
            'stats': {
                'burned_area': area_m2,
                'max_fire_intensity': max(intensity, 0)
            }
        })
    
    return stats_history

def demo_fire_visualization():
    """演示火场可视化功能"""
    print("=" * 60)
    print("火场可视化功能演示")
    print("=" * 60)
    
    # 创建可视化器
    fire_viz = FireVisualizer(figure_size=(12, 8), dpi=150)
    
    # 创建输出目录
    output_dir = Path("demo_figures")
    output_dir.mkdir(exist_ok=True)
    
    # 1. 火场边界演化图
    print("1. 生成火场边界演化图...")
    fire_boundaries = create_sample_fire_boundaries()
    fire_viz.plot_fire_boundaries(
        fire_boundaries, 
        "点A起火火场边界演化（演示数据）",
        str(output_dir / "demo_fire_boundaries.png")
    )
    
    # 2. 不同起火点对比图
    print("2. 生成起火点对比图...")
    scenarios = {
        "点A起火": fire_boundaries,
        "点B起火": {
            '72h': {
                'center': [1500.0, 2000.0],
                'area_m2': 1050000.0,
                'area_hectares': 105.0,
                'x_range': 1150.0,
                'y_range': 1150.0
            }
        }
    }
    fire_viz.plot_fire_spread_comparison(
        scenarios,
        "问题一：A、B两点起火对比（演示数据）",
        str(output_dir / "demo_comparison.png")
    )
    
    # 3. 燃烧面积时间序列图
    print("3. 生成燃烧面积时间序列图...")
    stats_history = create_sample_stats_history()
    fire_viz.plot_area_time_series(
        stats_history,
        "燃烧面积和火线强度时间序列（演示数据）",
        str(output_dir / "demo_time_series.png")
    )
    
    # 4. 风效应分析图
    print("4. 生成风效应分析图...")
    wind_scenarios = create_sample_wind_scenarios()
    fire_viz.create_wind_effect_diagram(
        wind_scenarios,
        "风效应影响分析（演示数据）",
        str(output_dir / "demo_wind_effects.png")
    )
    
    print(f"✅ 火场可视化演示完成，图表保存在: {output_dir}")

def demo_terrain_visualization():
    """演示地形可视化功能"""
    print("\n" + "=" * 60)
    print("地形可视化功能演示")
    print("=" * 60)
    
    # 加载配置
    config = load_config('config/default_config.yaml')
    terrain_config = config['terrain']
    
    # 生成地形
    print("正在生成地形数据...")
    terrain_gen = TerrainGenerator(
        cell_size=config['simulation']['cell_size'], 
        config=config
    )
    surface_cells, _ = terrain_gen.create_ideal_terrain(
        width=terrain_config['width'], 
        height=terrain_config['height'],
        slope_angle_deg=terrain_config['slope_angle_deg'],
        intersection_distance=terrain_config['intersection_distance']
    )
    
    # 创建地形可视化器
    terrain_viz = TerrainVisualizer(figure_size=(12, 8), dpi=150)
    
    # 创建输出目录
    output_dir = Path("demo_figures")
    output_dir.mkdir(exist_ok=True)
    
    # 1. 三维地形图
    print("1. 生成三维地形图...")
    terrain_viz.plot_3d_terrain(
        surface_cells,
        "理想几何地形 - 三维视图（演示）",
        str(output_dir / "demo_terrain_3d.png")
    )
    
    # 2. 坡度分析图
    print("2. 生成坡度分析图...")
    terrain_viz.plot_slope_analysis(
        surface_cells,
        "地形坡度和坡向分析（演示）",
        str(output_dir / "demo_slope_analysis.png")
    )
    
    # 3. 起火点位置示意图
    print("3. 生成起火点位置示意图...")
    ignition_points = {
        'point_A': {'position': [1500.0, 1500.0], 'radius': 15.0},
        'point_B': {'position': [1500.0, 2000.0], 'radius': 15.0}
    }
    terrain_viz.plot_ignition_points_diagram(
        terrain_config,
        ignition_points,
        "起火点位置和地形示意图（演示）",
        str(output_dir / "demo_ignition_points.png")
    )
    
    # 4. 元胞网格概览（抽样显示）
    print("4. 生成元胞网格概览...")
    # 为了演示，只显示部分元胞（每10个取1个）
    sample_cells = surface_cells[::10]
    terrain_viz.plot_cell_grid_overview(
        sample_cells,
        None,
        "元胞网格概览（抽样显示）",
        str(output_dir / "demo_cell_grid.png")
    )
    
    print(f"✅ 地形可视化演示完成，图表保存在: {output_dir}")

def main():
    """主函数 - 运行所有演示"""
    print("林火蔓延模型可视化功能演示")
    print("Fire Spread Model Visualization Demo")
    print("=" * 60)
    
    try:
        # 演示火场可视化
        demo_fire_visualization()
        
        # 演示地形可视化
        demo_terrain_visualization()
        
        print("\n" + "=" * 60)
        print("✅ 所有可视化功能演示完成！")
        print("检查 'demo_figures' 目录查看生成的图表")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 