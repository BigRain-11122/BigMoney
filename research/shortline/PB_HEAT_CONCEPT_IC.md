# P-B 热点概念因子批 IC 预注册（PB_HEAT_CONCEPT_IC）· 跑前写死

> 令源：O-20260923-1850 §2B/§4（P-B 车道）· 认领：MSG-20260923-2010（先于本批 commit）
> 性质：**因子层 IC 批测**（零引擎跑→引擎账本 N 不动）；IC≠策略，本批不注册交易员
> 前置件：round 39 源审计（research/digests/DIGEST-20260923-heat-source-audit.md）+ HEAT_ATTENTION_SPEC.md §2B

## §1 数据与面板（跑前事实，含分类法修订）

- **分类法定案（跑前修订，理由如实记）**：审计裁定 THS 主分类法（指数 15 年深度），但 akshare 1.18.96 **无 THS 成分接口**（`stock_board_cons_ths` 不在函数表；THS q. 域 cookie 墙=纪律不采）→ **改用 EM 分类法端到端**：
  - 板块列表：raw 直连 clist `fs=m:90+t:3`（pz=100 翻页）→ 全部 EM 概念板块（码 BKxxxx+名）
  - **成分映射：个股 f102 板块字段一揽子扫**（clist 股票宇宙 `fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23`，fields=f12,f102）——一次 ~54 页拿到全市场 stock→板块名映射，替代逐板块 cons ~800 请求（限流预算从 25min 级压到 2min 级）
  - 板块指数日线：raw 直连 push2his `secid=90.BKxxxx, klt=101, fqt=1`（前复权）
  - **直连铁律**：ProxyHandler({}) 无代理 opener（审计坑1：Clash 劫持 EM 行情域）
- **成分口径（幸存者偏差条款，spec §2B 原文适用）**：EM 成分=**现值快照**（无公开变更史端点）→ 本批用今日成分回填全史；**历史热点题材的真实当年成分不可得**，该偏差方向未知、不可量化，如实披露不粉饰
- **EM 板块指数深度=逐板块拉取时实证**（审计时被限流留白）；若整体浅于 2018 → IS 有效期数缩水，MIN_PERIODS=500 门前如实判
- **已知风险（跑前实证）**：EM push2/clist 此刻 **IP 级限流中**（20:00-20:05 我方 8 次多路由试探全 RemoteDisconnected<200ms，直连+代理+多 host+http/https 同死）→ 拉取管线带 checkpoint/断点续拉/限速 ≥2s/指数退避/连续 5 失败即停发留痕
- 价格面板：本机 `Money02/data/cache/p4_batch2_panel/`（R38-a 六门验证：T=2850×N=5212×7 列 float32，2015-01-01→2026-09-22，含 close/amount/pct_chg；6 位裸码）
- 窗口=面板全窗 2015-01-01→cutoff（P-4 批二同段；板块指数早于面板起点者截窗，晚者 NaN 起步=pairwise-complete 诚实处理）
- zt 判定（P-4 批二 spec 口径）：raw pct_chg ≥ 板别阈值（30xxxx/68xxxx=20%，其余=10%；ST 政体代理=5%，代理规则=全史 pct∈[4.5,5.5] 日数≥3 且 pct∈[9.5,10.5] 日数=0，r36 宇宙扫描同规则从面板自推）
- 滞后：板块指数/涨停计数均为 T 日收盘可得信息 → 因子对齐 T 日信号位，前瞻收益自 T 收盘起算（**无 LHB 式滞后**——榜单才需 T 盘后披露滞后，价格类不需）

## §2 因子清单（4 算 + 1 诚实跳过；全日频、全因果、定义冻结）

| # | 因子 | 定义（冻结） | 掩码 |
|---|---|---|---|
| 1 | `hot_concept_mom_5` | max（stock 现值归属板块集合内、t 日有指数数据的板块）的板块指数 5 日动量；无归属或全 NaN→NaN | A |
| 2 | `hot_concept_mom_20` | 同上，20 日 | A |
| 3 | `hot_concept_zt_count` | max（归属板块）的**板块当日涨停家数**（现值成分∩面板，zt 判定见 §1；板块涨停家数=题材热度广度） | A |
| 4 | `hot_concept_rank_delta` | 板块热度=当日 zt_count 降序密集排名（并列按板块 5 日动量降序、再按板块码升序=确定性冻结）；rank_delta=rank(t−1)−rank(t)（正=升温）；stock=max（归属板块） | A |
| 5 | `hot_pop_rank_delta` | **SKIP 诚实跳过**：人气榜单股历史仅 ~366 bars（≈1y，审计 run-1 实证）→ IS 段无历史不伪造；走 P-C 前向轨道 | — |

- 掩码 A=当日有 bar（close & amount 有限值）；四因子全用 A（zt_count=0 是真信息：「不在热题材里」，不额外造热子集掩码——简单解一次定稿）
- rank_delta 冷板块噪声条款（披露）：zt_count=0 的板块排名由 5 日动量 tie-break 决定，其 rank_delta 为动量序噪声——设计权衡如实记

## §3 方法学（P-A LHB 范式原文适用，零新规）

- IC=逐日截面 spearman，**先掩码后排名**（J7 坑族），逐日交集内 ≥5 名，零方差→NaN；快路径=pa_lhb_ic 的 rank_rows/ic_from_ranks 复用；**等价门禁先行**：探针因子（−60d 动量@A）随机 400 日子样本 vs composite_ic.ic_series，max|diff|≤1e-6 不过门不跑批
- IS≤2024-12-31（composite_ic.IS_END），OOS=2025+
- **h10=唯一门控期限**（短线 3-15 天令语境）；h5/h20 只对过门者补算报告列（非门控）
- null：白噪声 K=50（seed=20260923+i）@掩码 A，IS 段 p95
- 门（严口径）：**V1**=|IS IC| > max(0.02, A 掩码 null p95|IC|)；**V2**=|IS IC_IR| ≥ 0.30；**V3**=OOS 同号且 |OOS IC| ≥ 0.5×|IS IC|；IS 有效期数 ≥ 500
- 账本：零引擎跑→引擎账本 N 不动；本批 IC 计算数=4+50 记入 results JSON audit 段（compute_audit 纪律）；workers=1 向量化单进程（O-1738 内存受限算子合规）

## §4 跑前预测（写死于跑前，跑后对账）

1. `hot_concept_mom_5`：IS IC [+0.01, +0.03] 弱正（题材短动量延续，George-Hwang 相邻文献），60% 信心；OOS 保留不确定（J6 反转/动量政体切换先例）
2. `hot_concept_mom_20`：IS IC [+0.005, +0.025]（中期动量 2025+ 政体走强先例）
3. `hot_concept_zt_count`：IS IC **[−0.05, −0.01] 负向**（题材过热→h10 均值回归；P-A LHB 注意力峰值→反转 −0.064 同构假说，55% 信心）——本批最强候选
4. `hot_concept_rank_delta`：IS IC [−0.02, +0.02] 近零（冷板块 tie-break 噪声稀释）
5. 过门预测：**1-2/4**（zt_count 最可能过；mom 族 V2 IR≥0.30 难——dense 因子 IC 低但稳定，IR 能否到 0.30 是真考验）
6. 幸存者条款方向预判：现值成分回填或**高估**题材动量持续性（赢家题材被记住）， magnitude 不可测
7. 诚实预期：EM 限流若整轮不恢复，本批=预注册+拉取件交付，批跑顺延（§6 不填数字）

## §5 产物

`scripts/pb_heat_pull.py`（拉取件：board_list/stock_f102/klines 三段，checkpoint 断点续拉）→ `Money02/data/cache/pb_heat/`（gitignored）
`scripts/pb_heat_ic.py`（批跑件，gated on 缓存完备）→ `research/shortline/pb_heat_ic_results.csv` + `results/shortline/pb_heat_ic.json`
verdict 轮报告+CODELY.md 留痕；spec §2B 状态回写+动物园新族先入表。

## §6 跑后实证（跑前留空——写数字即造假）

