# REFINE_BENCH_STOCK_REV_P1 · 股票面 REV 族轴普查（stage A 廉价初筛）

- 票：T-2026-10-01-139（CEO 直令 O-2026-10-01-1035「股票呢？不要光走ETF」族 1）
- 法源：REFINE_BENCH_LAW v1.0 §2 手段轴 + TRIAL_LABOR_LAW（廉价初筛先行→存活者全量判决）+ CEO 意义门 O-1901（四硬闸①千级矿先廉价普查）
- 性质：**勘探面普查（stage A）**——非判决批。无 nulls、无 gates、无 verdict；产出=排序变体表，存活者按 §4 升格规则进入 stage B 判决预注册（另行起草），届时才做 D6 同族相关与科学闸。

## §1 机制（α 段·四选一：异象改进面）

REV 超跌反弹族（CEO 原发现）在 p1c_stock 冻结面板上的系统性轴扫描。判决批 REV_OSC_STOCK_P1 只测了**一形**（Top10 最深跌幅 × BG 门 × TP8/SL10 × H7/10）；本炉按 REFINE_BENCH_LAW §2 扫全带：深度阈 / 首阳过滤 / 流动性地板 / 出场三件套参数化 / 持有期族。

## §2 数据与引擎（复用律·零重实现）

- 面板：Money02 p1c_stock 冻结缓存（T=8792 × N=5222，evidence_cutoff 2026-09-22 D2 lockbox）× b_layer 宇宙（ok_static 3517 + P4_BATCH2 s2 动态子句）——`rev_osc_stock_p1.load_panel` 逐字复用（含全部 fail-closed 门）。
- 引擎：T+1 开盘保守代理、近涨停开盘不成交、一字跌停不成交、停牌顺延、同日双触 SL 优先、跌停开盘出场顺延——`rev_osc_stock_p1.sim_stock` 机制逐字拷贝，仅 TP/SL 价格构造参数化（`_sim_axis`）。成本 x1=13.041bp/边（V1 股票档冻结值）。
- 判据/门槛：本阶段不消费 science_gates（普查面）；stage B 判决预注册时调 g1_prime_v2/g2_registration_v2 共享库（禁手抄判线）。

## §3 轴网格（冻结·烧前定稿）

depth {top10（无阈=判决批面）, −15%, −25%} × entry {raw 接刀, yang 首阳} × liq {base amt20≥5e7, liq2 amt20≥2e8} × exit {纯时间止, TP+8/SL−10, TP+10/SL−10, TP+15/SL−10, TP+8/SL−5} × H {5, 7, 10, 20} = **240 胞**。BG 门恒开（族语境；无门 BASE 面已判决，不重烧）。3 胞与判决面重合（top10|yang|base|time|h7 / …|tp8sl10|h7 / …|time|h10）标 anchor_judged=true——普查复测作引擎复用一致性锚，非重判决，语法登记去重完好。

## §4 升格规则（结果出来前冻结）

普查产出 240 胞排序表（sharpe_full / ann_ret / max_dd / entries / hit_rate / 出场计数）。升格 stage B（判决）条件：**entries≥500 且 sharpe_full 排名前 10 的独立形**（同 depth-entry-liquidity 只取最优 exit×H 形，防同族变体灌位）；与判决批已测三形的重复面不重复升格。升格批另立预注册（nulls≥2000/面 + 虚拟起点普查 + gates 全链），预期消耗面=千人题库股票语法首批候选 + REV-OSC 淬炼。

## §5 烧录与预算

- 6 分片 × 40 胞入 results\runnable_pool.json（O-2355 多核强制：ProcessPool via parallel_runner，workers=min(cap,6) 内存护栏 ~8GB/工 + 16GB RAM floor）；daemon 认领烧录；r497 工人侧 claim 握手三调用点同律。
- 预算上限：单分片 ≤10 min 墙钟；超限亮牌合法停（诚实注记），禁续烧。
- 幂等：shard-<k>of6.json 在场=done（r488 烧+翻原子）；census 全确定性（网格扫描零 RNG，双跑字节恒等由 selftest leg1/3 保证）。

## §6 自检（selftest 4 腿·hermetic）

leg1 普查确定性（双跑字节恒等）/ leg2 出场轴参数化达 sim / leg3 inline==pool 单工恒等（ems S18 惯用法）/ leg4 网格完整性（240 胞+3 判决锚）。**2026-10-01 r511 实测 4/4 PASS**（烧前）。

## §7 结果回填（烧后机械回填·占位锚）

- [ ] 六分片产物：results\refine_bench_stock\rev_census\shard-{0..5}of6.json
- [ ] 240 胞排序表 + 前 10 独立形升格名单（→ stage B 判决预注册另行起草）
- [ ] 判决锚一致性：3 anchor 胞 vs REV_OSC_STOCK_P1 判决面 x1 读数对照（引擎复用证明）
- [ ] 语法登记：TRIAL_GRAMMAR_LEDGER.md 追加 240 胞行（防重烧）

## §8 判负处置

普查面无判负语义（勘探排序非判决）；全带皆弱=合法产出（族信号在股票面不成立，如实报 CEO）。
