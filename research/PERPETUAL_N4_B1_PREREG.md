# PERPETUAL-N4-B1 预注册（波级）——**DRAFT · 未冻结**

> **状态：DRAFT-NOT-FROZEN（2026-10-03 r600 bm-a 起草窗·席位认领=本件起草）。冻结门=下述
> 条件全过才允许烧批；冻结前零 burn 零 supply 零登记（R99 跑前冻结律 / R250 one-step 律）。**
> 法：research/PERPETUAL_FACES.md v1.0 §2 N4 行 + §4 起草序（N1-W2 ✅ → N3-R1 ✅ →
> N2-W15（bm-b slice-2 在建）→ **N4-B1（本件）**；冻结签名序 = 法内钉死）。
> 面性质（法 §2 L24）：N4=**测量加深面**（对既有族重新测量）——产物=更深置信面非新注册件，
> 不入候选漏斗，不占语法消耗登记簿行；D6 同族拒收门与去重门只约束候选判决面（N2），
> N4 免 D6 准入（法内豁免行如实引用）。
> runner：scripts/perpetual_faces_n4.py（**骨架已落地 r601 bm-a**：resample 层
> （circular moving-block bootstrap·交集轴默认）+ 同源回放（live.paper
> SIGNAL_BUILDERS/ExitPatch/build_panels+engine.run_backtest 零重实现）+ probe/status/
> selftest/run 腿；selftest 10/10 PASS + probe 六员真引擎冒烟 1.34s 墙钟
> （receipt results/perpetual_faces/n4_b1/probe.json）；cmd_run 带 DRAFT 标记机械拒烧
> （R99/R250 冻结前零 burn）；冻结时 PINNED-L 写入本件 §1 由 runner fail-closed 读取）。

## 冻结门（条件，冻结 commit 前逐条机证）

1. runner 落地 + selftest 全绿（resample 层确定性/幂等/双跑恒等腿）。
2. probe 真引擎面实证（在册成员回放冒烟，参照 N2-W15 probe 2.25s 双胞先例）。
3. 种子三步法 + SEED_REGISTRY 登记（§5）+ 冻结时重跑带扫描 results/_r600bma_n4b1_band_scan.py（R99/R250）。
4. 本 DRAFT §3/§4 判据写死（判线一律 import science_gates 共享库，禁手抄）。
5. banned_direction_gate 过闸（Tools/banned_direction_gate.py，N2-W15 §0.5 同法）。

## §0 批件身份【跑前填·冻结时核】

- 批名：PERPETUAL-N4-B1（bootstrap alternate-history 首波）。
- 席位：O-20261002-2155 P0 引擎发生器补全（N4 模块全缺=最大缺口）；本件起草窗=r600 bm-a
  认领（ticket T-2026-10-03-151-P1 + MSG-0135 席位公示 r565）。
- 波族：N4-B1（B=Bootstrap 首波；后续波按法典 §4 尾律顺延）。

## §1 伪机制段（α 机制·四选一）

**α = bar 块自助法平行宇宙重放（moving-block bootstrap alternate-history replay）**：
对在册成员的历史 bar 序列做**块重采样**（块长 L 待冻结时钉死，探针面给出分布事实后按
本节规格选定并写死于此）→ 生成 K 个平行宇宙历史 → 每个宇宙经 engine/run_backtest
同源回放该成员（前向不改史：重放面只在历史段内重排，evidence_cutoff 后零动作；
成员出场规则=成员注册件自有出场轴逐字回放，**禁用引擎缺省出场栈改写**）→ 产出每成员
的 Sharpe/ann/maxDD 分布 → bootstrap_ci_sharpe 置信面 + dsr_from_stats 深度面。
机制来源=canon §2 N4 行 verbatim（bar 重采样→平行宇宙重放在册成员·前向不改史·纯重放测量面）。

## §2 数据与面板【跑前探针事实，非结果】

- 面板：core48 在役面板（live.paper.load_core·RW-4 门内建）截断 evidence_cutoff
  2026-09-22（前向不改史=构造性）。**探针腿已落地（r601 bm-a·receipt
  results/perpetual_faces/n4_b1/probe.json·out-of-band 种子 95_006·零带位消耗）**：
  - **轴策略（OPEN 钉点·冻结时按事实钉死）**：交集轴 T=**797** bars
    （2023-06-13..2026-09-22·48 符号全上市共同纪元·零 NaN 面污染）vs 并集轴
    T=1,630（全史·晚上市员前段缺行=NaN 掩码面复杂度+平段伪影）。探针按交集轴
    实跑；冻结 commit 钉死轴选择入本节。
  - 块长分布事实（等权日收益 ACF·白噪带 ±0.0709）：lag1=-0.036 / lag4=+0.102 /
    lag5=-0.080 / lag9=+0.083——带内候选 L=2,3,6,7,8,10..14；**L 冻结值从本表
    选定写死 §1**（探针默认 L=20 为事实采集面非冻结值）。
  - 重放时长实读：六员单宇宙 0.137-0.266s/员（六员一遍墙钟 1.34s·真引擎
    run_backtest·X1 费率咬合真=engine FeeSchedule 默认==cost_spec.X1_RATE）；
    K=200 提案面单员全宇宙烧录预估 ~40-55s（冻结时按 K 终值复算预算）。
  - 六员冒烟（L=20·seed 95_006·同一宇宙配对设计）：全六员真引擎回放产出真
    trades（23-312 笔）与指标——交替宇宙面成立（负 Sharpe 宇宙照产=测量面
    诚实性实证，如 DROUGHT-CE-01 该宇宙 Sharpe=-0.72）。
- 成员范围：六员在册（COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01、
  VOLATILITY-CE-01）——冻结时以注册面实读为准（成员增删=月界面，本波钉六员）。

## §3 方法学

- K 个平行宇宙（K 待冻结钉死；每宇宙独立 rng=seed=带位值+宇宙序）；块长 L 从探针分布
  事实选；重放=engine/run_backtest 同源（复用 N1 面已验证的回放管线，禁重写引擎件）。
- 成本：COST_X1 常量 import（13.041bp/边），与判决面同源。

## §4 判据【跑前写死，禁看结果调线；判线一律调共享库】

- 产物面：每成员 bootstrap_ci_sharpe(x2 面) CI95 + dsr_from_stats（science_gates
  verbatim import，禁手抄判线）。
- N4=测量加深面：**零注册、零漏斗、零晋升判定**（法 §2 L24）——判据只产置信面披露，
  无 pass/fail 晋升线；诚实负发现（CI 下界≤0）照报不阻断。
- 出场轴声明（O-20261001-1108 显式门三选一）：**①策略自有出场**（成员注册件出场轴
  逐字回放，本节显式声明）。

## §5 种子（三步法·冻结 commit 登记 SEED_REGISTRY，R250 禁冻结后再挑）

- 带位（DRAFT 机器扫描回执 results/_r600bma_n4b1_band_scan.py，2026-10-03 r600）：
  - **gen 68_501..68_999** / **scrnull 69_000..69_499** / **unc 69_500..69_999**
    （宽 499 三带连续窗=68_501..69_999，40_000+ N4 域内首个 ≥1,499 连续净窗）。
  - 跳位被迫性机证（leg1/leg1b REFUSED facts）：40_000+ 域头 40_500 提案撞 N1 B-ext
    阶梯已入域（W28-W34 b_exit 40_451..42_000 连续）+SEED_REGISTRY p4_batch1=41_000；
    50_500 提案撞 N1_BANDS 投影阶梯（W68-W73 50_501..51_800）+cta_p2_noau=50_500/
    xstock_synth_null_a=51_000。gap-finder 全占用面合并后首净窗=68_501..69_999
    （上邻 N3 70_000+ 域、下邻 registry 点 68_500，皆 disjoint 机证）。
  - 冻结时重跑本扫描（表若前进=机闸再裁）；SEED_REGISTRY 登记面=perpetual_faces.py
    N4 行 base 值（冻结 commit 同步落，R250 one-step）。

## §6 跑后只许回填节（占位）

- §6.1 实跑数字（K/L/时长/行数）——跑后回填。
- §6.2 置信面产物指针——跑后回填。

## 附：席位分工账（防重复开发·跨窗接力）

- N1 面：三机轮值波（W18=bm-a 在册；法内）。
- N3-R2：bm-c（MSG-0115 认领，70_000+ 域）。
- N2-W15 slice-2：bm-b（MSG-0016 认领）；slice-3=冻结窗随开。
- **N4-B1：bm-a（本件起草窗 r600 认领；下一窗=runner 骨架+probe；精确续作点=ticket
  T-2026-10-03-151-P1 progress 行）**。
