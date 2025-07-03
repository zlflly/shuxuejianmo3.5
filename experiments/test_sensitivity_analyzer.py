"""
敏感性分析器测试脚本
Test Script for Sensitivity Analyzer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from pathlib import Path
from visualization.advanced.sensitivity_analyzer import SensitivityAnalyzer

def generate_sample_data():
    """生成示例敏感性分析数据"""
    print("📊 正在生成示例敏感性分析数据...")
    
    # 设置随机种子以便重现
    np.random.seed(42)
    
    n_samples = 500
    
    # 生成参数样本
    param_data = {
        '风速': np.random.uniform(0, 20, n_samples),  # 风速 0-20 m/s
        '湿度': np.random.uniform(0.05, 0.4, n_samples),  # 湿度 5%-40%
        '坡度': np.random.uniform(0, 45, n_samples),  # 坡度 0-45度
        '燃料负荷': np.random.uniform(1.0, 5.0, n_samples),  # 燃料负荷 1-5 kg/m²
        '温度': np.random.uniform(10, 40, n_samples),  # 温度 10-40℃
    }
    
    # 模拟林火蔓延速度（作为模型输出）
    # 基于经验公式，不同参数有不同的影响程度
    wind_speed = param_data['风速']
    humidity = param_data['湿度']
    slope = param_data['坡度']
    fuel_load = param_data['燃料负荷']
    temperature = param_data['温度']
    
    # 林火蔓延速度模型（示例公式）
    base_speed = 0.5  # 基础蔓延速度 m/min
    
    # 风速效应（正相关，高敏感性）
    wind_effect = 1 + 0.15 * wind_speed
    
    # 湿度效应（负相关，中等敏感性）
    humidity_effect = 1 - 2.0 * humidity
    
    # 坡度效应（正相关，中等敏感性）
    slope_effect = 1 + 0.02 * slope
    
    # 燃料负荷效应（正相关，低敏感性）
    fuel_effect = 0.5 + 0.2 * fuel_load
    
    # 温度效应（正相关，低敏感性）
    temp_effect = 1 + 0.01 * temperature
    
    # 综合计算火蔓延速度
    fire_spread_rate = (base_speed * wind_effect * humidity_effect * 
                       slope_effect * fuel_effect * temp_effect)
    
    # 添加随机噪声
    noise = np.random.normal(0, 0.05, n_samples)
    fire_spread_rate += noise
    
    # 确保非负值
    fire_spread_rate = np.maximum(fire_spread_rate, 0.01)
    
    print(f"✅ 生成了 {n_samples} 个样本")
    print(f"   火蔓延速度范围: {fire_spread_rate.min():.3f} - {fire_spread_rate.max():.3f} m/min")
    
    return param_data, fire_spread_rate

def test_sensitivity_analyzer():
    """测试敏感性分析器"""
    print("=" * 60)
    print("📈 敏感性分析器测试")
    print("=" * 60)
    
    # 生成示例数据
    param_data, model_outputs = generate_sample_data()
    
    # 创建敏感性分析器
    analyzer = SensitivityAnalyzer()
    
    # 创建输出目录
    output_dir = Path("visualization_reports")
    output_dir.mkdir(exist_ok=True)
    
    print("\n📊 开始敏感性分析...")
    
    # 1. 单参数敏感性分析 - 风速
    print("1. 生成风速单参数敏感性分析...")
    fig1 = analyzer.create_single_parameter_sensitivity(
        parameter_name="风速 (m/s)",
        parameter_values=param_data['风速'],
        model_outputs=model_outputs,
        title="风速对林火蔓延速度的敏感性分析",
        save_path=str(output_dir / "sensitivity_wind_speed.png")
    )
    
    # 2. 单参数敏感性分析 - 湿度
    print("2. 生成湿度单参数敏感性分析...")
    fig2 = analyzer.create_single_parameter_sensitivity(
        parameter_name="湿度",
        parameter_values=param_data['湿度'],
        model_outputs=model_outputs,
        title="湿度对林火蔓延速度的敏感性分析",
        save_path=str(output_dir / "sensitivity_humidity.png")
    )
    
    # 3. 双参数敏感性分析 - 风速vs湿度
    print("3. 生成风速-湿度双参数敏感性分析...")
    fig3 = analyzer.create_two_parameter_sensitivity(
        param1_name="风速 (m/s)",
        param1_values=param_data['风速'],
        param2_name="湿度",
        param2_values=param_data['湿度'],
        model_outputs=model_outputs,
        title="风速-湿度双参数敏感性分析",
        save_path=str(output_dir / "sensitivity_wind_humidity.png")
    )
    
    # 4. 双参数敏感性分析 - 坡度vs燃料负荷
    print("4. 生成坡度-燃料负荷双参数敏感性分析...")
    fig4 = analyzer.create_two_parameter_sensitivity(
        param1_name="坡度 (度)",
        param1_values=param_data['坡度'],
        param2_name="燃料负荷 (kg/m²)",
        param2_values=param_data['燃料负荷'],
        model_outputs=model_outputs,
        title="坡度-燃料负荷双参数敏感性分析",
        save_path=str(output_dir / "sensitivity_slope_fuel.png")
    )
    
    # 5. 蒙特卡洛不确定性分析
    print("5. 生成蒙特卡洛不确定性分析...")
    fig5 = analyzer.create_monte_carlo_uncertainty_analysis(
        parameter_samples=param_data,
        model_outputs=model_outputs,
        confidence_levels=[0.68, 0.95, 0.99],
        title="林火蔓延模型 - 蒙特卡洛不确定性分析",
        save_path=str(output_dir / "monte_carlo_uncertainty.png")
    )
    
    # 6. 生成敏感性统计摘要
    print("6. 生成敏感性统计摘要...")
    sensitivity_summary = {}
    for param_name, param_values in param_data.items():
        correlation = np.corrcoef(param_values, model_outputs)[0, 1]
        sensitivity_summary[param_name] = {
            '相关系数': correlation,
            '敏感性指数': abs(correlation),
            '敏感性等级': '高' if abs(correlation) > 0.5 else '中' if abs(correlation) > 0.3 else '低'
        }
    
    # 保存统计摘要为CSV
    df_summary = pd.DataFrame(sensitivity_summary).T
    df_summary.to_csv(output_dir / "sensitivity_summary.csv", encoding='utf-8-sig')
    
    print("\n" + "=" * 60)
    print("✅ 敏感性分析器测试完成！")
    print(f"📁 所有报告文件保存在: {output_dir}")
    print("📊 生成的文件包括:")
    print("   - sensitivity_wind_speed.png (风速单参数敏感性)")
    print("   - sensitivity_humidity.png (湿度单参数敏感性)")
    print("   - sensitivity_wind_humidity.png (风速-湿度双参数敏感性)")
    print("   - sensitivity_slope_fuel.png (坡度-燃料负荷双参数敏感性)")
    print("   - monte_carlo_uncertainty.png (蒙特卡洛不确定性分析)")
    print("   - sensitivity_summary.csv (敏感性统计摘要)")
    print("\n📈 敏感性分析结果:")
    for param, stats in sensitivity_summary.items():
        print(f"   {param}: {stats['敏感性等级']}敏感性 (相关系数={stats['相关系数']:.3f})")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_sensitivity_analyzer()
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc() 