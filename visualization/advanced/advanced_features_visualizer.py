"""
高级特征与多层耦合可视化器 - Advanced Features Visualizer

提供火场蔓延高级特征的专业可视化功能，包括：
1. 地表火/树冠火分层对比动画
2. 动态堆叠面积图（各状态元胞数量变化）
3. 飞火/跳火事件可视化
4. 多尺度视角切换（全局-局部-地面）
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Arrow
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class AdvancedFeaturesVisualizer:
    """高级特征与多层耦合可视化器"""
    
    def __init__(self, figsize=(12, 8), dpi=300):
        """
        初始化可视化器
        
        Args:
            figsize: 图片尺寸
            dpi: 图片分辨率
        """
        self.figsize = figsize
        self.dpi = dpi
        
        # 分层火场配色方案
        self.layer_colors = {
            'surface_unburned': '#2E8B57',      # 地表未燃烧
            'surface_burning': '#FF4500',       # 地表燃烧中
            'surface_burned': '#8B4513',        # 地表已燃尽
            'canopy_unburned': '#228B22',       # 树冠未燃烧
            'canopy_burning': '#FF0000',        # 树冠燃烧中
            'canopy_burned': '#A0522D',         # 树冠已燃尽
            'spotting': '#FFD700',              # 飞火点
            'ember': '#FFA500'                  # 飞火余烬
        }
        
        # 状态统计配色
        self.stats_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
    
    def create_layered_fire_comparison(self, simulation_data: Dict,
                                     save_path: Optional[str] = None) -> plt.Figure:
        """
        创建地表火/树冠火分层对比动画
        
        Args:
            simulation_data: 模拟数据
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig = plt.figure(figsize=(18, 12))
        
        # 创建子图布局
        gs = fig.add_gridspec(3, 3, height_ratios=[1.5, 1.5, 1], width_ratios=[1, 1, 1])
        
        # 生成分层火场数据
        time_steps = np.arange(0, 73, 6)  # 12个时间点
        layered_data = self._generate_layered_fire_data(time_steps)
        
        # 第一行：地表火与树冠火对比
        ax_surface = fig.add_subplot(gs[0, 0])
        ax_canopy = fig.add_subplot(gs[0, 1])
        ax_combined = fig.add_subplot(gs[0, 2])
        
        self._plot_layered_snapshots(ax_surface, ax_canopy, ax_combined, layered_data[6])  # 36小时时刻
        
        # 第二行：火势强度对比
        ax_intensity = fig.add_subplot(gs[1, :2])
        ax_coupling = fig.add_subplot(gs[1, 2])
        
        self._plot_fire_intensity_comparison(ax_intensity, layered_data)
        self._plot_surface_canopy_coupling(ax_coupling, layered_data)
        
        # 第三行：统计分析
        ax_stats = fig.add_subplot(gs[2, :])
        self._plot_layered_statistics(ax_stats, layered_data)
        
        fig.suptitle('地表火与树冠火分层对比分析\nSurface vs Crown Fire Layered Analysis', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"分层火场对比分析图已保存: {save_path}")
        
        return fig
    
    def create_dynamic_area_stacking(self, simulation_data: Dict,
                                   save_path: Optional[str] = None) -> plt.Figure:
        """
        创建动态堆叠面积图（各状态元胞数量变化）
        
        Args:
            simulation_data: 模拟数据
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('火场状态动态变化堆叠分析\nDynamic Fire State Stacking Analysis', 
                    fontsize=16, fontweight='bold', y=0.95)
        
        # 生成动态数据
        time_steps = np.arange(0, 73, 1)  # 每小时一个数据点
        dynamic_data = self._generate_dynamic_stacking_data(time_steps)
        
        # 子图1: 地表火状态堆叠
        ax1 = axes[0, 0]
        self._plot_surface_fire_stacking(ax1, dynamic_data)
        
        # 子图2: 树冠火状态堆叠
        ax2 = axes[0, 1]
        self._plot_canopy_fire_stacking(ax2, dynamic_data)
        
        # 子图3: 总体燃烧面积变化
        ax3 = axes[1, 0]
        self._plot_total_area_progression(ax3, dynamic_data)
        
        # 子图4: 燃烧速率分析
        ax4 = axes[1, 1]
        self._plot_burning_rate_analysis(ax4, dynamic_data)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"动态堆叠面积分析图已保存: {save_path}")
        
        return fig
    
    def create_spotting_events_visualization(self, simulation_data: Dict,
                                           save_path: Optional[str] = None) -> plt.Figure:
        """
        创建飞火/跳火事件可视化
        
        Args:
            simulation_data: 模拟数据
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig = plt.figure(figsize=(20, 14))
        
        # 创建复杂布局
        gs = fig.add_gridspec(3, 4, height_ratios=[1.5, 1, 1], width_ratios=[1, 1, 1, 1])
        
        # 生成飞火事件数据
        spotting_data = self._generate_spotting_events_data()
        
        # 第一行：飞火事件总览
        ax_main = fig.add_subplot(gs[0, :3])
        ax_legend = fig.add_subplot(gs[0, 3])
        
        self._plot_spotting_overview(ax_main, spotting_data)
        self._plot_spotting_legend(ax_legend)
        
        # 第二行：飞火距离分析
        ax_distance = fig.add_subplot(gs[1, :2])
        ax_frequency = fig.add_subplot(gs[1, 2:])
        
        self._plot_spotting_distance_analysis(ax_distance, spotting_data)
        self._plot_spotting_frequency_analysis(ax_frequency, spotting_data)
        
        # 第三行：风向影响与预测模型
        ax_wind = fig.add_subplot(gs[2, :2])
        ax_prediction = fig.add_subplot(gs[2, 2:])
        
        self._plot_wind_direction_impact(ax_wind, spotting_data)
        self._plot_spotting_prediction_model(ax_prediction, spotting_data)
        
        fig.suptitle('飞火事件综合分析\nSpotting Events Comprehensive Analysis', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"飞火事件分析图已保存: {save_path}")
        
        return fig
    
    def create_multiscale_perspective(self, simulation_data: Dict,
                                    save_path: Optional[str] = None) -> plt.Figure:
        """
        创建多尺度视角切换（全局-局部-地面）
        
        Args:
            simulation_data: 模拟数据
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig = plt.figure(figsize=(20, 16))
        
        # 创建多尺度布局
        gs = fig.add_gridspec(4, 4, height_ratios=[1.2, 1.2, 1, 0.8], width_ratios=[1, 1, 1, 1])
        
        # 生成多尺度数据
        multiscale_data = self._generate_multiscale_data()
        
        # 第一行：全局视角
        ax_global = fig.add_subplot(gs[0, :2])
        ax_global_3d = fig.add_subplot(gs[0, 2:], projection='3d')
        
        self._plot_global_perspective(ax_global, multiscale_data)
        self._plot_global_3d_perspective(ax_global_3d, multiscale_data)
        
        # 第二行：局部视角
        ax_local1 = fig.add_subplot(gs[1, 0])
        ax_local2 = fig.add_subplot(gs[1, 1])
        ax_local3 = fig.add_subplot(gs[1, 2])
        ax_local4 = fig.add_subplot(gs[1, 3])
        
        self._plot_local_perspectives(ax_local1, ax_local2, ax_local3, ax_local4, multiscale_data)
        
        # 第三行：地面视角
        ax_ground = fig.add_subplot(gs[2, :3])
        ax_profile = fig.add_subplot(gs[2, 3])
        
        self._plot_ground_perspective(ax_ground, multiscale_data)
        self._plot_vertical_profile(ax_profile, multiscale_data)
        
        # 第四行：尺度对比分析
        ax_comparison = fig.add_subplot(gs[3, :])
        self._plot_scale_comparison_analysis(ax_comparison, multiscale_data)
        
        fig.suptitle('多尺度视角分析\nMulti-Scale Perspective Analysis', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"多尺度视角分析图已保存: {save_path}")
        
        return fig
    
    def _generate_layered_fire_data(self, time_steps: np.ndarray) -> List[Dict]:
        """生成分层火场数据"""
        layered_data = []
        
        # 创建网格
        x = np.linspace(0, 3000, 60)
        y = np.linspace(0, 3000, 60)
        X, Y = np.meshgrid(x, y)
        
        # 起火点
        ignition_x, ignition_y = 1500, 1500
        
        for i, t in enumerate(time_steps):
            # 地表火蔓延
            surface_radius = min(200 + t * 25, 1000)
            distance = np.sqrt((X - ignition_x)**2 + (Y - ignition_y)**2)
            
            surface_state = np.zeros_like(X)
            surface_burned_radius = max(0, surface_radius - 80)
            surface_state[distance <= surface_burned_radius] = 2  # 已燃尽
            surface_state[(distance > surface_burned_radius) & (distance <= surface_radius)] = 1  # 燃烧中
            
            # 树冠火蔓延（延迟启动，速度较快）
            canopy_start_time = 12  # 12小时后开始树冠火
            if t >= canopy_start_time:
                canopy_radius = min(100 + (t - canopy_start_time) * 35, 800)
                canopy_state = np.zeros_like(X)
                canopy_burned_radius = max(0, canopy_radius - 60)
                canopy_state[distance <= canopy_burned_radius] = 2
                canopy_state[(distance > canopy_burned_radius) & (distance <= canopy_radius)] = 1
            else:
                canopy_state = np.zeros_like(X)
            
            # 火焰强度
            surface_intensity = np.zeros_like(X)
            canopy_intensity = np.zeros_like(X)
            
            surface_burning_mask = surface_state == 1
            if surface_burning_mask.any():
                surface_intensity[surface_burning_mask] = 0.7 + 0.3 * np.random.random(np.sum(surface_burning_mask))
            
            canopy_burning_mask = canopy_state == 1
            if canopy_burning_mask.any():
                canopy_intensity[canopy_burning_mask] = 0.8 + 0.2 * np.random.random(np.sum(canopy_burning_mask))
            
            layered_data.append({
                'time': t,
                'X': X,
                'Y': Y,
                'surface_state': surface_state,
                'canopy_state': canopy_state,
                'surface_intensity': surface_intensity,
                'canopy_intensity': canopy_intensity,
                'surface_area': np.sum(surface_state > 0) * (50*50) / 10000,  # 公顷
                'canopy_area': np.sum(canopy_state > 0) * (50*50) / 10000     # 公顷
            })
        
        return layered_data
    
    def _generate_dynamic_stacking_data(self, time_steps: np.ndarray) -> Dict:
        """生成动态堆叠数据"""
        # 各状态的元胞数量变化
        surface_unburned = []
        surface_burning = []
        surface_burned = []
        canopy_unburned = []
        canopy_burning = []
        canopy_burned = []
        
        total_cells = 3600  # 60x60网格
        
        for t in time_steps:
            # 地表火发展
            surface_burned_count = min(int(t * 8), total_cells // 2)
            surface_burning_count = min(int(t * 2), 200) if t < 60 else max(200 - int((t-60)*3), 0)
            surface_unburned_count = total_cells - surface_burned_count - surface_burning_count
            
            # 树冠火发展（延迟12小时）
            if t >= 12:
                canopy_burned_count = min(int((t-12) * 6), total_cells // 3)
                canopy_burning_count = min(int((t-12) * 1.5), 150) if t < 60 else max(150 - int((t-60)*2), 0)
                canopy_unburned_count = total_cells - canopy_burned_count - canopy_burning_count
            else:
                canopy_burned_count = 0
                canopy_burning_count = 0
                canopy_unburned_count = total_cells
            
            surface_unburned.append(surface_unburned_count)
            surface_burning.append(surface_burning_count)
            surface_burned.append(surface_burned_count)
            canopy_unburned.append(canopy_unburned_count)
            canopy_burning.append(canopy_burning_count)
            canopy_burned.append(canopy_burned_count)
        
        return {
            'time_steps': time_steps,
            'surface_unburned': np.array(surface_unburned),
            'surface_burning': np.array(surface_burning),
            'surface_burned': np.array(surface_burned),
            'canopy_unburned': np.array(canopy_unburned),
            'canopy_burning': np.array(canopy_burning),
            'canopy_burned': np.array(canopy_burned)
        }
    
    def _generate_spotting_events_data(self) -> Dict:
        """生成飞火事件数据"""
        np.random.seed(42)  # 保证可重现性
        
        # 飞火事件发生时间和位置
        num_events = 25
        event_times = np.random.uniform(6, 60, num_events)  # 6-60小时内发生
        
        # 主火场中心
        main_fire_x, main_fire_y = 1500, 1500
        
        # 飞火落点（考虑风向影响）
        wind_direction = 45  # 东北风
        wind_strength = 0.8
        
        spot_x = []
        spot_y = []
        spot_distances = []
        spot_success = []  # 是否成功点燃
        
        for i, t in enumerate(event_times):
            # 飞火距离（随时间和强度变化）
            base_distance = np.random.uniform(200, 800)
            wind_effect = wind_strength * base_distance * 0.3
            
            # 风向影响
            angle = np.random.normal(wind_direction, 30) * np.pi / 180
            distance = base_distance + wind_effect
            
            x = main_fire_x + distance * np.cos(angle)
            y = main_fire_y + distance * np.sin(angle)
            
            spot_x.append(x)
            spot_y.append(y)
            spot_distances.append(distance)
            
            # 成功概率（距离越远成功率越低）
            success_prob = max(0.1, 1 - distance / 1000)
            spot_success.append(np.random.random() < success_prob)
        
        return {
            'event_times': event_times,
            'spot_x': np.array(spot_x),
            'spot_y': np.array(spot_y),
            'spot_distances': np.array(spot_distances),
            'spot_success': np.array(spot_success),
            'main_fire_x': main_fire_x,
            'main_fire_y': main_fire_y,
            'wind_direction': wind_direction,
            'wind_strength': wind_strength
        }
    
    def _generate_multiscale_data(self) -> Dict:
        """生成多尺度数据"""
        # 全局尺度（整个模拟区域）
        global_x = np.linspace(0, 5000, 100)
        global_y = np.linspace(0, 5000, 100)
        Global_X, Global_Y = np.meshgrid(global_x, global_y)
        
        # 地形
        global_terrain = 200 + 150 * np.sin(Global_X/2000) * np.cos(Global_Y/2000)
        
        # 火场（多个火点）
        fire_centers = [(1500, 1500), (3200, 2800), (800, 3500)]
        global_fire = np.zeros_like(Global_X)
        
        for cx, cy in fire_centers:
            distance = np.sqrt((Global_X - cx)**2 + (Global_Y - cy)**2)
            fire_mask = distance <= 600
            global_fire[fire_mask] = 1
        
        # 局部尺度（重点区域放大）
        local_regions = [
            {'center': (1500, 1500), 'size': 800, 'title': '主火场核心区'},
            {'center': (3200, 2800), 'size': 600, 'title': '次火场区域'},
            {'center': (800, 3500), 'size': 500, 'title': '飞火点区域'},
            {'center': (2500, 1800), 'size': 400, 'title': '防火带区域'}
        ]
        
        # 地面尺度（植被类型、微地形）
        ground_x = np.linspace(1200, 1800, 50)
        ground_y = np.linspace(1200, 1800, 50)
        Ground_X, Ground_Y = np.meshgrid(ground_x, ground_y)
        
        # 植被类型分布
        vegetation_types = np.random.choice([1, 2, 3, 4], size=Ground_X.shape, 
                                          p=[0.3, 0.25, 0.25, 0.2])
        
        return {
            'global': {
                'X': Global_X,
                'Y': Global_Y,
                'terrain': global_terrain,
                'fire': global_fire
            },
            'local_regions': local_regions,
            'ground': {
                'X': Ground_X,
                'Y': Ground_Y,
                'vegetation': vegetation_types
            }
        }
    
    def _plot_layered_snapshots(self, ax_surface, ax_canopy, ax_combined, data):
        """绘制分层快照"""
        X, Y = data['X'], data['Y']
        
        # 地表火
        surface_unburned = ax_surface.contourf(X, Y, (data['surface_state'] == 0).astype(float),
                                             levels=[0.5, 1.5], colors=[self.layer_colors['surface_unburned']], alpha=0.6)
        if (data['surface_state'] == 1).any():
            surface_burning = ax_surface.contourf(X, Y, (data['surface_state'] == 1).astype(float),
                                                levels=[0.5, 1.5], colors=[self.layer_colors['surface_burning']], alpha=0.8)
        if (data['surface_state'] == 2).any():
            surface_burned = ax_surface.contourf(X, Y, (data['surface_state'] == 2).astype(float),
                                               levels=[0.5, 1.5], colors=[self.layer_colors['surface_burned']], alpha=0.7)
        
        ax_surface.set_title(f'地表火 (面积: {data["surface_area"]:.1f} ha)', fontweight='bold')
        ax_surface.set_aspect('equal')
        ax_surface.grid(True, alpha=0.3)
        
        # 树冠火
        canopy_unburned = ax_canopy.contourf(X, Y, (data['canopy_state'] == 0).astype(float),
                                           levels=[0.5, 1.5], colors=[self.layer_colors['canopy_unburned']], alpha=0.6)
        if (data['canopy_state'] == 1).any():
            canopy_burning = ax_canopy.contourf(X, Y, (data['canopy_state'] == 1).astype(float),
                                              levels=[0.5, 1.5], colors=[self.layer_colors['canopy_burning']], alpha=0.8)
        if (data['canopy_state'] == 2).any():
            canopy_burned = ax_canopy.contourf(X, Y, (data['canopy_state'] == 2).astype(float),
                                             levels=[0.5, 1.5], colors=[self.layer_colors['canopy_burned']], alpha=0.7)
        
        ax_canopy.set_title(f'树冠火 (面积: {data["canopy_area"]:.1f} ha)', fontweight='bold')
        ax_canopy.set_aspect('equal')
        ax_canopy.grid(True, alpha=0.3)
        
        # 组合视图
        # 先画地表火
        ax_combined.contourf(X, Y, (data['surface_state'] == 0).astype(float),
                           levels=[0.5, 1.5], colors=[self.layer_colors['surface_unburned']], alpha=0.4)
        if (data['surface_state'] > 0).any():
            ax_combined.contourf(X, Y, (data['surface_state'] > 0).astype(float),
                               levels=[0.5, 1.5], colors=[self.layer_colors['surface_burned']], alpha=0.5)
        
        # 再画树冠火（叠加）
        if (data['canopy_state'] > 0).any():
            ax_combined.contourf(X, Y, (data['canopy_state'] > 0).astype(float),
                               levels=[0.5, 1.5], colors=[self.layer_colors['canopy_burning']], alpha=0.7)
        
        ax_combined.set_title('地表火+树冠火组合', fontweight='bold')
        ax_combined.set_aspect('equal')
        ax_combined.grid(True, alpha=0.3)
    
    def _plot_fire_intensity_comparison(self, ax, layered_data):
        """绘制火势强度对比"""
        times = [data['time'] for data in layered_data]
        surface_intensities = [np.mean(data['surface_intensity'][data['surface_intensity'] > 0]) 
                             if (data['surface_intensity'] > 0).any() else 0 for data in layered_data]
        canopy_intensities = [np.mean(data['canopy_intensity'][data['canopy_intensity'] > 0]) 
                            if (data['canopy_intensity'] > 0).any() else 0 for data in layered_data]
        
        ax.plot(times, surface_intensities, 'o-', label='地表火强度', linewidth=3, markersize=6,
               color=self.layer_colors['surface_burning'])
        ax.plot(times, canopy_intensities, 's-', label='树冠火强度', linewidth=3, markersize=6,
               color=self.layer_colors['canopy_burning'])
        
        ax.fill_between(times, surface_intensities, alpha=0.3, color=self.layer_colors['surface_burning'])
        ax.fill_between(times, canopy_intensities, alpha=0.3, color=self.layer_colors['canopy_burning'])
        
        ax.set_title('地表火与树冠火强度对比', fontweight='bold')
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('平均火焰强度')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_surface_canopy_coupling(self, ax, layered_data):
        """绘制地表-树冠耦合分析"""
        surface_areas = [data['surface_area'] for data in layered_data]
        canopy_areas = [data['canopy_area'] for data in layered_data]
        
        # 散点图显示耦合关系
        ax.scatter(surface_areas, canopy_areas, s=80, alpha=0.7, 
                  c=range(len(surface_areas)), cmap='viridis')
        
        # 拟合线
        if len(surface_areas) > 1 and max(surface_areas) > 0:
            z = np.polyfit(surface_areas, canopy_areas, 1)
            p = np.poly1d(z)
            ax.plot(surface_areas, p(surface_areas), "r--", alpha=0.8, linewidth=2)
        
        ax.set_title('地表火-树冠火耦合关系', fontweight='bold')
        ax.set_xlabel('地表火面积 (ha)')
        ax.set_ylabel('树冠火面积 (ha)')
        ax.grid(True, alpha=0.3)
    
    def _plot_layered_statistics(self, ax, layered_data):
        """绘制分层统计"""
        times = [data['time'] for data in layered_data]
        surface_areas = [data['surface_area'] for data in layered_data]
        canopy_areas = [data['canopy_area'] for data in layered_data]
        total_areas = [s + c for s, c in zip(surface_areas, canopy_areas)]
        
        # 堆叠面积图
        ax.fill_between(times, 0, surface_areas, alpha=0.7, 
                       color=self.layer_colors['surface_burning'], label='地表火面积')
        ax.fill_between(times, surface_areas, total_areas, alpha=0.7,
                       color=self.layer_colors['canopy_burning'], label='树冠火面积')
        
        ax.set_title('分层火场面积演化', fontweight='bold')
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('燃烧面积 (ha)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_surface_fire_stacking(self, ax, data):
        """绘制地表火状态堆叠"""
        times = data['time_steps']
        
        # 转换为百分比
        total = data['surface_unburned'] + data['surface_burning'] + data['surface_burned']
        unburned_pct = data['surface_unburned'] / total * 100
        burning_pct = data['surface_burning'] / total * 100
        burned_pct = data['surface_burned'] / total * 100
        
        ax.fill_between(times, 0, unburned_pct, alpha=0.7, 
                       color=self.layer_colors['surface_unburned'], label='未燃烧')
        ax.fill_between(times, unburned_pct, unburned_pct + burning_pct, alpha=0.7,
                       color=self.layer_colors['surface_burning'], label='燃烧中')
        ax.fill_between(times, unburned_pct + burning_pct, 100, alpha=0.7,
                       color=self.layer_colors['surface_burned'], label='已燃尽')
        
        ax.set_title('地表火状态分布变化', fontweight='bold')
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('状态占比 (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)
    
    def _plot_canopy_fire_stacking(self, ax, data):
        """绘制树冠火状态堆叠"""
        times = data['time_steps']
        
        # 转换为百分比
        total = data['canopy_unburned'] + data['canopy_burning'] + data['canopy_burned']
        unburned_pct = data['canopy_unburned'] / total * 100
        burning_pct = data['canopy_burning'] / total * 100
        burned_pct = data['canopy_burned'] / total * 100
        
        ax.fill_between(times, 0, unburned_pct, alpha=0.7,
                       color=self.layer_colors['canopy_unburned'], label='未燃烧')
        ax.fill_between(times, unburned_pct, unburned_pct + burning_pct, alpha=0.7,
                       color=self.layer_colors['canopy_burning'], label='燃烧中')
        ax.fill_between(times, unburned_pct + burning_pct, 100, alpha=0.7,
                       color=self.layer_colors['canopy_burned'], label='已燃尽')
        
        ax.set_title('树冠火状态分布变化', fontweight='bold')
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('状态占比 (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)
    
    def _plot_total_area_progression(self, ax, data):
        """绘制总体燃烧面积变化"""
        times = data['time_steps']
        
        # 计算实际面积（假设每个元胞50x50米）
        cell_area = (50 * 50) / 10000  # 转换为公顷
        
        surface_burned_area = data['surface_burned'] * cell_area
        canopy_burned_area = data['canopy_burned'] * cell_area
        total_burned_area = surface_burned_area + canopy_burned_area
        
        ax.plot(times, surface_burned_area, '-', linewidth=3, label='地表火面积',
               color=self.layer_colors['surface_burning'])
        ax.plot(times, canopy_burned_area, '-', linewidth=3, label='树冠火面积',
               color=self.layer_colors['canopy_burning'])
        ax.plot(times, total_burned_area, '--', linewidth=3, label='总燃烧面积', color='black')
        
        ax.fill_between(times, surface_burned_area, alpha=0.3, color=self.layer_colors['surface_burning'])
        ax.fill_between(times, canopy_burned_area, alpha=0.3, color=self.layer_colors['canopy_burning'])
        
        ax.set_title('总体燃烧面积发展', fontweight='bold')
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('累积燃烧面积 (ha)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_burning_rate_analysis(self, ax, data):
        """绘制燃烧速率分析"""
        times = data['time_steps'][1:]  # 去掉第一个点
        
        # 计算燃烧速率（面积变化率）
        cell_area = (50 * 50) / 10000  # 公顷
        
        surface_rate = np.diff(data['surface_burned']) * cell_area
        canopy_rate = np.diff(data['canopy_burned']) * cell_area
        
        ax.plot(times, surface_rate, 'o-', linewidth=2, markersize=4, label='地表火燃烧速率',
               color=self.layer_colors['surface_burning'])
        ax.plot(times, canopy_rate, 's-', linewidth=2, markersize=4, label='树冠火燃烧速率',
               color=self.layer_colors['canopy_burning'])
        
        # 平滑曲线
        if len(times) > 5:
            from scipy.signal import savgol_filter
            surface_smooth = savgol_filter(surface_rate, min(len(surface_rate)//3*2+1, 11), 2)
            canopy_smooth = savgol_filter(canopy_rate, min(len(canopy_rate)//3*2+1, 11), 2)
            
            ax.plot(times, surface_smooth, '-', linewidth=3, alpha=0.7,
                   color=self.layer_colors['surface_burning'])
            ax.plot(times, canopy_smooth, '-', linewidth=3, alpha=0.7,
                   color=self.layer_colors['canopy_burning'])
        
        ax.set_title('燃烧速率变化', fontweight='bold')
        ax.set_xlabel('时间 (小时)')
        ax.set_ylabel('燃烧速率 (ha/h)')
        ax.legend()
        ax.grid(True, alpha=0.3) 
    
    def _plot_spotting_overview(self, ax, data):
        """绘制飞火事件总览"""
        # 绘制主火场
        main_circle = Circle((data['main_fire_x'], data['main_fire_y']), 800, 
                           fill=True, alpha=0.6, color=self.layer_colors['surface_burning'],
                           label='主火场')
        ax.add_patch(main_circle)
        
        # 绘制飞火点
        successful_spots = data['spot_success']
        failed_spots = ~data['spot_success']
        
        # 成功的飞火点
        if np.any(successful_spots):
            ax.scatter(data['spot_x'][successful_spots], data['spot_y'][successful_spots],
                      s=150, c=self.layer_colors['spotting'], marker='*', 
                      edgecolors='red', linewidth=2, label='成功飞火点', alpha=0.8)
        
        # 失败的飞火点
        if np.any(failed_spots):
            ax.scatter(data['spot_x'][failed_spots], data['spot_y'][failed_spots],
                      s=80, c=self.layer_colors['ember'], marker='x',
                      linewidth=2, label='失败飞火点', alpha=0.6)
        
        # 绘制飞火轨迹
        for i in range(len(data['spot_x'])):
            ax.plot([data['main_fire_x'], data['spot_x'][i]], 
                   [data['main_fire_y'], data['spot_y'][i]],
                   '--', alpha=0.4, color='gray', linewidth=1)
        
        # 风向箭头
        wind_length = 500
        wind_x = wind_length * np.cos(data['wind_direction'] * np.pi / 180)
        wind_y = wind_length * np.sin(data['wind_direction'] * np.pi / 180)
        
        ax.arrow(data['main_fire_x'] - wind_x/2, data['main_fire_y'] - wind_y/2,
                wind_x, wind_y, head_width=100, head_length=80, 
                fc='blue', ec='blue', alpha=0.7, linewidth=3)
        
        ax.set_title('飞火事件分布总览', fontweight='bold', fontsize=14)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    def _plot_spotting_legend(self, ax):
        """绘制飞火图例"""
        legend_elements = [
            plt.Circle((0, 0), 1, facecolor=self.layer_colors['surface_burning'], alpha=0.6, label='主火场'),
            plt.scatter([], [], s=150, c=self.layer_colors['spotting'], marker='*', 
                       edgecolors='red', linewidth=2, label='成功飞火点'),
            plt.scatter([], [], s=80, c=self.layer_colors['ember'], marker='x',
                       linewidth=2, label='失败飞火点'),
            plt.Line2D([0], [0], linestyle='--', color='gray', label='飞火轨迹'),
            plt.Arrow(0, 0, 1, 0, width=0.5, color='blue', label='风向')
        ]
        
        ax.legend(handles=legend_elements, loc='center', fontsize=12)
        ax.set_title('图例说明', fontweight='bold')
        ax.axis('off')
    
    def _plot_spotting_distance_analysis(self, ax, data):
        """绘制飞火距离分析"""
        distances = data['spot_distances']
        success = data['spot_success']
        
        # 距离分布直方图
        ax.hist(distances[success], bins=15, alpha=0.7, color='green', 
               label=f'成功飞火 (n={np.sum(success)})', density=True)
        ax.hist(distances[~success], bins=15, alpha=0.7, color='red',
               label=f'失败飞火 (n={np.sum(~success)})', density=True)
        
        # 添加统计信息
        ax.axvline(np.mean(distances[success]), color='green', linestyle='--', linewidth=2,
                  label=f'成功平均距离: {np.mean(distances[success]):.0f}m')
        ax.axvline(np.mean(distances[~success]), color='red', linestyle='--', linewidth=2,
                  label=f'失败平均距离: {np.mean(distances[~success]):.0f}m')
        
        ax.set_title('飞火距离分布分析', fontweight='bold')
        ax.set_xlabel('飞火距离 (m)')
        ax.set_ylabel('概率密度')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_spotting_frequency_analysis(self, ax, data):
        """绘制飞火频率分析"""
        times = data['event_times']
        
        # 时间分布直方图
        n, bins, patches = ax.hist(times, bins=12, alpha=0.7, color='orange', edgecolor='black')
        
        # 为每个bin着色
        for i, (patch, count) in enumerate(zip(patches, n)):
            if count > 0:
                patch.set_facecolor(plt.cm.YlOrRd(count / max(n)))
        
        ax.set_title('飞火事件时间分布', fontweight='bold')
        ax.set_xlabel('发生时间 (小时)')
        ax.set_ylabel('事件频次')
        ax.grid(True, alpha=0.3)
        
        # 添加统计信息
        ax.text(0.02, 0.98, f'总事件数: {len(times)}\n'
                           f'平均发生时间: {np.mean(times):.1f}h\n'
                           f'峰值时间段: {bins[np.argmax(n)]:.0f}-{bins[np.argmax(n)+1]:.0f}h',
               transform=ax.transAxes, fontsize=10,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
               verticalalignment='top')
    
    def _plot_wind_direction_impact(self, ax, data):
        """绘制风向影响分析"""
        # 计算各方向的飞火密度
        spot_angles = np.arctan2(data['spot_y'] - data['main_fire_y'], 
                                data['spot_x'] - data['main_fire_x'])
        spot_angles = (spot_angles + 2*np.pi) % (2*np.pi)  # 转换为0-2π
        
        # 统计各方向的飞火数量
        angle_bins = np.linspace(0, 2*np.pi, 36)  # 10度一个bin
        hist, _ = np.histogram(spot_angles, bins=angle_bins)
        
        # 绘制极坐标直方图
        angles = angle_bins[:-1] + np.diff(angle_bins)[0]/2
        
        # 转换为角度制（以北向为0度）
        angles_deg = np.degrees(angles)
        
        # 创建风玫瑰图
        width = 360 / len(hist)
        
        bars = ax.bar(angles_deg, hist, width=width, 
                     alpha=0.7, color='skyblue', edgecolor='navy')
        
        # 标记主风向
        wind_angle = data['wind_direction']
        max_val = max(hist) if max(hist) > 0 else 1
        
        ax.arrow(wind_angle, 0, 0, max_val*0.8, 
                head_width=15, head_length=max_val*0.1, 
                fc='red', ec='red', linewidth=3, alpha=0.8)
        
        ax.set_title('飞火方向分布\n(红箭头为主风向)', fontweight='bold')
        ax.set_xlabel('方向 (度)')
        ax.set_ylabel('飞火数量')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 360)
    
    def _plot_spotting_prediction_model(self, ax, data):
        """绘制飞火预测模型"""
        distances = data['spot_distances']
        success_prob = []
        
        # 计算不同距离的成功概率
        distance_bins = np.linspace(min(distances), max(distances), 10)
        bin_centers = (distance_bins[:-1] + distance_bins[1:]) / 2
        
        for i in range(len(distance_bins)-1):
            mask = (distances >= distance_bins[i]) & (distances < distance_bins[i+1])
            if np.sum(mask) > 0:
                prob = np.sum(data['spot_success'][mask]) / np.sum(mask)
                success_prob.append(prob)
            else:
                success_prob.append(0)
        
        # 绘制实际数据点
        ax.scatter(distances, data['spot_success'].astype(float), 
                  alpha=0.6, s=60, c='blue', label='实际数据')
        
        # 绘制预测曲线
        ax.plot(bin_centers, success_prob, 'ro-', linewidth=3, markersize=8,
               label='成功概率')
        
        # 拟合指数衰减模型
        from scipy.optimize import curve_fit
        
        def exp_decay(x, a, b, c):
            return a * np.exp(-b * x) + c
        
        try:
            popt, _ = curve_fit(exp_decay, bin_centers, success_prob, 
                              bounds=([0, 0, 0], [1, 0.01, 1]))
            x_smooth = np.linspace(min(distances), max(distances), 100)
            y_smooth = exp_decay(x_smooth, *popt)
            ax.plot(x_smooth, y_smooth, '--', linewidth=2, color='red', alpha=0.8,
                   label=f'指数衰减拟合\ny = {popt[0]:.2f}·exp(-{popt[1]:.4f}·x) + {popt[2]:.2f}')
        except:
            pass
        
        ax.set_title('飞火成功概率预测模型', fontweight='bold')
        ax.set_xlabel('飞火距离 (m)')
        ax.set_ylabel('成功概率')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.1, 1.1)
    
    def _plot_global_perspective(self, ax, data):
        """绘制全局视角"""
        global_data = data['global']
        
        # 绘制地形
        terrain_contour = ax.contour(global_data['X'], global_data['Y'], global_data['terrain'],
                                   levels=15, colors='gray', alpha=0.5, linewidths=0.5)
        ax.clabel(terrain_contour, inline=True, fontsize=8, fmt='%d m')
        
        # 绘制火场
        fire_contour = ax.contourf(global_data['X'], global_data['Y'], global_data['fire'],
                                 levels=[0.5, 1.5], colors=['red'], alpha=0.7)
        
        # 标记重点区域
        for region in data['local_regions']:
            center = region['center']
            size = region['size']
            rect = plt.Rectangle((center[0]-size/2, center[1]-size/2), size, size,
                               fill=False, edgecolor='blue', linewidth=2, linestyle='--')
            ax.add_patch(rect)
            ax.text(center[0], center[1]+size/2+100, region['title'],
                   ha='center', va='bottom', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        ax.set_title('全局视角 - 整体火场分布', fontweight='bold', fontsize=14)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
    
    def _plot_global_3d_perspective(self, ax, data):
        """绘制全局3D视角"""
        global_data = data['global']
        
        # 降采样以提高性能
        step = 4
        X_sub = global_data['X'][::step, ::step]
        Y_sub = global_data['Y'][::step, ::step]
        terrain_sub = global_data['terrain'][::step, ::step]
        fire_sub = global_data['fire'][::step, ::step]
        
        # 绘制地形表面
        ax.plot_surface(X_sub, Y_sub, terrain_sub, alpha=0.3, cmap='terrain')
        
        # 绘制火场（在地形上方）
        fire_height = terrain_sub + fire_sub * 100  # 火焰高度
        fire_colors = plt.cm.Reds(fire_sub)
        fire_colors[:, :, 3] = fire_sub * 0.8  # 设置透明度
        
        ax.plot_surface(X_sub, Y_sub, fire_height, facecolors=fire_colors, alpha=0.8)
        
        ax.set_title('全局3D视角', fontweight='bold')
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_zlabel('高度 (m)')
    
    def _plot_local_perspectives(self, ax1, ax2, ax3, ax4, data):
        """绘制局部视角"""
        regions = data['local_regions']
        
        axes = [ax1, ax2, ax3, ax4]
        
        for i, (ax, region) in enumerate(zip(axes, regions)):
            center = region['center']
            size = region['size']
            
            # 创建局部网格
            x_local = np.linspace(center[0]-size/2, center[0]+size/2, 30)
            y_local = np.linspace(center[1]-size/2, center[1]+size/2, 30)
            X_local, Y_local = np.meshgrid(x_local, y_local)
            
            # 模拟局部火场状态
            distance_to_center = np.sqrt((X_local - center[0])**2 + (Y_local - center[1])**2)
            fire_intensity = np.exp(-distance_to_center**2 / (size/4)**2)
            
            # 添加随机扰动
            fire_intensity += 0.2 * np.random.random(fire_intensity.shape)
            fire_intensity = np.clip(fire_intensity, 0, 1)
            
            # 绘制
            im = ax.contourf(X_local, Y_local, fire_intensity, levels=20, cmap='YlOrRd')
            ax.contour(X_local, Y_local, fire_intensity, levels=5, colors='black', alpha=0.3, linewidths=0.5)
            
            ax.set_title(region['title'], fontweight='bold', fontsize=10)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            
            # 添加颜色条（只在最后一个子图）
            if i == 3:
                plt.colorbar(im, ax=ax, label='火焰强度', shrink=0.8)
    
    def _plot_ground_perspective(self, ax, data):
        """绘制地面视角"""
        ground_data = data['ground']
        
        # 植被类型映射
        vegetation_colors = {1: '#2E8B57', 2: '#32CD32', 3: '#FFD700', 4: '#D2691E'}
        vegetation_names = {1: '针叶林', 2: '阔叶林', 3: '草地', 4: '灌木'}
        
        # 绘制植被分布
        for veg_type in [1, 2, 3, 4]:
            mask = ground_data['vegetation'] == veg_type
            if np.any(mask):
                ax.contourf(ground_data['X'], ground_data['Y'], mask.astype(float),
                           levels=[0.5, 1.5], colors=[vegetation_colors[veg_type]], 
                           alpha=0.7, label=vegetation_names[veg_type])
        
        # 添加微地形细节
        micro_terrain = 5 * np.sin(ground_data['X']/50) * np.cos(ground_data['Y']/50)
        ax.contour(ground_data['X'], ground_data['Y'], micro_terrain, 
                  levels=10, colors='brown', alpha=0.5, linewidths=0.5)
        
        # 模拟火头位置
        fire_front_x = np.linspace(1400, 1600, 20)
        fire_front_y = 1500 + 30 * np.sin((fire_front_x - 1500) / 50)
        ax.plot(fire_front_x, fire_front_y, 'r-', linewidth=4, label='火头位置')
        
        # 添加箭头显示蔓延方向
        for i in range(0, len(fire_front_x), 5):
            dx, dy = 20, 10
            ax.arrow(fire_front_x[i], fire_front_y[i], dx, dy,
                    head_width=8, head_length=8, fc='red', ec='red', alpha=0.8)
        
        ax.set_title('地面视角 - 植被分布与火头推进', fontweight='bold')
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.legend(loc='upper right')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
    
    def _plot_vertical_profile(self, ax, data):
        """绘制垂直剖面"""
        # 创建垂直剖面数据
        heights = np.array([0, 2, 5, 10, 15, 20, 25])  # 高度层(m)
        
        # 模拟不同高度的火焰强度
        ground_intensity = 1.0
        intensities = ground_intensity * np.exp(-heights / 8)  # 指数衰减
        
        # 添加树冠层效应
        canopy_height = 15
        canopy_mask = (heights >= 10) & (heights <= 20)
        intensities[canopy_mask] *= 1.5  # 树冠层增强
        
        ax.plot(intensities, heights, 'o-', linewidth=3, markersize=8, color='red', label='火焰强度')
        ax.fill_betweenx(heights, 0, intensities, alpha=0.3, color='red')
        
        # 标记重要高度层
        ax.axhline(y=2, color='green', linestyle='--', alpha=0.7, label='地表植被层')
        ax.axhline(y=15, color='brown', linestyle='--', alpha=0.7, label='树冠层')
        
        # 添加温度曲线
        ax2 = ax.twiny()
        temperatures = 20 + intensities * 300  # 模拟温度
        ax2.plot(temperatures, heights, 's-', linewidth=2, markersize=6, 
                color='orange', alpha=0.7, label='温度')
        
        ax.set_title('垂直剖面分析', fontweight='bold')
        ax.set_xlabel('火焰强度')
        ax.set_ylabel('高度 (m)')
        ax2.set_xlabel('温度 (°C)', color='orange')
        ax.legend(loc='upper right')
        ax2.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
    
    def _plot_scale_comparison_analysis(self, ax, data):
        """绘制尺度对比分析"""
        # 创建尺度对比表格
        scales = ['全局尺度\n(5km×5km)', '局部尺度\n(800m×800m)', '地面尺度\n(600m×600m)']
        resolutions = ['50m', '25m', '12m']
        applications = ['总体态势\n资源配置', '重点监控\n战术部署', '现场指挥\n精确作业']
        advantages = ['覆盖全面\n计算快速', '细节丰富\n平衡性好', '精度最高\n实时性强']
        
        # 创建表格数据
        table_data = []
        for i in range(len(scales)):
            table_data.append([scales[i], resolutions[i], applications[i], advantages[i]])
        
        table = ax.table(cellText=table_data,
                        colLabels=['空间尺度', '网格分辨率', '主要应用', '技术优势'],
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 3)
        
        # 设置表格样式
        n_rows, n_cols = len(table_data) + 1, len(table_data[0])
        for i in range(n_rows):
            for j in range(n_cols):
                cell = table[(i, j)]
                if i == 0:  # 表头
                    cell.set_facecolor('#4472C4')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    colors = ['#E6F3FF', '#F0F8E6', '#FFF0E6']
                    cell.set_facecolor(colors[(i-1) % len(colors)])
        
        ax.set_title('多尺度分析对比', fontweight='bold', fontsize=14)
        ax.axis('off') 