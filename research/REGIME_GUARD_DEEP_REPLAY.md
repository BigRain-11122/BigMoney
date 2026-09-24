# REGIME_GUARD_DEEP_REPLAY —— 深史行情体制回放批预注册（T-2026-09-24-13 deliverable-1）

> 权威与血统：本批=REGIME_GUARD 校准族第四批（v1 `research/REGIME_GUARD_VALIDATION.md`
> @ a885044 → v2 `_V2.md` @ ee8498e → v3 `_V3.md` @ a25f47a 的冻结判据/状态机/FA
> 定义逐字沿用）；法件 `firm/risk/REGIME_GUARD.md`（§1 阈值零改动；§3.2/§3.3 法定
> 度量与门禁）。任务单 `fleet/tasks/T-2026-09-24-13-P1`（GM order O-20260924-1120
> 裁定 D5）。
> 批性质：**测量/校准回放批**——零引擎跑、零信号函数、零注册后果。产物只作 v3+ 引证
> 与 GM 简报素材；**零行为变更**（enforce 接线=已落地法 O-1325，本批零触碰）。

## §0 批件身份【必填·跑前】
- 批名/批号：REGIME_GUARD_DEEP_REPLAY（批内格数：3 matrix × 1 window = 3 组
  状态分布 + 3 组 FA 度量 + 逐 episode 分解；N_eff 不适用=非信号批）。
- 认领：F-04 先行——`fleet/inbox/MSG-20260924-1455-bm-b-claim-T13.md`（claim
  commit 3e4f326）；任务单引用=T-2026-09-24-13-P1。
- 部门归属：dept:研究（政体研究团队）+数据部（任务单法定归属；bm-b 执行）。
- 算力预算：单进程纯本地回放，预计 <1 分钟、零网络、零引擎；worker 数不适用
  （单机单进程，R41 教训不适用=无批跑批）；轮报告如实带 audit 段引用。
- 账本口径：**trials=0**（测量批无引擎腿；不调用 `science_gates.append_ledger`；
  SEED_REGISTRY 零占用；K=50 null 腿不适用=无信号函数，v1 校准先例同口径）。

## §1 范围、素材与分段定义【冻结】
- 回放窗：**2005-04-08 → 2026-09-22**（hs300 指数面全史；21.4 年）。
  evidence_cutoff=2026-09-22（Money02 指数面最后一根已收盘 bar；与 ETF 面板
  09-23 尾差 1 日如实披露）。主窗分析段=全窗；连检段=2020-01-02→2026-09-22
  （与已记录 v1/v2/v3 批窗对齐，尾差 1 日披露）。
- **bench=指数面单一序列**：`Money02/data/index/hs300.parquet` close（5216 行，
  2005-04-08 起）。**禁与 ETF 价格面拼接**（指数点 vs 元=量纲不同，中途换基必造
  人为跳变）；基准差异（ETF 跟踪误差+费用拖累+分红除权 vs 指数价格收益）由 §2 D-C
  量化披露、由 D-D 门判定其是否翻转审计结论。Money02 全程只读（铁律）。
- 维度可用性与 warmup（逐维冻结，state 机跑满全窗、缺维=不触发=honest floor）：
  - crash10d：自第 11 根 bar（~2005-04-21）；panic1d：自第 2 根。
  - MA200（#10 收编趋势维）：自第 200 根（~2006-01）；R-配3 MA250+250 日高点
    回撤≤−20%：自第 250 根（~2006-04）。
  - vol20 3y 分位：vol_ok=live 同语义（`vol_cum > 756+20`，~2008-04 起）。
  - 广度（core48 close<MA20 占比）：**n_valid ≥ 5 才启用**（深窗专用语义，
    t18_deep_axis ≥5 员规则先例；live 点函数语义零触碰）；core48 各员 as-of
    语义（首员 ~2012-06 起 valid）。n_valid<5 → 广度双维不触发。
  - FOMC：冻结日历只覆盖 2020-2026（v1 §1.1 冻结清单）→ **2020 前 event_fomc
    恒不触发**（冻结清单覆盖面如实披露；FOMC 只触发最低级黄，R+O 份额零影响，
    升黄 FA 度量有轻量低估=披露项）。
  - 长假前 1 交易日：bars-gap 派生=回放态全窗合法（v1 §1.1 逐字）。
- 状态机初始化（冻结）：init_day=首个 bench 日 2005-04-08，prev_state=raw@该日
  （warmup 缺维→GREEN），streak=0；升降级语义逐字=live（升级即时；降级需连续
  2 个 GREEN 信号日；v3 matrix 用 resolve_state_v3 既有 B/C 语义）。
- **Episode 分段定义（机械规则冻结，命名=标签不影响边界）**：
  - dd250(t) = close(t)/max(close[t−249..t]) − 1（min_periods=250）。
  - 危机段 C：起=非危机态下首日 dd250 ≤ −15%；止=段内首日 dd250 > −5%（滞后带
    −15%~−5% 防抖，与状态机降级语义同风格）；窗尾未恢复=truncated。
  - 命名对照（§7 回填时按峰谷日期标注）：2008 GFC、2011 熊、2013 钱荒、
    2015 杠杆熊/2016 熔断、2018 贸易熊、2020 COVID、2021-22 熊、2024-01 微盘崩
    ——以及任何机械规则发现的段后命名。
  - FA 回合归属：回合首日 ∈ 段 C → 段内 FA；否则段外 FA。

## §2 数据完备门【跑前硬门，不过=批无效】
- **D-A 指数面完整性**：dates 严格单调无重复、close 无 NaN、首日 ≤ 2005-04-08、
  行数 ≥ 5200；实测值（5216 行）与末日照跑时记录。
- **D-B 10444 锚**：Money02/data/bars 文件总数 = 10444、parquet 数 = 5222
  （T-18 GC 同锚，任务单 deliverable-4 指名）。
- **D-C 基准差异量化（测量+粗界）**：重叠窗 2012-05-28→2026-09-22 上 hs300 指数
  vs sh510300 前开 twin 的日收益差 |Δr1|：**max ≤ 200bp**（硬界；超出=数据腐坏
  非跟踪误差）+ 全量披露 median/p99.9/10 日累计收益 max|Δ|（ETF 分红除权日差
  与费用拖累如实入册）。
- **D-D 连检门（基准不翻转结论）**：指数基 2020-01-02→2026-09-22 子窗 vs 已记录
  ETF 基三批：|R+O 份额 Δ| ≤ 6pp 且 ORANGE FA 率 Δ ≤ 20pp（v1/v2/v3 逐 matrix
  判；任一超界=verdict CONTINUITY_FAIL，禁在未明基准语义前下稀缺性结论）。
  记录基准（ETF 面）：v1 R+O=61.58%/FA 81.8%；v2 26.53%/57.1%；v3 记录值以
  results/regime_calibration_v3.json 为准（§7 回填引）。

## §3 方法与判读【冻结】
- 回放：`_LEVEL_FNS`/`_RESOLVERS` 三矩阵逐字复用（v1/v2/v3 语义零改动零手抄，
  引 scripts/regime_calibration.py 冻结分派）；FA 定义逐字=v1 §3.2（升橙 ≤20
  bench 日再跌幅 <5% 记误报；升黄 ≤10 日 maxDD<3%；truncated 单列不并入主率）。
- G1/G2/G3 法定值=law §3.3 逐字引用（R+O∈[2%,25%]；ORANGE FA≤60%；零空档）——
  深窗按同值审计，仅作诊断引用（本批无 PASS/FAIL 执法语义，v3 enforce 为已批
  法案不受本批影响）。
- **J1（v1 稀缺性裁定，冻结三带）**：深窗 v1 R+O > 40% → G1 败因=结构性非稀缺
  （趋势维长驻留本性）；∈(25%,40%] → 混合；≤ 25% → 稀缺驱动（6.7 年窗不典型）。
  ORANGE FA 同法：> 60% → 结构性；≤ 60% → 稀缺驱动。
- **J2（v2 同法三带）**：v2 为 1.53pp 边缘案，深窗裁定其越界是否窗驱动。
- **J3（v3 窗外稳健性）**：深窗 v3 R+O ∈ [2%,25%] 且 ORANGE FA ≤ 60% → v3
  6.7 年 PASS 在 21 年窗外复现=稳健引证；否则=脆弱性发现如实呈报 GM（零触碰
  enforce 接线，引证面仅此）。
- **J4（逐段表）**：每 episode × {v1,v2,v3} 状态日分布 + R+O 占比 + 段内/段外
  ORANGE FA 计数；回答任务单 deliverable-3（v1/v2 双杀是否 episode 稀缺驱动）。
- 判据冻结声明：本批判据=本节+§2（测量批先例=v1 校准批自设 G 门，非信号批
  g1_prime_v2/g2_registration_v2 共享库口径；D6 同族相关检查不适用=无信号函数
  入批；h10 不适用=无因子面）。

## §4 跑前预测【跑前写死，§7 对账】
1. v1 深窗 R+O：45-60%（2008/2011-13/2015-16/2018/2021-24 长程 below-MA200 段
   支配）→ J1 预判=结构性。v1 深窗 ORANGE FA：65-85%。
2. v2 深窗 R+O：20-32%（跨 25% 门两侧，诚实宽带）；ORANGE FA：40-65%。
3. v3 深窗 R+O：8-18%；ORANGE FA：30-60%。
4. Episode 数：7-11 段；2008=全矩阵最大 RED 簇（2008 非重仓 RED → 先查实现
   bug）；2015 段 v2 应有 crash10d≤−12% raw RED 日（若无 → 先查 bug）。
5. D-C：median |Δr1| < 5bp；段外 v1 ORANGE 回合 ≥ 全回合 40%（磨底期 MA200
   驻留 FA 主体）。
6. 2020-01→2026-09 指数基子窗连检（D-D）：三 matrix R+O Δ ≤ 3pp 预期（带宽 6pp）。

## §5 工程纪律【冻结】
- 新脚本 `scripts/regime_deep_replay.py`（唯一新代码件）：子命令 gates → replay
  → selftest；**import 复用** scripts/regime_calibration.py 原语（bench_dim_series/
  breadth_series/raw_series/state_replay/_LEVEL_FNS/_RESOLVERS/_episode），
  regime_calibration.py 本体零改动（FA 回合扫描 ~12 行在深脚本内薄封装，
  逐字沿用 v1 §3.2 定义并注明行级复用）。
- bench 加载器：hs300.parquet → pd.Series（date 索引）喂入既有原语。
- 产物（全 NEW）：results/regime_deep_replay.json（顶层 evidence_cutoff 必带=
  science_audit C2 合法键；含 D-A..D-D 详情、三矩阵状态分布/转移矩阵/FA、
  J1-J3 裁定、逐 episode 表、维度可用性日期表）+ results/regime_deep_replay_
  episodes.csv。
- 零触碰清单：market_regime.py（C6 指纹锚）、regime_calibration.py、
  regime_calibration*.json 已记录件、regime_state.json、live/paper.py、
  firm/risk/* 法件、engine/*、SEED_REGISTRY、Money02\（只读）。
- 分段执行合法（本轮=prereg 冻结；跑批=后续轮，续作点写回任务单）；跑后禁
  翻案禁重跑（产物写坏=确定性重执行合法，G2_FOLK 口径）；零阈值改动=本批
  不调任何 REGIME_GUARD §1 数值。

## §6 实证结果【跑前必须为空·跑后回填】（r103 2026-09-24 跑后回填）

- **裁定：批无效（GATES_FAILED）**——D-C 硬门失败 → 按本 prereg §2「不过=批
  无效」，测量腿（三矩阵深窗分布/J1-J3/episode 表）**未发射**。产物=
  `results/regime_deep_replay.json`（verdict=GATES_FAILED，四门全量详情+worst-days
  披露）；episodes CSV 未写。脚本=`scripts/regime_deep_replay.py`（selftest 16/16，
  含 r103 实弹抓出的 sub-FA 分母回归检查 I）。
- 门实证（跑时 evidence_cutoff=2026-09-22）：
  - **D-A PASS**：5216 行、2005-04-08→2026-09-22、严格单调无重复、close 零 NaN。
  - **D-B PASS**：Money02/data/bars 10444 文件 / 5222 parquet 精确。
  - **D-C FAIL**：重叠窗 2012-05-28→2026-09-22 共 3483 日，|Δr1| **max=461.59bp
    > 200bp 硬界**；median=9.792bp；p99.9=348.87bp；10 日累计收益 max|Δ|=761.95bp。
  - **D-D PASS（三矩阵全过）**：子窗 2020-01-02→2026-09-22（1631 日；vs ETF 基
    1632 日尾差 1 日披露）：v1 ΔR+O=1.37pp / ΔORANGE FA=9.60pp（界 6/20pp）；v2
    0.14pp / 0.00pp；v3 0.25pp / 0.00pp。子窗侧 v1 ro=60.21%（记录 61.58%）、
    v2 26.67%（26.53%）、v3 12.26%（12.01%）；FA：v1 72.22%（81.82%）、v2
    57.14%（57.14%）、v3 0.0%（0.0%）。
- D-D 语义注：深链（2005 起始 init）与记录批（2019 末 init）在子窗的贴合度
  0.14-1.37pp，证明指数基与 ETF 基在决策语义上高度连续——连检门作为唯一被
  授权的测量腿已经完成其使命。

## §7 跑后对账【预测 vs 实证逐条】（r103 回填）

1. 预测 1-3（三矩阵深窗 R+O/FA 分布）：**未测**——D-C 前置于测量腿，批无效。
2. 预测 4（episode 数 7-11、2008 RED 簇、2015 v2 raw RED）：未测。
3. 预测 5 D-C median <5bp：实测 9.792bp —— **错**（约 2 倍低估，但仍是正常
   跟踪误差量级；预测的「段外 v1 ORANGE 回合 ≥40%」未测）。
4. 预测 5 D-C max ≤200bp 硬界：实测 461.59bp —— **硬界失败=本批核心发现**。
   失败日诊断（worst-12 全量入册产品）：2015-07-07/08/09/10（千股跌停后救市，
   510300 涨停锁价 +9.98% vs 指数 +5.36%）、2016-01-07/08（熔断日 ETF 早收抗跌）、
   2015-08-26、2026-01-19（极端溢价日；与 r53 NAV 面 510300 premium_raw -2.56%
   独立互证）、2014-01-21、2015-01-19、2025-06-18、2024-01-18 共 12 日>200bp。
   **非数据腐坏三方佐证**：(a) 原始行逐日核验=真市场收盘价（2015-07-09 ETF
   3.463→3.809=+9.99% 涨停精确）；(b) D-A 全过；(c) D-D 三矩阵贴合 0.14-1.37pp
   （任一面腐坏不可能如此贴合）。裁定：**200bp 界把危机日涨停锁价/熔断/溢价
   冲击的 ETF↔指数微观结构分歧误分类为数据腐坏=界设计失误**。
5. 预测 6（D-D R+O Δ≤3pp 预期/6pp 带宽）：实测 0.14-1.37pp —— **对**（含
   FA 侧 0-9.6pp 全过 20pp 界）。
6. episode 命名对照表：未测（批无效，无段可命名）。

## §8 批后复盘【7-T】（r103 回填）

1. 预测对账：预测 5 median **错**（9.79 vs <5bp）；D-C max 硬界设计**错**
   （危机日分歧被误判腐坏）；预测 6 R+O 侧**对**；预测 1-4 未测。
2. v3 稳健性（J3）：未裁定（批无效）。D-D 子窗证据（ΔR+O 0.25pp）提示大概率
   成立，但按纪律不作 J3 结论引用——J3 留给再预注册后的合法重跑。
3. 脆弱性发现（如实呈报面）：D-C 界脆弱性=本批主要发现：ETF↔指数日收益差在
   涨停锁定/熔断/极端溢价日可达 ±462bp——任何以日收益差小界做腐坏检测的门
   必须危机日感知，或改用分布界+危机日单列披露。
4. 教训：硬界跑前写死时若对尾部微观结构缺乏先验，应写成「分布界（median/
   p99.9）+max 界+危机日豁免单列」三件套；单纯 max 界在 14 年重叠窗必被
   极端日击穿（本批 worst-12 中 8 日为历史级危机日）。
5. 唯一补救路径=**再预注册**（v2 批 re-prereg 先例；跑后禁翻案禁自行放宽）：
   修订 §2 D-C 界设计——候选 (a) 非危机日（双面 |r1|<5%）max≤200bp+危机日
   分歧单列全量披露；(b) median≤15bp+p99.9≤400bp 分布界+max 披露不设硬界；
   (c) max≤500bp+危机日标注。其余节（§1/§3-§5/§7 未测预测）零改动冻结沿用。
   再预注册走 F-04 认领+GM 裁定（O-1620 权限内，非红线增废）。
6. 工程交付（已在册）：scripts/regime_deep_replay.py selftest 16/16 全 PASS
   （含 I=sub-FA 分母回归，r103 实弹首跑抓出的实现 bug：fa⊂main 被二次扣减
   →fa_rate>1 数学不可能——修实现禁改判据，J18 族）；D-D 连检腿实证可用。
7. 下一步指针：T-13 任务单 note 更新（deliverable-2=gates 执行+诚实失败+D-C
   再预注册提案）；J1-J3/J4/episode 表全部留给再预注册后的重跑。
