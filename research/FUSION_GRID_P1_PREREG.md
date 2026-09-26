# FUSION_GRID_P1 预注册 · T-85 s2/s3 融合网格 judged 批（O-20260926-2320）

> 冻结律：本件 commit 即冻结（R99）——冻结后禁改判据禁重跑；跑后只许回填 §7/§8。
> 权威链：research/BACKTEST_SCIENCE.md（v2 判据）＋ BACKTEST_PLAN.md 三铁律 ＋ research/COMPUTE_AUDIT.md（批件纪律）。
> 探针事实面（已冻结）：results/fusion_grid_probe.json（R295 bm-a）——探针仅触碰成员/政体面，零判格值（冻结先行律）。

## §0 批件身份【跑前】

- **批名/批号**：FUSION_GRID_P1；judged cells = **5 权重族 × 9 成员子集 = 45 格**；nulls K=2000（同掩码随机组合）；账单 N = 45 + 2000 = **2045**（每格计入 N_eff）。
- **认领（F-04 先行）**：fleet/inbox/MSG-20260927-0515-bm-a-T85-FUSION-GRID-P1.md；任务板引用 = T-2026-09-26-85 s2/s3（immediate CEO 票·O-20260926-2320·bm-a R277 认领在册）。
- **部门归属**：dept:策略＋研究（票面 joint owner）；执行机=bm-a（车道锁科学面；池分片法=任意健康机可烧）。
- **算力预算**：判格面 numpy 矩阵乘（45 格 × ~66 再平衡点 × 1379 bars）+ 2000 nulls 同构 ≈ 单核 <90s、4 workers <30s（O-2100 5min 阈内可轮内收口；>10min 批必须后台化的约束不触发，仍按池法入 runnable_pool 带 workers_plan=4·BelowNormal——24h 满载令供给线常规载体）。批报告必带 audit 段（workers/elapsed/ledger 读数）。

## §1 α 机制段【D6】

- [x] **结构性**：融合层不引入新信号——成员 NAV 均为已判定在册面（s1 收割 64 行·锚门全过）。本批 α 主张=**组合结构性溢价**：低相关成员流（全史中位置对 corr=0.1534）的组合使单位风险收益在无新信息下抬升（Markowitz 面），代价付出方=组合内成员间的方差互抵（rebalancing premium），非市场对手盘新付；judged 面=**构型是否胜过随机构型**（null 校准线裁决），非新 α 来源宣称。诚实注记：若判负=「构型无增量」而非「成员 α 不存在」。

**同族相关性准入检查【D6】**：
- 本批**零新信号函数入批**（成员=既有在册面，NAV 级组合；成员自身的 D6 已在其原批过门）。
- 批内结构性相关**如实披露**：同子集跨权重族格间相关必然高（构型同源）——这是 N_eff 计费面（45 格全计），非准入面；准入拒绝线不适用于机械网格（无数据驱动准入）。
- 成员冗余治理=DEDUP 子集面（trailing-252 |corr|≥0.95 塌缩，代表=trailing Sharpe 高者；全史静态普查 12 对 ≥0.95、塌缩后 20 员，探针 F2）。
- **幸存者报告去重（T-84 s3 律）**：报告面任意两格日收益 |corr|≥0.999 → 塌缩一格（sha256 持仓指纹+诚实 dedup 披露，禁转译收敛叙事）。
- 全史 x1 成员 pairwise corr：median 0.1534 / p95 0.6374 / max 0.9998（PROS-OVB-01 vs PROS-OVB-CE-01）；≥0.70 对=19/496。

## §2 数据与面板【跑前探针事实】

- **成员池**：FUSION-P1-NAV s1 冻结产物 results/fusion_p1/navs.jsonl（manifest sha 双门、anchor_all_ok=true）——32 面 = CE6 + PROSPECT22 + OVERLAY_WIRED4；x1 判格面 + x2 成本压测平行道（32 行在位）。
- **公共栅格**：28 基面 1631 bars（2020-01-02..2026-09-22）；overlay 自报基延至 09-24（r251）→ **截断至公共栅格**（多 2 bars 丢弃，如实披露）。
- **evidence_cutoff（前向锁盒 D2）**：**2026-09-22**（成员 caliber r256 A1 钉死律——s1 NAV 即不含 09-22 后 bars；面板 09-24 可得性照票面披露，锁盒以成员冻结面为准）；cutoff 后新 bar 不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`。
- **政体重算面**：510300+core48 日线面板（in-repo）；state 序列 = market_regime.py **v3 语义逐日因果重算**（RED=crash10d≤−12%|panic1d≤−5%；ORANGE=≥2 同日维（crash10d∈(−12%,−8%] | vol20>3y-p95(基窗排除当日) | breadth≥0.80 且 5d 斜率<0）——**below_ma200 v3 已解收集不读**；单维 ORANGE 日落 YELLOW；YELLOW=crash10d≤−5%|vol20>p80|breadth≥0.65|FOMC|R-配3 major bear；upgrade 即时/downgrade 需连续 2 GREEN 信号日）；bear 输入=firm.risk.regime.major_bear_state 截断序列逐日因果调用（MA250 双条件原文复用零重写）；FOMC 面=仅 2026 冻结日历（2020-2025 FOMC 日不建模如实披露——YELLOW 影响有界）；event_pre_holiday=live-unknowable 恒 None。runner 自检义务=逐日重算 vs 模块原函数抽样等价（≥20 随机日+末日 vs probe() dims）。
- **数据完备门（不过门禁跑批）**：navs.jsonl 64 行（x1/x2 各 32）；x1 32 面公共栅格 1631 bars 零缺；anchor_all_ok=true；510300 面板 ≥2026-09-22；core48 每 symbol ≥20 bars 自 2020-01；政体序列 1631 日全覆盖。
- 探针 F4 政体全史份额（近似面·runner 以精确复刻为准）：ORANGE 715 / GREEN 534 / RED 283 / YELLOW 99（1631 日）。

## §3 方法学【冻结】

- **格构造（因果律）**：warmup=前 252 bars 持现金（零收益，诚实披露）；再平衡点=自 bar 252 起每 21 bars（~66 点）；权重用 ≤ t−1 数据；再平衡间权重自然漂移（禁日度再平衡）；权重和=1（REGIME_COND 族=Σw=cap、现金腿零收益）。
- **子集（每再平衡点因果重算）**：
  - ALL-32：全员；
  - DEDUP：trailing-252 |corr|≥0.95 单链聚簇塌缩，代表=trailing-252 Sharpe 最高（并列取成员名字典序）——动态面，员数随时点披露；
  - TOP-K（K=2..8）：DEDUP 池内按 trailing-252 Sharpe 取前 K。
  - trailing Sharpe = mean(r)/std(r)×√252（trailing 252 bars，std=0 员剔除该时点）。
- **权重族（5）**：
  1. **EW**：子集内等权；
  2. **INV_VOL**：1/trailing-252 vol，归一；
  3. **INV_MDD**：1/max(trailing-252 MDD, 0.05)，归一（5% 地板防零回撤权重爆炸——工程冻结披露）；
  4. **CORR_CLUSTER_RP**：trailing-252 corr 单链 |ρ|≥0.70 聚簇；跨簇等权；簇内 inverse trailing-252 vol；单例簇=跨权一份（工程冻结配方）；
  5. **REGIME_COND**：EW × cap 阶梯 {GREEN 0.80, YELLOW 0.65, ORANGE 0.50, RED 0.20}（state 用 t−1 日值；**YELLOW 0.65=工程冻结插值非 L5 正典**（正典仅 RED20/ORANGE50/GREEN80）如实披露；满热 95% 不入本族=v3 状态机无满热态）。
- **null 对照（三铁律）**：K=2000 同掩码随机组合——每 null 每 25 再平衡点重抽：子集尺寸 K* ~ 网格结构镜像（p=7/9 uniform{2..8}；p=1/9 取当点 DEDUP 员数；p=2/9 全 32）；成员=32 池内无放回均匀抽 K*；权重=Dirichlet(1,..,1) 单形均匀；rng 流=np.random.default_rng([20275200, k, j])（null k·再平衡 j 确定性流）；null 全史 Sharpe → **批自有 null_pool**（coverage mu/sigma/n=2000）入 skill_line_v2（P4_EXT_TILT 附加面）。seed 基 **fusion_grid_p1=20275200** 于本件冻结 commit 同步登记 SEED_REGISTRY（R250 一步律；撞号扫描 2026-09-27 05:1x 代码/正典面零命中，data/*.csv 数字巧合除外）。
- **被动基线**：共享库 EW48 passive（pool="core48"）；**双基准披露面**：EW48 + B_MAXDIV（benchmark-only，T-27 否决窗至 10-01 零接线，只读取数）+ 510300 买入持有——描述性披露，不构成额外判线。
- **成本口径**：成员 NAV 已内嵌成员级成本（s1 引擎口径）——**融合层成本=0（结构性披露：FoF 层再配置摩擦未建模，为批局限；成本敏感性由 x2 成员压测面部分覆盖）**；判格面=x1，x2=压测描述面（逐格 x2 Sharpe 与退化幅度披露）。
- **账本**：跑批时 `science_gates.append_ledger("FUSION_GRID_P1", 2045, file_name=..., evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev；确定性重执行=产物字节恒等+r253 单计律+n_eff_override=自身链位）。

## §4 判据【跑前写死】

- **G1' v2** = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=45, pool="core48", n_trades, n_entries, null_pool=<批自有 2000 nulls coverage>)`：全期 Sharpe > skill_line_v2（=max(passive+0.10, μ_null+σ_null·√(2·ln N_eff))）**且**平稳 bootstrap CI 下界>0 **且** entries≥30；批报告逐列披露 skill_line/CI/trade_gate 全输入。
  - **F6 双口径（融合层继承面）**：cell n_entries = Σ_m n_trades_m × (持有期数_m / 总期数)（成员持有份额加权——成员在格内驻留越久计入其交易证据越多；冻结公式如实披露）；n_trades 同式。成员交易证据来自 s1 行内 n_trades 字段。
  - **n_eff_override**（r259 前回声防漂移）= 跑时账本 prev_total + 2045（单计律：重跑字节恒等）。
- **G2 注册资格** = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑，禁 dsr_from_stats 充数）**且** 家族 PBO≤0.25（screening/pbo.py CSCV 8 块·同族网格=45 格收益矩阵）；缺输入=诚实拒收。
- **描述性条款（批级披露，不替代 v2 门）**：年化>0；**OOS 双正**：OOS 窗=格窗末 504 bars（~2 年），OOS Sharpe>0 且 OOS 年化>0；maxDD≥−35%；x2 压测面退化逐年披露；无崩年（逐年收益无 ≤−50% 年）。
- **分段/滚动统计面（s2 票面义务）**：全史+rolling 6m/12m/24m（126/252/504 bars 滚动 Sharpe min/median）+bear/bull/chop 分段（510300 trailing-252 收益：≥+10% bull / ≤−10% bear / 其余 chop；分段 Sharpe/年化/maxDD 全披露）。
- **硬界三件套**：本批非数据腐坏/健康检测类判线（NAV 线性组合无健康检测线）——三件套不适用，如实披露；§5 P5 仍给极端日先验（三件套 (c) 面义务不豁免）。
- **幸存者后续**（s4 面，本批不执行）：过 G2 者 → STRATEGY_LIBRARY 入册候选+FUSION-* 纸盘账户族提案（prereg only；激活=GM 署名+7 天否决窗 per T-27 先例）；报告面 dedup 塌缩律（§1）。

## §5 跑前预测【写死于跑前，≥3 条】

1. **EW-ALL32 全史 Sharpe ∈ [0.7, 1.1]**：成员均值 Sharpe 0.424 × √(32/(1+31×0.1534)) ≈ 0.424×2.36 ≈ 1.0（对/部分/错以落带为准）。
2. **skill line（N_eff≈2045·批自有 null 校准）≥1.4** → 多数/全部判格不过 G1'=**诚实判负为大概率结局**；唯一可能贴线族=ALL/DEDUP 大子集 × 分散权重族（EW/INV_VOL/CORR_CLUSTER_RP）——判负照报，slot 关闭注记，不开翻案。
3. **REGIME_COND bear 分段 maxDD 较其同子集 EW 对手改善 ≥5pp**（cap 阶梯在 ORANGE+RED 61% 日历份额压缩敞口）。
4. **TOP-K 小 K（2-4）格较 ALL 格：波动更高、maxDD 更深**（集中度风险；trailing 选择按构造劣于全知——诚实结构性劣势）。
5. **极端日先验（三件套 (c)）**：成员 NAV 携 2024-02-28 微盘崩（DCC 面 754 员）与 2024-09-30 政策脉冲（TWS 256 员）当值标记——融合层线性组合不放大单日极值；RED 态 283 日 cap≤0.20 压缩深回放日敞口；无新增 max 硬界面（非检测批披露）。

## §6 产物

- runner：`scripts/fusion_grid_p1.py`（冻结后建造；selftest 子命令=离线自检含政体逐日等价抽样门+合成成员构造性测试+null 确定性重放门）；
- 结果：`results/fusion_grid_p1/p1_results.json`（顶层 `evidence_cutoff` + `science_gates.cutoff_meta` 合并块；45 格×5 统计面全列；audit 段 workers/elapsed/ledger）+ `cells/`（逐格明细）+ `nulls_summary.json`（coverage mu/sigma/n）+ `regime_series.json`（1631 日 state 序列+触发摘要）+ x2 压测面行；
- 账本：append_ledger 单计一行；`results/gate_attrition.json` 追加一行（§8 时点）；
- 本件 §7 回填。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿 2026-09-27 R298 bm-a。**执行链留痕**：R296 runner 95f4e95d → 首 burn 05:50:01 autofill pid 20952 于首 cell job 即崩（KeyError st['sharpe_full']·cell_descriptive 未存全窗 Sharpe·零判格产物）→ 工程修复 64023a42（按冻结 §4 G1' 全窗 Sharpe 面补键+B7b 消费键契约腿·selftest 23/23·R297）→ 复飞 06:10:01 autofill pid 18524 新 sha 0cce319299acf467≠崩溃 sha 3b49bab9bb036efd（O-0947 sha 变更清熔断律）→ 落地 06:10:37·elapsed 28.8s·workers 4·`results/fusion_grid_p1/p1_results.json`；fill latency 29.9min > O-2100 10min 目标=miss 如实记（崩诊轮占用窗口）；修 bug 合法重执行≠结果重跑。**判读**：**0/45 G1' 判负照报**——skill line（own-null 校准）**1.7825**（n_eff 202,441·passive term 0.4792·null term 主导：μ_null 0.4209/σ_null 0.2754）vs 最佳格 EW__DEDUP **0.5301**（bootstrap CI [−0.3299, 1.392] 下界≤0 ∧ line_ok=False）；族面排序 EW 0.5301/0.5237（ALL32）> INV_MDD 0.5060 > CORR_CLUSTER_RP 0.4770 > REGIME_COND 0.4130 > INV_VOL 0.3925；TOP2 全族 ≤0.12（集中度面）；DSR 最佳 0.0（sr_star 1.2511@n_trials 202,441·T 1379·skew 0.590/kurt 11.98）；family PBO 0.4857>0.25；**G2 0/45 eligible**。**随机本底披露**：K=2000 同掩码随机构型 Sharpe μ 0.4209/σ 0.2754——32 员 NAV 面的随机构型本底即 ~0.42±0.28，判负语义=**网格构型不优于随机构型（结构无增量）**，非成员 α 不存在（§1 预埋注记）；μ_null>EW48 passive 0.3792=再平衡漂移面本身有收益本底。**描述面（全过·不构成判线）**：45/45 OOS 双正（最佳格 OOS Sharpe 1.4588/年化 5.86%）·45/45 maxDD≥−35% 线过（最深 TOP2 −12.77%·最浅 INV_VOL__ALL32 −5.15%）·0 崩年。**x2 成本压测面**：45 格全数 x2 Sharpe ≤0.0454（最佳 EW__DEDUP +0.0454·退化 −0.4847；最差 REGIME_COND__TOP2 −0.2396）——成员级压测残差主导融合层，x2 面无一生还如实披露。**政体精算面**：GREEN754/YELLOW714/RED141/ORANGE22（1631 日·R296 真数据门零漂移）——§2 F4 近似面（ORANGE 715/GREEN 534/RED 283/YELLOW 99）按其自注「runner 以精确复刻为准」被精算面接管。**dedup 面（T-84 s3 律）**：45×45=990 对中 ≥0.999 共 6 对（跨族同子集 TOP-K 机械孪生·max 0.9997）——幸存者报告面=0 员故零塌缩执行，未来幸存者报告必须先塌缩再入册。**基准描述面**：B_MAXDIV 格窗 Sharpe 0.8298>全部 45 格；510300 买入持有 −0.0933。**ledger**：200,396+2,045=202,441 单计 ✓（r253·n_eff_override=prev+2045 自身链位）。）

## §8 批后复盘【s7-T·跑后回填】

（2026-09-27 R298 定稿。**§5 五预测对账**：①「EW-ALL32 ∈ [0.7,1.1]」→ **落带外 MISS**（实 0.5237）：√(N/(1+ρ̄(N−1))) 分散算术高估——以 median corr 0.1534 代入 ρ̄ 忽略了高尾相关对（19 对 ≥0.70·max 0.9998）与成员 Sharpe 离散面，实得组合 Sharpe 折半；②「skill line ≥1.4→多数/全部判负」→ **命中**（线 1.7825·0/45）；③「REGIME_COND bear maxDD 较同子集 EW 改善 ≥5pp」→ **量级 MISS 方向对**（+1.71pp ALL32/+1.54pp DEDUP）：预测前提面=近似政体份额「ORANGE+RED 61% 压敞口」被 v3 精算面证伪——精算 ORANGE 仅 22 日、ORANGE+RED=163/1631=10%，cap 压缩作用日历份额缩 6 倍，结构性改善量随之下缩；④「TOP-K 小 K 波动更高/DD 更深」→ **命中**（EW TOP2 −12.77% vs ALL32 −7.82%·全族 TOP2 Sharpe ≤0.12）；⑤「极端日先验（组合不放大单日极值·RED cap 压缩）」→ 无矛盾实证（0 崩年·maxDD 面如上·非检测批无新 max 硬界面）。**教训入律候选（S4 记忆面）**：§5 预测若锚「近似探针面+runner-exact 准」条款，冻结窗内零成本可精算的面（本例 module recompute 0.3s）应**先精算再写预测**——P③ 整条被前提面证伪即此坑；P① 分散算术用 median corr 代入 ρ̄ 属模型面误设。**判线读数**：own-null 校准线 1.7825 高企=随机构型本底高（成员 NAV 面本身携带 ~0.42 Sharpe 本底），G1' 判负=**融合网格构型面（5 权重族×9 子集·32 成员 NAV·本构型域）判负关槽**，判负不重开律生效：新证据=新预注册（换成员池/换权重族/加新机制主张须另立 prereg 禁本批翻案）。**s4 幸存者后续面**：0 过线员→零 STRATEGY_LIBRARY 入册·零 FUSION-* 纸盘提案·提案面自然闭合。**gate_attrition**：own 行在册（entries 列表面·r248 律）。**回执面**：T-85 s2/s3 全链闭环 R99 序合规（freeze 7cf87f13 R295→runner 95f4e95d R296→burn 崩+修 64023a42 R297→复飞落地 06:10 R298→本收割）；post_review criteria 注册同轮（判据锚 §7/§8 稳定产物件·D-20260927-04 锚律）；24h 满载令供给线载体=本批已 discharge，池面移交下一供给批。）
