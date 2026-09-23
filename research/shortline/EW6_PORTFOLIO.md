# EW6 组合验证批 — 预注册（跑前写死）

- 任务单：T-2026-09-23-06（P1，组合与资金部首单，O-20260923-2311）
- 章程：firm/portfolio.md v1.0 · 判据科学层：research/BACKTEST_SCIENCE.md v2（D1-D6 全适用）
- 状态：**跑前冻结**（任何跑数之前写死；§6 结果区跑前必须为空——占位纪律）
- 执行体：bm-b OS 循环轮 round 51 · 认领 commit 先于本批所有跑数（F-04）

## 一、问题与范围（REPORT-ONLY pass 1）

在册 6 员交易员等权合并组合（EW6）是否有真实的组合层证据：分散化
benefit、组合 Sharpe、成本 ×2 存活、政体切片诚实度。**本批=测量与报告，
零注册、零资金再分配、零触碰 level/paper 字段**（报告制，charter §三）。

不做的事（反 p-hacking / 反镀金）：
- 不搜索权重、不换载体、不增删成员（成员=注册名册固定）；
- 不调门槛、不换口径（跑后禁翻案，铁律三）；
- 不触发任何晋升/淘汰（G2.5/DSR 属交易员注册面，bm-a r28 已 6/6 FAIL，
  本批不重算不引用为门，只作背景披露）。

## 二、冻结参数

1. **成员名册（固定 6 员）**=firm/traders/*.json 非下划线全集
   （=research/STRATEGY_LIBRARY.md §二指针）：
   VOLATILITY-CE-01 / COMPOSITE-CE-01 / COMPOSITE-CE-02 /
   ENGULF-CE-01 / NEEDLE-DE-01 / DROUGHT-CE-01。
2. **方案**：S-EW（唯一载体，参数自由）：各 1/6 初始权重，**不再平衡**
   （combine 语义=P3 portfolio_report.md §2：port=Σ w_i·(eq_i/eq_i0)，
   inner-join 各 sleeve 截断后净值轴）。IV 风险预算=Phase 1 后续批次，本批不做。
3. **跑数预算（run count）**：6 成员 × {x1, x2} = **12 次引擎跑**
   （anchor-cum-sleeve，P3 范式：sleeve 即锚定跑，不双跑）+ 2 次组合求值
   （EW x1 / EW x2，纯派生非引擎）= **账本 n=14**。零搜索 ⇒ 零 null 跑
   （零假设记账=账本条目组成如实披露，非 null 采样）。
4. **执行**：scripts/parallel_runner.py run_cells_parallel（ProcessPool，
   workers=min(worker_cap(), 6)，audit.workers 落盘；作业函数=顶层无闭包）。
5. **宇宙**：core48 裸码现行面板（live.paper load_core）。sleeve 逐员截断至
   各自 evidence_cutoff（注册件字段；live.paper evidence_cutoff）。**D2 前向
   锁盒**：IS=面板起点..2024-12-31；IS2（D2 降格，历史上称 OOS）=
   2025-01-01..cutoff；**真样本外=cutoff 后锁盒，本批不消费**（paper 通道
    accrue）。OOS_START 常量仅为与注册锚定口径连续沿用。
6. **成本**：legacy 费率路径（**引擎加性旗标全部默认 OFF**——additive 铁律；
   cost_v2 本批不启用：与注册证据口径连续优先，启用另开预注册）。x1/x2 经
   live.paper CostPatch（P3/J19 范式）。
7. **被动基线**：p2_calibration 记录常数（EW48 buyhold + monthly），不重跑
   （测量批无新搜索，被动 null 照 P3 口径引常数）。
8. **政体切片（charter §三必报，P-5/P-5B 教训）**：
   (a) IS / IS2 段分； (b) 日历年逐段收益； (c) R-配3 大熊态 vs 常态日切片。
9. **R-配3 应用层 REPORTING-ONLY pass 1（数值触发器冻结于此）**：
   - 熊态定义**引用唯一源** firm/risk/regime.py 常量（MA_WINDOW=250、
     DD_LINE=-0.20、CAP_MAJOR_BEAR=0.20、CAP_NORMAL=0.80——import 引用，
     禁本地重定义）；日频熊态序列=同一双条件（close<MA250 且 距250日高
     回撤≥20%）按日展开。
   - 覆盖算术：cap(t)=state(t-1)（**前一交易日的状态作用于当日**，无未来
     数据）；overlay 收益 r*(t)=r(t)×cap(t-1)；现金腿本期收益记 0
     （逆回购腿=Phase 1 交付件，如实披露，不虚构收益）。
   - **硬门**：派生日频序列末日三布尔（is_major_bear/below_ma250/
     dd_triggered）必须与 regime.py major_bear_state(close) 逐位一致，
     不一致 ⇒ 批 VOID（唯一源一致性门）。
   - 产出仅新增字段（r_pei3_* 前缀），不改任何在册证据。
10. **判读模板（预注册，连续性口径，报告制非闸门）**：
    - benefit = EW6 Sharpe − Σw_i·member_i Sharpe（>0 为分散化真实）；
    - 六条款 G1'（常数读自 p2_calibration，禁手抄）：i>随机p95、ii>0、
      iii 回撤≥-35%、iv 笔数≥30（组合笔数=成员和）、v IS2 双正、
      vi>被动+0.1；
    - x2 存活（full>vi_bar 且 IS2 sharpe>0）；
    - worst_year > -30%；
    - **适用性披露**：Sharpe 类条款含政体红利折价读（P-5B：6/6 成员在随机
      起点下 beat_rate 全 FAIL 0.70 线）——EW6 verdict 字段是**描述性连续
      指标**，不构成 G3 注册门、不构成资金分配依据；分配决策=charter §五
      T1 上报总经理，实盘承诺=CEO 唯一门。
11. **产物**：results/portfolio_ew6.json（含 audit.workers、prereg sha256、
    trials_ledger=science_gates.append_ledger dict schema、corr 矩阵、
    R-配3 状态序列、政体切片全量）+ research/shortline/ew6_results.csv
    （12 member 行 + 2 组合行）+ 本文档 §6（跑后追加）。
12. **锚定硬门（批 VOID 条件）**：6/6 成员 1x 证据逐位复现
    （_evidence_matches）且注册 cost_x2 证据 |Δ|<ANCHOR_TOL。任一破 ⇒
    批 VOID，无 verdict，禁修复重跑（新预注册另开）。

## 三、预测对照（J19 闭环纪律，跑前写死）

| # | 预测 | 置信 |
|---|------|------|
| P1 | 锚定门 6/6 PASS | 0.95（同机制 smoke 20/20 + 交互会话 0:27 六员全绿） |
| P2 | EW6 全期平均两两相关 ∈ [0.30, 0.60]；IS2 段高于 IS 段（P3 政体趋同律） | 点估 0.45 |
| P3 | EW6 full Sharpe ∈ [0.55, 0.95]（3员EW=0.9229；三新员 IS 0.62-0.78 稀释 + 低相关分散化对冲） | 0.70 |
| P4 | benefit ∈ [+0.00, +0.25]；若 <0 = 新员与 core48 池同源稀释的诚实发现，照报 | 0.60 |
| P5 | EW6 x2 存活（成员 x2 0.40-0.59 × 分散化；P3 EW3 x2=0.575 先例） | 0.85 |
| P6 | R-配3 overlay full Sharpe 与基础差 ∈ [-0.15, +0.15]，worst_year 改善 | 0.55 |
| P7 | 政体切片：熊态日 Sharpe 显著低于常态日（政体红利实证，预期现象非失败） | 0.90 |

## 四、坑预防（写死）

- ProcessPool 作业函数禁闭包（O-2345 铁律）；panels/prices 经 initializer
  模块全局，不跨线。
- equity 曲线跨进程传 list（禁 pandas 对象跨线）。
- 派生熊态序列须对齐 510300 完整史（MA250 warmup 诚实：前 249 日=
  insufficient，按常态处理并计数披露）。
- JSON 序列化 numpy 标量必须原生化（SLEEVE_P3 坑族）。

## 五、零触碰清单

trader level/paper 字段 · engine/exit_rules.py · iron_rules · O-2210 GM 道
在制件 · T-02/T-03/T-04/T-05 车道文件 · Money02/。

## 六、结果（跑后追加，跑前必须为空）

（占位——跑后填写实测对账与 verdict，跑前写入数字即造假）
