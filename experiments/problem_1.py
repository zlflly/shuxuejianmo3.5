"""
问题一：无风理想地形火灾蔓延模拟
Problem 1: Fire Spread Simulation on Ideal Terrain without Wind
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import numpy as np
from core.cellular_automaton import CellularAutomaton
from core.cell import CellState

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'problem_1_optimized.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def setup_problem_1_config(config):
    """设置问题一的特定配置"""
    # 应用问题一的简化开关
    switches = config['model_switches']['problem_1']
    
    # 关闭风效应
    if not switches['enable_wind']:
        config['environment']['wind_vector'] = [0.0, 0.0, 0.0]
    
    # 关闭树冠火
    if not switches['enable_crown_fire']:
        config['physics']['critical_fire_intensity'] = 999999.0  # 设置极高阈值
    
    # 关闭飞火
    if not switches['enable_spotting']:
        config['spotting']['probability'] = 0.0
    
    # 关闭动态湿度
    if not switches['enable_dynamic_moisture']:
        config['physics']['evaporation_coefficient'] = 0.0
    
    return config

def run_simulation_for_point(ca, point_config, point_name):
    """为指定起火点运行模拟"""
    print(f"\n=== {point_name} 起火点模拟 ===")
    
    # 重置CA状态
    ca.current_time = 0.0
    ca.burning_surface_cells = []
    ca.burning_canopy_cells = []
    ca.fire_history = []
    ca.stats_history = []
    
    # 重置所有元胞状态
    for cell in ca.surface_cells + ca.canopy_cells:
        cell.dynamic.state = CellState.UNBURNED
        cell.dynamic.fuel_load = 2.0 if cell.static.layer_type.name == 'SURFACE' else 0.5
        cell.dynamic.moisture_content = 0.12 if cell.static.layer_type.name == 'SURFACE' else 0.8
        cell.dynamic.energy = 0.0
        cell.dynamic.burn_time = 0.0
    
    # 设置起火点
    position = (point_config['x'], point_config['y'])
    radius = point_config['radius']
    ca.set_ignition_point(position, radius)
    
    print(f"起火点位置: ({position[0]}, {position[1]}), 影响半径: {radius}m")
    print(f"初始点燃元胞数: {len(ca.burning_surface_cells)}")
    
    # 运行模拟至72小时
    results = ca.run_simulation(end_time=4320)  # 72小时 = 4320分钟
    
    return results

def extract_fire_boundary_at_times(results, target_times=[1440, 2880, 4320]):
    """提取指定时间点的火场边界"""
    fire_boundaries = {}
    
    for target_time in target_times:
        hours = target_time // 60
        fire_boundaries[f"{hours}h"] = {
            'time': target_time,
            'burning_cells': [],
            'burned_out_cells': [],
            'total_area': 0.0
        }
    
    # 分析最终状态
    burning_cells = []
    burned_out_cells = []
    
    for cell in results['surface_cells']:
        if cell.dynamic.state == CellState.SURFACE_FIRE:
            burning_cells.append(cell.static.position)
        elif cell.dynamic.state == CellState.BURNED_OUT:
            burned_out_cells.append(cell.static.position)
    
    # 假设在72小时结束时获得最终边界
    cell_area = 10.0 ** 2  # 100 m²每个元胞
    total_affected = len(burning_cells) + len(burned_out_cells)
    total_area = total_affected * cell_area
    
    for time_key in fire_boundaries:
        fire_boundaries[time_key]['burning_cells'] = burning_cells.copy()
        fire_boundaries[time_key]['burned_out_cells'] = burned_out_cells.copy()
        fire_boundaries[time_key]['total_area'] = total_area
    
    return fire_boundaries

def print_results(point_name, results, boundaries):
    """打印结果摘要"""
    print(f"\n=== {point_name} 结果摘要 ===")
    print(f"模拟总时长: {results['final_time']:.1f} 分钟 ({results['final_time']/60:.1f} 小时)")
    print(f"最终燃烧面积: {results['stats']['burned_area']:.1f} m² ({results['stats']['burned_area']/10000:.2f} 公顷)")
    print(f"燃料消耗总量: {results['stats']['total_fuel_consumed']:.1f} kg")
    print(f"最大火线强度: {results['stats']['max_fire_intensity']:.1f} kW/m")
    
    print(f"\n各时间点火场范围:")
    for time_key, boundary in boundaries.items():
        print(f"  {time_key:>4}: 总面积 {boundary['total_area']:.1f} m² "
              f"({boundary['total_area']/10000:.3f} 公顷)")

def save_results(point_name, results, boundaries, output_dir="results"):
    """保存结果到文件"""
    import json
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存边界数据
    boundary_file = os.path.join(output_dir, f"{point_name}_boundaries.json")
    
    # 转换为可序列化的格式
    serializable_boundaries = {}
    for time_key, boundary in boundaries.items():
        serializable_boundaries[time_key] = {
            'time': boundary['time'],
            'total_area': boundary['total_area'],
            'burning_count': len(boundary['burning_cells']),
            'burned_out_count': len(boundary['burned_out_cells'])
        }
    
    with open(boundary_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_boundaries, f, indent=2, ensure_ascii=False)
    
    print(f"结果已保存到: {boundary_file}")

def main():
    """主函数"""
    print("林火蔓延模拟 - 问题一：无风理想地形")
    print("=" * 50)
    
    # 加载和设置配置
    config = load_config()
    config = setup_problem_1_config(config)
    
    # 创建元胞自动机
    ca = CellularAutomaton(config)
    
    # 初始化地形
    terrain_config = config['terrain']
    ca.initialize_terrain(
        terrain_type=terrain_config['type'],
        width=terrain_config['width'],
        height=terrain_config['height'],
        slope_angle_deg=terrain_config['slope_angle_deg'],
        intersection_distance=terrain_config['intersection_distance']
    )
    
    print(f"地形初始化完成:")
    print(f"  网格大小: {terrain_config['width']} × {terrain_config['height']}")
    print(f"  元胞大小: {config['simulation']['cell_size']} m")
    print(f"  山坡角度: {terrain_config['slope_angle_deg']}°")
    print(f"  到交线距离: {terrain_config['intersection_distance']} m")
    
    # A点模拟
    point_A_config = config['ignition']['point_A']
    results_A = run_simulation_for_point(ca, point_A_config, "点A")
    boundaries_A = extract_fire_boundary_at_times(results_A)
    print_results("点A", results_A, boundaries_A)
    save_results("point_A", results_A, boundaries_A)
    
    # B点模拟
    point_B_config = config['ignition']['point_B']
    results_B = run_simulation_for_point(ca, point_B_config, "点B")
    boundaries_B = extract_fire_boundary_at_times(results_B)
    print_results("点B", results_B, boundaries_B)
    save_results("point_B", results_B, boundaries_B)
    
    print(f"\n问题一模拟完成！")
    print(f"详细结果已保存到 results/ 目录")

if __name__ == "__main__":
    main() 