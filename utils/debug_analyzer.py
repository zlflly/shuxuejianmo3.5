"""
调试分析工具 - 诊断火灾蔓延机制
Debug Analyzer - Diagnose Fire Spread Mechanisms
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from core.cellular_automaton import CellularAutomaton
from core.cell import CellState

def debug_fire_spread():
    """调试火灾蔓延机制"""
    print("=== 火灾蔓延机制调试分析 ===\n")
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'problem_1_optimized.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建简化的测试环境
    ca = CellularAutomaton(config)
    ca.initialize_terrain(
        terrain_type="ideal",
        width=50,
        height=50,
        slope_angle_deg=30.0,
        intersection_distance=250.0
    )
    
    # 设置测试起火点
    ca.set_ignition_point((250.0, 250.0), 10.0)
    
    print(f"初始设置:")
    print(f"  起火元胞数: {len(ca.burning_surface_cells)}")
    print(f"  总元胞数: {len(ca.surface_cells)}")
    
    # 检查初始燃烧元胞的状态
    if ca.burning_surface_cells:
        burning_cell = ca.burning_surface_cells[0]
        print(f"\n初始燃烧元胞状态:")
        print(f"  位置: {burning_cell.static.position}")
        print(f"  状态: {burning_cell.dynamic.state.name}")
        print(f"  燃料载量: {burning_cell.dynamic.fuel_load} kg/m²")
        print(f"  含水量: {burning_cell.dynamic.moisture_content}")
        print(f"  邻居数: {len(burning_cell.neighbors)}")
        
        # 检查邻居状态
        print(f"\n邻居元胞状态:")
        for i, neighbor in enumerate(burning_cell.neighbors[:3]):  # 只看前3个邻居
            print(f"  邻居{i+1}: 状态={neighbor.dynamic.state.name}, "
                  f"燃料={neighbor.dynamic.fuel_load:.1f}, "
                  f"含水量={neighbor.dynamic.moisture_content:.3f}, "
                  f"能量={neighbor.dynamic.energy:.1f}")
    
    # 模拟几个时间步并分析
    print(f"\n=== 时间步分析 ===")
    for step in range(5):
        print(f"\n--- 时间步 {step+1} (t={ca.current_time:.1f}min) ---")
        
        # 执行一步
        ca.step()
        
        print(f"活跃燃烧元胞数: {len(ca.burning_surface_cells)}")
        
        if ca.burning_surface_cells:
            burning_cell = ca.burning_surface_cells[0]
            
            # 分析能量传递
            total_energy_transfer = 0.0
            for neighbor in burning_cell.neighbors:
                if neighbor.dynamic.state == CellState.UNBURNED:
                    energy_delta = ca.fire_engine.calculate_energy_transfer(
                        burning_cell, neighbor, ca.dt
                    )
                    total_energy_transfer += energy_delta
                    
                    spread_rate = ca.fire_engine.calculate_spread_rate(burning_cell, neighbor)
                    
                    print(f"  → 邻居: 蔓延速度={spread_rate:.3f}m/min, "
                          f"能量传递={energy_delta:.1f}kJ, "
                          f"邻居能量={neighbor.dynamic.energy:.1f}kJ, "
                          f"点燃阈值={neighbor.ignition_threshold:.1f}kJ")
            
            print(f"  总能量传递: {total_energy_transfer:.1f}kJ")
            print(f"  燃料剩余: {burning_cell.dynamic.fuel_load:.2f}kg/m²")
            
        # 检查是否有新点燃
        newly_ignited = [cell for cell in ca.surface_cells 
                        if cell.dynamic.state == CellState.SURFACE_FIRE and 
                        cell.dynamic.burn_time < ca.dt]
        
        if newly_ignited:
            print(f"  新点燃元胞数: {len(newly_ignited)}")
        
        # 如果没有活跃火点，停止
        if len(ca.burning_surface_cells) == 0:
            print(f"  火灾在第{step+1}步熄灭")
            break
    
    # 分析点燃阈值机制
    print(f"\n=== 点燃阈值分析 ===")
    test_cell = ca.surface_cells[0]
    base_threshold = 100.0
    moisture_factor = 2.0
    threshold = base_threshold * (2.71828 ** (moisture_factor * test_cell.dynamic.moisture_content))
    
    print(f"基础点燃能量: {base_threshold} kJ/m²")
    print(f"含水量: {test_cell.dynamic.moisture_content}")
    print(f"湿度因子: {moisture_factor}")
    print(f"实际点燃阈值: {threshold:.1f} kJ/m²")
    
    # 分析蔓延速度计算
    print(f"\n=== 蔓延速度分析 ===")
    if len(ca.surface_cells) >= 2:
        cell1 = ca.surface_cells[0]
        cell2 = ca.surface_cells[1]
        
        spread_rate = ca.fire_engine.calculate_spread_rate(cell1, cell2)
        
        print(f"基础蔓延速度 R0: {ca.fire_engine.R0} m/min")
        print(f"可燃物系数 Ks: {ca.fire_engine.Ks}")
        print(f"湿度因子参数 b: {ca.fire_engine.moisture_factor_b}")
        print(f"实际蔓延速度: {spread_rate:.3f} m/min")
        
        # 分解各个因子
        moisture_effect = ca.fire_engine.moisture_effect(cell2.dynamic.moisture_content)
        print(f"湿度效应 K_m: {moisture_effect:.3f}")

if __name__ == "__main__":
    debug_fire_spread() 