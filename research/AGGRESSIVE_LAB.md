# AGGRESSIVE_LAB — 激进组合试验线预注册（跑前冻结）

> 令：O-20260925-1126（CEO 直令「设立激进的各种组合，最大化的激进，现在你太保守了！」）· 票：T-2026-09-25-56（P1·immediate）· 认领：bm-a R157（claim d03b1ae2 后 rebase 推送）。
> 双轨制（令 §一）：本试验线=候选供给面；稳定判决台（0.70/J2 冻结线）=唯一选拔器，两轨并行互不取代。**本批零采纳零接线**——月界入 T-27 锦标赛池=常设激进候选（票 (e)），采纳仍走 GM 批准+7 天否决窗。
> 跑前冻结：本文件 commit 先于任何跑批（R99 律）；跑后只许回填 §7/§8，禁改判据禁重跑。

## §0 批件身份【跑前】

- 批名：T56-AGGRESSIVE-LAB；判断格=**100 聚合判断单元**（5 变体 × 20 格：W-CUR {x1,x2}=2 + W-SEG 3 段类×{x1,x2}=6 + W-GRID {legacy,deep}×{6m,12m,24m}×{base,x2}=12；T-28 口径逐字沿用，per-cell N 沿用 P5C/t22 已计账本不重复计数）。
- 56 sleeve = T-27 机件 o1600 口径复现（live paper 面板截断 2026-09-23，T-28 先例）→ 账本 **+0**（onboarding 先例）；账本入账=100 判断格（append_ledger）。
- 部门归属：dept:组合与资金（变体/判决）+研究（军种映射）+工程（runner/pool）joint。
- 算力：实测 T-28 同构批 5.4s（56 sleeve×25 workers）；本批同 sleeve 基座+5 帧算术 → 预估 <60s，<5min → **轮内跑合法**（R41 纪律）；pool-ready 入口登记（workers_plan O-2130）供月界重跑/舰队节点拾取。

## §1 α 机制段【D6】

- [x] **风险溢价**：混合不创造 α（P3 裁定先例）——五激进面全部=已注册 28 员 sleeve 上的**权重集中规则**，零新信号函数、零搜索、零 null 族（SEED_REGISTRY 零登记）。
- 激进≠新 α 主张：本批 KPI=**收益天花板 + 牛市段增量 vs 正典 B_MAXDIV**（票 verbatim），非过闸数；集中度本身是待测量，非待主张。
- 同族相关性准入：N/A（零新信号函数）；替代披露=五变体组合日收益两两 corr（描述性）+ 与正典 B_MAXDIV 面 corr。

## §2 数据与面板【跑前事实】

- 成员池：T-27 v2 冻结 28 员 roster（set 相等门；6 INTERN + 22 PROSPECT）；evidence_cutoff=面板截断 2026-09-23（sleeve 截断律同 T-28：cutoff 后新 bar 不回流本批）。
- 面板：live.paper.load_core() core48（o1600 口径）截断 W_CUR_END=2026-09-23；完备门=面板 cutoff ≥ 2026-09-23。
- 政体序列：live.paper.v3_state_series() 原始四态（GREEN/YELLOW/ORANGE/RED）import-replay 单源现算（T-21 语义，无缓存）。
- 军种名册：results/corps_roster.json（T-33 v1）——进攻(attack)=6 员 {COMPOSITE-CE-01 + PROS-DUCK-01/CE-01 + PROS-IBB-01/CE-01 + PROS-VOB-CE-01}；震荡(chop)=15 员（5 在册 + 10 候选）；**防空军=0 员（名册诚实发现）**；pending=7 员（ANTS×2/IMM×2/MCB×2/RSRS-CE）权重 0。
- 锚定输入：portfolio_blend_tournament.json 注册权重三向量 sha 复核门（跑时断言）：B_MAXDIV=9b112d51583aeeb7、C_IVMOM=5655696a60300bf4、A_IV=3868f2f55bae825e。

## §3 五变体权重规则【冻结·逐向量 sha】

统一帧=按目标权重日再平衡于 28 员 inner-join sleeve 日收益（T-27 §3 语义；静态面向、AGGR-REGIME 政体面向）。**x2 成本面沿用 x1 冻结权重**（13bp×2 压测，CostPatch(2.0)）。

| # | 变体 | 规则（跑前写死） | 权重 sha256[:16] |
|---|---|---|---|
| 1 | **AGGR-CONC-TOP2** | 前二 OOS-Sharpe 集中：VOLATILITY-CE-01 0.50 + COMPOSITE-CE-01 0.50（注册 OOS Sharpe 2.0568/1.6085 实核于成员注册件 backtest.out_sample.sharpe；其余 26 员 0） | **9a9579482cc1851b** |
| 2 | **AGGR-OFFENSE** | 三军预算 70/15/15（进攻/防空/震荡，令 §二.2）；**防空军 0 员（名册事实）→其 15% 预算按非空军 pro-rata 重归一**：进攻 70/85=0.823529、震荡 15/85=0.176471；军内等权（进攻 6×0.137255、震荡 15×0.011765）；pending 7 员 0。重归一方向=更集中=与「最大化激进」令意一致，如实披露 | **eac2b583586e8bb3** |
| 3 | **AGGR-MOM** | T-27 注册落选者 C 复活（registered-not-deleted 律）：C_IVMOM 向量逐字复用（raw=(1/σ_IS)×(1+m_IS) 截 0 归一） | **5655696a60300bf4** |
| 4 | **AGGR-NOCASH** | B_MAXDIV 冻结权重逐字复用 + **纸盘风险预算面 cap 95% + 现金腿关闭**（账户参数面声明；判决帧 blend 面与正典字节恒等=验证腿；铁律正典 6 生产账户零触碰） | **9b112d51583aeeb7** |
| 5 | **AGGR-REGIME** | T-27 注册落选者 D 复活·v3 化：offensive=进攻军满配（6 员各 1/6）；defensive=A_IV 全 28 员（3868f2f55bae825e）；state(t−1)∈{GREEN,YELLOW}→offensive，∈{ORANGE,RED}→defensive（v3 原始四态 shift(1) 因果，首日缺省 offensive=D 先例） | offensive **b95dab70673f5941** / defensive **3868f2f55bae825e** |

- 五向量零数据搜索：CONC 选择基=注册 OOS Sharpe（已注册证据，樱桃面如实承认——本批目的即测天花板）；OFFENSE 预算=令文 70/15/15；MOM/NOCASH/REGIME-defensive=注册向量复用。
- AGGR-REGIME 网格面代表权重=时间平均权重 ā_i（T-27 D 先例）经 sleeve 域全窗计算后 CE-6 限制归一。

## §4 判据与判决台【跑前写死·T-28 J 线逐字同门】

- **W-CUR**=2026-01-05→2026-09-23（T-28 冻结窗，正典可比性）；**J1**：x1 净收益>0 且 |maxDD|≤5%；**J2**：x2 净收益>0。
- **W-SEG**=v3 段类（REGIME_MAP 映射 bull/chop/bear）；**J3**：各段类累计净贡献 ≥ −5%（两成本面全段类披露，任一破界=J3 FAIL）。
- **J5 D7 四必报**（逐变体逐网格单元披露，非门）：OOS 笔数池化/覆盖年数/独立政体窗数/CI95 宽度。
- **W-GRID**=5 变体×{legacy,deep}×{6m,12m,24m}×{base,x2}；变体权重 CE-6 限制归一（网格冻结域 6 员子组合近似面，T-28 诚实披露沿用；AGGR-CONC-TOP2 限制=恒等、AGGR-OFFENSE/REGIME 限制=重归一）。
- **硬界设计三件套**（D-20260925-01①）：max 硬界=J1 dd≤5% 跑前预估（五面 sleeve 域 max|dd| 预估全部 <8%，破 8% 即异常面如实报）；分布界=逐变体日收益 median/p99.9 描述性披露；危机日感知=J3 段类面即危机段测量。
- **KPI 面（非过闸数）**：①收益天花板=W-CUR x1 净收益；②牛市段增量=W-SEG x1 bull 类累计 − 正典 B_MAXDIV bull 类累计（正典数同跑重derive 验证腿，账本 +0）；③12m pooled beat 率全披露（对照正典 0.4854 记录）。
- **预期失败披露（票 verbatim）**：激进面预期破 J2/J3——这是诚实实验结局；落败照报禁跑到达标为止。
- 判定输出=逐变体 J1/J2/J3 布尔 + KPI 读数 + 网格 beat 率；**零采纳动作**（本批不进正典、不改 paper、不动选拔器）。

## §5 跑前预测【冻结】

1. AGGR-CONC-TOP2：五面 W-CUR x1 收益天花板最高或次高；J2 破概率高（2 员集中+成本拖拽）；J3 bear 破概率高。
2. AGGR-OFFENSE：bull 段增量五面最强；J3 bear 破近必然（82% 进攻配比含 5 员零段证据候选）；J1 可能过。
3. AGGR-MOM：镜像 T-27 C 面——中庸；J2 边缘至破。
4. AGGR-NOCASH：blend 判决面与正典字节恒等（J1/J2/J3=正典 T-28 三过）；增量全在纸盘账户参数面（cap 0.95/现金腿关）。
5. AGGR-REGIME：集中面中 J3 最可能存活（ORANGE/RED 切防御）；J2 不确定；bull 增量为正。
6. 网格 12m pooled：激进变体 ≤ 正典 0.4854（集中伤广度）；NOCASH=正典逐字节。

## §6 产物与接线【跑前】

- runner：scripts/aggressive_lab.py（t28_stable_profit 原语 import 复用：_sleeve_worker/_blend_daily_ret/_window_face/_seg_classes/_load_legacy_grid/_load_deep_grid/_grid_unit；selftest/run 子命令；pool-ready：workers_plan+分片协议字段）。
- 产物：results/aggressive_lab.json（顶层 evidence_cutoff+cutoff_meta+audit+prereg sha 嵌入）+ gate_attrition 追加行 + 本文件 §7/§8 回填。
- pool 入口：results/runnable_pool.json 登记 T56-AGGR-LAB（workers_plan 实填；首次判决跑=轮内执行 R41 <5min 豁免，月界重跑走池）。
- 纸盘接线（票 (d)·slice-2 续作，设计冻结）：5 账户 AGGR-*（各 ¥1,000,000 初始、shadow 守卫、实验风险预算逐账户申报：position_cap NOCASH=0.95 其余=0.80 生产对齐；现金腿=NOCASH 关闭声明——纸盘面结构性无停靠腿（T-09 未接线披露），live 面关注项）；marks=每日 blend 累计（sleeve 域随新 bar 推进）；s6 链消费面按 PROS-* 白名单范式加 AGGR-*。

## §7 跑后实证【跑后回填——唯一产数跑】

（待跑后回填）

## §8 批后复盘【跑后回填】

（待跑后回填）
