# PLAN-2-fire-spread-physics-fix

林火蔓延模型物理一致性与风-坡耦合修正计划

---

## 任务清单

- [ ] 配置与地形生成一致性修正
- [ ] 风-坡耦合物理模型完善
- [ ] 起火点与地形分区可视化验证
- [ ] 边界条件与模拟区域优化
- [ ] 物理参数与结果合理性校验

---

## 工程细节

### 1. 配置与地形生成一致性修正
- 检查并修正`config/default_config.yaml`、`config/problem_1_optimized.yaml`等配置文件：
  - `terrain.width`、`terrain.height`、`terrain.slope_angle_deg`、`terrain.intersection_distance`
  - `ignition.point_A`、`ignition.point_B`的x/y/radius
- 检查`core/terrain.py`：
  - `create_ideal_terrain`方法，确保y坐标与`intersection_distance`的判定逻辑与配置一致
  - 明确注释A、B点的地形分区判定
- 检查`experiments/problem_1_solution.py`等脚本，确保读取和传递参数时无硬编码

### 2. 风-坡耦合物理模型完善
- 修改`core/fire_engine.py`：
  - `wind_effect`方法增加坡面法向量计算
    - 平地：n=(0,0,1)
    - 山坡：n=(0,-sinθ,cosθ)，θ为坡度
  - 增加风向在坡面上的投影Vw_proj = Vw - (Vw·n)n
  - 计算蔓延方向S与Vw_proj的夹角α
  - `calculate_spread_rate`跨越分界线时，分别用两侧的坡度/法向量
  - 增加详细注释，说明每一步的物理意义
- 新增/修正单元测试`experiments/test_wind_effects.py`，验证不同坡度、风向下的K_wind输出

### 3. 起火点与地形分区可视化验证
- 修改`visualization/terrain_visualizer.py`：
  - `plot_ignition_points_diagram`方法，增加分界线、平地/坡地区域着色
  - 标注A、B点及其分区（平地/坡地）
  - 图例区分平地、坡地、分界线、起火点
- 在`experiments/visualization_demo.py`中增加调用，生成分区验证图
- 检查输出图像，确保A点在平地、B点在坡地

### 4. 边界条件与模拟区域优化
- 检查`core/cellular_automaton.py`主循环：
  - 增加边界元胞不可燃（如四周一圈BURNED_OUT或特殊类型）
  - 或在配置中增大`terrain.width`/`height`，保证火场不会在短时间内烧穿
  - 增加边界蔓延的日志输出，便于调试
- 在`experiments/problem_1_solution.py`中，输出模拟终止原因（自然熄灭/到达边界）

### 5. 物理参数与结果合理性校验
- 在`experiments/problem_1_solution.py`中，分别输出A、B点的蔓延速度、面积随时间变化
- 在`visualization/fire_visualizer.py`中，增加面积-时间、速率-时间对比图
- 检查`core/fire_engine.py`的参数（如R0、Ks、坡度/风因子），与文献/物理常识对比
- 增加单元测试，验证不同坡度/风向下的spread_rate、K_wind、Φ(φ)输出

---

## Mermaid 流程图：风-坡耦合与蔓延决策

```mermaid
flowchart TD
    A[读取配置/地形参数] --> B{判断元胞位置}
    B -- 平地 --> C1[坡度=0, 法向量(0,0,1)]
    B -- 山坡 --> C2[坡度=30°, 法向量(0,-sin30°,cos30°)]
    C1 & C2 --> D[计算风向在坡面上的投影]
    D --> E[计算蔓延方向向量]
    E --> F[计算风-坡耦合夹角cosα]
    F --> G[计算风效应K_wind]
    G --> H[计算坡度效应Φ(φ)]
    H --> I[合成蔓延速率R]
    I --> J{是否跨越分界线?}
    J -- 是 --> B
    J -- 否 --> K[更新元胞状态]
    K --> L[下一步模拟]
``` 