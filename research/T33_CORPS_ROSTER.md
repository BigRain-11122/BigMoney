# T33_CORPS_ROSTER 预注册 · T-2026-09-24-33 deliverable-1 军种归属判定批

> 模板=research/PREREG_TEMPLATE.md · 顶层权威=firm/STYLE_CORPS.md v1.1 · O-20260924-2012 §一.4/§五
> 本批=**归属判定聚合批**（对既有 recorded cells 的分段聚合+军种标注），非新信号试验批。

## §0 批件身份

- 批名：T33_CORPS_ROSTER（28 员军种归属表 v1）· 批号格数=**0 新试验格**（纯聚合，账本 0，t24_prospect_paper「聚合非试验」先例）
- 认领：F-04 MSG-20260924-2031 先行；票=T-2026-09-24-33（claimed by bm-c，commit 4eeb56a 锁）
- 部门归属：dept:研究+交易（风控 router spec=d3 另批）
- 算力预算：纯本地聚合 <1min，零 spawn 零网络；批报告带 audit 段

## §1 α 机制段

- 机制段四选一：**行为偏差＋风险溢价（聚合面）**——军种制主张=风格-行情适配溢价（防守反转族在 bear 段的对手方为追涨杀跌行为偏差付出代价；趋势突破族在 bull 段由动量追逐溢价补偿）。本批不引入新信号函数，仅聚合既有批证据，D6 同族检查=不适用（零新函数入批）。
- 账本：ledger_trials_added=0（源批 T22_VIRTUAL_TIMEPOINTS/T24_G2_PACK 已计；聚合标注不重复计费——反重复律）。

## §2 数据与面板

- 源据（全为 recorded cells，禁重跑）：
  - T-22 legacy c1 cells：`results/t22/cells_legacy_base_c1.jsonl`（7,530 行）+ `cells_legacy_x2_c1.jsonl`（7,530 行）=6 在册员×1,255 起点×{6m,12m,24m} 内嵌指标；regime 字段=起点态。
  - PROSPECT 池：`results/prospect_pool.json`（22 记录格）+ `results/prospect_g2/PROS-*.json`（22 件 G2 pack）。
- evidence_cutoff=**2026-09-23**（源批同 cutoff，前向锁盒随源批）；结果 JSON 顶层带 `science_gates.cutoff_meta` 键。
- 数据完备门（不过即中止 exit 2）：cells 双件在位且各 7,530 行、6 员齐；pool=22 员；G2 pack=22 件。

## §3 方法学（跑前冻结）

- 分段定义：复用 `t22_virtual_timepoints.regime_proxy` 冻结原语（510300 close vs MA200 三态 bear/chop/bull，disclosed proxy 非门，与 REGIME_GUARD v3 分立）——段=cell 起点所处态，零重实现。
- 在册 6 员归属规则（主判据=**base face · 12m 窗**，跑前写死）：
  - 段统计 per trader×segment：n_startpoints、beat_rate_12m（beat_12m=true 占比）、pooled_excess_12m（mean(ret_12m−p_ret_12m)）、n_trades_12m、worst_dd（该段全部窗 min(dd_6m,dd_12m,dd_24m)）、Wilson 95% CI。
  - **segment_pass = beat_rate_12m ≥ 0.50 AND n_startpoints ≥ 30**（D7 分段样本地板）。
  - **corps_assignment = 过段中 beat_rate_12m 最高者**（平手=pooled_excess_12m 高者）；无过段=`no-dominant-segment`。
  - **no_blowup 门槛=全段全窗 worst_dd ≥ −0.35**（红线口径同 G2 worst_year_floor）——不满足则归属降级 `blowup-veto`。
  - x2 面/6m/24m 窗=全量披露非判据（防事后择优）。
- PROSPECT 22 员候选军种映射（**仅 O-2012 §3 CEO 明示清单**，其余诚实 pending）：
  - attack 候选族={vol_breakout, inside_bar_breakup, duck_head}；chop 候选族={bb_squeeze_breakout, doji_at_low, hammer_reversal, three_methods_up, oversold_bounce_20_15}；pending={ma_converge_break, immortal_guide, ants_climb, rsrs_timing}（未入令面清单，禁臆断分类）。
  - 证据行=G2 pack（per_year/neighborhood/cost_x3/worst_year）+pool recorded stats（oos/x2 sharpe、max_dd、n_trades）；no_blowup=recorded_max_dd ≥ −0.35 且 worst_year ≥ −0.35。
  - 状态=**candidate**（段证据未采——T-22 仅覆盖 6 在册员；段证据待 d2 进攻军 G1' 波+后续分段批；归属 assign 仅对有段证据者生效）。
- 独立段数披露：以 regime_proxy 序列 episode 计数（连续同态段）报 per-segment 覆盖的独立段窗数下界（起点离散分布如实）。

## §4 判据

- 归属=数据判定非点名（O-2012 §一.4）：候选军种=目标行情段跑赢被动＋全史不爆仓的证据段。
- 判线全表（冻结）：beat_rate_12m≥0.50；n≥30；dd≥−0.35；映射表见 §3。
- 不设翻案面：本表为 v1 基线，归属变更=新证据+留痕（STYLE_CORPS §8）。

## §5 预测（跑前写死）

1. 全 6 在册员系防守/反转族（O-1600 熊市段实证+票面披露）→ bear 段 beat_rate_12m 预期为各员最高段 → 防空军 assignment 主导。
2. chop 段起点稀薄（~87/员量级）→ CI 宽，如实披露；个别员 chop 段可能不达 n≥30 地板。
3. 22 PROSPECT 员零段证据 → assigned=0、candidate=22（attack 候选 6 件·双 exit 变体计族、chop 候选 10 件、pending 6 件——按族计 3/5/4）。
4. x2 面段 beat_rate 普遍低于 base（成本拖拽），不改变主判据面结论。

## §6 算力与工程

- <1min 单进程；selftest 子命令=离线自检（合成 fixture 走自然 JSON 面构造，r52 坑律）；exit 契约=0 正常/2 数据门红。

## §7 结果回填（run#2 正典 · 2026-09-24 20:4x bm-c）

- **工程双跑留痕**（r55 范式）：run#1 join 缺陷=G2 entry_key 函数名 `oversold_bounce` 与池名 `oversold_bounce_20_15` 不匹配→OVB 2 员误落 pending+证据行 null；修实现禁改判据（alias+下划线变体 join，J18）→run#2 唯一产数正典。判据零改动。
- **在册 6 员归属**（base·12m 主判据，全员 no_blowup=True，worst_dd −0.28~−0.17 ≥ −0.35）：
  - COMPOSITE-CE-01 → **attack**（bull 段 beat 0.8191/n=470/excess +0.082 为其最高段；bear 0.5659/chop 0.7356 亦过线但 argmax=bull）
  - COMPOSITE-CE-02 → **chop**（chop 0.6667 > bear 0.6533 > bull 0.634，n=87）
  - DROUGHT/ENGULF/NEEDLE/VOLATILITY → **chop**（chop 0.6207/n=87 为各自最高过段；bear 0.53-0.59、bull 0.54-0.57 均较低）
  - **defense=0**：全 6 员 bear 段 beat_rate 均非其 argmax 段（0.526-0.659）
- **PROSPECT 22 员候选**：attack 5（VOB-CE/IBB×2/DUCK×2）·chop 10（OVB×2/BBS×2/DOJI×2/HAM×2/TMU×2）·pending 7（ANTS×2/IMM×2/MCB×2/RSRS-CE）；状态全=candidate（零段证据，待 d2 G1' 波+分段批）；no_blowup 22/22 由 recorded_max_dd 与 G2 worst_year 双面披露。
- x2 披露面（非判据）：成本拖拽可见（如 COMPOSITE-CE-01 bull base 0.8191→x2 0.7553）。
- 产物=results/corps_roster.json（28 员·per-member 证据行·Wilson CI·episode 块数·audit 段 ledger 0/engine 0）；selftest 21/21（S6b 下划线 join 防回归）。

## §8 判据对账与预测对账

| §5 预测 | 实测 | 裁定 |
|---|---|---|
| 1. bear 段主导→防空军 assignment 主导 | **未中**：chop 5+attack 1，defense 0——防守/反转族的 argmax 段=chop 非 bear；COMPOSITE-CE-01 bull 0.819 为全表最强段 | 预测未中如实记；数据判定优先于风格先验（§一.4）；在册 cohort 的 bear 段证据真实存在（0.53-0.66）但非各自最高段 |
| 2. chop n=87 稀薄→CI 宽 | 命中：n=87≥30 地板过、CI 如实宽（如 0.62→CI~[0.52,0.71]） | 命中 |
| 3. PROSPECT 按族 3/5/4 | 命中（族面）；成员面 5/10/7（VOB/Rsrs 无 default 变体致成员数≠族×2） | 命中+成员面差异披露 |
| 4. x2 段 beat 普遍低于 base | 命中（抽样核验 0.819→0.755 等） | 命中 |

- **诚实发现（喂给 O-2012 §一.3 缺口面）**：进攻军缺口的第一份在册证据=COMPOSITE-CE-01（bull 段 beat 0.819、n=470、excess +0.082、no_blowup 全过）——但按 §5 门禁其 bull 段仍须过「段内 OOS≥30 笔/独立政体窗/CI 必报」+G2 全门后才可谈军种在册；本批为归属表非晋升门。
- 账本对账：ledger_trials_added=0（聚合非试验，t24 先例）——反重复律兑现，源批 cells 不重复计费。
