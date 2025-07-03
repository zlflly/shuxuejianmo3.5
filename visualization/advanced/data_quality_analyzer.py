"""
数据质量分析器 - 林火蔓延模型数据预处理与质量检查
Data Quality Analyzer - Data Preprocessing and Quality Check for Fire Spread Model
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class DataQualityAnalyzer:
    """数据质量分析器"""
    
    def __init__(self, figure_size: Tuple[int, int] = (15, 10), dpi: int = 150):
        """
        初始化数据质量分析器
        
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
        sns.set_palette("husl")
    
    def analyze_terrain_data_quality(self, surface_cells: List, 
                                   title: str = "地形数据质量分析", 
                                   save_path: Optional[str] = None) -> plt.Figure:
        """
        分析地形数据质量，生成缺失值/异常值分布热力图
        
        Args:
            surface_cells: 地表元胞列表
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        print("🔍 开始分析地形数据质量...")
        
        # 提取地形数据
        terrain_data = self._extract_terrain_features(surface_cells)
        
        # 创建主图形
        fig = plt.figure(figsize=(20, 15), dpi=self.dpi)
        
        # 1. 缺失值分布热力图 (2x3布局的第1个)
        ax1 = plt.subplot(3, 3, 1)
        missing_matrix = pd.DataFrame(terrain_data).isnull()
        sns.heatmap(missing_matrix, cmap='Reds', cbar_kws={'label': '缺失值'}, ax=ax1)
        ax1.set_title('1. 缺失值分布热力图')
        ax1.set_xlabel('数据字段')
        ax1.set_ylabel('元胞索引')
        
        # 2. 高程异常值检测 (第2个)
        ax2 = plt.subplot(3, 3, 2)
        elevation_data = terrain_data['elevation']
        Q1, Q3 = np.percentile(elevation_data, [25, 75])
        IQR = Q3 - Q1
        outlier_mask = (elevation_data < Q1 - 1.5*IQR) | (elevation_data > Q3 + 1.5*IQR)
        
        # 2D网格显示异常值
        positions = np.array([[cell.static.position[0], cell.static.position[1]] for cell in surface_cells])
        x_coords, y_coords = positions[:, 0], positions[:, 1]
        
        scatter = ax2.scatter(x_coords, y_coords, c=outlier_mask, cmap='RdYlBu_r', s=2, alpha=0.7)
        ax2.set_title('2. 高程异常值分布')
        ax2.set_xlabel('X坐标 (m)')
        ax2.set_ylabel('Y坐标 (m)')
        plt.colorbar(scatter, ax=ax2, label='异常值(1=是, 0=否)')
        
        # 3. 坡度异常值检测 (第3个)
        ax3 = plt.subplot(3, 3, 3)
        slope_data = terrain_data['slope_degrees']
        slope_outliers = (slope_data < 0) | (slope_data > 90)  # 坡度应该在0-90度之间
        
        scatter3 = ax3.scatter(x_coords, y_coords, c=slope_outliers, cmap='RdYlBu_r', s=2, alpha=0.7)
        ax3.set_title('3. 坡度异常值分布')
        ax3.set_xlabel('X坐标 (m)')
        ax3.set_ylabel('Y坐标 (m)')
        plt.colorbar(scatter3, ax=ax3, label='异常值(1=是, 0=否)')
        
        # 4. 数据完整性统计 (第4个)
        ax4 = plt.subplot(3, 3, 4)
        completeness_stats = {
            '高程': 100 * (1 - np.isnan(elevation_data).sum() / len(elevation_data)),
            '坡度': 100 * (1 - np.isnan(slope_data).sum() / len(slope_data)),
            '坡向': 100 * (1 - np.isnan(terrain_data['aspect_degrees']).sum() / len(terrain_data['aspect_degrees'])),
            '燃料负荷': 100 * (1 - np.isnan(terrain_data['fuel_load']).sum() / len(terrain_data['fuel_load'])),
            '湿度': 100 * (1 - np.isnan(terrain_data['moisture']).sum() / len(terrain_data['moisture']))
        }
        
        bars = ax4.bar(completeness_stats.keys(), completeness_stats.values(), 
                      color=['#2E8B57', '#4682B4', '#DAA520', '#CD853F', '#6495ED'])
        ax4.set_title('4. 数据完整性统计 (%)')
        ax4.set_ylabel('完整性百分比')
        ax4.set_ylim(0, 105)
        
        # 在柱子上标注数值
        for bar, value in zip(bars, completeness_stats.values()):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 5. 高程分布直方图 (第5个)
        ax5 = plt.subplot(3, 3, 5)
        ax5.hist(elevation_data, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax5.axvline(np.mean(elevation_data), color='red', linestyle='--', label=f'均值: {np.mean(elevation_data):.1f}m')
        ax5.axvline(np.median(elevation_data), color='green', linestyle='--', label=f'中位数: {np.median(elevation_data):.1f}m')
        ax5.set_title('5. 高程数据分布')
        ax5.set_xlabel('高程 (m)')
        ax5.set_ylabel('频次')
        ax5.legend()
        
        # 6. 坡度分布直方图 (第6个)
        ax6 = plt.subplot(3, 3, 6)
        ax6.hist(slope_data, bins=50, alpha=0.7, color='orange', edgecolor='black')
        ax6.axvline(np.mean(slope_data), color='red', linestyle='--', label=f'均值: {np.mean(slope_data):.1f}°')
        ax6.axvline(np.median(slope_data), color='green', linestyle='--', label=f'中位数: {np.median(slope_data):.1f}°')
        ax6.set_title('6. 坡度数据分布')
        ax6.set_xlabel('坡度 (度)')
        ax6.set_ylabel('频次')
        ax6.legend()
        
        # 7. 相关性矩阵热力图 (第7个)
        ax7 = plt.subplot(3, 3, 7)
        df_terrain = pd.DataFrame(terrain_data)
        correlation_matrix = df_terrain.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, ax=ax7, fmt='.2f')
        ax7.set_title('7. 地形参数相关性矩阵')
        
        # 8. 燃料负荷与湿度散点图 (第8个)
        ax8 = plt.subplot(3, 3, 8)
        fuel_load = terrain_data['fuel_load']
        moisture = terrain_data['moisture']
        scatter8 = ax8.scatter(fuel_load, moisture, c=elevation_data, cmap='terrain', alpha=0.6, s=3)
        ax8.set_xlabel('燃料负荷 (kg/m²)')
        ax8.set_ylabel('湿度含量')
        ax8.set_title('8. 燃料负荷 vs 湿度含量')
        plt.colorbar(scatter8, ax=ax8, label='高程 (m)')
        
        # 9. 数据质量总结 (第9个)
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        # 计算质量指标
        total_cells = len(surface_cells)
        missing_count = pd.DataFrame(terrain_data).isnull().sum().sum()
        outlier_count = sum(outlier_mask) + sum(slope_outliers)
        quality_score = max(0, 100 - (missing_count + outlier_count) / total_cells * 10)
        
        quality_text = f"""
数据质量评估报告

📊 数据规模: {total_cells:,} 个元胞
🔍 缺失值数量: {missing_count}
⚠️  异常值数量: {outlier_count}
📈 数据质量得分: {quality_score:.1f}/100

高程范围: {np.min(elevation_data):.1f} - {np.max(elevation_data):.1f} m
坡度范围: {np.min(slope_data):.1f} - {np.max(slope_data):.1f} °

建议:
{'✅ 数据质量良好' if quality_score > 85 else '⚠️ 建议进一步清理数据'}
        """
        
        ax9.text(0.05, 0.95, quality_text, transform=ax9.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
        
        plt.suptitle(title, fontsize=18, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"✅ 数据质量分析图已保存到: {save_path}")
        
        print("🎯 地形数据质量分析完成！")
        return fig
    
    def _extract_terrain_features(self, surface_cells: List) -> Dict[str, np.ndarray]:
        """从地表元胞中提取地形特征数据"""
        
        features = {
            'elevation': [],
            'slope_degrees': [],
            'aspect_degrees': [],
            'fuel_load': [],
            'moisture': []
        }
        
        for cell in surface_cells:
            # 提取位置和地形信息
            features['elevation'].append(cell.static.position[2])  # z坐标即海拔
            features['slope_degrees'].append(np.degrees(cell.static.slope))
            features['aspect_degrees'].append(np.degrees(cell.static.aspect))
            features['fuel_load'].append(cell.dynamic.fuel_load)
            features['moisture'].append(cell.dynamic.moisture_content)
        
        # 转换为numpy数组
        for key in features:
            features[key] = np.array(features[key])
            
        return features
    
    def create_data_preprocessing_report(self, surface_cells: List, 
                                       output_dir: str = "visualization_reports"):
        """
        创建完整的数据预处理质量报告
        
        Args:
            surface_cells: 地表元胞列表
            output_dir: 输出目录
        """
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("📋 正在生成数据预处理质量报告...")
        
        # 生成主要的数据质量分析图
        self.analyze_terrain_data_quality(
            surface_cells, 
            "林火蔓延模型 - 地形数据质量全面分析",
            str(output_path / "data_quality_analysis.png")
        )
        
        # 生成数据统计摘要CSV
        terrain_data = self._extract_terrain_features(surface_cells)
        df_stats = pd.DataFrame(terrain_data).describe()
        df_stats.to_csv(output_path / "terrain_data_statistics.csv", encoding='utf-8-sig')
        
        print(f"✅ 数据预处理质量报告已保存到: {output_path}")
        print("📁 报告包含:")
        print("   - data_quality_analysis.png (数据质量分析图)")
        print("   - terrain_data_statistics.csv (地形数据统计摘要)")
        
        return output_path 