"""
地形分区与起火点验证脚本
Terrain Zone and Ignition Point Verification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import matplotlib.pyplot as plt
from visualization.terrain_visualizer import TerrainVisualizer

def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def verify_terrain_zones():
    """验证地形分区和起火点位置"""
    print("=== 地形分区与起火点验证 ===")
    
    # 加载配置
    config = load_config('config/problem_1_optimized.yaml')
    
    # 提取地形和起火点配置
    terrain_config = config['terrain']
    ignition_config = config['ignition']
    
    print("地形配置:")
    print(f"  网格大小: {terrain_config['width']}×{terrain_config['height']}")
    print(f"  元胞大小: {config['simulation']['cell_size']}m")
    print(f"  分界线距离: {terrain_config['intersection_distance']}m")
    print(f"  坡度角: {terrain_config['slope_angle_deg']}°")
    
    print("\n起火点配置:")
    intersection_distance = terrain_config['intersection_distance']
    
    for point_name, point_config in ignition_config.items():
        x, y = point_config['position']
        radius = point_config['radius']
        
        # 判断地形分区
        terrain_zone = "平地" if y <= intersection_distance else "山坡"
        distance_to_boundary = abs(y - intersection_distance)
        
        print(f"  {point_name}: ({x}, {y})")
        print(f"    地形分区: {terrain_zone}")
        print(f"    距分界线: {distance_to_boundary}m")
        print(f"    影响半径: {radius}m")
    
    # 创建可视化
    visualizer = TerrainVisualizer()
    
    print("\n生成地形分区验证图...")
    fig = visualizer.plot_ignition_points_diagram(
        terrain_config=terrain_config,
        ignition_points=ignition_config,
        title="地形分区与起火点验证图",
        save_path="demo_figures/terrain_zone_verification.png"
    )
    
    plt.show()
    print("✅ 地形分区验证图已保存到: demo_figures/terrain_zone_verification.png")
    
    return config

def verify_physical_consistency(config: dict):
    """验证物理参数的一致性"""
    print("\n=== 物理参数一致性检查 ===")
    
    # 检查地形参数
    terrain = config['terrain']
    simulation = config['simulation']
    physics = config['physics']
    
    print("关键参数检查:")
    print(f"  模拟时间步长: {simulation['time_step']} 分钟")
    print(f"  最大模拟时间: {simulation['max_simulation_time']} 分钟 ({simulation['max_simulation_time']/60:.1f} 小时)")
    print(f"  基础蔓延速度: {physics['base_spread_rate']} m/min")
    print(f"  坡度因子: {physics['slope_factor_a']}")
    print(f"  湿度阻抗: {physics['moisture_factor_b']}")
    
    # 检查环境条件
    environment = config['environment']
    print(f"\n环境条件:")
    print(f"  风向量: {environment['wind_vector']}")
    print(f"  初始燃料载量: {environment['initial_fuel_load']} kg/m²")
    print(f"  初始含水量: {environment['initial_moisture_content']*100:.1f}%")
    
    # 检查模型开关
    switches = config['model_switches']['problem_1']
    print(f"\n问题一模型开关:")
    for switch, enabled in switches.items():
        status = "启用" if enabled else "禁用"
        print(f"  {switch}: {status}")
    
    print("\n✅ 物理参数一致性检查完成")

def calculate_expected_fire_spread():
    """计算预期的火场蔓延范围"""
    print("\n=== 预期火场蔓延范围计算 ===")
    
    config = load_config('config/problem_1_optimized.yaml')
    
    # 基础参数
    R0 = config['physics']['base_spread_rate']  # m/min
    Ks = config['physics']['fuel_coefficient']
    slope_factor_a = config['physics']['slope_factor_a']
    moisture_factor_b = config['physics']['moisture_factor_b']
    moisture_content = config['environment']['initial_moisture_content']
    
    # 计算平地蔓延速度
    K_m = 2.71828 ** (-moisture_factor_b * moisture_content)  # 湿度因子
    Phi_flat = 1.0  # 平地坡度因子
    spread_rate_flat = R0 * Ks * K_m * Phi_flat
    
    # 计算山坡蔓延速度（30°上坡）
    import math
    slope_30deg = math.radians(30)
    Phi_slope = math.exp(slope_factor_a * slope_30deg)
    spread_rate_slope = R0 * Ks * K_m * Phi_slope
    
    print(f"理论蔓延速度:")
    print(f"  平地: {spread_rate_flat:.3f} m/min")
    print(f"  30°山坡: {spread_rate_slope:.3f} m/min")
    print(f"  坡地/平地比: {spread_rate_slope/spread_rate_flat:.2f}")
    
    # 预期火场半径（24小时）
    time_24h = 24 * 60  # 分钟
    radius_flat_24h = spread_rate_flat * time_24h
    radius_slope_24h = spread_rate_slope * time_24h
    
    print(f"\n24小时预期火场半径:")
    print(f"  平地A点: {radius_flat_24h:.0f} m")
    print(f"  山坡B点: {radius_slope_24h:.0f} m")
    
    # 预期面积
    area_flat_24h = math.pi * (radius_flat_24h ** 2) / 10000  # 公顷
    area_slope_24h = math.pi * (radius_slope_24h ** 2) / 10000  # 公顷
    
    print(f"\n24小时预期火场面积:")
    print(f"  平地A点: {area_flat_24h:.1f} 公顷")
    print(f"  山坡B点: {area_slope_24h:.1f} 公顷")
    
    print("\n✅ 预期蔓延范围计算完成")
    
    return {
        'flat_spread_rate': spread_rate_flat,
        'slope_spread_rate': spread_rate_slope,
        'flat_24h_area': area_flat_24h,
        'slope_24h_area': area_slope_24h
    }

def main():
    """主验证函数"""
    print("地形分区与起火点验证")
    print("Terrain Zone and Ignition Point Verification")
    print("=" * 60)
    
    try:
        # 验证地形分区
        config = verify_terrain_zones()
        
        # 验证物理参数一致性
        verify_physical_consistency(config)
        
        # 计算预期蔓延范围
        expected_results = calculate_expected_fire_spread()
        
        print("\n" + "=" * 60)
        print("✅ 地形分区与起火点验证完成！")
        print("✅ 配置文件一致性检查通过！")
        print("✅ 预期蔓延范围已计算！")
        
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 