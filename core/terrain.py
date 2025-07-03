"""
地形生成与初始化模块
Terrain Generation and Initialization Module
"""

import numpy as np
import math
from typing import Tuple, Optional, List
from .cell import Cell, StaticAttributes, DynamicAttributes, LayerType, CellState

class TerrainGenerator:
    """地形生成器"""
    
    def __init__(self, cell_size: float = 10.0, config: dict = None):
        """
        初始化地形生成器
        
        Args:
            cell_size: 元胞大小 (米)
            config: 配置字典
        """
        self.cell_size = cell_size
        self.config = config or {}
    
    def create_ideal_terrain(self, 
                           width: int, height: int,
                           slope_angle_deg: float = 30.0,
                           intersection_distance: float = 1000.0) -> Tuple[List[Cell], List[Cell]]:
        """
        创建理想几何地形（问题一、二使用）
        
        Args:
            width, height: 网格尺寸
            slope_angle_deg: 山坡与地面夹角（度）
            intersection_distance: 到交线的距离（米）
            
        Returns:
            surface_cells, canopy_cells: 地表层和树冠层元胞列表
        """
        surface_cells = []
        canopy_cells = []
        cell_id = 0
        
        slope_rad = math.radians(slope_angle_deg)
        
        for i in range(height):
            for j in range(width):
                # 计算实际坐标
                x = j * self.cell_size
                y = i * self.cell_size
                
                # 判断是在地面还是山坡
                # 关键物理分区：y <= intersection_distance为平地，y > intersection_distance为山坡
                distance_to_intersection = y
                
                if distance_to_intersection <= intersection_distance:
                    # 平地区域 (坡度为0)
                    # 点A(4000,3000)位于此区域：y=3000 <= intersection_distance=4000，距分界线1000m
                    z = 0.0
                    local_slope = 0.0
                    local_aspect = 0.0
                else:
                    # 山坡区域 (30°坡度)
                    # 点B(4000,4500)位于此区域：y=4500 > intersection_distance=4000，距分界线500m
                    slope_distance = distance_to_intersection - intersection_distance
                    z = slope_distance * math.tan(slope_rad)
                    local_slope = slope_rad
                    local_aspect = math.pi / 2  # 北向坡
                
                # 创建地表层元胞
                surface_static = StaticAttributes(
                    id=cell_id,
                    position=(x, y, z),
                    slope=local_slope,
                    aspect=local_aspect,
                    fuel_type="pine",
                    layer_type=LayerType.SURFACE
                )
                
                surface_dynamic = DynamicAttributes(
                    fuel_load=self.config.get('initial_fuel_load', 2.0),
                    moisture_content=self.config.get('initial_moisture_content', 0.12)
                )
                
                surface_cell = Cell(surface_static, surface_dynamic)
                
                # 设置点燃参数
                surface_cell.set_ignition_parameters(
                    self.config.get('base_ignition_energy', 100.0),
                    self.config.get('ignition_moisture_factor', 2.0)
                )
                surface_cells.append(surface_cell)
                
                # 创建对应的树冠层元胞
                canopy_static = StaticAttributes(
                    id=cell_id + width * height,
                    position=(x, y, z + 5.0),  # 树冠高度5米
                    slope=local_slope,
                    aspect=local_aspect,
                    fuel_type="pine",
                    layer_type=LayerType.CANOPY
                )
                
                canopy_dynamic = DynamicAttributes(
                    fuel_load=0.5,  # 树冠燃料较少
                    moisture_content=0.8   # 活燃料含水量较高
                )
                
                canopy_cell = Cell(canopy_static, canopy_dynamic)
                
                # 设置点燃参数
                canopy_cell.set_ignition_parameters(
                    self.config.get('base_ignition_energy', 100.0),
                    self.config.get('ignition_moisture_factor', 2.0)
                )
                canopy_cells.append(canopy_cell)
                
                cell_id += 1
        
        # 建立邻居关系
        self._build_neighbor_relationships(surface_cells, width, height)
        self._build_neighbor_relationships(canopy_cells, width, height)
        
        return surface_cells, canopy_cells
    
    def set_ignition_point(self, cells: List[Cell], 
                          position, 
                          radius: float = 10.0) -> List[Cell]:
        """
        设置起火点
        
        Args:
            cells: 元胞列表
            position: 起火点坐标 (x, y) 或 (x, y, z)
            radius: 起火范围半径
            
        Returns:
            ignited_cells: 被点燃的元胞列表
        """
        ignited_cells = []
        
        # 兼容2D和3D坐标
        if len(position) == 2:
            target_x, target_y = position[0], position[1]
            use_z = False
        elif len(position) == 3:
            target_x, target_y, target_z = position[0], position[1], position[2]
            use_z = True
        else:
            raise ValueError("position must be (x, y) or (x, y, z)")
        
        for cell in cells:
            cell_x, cell_y, cell_z = cell.static.position
            
            if use_z:
                # 3D距离计算
                distance = math.sqrt((cell_x - target_x)**2 + 
                                   (cell_y - target_y)**2 + 
                                   (cell_z - target_z)**2)
            else:
                # 2D距离计算（忽略z坐标）
                distance = math.sqrt((cell_x - target_x)**2 + (cell_y - target_y)**2)
            
            if distance <= radius:
                cell.ignite(CellState.SURFACE_FIRE)
                ignited_cells.append(cell)
        
        return ignited_cells
    
    def _build_neighbor_relationships(self, cells: List[Cell], 
                                    width: int, height: int):
        """建立规则网格的邻居关系"""
        for i in range(height):
            for j in range(width):
                center_idx = i * width + j
                center_cell = cells[center_idx]
                
                # 8邻域
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        
                        ni, nj = i + di, j + dj
                        
                        if 0 <= ni < height and 0 <= nj < width:
                            neighbor_idx = ni * width + nj
                            neighbor_cell = cells[neighbor_idx]
                            center_cell.add_neighbor(neighbor_cell) 