"""
问题一最终解决方案 - 无风理想地形下的林火蔓延模拟
Problem 1 Final Solution - Fire Spread Simulation in Ideal Terrain without Wind
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import json
import math
from core.cellular_automaton import CellularAutomaton

def run_problem_1():
    """运行问题一完整模拟"""
    print("=" * 60)
    print("林火蔓延模型 - 问题一解决方案")
    print("无风理想地形下A、B两点起火的火场范围预测")
    print("=" * 60)
    
    # 加载激进配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'problem_1_aggressive.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 地形参数
    terrain_params = {
        'width': 300,
        'height': 300,
        'slope_angle_deg': 30.0,
        'intersection_distance': 1500.0  # 到平面-山坡交线的距离
    }
    
    cell_size = config.get('cell_size', 10.0)
    
    print(f"地形设置:")
    print(f"  网格大小: {terrain_params['width']} × {terrain_params['height']}")
    print(f"  元胞大小: {cell_size} m")
    print(f"  山坡角度: {terrain_params['slope_angle_deg']}°")
    print(f"  交线距离: {terrain_params['intersection_distance']} m")
    print()
    
    # 起火点配置
    point_A = config['ignition']['point_A']
    point_B = config['ignition']['point_B']
    
    results = {}
    
    # ===== 模拟点A起火 =====
    print("=== 点A 起火点模拟 ===")
    print(f"起火点位置: {point_A['position']}, 影响半径: {point_A['radius']}m")
    
    ca_A = CellularAutomaton(config)
    ca_A.initialize_terrain(terrain_type="ideal", **terrain_params)
    ca_A.set_ignition_point(point_A['position'], point_A['radius'])
    
    print(f"初始点燃元胞数: {len(ca_A.burning_surface_cells)}")
    
    # 运行72小时模拟
    simulation_result_A = ca_A.run_simulation(4320)  # 72小时 = 4320分钟
    
    # 提取各时间点的火场边界
    fire_boundaries_A = extract_fire_boundaries(ca_A, [24*60, 48*60, 72*60])
    
    print_summary("点A", simulation_result_A, fire_boundaries_A)
    results['point_A'] = {
        'simulation_result': simulation_result_A,
        'fire_boundaries': fire_boundaries_A
    }
    
    print()
    
    # ===== 模拟点B起火 =====  
    print("=== 点B 起火点模拟 ===")
    print(f"起火点位置: {point_B['position']}, 影响半径: {point_B['radius']}m")
    
    ca_B = CellularAutomaton(config)
    ca_B.initialize_terrain(terrain_type="ideal", **terrain_params)
    ca_B.set_ignition_point(point_B['position'], point_B['radius'])
    
    print(f"初始点燃元胞数: {len(ca_B.burning_surface_cells)}")
    
    # 运行72小时模拟
    simulation_result_B = ca_B.run_simulation(4320)
    
    # 提取各时间点的火场边界
    fire_boundaries_B = extract_fire_boundaries(ca_B, [24*60, 48*60, 72*60])
    
    print_summary("点B", simulation_result_B, fire_boundaries_B)
    results['point_B'] = {
        'simulation_result': simulation_result_B,
        'fire_boundaries': fire_boundaries_B
    }
    
    # 保存详细结果
    save_results(results)
    
    print("\n" + "=" * 60)
    print("问题一模拟完成！")
    print("详细结果已保存到 results/ 目录")
    print("=" * 60)
    
    return results

def extract_fire_boundaries(ca, time_points):
    """提取指定时间点的火场边界"""
    boundaries = {}
    cell_size = ca.terrain_generator.cell_size
    
    for time_minutes in time_points:
        time_hours = time_minutes // 60
        
        # 获取该时间点的燃烧和燃尽元胞
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
                'radius': 0.0
            }
            continue
        
        # 计算火场面积
        area_m2 = len(burned_cells) * (cell_size ** 2)
        area_hectares = area_m2 / 10000
        
        # 提取边界点
        boundary_points = extract_boundary_points(burned_cells)
        
        # 计算火场中心和平均半径
        if boundary_points:
            center_x = sum(p[0] for p in boundary_points) / len(boundary_points)
            center_y = sum(p[1] for p in boundary_points) / len(boundary_points)
            center = [center_x, center_y]
            
            # 计算平均半径
            avg_radius = sum(
                math.sqrt((p[0] - center_x)**2 + (p[1] - center_y)**2) 
                for p in boundary_points
            ) / len(boundary_points)
        else:
            center = [0, 0]
            avg_radius = 0.0
        
        boundaries[f"{time_hours}h"] = {
            'area_m2': area_m2,
            'area_hectares': area_hectares,
            'boundary_points': boundary_points,
            'center': center,
            'radius': avg_radius
        }
    
    return boundaries

def extract_boundary_points(burned_cells):
    """提取火场边界点"""
    if not burned_cells:
        return []
    
    # 简化的边界提取：找到最外围的点
    positions = [cell.static.position for cell in burned_cells]
    
    # 按角度排序找边界点
    if len(positions) <= 3:
        return [(pos[0], pos[1]) for pos in positions]
    
    # 找到重心
    center_x = sum(pos[0] for pos in positions) / len(positions)
    center_y = sum(pos[1] for pos in positions) / len(positions)
    
    # 计算每个点相对于重心的角度
    def angle_from_center(pos):
        return math.atan2(pos[1] - center_y, pos[0] - center_x)
    
    # 按角度分组，每个扇区取最远的点
    angle_groups = {}
    for pos in positions:
        angle = angle_from_center(pos)
        sector = int(angle * 8 / (2 * math.pi))  # 16个扇区
        
        if sector not in angle_groups:
            angle_groups[sector] = []
        angle_groups[sector].append(pos)
    
    # 每个扇区选择距离重心最远的点
    boundary_points = []
    for sector_points in angle_groups.values():
        farthest = max(sector_points, 
                      key=lambda p: (p[0] - center_x)**2 + (p[1] - center_y)**2)
        boundary_points.append((farthest[0], farthest[1]))
    
    # 按角度排序
    boundary_points.sort(key=lambda p: math.atan2(p[1] - center_y, p[0] - center_x))
    
    return boundary_points

def print_summary(point_name, simulation_result, fire_boundaries):
    """打印模拟结果摘要"""
    final_time = simulation_result['final_time']
    stats = simulation_result['stats']
    
    print(f"=== {point_name} 结果摘要 ===")
    print(f"模拟总时长: {final_time:.1f} 分钟 ({final_time/60:.1f} 小时)")
    print(f"最终燃烧面积: {stats['burned_area']:.1f} m² ({stats['burned_area']/10000:.2f} 公顷)")
    print(f"燃料消耗总量: {stats['total_fuel_consumed']:.1f} kg")
    print(f"最大火线强度: {stats['max_fire_intensity']:.1f} kW/m")
    print()
    
    print("各时间点火场范围:")
    for time_key, boundary in fire_boundaries.items():
        print(f"   {time_key}: 总面积 {boundary['area_m2']:.1f} m² "
              f"({boundary['area_hectares']:.3f} 公顷)")

def save_results(results):
    """保存结果到文件"""
    # 确保结果目录存在
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # 保存点A结果
    point_A_file = os.path.join(results_dir, 'point_A_solution.json')
    with open(point_A_file, 'w', encoding='utf-8') as f:
        json.dump(results['point_A']['fire_boundaries'], f, indent=2, ensure_ascii=False)
    
    # 保存点B结果  
    point_B_file = os.path.join(results_dir, 'point_B_solution.json')
    with open(point_B_file, 'w', encoding='utf-8') as f:
        json.dump(results['point_B']['fire_boundaries'], f, indent=2, ensure_ascii=False)
    
    print(f"结果已保存到: {point_A_file}")
    print(f"结果已保存到: {point_B_file}")

if __name__ == "__main__":
    run_problem_1() 