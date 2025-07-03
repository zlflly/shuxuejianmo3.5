"""
元胞自动机主类 - 林火蔓延模拟核心
Cellular Automaton Main Class - Fire Spread Simulation Core
"""

import numpy as np
import random
from typing import List, Dict, Tuple, Optional
from .cell import Cell, CellState, LayerType
from .fire_engine import FireEngine
from .terrain import TerrainGenerator

class CellularAutomaton:
    """多层元胞自动机 - 林火蔓延模拟"""
    
    def __init__(self, config: dict):
        """
        初始化元胞自动机
        
        Args:
            config: 配置参数字典
        """
        self.config = config
        self.dt = config.get('time_step', 1.0)  # 时间步长（分钟）
        self.max_simulation_time = config.get('max_simulation_time', 4320)  # 最大模拟时间（72小时=4320分钟）
        
        # 初始化组件
        self.fire_engine = FireEngine(config)
        self.terrain_generator = TerrainGenerator(config.get('cell_size', 10.0), config)
        
        # 模拟状态
        self.current_time = 0.0
        self.surface_cells: List[Cell] = []
        self.canopy_cells: List[Cell] = []
        self.burning_surface_cells: List[Cell] = []
        self.burning_canopy_cells: List[Cell] = []
        
        # 统计信息
        self.stats = {
            'burned_area': 0.0,
            'fire_perimeter': 0.0,
            'max_fire_intensity': 0.0,
            'total_fuel_consumed': 0.0
        }
        
        # 历史记录
        self.fire_history = []
        self.stats_history = []
        
        # 飞火参数
        self.spotting_probability = config.get('spotting_probability', 0.1)
        self.max_spotting_distance = config.get('max_spotting_distance', 500.0)
        
        # 燃料消耗速率
        self.fuel_consumption_rate = config.get('fuel_consumption_rate', 0.1)  # kg/m²/min
        
        # 存储初始燃料载量，用于统计计算
        self.initial_fuel_load = config.get('initial_fuel_load', 2.0)
        
        # 模拟功能开关
        self.enable_wind_effects = config.get('enable_wind_effects', False)
        self.enable_crown_fire = config.get('enable_crown_fire', True)
        self.enable_spotting = config.get('enable_spotting', True)
        self.enable_dynamic_moisture = config.get('enable_dynamic_moisture', True)
    
    def initialize_terrain(self, terrain_type: str, **kwargs):
        """
        初始化地形
        
        Args:
            terrain_type: 地形类型 ("ideal" 或 "real")
            **kwargs: 地形参数
        """
        if terrain_type == "ideal":
            width = kwargs.get('width', 200)
            height = kwargs.get('height', 200) 
            slope_angle = kwargs.get('slope_angle_deg', 30.0)
            intersection_distance = kwargs.get('intersection_distance', 1000.0)
            
            self.surface_cells, self.canopy_cells = self.terrain_generator.create_ideal_terrain(
                width, height, slope_angle, intersection_distance
            )
        else:
            raise NotImplementedError("真实地形初始化将在问题三中实现")
    
    def set_ignition_point(self, position: Tuple[float, float], radius: float = 10.0):
        """设置起火点"""
        ignited_cells = self.terrain_generator.set_ignition_point(
            self.surface_cells, position, radius
        )
        self.burning_surface_cells.extend(ignited_cells)
        
        # 记录起火点
        self.fire_history.append({
            'time': self.current_time,
            'ignition_points': [cell.static.position for cell in ignited_cells]
        })
    
    def step(self):
        """执行一个时间步的模拟"""
        # 1. 能量传递与预热
        self._energy_transfer_step()
        
        # 2. 点燃判定
        self._ignition_step()
        
        # 3. 燃料消耗与熄灭
        self._fuel_consumption_step()
        
        # 4. 树冠火跃变（可选）
        if self.enable_crown_fire:
            self._crown_fire_transition_step()
        
        # 5. 飞火（可选）
        if self.enable_spotting:
            self._spotting_step()
        
        # 6. 更新模拟时间
        self.current_time += self.dt
        
        # 7. 更新统计信息
        self._update_statistics()
        
        # 8. 记录历史
        self._record_history()
    
    def run_simulation(self, end_time: Optional[float] = None) -> Dict:
        """
        运行完整模拟
        
        Args:
            end_time: 结束时间（分钟），None表示使用默认最大时间
            
        Returns:
            模拟结果字典
        """
        if end_time is None:
            end_time = self.max_simulation_time
        
        print(f"开始火灾模拟，目标时间: {end_time} 分钟")
        
        while self.current_time < end_time:
            self.step()
            
            # 检查是否有活跃火点
            if len(self.burning_surface_cells) == 0 and len(self.burning_canopy_cells) == 0:
                print(f"模拟在 {self.current_time:.1f} 分钟时自然结束（无活跃火点）")
                break
            
            # 每小时输出进度
            if int(self.current_time) % 60 == 0:
                print(f"模拟进度: {self.current_time:.1f} 分钟, "
                      f"燃烧面积: {self.stats['burned_area']:.1f} m²")
        
        print(f"模拟完成，总用时: {self.current_time:.1f} 分钟")
        
        return {
            'final_time': self.current_time,
            'stats': self.stats.copy(),
            'surface_cells': self.surface_cells,
            'canopy_cells': self.canopy_cells,
            'fire_history': self.fire_history,
            'stats_history': self.stats_history
        }
    
    def _energy_transfer_step(self):
        """能量传递步骤"""
        energy_updates = {}  # {cell_id: energy_delta}
        
        # 从地表火传递能量
        for burning_cell in self.burning_surface_cells:
            for neighbor in burning_cell.neighbors:
                if neighbor.dynamic.state == CellState.UNBURNED:
                    energy_delta = self.fire_engine.calculate_energy_transfer(
                        burning_cell, neighbor, self.dt, self.enable_wind_effects
                    )
                    
                    if neighbor.static.id not in energy_updates:
                        energy_updates[neighbor.static.id] = 0.0
                    energy_updates[neighbor.static.id] += energy_delta
        
        # 从树冠火传递能量
        for burning_cell in self.burning_canopy_cells:
            for neighbor in burning_cell.neighbors:
                if neighbor.dynamic.state == CellState.UNBURNED:
                    energy_delta = self.fire_engine.calculate_energy_transfer(
                        burning_cell, neighbor, self.dt, self.enable_wind_effects
                    )
                    
                    if neighbor.static.id not in energy_updates:
                        energy_updates[neighbor.static.id] = 0.0
                    energy_updates[neighbor.static.id] += energy_delta
        
        # 应用能量更新和湿度变化
        all_cells = self.surface_cells + self.canopy_cells
        for cell in all_cells:
            if cell.static.id in energy_updates:
                energy_received = energy_updates[cell.static.id]
                cell.update_energy(energy_received)
                
                # 预热干燥过程
                self.fire_engine.update_moisture_from_heat(cell, energy_received)
    
    def _ignition_step(self):
        """点燃判定步骤"""
        newly_ignited_surface = []
        newly_ignited_canopy = []
        
        # 检查地表层元胞
        for cell in self.surface_cells:
            if cell.can_ignite():
                cell.ignite(CellState.SURFACE_FIRE)
                newly_ignited_surface.append(cell)
        
        # 检查树冠层元胞
        for cell in self.canopy_cells:
            if cell.can_ignite():
                cell.ignite(CellState.CROWN_FIRE)
                newly_ignited_canopy.append(cell)
        
        # 更新燃烧元胞列表
        self.burning_surface_cells.extend(newly_ignited_surface)
        self.burning_canopy_cells.extend(newly_ignited_canopy)
    
    def _fuel_consumption_step(self):
        """燃料消耗步骤"""
        # 处理地表火燃料消耗
        cells_to_remove = []
        for cell in self.burning_surface_cells:
            cell.consume_fuel(self.fuel_consumption_rate, self.dt)
            
            if cell.dynamic.state == CellState.BURNED_OUT:
                cells_to_remove.append(cell)
        
        # 移除燃尽的元胞
        for cell in cells_to_remove:
            self.burning_surface_cells.remove(cell)
        
        # 处理树冠火燃料消耗
        cells_to_remove = []
        for cell in self.burning_canopy_cells:
            cell.consume_fuel(self.fuel_consumption_rate * 2, self.dt)  # 树冠火燃烧更快
            
            if cell.dynamic.state == CellState.BURNED_OUT:
                cells_to_remove.append(cell)
        
        # 移除燃尽的元胞
        for cell in cells_to_remove:
            self.burning_canopy_cells.remove(cell)
    
    def _crown_fire_transition_step(self):
        """树冠火跃变步骤"""
        newly_crown_fires = []
        
        for surface_cell in self.burning_surface_cells:
            if self.fire_engine.can_crown_fire_initiate(surface_cell):
                # 找到对应的树冠层元胞
                corresponding_canopy = self._find_corresponding_canopy_cell(surface_cell)
                
                if (corresponding_canopy and 
                    corresponding_canopy.dynamic.state == CellState.UNBURNED):
                    
                    corresponding_canopy.ignite(CellState.CROWN_FIRE)
                    newly_crown_fires.append(corresponding_canopy)
        
        self.burning_canopy_cells.extend(newly_crown_fires)
    
    def _spotting_step(self):
        """飞火步骤"""
        new_spot_fires = []
        
        for crown_cell in self.burning_canopy_cells:
            if random.random() < self.spotting_probability:
                # 在下风向随机选择飞火位置
                spot_position = self._calculate_spot_fire_position(crown_cell)
                
                if spot_position:
                    # 寻找最近的未燃烧地表元胞
                    target_cell = self._find_nearest_unburned_surface_cell(spot_position)
                    
                    if target_cell:
                        target_cell.ignite(CellState.SURFACE_FIRE)
                        new_spot_fires.append(target_cell)
        
        self.burning_surface_cells.extend(new_spot_fires)
    
    def _find_corresponding_canopy_cell(self, surface_cell: Cell) -> Optional[Cell]:
        """找到地表元胞对应的树冠层元胞"""
        surface_pos = surface_cell.static.position
        
        for canopy_cell in self.canopy_cells:
            canopy_pos = canopy_cell.static.position
            
            # 检查x,y坐标是否匹配（z坐标不同）
            if (abs(canopy_pos[0] - surface_pos[0]) < 1.0 and 
                abs(canopy_pos[1] - surface_pos[1]) < 1.0):
                return canopy_cell
        
        return None
    
    def _calculate_spot_fire_position(self, crown_cell: Cell) -> Optional[Tuple[float, float]]:
        """计算飞火位置"""
        # 获取风向量
        wind_vector = self.fire_engine.wind_vector
        wind_speed = np.linalg.norm(wind_vector)
        
        if wind_speed == 0:
            return None
        
        # 飞火距离与风速相关
        spot_distance = min(wind_speed * 50, self.max_spotting_distance)
        
        # 在风向方向±30度范围内随机选择
        wind_direction = np.arctan2(wind_vector[1], wind_vector[0])
        direction_variation = random.uniform(-np.pi/6, np.pi/6)
        spot_direction = wind_direction + direction_variation
        
        # 计算飞火位置
        cx, cy, _ = crown_cell.static.position
        spot_x = cx + spot_distance * np.cos(spot_direction)
        spot_y = cy + spot_distance * np.sin(spot_direction)
        
        return (spot_x, spot_y)
    
    def _find_nearest_unburned_surface_cell(self, position: Tuple[float, float]) -> Optional[Cell]:
        """找到离指定位置最近的未燃烧地表元胞"""
        min_distance = float('inf')
        nearest_cell = None
        
        for cell in self.surface_cells:
            if cell.dynamic.state == CellState.UNBURNED:
                cx, cy, _ = cell.static.position
                distance = np.sqrt((cx - position[0])**2 + (cy - position[1])**2)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_cell = cell
        
        return nearest_cell if min_distance <= 50.0 else None  # 50米范围内
    
    def _update_statistics(self):
        """更新统计信息"""
        # 计算燃烧面积
        burned_count = sum(1 for cell in self.surface_cells 
                          if cell.dynamic.state in [CellState.SURFACE_FIRE, CellState.BURNED_OUT])
        
        cell_area = self.terrain_generator.cell_size ** 2
        self.stats['burned_area'] = burned_count * cell_area
        
        # 计算燃料消耗总量
        total_consumed = sum(
            (self.initial_fuel_load - cell.dynamic.fuel_load) for cell in self.surface_cells
            if cell.dynamic.state in [CellState.SURFACE_FIRE, CellState.BURNED_OUT]
        )
        self.stats['total_fuel_consumed'] = total_consumed * cell_area
        
        # 计算最大火线强度
        max_intensity = 0.0
        for cell in self.burning_surface_cells:
            intensity = self.fire_engine.calculate_fire_line_intensity(cell)
            max_intensity = max(max_intensity, intensity)
        
        self.stats['max_fire_intensity'] = max_intensity
    
    def _record_history(self):
        """记录历史数据"""
        if int(self.current_time) % 60 == 0:  # 每小时记录一次
            self.stats_history.append({
                'time': self.current_time,
                'stats': self.stats.copy(),
                'burning_surface_count': len(self.burning_surface_cells),
                'burning_canopy_count': len(self.burning_canopy_cells)
            }) 