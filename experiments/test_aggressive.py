"""
测试激进配置的火灾蔓延效果
Test Aggressive Configuration Fire Spread
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from core.cellular_automaton import CellularAutomaton

def test_aggressive_config():
    """测试激进配置"""
    print("=== 激进配置火灾蔓延测试 ===\n")
    
    # 加载激进配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'problem_1_aggressive.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建模拟环境
    ca = CellularAutomaton(config)
    ca.initialize_terrain(
        terrain_type="ideal",
        width=100,  # 缩小到100x100便于快速测试
        height=100,
        slope_angle_deg=30.0,
        intersection_distance=500.0  # 调整交线距离
    )
    
    print(f"地形初始化完成:")
    print(f"  网格大小: {100} × {100}")
    print(f"  总元胞数: {len(ca.surface_cells)}")
    
    # 设置起火点 (中心位置)
    ignition_x = 50 * config.get('cell_size', 10.0)
    ignition_y = 50 * config.get('cell_size', 10.0)
    ca.set_ignition_point((ignition_x, ignition_y), 15.0)
    
    print(f"起火点设置: ({ignition_x}, {ignition_y})")
    print(f"初始燃烧元胞数: {len(ca.burning_surface_cells)}")
    
    # 检查初始状态
    if ca.burning_surface_cells:
        cell = ca.burning_surface_cells[0]
        print(f"\n初始燃烧元胞:")
        print(f"  燃料载量: {cell.dynamic.fuel_load} kg/m²") 
        print(f"  含水量: {cell.dynamic.moisture_content}")
        print(f"  点燃阈值: {cell.ignition_threshold:.1f} kJ")
        
        # 检查邻居点燃阈值
        if cell.neighbors:
            neighbor = cell.neighbors[0]
            print(f"  邻居点燃阈值: {neighbor.ignition_threshold:.1f} kJ")
    
    # 运行短期模拟
    print(f"\n开始模拟...")
    target_time = 30.0  # 30分钟
    
    step_count = 0
    while ca.current_time < target_time and len(ca.burning_surface_cells) > 0:
        ca.step()
        step_count += 1
        
        # 每5步报告一次
        if step_count % 5 == 0:
            print(f"时间 {ca.current_time:.1f}min: "
                  f"燃烧元胞 {len(ca.burning_surface_cells)}, "
                  f"燃烧面积 {ca.stats['burned_area']:.0f}m²")
        
        # 检查蔓延情况
        if step_count == 1:
            print(f"\n第1步后:")
            if ca.burning_surface_cells:
                cell = ca.burning_surface_cells[0]
                energy_transfers = []
                for neighbor in cell.neighbors:
                    if neighbor.dynamic.state.name == 'UNBURNED':
                        energy_transfer = ca.fire_engine.calculate_energy_transfer(
                            cell, neighbor, ca.dt
                        )
                        energy_transfers.append(energy_transfer)
                
                print(f"  能量传递样本: {energy_transfers[:3]}")
                
        if step_count >= 50:  # 限制最大步数
            break
    
    print(f"\n=== 测试完成 ===")
    print(f"模拟时长: {ca.current_time:.1f} 分钟")
    print(f"执行步数: {step_count}")
    print(f"最终燃烧元胞数: {len(ca.burning_surface_cells)}")
    print(f"最终燃烧面积: {ca.stats['burned_area']:.1f} m²")
    print(f"燃料消耗: {ca.stats['total_fuel_consumed']:.1f} kg")
    
    # 分析火场形状
    if ca.stats['burned_area'] > 0:
        print(f"\n=== 蔓延分析 ===")
        burned_cells = [cell for cell in ca.surface_cells 
                       if cell.dynamic.state.name in ['SURFACE_FIRE', 'BURNED_OUT']]
        
        if burned_cells:
            x_coords = [cell.static.position[0] for cell in burned_cells]
            y_coords = [cell.static.position[1] for cell in burned_cells]
            
            x_range = max(x_coords) - min(x_coords)
            y_range = max(y_coords) - min(y_coords)
            
            print(f"火场尺寸: {x_range:.1f}m × {y_range:.1f}m")
            print(f"火场圆度: {min(x_range, y_range) / max(x_range, y_range):.2f}")

if __name__ == "__main__":
    test_aggressive_config() 