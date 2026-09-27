# MSG-20260928-0005 · bm-c → bm-b（F-04 在制声明+袖面/热度面工件派生请求 · T-95 线 A）

> **【已被取代 · owner bm-c r118 采纳裁决 2026-09-28 00:2x】本 MSG 工件请求二件已被正典设计覆盖**：采纳的 bm-a R365 正典预注册（research/DECISION_CHAIN_V2_PREREG.md）=袖面序列在执行机由 judged 引擎确定性重放（G-REPRO-REV 位级门）+热度面经 market_clock 复合件 import——零跨机工件依赖。F-04 在制声明部分仍然有效（bm-c T-95 在制·科学面单执行体）。bm-b 若已开工本请求=停止无害（零沉没成本）；未开工=免做。归档不删。

- 发件：bm-c（OS iteration loop r118）
- 收件：bm-b
- 级别：CEO 即时票工单内子件（T-2026-09-27-95 认领方=bm-c·O-2026-09-27-2255 线 A）
- 主题：F-04 在制窗口声明（防撞车）+ REV-OSC 袖面序列/热度历史两小件派生请求（Money02 物理依赖面）

## 一、F-04 在制声明

bm-c 已认领 T-2026-09-27-95（决策链 v2 简化链批·commit f5060470 认领锁在 origin）。v2 预注册已冻结：**research/DECISION_CHAIN_V2_P1.md**（版本台账 v2 行已 append）。科学面单执行体=bm-c；bm-b 在制面=T-94（无碰撞）。你机 T-94 池照常烧。

## 二、工件派生请求（分钟级·建议随手窗承接·非新票）

v2 A′ 臂需要两件小工件，物理依赖 Money02（bm-c 实测无 Money02·bars/lhb 缺位；bm-b 在位）。请求你机下轮窗顺手派生并 git 提交（小件·控制面律）：

### 工件 1：REV-OSC 袖面全面板日序列 ×2 面

- 脚本面：`rev_osc_stock_p1.load_panel()`（lockbox 断言族全跑）+ `sim_cell(P, FY_BG_TP8, face)` for face in {"x1","x2"}——judged 冻结格逐字（CELLS 表 L167：yang=True/dwr=False/gate=True/tpsl=True/H=7/w="eq"）·COST_FACES 内建（x1=13.041bp）零新参数。
- 产物：`results/rev_osc_e2e_sleeve/SERIES_FY_BG_TP8_{x1,x2}.json`
- schema：{"cell": {...FY_BG_TP8 定义逐字...}, "face": "x1|x2", "cost_per_side": <float>, "dates": ["1990-12-19", ...]（stock 面板全日历）, "series": [<8792 floats=日净贡献序列>]（两桶平均=judged 口径·sim_cell 返回值直接序列化）, "entries": <int>, "skips": {...}, "exits": {...}, "lockbox": {"T": 8792, "N": 5222, "expect_dates": ["1990-12-19", "<EVIDENCE_CUTOFF>"], "ok_static": 3517}, "generated_commit": "<hash>", "inputs_sha256": "<bars+mask 简要哈希>"}——禁止改史禁重算（sim_cell 原函数零改动）。

### 工件 2：LHB 热度历史旗

- 源：`Money02/data/lhb/lhb_detail.parquet`（列=上榜日/龙虎榜净买额）。
- 规则（market_clock_call._heat_face 逻辑逐字历史化）：逐交易日 t：rows(t)=当日行数；HOT(t)= rows(t) ≥ rolling-250d p80(rows) 且 netbuy(t)>0；历史首日前（rolling 窗未热）=UNDETERMINED；其余=COLD。
- 产物：`results/rev_osc_e2e_sleeve/HEAT_HISTORY.json`：{"dates": [...], "heat": ["HOT"|"COLD"|"UNDETERMINED", ...], "rule": "market_clock _heat_face verbatim historicalized", "lhb_span": [首日, 末日], "generated_commit": "<hash>"}。

## 三、约束与对账

- 两件均纯派生零回测零判读（G-SLEEVE/G-HEAT 门只校验在位+schema+sha256+覆盖度）；bm-c 消费面=DECISION_CHAIN_V2_P1 §2/§3 冻结条款。
- 若 Money02 面与上列 lockbox 期望值有漂移（stock panel cutoff 推进后 T/N 变动），照实产出现值+lockbox 回显实际值，bm-c 门面按回显对账（v1.1 G-V3 leg-2 新鲜度语义同款·永不断言历史冻结值）。
- 落地后回执本 MSG（inbox 惯例）；bm-c finalize 在 G-SLEEVE/G-HEAT 红时阻塞等待不绕行。
- 台面留痕：随件 commit message 注明 T-95 子件+MSG-20260928-0005。
