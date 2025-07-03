"""
火场可视化器 - 生成火场边界图和统计图表
Fire Visualizer - Generate Fire Boundary Plots and Statistical Charts
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import numpy as np
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path

class FireVisualizer:
    """火场可视化器"""
    
    def __init__(self, figure_size: Tuple[int, int] = (12, 8), dpi: int = 150):
        """
        初始化可视化器
        
        Args:
            figure_size: 图形尺寸 (宽, 高)
            dpi: 图形分辨率
        """
        self.figure_size = figure_size
        self.dpi = dpi
        
        # 定义火场状态颜色映射
        self.fire_colors = {
            'UNBURNED': '#228B22',      # 森林绿
            'SURFACE_FIRE': '#FF4500',  # 橙红色
            'CROWN_FIRE': '#FF0000',    # 红色
            'BURNED_OUT': '#2F4F4F'     # 深灰色
        }
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_fire_boundaries(self, fire_boundaries: Dict, title: str = "火场边界演化", 
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制火场边界演化图
        
        Args:
            fire_boundaries: 火场边界数据
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        colors = ['blue', 'orange', 'red']
        time_keys = sorted(fire_boundaries.keys(), key=lambda x: int(x.replace('h', '')))
        
        for i, time_key in enumerate(time_keys):
            boundary = fire_boundaries[time_key]
            
            if boundary['area_m2'] > 0:
                # 绘制火场边界圆
                center = boundary['center']
                radius = boundary['radius']
                
                circle = patches.Circle(center, radius, 
                                      fill=False, 
                                      edgecolor=colors[i % len(colors)], 
                                      linewidth=2, 
                                      label=f'{time_key}: {boundary["area_hectares"]:.1f}公顷')
                ax.add_patch(circle)
                
                # 标记中心点
                ax.plot(center[0], center[1], 'o', 
                       color=colors[i % len(colors)], markersize=8)
        
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        # 自动调整坐标轴范围
        self._auto_adjust_limits(ax, fire_boundaries)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def plot_fire_spread_comparison(self, scenarios: Dict[str, Dict], 
                                  title: str = "不同条件下火场对比", 
                                  save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制不同情景下的火场对比图
        
        Args:
            scenarios: 多情景火场数据 {scenario_name: fire_boundaries}
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig, axes = plt.subplots(1, len(scenarios), 
                                figsize=(self.figure_size[0] * len(scenarios), self.figure_size[1]), 
                                dpi=self.dpi)
        
        if len(scenarios) == 1:
            axes = [axes]
        
        for i, (scenario_name, fire_boundaries) in enumerate(scenarios.items()):
            ax = axes[i]
            
            # 绘制72小时火场边界
            if '72h' in fire_boundaries and fire_boundaries['72h']['area_m2'] > 0:
                boundary = fire_boundaries['72h']
                
                # 绘制椭圆近似
                center = boundary['center']
                if 'x_range' in boundary and 'y_range' in boundary:
                    width = boundary['x_range']
                    height = boundary['y_range']
                    
                    ellipse = patches.Ellipse(center, width, height, 
                                            fill=True, alpha=0.3,
                                            facecolor='red', edgecolor='darkred', linewidth=2)
                    ax.add_patch(ellipse)
                
                # 标记起火点
                ax.plot(1500, 1500, 'ko', markersize=10, label='起火点A')
                ax.plot(1500, 2000, 'ks', markersize=10, label='起火点B')
            
            ax.set_xlabel('X坐标 (m)')
            ax.set_ylabel('Y坐标 (m)')
            ax.set_title(f'{scenario_name}\n面积: {fire_boundaries.get("72h", {}).get("area_hectares", 0):.1f}公顷')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')
            
            # 设置统一的坐标轴范围
            ax.set_xlim(500, 2500)
            ax.set_ylim(500, 2500)
        
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def plot_area_time_series(self, stats_history: List[Dict], 
                             title: str = "燃烧面积时间序列", 
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制燃烧面积随时间变化图
        
        Args:
            stats_history: 统计历史数据
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figure_size, dpi=self.dpi)
        
        times = [entry['time'] / 60 for entry in stats_history]  # 转换为小时
        areas = [entry['stats']['burned_area'] / 10000 for entry in stats_history]  # 转换为公顷
        intensities = [entry['stats']['max_fire_intensity'] for entry in stats_history]
        
        # 燃烧面积图
        ax1.plot(times, areas, 'r-', linewidth=2, marker='o', markersize=4)
        ax1.set_xlabel('时间 (小时)')
        ax1.set_ylabel('燃烧面积 (公顷)')
        ax1.set_title('燃烧面积随时间变化')
        ax1.grid(True, alpha=0.3)
        
        # 火线强度图
        ax2.plot(times, intensities, 'orange', linewidth=2, marker='s', markersize=4)
        ax2.set_xlabel('时间 (小时)')
        ax2.set_ylabel('最大火线强度 (kW/m)')
        ax2.set_title('火线强度随时间变化')
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def create_wind_effect_diagram(self, wind_scenarios: Dict, 
                                 title: str = "风效应影响分析", 
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        创建风效应影响分析图
        
        Args:
            wind_scenarios: 风况情景数据
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=self.dpi)
        
        # 提取数据用于柱状图
        scenario_names = []
        areas = []
        ellipticities = []
        
        for scenario_name, data in wind_scenarios.items():
            if 'point_A' in data and '72h' in data['point_A']['fire_boundaries']:
                boundary = data['point_A']['fire_boundaries']['72h']
                scenario_names.append(scenario_name)
                areas.append(boundary['area_hectares'])
                
                # 计算椭圆度
                x_range = boundary.get('x_range', 0)
                y_range = boundary.get('y_range', 0)
                ellipticity = max(x_range, y_range) / max(min(x_range, y_range), 1.0)
                ellipticities.append(ellipticity)
        
        # 燃烧面积对比
        colors = ['lightblue', 'lightgreen', 'lightcoral']
        bars1 = ax1.bar(scenario_names, areas, color=colors[:len(scenario_names)])
        ax1.set_ylabel('燃烧面积 (公顷)')
        ax1.set_title('不同风况下的燃烧面积')
        ax1.grid(True, alpha=0.3)
        
        # 在柱子上标注数值
        for bar, area in zip(bars1, areas):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'{area:.1f}', ha='center', va='bottom')
        
        # 火场椭圆度对比
        bars2 = ax2.bar(scenario_names, ellipticities, color=colors[:len(scenario_names)])
        ax2.set_ylabel('椭圆度 (长轴/短轴)')
        ax2.set_title('不同风况下的火场形状')
        ax2.grid(True, alpha=0.3)
        
        # 在柱子上标注数值
        for bar, ellipticity in zip(bars2, ellipticities):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                    f'{ellipticity:.2f}', ha='center', va='bottom')
        
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def _auto_adjust_limits(self, ax, fire_boundaries: Dict):
        """自动调整坐标轴范围"""
        all_points = []
        
        for boundary in fire_boundaries.values():
            if boundary['area_m2'] > 0:
                center = boundary['center']
                radius = boundary['radius']
                
                # 添加边界点
                all_points.extend([
                    [center[0] - radius, center[1] - radius],
                    [center[0] + radius, center[1] + radius]
                ])
        
        if all_points:
            all_points = np.array(all_points)
            margin = 100  # 100米边距
            
            ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
            ax.set_ylim(all_points[:, 1].min() - margin, all_points[:, 1].max() + margin)
        else:
            # 默认范围
            ax.set_xlim(0, 3000)
            ax.set_ylim(0, 3000)
    
    @staticmethod
    def load_fire_boundaries(file_path: str) -> Dict:
        """从JSON文件加载火场边界数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_report_figures(self, results_dir: str, output_dir: str = "figures"):
        """
        生成完整的报告图表
        
        Args:
            results_dir: 结果文件目录
            output_dir: 输出图表目录
        """
        results_path = Path(results_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("正在生成可视化报告...")
        
        # 问题一结果可视化
        try:
            point_A_data = self.load_fire_boundaries(results_path / "point_A_solution.json")
            point_B_data = self.load_fire_boundaries(results_path / "point_B_solution.json")
            
            # 单独绘制A、B点火场边界
            self.plot_fire_boundaries(point_A_data, "点A起火火场边界演化", 
                                     str(output_path / "point_A_boundaries.png"))
            self.plot_fire_boundaries(point_B_data, "点B起火火场边界演化", 
                                     str(output_path / "point_B_boundaries.png"))
            
            # 对比图
            scenarios = {"点A起火": point_A_data, "点B起火": point_B_data}
            self.plot_fire_spread_comparison(scenarios, "问题一：A、B两点起火对比", 
                                           str(output_path / "problem1_comparison.png"))
            
            print("✅ 问题一可视化完成")
        except FileNotFoundError as e:
            print(f"⚠️ 问题一结果文件未找到: {e}")
        
        # 问题二风效应结果可视化
        wind_files = list(results_path.glob("*_wind_*.json"))
        if wind_files:
            wind_scenarios = {}
            for wind_file in wind_files:
                scenario_name = wind_file.stem.split('_wind_')[-1]
                wind_scenarios[scenario_name] = self.load_fire_boundaries(wind_file)
            
            self.create_wind_effect_diagram(wind_scenarios, "问题二：风效应影响分析",
                                          str(output_path / "wind_effects_analysis.png"))
            print("✅ 问题二可视化完成")
        
        print(f"所有图表已保存到: {output_path}") 