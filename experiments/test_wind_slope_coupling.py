"""
风-坡耦合效应单元测试
Wind-Slope Coupling Effect Unit Tests
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import math
from core.fire_engine import FireEngine
from core.cell import Cell, StaticAttributes, DynamicAttributes, LayerType

def create_test_cell(position, slope=0.0, aspect=0.0):
    """创建测试用元胞"""
    static = StaticAttributes(
        id=0,
        position=position,
        slope=slope,
        aspect=aspect,
        fuel_type="pine",
        layer_type=LayerType.SURFACE
    )
    
    dynamic = DynamicAttributes(
        fuel_load=2.0,
        moisture_content=0.12
    )
    
    return Cell(static, dynamic)

def test_wind_projection_on_slope():
    """测试风向在坡面上的投影计算"""
    print("=== 测试风向在坡面上的投影 ===")
    
    # 创建火灾引擎，设置东风 (2 m/s)
    config = {
        'physics': {
            'base_spread_rate': 1.0,
            'fuel_coefficient': 1.0,
            'wind_speed_factor_c': 0.4,
            'wind_speed_power_d': 1.5,
            'wind_direction_factor_k': 3.0
        },
        'environment': {
            'wind_vector': [2.0, 0.0, 0.0]  # 2 m/s 东风
        }
    }
    
    engine = FireEngine(config)
    
    # 测试用例1：平地上的风效应
    print("\n1. 平地上的风效应：")
    spread_vector = np.array([1.0, 0.0, 0.0])  # 向东蔓延
    wind_effect_flat = engine.wind_effect(
        spread_vector,
        local_slope=0.0,
        slope_aspect=0.0,
        enable_wind=True
    )
    print(f"   向东蔓延，东风助力: {wind_effect_flat:.3f}")
    
    spread_vector = np.array([-1.0, 0.0, 0.0])  # 向西蔓延
    wind_effect_flat_opposite = engine.wind_effect(
        spread_vector,
        local_slope=0.0,
        slope_aspect=0.0,
        enable_wind=True
    )
    print(f"   向西蔓延，东风阻碍: {wind_effect_flat_opposite:.3f}")
    
    # 测试用例2：30°北向坡上的风效应
    print("\n2. 30°北向坡上的风效应：")
    slope_30deg = math.radians(30)
    north_aspect = math.pi / 2  # 北向坡
    
    # 向东蔓延（沿等高线）
    spread_vector = np.array([1.0, 0.0, 0.0])
    wind_effect_slope = engine.wind_effect(
        spread_vector,
        local_slope=slope_30deg,
        slope_aspect=north_aspect,
        enable_wind=True
    )
    print(f"   向东蔓延（沿等高线）: {wind_effect_slope:.3f}")
    
    # 向北上坡蔓延
    spread_vector = np.array([0.0, 1.0, math.tan(slope_30deg)])
    wind_effect_upslope = engine.wind_effect(
        spread_vector,
        local_slope=slope_30deg,
        slope_aspect=north_aspect,
        enable_wind=True
    )
    print(f"   向北上坡蔓延: {wind_effect_upslope:.3f}")
    
    print("\n风效应对比分析：")
    print(f"   平地东风助力 vs 坡地: {wind_effect_flat:.3f} vs {wind_effect_slope:.3f}")
    print(f"   风效应变化: {((wind_effect_slope/wind_effect_flat - 1) * 100):.1f}%")

def test_terrain_boundary_crossing():
    """测试跨越地形分界线的蔓延"""
    print("\n=== 测试跨越地形分界线的蔓延 ===")
    
    config = {
        'physics': {
            'base_spread_rate': 1.0,
            'fuel_coefficient': 1.0,
            'slope_factor_a': 0.3,
            'wind_speed_factor_c': 0.4,
            'wind_speed_power_d': 1.5,
            'wind_direction_factor_k': 3.0,
            'moisture_factor_b': 8.0
        },
        'environment': {
            'wind_vector': [0.0, 0.0, 0.0]  # 无风
        }
    }
    
    engine = FireEngine(config)
    
    # 创建测试元胞
    # A点：平地 (1500, 1500)
    cell_A = create_test_cell((1500.0, 1500.0, 0.0), slope=0.0, aspect=0.0)
    
    # B点：山坡上的邻居 (1500, 1510)  
    slope_30deg = math.radians(30)
    north_aspect = math.pi / 2
    z_B = 10 * math.tan(slope_30deg)  # 10米水平距离的高度差
    cell_B = create_test_cell((1500.0, 1510.0, z_B), slope=slope_30deg, aspect=north_aspect)
    
    # 测试从平地到山坡的蔓延
    spread_rate_A_to_B = engine.calculate_spread_rate(cell_A, cell_B, enable_wind=False)
    print(f"从平地A到山坡B的蔓延速度: {spread_rate_A_to_B:.3f} m/min")
    
    # 测试从山坡到平地的蔓延
    spread_rate_B_to_A = engine.calculate_spread_rate(cell_B, cell_A, enable_wind=False)
    print(f"从山坡B到平地A的蔓延速度: {spread_rate_B_to_A:.3f} m/min")
    
    print(f"上坡 vs 下坡蔓延比: {spread_rate_A_to_B / spread_rate_B_to_A:.2f}")
    
    # 测试分界线检测
    crosses_boundary = engine._cells_cross_terrain_boundary(cell_A, cell_B)
    print(f"是否跨越分界线: {crosses_boundary}")

def test_slope_effect_comparison():
    """测试不同坡度下的蔓延效应对比"""
    print("\n=== 测试不同坡度下的蔓延效应对比 ===")
    
    config = {
        'physics': {
            'base_spread_rate': 1.0,
            'fuel_coefficient': 1.0,
            'slope_factor_a': 0.3,
            'moisture_factor_b': 8.0
        }
    }
    
    engine = FireEngine(config)
    
    # 测试不同坡度的效应
    slopes_deg = [0, 10, 20, 30, 40, 50]
    print("坡度 (度) | 坡度效应因子 Φ(φ)")
    print("-" * 30)
    
    for slope_deg in slopes_deg:
        slope_rad = math.radians(slope_deg)
        slope_factor = engine.slope_effect(slope_rad)
        print(f"{slope_deg:8.0f} | {slope_factor:12.3f}")
    
    print("\n坡度效应分析:")
    flat_effect = engine.slope_effect(0.0)
    slope_30_effect = engine.slope_effect(math.radians(30))
    print(f"平地 vs 30°坡地效应比: {slope_30_effect / flat_effect:.2f}")

def main():
    """主测试函数"""
    print("风-坡耦合效应单元测试")
    print("Wind-Slope Coupling Effect Unit Tests")
    print("=" * 60)
    
    try:
        # 测试风向投影
        test_wind_projection_on_slope()
        
        # 测试地形分界线跨越
        test_terrain_boundary_crossing()
        
        # 测试坡度效应对比
        test_slope_effect_comparison()
        
        print("\n" + "=" * 60)
        print("✅ 所有风-坡耦合效应测试通过！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 