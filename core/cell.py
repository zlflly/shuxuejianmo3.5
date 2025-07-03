"""
元胞类定义 - 林火蔓延模型的基本单元
Cell Class Definition - Basic Unit for Fire Spread Model
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional

class CellState(Enum):
    """元胞状态枚举"""
    UNBURNED = 0      # 未燃烧
    SURFACE_FIRE = 1  # 地表火
    CROWN_FIRE = 2    # 树冠火  
    BURNED_OUT = 3    # 燃尽

class LayerType(Enum):
    """层类型枚举"""
    SURFACE = 0   # 地表层
    CANOPY = 1    # 树冠层

@dataclass
class StaticAttributes:
    """静态属性 - 模拟开始前设定，不再变化"""
    id: int                    # 唯一标识符
    position: Tuple[float, float, float]  # 三维坐标 (x, y, z)
    slope: float              # 坡度 (弧度)
    aspect: float             # 坡向 (弧度)
    fuel_type: str           # 可燃物类型 ("pine" for 松树)
    layer_type: LayerType    # 层类型
    
    # 燃料参数（基于文献的松树参数）
    canopy_base_height: float = 3.0      # 树冠基部高度 (m)
    canopy_bulk_density: float = 0.1     # 树冠体密度 (kg/m³)
    heat_content: float = 18500          # 热值 (kJ/kg)
    ignition_temp: float = 315           # 点燃温度 (°C)

@dataclass 
class DynamicAttributes:
    """动态属性 - 模拟过程中不断变化"""
    state: CellState = CellState.UNBURNED
    fuel_load: float = 2.0              # 可燃物载量 (kg/m²)
    moisture_content: float = 0.12      # 含水量 (小数形式)
    energy: float = 0.0                 # 累积能量 (kJ)
    temperature: float = 20.0           # 温度 (°C)
    burn_time: float = 0.0              # 燃烧时间 (分钟)

class Cell:
    """元胞类 - 林火蔓延模型的基本单元"""
    
    def __init__(self, static_attrs: StaticAttributes, 
                 dynamic_attrs: Optional[DynamicAttributes] = None):
        self.static = static_attrs
        self.dynamic = dynamic_attrs or DynamicAttributes()
        
        # 邻居元胞列表 (最多8个邻居)
        self.neighbors: list = []
        
        # 点燃阈值（基于含水量动态计算）
        self._ignition_threshold = None
    
    @property
    def ignition_threshold(self) -> float:
        """点燃阈值 - 基于含水量和温度动态计算"""
        if self._ignition_threshold is None:
            # 使用配置参数计算点燃阈值
            base_energy = getattr(self, '_base_ignition_energy', 100.0)
            moisture_factor_exp = getattr(self, '_ignition_moisture_factor', 2.0)
            
            moisture_effect = np.exp(moisture_factor_exp * self.dynamic.moisture_content)
            self._ignition_threshold = base_energy * moisture_effect
        return self._ignition_threshold
    
    def set_ignition_parameters(self, base_energy: float, moisture_factor: float):
        """设置点燃参数"""
        self._base_ignition_energy = base_energy
        self._ignition_moisture_factor = moisture_factor
        self._ignition_threshold = None  # 重置缓存
    
    def add_neighbor(self, neighbor: 'Cell'):
        """添加邻居元胞"""
        if neighbor not in self.neighbors and len(self.neighbors) < 8:
            self.neighbors.append(neighbor)
    
    def distance_to(self, other: 'Cell') -> float:
        """计算到其他元胞的三维距离"""
        x1, y1, z1 = self.static.position
        x2, y2, z2 = other.static.position
        return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
    
    def can_ignite(self) -> bool:
        """判断是否可以被点燃"""
        return (self.dynamic.state == CellState.UNBURNED and 
                self.dynamic.energy >= self.ignition_threshold)
    
    def ignite(self, fire_type: CellState = CellState.SURFACE_FIRE):
        """点燃元胞"""
        if self.dynamic.state == CellState.UNBURNED:
            self.dynamic.state = fire_type
            self.dynamic.burn_time = 0.0
            self._ignition_threshold = None  # 重置缓存
    
    def burn_out(self):
        """燃尽"""
        self.dynamic.state = CellState.BURNED_OUT
        self.dynamic.fuel_load = 0.0
    
    def update_energy(self, energy_delta: float):
        """更新累积能量"""
        self.dynamic.energy += energy_delta
        
    def update_moisture(self, moisture_delta: float):
        """更新含水量"""
        self.dynamic.moisture_content = max(0.0, 
            self.dynamic.moisture_content + moisture_delta)
        self._ignition_threshold = None  # 重置缓存
    
    def consume_fuel(self, consumption_rate: float, dt: float):
        """消耗燃料"""
        consumption = consumption_rate * dt
        self.dynamic.fuel_load = max(0.0, self.dynamic.fuel_load - consumption)
        self.dynamic.burn_time += dt
        
        # 燃料耗尽则燃尽
        if self.dynamic.fuel_load <= 0.0:
            self.burn_out()
    
    def __repr__(self) -> str:
        return (f"Cell(id={self.static.id}, "
                f"pos={self.static.position}, "
                f"state={self.dynamic.state.name}, "
                f"fuel={self.dynamic.fuel_load:.2f})") 