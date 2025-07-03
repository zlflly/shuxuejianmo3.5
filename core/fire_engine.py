"""
火蔓延物理引擎 - 统一的蔓延速度计算
Fire Spread Physics Engine - Unified Spread Rate Calculation
"""

import numpy as np
from typing import Tuple, Optional
from .cell import Cell, CellState
import math

class FireEngine:
    """火蔓延物理引擎"""
    
    def __init__(self, config: dict):
        """初始化物理引擎参数"""
        # 基础蔓延速度 (m/min)
        self.R0 = config.get('base_spread_rate', 0.5)
        
        # 可燃物系数 (松树)
        self.Ks = config.get('fuel_coefficient', 1.2)
        
        # 坡度效应参数
        self.slope_factor_a = config.get('slope_factor_a', 0.3)
        self.max_slope_deg = config.get('max_slope_deg', 55.0)
        
        # 风效应参数
        self.wind_speed_factor_c = config.get('wind_speed_factor_c', 0.4)
        self.wind_speed_power_d = config.get('wind_speed_power_d', 1.5)
        self.wind_direction_factor_k = config.get('wind_direction_factor_k', 3.0)
        
        # 湿度效应参数
        self.moisture_factor_b = config.get('moisture_factor_b', 8.0)
        
        # 蒸发系数
        self.evaporation_coefficient = config.get('evaporation_coefficient', 0.001)
        
        # 全局风向量 (水平风)
        # 支持从environment节点或直接从根节点读取
        if 'environment' in config:
            wind_vector = config['environment'].get('wind_vector', [0.0, 0.0, 0.0])
        else:
            wind_vector = config.get('wind_vector', [0.0, 0.0, 0.0])
        self.wind_vector = np.array(wind_vector)
        
        # 树冠火参数
        self.crown_fire_multiplier = config.get('crown_fire_multiplier', 3.0)
        self.critical_fire_intensity = config.get('critical_fire_intensity', 500.0)  # kW/m
        
        # 新增：能量传递优化参数
        self.energy_transfer_multiplier = config.get('energy_transfer_multiplier', 1.0)
        self.min_energy_transfer = config.get('min_energy_transfer', 0.0)
        
        # 新增：点燃参数
        self.base_ignition_energy = config.get('base_ignition_energy', 100.0)
        self.ignition_moisture_factor = config.get('ignition_moisture_factor', 2.0)
        
    def set_wind(self, wind_speed: float, wind_direction_deg: float):
        """设置风向和风速"""
        wind_dir_rad = math.radians(wind_direction_deg)
        self.wind_vector = np.array([
            wind_speed * math.cos(wind_dir_rad),
            wind_speed * math.sin(wind_dir_rad),
            0.0
        ])
    
    def slope_effect(self, slope_rad: float) -> float:
        """
        坡度效应因子 Φ(φ)
        使用指数形式: e^(a·φ)，但限制最大坡度
        """
        slope_deg = math.degrees(abs(slope_rad))
        
        # 限制坡度范围，避免无界外推
        if slope_deg > self.max_slope_deg:
            slope_deg = self.max_slope_deg
        
        slope_rad_limited = math.radians(slope_deg)
        
        # 上坡为正，下坡为负
        if slope_rad < 0:
            slope_rad_limited = -slope_rad_limited
            
        return math.exp(self.slope_factor_a * slope_rad_limited)
    
    def wind_effect(self, spread_vector: np.ndarray, local_slope: float = 0.0, 
                   slope_aspect: float = 0.0, enable_wind: bool = True) -> float:
        """
        风-坡耦合效应因子 K_wind(V_w, α_ij, φ, aspect)
        考虑风向在坡面上的投影和坡度对风效应的影响
        
        Args:
            spread_vector: 蔓延方向向量
            local_slope: 局部坡度 (弧度)
            slope_aspect: 坡向 (弧度，0为正北)
            enable_wind: 是否启用风效应
        """
        if not enable_wind:
            return 1.0
            
        wind_speed = np.linalg.norm(self.wind_vector)
        
        if wind_speed == 0:
            return 1.0
            
        # 计算坡面法向量
        # 平地：n = (0, 0, 1)
        # 斜坡：n = (-sin(aspect)*sin(slope), -cos(aspect)*sin(slope), cos(slope))
        if abs(local_slope) < 1e-6:
            # 平地情况
            surface_normal = np.array([0.0, 0.0, 1.0])
        else:
            # 斜坡情况
            surface_normal = np.array([
                -math.sin(slope_aspect) * math.sin(local_slope),
                -math.cos(slope_aspect) * math.sin(local_slope),
                math.cos(local_slope)
            ])
        
        # 将水平风向量投影到坡面上
        # V_proj = V_wind - (V_wind · n) * n
        wind_dot_normal = np.dot(self.wind_vector, surface_normal)
        wind_projected = self.wind_vector - wind_dot_normal * surface_normal
        
        # 如果投影后的风向量很小，说明风向几乎垂直于坡面
        wind_proj_speed = np.linalg.norm(wind_projected)
        if wind_proj_speed < 1e-6:
            return 1.0
        
        # 计算投影风向与蔓延方向的夹角
        spread_speed = np.linalg.norm(spread_vector)
        if spread_speed == 0:
            return 1.0
            
        cos_alpha = np.dot(wind_projected, spread_vector) / (wind_proj_speed * spread_speed)
        cos_alpha = np.clip(cos_alpha, -1.0, 1.0)  # 防止数值误差
        
        # 风速大小效应（使用投影后的风速）
        speed_effect = 1.0 + self.wind_speed_factor_c * (wind_proj_speed ** self.wind_speed_power_d)
        
        # 风向效应: f_dir(α) = e^(k(cos(α)-1))
        direction_effect = math.exp(self.wind_direction_factor_k * (cos_alpha - 1.0))
        
        return speed_effect * direction_effect
    
    def moisture_effect(self, moisture_content: float) -> float:
        """
        湿度抑制因子 K_m(M_j)
        使用指数衰减: e^(-b·M_j)
        """
        return math.exp(-self.moisture_factor_b * moisture_content)
    
    def calculate_spread_rate(self, from_cell: Cell, to_cell: Cell, enable_wind: bool = True) -> float:
        """
        计算从 from_cell 到 to_cell 的蔓延速度
        R_i→j = R0 · K_wind(V_w,α_ij,φ,aspect) · Ks · K_m(M_j) · Φ(φ_ij)
        考虑风-坡耦合效应和跨越地形分界线的情况
        """
        # 计算蔓延方向向量
        pos_from = np.array(from_cell.static.position)
        pos_to = np.array(to_cell.static.position)
        spread_vector = pos_to - pos_from
        
        # 计算局部坡度（从from到to的坡度）
        horizontal_dist = math.sqrt(spread_vector[0]**2 + spread_vector[1]**2)
        if horizontal_dist == 0:
            local_slope = 0.0
        else:
            local_slope = math.atan(spread_vector[2] / horizontal_dist)
        
        # 确定用于风效应计算的坡度和坡向
        # 如果跨越分界线，使用目标元胞的坡度/坡向；否则使用源元胞的
        if self._cells_cross_terrain_boundary(from_cell, to_cell):
            # 跨越平地-山坡分界线，使用目标元胞的地形参数
            terrain_slope = to_cell.static.slope
            terrain_aspect = to_cell.static.aspect
        else:
            # 在同一地形区域内，使用源元胞的地形参数
            terrain_slope = from_cell.static.slope
            terrain_aspect = from_cell.static.aspect
        
        # 计算各项因子
        slope_factor = self.slope_effect(local_slope)
        wind_factor = self.wind_effect(
            spread_vector, 
            local_slope=terrain_slope,
            slope_aspect=terrain_aspect,
            enable_wind=enable_wind
        )
        moisture_factor = self.moisture_effect(to_cell.dynamic.moisture_content)
        
        # 统一蔓延速度公式
        spread_rate = (self.R0 * wind_factor * self.Ks * 
                      moisture_factor * slope_factor)
        
        return max(0.0, spread_rate)  # 确保非负
    
    def _cells_cross_terrain_boundary(self, from_cell: Cell, to_cell: Cell) -> bool:
        """
        判断两个元胞是否跨越地形分界线（平地-山坡）
        基于y坐标和intersection_distance判断
        """
        # 使用更新后的分界线距离
        intersection_distance = 4000.0
        
        from_y = from_cell.static.position[1]
        to_y = to_cell.static.position[1]
        
        from_is_flat = from_y <= intersection_distance
        to_is_flat = to_y <= intersection_distance
        
        return from_is_flat != to_is_flat
    
    def calculate_energy_transfer(self, from_cell: Cell, to_cell: Cell, dt: float, enable_wind: bool = True) -> float:
        """
        计算能量传递增量
        ΔE_j = (C·W_i·R_i→j) / D_ij² · Δt · multiplier
        """
        if from_cell.dynamic.state not in [CellState.SURFACE_FIRE, CellState.CROWN_FIRE]:
            return 0.0
            
        # 计算距离
        distance = from_cell.distance_to(to_cell)
        if distance == 0:
            return 0.0
            
        # 计算蔓延速度
        spread_rate = self.calculate_spread_rate(from_cell, to_cell, enable_wind)
        
        # 能量传递系数 C（基于燃料载量和热值）
        energy_coefficient = (from_cell.dynamic.fuel_load * 
                            from_cell.static.heat_content / 1000)  # 转换为MJ
        
        # 热通量计算
        heat_flux = energy_coefficient * spread_rate
        
        # 距离衰减（平方反比）- 但不让距离过大影响传递
        distance_factor = max(1.0, distance)  # 防止距离为0
        energy_transfer = heat_flux / distance_factor * dt
        
        # 应用能量传递放大系数
        energy_transfer *= self.energy_transfer_multiplier
        
        # 确保最小能量传递
        energy_transfer = max(energy_transfer, self.min_energy_transfer * dt)
        
        return energy_transfer
    
    def calculate_fire_line_intensity(self, cell: Cell) -> float:
        """
        计算火线强度 I = c_I · R_avg · W
        用于判断树冠火跃变
        """
        if cell.dynamic.state != CellState.SURFACE_FIRE:
            return 0.0
            
        # 计算平均蔓延速度（向所有邻居的平均）
        total_spread_rate = 0.0
        neighbor_count = 0
        
        for neighbor in cell.neighbors:
            if neighbor.dynamic.state == CellState.UNBURNED:
                spread_rate = self.calculate_spread_rate(cell, neighbor)
                total_spread_rate += spread_rate
                neighbor_count += 1
                
        if neighbor_count == 0:
            return 0.0
            
        avg_spread_rate = total_spread_rate / neighbor_count
        
        # 火线强度 = 热值 × 蔓延速度 × 燃料载量
        intensity = (cell.static.heat_content * avg_spread_rate * 
                    cell.dynamic.fuel_load / 1000)  # 转换为kW/m
        
        return intensity
    
    def can_crown_fire_initiate(self, surface_cell: Cell) -> bool:
        """
        判断是否可以发生树冠火跃变
        基于Van Wagner模型的临界火线强度
        """
        fire_intensity = self.calculate_fire_line_intensity(surface_cell)
        
        # Van Wagner临界强度公式（简化版）
        cbh = surface_cell.static.canopy_base_height
        fmc = surface_cell.dynamic.moisture_content * 100  # 转换为百分比
        
        critical_intensity = (0.01 * cbh * (460 + 26 * fmc)) ** 1.5
        
        return fire_intensity > critical_intensity
    
    def update_moisture_from_heat(self, cell: Cell, energy_received: float):
        """
        基于接收到的热量更新含水量（预热干燥过程）
        """
        if energy_received > 0:
            moisture_loss = energy_received * self.evaporation_coefficient
            cell.update_moisture(-moisture_loss) 