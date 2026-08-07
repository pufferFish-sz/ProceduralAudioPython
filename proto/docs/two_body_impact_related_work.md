# 相关工作：体量相当的双共振体碰撞（two-body impact）

问题：当前 stage 3 是"锤-物"简化（striker 不响）。玻璃杯碰玻璃杯这类
"两个体量相当、都会响的物体互撞"有哪些已有研究？

结论：有成熟研究，分两条传统。图形学阵营默认"每个物体都有自己的模态库、
接触力同时激励双方（单向/开环）"；声学阵营把耦合求解做得更严格但撞击方
通常简化。我们的"开环双库"方案即图形学标准做法，有直接引用可用。

标注：✔ = 2026-08-06 在 DBLP 在线核对过出处；◇ = 凭模型知识，引用前请点开确认。

## A. 图形学 / 动画阵营（多物体、都响、开环激励）

- ✔ van den Doel, Kry & Pai, "FoleyAutomatic: physically-based sound effects
  for interactive simulation and animation", SIGGRAPH 2001.
  接触声框架奠基作：场景内每个物体都是模态模型，物理引擎接触力分别激励
  各自模态库——"两个都响"是默认设定。含 impact/rolling/sliding。
- ✔ O'Brien, Shen & Gatchalian, "Synthesizing sounds from rigid-body
  simulations", SCA 2002. 从网格自动提取每个刚体的模态，碰撞冲量同时喂
  双方。即本项目"开环廉价路"的已发表标准形态。
- ✔ Raghuvanshi & Lin, "Interactive sound synthesis for large scale
  environments", I3D 2006. 数百个模态物体互撞的实时预算方案（模式裁剪、
  质量分级）——写游戏预算章节的直接引用。
- ✔ Zheng & James, "Toward high-quality modal contact sound", SIGGRAPH 2011.
  与本问题最贴：指出朴素冲量激励在共振体撞共振体时失真，引入接触阻尼
  （持续接触时互相消音）、微碰撞序列与多点摩擦接触的耦合处理。
  杯叠杯/杯碰杯的失真机理出处；也接上我们观察到的 micro-bounce。
- ✔ Chadwick, Zheng & James, "Precomputed acceleration noise for improved
  rigid-body sound", SIGGRAPH 2012. 碰撞除振铃外的"加速度噪声"（刚体整体
  加速推空气）——ground layer 噪声 burst 的理论出处。
- ✔ Ante Qu, "Computer methods for collision processing: from sound to
  topology", Stanford PhD thesis 2021. Qu & James ground sound 的完整版。

## B. 声学 / 物理建模阵营（耦合严格、撞击方常简化）

- ◇ Rocchesso & Fontana (eds.), "The Sounding Object", 2003
  （soundobject.org 免费 PDF）。Avanzini 模型的全书版；impact 章节给出
  两个模态物体互撞的方程形式（各自模态展开 + 共享接触力）。SDT 实现的是
  质量块撞模态体，但理论框架是双模态体的。
- ◇ Papetti, Avanzini & Rocchesso, "Numerical methods for a nonlinear
  impact model", IEEE TASLP 2011. K-method 等离散化系统比较——本项目
  implicit 积分器的直系文献；扩展到双模态体数值方案不变。
- ◇ Chaigne & Doutaut, 木琴敲击建模, JASA 1997. 声学界经典双体耦合：
  琴槌为"质量+非线性弹簧"（最简单的会变形撞击方）。
- ◇ 钢琴槌-弦文献（Hall；Stulov 迟滞槌模型）：撞击方有内部动力学的极端例子。

## 对本项目的三个落点

1. 开环双库法有靠山（O'Brien 2002 / Raghuvanshi 2006），论文里直接引用
   论证近似合理性；
2. 失真边界引 Zheng & James 2011：持续接触的互相阻尼、微碰撞序列是
   朴素做法破功的场景；
3. 体量相当时接触时长用约化质量修正：m_eff = m₁m₂/(m₁+m₂) 替入
   `hertz_contact_time()` 即可。
