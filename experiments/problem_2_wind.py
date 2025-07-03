"""
问题二解决方案 - 有风条件下的林火蔓延模拟
Problem 2 Solution - Fire Spread Simulation with Wind Effects
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import json
import math
from core.cellular_automaton import CellularAutomaton

def run_problem_2():
    """运行问题二完整模拟"""
    print("=" * 70)
    print("林火蔓延模型 - 问题二解决方案")
    print("有风条件下A、B两点起火的火场范围预测")
    print("=" * 70)
    
    # 加载有风配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'problem_2_wind.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 获取风况配置
    wind_scenarios = config['wind_scenarios']
    default_scenario = config['default_wind_scenario']
    
    print(f"可用风况情景:")
    for scenario_id, scenario in wind_scenarios.items():
        print(f"  {scenario_id}: {scenario['description']} "
              f"({scenario['wind_speed']}m/s, {scenario['wind_direction_deg']}°)")
    print(f"默认使用: {default_scenario}")
    print()
    
    # 地形参数
    terrain_params = config['terrain']
    cell_size = config.get('cell_size', 10.0)
    
    print(f"地形设置:")
    print(f"  网格大小: {terrain_params['width']} × {terrain_params['height']}")
    print(f"  元胞大小: {cell_size} m")
    print(f"  山坡角度: {terrain_params['slope_angle_deg']}°")
    print(f"  交线距离: {terrain_params['intersection_distance']} m")
    print()
    
    results = {}
    
    # 对每种风况运行模拟
    for scenario_id, wind_scenario in wind_scenarios.items():
        print(f"=== 风况 {scenario_id}: {wind_scenario['description']} ===")
        
        # 创建当前风况的配置
        scenario_config = config.copy()
        scenario_config['wind_vector'] = [
            wind_scenario['wind_speed'] * math.cos(math.radians(wind_scenario['wind_direction_deg'])),
            wind_scenario['wind_speed'] * math.sin(math.radians(wind_scenario['wind_direction_deg'])),
            0.0
        ]
        
        print(f"风向量: {scenario_config['wind_vector']}")
        
        scenario_results = {}
        
        # ===== 模拟点A起火 =====
        print(f"\n--- 点A 起火点模拟 ---")
        point_A = config['ignition_points']['point_A']
        print(f"起火点位置: {point_A['position']}")
        
        ca_A = CellularAutomaton(scenario_config)
        ca_A.initialize_terrain(terrain_type="ideal", **terrain_params)
        ca_A.set_ignition_point(point_A['position'], point_A['radius'])
        
        print(f"初始点燃元胞数: {len(ca_A.burning_surface_cells)}")
        
        # 运行72小时模拟
        simulation_result_A = ca_A.run_simulation(4320)  # 72小时
        fire_boundaries_A = extract_fire_boundaries(ca_A, [24*60, 48*60, 72*60])
        
        print_summary(f"点A ({scenario_id})", simulation_result_A, fire_boundaries_A, wind_scenario)
        scenario_results['point_A'] = {
            'simulation_result': simulation_result_A,
            'fire_boundaries': fire_boundaries_A,
            'wind_scenario': wind_scenario
        }
        
        print()
        
        # ===== 模拟点B起火 =====
        print(f"--- 点B 起火点模拟 ---")
        point_B = config['ignition_points']['point_B']
        print(f"起火点位置: {point_B['position']}")
        
        ca_B = CellularAutomaton(scenario_config)
        ca_B.initialize_terrain(terrain_type="ideal", **terrain_params)
        ca_B.set_ignition_point(point_B['position'], point_B['radius'])
        
        print(f"初始点燃元胞数: {len(ca_B.burning_surface_cells)}")
        
        # 运行72小时模拟
        simulation_result_B = ca_B.run_simulation(4320)
        fire_boundaries_B = extract_fire_boundaries(ca_B, [24*60, 48*60, 72*60])
        
        print_summary(f"点B ({scenario_id})", simulation_result_B, fire_boundaries_B, wind_scenario)
        scenario_results['point_B'] = {
            'simulation_result': simulation_result_B,
            'fire_boundaries': fire_boundaries_B,
            'wind_scenario': wind_scenario
        }
        
        results[scenario_id] = scenario_results
        print("\n" + "-" * 50 + "\n")
    
    # 保存详细结果
    save_wind_results(results)
    
    # 风况对比分析
    compare_wind_scenarios(results)
    
    print("\n" + "=" * 70)
    print("问题二模拟完成！")
    print("详细结果已保存到 results/ 目录")
    print("=" * 70)
    
    return results

def extract_fire_boundaries(ca, time_points):
    """提取指定时间点的火场边界（复用问题一的方法）"""
    boundaries = {}
    cell_size = ca.terrain_generator.cell_size
    
    for time_minutes in time_points:
        time_hours = time_minutes // 60
        
        burned_cells = []
        for cell in ca.surface_cells:
            if cell.dynamic.state.name in ['SURFACE_FIRE', 'BURNED_OUT']:
                burned_cells.append(cell)
        
        if not burned_cells:
            boundaries[f"{time_hours}h"] = {
                'area_m2': 0.0,
                'area_hectares': 0.0,
                'boundary_points': [],
                'center': [0, 0],
                'radius': 0.0,
                'max_extent': {'x': 0, 'y': 0},
                'min_extent': {'x': 0, 'y': 0}
            }
            continue
        
        # 计算火场面积
        area_m2 = len(burned_cells) * (cell_size ** 2)
        area_hectares = area_m2 / 10000
        
        # 计算火场范围
        positions = [cell.static.position for cell in burned_cells]
        x_coords = [pos[0] for pos in positions]
        y_coords = [pos[1] for pos in positions]
        
        max_extent = {'x': max(x_coords), 'y': max(y_coords)}
        min_extent = {'x': min(x_coords), 'y': min(y_coords)}
        
        # 计算中心
        center_x = (max_extent['x'] + min_extent['x']) / 2
        center_y = (max_extent['y'] + min_extent['y']) / 2
        center = [center_x, center_y]
        
        # 计算平均半径
        avg_radius = sum(
            math.sqrt((pos[0] - center_x)**2 + (pos[1] - center_y)**2) 
            for pos in positions
        ) / len(positions)
        
        boundaries[f"{time_hours}h"] = {
            'area_m2': area_m2,
            'area_hectares': area_hectares,
            'center': center,
            'radius': avg_radius,
            'max_extent': max_extent,
            'min_extent': min_extent,
            'x_range': max_extent['x'] - min_extent['x'],
            'y_range': max_extent['y'] - min_extent['y']
        }
    
    return boundaries

def print_summary(point_name, simulation_result, fire_boundaries, wind_scenario):
    """打印带风况的模拟结果摘要"""
    final_time = simulation_result['final_time']
    stats = simulation_result['stats']
    
    print(f"=== {point_name} 结果摘要 ===")
    print(f"风况: {wind_scenario['description']}")
    print(f"模拟总时长: {final_time:.1f} 分钟 ({final_time/60:.1f} 小时)")
    print(f"最终燃烧面积: {stats['burned_area']:.1f} m² ({stats['burned_area']/10000:.2f} 公顷)")
    print(f"燃料消耗总量: {stats['total_fuel_consumed']:.1f} kg")
    print(f"最大火线强度: {stats['max_fire_intensity']:.1f} kW/m")
    print()
    
    print("各时间点火场范围:")
    for time_key, boundary in fire_boundaries.items():
        print(f"   {time_key}: 面积 {boundary['area_hectares']:.2f} 公顷, "
              f"范围 {boundary['x_range']:.0f}×{boundary['y_range']:.0f}m")

def compare_wind_scenarios(results):
    """对比不同风况的影响"""
    print("=== 风况影响对比分析 ===")
    
    for point in ['point_A', 'point_B']:
        print(f"\n{point.upper()} 起火点对比:")
        print("风况\t\t72h面积(公顷)\tX范围(m)\tY范围(m)\t椭圆度")
        print("-" * 60)
        
        for scenario_id, scenario_data in results.items():
            if point in scenario_data:
                boundary_72h = scenario_data[point]['fire_boundaries']['72h']
                wind_desc = scenario_data[point]['wind_scenario']['description']
                
                area = boundary_72h['area_hectares']
                x_range = boundary_72h['x_range']
                y_range = boundary_72h['y_range']
                
                # 计算椭圆度（长短轴比）
                ellipticity = max(x_range, y_range) / max(min(x_range, y_range), 1.0)
                
                print(f"{wind_desc:12}\t{area:8.2f}\t{x_range:7.0f}\t{y_range:7.0f}\t{ellipticity:6.2f}")

def save_wind_results(results):
    """保存有风结果到文件"""
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # 为每个风况保存结果
    for scenario_id, scenario_data in results.items():
        for point in ['point_A', 'point_B']:
            if point in scenario_data:
                filename = f"{point}_wind_{scenario_id}.json"
                filepath = os.path.join(results_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        'wind_scenario': scenario_data[point]['wind_scenario'],
                        'fire_boundaries': scenario_data[point]['fire_boundaries']
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"结果已保存到: {filepath}")

if __name__ == "__main__":
    # 先运行一个快速测试
    print("开始问题二风效应测试...")
    run_problem_2() 