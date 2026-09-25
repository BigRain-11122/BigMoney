# OPTIONS_WAVE2 — 波-2 期权备兑族批预注册（跑前冻结）

> 按 research/PREREG_TEMPLATE.md 起草。**本件 commit 即冻结**；跑后只许回填 §7/§8，禁改判据禁重跑。
> CEO 授权链：O-20260925-1158（全品种回溯验证令）→ T-2026-09-25-65-P1 s1（census §六波-2 定稿：行权价审计门后开）→ T-65 s3 审计 PASS（results/option_s3_audit.json 六绿）→ 票 T-2026-09-25-67-P1（immediate·claimed_by bm-a R190 21:47:25，CEO 即时律同轮认领同轮开动）。
> 反重复：仓内首期权批（rg option 扫描 engine/ scripts/ 零既有期权实现；OPTIONS_WAVE2_PREREG.md/engine options_runner 均新建）。
> 数据债锚：s3 retention_boundary 冻结披露——sina codes 面只留近期过期月（202606 深过期/202608 从未挂牌双空载崩壳实证），期权链历史重建窗=保留窗。

## §0 批件身份【跑前冻结】

- 批名：OPTIONS_WAVE2（波-2 期权备兑族 pilot 批·T-67）。
- **批内格数=70**：候选 18（3 族×3 moneyness 档×2 滚仓制式）＋随机 null K=50＋被动基线 2。每格计入 N_eff（扩容即买单）。
- 认领：票 T-2026-09-25-67-P1（claimed_by=bm-a R190，同轮开动）；F-04 先行=MSG 本轮入 fleet/inbox/（波-2 批窗声明，与 bm-b WAVE-3A 债券车道零重叠）。
- 部门归属：**dept:研究+数据**（族研究与判据=研究部；期权三面数据腿=数据部）。
- 合法性链：O-1620 GM 署名下放 + O-1158 品种扩容 CEO 令（期权=新器械域 P1 门槛由 CEO 令兑现，票面在册）。
- 算力预算：面板 ~124 交易日 × 70 格 → **<60s 单进程**（CTA_WAVE1 78 格×4561 日 64.6s 先例的 1/37 载荷），无需池化；P0 面板构建腿=网络枚举拉取（~30-70 合同×0.3-0.5s，<2min）实现切片内联合法。批报告必带 audit 段（无 audit 段不入账本）。

## §1 α 机制段【D6】

- [x] **风险溢价（CC/CSP 主）**：**波动率风险溢价（VRP）**——ETF 期权隐含波动率系统性高于事后实现波动率，期权卖方收取方差保险费；代价支付方=期权买方（崩溃恐惧的认沽买方付出尾部保护保费＋彩票偏好的认购买方付出凸性溢价）。CC/CSP=VRP 收取方（卖权利金收 carry）。
- [x] **结构性（PP 注记·非独立 α 主张）**：PP=保险成本基准腿——保费-赔付不对称由买方保护需求支付；**其 Sharpe 主张如实预测为负**（保费纯损耗），科学产出=每权利金单位的尾部减损效率面（dd/vol 缩减披露），G1' 判据面如实预测不过。
- **同族相关性准入【跑后必填】**：批内 18 候选 pairwise 全披露（CTA_WAVE1 先例）；在册 6 员（core48 ETF 域）corr 仅对 passer 计算。跑前预注：CC↔CSP 同为 VRP 收取方同滚仓制式 → 同 m 档孪生 corr 预期 ≥0.7 带（设计孪生如实，CTA LegB 帽孪生 0.98 先例）；PP 与 CC/CSP 方向相反（买保险 vs 卖保险）预期负相关；备兑腿含 underlying 多腿 → 与在册 ETF 多头员 corr 预期 0.3-0.7 带；`max|corr|≥0.7` 拒收律照跑。

## §2 数据与面板【跑前探针事实·s0 census + s3 audit·results/option_s3_audit.json】

- 宇宙：2 标的＝**510050（上证50ETF）＋510300（沪深300ETF）**。期权合同域三面（s0/s3 已验）：codes(月×标的→合同码集)＋per-contract daily OHLCV（列=日期/开盘/最高/最低/收盘/成交量）＋expire(月×标的→到期日+剩余天数)；行权价面=合约代码内嵌解析（510050C2610M02750→2.750）×board 链级面×greeks 面三源交叉验 **100% 合**（s3 G2）。
- **保留窗数据债（票面要求冻结披露项）**：sina codes 面只留近期过期月——近过期月（202609·过期 2 日）可枚举 14 call 合同＋单合同全生命周期日线 127 行（2026-03-24→2026-09-23 实测）；挂牌月 {202610, 202612, 202703} board 22-28 行/月在册。**历史链重建窗=保留窗**（深过期月双空载崩壳实证）。
- **回填 vs 前向决策（冻结）**：本批＝**保留窗回填 pilot**；**前向采集道=wave-2b 数据腿另开票**（update_options.py 日增量采集器建立真史，近月标准滚仓 definitive 批在前向史 ≥12 月循环后另开预注册——本批窗薄如实披露，pilot 判负不立终判）。
- **合同选择规则（保留窗强制设计·冻结）**：选日 T 在「日线面已有 ≤T 行的存活合同集」（上市日=合同日线首行代理——防幸存者/梯子可用性偏，s0 新上市合同 7 行自然短史注记）中取**可枚举最近到期月族**、按 moneyness 规则选 strike。**数据面强制 tenure 1-6 个月非设计选择**（2026-03→08 近月族 202604-202608 已不可枚举=最近可得=202609 远月族）：远月低 gamma/theta 保费结构如实披露；标准近月滚仓=wave-2b definitive 批专属，本批不做近月重构宣称。
- **evidence_cutoff=2026-09-24**（最后完整 bar 日；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-24")`）。
- **数据完备门（P0 面板构建腿跑、不过禁跑批）**：①两标的×全可枚举月（过期 {202609}∪挂牌 {202610,202612,202703}）×call+put 合同集在位（每合同日线行数≥1，head/tail repr 落 audit 段）；②逐合同首行日期（上市日代理）披露+选日可用性由日线面判定；③510050/510300 underlying 日线（data/daily）与期权日历对齐（SSE 同交易日历，缺口 0 容差）；④权利金 close>0 卫生全行；⑤逐月 strike 阶梯连续性=代码解析 100% 合（s3 G1/G2 判据复用）。**put 腿若 P0 枚举空载**（s3 仅验 call 侧）→PP/CSP 相应格诚实 FAIL 记录零替身。
- 面板规模预注：~30-70 合同×~30-127 行/合同 ≈ 2,000-5,000 行级（P0 实测定盘）；**span 自适应裁定（冻结）**：P0 实测 span <90 交易日 → weekly 制式 entries≥30 结构性不可达 → 批降级 descriptive-only 零注册主张如实披露。

## §3 方法学【跑前冻结】

- **信号族（3×3×2=18 候选格·冻结参数）**：
  1. `covered_call`（CC 备兑开仓）：持有 underlying 满仓份额（权利腿全额覆盖），卖 §2 规则选定月族 OTM call，strike=argmin{|K/S−1−m|}（最近上市档），m∈{0.03, 0.05, 0.10}；
  2. `protective_put`（PP 保护认沽）：持有 underlying＋买同规则 OTM put，m 同三档；
  3. `cash_secured_put`（CSP 现金担保卖权）：全现金 sleeve，卖 OTM put（现金担保=strike×unit/张全额冻结），m 同三档。
  - 滚仓制式 2 档：`weekly`（每周首交易日滚仓，**判据制式**——pilot 窗内可达 ~50 entries/格）＋`monthly`（月末/到期滚仓，**描述性信息列**——窗内 ~6 entries/格，F6 结构性 FAIL 预测冻结于 §5）。
- 执行语义（daily T+1 引擎域）：T 信号/选价 → T+1 开盘建仓（OHLCV 面开盘价）；盯市=日收盘（结算代理面）；到期=expire 面合同月到期日按当日收盘现金结算近似（ETF 期权实物交割→以到期日 underlying 收盘近似交割腿=代理近似披露；pilot 窗内到期仅 202609 一族）；涨跌停近似=开盘触昨结±标的限幅不开新仓（平仓恒允许）。
- 手数与规模：¥1,000,000/sleeve；CC/PP lots=floor(equity/(spot×unit))；CSP lots=floor(cash/(strike×unit))。
- **器械常数（provisional·G2 交易所核验门前置·CTA TS tick 先例）**：unit=10_000（合约单位·张）/fee_lot=6.6 元/张/边（经手 1.3＋结算 0.3＋佣金 5.0 provisional）/tick=0.0001 元。G2 门=对照交易所/结算官方费率页核验（R169 律：核验页 URL 从父页 href 实读禁盲猜），偏差>30% → 冻结核验值＋披露。
- 成本口径：期权腿 per-lot 固定费＋滑点=**max(2 ticks, 0.05×premium)/边**（OTM 宽价差保守 provisional 冻结）＋ETF 腿=V2（ADV20 三层滑点+1%ADV 帽，knowledge/rules.py 既有面）；**×2/×3 成本压测信息列照跑**（保费收取族=成本敏感性主检验点）。
- null 对照：K=50 同面板随机信号（每周随机三态 {CC,PP,off} 同持有分布同滚仓制式同合同选择规则），**seed=SEED_REGISTRY["options_wave2"]=63_000（63_000+k, k<50；全仓 rg 扫描 2026-09-25 22:0x 空闲——命中=数据文件 float/sha256 巧合非 RNG，t34/wild_route 先例披露；登记后跑）**；同 seed 双跑逐位确定性=硬门。
- 被动基线 2：`passive_buy_hold_510050`＋`passive_buy_hold_510300`（underlying 满仓 buy-hold；skill_line 被动项=本批自有，禁跨域套用 core48/期货线）。
- 引擎载体：engine/options_runner.py **新建加性**（futures_runner/ETF 引擎零触碰；R99=本件冻结前零引擎改动）；scripts/options_wave2.py（gates/run/selftest 三态子命令；P0 面板构建内嵌 gates 子命令）。
- 账本：`science_gates.append_ledger("options_wave2", 70, "results/options_wave2.json", evidence_cutoff="2026-09-24")`（dict schema 单源，禁手抄 prev）。

## §4 判据【跑前写死】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=70, pool="options_wave2", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据驱动=max(本批被动 strict-max+0.10, μ_null+σ_null·√(2·ln N_eff))）**且**平稳 bootstrap CI 下界>0**且 entries≥30（F6 双口径 (entries_ok) 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线**且** DSR≥0.95（原始收益 deflated_sharpe_ratio）**且**家族 PBO≤0.25（CSCV 8 块；族=3 family 各自 6 格 m×制式网格）。
- 描述性条款（批级披露）：年化>0；回撤≥−35%；无崩年；×2/×3 成本压测；**PP 腿保险效率面**（每 1% 保费→maxDD 缩减比）；CSP 现金腿占用披露。
- **硬界设计三件套（D-20260925-01①）**：(a) 数据健康门主责=**分布界**——逐合同日收益 |r1| 的 median/p99.9 全披露＋权利金 close>0 卫生＋strike 阶梯零缺；**期权单合同日收益天然厚尾，禁裸 max |r1| 作腐坏主判**；(b) max 硬界（单合同 |r1|>50%）须配**危机日感知条款**——命中先记危机日志＋豁免路径=单点单列披露优先于整批判负；(c) 极端日先验入 §5。
- 结果 JSON 顶层 `science_gates.cutoff_meta("2026-09-24")` 硬门（缺=science_audit C2 VIOLATION）。

## §5 跑前预测【写死，跑后对账】

1. **窗口环境**：2026-03→09 窗（~124 交易日）——50ETF strike 带 2.75-3.5/300ETF 4.1-6.0（s3 board 实测）；regime 面=ORANGE shadow（震荡）→ CC 上限截断损耗中低、PP 保费纯损耗概率高。
2. **CC weekly**：Sharpe 预测 **0.1-0.6**（保费正 carry−截断−成本；远月低 gamma 保费薄）；m=0.10 深虚值保费最薄→费后负风险。
3. **PP 全 m 档**：Sharpe 预测 **−0.8~−0.3**（保险成本腿如实判负预期）；CSP **0.0-0.4**（认沽价差宽＋现金腿 0 利拖累）。
4. **monthly 制式 9 格**：entries≈12<30 → F6 **结构性 FAIL**（冻结预测，信息列保留）。
5. **被动**：窗内两 ETF buy-hold 走势如实未知（跑时实测定盘）；预测 0.0-0.6 带。
6. **null 带**：σ_null 预测 **0.25-0.45**（窄窗+周频三态随机账本波动放大）；N_eff≈70 → null_term≈0.6-1.0；skill_line 预测 **0.7-1.1**。
7. **passer 预测 0-1**：窄窗统计力弱+monthly 结构 fail+PP 负带+成本压测深负风险；**批科学价值=首期权批测量器械落地（三面→面板→账本全链）＋保费会计面验证＋三族窗内证据，非注册预期**；pilot 判负不立终判（wave-2b 前向真史 definitive 批在册）。
8. **极端日先验（三件套(c)·窗内已知/可能形态）**：2026-09-23/24 权利金单日 −17%~−26% 跳（s3 board 面实测=标的 ~−1.4% 伴随 IV 压缩）；标的 |r1|≥3% 日（窗内如有）→ ATM 权利金 ±30-80%、深虚 ±100%+；命中=max 硬界豁免单列预案在册。

## §6 产物【跑前声明】

- scripts/options_wave2.py（gates/run/selftest；P0 面板枚举构建内嵌）＋engine/options_runner.py（新建加性）
- results/options_wave2.json（顶层 evidence_cutoff+audit 段+verdicts+null_pool+passives+prereg_sha256_at_run）
- research/options_wave2_results.csv（70 行全列）＋本件 §7 回填
- results/gate_attrition.json 追加一行；SEED_REGISTRY 登记 options_wave2=63_000（本轮随冻结落）
- wave-2b 前向采集道=另票注记（T-67 票面 next-slice 登记）

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

**（2026-09-25 22:58 跑后回填 · bm-a R194 收割轮 · 70 格全跑 · 结果件 results/options_wave2.json（evidence_cutoff 2026-09-24）· 禁改判据禁重跑（跑前 sha a6998921 已断言入结果件 meta）**

- **门禁 G0-G4 全绿**（批内重跑）：G0 smoke 25/25；G1 引擎自检 12 断言族（含本轮新增第 12 族=缺行日 roll 顺延生产形态夹具）；**G2 器械常数 4/4 腿全 verified**——CSDC 结算费腿本轮收口：官网收费标准列面 iframe 子页 `service_tlist/code_0.shtml`（非 AJAX 壳·R193 诊断修正）→《上海市场证券登记结算业务收费暨征税一览表》PDF 官方字面 **「ETF 期权交易：每张合约0.3 元」**（行权 0.6 元/张·卖开试点期暂免=保守方向披露；股票期权 0.45/0.9 元非本批范围披露）→fee_lot 分解 1.3+0.3+5.0=6.6 对账合；G3 面板完备（200 合同）；G4 null/被动同 seed 双跑逐位。
- **跑前两处引擎修复（诚实披露·判据零改动）**：①零成交缺行日崩溃修复——实弹 2026-03-10 roll_close 填充合同 10011005（153/160 行=6 个中段零成交日）NaN 开盘价 → `_opt_trade` 无 NaN 卫 → cash 污染 → 下周 exec `int(NaN)` 崩（首发即崩于第 9/18 格）；修=缺行日整 roll 顺延（无假价成交无孤儿腿）+盯市 close_mark=最后可观测收盘 ffill（修复缺行日期权腿从权益凭空消失的度量污染）；②PBO 腿结构性 NA——T=159 回报行 < CSCV 冻结最小 160（8 块×20·BACKTEST_SCIENCE §4），**阈值不动（判据红线）**，三族记 structurally_unavailable；`g2_registration_v2` 对 pbo=None 天然 fail-closed（missing_inputs 面）。
- **null 带（K=50·seed 63,000 链）**：μ **−2.4195** / σ **0.8205**（p95 −1.3793 / max −0.0193 / min −4.2307）；**skill_line v2 = 1.6196**（n_eff=183,100 账本统一链口径；null_term 1.6196 > 被动项 −0.2563）；被动 510050 **−0.6454** / 510300 **−0.3563**。
- **判定：G1 通过者 0/18（诚实判负·零注册主张）**。最优格（按 Sharpe 全量排序复验·R189 律）**covered_call_m10@monthly −0.2503** > CC_m3@monthly −0.2997 > CC_m5@monthly −0.3171；最差 PP_m10@weekly **−7.0970**；18 格全负+2 被动全负=**窗本身为回撤窗**（50ETF/300ETF 2026-01-29→09-24 buy-hold 判负），全族收费结构在回撤窗内无一胜过被动基线。
- **PP 保险效率面（描述性主产出）**：weekly 制式三档真保护成立——m10@weekly 每付 1% 保费换 maxDD 缩减 **751 bps**（dd_delta −0.2001 vs 裸混合）/ m5@weekly 675 bps / m3@weekly 561 bps；**monthly 制式反向**（三档全负效率 −162~−788 bps/prem%=8 次滚仓覆盖洞如实）。
- **CSP 现金腿**：max_open_lots 14-15（K×unit 抵押冻结如设计）；**D6 批内 corr**：CC 六格互相关 0.994-0.997（设计孪生带命中预测·无 passer 无拒收动作）。
- **gate_attrition**：追加一行（cells_delta 70 / ledger_total_after 183,100 / eliminated 18 / g1_passers 0）。
- **pilot 判负不立终判**（§5.7 冻结）：保留窗回填批窗薄（160 交易日）+远月低 gamma 保费结构数据面强制——**wave-2b 前向采集道=definitive 路已在册**（T-2026-09-25-69 开票，近月标准滚仓 definitive 批=前向史 ≥12 月循环后另开预注册）。

## §8 批后复盘【必填·s7-T】

**（2026-09-25 23:0x · bm-a R194 同轮回填）**

- **§5 逐条对账**：①窗口环境 ORANGE 假设**过乐观**——实况=回撤窗（被动双负）；②CC weekly 预测 0.1-0.6 **MISS**（实况全负 −0.78~−1.32：回撤窗+远月薄保费+成本三重压制）；③PP 预测 −0.8~−0.3 **方向命中但深度 MISS**（实况 −1.35~−7.10：回撤放大保险腿损耗，但保险效率面主产出成立）；④CSP 预测 0.0-0.4 **MISS**（−0.68~−3.92）；⑤monthly 9 格 entries=8<30 F6 结构性 FAIL **命中**；⑥null σ 预测 0.25-0.45 **MISS**（实况 0.8205：三态周频随机账本在回撤窗方差放大——预测口径欠考虑回撤窗条件分布）；⑦passer 预测 0-1 **命中 0**；⑧极端日先验在册（权利金 −17%~−26% 跳=标的 −1.4%+IV 压缩，未触发 max 硬界豁免）。
- **损耗账**：gate_attrition 一行（18 候选全淘汰·零注册）；算力=55.0s 单机批内（<60s 预算内·零池分片需要）。
- **skill_line_v2 读数**：1.6196（null term 主导·被动项 −0.2563）；N_eff=183,100（含本批 70 格入账）。
- **无新员注册**→零 SIGNAL_BUILDERS 接线、零 smoke 锚定门复跑需求；期权测量器械三面（codes/daily/expiry→面板→账本全链）**落地即本批主科学产出**（§5.7 冻结口径）+保费会计面验证+PP 保险效率面首测（weekly 真保护/monthly 覆盖洞=前向批设计输入）。
- **回执**：本轮报告 R194+CODELY 行级+T-67 票面 next-slice 登记+wave-2b 开票 T-2026-09-25-69。

---

## 实现轮前置门（gate list，跑批前全过才许 run）

- G0：smoke 全绿
- G1：options_runner 自检＝合成面板确定性双跑逐位＋合同选择可用性滞后断言（T 选价 T+1 开盘，禁未来数据）＋手数/预算/到期结算单员断言
- G2：器械常数交易所核验门（unit/fee/tick provisional 对照官方页，>30% 偏差冻结核验值）
- G3：P0 数据完备门（§2 五条+span 自适应裁定）
- G4：null/被动确定性（同 seed 双跑逐位）
- G5：D6 同族 corr 披露（跑后）
- 审计段必带（compute_audit run 嵌批内）
