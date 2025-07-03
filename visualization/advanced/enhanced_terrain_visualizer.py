"""
增强版地形可视化器 - 静态环境全场景可视化
Enhanced Terrain Visualizer - Comprehensive Static Environment Visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import pandas as pd

class EnhancedTerrainVisualizer:
    """增强版地形可视化器"""
    
    def __init__(self, figure_size: Tuple[int, int] = (15, 10), dpi: int = 150):
        """
        初始化增强版地形可视化器
        
        Args:
            figure_size: 图形尺寸 (宽, 高)
            dpi: 图形分辨率
        """
        self.figure_size = figure_size
        self.dpi = dpi
        
        # 设置中文字体和美化样式
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        sns.set_style("whitegrid")
        
        # 定义专业的地形配色方案
        self.terrain_colormap = self._create_terrain_colormap()
        self.slope_colormap = plt.cm.YlOrRd
        self.aspect_colormap = plt.cm.hsv
    
    def create_comprehensive_terrain_analysis(self, surface_cells: List, 
                                            title: str = "地形环境全面分析", 
                                            save_path: Optional[str] = None) -> plt.Figure:
        """
        创建地形环境的全面分析图表
        
        Args:
            surface_cells: 地表元胞列表
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        print("🌄 开始生成地形环境全面分析...")
        
        # 提取地形数据
        terrain_data = self._extract_terrain_data(surface_cells)
        
        # 创建大型图形 (4x3布局)
        fig = plt.figure(figsize=(24, 18), dpi=self.dpi)
        
        # 1. 高分辨率DEM热力图 (左上)
        ax1 = plt.subplot(3, 4, 1)
        self._plot_dem_heatmap(ax1, terrain_data, "高程分布 (DEM)")
        
        # 2. 等高线图 (右上第2个)
        ax2 = plt.subplot(3, 4, 2)
        self._plot_contour_lines(ax2, terrain_data, "等高线图")
        
        # 3. 坡度分布图 (第3个)
        ax3 = plt.subplot(3, 4, 3)
        self._plot_slope_distribution(ax3, terrain_data, "坡度分布")
        
        # 4. 坡向分布图 (第4个)
        ax4 = plt.subplot(3, 4, 4)
        self._plot_aspect_distribution(ax4, terrain_data, "坡向分布")
        
        # 5. 坡度-坡向综合分析 (第5个)
        ax5 = plt.subplot(3, 4, 5)
        self._plot_slope_aspect_combined(ax5, terrain_data, "坡度-坡向综合")
        
        # 6. 地形崎岖度分析 (第6个)
        ax6 = plt.subplot(3, 4, 6)
        self._plot_terrain_roughness(ax6, terrain_data, "地形崎岖度")
        
        # 7. 流域分析 (第7个)
        ax7 = plt.subplot(3, 4, 7)
        self._plot_watershed_analysis(ax7, terrain_data, "水流方向分析")
        
        # 8. 视域分析 (第8个)
        ax8 = plt.subplot(3, 4, 8)
        self._plot_viewshed_analysis(ax8, terrain_data, "视域可达性")
        
        # 9. 地形分类 (第9个)
        ax9 = plt.subplot(3, 4, 9)
        self._plot_terrain_classification(ax9, terrain_data, "地形分类")
        
        # 10. 燃料分布 (第10个)
        ax10 = plt.subplot(3, 4, 10)
        self._plot_fuel_distribution(ax10, terrain_data, "燃料负荷分布")
        
        # 11. 湿度分布 (第11个)
        ax11 = plt.subplot(3, 4, 11)
        self._plot_moisture_distribution(ax11, terrain_data, "湿度分布")
        
        # 12. 地形统计摘要 (第12个)
        ax12 = plt.subplot(3, 4, 12)
        self._plot_terrain_statistics(ax12, terrain_data, "地形统计摘要")
        
        plt.suptitle(title, fontsize=20, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"✅ 地形环境分析图已保存到: {save_path}")
        
        print("🎯 地形环境全面分析完成！")
        return fig
    
    def create_3d_terrain_advanced(self, surface_cells: List, 
                                 title: str = "高级3D地形渲染", 
                                 save_path: Optional[str] = None,
                                 use_plotly: bool = True) -> Any:
        """
        创建高级3D地形渲染
        
        Args:
            surface_cells: 地表元胞列表
            title: 图表标题
            save_path: 保存路径
            use_plotly: 是否使用Plotly（更美观）
            
        Returns:
            图形对象
        """
        print("🎨 开始生成高级3D地形渲染...")
        
        terrain_data = self._extract_terrain_data(surface_cells)
        
        if use_plotly:
            return self._create_plotly_3d_terrain(terrain_data, title, save_path)
        else:
            return self._create_matplotlib_3d_terrain(terrain_data, title, save_path)
    
    def create_interactive_terrain_browser(self, surface_cells: List, 
                                         output_dir: str = "visualization/interactive") -> str:
        """
        创建交互式地形浏览器 (HTML文件)
        
        Args:
            surface_cells: 地表元胞列表
            output_dir: 输出目录
            
        Returns:
            HTML文件路径
        """
        print("🌐 开始生成交互式地形浏览器...")
        
        terrain_data = self._extract_terrain_data(surface_cells)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # 创建多页面交互式图表
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('高程分布', '坡度分布', '坡向分布', '3D地形'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "surface"}]]
        )
        
        # 高程散点图
        fig.add_trace(
            go.Scatter(
                x=terrain_data['x_coords'],
                y=terrain_data['y_coords'],
                mode='markers',
                                 marker=dict(
                     color=terrain_data['elevation'],
                     colorscale='earth',
                     size=3,
                     colorbar=dict(title="高程 (m)")
                 ),
                name='高程分布'
            ),
            row=1, col=1
        )
        
        # 坡度散点图
        fig.add_trace(
            go.Scatter(
                x=terrain_data['x_coords'],
                y=terrain_data['y_coords'],
                mode='markers',
                marker=dict(
                    color=terrain_data['slope_degrees'],
                    colorscale='YlOrRd',
                    size=3,
                    colorbar=dict(title="坡度 (°)")
                ),
                name='坡度分布'
            ),
            row=1, col=2
        )
        
        # 坡向散点图
        fig.add_trace(
            go.Scatter(
                x=terrain_data['x_coords'],
                y=terrain_data['y_coords'],
                mode='markers',
                marker=dict(
                    color=terrain_data['aspect_degrees'],
                    colorscale='hsv',
                    size=3,
                    colorbar=dict(title="坡向 (°)")
                ),
                name='坡向分布'
            ),
            row=2, col=1
        )
        
        # 3D地表
        unique_x = np.unique(terrain_data['x_coords'])
        unique_y = np.unique(terrain_data['y_coords'])
        
        if len(unique_x) > 1 and len(unique_y) > 1:
            X, Y = np.meshgrid(unique_x, unique_y)
            Z = np.zeros_like(X)
            
            # 填充高程数据
            for i, x in enumerate(terrain_data['x_coords']):
                for j, y in enumerate(terrain_data['y_coords']):
                    try:
                        x_idx = np.where(unique_x == x)[0][0]
                        y_idx = np.where(unique_y == y)[0][0]
                        Z[y_idx, x_idx] = terrain_data['elevation'][j]
                    except:
                        continue
            
            fig.add_trace(
                                 go.Surface(
                     x=X, y=Y, z=Z,
                     colorscale='earth',
                     name='3D地形'
                 ),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="林火蔓延模型 - 交互式地形分析浏览器",
            showlegend=True,
            height=800
        )
        
        # 保存为HTML文件
        html_file = output_path / "interactive_terrain_browser.html"
        fig.write_html(str(html_file))
        
        print(f"✅ 交互式地形浏览器已保存到: {html_file}")
        return str(html_file)
    
    def _extract_terrain_data(self, surface_cells: List) -> Dict[str, np.ndarray]:
        """提取地形数据"""
        
        data = {
            'x_coords': [],
            'y_coords': [],
            'elevation': [],
            'slope_degrees': [],
            'aspect_degrees': [],
            'fuel_load': [],
            'moisture': []
        }
        
        for cell in surface_cells:
            x, y, z = cell.static.position
            data['x_coords'].append(x)
            data['y_coords'].append(y)
            data['elevation'].append(z)
            data['slope_degrees'].append(np.degrees(cell.static.slope))
            data['aspect_degrees'].append(np.degrees(cell.static.aspect))
            data['fuel_load'].append(cell.dynamic.fuel_load)
            data['moisture'].append(cell.dynamic.moisture_content)
        
        # 转换为numpy数组
        for key in data:
            data[key] = np.array(data[key])
            
        return data
    
    def _create_terrain_colormap(self):
        """创建专业地形配色方案"""
        colors = [
            (0.0, '#2E8B57'),    # 深绿 - 低海拔
            (0.2, '#228B22'),    # 森林绿
            (0.4, '#9ACD32'),    # 黄绿 - 丘陵
            (0.6, '#DAA520'),    # 金黄 - 高地
            (0.8, '#CD853F'),    # 褐色 - 山地
            (1.0, '#8B4513')     # 深褐 - 高山
        ]
        return LinearSegmentedColormap.from_list('terrain_pro', colors)
    
    def _plot_dem_heatmap(self, ax, terrain_data, title):
        """绘制DEM热力图"""
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=terrain_data['elevation'], cmap=self.terrain_colormap, 
                           s=1, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label='高程 (m)')
    
    def _plot_contour_lines(self, ax, terrain_data, title):
        """绘制等高线图"""
        # 创建网格
        xi = np.linspace(terrain_data['x_coords'].min(), terrain_data['x_coords'].max(), 100)
        yi = np.linspace(terrain_data['y_coords'].min(), terrain_data['y_coords'].max(), 100)
        X, Y = np.meshgrid(xi, yi)
        
        # 插值高程数据
        from scipy.interpolate import griddata
        Z = griddata((terrain_data['x_coords'], terrain_data['y_coords']), 
                    terrain_data['elevation'], (X, Y), method='cubic')
        
        # 绘制等高线
        contour = ax.contour(X, Y, Z, levels=15, colors='black', alpha=0.6, linewidths=0.8)
        ax.contourf(X, Y, Z, levels=20, cmap=self.terrain_colormap, alpha=0.7)
        ax.clabel(contour, inline=True, fontsize=8, fmt='%d')
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
    
    def _plot_slope_distribution(self, ax, terrain_data, title):
        """绘制坡度分布"""
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=terrain_data['slope_degrees'], cmap=self.slope_colormap, 
                           s=1, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label='坡度 (°)')
    
    def _plot_aspect_distribution(self, ax, terrain_data, title):
        """绘制坡向分布"""
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=terrain_data['aspect_degrees'], cmap=self.aspect_colormap, 
                           s=1, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label='坡向 (°)')
    
    def _plot_slope_aspect_combined(self, ax, terrain_data, title):
        """绘制坡度-坡向综合分析"""
        # 使用坡度作为点的大小，坡向作为颜色
        sizes = terrain_data['slope_degrees'] * 2  # 放大显示
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=terrain_data['aspect_degrees'], s=sizes, 
                           cmap=self.aspect_colormap, alpha=0.6)
        ax.set_title(title + '\n(大小=坡度, 颜色=坡向)')
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label='坡向 (°)')
    
    def _plot_terrain_roughness(self, ax, terrain_data, title):
        """绘制地形崎岖度"""
        # 计算地形崎岖度（高程标准差的局部估计）
        elevation = terrain_data['elevation']
        slope = terrain_data['slope_degrees']
        
        # 简化的崎岖度指标：坡度与高程变异的组合
        roughness = slope * (1 + np.abs(elevation - np.mean(elevation)) / np.std(elevation))
        
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=roughness, cmap='plasma', s=1, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label='崎岖度指数')
    
    def _plot_watershed_analysis(self, ax, terrain_data, title):
        """绘制流域分析"""
        # 简化的水流方向分析（基于坡向）
        aspect_rad = np.radians(terrain_data['aspect_degrees'])
        flow_x = np.sin(aspect_rad)
        flow_y = np.cos(aspect_rad)
        
        # 每10个点绘制一个箭头以避免过于密集
        step = max(1, len(terrain_data['x_coords']) // 500)
        x_sample = terrain_data['x_coords'][::step]
        y_sample = terrain_data['y_coords'][::step]
        u_sample = flow_x[::step]
        v_sample = flow_y[::step]
        
        ax.quiver(x_sample, y_sample, u_sample, v_sample, 
                 alpha=0.7, scale=50, width=0.002, color='blue')
        
        # 背景显示高程
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=terrain_data['elevation'], cmap=self.terrain_colormap, 
                           s=0.5, alpha=0.3)
        
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
    
    def _plot_viewshed_analysis(self, ax, terrain_data, title):
        """绘制视域可达性分析"""
        # 简化的视域分析：基于相对高程优势
        elevation = terrain_data['elevation']
        max_elev = np.max(elevation)
        min_elev = np.min(elevation)
        
        # 视域可达性 = 相对高程 + 地形开阔度（反比坡度）
        relative_elevation = (elevation - min_elev) / (max_elev - min_elev)
        openness = 1 / (1 + terrain_data['slope_degrees'] / 90)  # 归一化
        viewshed_score = relative_elevation * 0.7 + openness * 0.3
        
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=viewshed_score, cmap='viridis', s=1, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label='视域得分')
    
    def _plot_terrain_classification(self, ax, terrain_data, title):
        """绘制地形分类"""
        # 基于坡度和高程的地形分类
        elevation = terrain_data['elevation']
        slope = terrain_data['slope_degrees']
        
        # 定义分类规则
        terrain_class = np.zeros_like(elevation)
        
        # 平地 (坡度 < 5°)
        terrain_class[(slope < 5)] = 1
        
        # 缓坡 (5° ≤ 坡度 < 15°)
        terrain_class[(slope >= 5) & (slope < 15)] = 2
        
        # 陡坡 (15° ≤ 坡度 < 30°)
        terrain_class[(slope >= 15) & (slope < 30)] = 3
        
        # 峭壁 (坡度 ≥ 30°)
        terrain_class[(slope >= 30)] = 4
        
        # 自定义颜色映射
        colors = ['white', '#90EE90', '#32CD32', '#FF8C00', '#8B0000']
        cmap = ListedColormap(colors)
        
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=terrain_class, cmap=cmap, s=1, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        
        # 添加图例
        labels = ['', '平地 (<5°)', '缓坡 (5-15°)', '陡坡 (15-30°)', '峭壁 (>30°)']
        cbar = plt.colorbar(scatter, ax=ax, ticks=[0, 1, 2, 3, 4])
        cbar.ax.set_yticklabels(labels)
    
    def _plot_fuel_distribution(self, ax, terrain_data, title):
        """绘制燃料分布"""
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=terrain_data['fuel_load'], cmap='Oranges', 
                           s=1, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label='燃料负荷 (kg/m²)')
    
    def _plot_moisture_distribution(self, ax, terrain_data, title):
        """绘制湿度分布"""
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           c=terrain_data['moisture'], cmap='Blues', 
                           s=1, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label='湿度含量')
    
    def _plot_terrain_statistics(self, ax, terrain_data, title):
        """绘制地形统计摘要"""
        ax.axis('off')
        
        # 计算统计指标
        stats_text = f"""
地形统计摘要

📊 基本信息:
• 元胞数量: {len(terrain_data['elevation']):,}
• 研究区域: {terrain_data['x_coords'].max() - terrain_data['x_coords'].min():.0f}m × {terrain_data['y_coords'].max() - terrain_data['y_coords'].min():.0f}m

🏔️ 高程信息:
• 最低高程: {terrain_data['elevation'].min():.1f} m
• 最高高程: {terrain_data['elevation'].max():.1f} m
• 平均高程: {terrain_data['elevation'].mean():.1f} m
• 高程标准差: {terrain_data['elevation'].std():.1f} m

📐 坡度信息:
• 最小坡度: {terrain_data['slope_degrees'].min():.1f}°
• 最大坡度: {terrain_data['slope_degrees'].max():.1f}°
• 平均坡度: {terrain_data['slope_degrees'].mean():.1f}°
• 坡度标准差: {terrain_data['slope_degrees'].std():.1f}°

🔥 燃料信息:
• 平均燃料负荷: {terrain_data['fuel_load'].mean():.2f} kg/m²
• 平均湿度: {terrain_data['moisture'].mean():.3f}

📈 地形复杂性:
• 地形变异系数: {terrain_data['elevation'].std()/terrain_data['elevation'].mean():.3f}
• 坡度多样性: {len(np.unique(np.round(terrain_data['slope_degrees'], 0)))} 种坡度类型
        """
        
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightcyan', alpha=0.8))
        ax.set_title(title)
    
    def _create_plotly_3d_terrain(self, terrain_data, title, save_path):
        """使用Plotly创建3D地形"""
        # 创建网格
        unique_x = np.unique(terrain_data['x_coords'])
        unique_y = np.unique(terrain_data['y_coords'])
        
        if len(unique_x) > 1 and len(unique_y) > 1:
            X, Y = np.meshgrid(unique_x, unique_y)
            Z = np.zeros_like(X)
            
            # 填充高程数据
            for i, (x, y, z) in enumerate(zip(terrain_data['x_coords'], 
                                            terrain_data['y_coords'], 
                                            terrain_data['elevation'])):
                try:
                    x_idx = np.where(unique_x == x)[0][0]
                    y_idx = np.where(unique_y == y)[0][0]
                    Z[y_idx, x_idx] = z
                except:
                    continue
            
            fig = go.Figure(data=[
                                 go.Surface(
                     x=X, y=Y, z=Z,
                     colorscale='earth',
                    lighting=dict(
                        ambient=0.4,
                        diffuse=0.8,
                        fresnel=0.1,
                        specular=0.1,
                        roughness=0.1
                    ),
                    contours={
                        "z": {"show": True, "start": Z.min(), "end": Z.max(), "size": 50}
                    }
                )
            ])
            
            fig.update_layout(
                title=title,
                scene=dict(
                    xaxis_title='X坐标 (m)',
                    yaxis_title='Y坐标 (m)',
                    zaxis_title='高程 (m)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                width=800,
                height=600
            )
            
            if save_path:
                fig.write_html(save_path.replace('.png', '_3d.html'))
                fig.write_image(save_path)
            
            return fig
        else:
            print("⚠️ 网格数据不足，无法生成3D地形")
            return None
    
    def _create_matplotlib_3d_terrain(self, terrain_data, title, save_path):
        """使用Matplotlib创建3D地形"""
        fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
        ax = fig.add_subplot(111, projection='3d')
        
        # 创建3D散点图
        scatter = ax.scatter(terrain_data['x_coords'], terrain_data['y_coords'], 
                           terrain_data['elevation'], c=terrain_data['elevation'], 
                           cmap=self.terrain_colormap, s=1, alpha=0.8)
        
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.set_zlabel('高程 (m)')
        ax.set_title(title)
        
        plt.colorbar(scatter, ax=ax, shrink=0.5, aspect=20, label='高程 (m)')
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig 