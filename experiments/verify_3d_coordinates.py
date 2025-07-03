"""
验证3D坐标起火点
Verify 3D Coordinate Ignition Points
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import math
from core.cellular_automaton import CellularAutomaton

def verify_3d_coordinates():
    """验证3D坐标起火点"""
    print("=== 验证3D坐标起火点 ===")
    
    # 加载配置
    config = yaml.safe_load(open('config/problem_1_optimized.yaml'))
    
    print("起火点3D坐标验证:")
    for point_name, point_config in config['ignition'].items():
        pos = point_config['position']
        print(f"  {point_name}: {pos} (len={len(pos)})")
        if len(pos) == 3:
            print(f"    x={pos[0]}, y={pos[1]}, z={pos[2]}")
        print()
    
    # 验证地形坐标计算
    print("地形坐标计算验证:")
    intersection_distance = config['terrain']['intersection_distance']
    slope_angle_deg = config['terrain']['slope_angle_deg']
    slope_rad = math.radians(slope_angle_deg)
    
    for point_name, point_config in config['ignition'].items():
        pos = point_config['position']
        x, y = pos[0], pos[1]
        
        # 根据地形生成逻辑计算期望的z坐标
        if y <= intersection_distance:
            expected_z = 0.0
            terrain_type = "平地"
        else:
            slope_distance = y - intersection_distance
            expected_z = slope_distance * math.tan(slope_rad)
            terrain_type = "山坡"
        
        if len(pos) == 3:
            actual_z = pos[2]
            z_diff = abs(actual_z - expected_z)
            print(f"  {point_name} ({terrain_type}):")
            print(f"    配置z坐标: {actual_z}")
            print(f"    期望z坐标: {expected_z:.1f}")
            print(f"    差异: {z_diff:.1f}m")
        else:
            print(f"  {point_name}: 缺少z坐标！")
        print()

def test_3d_ignition():
    """测试3D起火点设置"""
    print("=== 测试3D起火点设置 ===")
    
    config = yaml.safe_load(open('config/problem_1_optimized.yaml'))
    
    # 创建元胞自动机
    ca = CellularAutomaton(config)
    
    terrain_params = {
        'width': config['terrain']['width'],
        'height': config['terrain']['height'], 
        'cell_size': config['simulation']['cell_size'],
        'slope_angle_deg': config['terrain']['slope_angle_deg'],
        'intersection_distance': config['terrain']['intersection_distance']
    }
    
    ca.initialize_terrain(terrain_type='ideal', **terrain_params)
    
    # 测试A点3D起火
    point_A = config['ignition']['point_A']
    print(f"设置A点起火: {point_A['position']}")
    
    try:
        ca.set_ignition_point(point_A['position'], point_A['radius'])
        print(f"✅ A点起火成功，燃烧元胞数: {len(ca.burning_surface_cells)}")
        
        # 检查起火元胞的坐标
        if ca.burning_surface_cells:
            first_burning = ca.burning_surface_cells[0]
            pos = first_burning.static.position
            print(f"   第一个燃烧元胞坐标: ({pos[0]}, {pos[1]}, {pos[2]})")
    except Exception as e:
        print(f"❌ A点起火失败: {e}")
    
    # 创建新的CA测试B点
    ca_B = CellularAutomaton(config)
    ca_B.initialize_terrain(terrain_type='ideal', **terrain_params)
    
    # 测试B点3D起火
    point_B = config['ignition']['point_B']
    print(f"\n设置B点起火: {point_B['position']}")
    
    try:
        ca_B.set_ignition_point(point_B['position'], point_B['radius'])
        print(f"✅ B点起火成功，燃烧元胞数: {len(ca_B.burning_surface_cells)}")
        
        # 检查起火元胞的坐标
        if ca_B.burning_surface_cells:
            first_burning = ca_B.burning_surface_cells[0]
            pos = first_burning.static.position
            print(f"   第一个燃烧元胞坐标: ({pos[0]}, {pos[1]}, {pos[2]})")
    except Exception as e:
        print(f"❌ B点起火失败: {e}")

def main():
    """主函数"""
    print("3D坐标起火点验证")
    print("3D Coordinate Ignition Point Verification")
    print("=" * 60)
    
    try:
        verify_3d_coordinates()
        test_3d_ignition()
        
        print("\n" + "=" * 60)
        print("✅ 3D坐标验证完成！")
        
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 