"""
数据质量分析器测试脚本
Test Script for Data Quality Analyzer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from pathlib import Path
from core.terrain import TerrainGenerator
from visualization.advanced.data_quality_analyzer import DataQualityAnalyzer

def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_data_quality_analyzer():
    """测试数据质量分析器"""
    print("=" * 60)
    print("🔍 数据质量分析器测试")
    print("=" * 60)
    
    # 加载配置
    config = load_config('../config/default_config.yaml')
    terrain_config = config['terrain']
    
    # 生成地形数据
    print("📍 正在生成地形数据...")
    terrain_gen = TerrainGenerator(
        cell_size=config['simulation']['cell_size'], 
        config=config
    )
    
    surface_cells, _ = terrain_gen.create_ideal_terrain(
        width=terrain_config['width'], 
        height=terrain_config['height'],
        slope_angle_deg=terrain_config['slope_angle_deg'],
        intersection_distance=terrain_config['intersection_distance']
    )
    
    print(f"✅ 地形数据生成完成，共 {len(surface_cells)} 个地表元胞")
    
    # 创建数据质量分析器
    analyzer = DataQualityAnalyzer()
    
    # 创建输出目录
    output_dir = Path("visualization_reports")
    output_dir.mkdir(exist_ok=True)
    
    # 执行数据质量分析
    print("\n🔍 开始数据质量分析...")
    
    # 1. 生成数据质量分析图
    fig = analyzer.analyze_terrain_data_quality(
        surface_cells,
        "林火蔓延模型 - 地形数据质量全面分析",
        str(output_dir / "data_quality_analysis.png")
    )
    
    # 2. 生成完整的数据预处理报告
    analyzer.create_data_preprocessing_report(
        surface_cells,
        str(output_dir)
    )
    
    print("\n" + "=" * 60)
    print("✅ 数据质量分析测试完成！")
    print(f"📁 报告文件保存在: {output_dir}")
    print("=" * 60)
    
    return fig

if __name__ == "__main__":
    try:
        test_data_quality_analyzer()
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc() 