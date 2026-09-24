# P-5C 虚拟时间点大规模检验 · 预注册（跑前写死）

> 令链：CEO O-20260924-1532（原话：「我说过 历史数据也可以当做虚拟时间点去测，大量的去测」）→ 票据 T-2026-09-24-22 → 认领 bm-b r104（MSG-20260924-1552 先行）→ 本件=r105 首件（预注册冻结）。
> 模板：research/PREREG_TEMPLATE.md（T-02 6/7）。P-5（O-1816）/P-5B（O-2345）冻结口径直系升格：K=50 抽样 → 全史滚动全起点。
> 跑后禁调口径/禁换判据/禁以结果回头调参；工程修复重跑须双跑留痕如实记账。

## §0 批件身份

- **批名/批号**：P-5C（virtual-timepoint mass validation）。计账格=每引擎跑（策略跑=起点×员×成本面；被动=起点；锚=员），跑前粗估 **≈56,647 格**（深 18,624×2 面 + 对照 7,518×2 面 + 被动 4,357 + 锚 6），实跑入账（见 §3）。
- **认领**：F-04 先行=MSG-20260924-1552（r104）；票据 T-2026-09-24-22 claimed_by=bm-b。
- **部门归属**：dept:研究+数据（票据 note 同）。
- **算力预算**：BelowNormal 满载池（O-1136）；三机并行分片（起点区间切分：bm-a/bm-c 25 workers、bm-b 12 workers=floor(16×0.8)）；checkpoint 断点续跑（>10min 批后台化+跨轮，R41）；批报告必带 audit 段。粗估池时 1.5-3h（串行 ~13h 深腿面1 折算）；**本机 run 排队于 XSTOCK post-chain 之后**（Money02 缓存数据面争用，票据 note 同款协调；bm-a/bm-c 无此争用可先行接片）。

## §1 α 机制段（D6）

- 本批=**在册 6 员稳健性复检，不引入新函数/新 α 主张**——四选一勾选=N/A（逐员机制继承各自注册件 D6 段：VOLATILITY-CE-01=低波风险溢价；COMPOSITE-CE-01/02=风格动量溢价；ENGULF-CE-01/NEEDLE-DE-01/DROUGHT-CE-01=行为偏差形态族）。一句话论证：检验的是**在册机制在起点×政体维度的分布稳健性**（谁在虚拟平行未来中付出代价=各注册件既有论证，不在本批扩展）。
- 同族相关性准入检查=N/A（零新入册，在册相关谱不变；zoo 不动）。

## §2 数据与面板（跑前探针事实，非结果）

- **双腿**：
  - **腿 D（深轴）**：T-18 深面板缓存 `Money02/data/cache/t18_deep_panel/ohlcv`（48 员 114,142 行，2005-02-23..2026-09-22 cutoff 截断；GA 孪生-裸码 48/48 max|Δclose|=0、manifest sha 幂等=r101 实证；panel_start=2013-06-17=第 5 员 valid_from 规则）。**起点域=2013-06-17 起每个交易日**（CEO 口径 ≈3,200+ 起点）。
  - **腿 L（对照）**：legacy 6.7 年锚定轴 2020-01-02..2026-09-22（P-5 同款；同缓存切片，warmup 计入 2020+ 切片=P-5 锚定口径）。**无 GF 依赖，先行。**
- **起点网格普查（跑前探针，`results/shortline/p5c_grid_probe.json` + `logs/iteration-loop/_r105_probe.py`，确定性零网络）**：
  - 腿 D（无 MIN_LISTED 主网格，见 §3 敏感面）：6m=**3,104** 起点（2013-06-17..2026-03-23）/12m=2,978/24m=2,726。
  - 腿 L：6m=**1,253**/12m=1,127/24m=875（P-5 冻结事实 eligible=1254 vs 本普查 1253 差 1=边界约定披露，如实记录不改 P-5 存档）。
  - MIN_LISTED=24 敏感面（P-5/P-5B 口径连续性）：腿 D 首合格日 **2017-08-24**（2013-2017 薄池段 5-23 员被该门切走→主网格不设此门、以**成员数分层披露**替代，CEO 令全网格口径；6m=2,079/12m=1,953/24m=1,701）；腿 L 不 bound（listed 45-48）。
- **evidence_cutoff=2026-09-22（双腿同界，D2 前向锁盒）**：T-18 manifest cutoff=注册锚定 cutoff 同界；09-23 起新 bar 锁定禁回流本批。
- **数据完备门（不过门禁跑批）**：① `scripts/t18_deep_axis.py gates` 复跑 GA-GE PASS（GF 状态如实=见 §2.5）；② manifest sha 幂等；③ **锚定硬门：6 员 `anchor_gate` 逐位复现注册证据（cutoff 2026-09-22，P-5B 范式）——任一破=批无效即中止**；④ 双腿交易日历=缓存并集无缝（GA 已证）。

## §2.5 GF 硬门处置（O-1310 s3 · deliverable-0）

深轴面板消费属 nulls/reval 同族 gated 面（GF=T-19 stage-3 调整视图未交付）。**本批不让空等**，处置=本预注册 + 同轮 GM 裁定请求（MSG-20260924-1615-bm-b-T22-gf-gate-ruling），分支（判据三分支全同，仅 cell admission 差异，结果件按分支披露）：

- (a) **T-19 stage-3 调整视图落地**（bm-c 车道）→ 腿 D 跑调整面（最干净，首选）；
- (b) **GM 豁免 raw 面** → exposed cells 照跑 + 每格 `events_n` 暴露披露列（登记册=`data/consolidation/registry.json`，21 事件/19 符、|pct| 0.13%-1.76%、**全部 ≥2021-02-25**；策略与被动同 raw 面差分论证：注册锚定证据本身即含此 21 事件的 raw 面注册口径）；
- (c1) **洁净子集先行**：窗内零登记事件 cells（窗全程 ≤2021-02-24；t14 探测器对 2013-2020 段先行扫描=门侧探针，发现事件即移入暴露桶）先跑，exposed cells 等待 (a)/(b)。

腿 L 无 GF 依赖（锚定轴注册口径本身）→ 先行开跑不等任何裁定。

## §3 方法学（跑前写死）

- **6 员**=`firm/traders/` 全册（COMPOSITE-CE-01/02、VOLATILITY-CE-01、ENGULF-CE-01、NEEDLE-DE-01、DROUGHT-CE-01）；entry 经 `live.paper.SIGNAL_BUILDERS` 复现，exit 经 `ExitPatch(exit_overrides)` 运行时补丁，桥接 kwargs 照注册件（P-5 范式逐字）。
- **实战规则**：信号全史因果算子（只用过去收盘，`_selftest_causality` 同款保证），起点前数据仅 warmup；`run_backtest._injected` 只重索引窗口日期（J16 三重防未来数据）。每起点跑至最长完备窗，三窗切片 **{6m=126, 12m=252, 24m=504}**（P-5 12m+P-5B 6m 先例扩展）；起点资格=起点≥腿 floor（D:2013-06-17/L:2020-01-02）+252td warmup（D:全缓存历/L:2020+ 切片）+窗完整（起点+W ≤ 末日）。
- **成本**：V1 legacy 口径（T+1、佣金 13bp 全套费率+滑点，注册锚定复现口径）主面；**cost×2 并行面**（费率×2 同构重跑）。
- **被动基准**：同窗 EW buy&hold 起点日已上市成员（`mean_i(p_i,t/p_i,s)`，P-5 逐字），单面（成本对被动为一次性买入，×2 面不重复计）。
- **MIN_LISTED=24 敏感面**：主网格不设门（CEO 全网格口径+该门在 P-5/P-5B 从未实际 bind——2020+ 轴 listed 恒 45-48，属潜伏规则），成员数分层 {thin 5-23 / mid 24-47 / full 48} 逐格披露 + MIN_LISTED=24 子集独立判定列（P-5/P-5B 口径连续性）。
- **政体分段**：`regime_calibration` v3 原语 import-replay 同公式分腿计算；报告映射 GREEN=牛/YELLOW=震荡/ORANGE+RED=熊；腿 D 2013-2019 段=公式延伸（校准证据窗 2020+，延伸段标 `formula_extension` 如实披露）。
- **null 对照**：无随机信号 null（零新函数入批；海量起点本身=重抽样分布检验；被动线=对照基线）。**seed=N/A（确定性全网格，无抽样）——SEED_REGISTRY 零触碰**。
- **账本**：`science_gates.append_ledger("P5C_VIRTUAL_TIMEPOINT", <实跑格数>, "p5c_virtual_timepoint.json", evidence_cutoff="2026-09-22")`；prev=3077（引擎链头 regime_calibration_v3）。

## §4 判据（跑前写死，禁看结果调线）

- **主判 per (员×窗×腿)**：PASS iff `beat_rate ≥ 0.70` **且** `min_dd ≥ −0.35`（P-5/P-5B 逐字冻结口径）。二值判定，跑后禁调。
- **cost×2 面**：同线独立判定列（并行面，按令「成本 ×2 面并行」——不发明合取，双 verdict 并列披露）。
- **政体分段**=分报非分判：段级 beat_rate/dd/D7 全披露；牛/震荡/熊映射见 §3。
- **D7 四必报 per 判定格**：OOS 笔数（判定起点池化）/覆盖年数（首末合格起点跨距）/独立政体窗数（连续同态段计数）/CI 宽度（beat_rate 的 Wilson 95% 全宽）。相邻起点 1td → 窗重叠 (W−1)/W，有效样本 ≪ n，读数按此折价（P-5 §4 同款披露）。
- G1'/G2 v2 不适用（在册员复检非新注册）；全部面格如实入多重检验账本（扩容即买单）；预测对账与 gate_attrition 见 §8。

## §5 跑前预测（写死，≥3 条）

1. 腿 L 全网格 pooled beat_rate_6m ∈ [0.55, 0.68]（P-5 0.6467/P-5B 0.6067 邻域一致性）；6 员 6m 全 FAIL 0.70 线概率 ≥60%。
2. 腿 D 全网格 pooled 低于腿 L（2015 股灾/2016-18 段加入，高 β composite 更伤），6m pooled ∈ [0.45, 0.62]；**方向**：VOLATILITY 腿D−腿L >0（熊段防守增益）而 COMPOSITE 双员 <0。
3. 窗族：COMPOSITE 12m ≥ 6m（P-5 实证方向延续）、24m 续升；VOLATILITY 窗越长越弱（现金拖累）。
4. cost×2 面全员 ≤ 标准面（费率×2 单调损），幅度 ≤3pp（员皆 ×2 注册存活者）。
5. VOLATILITY 熊段 beat > 牛段 beat（反向于 composite）。
6. 薄池段（2013-2017）beat 方差大于全池段、中位不低于全池段（被动同薄池对照自归一）——不确定带宽大。

## §6 产物

- `scripts/p5c_virtual_timepoint.py`（分片/checkpoint/selftest 子命令；parallel_runner 范式 P-5B §7.3）
- `results/shortline/p5c_virtual_timepoint.json`（顶层 evidence_cutoff=2026-09-22 + `science_gates.cutoff_meta` + audit 段 + 判定汇总 + D7 + 政体段 + 分支 admission + 网格普查引用）
- `research/shortline/p5c_virtual_timepoint_results.csv`（逐起点行：leg/trader/face/start/window/ret/dd/n_trades/passive/beat/events_n/regime_state/segment）
- 本文件 §7/§8 回填；`results/gate_attrition.json` 追加一行。

## §7 跑后实证（跑前必须为空——写数字即造假）

（占位）

## §8 批后复盘（必填 s7-T）

- 预测对账（对/部分/错）+ gate_attrition 追加 + skill_line_v2 当批读数=N/A 披露（无新注册）；
- 回执入轮报告+CODELY.md 行级追加；判负=诚实收线（注册件注记区 P-5B §5 范式，level/paper 数据零触碰，纸盘通道不变）；禁调判据/禁重跑/禁以本检结果调参。

—— bm-b 循环轮 r105 · dept:研究+数据 · 2026-09-24 16:1x 写死（跑前冻结，commit 即锁）
