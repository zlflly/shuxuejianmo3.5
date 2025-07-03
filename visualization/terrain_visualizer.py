"""
地形可视化器 - 生成三维地形和元胞网格图
Terrain Visualizer - Generate 3D Terrain and Cell Grid Plots
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Optional, Tuple
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap

class TerrainVisualizer:
    """地形可视化器"""
    
    def __init__(self, figure_size: Tuple[int, int] = (12, 8), dpi: int = 150):
        """
        初始化地形可视化器
        
        Args:
            figure_size: 图形尺寸
            dpi: 图形分辨率
        """
        self.figure_size = figure_size
        self.dpi = dpi
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_3d_terrain(self, surface_cells: List, title: str = "三维地形图", 
                       save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制三维地形图
        
        Args:
            surface_cells: 地表元胞列表
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
        ax = fig.add_subplot(111, projection='3d')
        
        # 提取位置和高度数据
        positions = np.array([cell.static.position for cell in surface_cells])
        x_coords = positions[:, 0]
        y_coords = positions[:, 1]
        z_coords = positions[:, 2]
        
        # 创建网格数据
        # 假设是规则网格，找出网格尺寸
        unique_x = np.unique(x_coords)
        unique_y = np.unique(y_coords)
        
        X, Y = np.meshgrid(unique_x, unique_y)
        Z = np.zeros_like(X)
        
        # 填充高度数据
        for cell in surface_cells:
            x, y, z = cell.static.position
            i = np.where(unique_y == y)[0][0]
            j = np.where(unique_x == x)[0][0]
            Z[i, j] = z
        
        # 绘制地表
        surf = ax.plot_surface(X, Y, Z, cmap='terrain', alpha=0.8, 
                              linewidth=0, antialiased=True)
        
        # 绘制等高线投影
        ax.contour(X, Y, Z, zdir='z', offset=Z.min()-10, cmap='terrain', alpha=0.5)
        
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_zlabel('海拔高度 (m)')
        ax.set_title(title)
        
        # 添加颜色条
        fig.colorbar(surf, shrink=0.5, aspect=20, label='海拔 (m)')
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def plot_slope_analysis(self, surface_cells: List, title: str = "坡度分析图", 
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制坡度分析图
        
        Args:
            surface_cells: 地表元胞列表
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=self.dpi)
        
        # 提取坡度数据
        positions = np.array([cell.static.position for cell in surface_cells])
        slopes = np.array([np.degrees(cell.static.slope) for cell in surface_cells])
        aspects = np.array([np.degrees(cell.static.aspect) for cell in surface_cells])
        
        x_coords = positions[:, 0]
        y_coords = positions[:, 1]
        
        # 坡度分布图
        scatter1 = ax1.scatter(x_coords, y_coords, c=slopes, cmap='YlOrRd', s=1)
        ax1.set_xlabel('X坐标 (m)')
        ax1.set_ylabel('Y坐标 (m)')
        ax1.set_title('坡度分布')
        ax1.set_aspect('equal')
        fig.colorbar(scatter1, ax=ax1, label='坡度 (度)')
        
        # 坡向分布图
        scatter2 = ax2.scatter(x_coords, y_coords, c=aspects, cmap='hsv', s=1)
        ax2.set_xlabel('X坐标 (m)')
        ax2.set_ylabel('Y坐标 (m)')
        ax2.set_title('坡向分布')
        ax2.set_aspect('equal')
        fig.colorbar(scatter2, ax=ax2, label='坡向 (度)')
        
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def plot_cell_grid_overview(self, surface_cells: List, canopy_cells: List = None,
                               title: str = "元胞网格概览", 
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制元胞网格概览图
        
        Args:
            surface_cells: 地表元胞列表
            canopy_cells: 树冠元胞列表（可选）
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig, axes = plt.subplots(1, 2 if canopy_cells else 1, 
                                figsize=(16 if canopy_cells else 8, 8), dpi=self.dpi)
        
        if not canopy_cells:
            axes = [axes]
        
        # 绘制地表层
        self._plot_cell_layer(axes[0], surface_cells, "地表层元胞状态")
        
        # 绘制树冠层（如果有）
        if canopy_cells:
            self._plot_cell_layer(axes[1], canopy_cells, "树冠层元胞状态")
        
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def _plot_cell_layer(self, ax, cells: List, layer_title: str):
        """绘制单个层的元胞状态"""
        # 提取位置和状态数据
        positions = np.array([cell.static.position for cell in cells])
        states = [cell.dynamic.state.name for cell in cells]
        
        x_coords = positions[:, 0]
        y_coords = positions[:, 1]
        
        # 定义状态颜色映射
        state_colors = {
            'UNBURNED': 'green',
            'SURFACE_FIRE': 'orange', 
            'CROWN_FIRE': 'red',
            'BURNED_OUT': 'gray'
        }
        
        # 为每个状态绘制散点
        for state, color in state_colors.items():
            mask = [s == state for s in states]
            if any(mask):
                x_state = x_coords[mask]
                y_state = y_coords[mask]
                ax.scatter(x_state, y_state, c=color, s=1, label=state, alpha=0.7)
        
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_title(layer_title)
        ax.legend()
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
    
    def plot_ignition_points_diagram(self, terrain_config: dict, ignition_points: dict,
                                   title: str = "起火点位置与地形分区示意图", 
                                   save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制起火点位置示意图
        
        Args:
            terrain_config: 地形配置参数
            ignition_points: 起火点配置
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # 绘制地形轮廓
        width = terrain_config.get('width', 300)
        height = terrain_config.get('height', 300)
        cell_size = terrain_config.get('cell_size', 10.0)
        intersection_distance = terrain_config.get('intersection_distance', 1500.0)
        
        # 绘制平地和山坡区域（明确区分）
        flat_rect = patches.Rectangle((0, 0), width * cell_size, intersection_distance,
                                    linewidth=2, edgecolor='green', facecolor='lightgreen',
                                    alpha=0.4, label='平地区域 (坡度=0°)')
        ax.add_patch(flat_rect)
        
        slope_rect = patches.Rectangle((0, intersection_distance), width * cell_size, 
                                     height * cell_size - intersection_distance,
                                     linewidth=2, edgecolor='brown', facecolor='lightsalmon',
                                     alpha=0.4, label='山坡区域 (坡度=30°)')
        ax.add_patch(slope_rect)
        
        # 绘制地形分界线（重点标识）
        ax.axhline(y=intersection_distance, color='red', linestyle='-', linewidth=3, 
                  label=f'地形分界线 (y={intersection_distance}m)', zorder=10)
        
        # 绘制起火点并标识其地形分区
        for point_name, point_config in ignition_points.items():
            x, y = point_config['position']
            radius = point_config['radius']
            
            # 判断起火点所在地形分区
            point_terrain = "平地" if y <= intersection_distance else "山坡"
            point_color = 'darkgreen' if y <= intersection_distance else 'darkred'
            
            # 起火点标记（根据地形分区选择颜色）
            ax.plot(x, y, 'o', color=point_color, markersize=15, 
                   markeredgecolor='black', markeredgewidth=2,
                   label=f'{point_name}: ({x}, {y}) - {point_terrain}', zorder=20)
            
            # 起火影响范围
            circle = patches.Circle((x, y), radius, fill=False, 
                                  edgecolor=point_color, linewidth=2, linestyle=':', alpha=0.8)
            ax.add_patch(circle)
            
            # 标注（包含地形信息）
            ax.annotate(f'{point_name}\n({point_terrain})', (x, y), xytext=(15, 15), 
                       textcoords='offset points', fontsize=11, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        # 设置坐标轴范围
        ax.set_xlim(0, width * cell_size)
        ax.set_ylim(0, height * cell_size)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def create_terrain_summary_report(self, surface_cells: List, terrain_config: dict,
                                    output_dir: str = "figures"):
        """
        创建地形总结报告
        
        Args:
            surface_cells: 地表元胞列表
            terrain_config: 地形配置
            output_dir: 输出目录
        """
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("正在生成地形分析报告...")
        
        # 三维地形图
        self.plot_3d_terrain(surface_cells, "理想几何地形 - 三维视图",
                           str(output_path / "terrain_3d.png"))
        
        # 坡度分析图
        self.plot_slope_analysis(surface_cells, "地形坡度和坡向分析",
                               str(output_path / "slope_analysis.png"))
        
        # 起火点示意图
        ignition_points = {
            'point_A': {'position': [1500.0, 1500.0], 'radius': 15.0},
            'point_B': {'position': [1500.0, 2000.0], 'radius': 15.0}
        }
        self.plot_ignition_points_diagram(terrain_config, ignition_points,
                                        "起火点位置和地形示意图",
                                        str(output_path / "ignition_points.png"))
        
        print(f"✅ 地形分析报告已保存到: {output_path}") 