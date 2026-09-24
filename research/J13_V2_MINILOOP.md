# J13V2_MILL — LLM 草稿磨坊 × L1 IC 判定迷你环 · 预注册（跑前冻结）

- 冻结日期: 2026-09-24 10:1x · 认领: MSG-20260924-1010（F-04 先行）· 车道来源: R61 RD-Agent 开放池候选#2 → R64 盲测 marginal → R65 v2a viable（digest §6 后继条款的直接兑现）
- 部门归属: dept:研究（L1 IC 判定）+ 总经办（L2 磨坊，org_chart v3 J13 助理承接 O-2325）
- 性质: **候选搜索批（candidate-search），非策略批**。零引擎跑、零注册、零入池、零 SIGNAL_BUILDERS 接线；
  幸存者=候选记录，**LLM 产物=主张非指令**，判定权恒在 L1 门禁＋预注册（R61/R64/R65 条款原文）。
- 算力预算: 磨坊 32 草稿×[10,40]s≈[5,21]min（**>10min 必须后台化+逐草稿 checkpoint 追加**，R41/r52 截断教训）；
  IC 判定 <1min（core48 面板 32 候选+50 null）。GPU 接触=经 Ollama（J13 授权常设服务白名单，单次短推理，不碰 keepwarm.pause 阀）。
  批报告必带 audit 段（compute_audit；Ollama=白名单服务非我方 GPU 越权）。

## §0 批件身份

- 批族: J13V2_MILL（本文件=族级预注册，**判据族内所有 run 永久冻结**，见 §9 章程）；首个 run=**J13V2_MILL_IC1**。
- 每格计数（D1 扩容即买单）: trials = 去重后进入 E4 计算的独立公式数（含 E4/E5 失败=attempted，P-1c「computed+error+nulls」先例）
  ＋ K=50 null；E1-E3 格式失败=磨坊机械噪声（留档不计 trials——未触面板无数可筛）。
- 账本: 因子账本（results/shortline/），`science_gates.append_ledger("j13v2_mill_ic{n}", trials, "results/shortline/j13v2_mill_ic{n}.json", evidence_cutoff=...)`；
  引擎账本不动（零引擎跑）。

## §1 α 机制段【D6——搜索批的诚实结构】

- [x] **行为偏差**（搜索空间级）: ETF 日线 OHLCV 公式空间=散户/游资行为足迹——隔夜跳空=情绪过度反应、
  量价关系=注意力驱动交易、短期反转=处置效应/过度自信、趋势延续=反应不足。对手盘=追涨杀跌的迟到者与注意力稀缺的锚定者。
- **单候选机制=幸存后置**: 本批是搜索批，草稿个体机制未知；任何幸存者进入下游（合成/策略）批前，须在**该批**预注册
  补其机制段与同族准入——无机制论证不采纳，幸存≠机制成立。
- **同族相关性准入检查【必填·逐候选】**: 每个候选算 `max|corr|`（候选 h10 IC 序列 vs **内部 28 因子注册表
  （engine.factors.FACTORS）**的 h10 IC 序列，同面板共享 IS 日 ≥500，pearson on daily IC）：
  - `max|corr| ≥ 0.7` → 标签 **same_family_dup**（如实记录）→ **不计入 novel 幸存**（防「novel」实为在库因子重发现——
    R65 实证：v2a 全部 5 族均系 intraday_range/vol 族近亲）；
  - 数值与对照清单逐对列出（对照=内部 28 因子名+corr 值，JSON 留档）。

## §2 数据与面板

- 宇宙: core48 裸码池（data/daily，smoke "no-prefix" 定义，load_universe('core') 复用）。**不扩池**（扩池=P1 署名门）。
- 窗口与 **evidence_cutoff（D2 前向锁盒）**: 面板加载后**先截断到 evidence_cutoff**（=run 时数据 cutoff，IC1 预期 2026-09-23）
  再算一切（E4/E5/IC/null 全部）；cutoff 后新 bar 锁定不得回流本 run。
  结果 JSON 顶层必须带 `science_gates.cutoff_meta(cutoff)` 字段（缺=C2 VIOLATION）。
- 分窗: IS=面板起点→2024-12-31（V1/V2 判定窗）；**IS2=2025-01-01→cutoff（D2 降格如实标注，V3 稳定窗，禁再称样本外）**。
- 数据完备门（不过禁跑批）: core48 48/48 符号在场＋close 面板 ≥1500 交易日＋cutoff 新鲜度 ≤15d（smoke F1 口径）。
- 滞后规则: 因子仅用 ≤t 日数据（E3 静态禁 shift(-)＋公式自身因果）；h10 前瞻收益=判定口径非交易信号（因子批惯例）。

## §3 方法学（磨坊协议 + L1 判定，全冻结）

### 3.1 磨坊（生成侧，qwen2.5:7b-instruct via scripts.llm_assist.chat，零新传输）

- 基础 prompt = `j13_draft_probe.PROMPT_USER_V2A` **逐字**＋两条新增（构成 PROMPT_MILL，英文逐字冻结）:
  - 规则 6（R65 draft-9 ETF_close 变体收口）: `6. Use the variable names EXACTLY as listed (open, high, low, close, volume, amount); do not invent prefixed or renamed variants.`
  - 家族提示行（轮换，见 3.2）。
- 参数: temperature=0.7、num_predict=512、num_ctx=4096、system=J13 现行 SYSTEM_PROMPT（逐字）。
- N=4 草稿/家族 × 8 家族 = **32 草稿/run**；逐草稿 JSONL checkpoint 追加（断点续跑）＋原始回复全留档（audit trail）。

### 3.2 家族提示轮换（R64 机制(b) 判定维持：裸 prompt 塌缩 one-day shape 空间，谱面必须 prompt 侧注入）

| # | 家族 | 提示行（英文逐字冻结） |
|---|---|---|
| F1 | 趋势/动量 | `Target the TREND/MOMENTUM family: a lookback return over 20-120 days (close vs its own value n days ago), possibly a blend of horizons.` |
| F2 | 短期反转 | `Target the SHORT-TERM REVERSAL family: a short-horizon 3-10 day return, typically inverted (recent losers vs winners).` |
| F3 | 波动率 | `Target the VOLATILITY family: rolling standard deviation of daily returns over 20-60 days, or range-based (high-low) volatility.` |
| F4 | 量价 | `Target the VOLUME-PRICE family: volume or amount relative to its own rolling mean, price-volume divergence, or Amihud-style illiquidity.` |
| F5 | 隔夜/跳空 | `Target the OVERNIGHT family: the overnight gap (open vs previous close) and its decomposition vs the intraday return.` |
| F6 | 区间位置 | `Target the RANGE-POSITION family: where the close sits within its recent (60-252 day) high-low range, or its distance from moving averages.` |
| F7 | 时序标准化 | `Target the TIME-SERIES NORMALIZATION family: a rolling z-score or rolling rank of price, return, or volume over 60-252 days.` |
| F8 | 自由臂 | （无提示行=v2a 对照臂，磨坊漂移监测） |

### 3.3 机械门 E1-E5（复用 j13_draft_probe 判定器逐字，零重写）

E1 extract（围栏+factor=+NAME:）→ 去重（归一化代码串：剥注释/空白，**去重先于 E4**）→ E2 syntax（compile）→
E3 lookahead-static（禁 `shift(-`）→ E4 compute（core48 面板 exec，30s 超时，cutoff 截断面板）→
E5 validity（≥50% 交易日有 ≥5 有限值＋有限值占比 ≥50%＋≥30% 交易日截面 std>0）。

### 3.4 L1 IC 判定（候选级，全复用零重写）

- 前瞻: h10 主口径（唯一口径，**跑后禁换 h**——换口径=数据窥探红线）；fwd=close.shift(-10)/close-1（cutoff 截断面板上）。
- IC: 日频 spearman 截面（`composite_ic.ic_series`）＋统计块（`composite_ic.stats_block`）＝full/IS/IS2 三窗。
- 期数门: IS 有效 IC 日 ≥500（p1d/P-1c MIN_PERIODS 先例）＋IS2 ≥60；不过=insufficient（如实记，非 pass 非 fail）。
- **null 对照**: K=50 白噪声面板（`np.random.default_rng(53_000+i)`，iid N(0,1)，close 面板全 index×48 列形状），
  过同一 IC 管线 → nullA 的 |IS IC| p95 与 |IS IR| p95（双报）；seed 基 53_000 已登记 SEED_REGISTRY（rg+registry 双查空闲 2026-09-24 10:05）。
- D6 标签: §1 逐候选执行。

### 3.5 成本口径

零引擎跑=无成本模型适用；候选的可交易性只在下游策略/合成批检验（V2 ADV 三层滑点在那里的批声明）。

## §4 判据【跑前写死，族内永久冻结，禁看结果调线】

因子批三门口径（P-1a/P-1c 族系惯例）＋层级判定：

- **V1**: `|IS IC| > max(0.02, nullA |IS IC| p95)`
- **V2**: `|IS IC_IR| ≥ 0.30`（内部单因子墙——J6/P-1a/P-1b/XLIB 四证：core48 截面上该线即天花板附近）
- **V3**: IS2 同号 且 `|IS2 IC| ≥ 0.5 × |IS IC|`（D2 降格窗上的稳定性检查，禁称样本外验证）
- **层级判定**:
  - **novel_survivor** = V1&V2&V3 全过 且 max|corr| < 0.7；
  - **dup_survivor** = V1&V2&V3 全过 但 max|corr| ≥ 0.7（same_family_dup 标签，如实记录不计 novel）；
  - 其余 = fail（含 insufficient）。
- **幸存者处置**: 仅记录为候选（全统计留档 JSON）——不入因子池、不入 STRATEGY_LIBRARY 幸存清单、不注册、不接线；
  下游消费=另开预注册＋机制段（§1 后置条款）。
- 无 G2/无注册（因子级证据，非策略出厂）；本批也不触发 skill_line_v2（那是策略/组合批口径）。

## §5 跑前预测【写死于跑前】

1. 机械合格率（去重后 E4 通过率）: [50%, 90%]——家族提示引入 rolling/回看窗操作→warmup NaN 可能杀 E5；
   规则 6 应消灭变体命名死因（v2a 唯一失败=R65 draft-9）。
2. 去重独立公式数 n_distinct ∈ [10, 25]（of 32）——轮换扩谱 vs 家族内塌缩并存。
3. **novel 幸存（V1&V2&V3+corr<0.7）: [0, 2]**——诚实低预期：core48 48 名窄截面单因子 IR 0.30 墙=P-1a/P-1b/XLIB 三库实证；
   R65 已证 v2a 全部 5 族系在库近亲；动量向家族（J6: mom_12_1/price_position 2025+ 走强）可能产出 IS 弱/IS2 强候选→V2 杀。
4. 最常见死因预测: E5 validity（F3/F7 rolling warmup 压缩有效日覆盖）＞ E4（命名变体残留）。
5. V1 过线者中 same_family_dup 占比 ≥ 50%（R65 在库同源性外推）。
6. 磨坊墙钟 32×[10,40]s=[5,21]min→后台化强制；IS 弱/IS2 强的「政体红利型」候选（P-5/P-5B 政体依赖教训）不因 IS2 强而上调评级。

## §6 产物

- `scripts/j13v2_mill.py`（run/selftest 两子命令；磨坊 JSONL checkpoint+判定+nulls+D6+账本；实现轮交付）
- `results/shortline/j13v2_mill_ic1.json`（磨坊 readout＋逐候选全统计＋nullA＋D6 对照清单＋trials_ledger＋audit 段＋顶层 cutoff_meta）
- 本文件 §7 回填（一次定稿；工程修复重跑双跑留痕如实记账）

## §7 跑后实证【2026-09-24 R67 bm-a 一次定稿·J13V2_MILL_IC1】

- **磨坊**: 32 草稿（8 家族×4，temp0.7）→ **去重独立公式 13**（DUP=19=家族内塌缩持续，R64 机制(b) 判定维持：
  家族提示扩了谱面跨度但未扩族内多样性）；进入 E4=13，**E4/E5 机械合格 12/13=92.3%**（E4 失败 1 例 range_position；
  E5 零触发——1632 日面板下 rolling warmup 不足以压破 50% 日覆盖门）；GEN 失败 0。
- **L1 判定: novel=0 / dup_survivor=0（诚实判负）**——**V2 内部单因子墙全灭 12 员**（最强 |IS IR|=0.129
  （range_position）<<0.30，J6/P-1a/P-1b/XLIB 四证之墙对 7B 草稿同样成立）；V1 过 5/12（IS |IC| 0.0375-0.0502>0.02
  地板；nullA |IS IC| p95=0.010045 低于地板→地板主导）；V3 过 6/12（IS2 同号且留存≥0.5，动量/标准化族
  IS2 反强=J6「mom 类 2025+ 政体走强」同向读数）。
- **D6 同族实锤: V1 过线 5 员 max|corr| 全≥0.84=100% 在库近亲**——trend_120d≡mom_120（corr=1.0）、
  overnight_gap≡gap_overnight（1.0）、short_reversal≡intraday_range/rev_5（1.0）、illiquidity_vol≡intraday_range（0.965）、
  mean_reversion/range_position≡ma_bias_60/mom_120（0.89-0.92）——7B 在冻结 prompt 下系统性重发现在库因子
  （R65 判定再证），「novel」防线必要但本轮未被触发（V2 先杀）。
- **nullA 当批读数**: |IS IC| p95=0.010045 / |IS IR| p95=0.06705（K=50，n_periods≥1212）——白噪声 IC 均值带
  远低于 0.02 地板=V1 地板主导结构性成立；该读数为族内后续 run 的 null 参照档（种子梯子换基后重算）。
- **账本**: 因子链 5476+63（13 公式+50 null）→ **5539**；引擎账本不动（零引擎跑）；evidence_cutoff=2026-09-23。
- **停环监视**: novel_zero_streak=1（须连续 2 run 且 n_distinct<8 才 park）；n_distinct=13≥8 → 磨坊线按 §9 继续。
- **工程双跑留痕（诚实）**: r1 finalize 崩于白噪声面板构造 shape bug（`index.size` 误用→1632×1632 vs 1632×48），
  修复+自测锁（`_noise_panel` helper+end-to-end null_band selftest，22/22）后 r2 finalize 数字逐位复现；
  r2 账本误走引擎链（append_ledger 默认 results/ → prev=3041/total=3104）违反 §0 因子账本=results/shortline/，
  修=science_gates.append_ledger 加 `prev_total` 覆盖参数（加性默认 None=legacy 零行为变化，selftest 30/30 加锁）
  +磨坊侧按 r60 单链双目录 max 约定（p1c `_chain_head_total` 先例）重算 prev=5476 → r3 finalize 总账 5539 定稿；
  **磨坊相位从未重生成**（checkpoint 32 件续跑冻结）=审计轨迹保真，三跑判定数字逐位相同（判定侧确定性设计应验）。

### §7.2 跑后实证【2026-09-24 r92 bm-b 一次定稿·J13V2_MILL_IC2】

- **磨坊**: 32 草稿（8 家族×4，temp0.7）→ **去重独立公式 11**（DUP=21——族内塌缩持续，IC1 DUP=19 同向第三证）；
  进入 E4=11，**E4/E5 机械合格 10/11**（E4 失败 1 例）；GEN 失败 0；磨坊墙钟 17.1s（与 IC1 逐位同量级）。
- **L1 判定: novel=0 / dup_survivor=0（诚实判负）**——**V2 内部单因子墙全灭 10 员**（最强 |IS IR|=0.142
  （short_reversal/高低开比率，日内振幅族）<<0.30；IC1 最强 0.129 同墙同判=**墙的跨 run 稳定性第二证**）；
  V1 过 3/10（|IS IC| 0.0269-0.0502>0.02 地板；nullA |IS IC| p95=0.00752 低于地板→地板主导结构性成立）；
  V3 过 5/10（twelvemonth_return/close_zscore 等 IS2 同号留存≥0.5）；**D6 未触发**（V2 先杀，D6 只对全三门
  过线员生效）——IC1 的「V1 过线 5 员 100% 在库近亲」在 IC2 无对应读数面（无员到 D6）。
- **IS2 全正读数（机制）**: 10/10 员 IS2 ic_mean 全正（含 IS 段为负的 short_reversal −0.0502→+0.0135 翻号）=
  2025+ 政体漂移对 7B 常见公式族普遍友好（J6「mom 类 2025+ 走强」/IC1 V3 6/12 同向）——IS2 仅为降格稳定窗
  禁称样本外，无翻案权。
- **nullA 换基读数**: |IS IC| p95=0.00752 / |IS IR| p95=0.04865（K=50，seed 53_100 梯子基）——与 IC1
  （0.010045/0.06705）同带（白噪声线对换基稳健），V1 地板主导结论跨 run 成立。
- **账本**: 因子链 5539+61（11 公式进 E4+50 null）→ **5600**；引擎账本不动（零引擎跑）；evidence_cutoff=2026-09-23。
- **停环监视**: IC1 novel_zero_streak=1(n_distinct=13) + IC2 novel=0(n_distinct=11)——**n_distinct 连续两 run
  ≥8 → 停环条件（连续 2 run novel=0 且 n_distinct<8）未触发**，磨坊线按 §9 继续；但 2-run 判定数据点已齐
  （两 run 合计 novel 0/24 员、最强 |IS IR| 0.129-0.142、谱面无塌缩），下一 run 触发器归 §9 逢发式节奏
  （开放池优先级/GM/CEO 指针），禁自动连跑（每机 ≤1 run/日配额制）。
- **工程留痕**: 账本 note 标签陈旧 bug（脚本写死「J13V2_MILL_IC1」字样、batch 字段本身正确）=纯元数据外科
  修正（R57 先例，diff 1 行零数字）+脚本侧改用 BATCH 泛化防复发；磨坊/判定零重跑（checkpoint 32 件冻结，
  finalize 单跑定稿 168.7s）。

## §8 批后复盘【s7-T 已填·R67】

- **预测对账（§5 逐条）**: ①机械合格率 92.3% vs [50,90] —— 方向对、带上沿外 2.3pp（部分对）；②n_distinct 13∈[10,25]
  **✓**；③novel 0∈[0,2] **✓**（带下沿）；④最常见死因预测 E5>E4 —— **错**：机械层 E5 零触发（DUP 19/E4 1），
  真死因在判定层 V2 墙（12/12）；⑤same_family_dup 占比 100%≥50% **✓**；⑥墙钟 [5,21]min —— **错**：实际
  ~2min（磨坊 17.1s+finalize 87-105s；R64 探针 gen_s=0.3-1.8s 早已实测，预注册估算沿用了 spec 起草时的
  [10,40]s 假设未回查探针数据——教训：预算段估算须回查在库实测）。
- `results/gate_attrition.json` 已追加 j13v2_mill_ic1 条目（kind=search，eliminated=13-0=13 进 E4 全灭于 V2）。
- 幸存者=0 → 无候选登记、无下游消费动作；磨坊线按 §9 继续（停环监视未触发）。

## §9 迷你环章程（recurring charter）

- **判据永久冻结**: §3/§4 对族内一切 run 不变；后续 run 禁调门槛禁换口径（改=另开预注册重立族）。
- **每 run 三件套**: ①MSG 认领（F-04）②新 null seed 基登记 SEED_REGISTRY（**梯子=53_000+100×(run−1)**，
  每 run K=50 取 base+i, i<50，run 间隔 100 无碰撞；r66 冻结前 rg 双查律照走）③本文件 §7 追加子节＋append_ledger（批号 j13v2_mill_ic{n}）。
- **节奏**: 逢发式非每轮——触发器=开放池优先级/GM/CEO 指针/板空且队列见底（O-1819 条款）；**每机 ≤1 run/日**
  （7B 算力公民义务＋D1 经济性——每次 run 都是 32+50 真试验入账）。
- **停环条件**: 连续 2 run novel 幸存=0 且磨坊谱面塌缩（n_distinct < 8）→ 磨坊线 park 呈开放池复评（禁自动迭代 prompt 再盲测——
  两连 marginal/park 判例=R64 §3 冻结条款精神）。
- **判定权边界**: 磨坊永远不写任何池/注册件/策略代码；幸存者消费=人工（GM/CEO/预注册）审后另开批。LLM 产物=主张非指令。

## §10 边界与诚实声明

- 本预注册授权范围=磨坊+IC 判定管道；**不授权**任何幸存者直接进入交易/合成/注册——那是下游批的预注册权。
- 磨坊生成非确定性（temp=0.7）→ 原始草稿全留档为唯一 audit trail；判定侧给定草稿确定性可复现（E2-E5+IC 重放）。
- 账本只记本 run 真试验；「跑后禁调门槛禁重跑」对本族同样生效（工程 bug 修复=双跑留痕先例）。
