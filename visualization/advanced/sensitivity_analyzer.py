"""
敏感性与不确定性分析器 - 林火蔓延模型参数敏感性分析
Sensitivity and Uncertainty Analyzer - Fire Spread Model Parameter Sensitivity Analysis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import norm, uniform
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Tuple, Optional, Callable, Any
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class SensitivityAnalyzer:
    """敏感性与不确定性分析器"""
    
    def __init__(self, figure_size: Tuple[int, int] = (15, 10), dpi: int = 150):
        """
        初始化敏感性分析器
        
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
        
        # 定义敏感性分析配色方案
        self.sensitivity_colormap = self._create_sensitivity_colormap()
    
    def create_single_parameter_sensitivity(self, parameter_name: str, 
                                          parameter_values: np.ndarray,
                                          model_outputs: np.ndarray,
                                          title: str = "单参数敏感性分析",
                                          save_path: Optional[str] = None) -> plt.Figure:
        """
        创建单参数敏感性曲线
        
        Args:
            parameter_name: 参数名称
            parameter_values: 参数值数组
            model_outputs: 对应的模型输出
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        print(f"📊 开始生成单参数敏感性分析: {parameter_name}")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=self.dpi)
        
        # 1. 敏感性曲线 (左上)
        ax1 = axes[0, 0]
        ax1.plot(parameter_values, model_outputs, 'b-', linewidth=2, marker='o', markersize=4)
        ax1.set_xlabel(f'{parameter_name}')
        ax1.set_ylabel('模型输出')
        ax1.set_title(f'{parameter_name} 敏感性曲线')
        ax1.grid(True, alpha=0.3)
        
        # 添加敏感性指标
        sensitivity_index = self._calculate_sensitivity_index(parameter_values, model_outputs)
        ax1.text(0.05, 0.95, f'敏感性指数: {sensitivity_index:.4f}', 
                transform=ax1.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
        
        # 2. 参数分布直方图 (右上)
        ax2 = axes[0, 1]
        ax2.hist(parameter_values, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.set_xlabel(f'{parameter_name}')
        ax2.set_ylabel('频次')
        ax2.set_title(f'{parameter_name} 参数分布')
        ax2.axvline(np.mean(parameter_values), color='red', linestyle='--', 
                   label=f'均值: {np.mean(parameter_values):.3f}')
        ax2.legend()
        
        # 3. 输出分布直方图 (左下)
        ax3 = axes[1, 0]
        ax3.hist(model_outputs, bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
        ax3.set_xlabel('模型输出')
        ax3.set_ylabel('频次')
        ax3.set_title('模型输出分布')
        ax3.axvline(np.mean(model_outputs), color='red', linestyle='--', 
                   label=f'均值: {np.mean(model_outputs):.3f}')
        ax3.legend()
        
        # 4. 散点图与相关性 (右下)
        ax4 = axes[1, 1]
        correlation = np.corrcoef(parameter_values, model_outputs)[0, 1]
        scatter = ax4.scatter(parameter_values, model_outputs, c=model_outputs, 
                            cmap='viridis', alpha=0.7, s=30)
        ax4.set_xlabel(f'{parameter_name}')
        ax4.set_ylabel('模型输出')
        ax4.set_title(f'参数-输出相关性 (r={correlation:.3f})')
        
        # 添加拟合线
        z = np.polyfit(parameter_values, model_outputs, 1)
        p = np.poly1d(z)
        ax4.plot(parameter_values, p(parameter_values), "r--", alpha=0.8, linewidth=2)
        
        plt.colorbar(scatter, ax=ax4, label='模型输出')
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"✅ 单参数敏感性分析图已保存到: {save_path}")
        
        return fig
    
    def create_two_parameter_sensitivity(self, param1_name: str, param1_values: np.ndarray,
                                       param2_name: str, param2_values: np.ndarray,
                                       model_outputs: np.ndarray,
                                       title: str = "双参数敏感性分析",
                                       save_path: Optional[str] = None) -> plt.Figure:
        """
        创建双参数敏感性热力图
        
        Args:
            param1_name: 第一个参数名称
            param1_values: 第一个参数值数组
            param2_name: 第二个参数名称
            param2_values: 第二个参数值数组
            model_outputs: 对应的模型输出
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        print(f"🔥 开始生成双参数敏感性分析: {param1_name} vs {param2_name}")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=self.dpi)
        
        # 1. 敏感性热力图 (左上)
        ax1 = axes[0, 0]
        
        # 创建网格数据
        unique_param1 = np.unique(param1_values)
        unique_param2 = np.unique(param2_values)
        
        if len(unique_param1) > 1 and len(unique_param2) > 1:
            # 使用散点图代替复杂的网格插值
            scatter = ax1.scatter(param1_values, param2_values, c=model_outputs, 
                                cmap=self.sensitivity_colormap, s=50, alpha=0.7)
            plt.colorbar(scatter, ax=ax1, label='模型输出')
        
        ax1.set_xlabel(param1_name)
        ax1.set_ylabel(param2_name)
        ax1.set_title('敏感性热力图')
        
        # 2. 参数1边际效应 (右上)
        ax2 = axes[0, 1]
        param1_marginal = []
        param1_std = []
        for p1 in unique_param1:
            mask = np.abs(param1_values - p1) < 1e-6
            if np.any(mask):
                param1_marginal.append(np.mean(model_outputs[mask]))
                param1_std.append(np.std(model_outputs[mask]))
        
        if param1_marginal:
            ax2.errorbar(unique_param1[:len(param1_marginal)], param1_marginal, 
                        yerr=param1_std, marker='o', linewidth=2, capsize=5)
        ax2.set_xlabel(param1_name)
        ax2.set_ylabel('平均模型输出')
        ax2.set_title(f'{param1_name} 边际效应')
        ax2.grid(True, alpha=0.3)
        
        # 3. 参数2边际效应 (左下)
        ax3 = axes[1, 0]
        param2_marginal = []
        param2_std = []
        for p2 in unique_param2:
            mask = np.abs(param2_values - p2) < 1e-6
            if np.any(mask):
                param2_marginal.append(np.mean(model_outputs[mask]))
                param2_std.append(np.std(model_outputs[mask]))
        
        if param2_marginal:
            ax3.errorbar(unique_param2[:len(param2_marginal)], param2_marginal, 
                        yerr=param2_std, marker='s', linewidth=2, capsize=5)
        ax3.set_xlabel(param2_name)
        ax3.set_ylabel('平均模型输出')
        ax3.set_title(f'{param2_name} 边际效应')
        ax3.grid(True, alpha=0.3)
        
        # 4. 交互效应分析 (右下)
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        interaction_text = f"""
双参数敏感性分析摘要

📊 基本统计:
• 样本数量: {len(model_outputs)}
• 输出范围: {model_outputs.min():.3f} - {model_outputs.max():.3f}
• 输出标准差: {model_outputs.std():.3f}

🔗 相关性分析:
• {param1_name} 相关性: {np.corrcoef(param1_values, model_outputs)[0,1]:.3f}
• {param2_name} 相关性: {np.corrcoef(param2_values, model_outputs)[0,1]:.3f}
• 参数间相关性: {np.corrcoef(param1_values, param2_values)[0,1]:.3f}

🎯 敏感性排序:
1. {'参数1更敏感' if abs(np.corrcoef(param1_values, model_outputs)[0,1]) > abs(np.corrcoef(param2_values, model_outputs)[0,1]) else '参数2更敏感'}
2. {'参数2' if abs(np.corrcoef(param1_values, model_outputs)[0,1]) > abs(np.corrcoef(param2_values, model_outputs)[0,1]) else '参数1'}
        """
        
        ax4.text(0.05, 0.95, interaction_text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightcyan', alpha=0.8))
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"✅ 双参数敏感性分析图已保存到: {save_path}")
        
        return fig
    
    def create_monte_carlo_uncertainty_analysis(self, parameter_samples: Dict[str, np.ndarray],
                                              model_outputs: np.ndarray,
                                              confidence_levels: List[float] = [0.68, 0.95, 0.99],
                                              title: str = "蒙特卡洛不确定性分析",
                                              save_path: Optional[str] = None) -> plt.Figure:
        """
        创建蒙特卡洛不确定性分析图
        
        Args:
            parameter_samples: 参数样本字典 {参数名: 样本数组}
            model_outputs: 模型输出数组
            confidence_levels: 置信水平列表
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        print("🎲 开始生成蒙特卡洛不确定性分析...")
        
        fig = plt.figure(figsize=(20, 15), dpi=self.dpi)
        
        # 1. 输出分布与置信区间 (占据上方1/3)
        ax_main = plt.subplot(3, 1, 1)
        
        # 绘制输出分布直方图
        n_bins = min(50, len(model_outputs) // 10)
        counts, bins, patches = ax_main.hist(model_outputs, bins=n_bins, alpha=0.7, 
                                           color='skyblue', edgecolor='black', density=True)
        
        # 拟合正态分布
        mu, sigma = norm.fit(model_outputs)
        x_norm = np.linspace(model_outputs.min(), model_outputs.max(), 100)
        pdf_norm = norm.pdf(x_norm, mu, sigma)
        ax_main.plot(x_norm, pdf_norm, 'r-', linewidth=2, label=f'正态拟合 (μ={mu:.3f}, σ={sigma:.3f})')
        
        # 添加置信区间
        colors = ['red', 'orange', 'green']
        for i, conf_level in enumerate(confidence_levels):
            alpha_level = 1 - conf_level
            lower_percentile = (alpha_level / 2) * 100
            upper_percentile = (1 - alpha_level / 2) * 100
            
            lower_bound = np.percentile(model_outputs, lower_percentile)
            upper_bound = np.percentile(model_outputs, upper_percentile)
            
            ax_main.axvline(lower_bound, color=colors[i], linestyle='--', alpha=0.8,
                          label=f'{conf_level*100:.0f}% CI: [{lower_bound:.3f}, {upper_bound:.3f}]')
            ax_main.axvline(upper_bound, color=colors[i], linestyle='--', alpha=0.8)
        
        ax_main.set_xlabel('模型输出')
        ax_main.set_ylabel('概率密度')
        ax_main.set_title('模型输出不确定性分布与置信区间')
        ax_main.legend()
        ax_main.grid(True, alpha=0.3)
        
        # 2. 参数敏感性排序 (中间部分)
        ax_sensitivity = plt.subplot(3, 2, 3)
        
        # 计算每个参数的敏感性指数
        sensitivity_indices = {}
        for param_name, param_values in parameter_samples.items():
            sensitivity_indices[param_name] = abs(np.corrcoef(param_values, model_outputs)[0, 1])
        
        # 排序并绘制
        sorted_params = sorted(sensitivity_indices.items(), key=lambda x: x[1], reverse=True)
        param_names = [item[0] for item in sorted_params]
        param_sensitivities = [item[1] for item in sorted_params]
        
        bars = ax_sensitivity.barh(param_names, param_sensitivities, 
                                 color=sns.color_palette("viridis", len(param_names)))
        ax_sensitivity.set_xlabel('敏感性指数 (|相关系数|)')
        ax_sensitivity.set_title('参数敏感性排序')
        ax_sensitivity.grid(True, alpha=0.3)
        
        # 在柱子上标注数值
        for bar, sensitivity in zip(bars, param_sensitivities):
            ax_sensitivity.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                              f'{sensitivity:.3f}', ha='left', va='center')
        
        # 3. 不确定性贡献分析 (中间右侧)
        ax_contribution = plt.subplot(3, 2, 4)
        
        # 计算每个参数对输出方差的贡献
        variance_contributions = []
        for param_name, param_values in parameter_samples.items():
            # 简化的方差分解
            contribution = (np.corrcoef(param_values, model_outputs)[0, 1] ** 2) * np.var(model_outputs)
            variance_contributions.append(contribution)
        
        # 饼图显示方差贡献
        wedges, texts, autotexts = ax_contribution.pie(variance_contributions, labels=param_names, 
                                                      autopct='%1.1f%%', startangle=90)
        ax_contribution.set_title('输出方差贡献分解')
        
        # 4. 参数相关性矩阵 (下方左侧)
        ax_corr = plt.subplot(3, 2, 5)
        
        # 创建参数相关性矩阵
        param_df = pd.DataFrame(parameter_samples)
        param_df['model_output'] = model_outputs
        correlation_matrix = param_df.corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, ax=ax_corr, fmt='.3f')
        ax_corr.set_title('参数相关性矩阵')
        
        # 5. 累积分布函数 (下方右侧)
        ax_cdf = plt.subplot(3, 2, 6)
        
        # 绘制经验累积分布函数
        sorted_outputs = np.sort(model_outputs)
        cumulative_probs = np.arange(1, len(sorted_outputs) + 1) / len(sorted_outputs)
        
        ax_cdf.plot(sorted_outputs, cumulative_probs, 'b-', linewidth=2, label='经验CDF')
        
        # 绘制拟合的正态分布CDF
        theoretical_cdf = norm.cdf(sorted_outputs, mu, sigma)
        ax_cdf.plot(sorted_outputs, theoretical_cdf, 'r--', linewidth=2, label='理论CDF (正态)')
        
        # 添加关键百分位数
        percentiles = [5, 25, 50, 75, 95]
        for p in percentiles:
            value = np.percentile(model_outputs, p)
            ax_cdf.axvline(value, color='gray', linestyle=':', alpha=0.7)
            ax_cdf.text(value, p/100, f'P{p}', rotation=90, va='bottom')
        
        ax_cdf.set_xlabel('模型输出')
        ax_cdf.set_ylabel('累积概率')
        ax_cdf.set_title('累积分布函数')
        ax_cdf.legend()
        ax_cdf.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=18, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"✅ 蒙特卡洛不确定性分析图已保存到: {save_path}")
        
        return fig
    
    def create_sensitivity_tornado_diagram(self, parameter_impacts: Dict[str, Tuple[float, float]],
                                         title: str = "敏感性龙卷图",
                                         save_path: Optional[str] = None) -> plt.Figure:
        """
        创建敏感性龙卷图
        
        Args:
            parameter_impacts: 参数影响字典 {参数名: (负向影响, 正向影响)}
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            matplotlib图形对象
        """
        print("🌪️ 开始生成敏感性龙卷图...")
        
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # 计算总影响范围并排序
        total_impacts = {}
        for param, (neg_impact, pos_impact) in parameter_impacts.items():
            total_impacts[param] = abs(pos_impact - neg_impact)
        
        sorted_params = sorted(total_impacts.items(), key=lambda x: x[1])
        
        # 绘制龙卷图
        y_positions = np.arange(len(sorted_params))
        
        for i, (param, _) in enumerate(sorted_params):
            neg_impact, pos_impact = parameter_impacts[param]
            baseline = 0  # 基准线
            
            # 负向影响（左侧）
            ax.barh(y_positions[i], abs(neg_impact - baseline), left=min(neg_impact, baseline),
                   color='red', alpha=0.7, height=0.6)
            
            # 正向影响（右侧）
            ax.barh(y_positions[i], abs(pos_impact - baseline), left=baseline,
                   color='green', alpha=0.7, height=0.6)
            
            # 标注数值
            ax.text(neg_impact, y_positions[i], f'{neg_impact:.3f}', 
                   ha='right' if neg_impact < baseline else 'left', va='center')
            ax.text(pos_impact, y_positions[i], f'{pos_impact:.3f}', 
                   ha='left' if pos_impact > baseline else 'right', va='center')
        
        # 设置y轴标签
        ax.set_yticks(y_positions)
        ax.set_yticklabels([param for param, _ in sorted_params])
        
        # 添加基准线
        ax.axvline(0, color='black', linestyle='-', linewidth=2)
        
        ax.set_xlabel('模型输出变化')
        ax.set_title(title)
        ax.grid(True, alpha=0.3, axis='x')
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='red', alpha=0.7, label='负向影响'),
                          Patch(facecolor='green', alpha=0.7, label='正向影响')]
        ax.legend(handles=legend_elements, loc='best')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"✅ 敏感性龙卷图已保存到: {save_path}")
        
        return fig
    
    def _calculate_sensitivity_index(self, parameter_values: np.ndarray, model_outputs: np.ndarray) -> float:
        """计算敏感性指数"""
        return abs(np.corrcoef(parameter_values, model_outputs)[0, 1])
    
    def _calculate_interaction_effect(self, param1_values: np.ndarray, 
                                    param2_values: np.ndarray, 
                                    model_outputs: np.ndarray) -> float:
        """计算参数间交互效应强度"""
        # 使用多项式回归检测非线性交互
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        
        # 准备数据
        X = np.column_stack((param1_values, param2_values))
        
        # 线性模型
        linear_model = LinearRegression()
        linear_model.fit(X, model_outputs)
        linear_pred = linear_model.predict(X)
        linear_r2 = r2_score(model_outputs, linear_pred)
        
        # 包含交互项的多项式模型
        poly_features = PolynomialFeatures(degree=2, include_bias=False)
        X_poly = poly_features.fit_transform(X)
        
        poly_model = LinearRegression()
        poly_model.fit(X_poly, model_outputs)
        poly_pred = poly_model.predict(X_poly)
        poly_r2 = r2_score(model_outputs, poly_pred)
        
        # 交互效应强度 = 多项式模型改进程度
        interaction_strength = max(0, poly_r2 - linear_r2)
        
        return interaction_strength
    
    def _create_sensitivity_colormap(self):
        """创建敏感性分析专用配色方案"""
        colors = [
            (0.0, '#2E8B57'),    # 深绿 - 低敏感性
            (0.2, '#9ACD32'),    # 黄绿
            (0.4, '#FFD700'),    # 金黄 - 中等敏感性
            (0.6, '#FF8C00'),    # 深橙
            (0.8, '#FF4500'),    # 橙红
            (1.0, '#DC143C')     # 深红 - 高敏感性
        ]
        return LinearSegmentedColormap.from_list('sensitivity', colors)
    
    def generate_comprehensive_sensitivity_report(self, analysis_results: Dict[str, Any],
                                                output_dir: str = "visualization_reports") -> str:
        """
        生成综合敏感性分析报告
        
        Args:
            analysis_results: 分析结果字典
            output_dir: 输出目录
            
        Returns:
            报告目录路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        print("📋 正在生成综合敏感性分析报告...")
        
        # 这里可以基于analysis_results生成各种图表
        # 示例：生成参数敏感性总结CSV
        if 'parameter_sensitivities' in analysis_results:
            df_sensitivity = pd.DataFrame(analysis_results['parameter_sensitivities'], 
                                        index=['敏感性指数']).T
            df_sensitivity.to_csv(output_path / "parameter_sensitivity_summary.csv", 
                                encoding='utf-8-sig')
        
        print(f"✅ 综合敏感性分析报告已保存到: {output_path}")
        
        return str(output_path) 