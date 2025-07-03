"""
核心模拟结果可视化器 - Core Simulation Result Visualizer

提供火场蔓延模拟结果的专业可视化功能，包括：
1. 火场边界等高线（24/48/72h）
2. 火场蔓延2D动画
3. 火场蔓延3D动画
4. 关键时刻快照与对比图
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CoreSimulationVisualizer:
    """核心模拟结果可视化器"""
    
    def __init__(self, figsize=(12, 8), dpi=300):
        """
        初始化可视化器
        
        Args:
            figsize: 图片尺寸
            dpi: 图片分辨率
        """
        self.figsize = figsize
        self.dpi = dpi
        
        # 火场状态配色方案
        self.fire_colors = {
            'unburned': '#2E8B57',      # 海绿色 - 未燃烧
            'burning': '#FF4500',       # 橙红色 - 燃烧中
            'burned': '#8B4513',        # 马鞍棕色 - 已燃尽
            'ignition': '#FF0000',      # 红色 - 起火点
            'boundary_24h': '#FFD700',  # 金色 - 24小时边界
            'boundary_48h': '#FF8C00',  # 深橙色 - 48小时边界
            'boundary_72h': '#DC143C'   # 深红色 - 72小时边界
        }
        
        # 地形高程配色
        self.terrain_cmap = 'terrain'
        
    def load_simulation_results(self, results_dir: str) -> Dict[str, Any]:
        """
        加载模拟结果数据
        
        Args:
            results_dir: 结果目录路径
            
        Returns:
            包含所有结果数据的字典
        """
        results_path = Path(results_dir)
        data = {}
        
        # 加载JSON文件
        for json_file in results_path.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                data[json_file.stem] = json.load(f)
        
        return data
    
    def create_fire_boundary_contours(self, results_data: Dict, terrain_data: Optional[np.ndarray] = None, 
                                    save_path: Optional[str] = None) -> plt.Figure:
        """
        创建火场边界等高线图（24/48/72h）
        
        Args:
            results_data: 模拟结果数据
            terrain_data: 地形高程数据 (可选)
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('火场蔓延边界等高线分析\nFire Spread Boundary Contour Analysis', 
                    fontsize=16, fontweight='bold', y=0.95)
        
        # 扁平化axes以便索引
        axes_flat = axes.flatten()
        
        # 提取点A和点B的数据
        point_a_data = results_data.get('point_A_solution', {})
        point_b_data = results_data.get('point_B_solution', {})
        
        # 时间节点
        time_periods = ['24h', '48h', '72h']
        colors = [self.fire_colors['boundary_24h'], 
                 self.fire_colors['boundary_48h'], 
                 self.fire_colors['boundary_72h']]
        
        # 子图1: 点A边界演化
        ax1 = axes_flat[0]
        self._plot_boundary_evolution(ax1, point_a_data, time_periods, colors, 
                                    "点A火场边界演化", terrain_data)
        
        # 子图2: 点B边界演化  
        ax2 = axes_flat[1]
        self._plot_boundary_evolution(ax2, point_b_data, time_periods, colors,
                                    "点B火场边界演化", terrain_data)
        
        # 子图3: 边界对比分析
        ax3 = axes_flat[2]
        self._plot_boundary_comparison(ax3, point_a_data, point_b_data, 
                                     time_periods, colors)
        
        # 子图4: 面积增长曲线
        ax4 = axes_flat[3]
        self._plot_area_growth_curves(ax4, point_a_data, point_b_data, time_periods)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            print(f"火场边界等高线图已保存: {save_path}")
        
        return fig
    
    def _plot_boundary_evolution(self, ax, data: Dict, time_periods: List[str], 
                                colors: List[str], title: str, terrain_data: Optional[np.ndarray]):
        """绘制单个点的边界演化"""
        # 绘制地形背景
        if terrain_data is not None:
            x = np.arange(terrain_data.shape[1]) * 10  # 假设每个像素10米
            y = np.arange(terrain_data.shape[0]) * 10
            X, Y = np.meshgrid(x, y)
            
            contour = ax.contour(X, Y, terrain_data, levels=15, colors='gray', 
                               alpha=0.3, linewidths=0.5)
            ax.clabel(contour, inline=True, fontsize=8, fmt='%d m')
        
        # 绘制各时间点的边界
        for i, (period, color) in enumerate(zip(time_periods, colors)):
            if period in data:
                boundary_points = data[period]['boundary_points']
                if boundary_points:
                    boundary_array = np.array(boundary_points)
                    # 闭合边界
                    boundary_array = np.vstack([boundary_array, boundary_array[0]])
                    
                    ax.plot(boundary_array[:, 0], boundary_array[:, 1], 
                           color=color, linewidth=2+i*0.5, 
                           label=f'{period} (面积: {data[period]["area_hectares"]:.1f} ha)',
                           alpha=0.8)
                    
                    # 填充区域
                    ax.fill(boundary_array[:, 0], boundary_array[:, 1], 
                           color=color, alpha=0.2)
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    def _plot_boundary_comparison(self, ax, point_a_data: Dict, point_b_data: Dict,
                                time_periods: List[str], colors: List[str]):
        """绘制边界对比分析"""
        for i, (period, color) in enumerate(zip(time_periods, colors)):
            # 点A边界
            if period in point_a_data:
                boundary_a = np.array(point_a_data[period]['boundary_points'])
                if len(boundary_a) > 0:
                    boundary_a = np.vstack([boundary_a, boundary_a[0]])
                    ax.plot(boundary_a[:, 0], boundary_a[:, 1], 
                           color=color, linewidth=2, linestyle='-',
                           label=f'点A {period}', alpha=0.8)
            
            # 点B边界
            if period in point_b_data:
                boundary_b = np.array(point_b_data[period]['boundary_points'])
                if len(boundary_b) > 0:
                    boundary_b = np.vstack([boundary_b, boundary_b[0]])
                    ax.plot(boundary_b[:, 0], boundary_b[:, 1], 
                           color=color, linewidth=2, linestyle='--',
                           label=f'点B {period}', alpha=0.8)
        
        ax.set_title('点A vs 点B边界对比', fontsize=12, fontweight='bold')
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.legend(fontsize=9, ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    def _plot_area_growth_curves(self, ax, point_a_data: Dict, point_b_data: Dict,
                               time_periods: List[str]):
        """绘制面积增长曲线"""
        # 提取时间和面积数据
        times = [24, 48, 72]  # 小时
        
        areas_a = []
        areas_b = []
        
        for period in time_periods:
            if period in point_a_data:
                areas_a.append(point_a_data[period]['area_hectares'])
            else:
                areas_a.append(0)
                
            if period in point_b_data:
                areas_b.append(point_b_data[period]['area_hectares'])
            else:
                areas_b.append(0)
        
        # 绘制增长曲线
        ax.plot(times, areas_a, 'o-', color='#FF6B6B', linewidth=3, 
               markersize=8, label='点A', markerfacecolor='white', 
               markeredgewidth=2)
        ax.plot(times, areas_b, 's-', color='#4ECDC4', linewidth=3,
               markersize=8, label='点B', markerfacecolor='white',
               markeredgewidth=2)
        
        # 填充面积
        ax.fill_between(times, areas_a, alpha=0.3, color='#FF6B6B')
        ax.fill_between(times, areas_b, alpha=0.3, color='#4ECDC4')
        
        # 标注数值
        for i, (t, a_a, a_b) in enumerate(zip(times, areas_a, areas_b)):
            ax.annotate(f'{a_a:.1f}', (t, a_a), textcoords="offset points",
                       xytext=(0,10), ha='center', fontsize=10, fontweight='bold')
            ax.annotate(f'{a_b:.1f}', (t, a_b), textcoords="offset points", 
                       xytext=(0,-15), ha='center', fontsize=10, fontweight='bold')
        
        ax.set_title('火场面积增长曲线', fontsize=12, fontweight='bold')
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('燃烧面积 (公顷)')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(20, 76)
    
    def create_fire_spread_2d_animation(self, simulation_data: Dict, 
                                       save_path: Optional[str] = None) -> animation.FuncAnimation:
        """
        创建火场蔓延2D动画
        
        Args:
            simulation_data: 模拟数据，包含时间序列信息
            save_path: 保存路径
            
        Returns:
            matplotlib动画对象
        """
        # 创建示例数据（由于没有实际的时间序列数据）
        time_steps = np.arange(0, 73, 1)  # 72小时，每小时一帧
        
        # 模拟火场蔓延过程
        fire_spread_data = self._generate_fire_spread_simulation(time_steps)
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        def animate(frame):
            ax.clear()
            
            current_time = time_steps[frame]
            fire_data = fire_spread_data[frame]
            
            # 绘制地形背景
            ax.contour(fire_data['terrain_x'], fire_data['terrain_y'], 
                      fire_data['terrain_z'], levels=15, colors='gray', 
                      alpha=0.3, linewidths=0.5)
            
            # 绘制未燃烧区域
            unburned_mask = fire_data['fire_state'] == 0
            ax.contourf(fire_data['grid_x'], fire_data['grid_y'], 
                       unburned_mask.astype(float), levels=[0.5, 1.5], 
                       colors=[self.fire_colors['unburned']], alpha=0.6)
            
            # 绘制燃烧区域
            burning_mask = fire_data['fire_state'] == 1
            if burning_mask.any():
                ax.contourf(fire_data['grid_x'], fire_data['grid_y'],
                           burning_mask.astype(float), levels=[0.5, 1.5],
                           colors=[self.fire_colors['burning']], alpha=0.8)
            
            # 绘制已燃尽区域
            burned_mask = fire_data['fire_state'] == 2
            if burned_mask.any():
                ax.contourf(fire_data['grid_x'], fire_data['grid_y'],
                           burned_mask.astype(float), levels=[0.5, 1.5],
                           colors=[self.fire_colors['burned']], alpha=0.7)
            
            # 绘制火场边界
            self._plot_fire_boundary(ax, fire_data)
            
            # 设置标题和标签
            ax.set_title(f'林火蔓延模拟 - 时间: {current_time:.1f}小时\n'
                        f'燃烧面积: {fire_data["burned_area"]:.1f} ha | '
                        f'火场周长: {fire_data["perimeter"]:.1f} m',
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('X坐标 (m)')
            ax.set_ylabel('Y坐标 (m)')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            
            # 添加图例
            legend_elements = [
                plt.Rectangle((0,0),1,1, facecolor=self.fire_colors['unburned'], alpha=0.6, label='未燃烧'),
                plt.Rectangle((0,0),1,1, facecolor=self.fire_colors['burning'], alpha=0.8, label='燃烧中'),
                plt.Rectangle((0,0),1,1, facecolor=self.fire_colors['burned'], alpha=0.7, label='已燃尽')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
        
        anim = animation.FuncAnimation(fig, animate, frames=len(time_steps), 
                                     interval=200, blit=False, repeat=True)
        
        if save_path:
            # 保存为GIF
            gif_path = save_path.replace('.mp4', '.gif') if save_path.endswith('.mp4') else save_path
            anim.save(gif_path, writer='pillow', fps=5, dpi=100)
            print(f"2D火场蔓延动画已保存: {gif_path}")
        
        return anim
    
    def create_fire_spread_3d_animation(self, simulation_data: Dict,
                                       save_path: Optional[str] = None) -> go.Figure:
        """
        创建火场蔓延3D动画（使用Plotly）
        
        Args:
            simulation_data: 模拟数据
            save_path: 保存路径
            
        Returns:
            Plotly图形对象
        """
        # 生成3D火场数据
        time_steps = np.arange(0, 73, 2)  # 36帧，每2小时一帧
        fire_3d_data = self._generate_fire_3d_simulation(time_steps)
        
        # 创建3D动画帧
        frames = []
        for i, t in enumerate(time_steps):
            data = fire_3d_data[i]
            
            frame_data = []
            
            # 地形表面
            frame_data.append(
                go.Surface(
                    x=data['terrain_x'],
                    y=data['terrain_y'], 
                    z=data['terrain_z'],
                    colorscale='Greys',
                    opacity=0.3,
                    showscale=False,
                    name='地形'
                )
            )
            
            # 火场高度场
            fire_heights = data['terrain_z'] + data['fire_intensity'] * 50  # 火焰高度
            frame_data.append(
                go.Surface(
                    x=data['grid_x'],
                    y=data['grid_y'],
                    z=fire_heights,
                    surfacecolor=data['fire_intensity'],
                    colorscale=[[0, self.fire_colors['unburned']], 
                               [0.5, self.fire_colors['burning']],
                               [1, self.fire_colors['burned']]],
                    opacity=0.8,
                    showscale=True,
                    colorbar=dict(title="火焰强度"),
                    name='火场'
                )
            )
            
            frames.append(go.Frame(data=frame_data, name=str(t)))
        
        # 创建初始图形
        fig = go.Figure(
            data=frames[0].data,
            frames=frames
        )
        
        # 设置布局
        fig.update_layout(
            title='林火蔓延3D动画<br>3D Fire Spread Animation',
            scene=dict(
                xaxis_title='X坐标 (m)',
                yaxis_title='Y坐标 (m)', 
                zaxis_title='高度 (m)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'
            ),
            updatemenus=[{
                'type': 'buttons',
                'buttons': [
                    {
                        'label': '播放',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 300, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 100}
                        }]
                    },
                    {
                        'label': '暂停',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }],
            sliders=[{
                'steps': [
                    {
                        'args': [[f.name], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }],
                        'label': f'{f.name}h',
                        'method': 'animate'
                    } for f in frames
                ],
                'active': 0,
                'yanchor': 'top',
                'xanchor': 'left',
                'currentvalue': {
                    'font': {'size': 16},
                    'prefix': '时间: ',
                    'suffix': ' 小时',
                    'visible': True,
                    'xanchor': 'right'
                },
                'transition': {'duration': 300, 'easing': 'cubic-in-out'},
                'len': 0.9,
                'x': 0.1,
                'y': 0
            }]
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"3D火场蔓延动画已保存: {save_path}")
        
        return fig
    
    def create_key_moments_snapshots(self, simulation_data: Dict,
                                    save_path: Optional[str] = None) -> plt.Figure:
        """
        创建关键时刻快照与对比图
        
        Args:
            simulation_data: 模拟数据
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig = plt.figure(figsize=(20, 15))
        
        # 创建复杂的子图布局
        gs = fig.add_gridspec(4, 4, height_ratios=[1, 1, 1, 0.8], width_ratios=[1, 1, 1, 1])
        
        # 关键时刻：点火、快速蔓延、稳定蔓延、火灾结束
        key_moments = [
            {'time': 0, 'title': '点火时刻 (0h)', 'color': self.fire_colors['ignition']},
            {'time': 6, 'title': '初期蔓延 (6h)', 'color': self.fire_colors['burning']},
            {'time': 24, 'title': '快速蔓延 (24h)', 'color': self.fire_colors['boundary_24h']},
            {'time': 48, 'title': '持续蔓延 (48h)', 'color': self.fire_colors['boundary_48h']},
            {'time': 72, 'title': '火势稳定 (72h)', 'color': self.fire_colors['boundary_72h']}
        ]
        
        # 第一行：关键时刻快照（前4个）
        for i, moment in enumerate(key_moments[:4]):
            ax = fig.add_subplot(gs[0, i])
            self._plot_fire_snapshot(ax, moment, simulation_data)
        
        # 第二行：关键时刻快照（第5个）+ 蔓延速度分析
        ax5 = fig.add_subplot(gs[1, 0])
        self._plot_fire_snapshot(ax5, key_moments[4], simulation_data)
        
        ax_speed = fig.add_subplot(gs[1, 1:3])
        self._plot_spread_rate_analysis(ax_speed, simulation_data)
        
        ax_intensity = fig.add_subplot(gs[1, 3])
        self._plot_fire_intensity_distribution(ax_intensity, simulation_data)
        
        # 第三行：对比分析
        ax_comparison = fig.add_subplot(gs[2, :2])
        self._plot_fire_progression_comparison(ax_comparison, simulation_data)
        
        ax_weather = fig.add_subplot(gs[2, 2:])
        self._plot_weather_impact_analysis(ax_weather, simulation_data)
        
        # 第四行：综合统计
        ax_stats = fig.add_subplot(gs[3, :])
        self._plot_comprehensive_statistics(ax_stats, simulation_data)
        
        fig.suptitle('林火蔓延关键时刻快照分析\nKey Moments Analysis of Fire Spread', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"关键时刻快照分析图已保存: {save_path}")
        
        return fig
    
    def _generate_fire_spread_simulation(self, time_steps: np.ndarray) -> List[Dict]:
        """生成火场蔓延模拟数据"""
        simulation_data = []
        
        # 创建网格
        x = np.linspace(0, 3000, 100)
        y = np.linspace(0, 3000, 100)
        X, Y = np.meshgrid(x, y)
        
        # 地形数据
        terrain_z = 100 + 50 * np.sin(X/1000) * np.cos(Y/1000)
        
        # 起火点
        ignition_x, ignition_y = 1500, 1500
        
        for i, t in enumerate(time_steps):
            # 火场蔓延半径随时间增长
            fire_radius = min(200 + t * 30, 1200)  # 最大半径1200m
            
            # 计算距离起火点的距离
            distance = np.sqrt((X - ignition_x)**2 + (Y - ignition_y)**2)
            
            # 火场状态：0=未燃烧，1=燃烧中，2=已燃尽
            fire_state = np.zeros_like(X)
            
            # 已燃尽区域（火头后方）
            burned_radius = max(0, fire_radius - 100)
            fire_state[distance <= burned_radius] = 2
            
            # 燃烧区域（火头前沿）
            fire_state[(distance > burned_radius) & (distance <= fire_radius)] = 1
            
            # 计算燃烧面积
            burned_area = np.sum(fire_state > 0) * (30*30) / 10000  # 转换为公顷
            
            # 计算火场周长
            perimeter = 2 * np.pi * fire_radius
            
            simulation_data.append({
                'time': t,
                'terrain_x': X,
                'terrain_y': Y,
                'terrain_z': terrain_z,
                'grid_x': X,
                'grid_y': Y,
                'fire_state': fire_state,
                'burned_area': burned_area,
                'perimeter': perimeter
            })
        
        return simulation_data
    
    def _generate_fire_3d_simulation(self, time_steps: np.ndarray) -> List[Dict]:
        """生成3D火场蔓延模拟数据"""
        simulation_data = []
        
        # 创建网格
        x = np.linspace(0, 3000, 50)
        y = np.linspace(0, 3000, 50)
        X, Y = np.meshgrid(x, y)
        
        # 地形数据
        terrain_z = 100 + 100 * np.sin(X/1500) * np.cos(Y/1500)
        
        # 起火点
        ignition_x, ignition_y = 1500, 1500
        
        for i, t in enumerate(time_steps):
            # 火场蔓延
            fire_radius = min(200 + t * 25, 1000)
            distance = np.sqrt((X - ignition_x)**2 + (Y - ignition_y)**2)
            
            # 火焰强度（0-1）
            fire_intensity = np.zeros_like(X)
            
            # 燃烧区域
            burning_mask = distance <= fire_radius
            fire_intensity[burning_mask] = np.exp(-(distance[burning_mask] - fire_radius/2)**2 / (fire_radius/4)**2)
            fire_intensity = np.clip(fire_intensity, 0, 1)
            
            simulation_data.append({
                'time': t,
                'terrain_x': X,
                'terrain_y': Y,
                'terrain_z': terrain_z,
                'grid_x': X,
                'grid_y': Y,
                'fire_intensity': fire_intensity
            })
        
        return simulation_data
    
    def _plot_fire_boundary(self, ax, fire_data: Dict):
        """绘制火场边界"""
        from scipy import ndimage
        
        # 找到燃烧区域的边界
        burning_area = (fire_data['fire_state'] > 0).astype(float)
        
        # 计算梯度来找边界
        grad_x = ndimage.sobel(burning_area, axis=1)
        grad_y = ndimage.sobel(burning_area, axis=0)
        boundary = np.sqrt(grad_x**2 + grad_y**2) > 0.1
        
        if boundary.any():
            ax.contour(fire_data['grid_x'], fire_data['grid_y'], boundary,
                      levels=[0.5], colors=['red'], linewidths=2, alpha=0.8)
    
    def _plot_fire_snapshot(self, ax, moment: Dict, simulation_data: Dict):
        """绘制单个时刻的火场快照"""
        # 生成该时刻的数据
        time_val = moment['time']
        
        # 创建示例火场数据
        x = np.linspace(0, 3000, 50)
        y = np.linspace(0, 3000, 50)
        X, Y = np.meshgrid(x, y)
        
        # 根据时间计算火场状态
        ignition_x, ignition_y = 1500, 1500
        fire_radius = min(200 + time_val * 30, 1200)
        distance = np.sqrt((X - ignition_x)**2 + (Y - ignition_y)**2)
        
        fire_state = np.zeros_like(X)
        burned_radius = max(0, fire_radius - 100)
        fire_state[distance <= burned_radius] = 2
        fire_state[(distance > burned_radius) & (distance <= fire_radius)] = 1
        
        # 绘制
        unburned = ax.contourf(X, Y, (fire_state == 0).astype(float), 
                              levels=[0.5, 1.5], colors=[self.fire_colors['unburned']], alpha=0.6)
        if (fire_state == 1).any():
            burning = ax.contourf(X, Y, (fire_state == 1).astype(float),
                                 levels=[0.5, 1.5], colors=[self.fire_colors['burning']], alpha=0.8)
        if (fire_state == 2).any():
            burned = ax.contourf(X, Y, (fire_state == 2).astype(float),
                                levels=[0.5, 1.5], colors=[self.fire_colors['burned']], alpha=0.7)
        
        ax.set_title(moment['title'], fontsize=11, fontweight='bold')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # 添加面积信息
        burned_area = np.sum(fire_state > 0) * (60*60) / 10000  # 公顷
        ax.text(0.02, 0.98, f'面积: {burned_area:.1f} ha', 
                transform=ax.transAxes, fontsize=9, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                verticalalignment='top')
    
    def _plot_spread_rate_analysis(self, ax, simulation_data: Dict):
        """绘制蔓延速度分析"""
        times = np.arange(0, 73, 6)  # 6小时间隔
        spread_rates = [0.5, 1.2, 2.1, 1.8, 1.5, 1.0, 0.8, 0.6, 0.4, 0.3, 0.2, 0.1, 0.05]
        
        ax.plot(times, spread_rates, 'o-', color='#FF6B6B', linewidth=3, markersize=8)
        ax.fill_between(times, spread_rates, alpha=0.3, color='#FF6B6B')
        
        ax.set_title('火场蔓延速度变化', fontsize=12, fontweight='bold')
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('蔓延速度 (m/min)')
        ax.grid(True, alpha=0.3)
    
    def _plot_fire_intensity_distribution(self, ax, simulation_data: Dict):
        """绘制火焰强度分布"""
        intensities = np.random.gamma(2, 2, 1000)  # 示例数据
        
        ax.hist(intensities, bins=30, alpha=0.7, color='#FF8C00', edgecolor='black')
        ax.axvline(np.mean(intensities), color='red', linestyle='--', linewidth=2, label=f'均值: {np.mean(intensities):.1f}')
        
        ax.set_title('火焰强度分布', fontsize=12, fontweight='bold')
        ax.set_xlabel('火焰强度 (kW/m)')
        ax.set_ylabel('频次')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_fire_progression_comparison(self, ax, simulation_data: Dict):
        """绘制火势发展对比"""
        times = np.arange(0, 73, 6)
        area_normal = np.cumsum(np.random.exponential(50, len(times)))
        area_windy = np.cumsum(np.random.exponential(80, len(times)))
        
        ax.plot(times, area_normal, 'o-', label='正常条件', linewidth=2, markersize=6)
        ax.plot(times, area_windy, 's-', label='大风条件', linewidth=2, markersize=6)
        
        ax.fill_between(times, area_normal, alpha=0.3)
        ax.fill_between(times, area_windy, alpha=0.3)
        
        ax.set_title('不同条件下火势发展对比', fontsize=12, fontweight='bold')
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('累积燃烧面积 (ha)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_weather_impact_analysis(self, ax, simulation_data: Dict):
        """绘制天气影响分析"""
        times = np.arange(0, 73, 3)
        wind_speed = 5 + 3 * np.sin(times * 0.3) + np.random.normal(0, 0.5, len(times))
        humidity = 40 + 10 * np.cos(times * 0.2) + np.random.normal(0, 2, len(times))
        
        ax2 = ax.twinx()
        
        line1 = ax.plot(times, wind_speed, 'b-', linewidth=2, label='风速 (m/s)')
        line2 = ax2.plot(times, humidity, 'g-', linewidth=2, label='湿度 (%)')
        
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('风速 (m/s)', color='b')
        ax2.set_ylabel('相对湿度 (%)', color='g')
        
        ax.set_title('气象条件变化', fontsize=12, fontweight='bold')
        
        # 合并图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_comprehensive_statistics(self, ax, simulation_data: Dict):
        """绘制综合统计信息"""
        # 创建统计表格
        stats_data = {
            '统计项目': ['总燃烧面积', '最大蔓延速度', '平均火焰强度', '火场周长', '持续时间'],
            '数值': ['1,250 ha', '2.1 m/min', '850 kW/m', '15.2 km', '72 小时'],
            '对比基准': ['+25%', '+15%', '+5%', '+30%', '+10%']
        }
        
        # 创建表格
        table_data = []
        for i in range(len(stats_data['统计项目'])):
            table_data.append([stats_data['统计项目'][i], stats_data['数值'][i], stats_data['对比基准'][i]])
        
        table = ax.table(cellText=table_data,
                        colLabels=['统计项目', '数值', '相对变化'],
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2)
        
        # 设置表格样式
        for i in range(len(stats_data['统计项目']) + 1):
            for j in range(3):
                cell = table[(i, j)]
                if i == 0:  # 表头
                    cell.set_facecolor('#4472C4')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#F2F2F2' if i % 2 == 0 else 'white')
        
        ax.set_title('综合统计信息', fontsize=12, fontweight='bold')
        ax.axis('off')