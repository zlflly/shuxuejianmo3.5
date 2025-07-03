"""
增强版地形可视化器测试脚本
Test Script for Enhanced Terrain Visualizer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from pathlib import Path
from core.terrain import TerrainGenerator
from visualization.advanced.enhanced_terrain_visualizer import EnhancedTerrainVisualizer

def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_enhanced_terrain_visualizer():
    """测试增强版地形可视化器"""
    print("=" * 60)
    print("🌄 增强版地形可视化器测试")
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
    
    # 创建增强版地形可视化器
    enhanced_viz = EnhancedTerrainVisualizer()
    
    # 创建输出目录
    output_dir = Path("visualization_reports")
    output_dir.mkdir(exist_ok=True)
    
    print("\n🌄 开始增强版地形可视化分析...")
    
    # 1. 生成综合地形分析图
    print("1. 生成地形环境全面分析图...")
    fig1 = enhanced_viz.create_comprehensive_terrain_analysis(
        surface_cells,
        "林火蔓延模型 - 地形环境全面分析",
        str(output_dir / "comprehensive_terrain_analysis.png")
    )
    
    # 2. 生成高级3D地形渲染 (Matplotlib版本)
    print("2. 生成3D地形渲染图 (Matplotlib)...")
    fig2 = enhanced_viz.create_3d_terrain_advanced(
        surface_cells,
        "高级3D地形渲染 (Matplotlib)",
        str(output_dir / "3d_terrain_matplotlib.png"),
        use_plotly=False
    )
    
    # 3. 生成交互式地形浏览器
    print("3. 生成交互式地形浏览器...")
    try:
        html_path = enhanced_viz.create_interactive_terrain_browser(
            surface_cells,
            str(output_dir)
        )
        print(f"✅ 交互式地形浏览器已保存到: {html_path}")
    except Exception as e:
        print(f"⚠️ 交互式浏览器生成遇到问题: {e}")
    
    # 4. 尝试生成Plotly 3D地形 (可能需要额外依赖)
    print("4. 尝试生成3D地形渲染图 (Plotly)...")
    try:
        fig3 = enhanced_viz.create_3d_terrain_advanced(
            surface_cells,
            "高级3D地形渲染 (Plotly)",
            str(output_dir / "3d_terrain_plotly.png"),
            use_plotly=True
        )
        if fig3:
            print("✅ Plotly 3D地形渲染完成")
        else:
            print("⚠️ Plotly 3D地形渲染跳过（数据格式问题）")
    except Exception as e:
        print(f"⚠️ Plotly 3D地形渲染遇到问题: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 增强版地形可视化器测试完成！")
    print(f"📁 所有报告文件保存在: {output_dir}")
    print("📊 生成的文件包括:")
    print("   - comprehensive_terrain_analysis.png (12合1地形全面分析)")
    print("   - 3d_terrain_matplotlib.png (3D地形渲染图)")
    print("   - interactive_terrain_browser.html (交互式地形浏览器)")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_enhanced_terrain_visualizer()
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc() 