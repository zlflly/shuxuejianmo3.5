"""
快速测试修正后的配置
Quick Test for Corrected Configuration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from core.cellular_automaton import CellularAutomaton

def quick_test():
    """30分钟快速测试"""
    print("=== 修正后配置30分钟快速测试 ===")
    
    # 加载配置
    config = yaml.safe_load(open('config/problem_1_optimized.yaml'))
    
    # 显示关键配置
    print(f"网格大小: {config['terrain']['width']}×{config['terrain']['height']}")
    print(f"总范围: {config['terrain']['width']*config['simulation']['cell_size']}m×{config['terrain']['height']*config['simulation']['cell_size']}m")
    print(f"分界线: y={config['terrain']['intersection_distance']}m")
    
    # 测试A点（平地）
    print("\n--- 测试A点（平地）---")
    ca_A = CellularAutomaton(config)
    
    terrain_params = {
        'width': config['terrain']['width'],
        'height': config['terrain']['height'], 
        'cell_size': config['simulation']['cell_size'],
        'slope_angle_deg': config['terrain']['slope_angle_deg'],
        'intersection_distance': config['terrain']['intersection_distance']
    }
    
    ca_A.initialize_terrain(terrain_type='ideal', **terrain_params)
    
    # 设置A点起火
    point_A = config['ignition']['point_A']
    ca_A.set_ignition_point(point_A['position'], point_A['radius'])
    
    print(f"A点位置: {point_A['position']}")
    print(f"初始燃烧元胞数: {len(ca_A.burning_surface_cells)}")
    
    # 运行30分钟
    result_A = ca_A.run_simulation(30)
    final_area_A = result_A['stats']['burned_area']
    print(f"30分钟后燃烧面积: {final_area_A:.1f} m² ({final_area_A/10000:.3f} 公顷)")
    
    # 分析火场分布
    burned_cells_A = [c for c in ca_A.surface_cells if c.dynamic.state.name in ['SURFACE_FIRE', 'BURNED_OUT']]
    if burned_cells_A:
        positions_A = [c.static.position for c in burned_cells_A]
        center_x_A = sum(p[0] for p in positions_A) / len(positions_A)
        center_y_A = sum(p[1] for p in positions_A) / len(positions_A)
        max_dist_A = max(((p[0]-center_x_A)**2 + (p[1]-center_y_A)**2)**0.5 for p in positions_A)
        print(f"火场中心: ({center_x_A:.0f}, {center_y_A:.0f})")
        print(f"火场最大半径: {max_dist_A:.0f} m")
        
        # 验证是否在平地区域
        intersection_distance = config['terrain']['intersection_distance']
        in_flat_area = center_y_A <= intersection_distance
        print(f"火场位于平地区域: {in_flat_area}")
    
    # 测试B点（山坡）
    print("\n--- 测试B点（山坡）---")
    ca_B = CellularAutomaton(config)
    ca_B.initialize_terrain(terrain_type='ideal', **terrain_params)
    
    # 设置B点起火
    point_B = config['ignition']['point_B']
    ca_B.set_ignition_point(point_B['position'], point_B['radius'])
    
    print(f"B点位置: {point_B['position']}")
    print(f"初始燃烧元胞数: {len(ca_B.burning_surface_cells)}")
    
    # 运行30分钟
    result_B = ca_B.run_simulation(30)
    final_area_B = result_B['stats']['burned_area']
    print(f"30分钟后燃烧面积: {final_area_B:.1f} m² ({final_area_B/10000:.3f} 公顷)")
    
    # 分析火场分布
    burned_cells_B = [c for c in ca_B.surface_cells if c.dynamic.state.name in ['SURFACE_FIRE', 'BURNED_OUT']]
    if burned_cells_B:
        positions_B = [c.static.position for c in burned_cells_B]
        center_x_B = sum(p[0] for p in positions_B) / len(positions_B)
        center_y_B = sum(p[1] for p in positions_B) / len(positions_B)
        max_dist_B = max(((p[0]-center_x_B)**2 + (p[1]-center_y_B)**2)**0.5 for p in positions_B)
        print(f"火场中心: ({center_x_B:.0f}, {center_y_B:.0f})")
        print(f"火场最大半径: {max_dist_B:.0f} m")
        
        # 验证是否在山坡区域
        in_slope_area = center_y_B > intersection_distance
        print(f"火场位于山坡区域: {in_slope_area}")
    
    # 对比分析
    print("\n=== 对比分析 ===")
    if final_area_A > 0 and final_area_B > 0:
        slope_advantage = final_area_B / final_area_A
        print(f"坡地/平地燃烧面积比: {slope_advantage:.2f}")
        print(f"坡度效应: {'正常 (>1.0)' if slope_advantage > 1.0 else '异常 (≤1.0)'}")
    
    print("\n✅ 快速测试完成！")
    return {
        'A_area': final_area_A,
        'B_area': final_area_B,
        'A_radius': max_dist_A if 'max_dist_A' in locals() else 0,
        'B_radius': max_dist_B if 'max_dist_B' in locals() else 0
    }

if __name__ == "__main__":
    quick_test() 