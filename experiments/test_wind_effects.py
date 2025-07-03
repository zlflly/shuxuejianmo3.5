"""
风效应快速测试 - 验证风向对火灾蔓延的影响
Quick Wind Effects Test - Verify Wind Direction Impact on Fire Spread
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import math
from core.cellular_automaton import CellularAutomaton

def test_wind_effects():
    """测试风效应的基本功能"""
    print("=== 风效应快速测试 ===\n")
    
    # 加载有风配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'problem_2_wind.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 测试两种情况：无风 vs 有风
    test_scenarios = [
        {
            'name': '无风对照',
            'wind_speed': 0.0,
            'wind_direction_deg': 0.0,
            'enable_wind': False
        },
        {
            'name': '3m/s东风',
            'wind_speed': 3.0,
            'wind_direction_deg': 90.0,  # 正东
            'enable_wind': True
        }
    ]
    
    results = {}
    
    for scenario in test_scenarios:
        print(f"--- {scenario['name']} ---")
        
        # 设置配置
        test_config = config.copy()
        test_config['enable_wind_effects'] = scenario['enable_wind']
        test_config['wind_vector'] = [
            scenario['wind_speed'] * math.cos(math.radians(scenario['wind_direction_deg'])),
            scenario['wind_speed'] * math.sin(math.radians(scenario['wind_direction_deg'])),
            0.0
        ]
        
        print(f"风向量: {test_config['wind_vector']}")
        
        # 创建小规模测试环境
        ca = CellularAutomaton(test_config)
        ca.initialize_terrain(
            terrain_type="ideal",
            width=80,  # 80x80网格
            height=80,
            slope_angle_deg=30.0,
            intersection_distance=400.0
        )
        
        # 设置中心起火点
        center_x = 40 * test_config.get('cell_size', 10.0)
        center_y = 40 * test_config.get('cell_size', 10.0)
        ca.set_ignition_point((center_x, center_y), 10.0)
        
        print(f"起火点: ({center_x}, {center_y})")
        print(f"初始燃烧元胞数: {len(ca.burning_surface_cells)}")
        
        # 运行30分钟测试
        target_time = 30.0
        step_count = 0
        
        while ca.current_time < target_time and len(ca.burning_surface_cells) > 0:
            ca.step()
            step_count += 1
            
            if step_count % 10 == 0:
                print(f"  {ca.current_time:.0f}min: 燃烧元胞{len(ca.burning_surface_cells)}, "
                      f"面积{ca.stats['burned_area']/10000:.2f}公顷")
        
        # 分析火场形状
        burned_cells = [cell for cell in ca.surface_cells 
                       if cell.dynamic.state.name in ['SURFACE_FIRE', 'BURNED_OUT']]
        
        if burned_cells:
            positions = [cell.static.position for cell in burned_cells]
            x_coords = [pos[0] for pos in positions]
            y_coords = [pos[1] for pos in positions]
            
            x_range = max(x_coords) - min(x_coords)
            y_range = max(y_coords) - min(y_coords)
            
            # 计算火场中心相对于起火点的偏移
            center_x_fire = (max(x_coords) + min(x_coords)) / 2
            center_y_fire = (max(y_coords) + min(y_coords)) / 2
            
            offset_x = center_x_fire - center_x
            offset_y = center_y_fire - center_y
            
            print(f"  最终状态:")
            print(f"    燃烧面积: {ca.stats['burned_area']/10000:.2f} 公顷")
            print(f"    火场尺寸: {x_range:.0f}m × {y_range:.0f}m")
            print(f"    中心偏移: ({offset_x:.0f}, {offset_y:.0f})m")
            print(f"    椭圆度: {max(x_range, y_range) / max(min(x_range, y_range), 1.0):.2f}")
            
            # 计算主导风向（如果有风）
            if scenario['enable_wind'] and scenario['wind_speed'] > 0:
                wind_direction = math.degrees(math.atan2(test_config['wind_vector'][1], 
                                                       test_config['wind_vector'][0]))
                offset_direction = math.degrees(math.atan2(offset_y, offset_x))
                direction_diff = abs(wind_direction - offset_direction)
                if direction_diff > 180:
                    direction_diff = 360 - direction_diff
                
                print(f"    风向: {wind_direction:.0f}°")
                print(f"    火场偏移方向: {offset_direction:.0f}°")
                print(f"    方向一致性: {direction_diff:.0f}° 偏差")
        
        results[scenario['name']] = {
            'area_hectares': ca.stats['burned_area']/10000,
            'x_range': x_range if burned_cells else 0,
            'y_range': y_range if burned_cells else 0,
            'offset_x': offset_x if burned_cells else 0,
            'offset_y': offset_y if burned_cells else 0
        }
        
        print()
    
    # 对比分析
    print("=== 风效应对比分析 ===")
    no_wind = results['无风对照']
    with_wind = results['3m/s东风']
    
    area_ratio = with_wind['area_hectares'] / max(no_wind['area_hectares'], 0.01)
    
    print(f"面积变化: {no_wind['area_hectares']:.2f} → {with_wind['area_hectares']:.2f} 公顷 "
          f"(倍数: {area_ratio:.2f})")
    
    print(f"形状变化:")
    print(f"  无风: {no_wind['x_range']:.0f}×{no_wind['y_range']:.0f}m")
    print(f"  有风: {with_wind['x_range']:.0f}×{with_wind['y_range']:.0f}m")
    
    print(f"中心偏移:")
    print(f"  无风: ({no_wind['offset_x']:.0f}, {no_wind['offset_y']:.0f})m")
    print(f"  有风: ({with_wind['offset_x']:.0f}, {with_wind['offset_y']:.0f})m")
    
    # 验证风效应是否生效
    wind_offset_magnitude = math.sqrt(with_wind['offset_x']**2 + with_wind['offset_y']**2)
    no_wind_offset_magnitude = math.sqrt(no_wind['offset_x']**2 + no_wind['offset_y']**2)
    
    if wind_offset_magnitude > no_wind_offset_magnitude + 20:  # 20m阈值
        print("✅ 风效应验证成功：有风情况下火场明显向下风向偏移")
    else:
        print("❌ 风效应可能未生效：火场偏移不明显")
    
    if area_ratio > 1.2:
        print("✅ 风速效应验证成功：有风情况下火场面积显著增大")
    else:
        print("❌ 风速效应可能不足：面积增长有限")

if __name__ == "__main__":
    test_wind_effects() 