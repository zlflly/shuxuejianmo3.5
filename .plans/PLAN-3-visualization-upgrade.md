# PLAN-3-visualization-upgrade.md

## 林火蔓延模型·全场景数据可视化方案（升级版）

### 一、方案简介
本计划旨在全面升级林火蔓延模型的数据可视化能力，兼顾科学性、实用性、创新性与沟通性，服务于模型开发、调试、决策支持和科学传播全流程。

---

### 二、阶段任务清单

#### 1. 数据预处理与质量检查（Data QA）
- [x] 缺失值/异常值分布热力图
- [-] 多源地形数据对比与一致性检查
- [ ] 插值前后地形对比可视化
- [ ] 数据预处理自动化脚本开发
- [ ] 交互式数据质量报告生成

**技术选型**：Matplotlib/Seaborn，Plotly，QGIS插件

---

#### 2. 静态环境可视化（Static Environment）
- [x] 2D DEM热力图与等高线图
- [x] 3D地形表面渲染（Matplotlib/Plotly）
- [x] 坡度/坡向分布图
- [-] 关键地理要素（道路/水体/居民点）叠加
- [x] 交互式地形浏览器开发

**技术选型**：Matplotlib、Mayavi、rayshader、Plotly、QGIS

---

#### 3. 模型敏感性与不确定性分析（Sensitivity & Uncertainty）
- [x] 单参数敏感性曲线绘制
- [x] 双参数敏感性热力图/等高线图
- [x] 蒙特卡洛模拟结果分布可视化
- [x] 置信区间带状图
- [x] 敏感性分析自动化脚本

**技术选型**：Seaborn、Matplotlib、Plotly、ggplot2

---

#### 4. 核心模拟结果可视化（Core Simulation）
- [x] 火场边界等高线（24/48/72h）
- [x] 火场蔓延2D动画（Matplotlib.animation）
- [x] 火场蔓延3D动画（Plotly交互式）
- [x] 关键时刻快照与对比图

**技术选型**：Matplotlib.animation、Plotly动画、GIF/HTML输出

---

#### 5. 高级特征与多层耦合可视化（Advanced Features）
- [x] 地表火/树冠火分层对比动画
- [x] 动态堆叠面积图（各状态元胞数量变化）
- [x] 飞火/跳火事件可视化
- [x] 多尺度视角切换（全局-局部-地面）

**技术选型**：Matplotlib子图、分层可视化、飞火建模、多尺度集成

---

#### 6. 决策支持与应急输出（Decision Support）
- [ ] 撤离路线规划图（高风险区、可通行道路）
- [ ] 资源部署优化图（消防站点、设备分布）
- [ ] 风险热力图与经济损失评估
- [ ] 标准化报告输出（PDF/Word/GIS格式）
- [ ] 移动端适配与GIS兼容性测试

**技术选型**：QGIS、ArcGIS、Plotly Dash、自动化报告生成



---

### 三、进度追踪与协作说明
- 每项任务请按实际进展及时更新状态标记。
- 任务细化与补充请在本文件下方追加，不要覆盖原有内容。
- 重要变更请同步团队成员。

---

> 本计划文件由AI助手根据多人格协作建议自动生成，欢迎团队成员补充完善。 