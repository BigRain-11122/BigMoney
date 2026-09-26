# CN_DIV_LOWVOL_ROT_PREREG — CN-DIV-LOWVOL-ROT 组合模型·s3 切片 2 预注册（跑前冻结）

> 令：O-20260926-0926（CEO「去调研国内市场的各个流派……建立起适合国内情况的组合模型」）· 票：T-2026-09-26-73（P1·immediate·bm-a）s3 第二模型切片（切片 1=CN-REVERSAL-TILT 已判负收线在案，互不挪用判据）。
> 跑前冻结：本文件 commit 先于任何跑批（R99 律）；跑后只许回填 §7/§8，禁改判据禁重跑；工程修复合法重执行≠结果重跑须双跑留痕。冻结时点=2026-09-26 R250（bm-a）。
> F-04 先行声明：fleet/inbox/MSG-20260926-1416-bm-a-claim-t73-s3-slice2-divlowvolrot.md（同轮 commit）。
> 切片选择依据（诚实面）：三剩余模型中本轮唯一全仓内确定性可开面——CORE-SATELLITE 卫星腿供给缺位（T-57 野路子 0/25 幸存诚实负）；REGIME-POLICY 政策轴 s2 研究未做（先研后建模律）；本模型器械域 GM 已批+corpus 在仓零网络。
>
> **R251 零跑修正（R246 前例·零结果零跑批窗内·修正先于任何跑批）**：①§2 T_joint **1861→1862**——探针引用件 `results/div_lowvol_rot_probe.json` 自身 `joint_bars=1862` 为权威数；错位日 2021-10-22 是 510880-only 日（512890 无该 bar），本就**不在交集内**，冻结稿「1862−1=1861」为双重扣减 off-by-one（runner 实算交集=1862 实证复核在案）；②错位日叙事修正：2021-10-22 **=512890 份额拆分停牌 bar**（`div_lowvol_probe.SPLIT_EVENTS['512890']` 单源机械证据：last_cum_close 1.639 → first_post_close 0.801·ratio 2.0449·factor 0.5·suspended_bars=['2021-10-22']），非「数据面缺口」——排除处理不变（该日不在交集时间线内）；③**事件守卫腿（r239 坑律族承袭）**：RS/收益/MA200 全部在 `DLP._adjust_split(512890 factor 0.5, 510880 None)` 事后价面上计算（家族 DIV_LOWVOL_P1 同源装载），raw 面在拆分日含 −51% 假跳空禁入信号面；ADV20=raw volume×close 滚动 20（CNY 口径跨拆分连续，volume 不调整=保守偏严承袭家族注记）；④corpus=价格面（分红除权不在 twins 内），双腿同红利族 RS 相对面较稳、绝对收益面同步低估如实注记。判据零改动（§3/§4 门线数值全部不动）。

## §0 批件身份【跑前】

- 批名：`CN-DIV-LOWVOL-ROT-P1`；判断格=**4 策略格**（{W63, W252} × {裸轮动, MA200 防御门}）+ K=50 nulls（成本压测不入 skill 格·J2 式披露）；per-cell N 计入 N_eff（54）。
- 部门归属：组合与资金部（装配/判决）+研究部（机制/信号）+工程部（runner）joint；dept 标注=组合与资金部。
- 算力预算：单遍 <5min CPU（2 腿×1862 bar 模拟+50 nulls+CSCV 全轻量·R251 修正①）；**仍按 O-1137 真实载体供给律池提交**（池 ready=0 持续饥饿面+R247 CN-REV 41s 批照池提交同例）；池条目带 checkpoint 幂等+audit 段（elapsed/worker/瞎跑白跑旗自检）。
- 三线三判律声明：本批=交易线（G1'/G2 门）；配置面四指标判据不挪用；ALLOC 线 corr 只作披露不互判。

## §1 α 机制段【D6——四选一】

- [x] **结构性（主选）**：两器械指数构造法则差异——上证红利（510880）=股息率加权 vs 中证红利低波（512890）=股息率×低波动双因子加权+波动率筛选——成分与权重机制不同→不同利率/风格政体下相对强弱有持续性；付费方=未跟随构造法则差异切换的风格持仓者（指数机械再平衡的结构性时滞面）。**分层诚实注记**：组合主收益由红利/红利低波风格溢价承载（风险溢价副选注记，非本批轮动增量主张）；若 bare 轮动格收益≈被动 EW pair 基线，则「轮动选择面零增量」结论照登（§5.7 预注）。
- **政体依赖诚实注记（家族前批 §2 批判入边界承袭）**：红利低波=利率政体函数（2014 利率拐点起点论）+银行权重集中 ~50% 拥挤批判——本批政体轴（§3.3 MA200 防御门）为构成件非可选件。
- **同族相关性准入【跑时必填·§7 回填】**：入批时对**在册交易员全员**（6 员）+同批 4 格函数逐对算 `max|corr|`（日收益口径），**≥0.7 → 拒收**。**H4 式增量披露（非 admission set·照登不拒收）**：①vs 家族前批 DIV_LOWVOL_P1 C1 x2 face（同器械域·已判负非在册——预注 corr 0.6-0.9 高带如实预告）；②vs ALLOC P5 slot 510880 腿面（配置线·判据不挪用只披露）。

## §2 数据与面板【跑前探针事实·冻结引用件 `results/div_lowvol_rot_probe.json`】

- 器械域：{510880, 512890}＝GM 批准的两器械域（DIV_LOWVOL_P1 §2「512890+510880 交叉验」承袭）；corpus twins `data/daily/sh510880.csv`（4784 行·2007-01-18→2026-09-22）+ `sh512890.csv`（1862 行·2019-01-18→2026-09-22）；零新拉取零网络。信号/估值价面=`DLP._adjust_split` 事后价（512890 factor 0.5·2021-10-25 起 post 面；R251 修正③）。
- **时间线口径=intersection**：联合时间线 T=**1862** bar（2019-01-18..2026-09-22·R251 修正①：探针 joint_bars=1862 权威数，错位日 A-only 已不在交集内）；错位日冻结清单=**['2021-10-22']**（=512890 拆分停牌 bar·R251 修正②：DLP.SPLIT_EVENTS 单源机械证据 1.639→0.801 ratio 2.0449；该日不在交集时间线内如实披露）；runner 断言「A-only-within-window==冻结清单 ∧ B-only 空」，不等即 fail-closed exit 2 零产物（日期漂移拒跑律）。
- **evidence_cutoff（D2 前向锁盒）＝2026-09-22**（双腿 corpus 末完整 bar=家族前批同 cutoff=比较性成立；core48 无前缀面板 09-23/09-24 有 bar 但 510880/512890 无无前缀孪生=锁盒排除面如实注记）；cutoff 后新 bar 不回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta('2026-09-22')`（缺字段=science_audit C2 VIOLATION）。
- 数据完备门（不过不跑）：cutoff==2026-09-22 ∧ T_joint==1862 ∧ legs==2 ∧ A-only-错位日==['2021-10-22'] ∧ 双腿时间线内 open/close/volume 零 NaN（探针后实证复核）。
- **ADV 容量面（探针实证·家族根因承重）**：ADV20 中位（CNY·volume×close 口径）：512890＝2020 **2.45M**/2021 **2.08M**/2022 19.3M/2024+ 225M+（薄窗→深水结构变迁）；510880 全窗 73M+。→ §3.5 参与帽排队面由此定标。

## §3 方法学【全冻结】

### §3.1 信号（零 α 参数搜索）

- RS_W(t) = C_t / C_{t−W} − 1，W ∈ {63, 252}（两腿各算）；t 收盘算信号、**t+1 开盘执行**（T+1 禁未来数据）。持有 argmax 腿；浮点严格相等 tie → 双腿各 50%（冻结确定性规则）。

### §3.2 组合构造（百万资金日线可建模性）

- 初始资本 **¥1,000,000**（票面 CN-* 纸盘规格）；每 **21 交易日**再平衡（月度节律=容量友好·冻结）；单腿 100% 仓位（无杠杆无 cash buffer）；执行/估值=家族先例（MF_ROT/DOG 面）：入场 t+1 开盘成交、日终收盘估值、出场 t+1 开盘成交（出场日腿 P&L=open/prev_close−1）；现金腿零收益（逆回购面另票）。
- T+1 合规：月度节律持有恒 ≥21 交易日>1，结构性无同日往返；runner 加 T+1 断言（R240 fail-closed 律）。

### §3.3 防御门（构成件·政体轴）

- **MA200 门**：t 收盘评——选中腿 C_t > MA200(t) → 持有该腿本周期；C_t ≤ MA200(t) → 本周期 100% 现金。冻结 200 无搜索无调参。bare 格无门。warmup（W 或 MA200 未满）=现金如实披露（cash-honest）。

### §3.4 null 与基线

- null：K=50 **随机腿轮动袖**（每再平衡点 `numpy.random.default_rng(20260980+k)` 均匀抽腿·k<50·同窗同节律同成本同 warmup）；**seed 基已在本件冻结 commit 内登记 `science_gates.SEED_REGISTRY['cn_div_lowvol_rot_p1']=20260980`**（band 20260980..20261029·全仓 rg 扫描零 RNG 使用命中·CN-REV 撞号教训前移到冻结点）；gate 格共用 bare-null 分布=对 gate 格更严的保守面如实注记。
- 被动基线：静态 EW pair 50/50（同 21d 节律再平衡回 50/50）+ 双腿 buy-hold 披露列；试验总数 N=54 记入账本（BACKTEST_PLAN 铁律三）。

### §3.5 成本与容量（家族根因承重面）

- **V2**＝ADV20 三层滑点+**1% ADV 参与帽**（knowledge/rules.py CostPatch 单源）；**判 face=费率×2 恒开**（家族先例）；×1/×3 披露列；逐段/逐年成本披露。
- **参与帽排队成交模型（诚实容量面）**：单名义超过 1%×ADV20 时**逐日排队成交**（每日 min(剩余, 1%×ADV20)，fill_days 计数器落盘披露）；探针定标：2020-2021 512890 腿 ¥500K 级单按帽排队 ~20-25 交易日=早期窗仓位建立滞后如实入账（家族 fill_refusal 面的排队化正解）。

## §4 判据【跑前写死·共享库调用禁手抄判线】

- **G1' v2**＝`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=4, pool='core48', n_trades, n_entries, null_pool={values, coverage})`（判 face x2）：全期 Sharpe > skill_line_v2（max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）且平稳 bootstrap CI95 下界>0 且 entries≥30；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入（缺输入=诚实拒收）。
- **G2 注册资格 v2**＝`science_gates.g2_registration_v2(g1_pass, dsr, pbo)`：G1' 过线 ∧ DSR≥0.95（`deflated_sharpe_ratio` 原始日收益跑·禁 dsr_from_stats 充数）∧ 家族 PBO≤0.25（`screening/pbo.py` CSCV-8·4 格网格）。
- 描述性条款（批级披露不替代 v2 门）：年化>0、OOS（≥2025-01-01）双正、|maxDD|≤35%、无≤−30% 崩年、×2/×3 成本逐年稳定。
- **硬界设计三件套【D-20260925-01①】**：极端日判读以 median/p99.9 分布界承担主责；max 硬界配**危机窗感知**（冻结三窗：2020-03 COVID 崩、2021-02 核心资产崩、2024-09/10 暴力反弹——命中→记危机日志+单点豁免单列披露，单点删除优先于整批判负）；§5 跑前预测给极端日先验。
- 判负即收线：4 格全负=CN-DIV-LOWVOL-ROT 模型判负照登（新证据=新预注册，禁翻案）。

## §5 跑前预测【写死于跑前·跑后对账】

1. **bare 格 x2 全期 Sharpe ∈ [0.3, 1.0]**（家族 C1 0.3557 为 ORANGE 门段内持有面；裸轮动过 2021 风格逆风段——红利低波 2020-2026 主升政体承载，带宽从宽诚实）。
2. **MA200 门格 vs bare**：maxDD 收窄 ≥25%（跳过风格趋势破位段）但 2024-09/10 V 型反弹 whipsaw 付出再入场成本——全期 Sharpe 变化方向不确定 ∈ [−0.2, +0.3]（诚实双向带）。
3. **W252 > W63 稳定性**（年窗少 whipsaw）；预测 W252_bare 为四格最强。
4. **成本面**：月度节律+双腿 argmax 低换手（预计年切换 1-3 次）→ ×1→×2 Sharpe 衰减 <15%（与 REV20 月级 20 名重建重成本面反差）。
5. **容量面**：2020-2021 512890 腿 fill_days 排队计数 >0（家族根因承重预测）；早期窗实际建仓滞后=裸面收益打折诚实入账。
6. **极端日先验**：2024-09-24→10-08 暴力反弹窗=红利风格主 whipsaw/极端面（利率政策转向）；2020-03 COVID 崩窗；2021-02 核心资产崩窗；max|d1| 硬界按三件套分布界+危机豁免，禁裸 max 判负。
7. **判负先验（诚实）**：家族前批 0.3557 败线 1.0924 在案；两腿同风格族内相关高→argmax 选择增量薄；本批=假设检验载体非准入保证，先验偏 FAIL；若 bare≈EW pair 则「轮动零增量」照登。

## §6 产物

- 脚本：`scripts/cn_div_lowvol_rot_p1.py`（实现切片·后继轮次：intersection 装载器+mismatch 冻结清单断言+V2 CostPatch 排队成交+checkpoint 幂等+selftest 腿+audit 段）；
- 结果：`results/cn_div_lowvol_rot/p1_results.json`（顶层 evidence_cutoff + cutoff_meta + 4 格×{x1,x2,x3} 全输入输出 + nulls50 + 基线 + D6 清单 + fill_days 面）+ CSV 明细；
- 账本：`science_gates.append_ledger('CN-DIV-LOWVOL-ROT-P1', 54, <结果件名>, evidence_cutoff='2026-09-22')`（dict schema 唯一禁手抄 prev）；attrition 行入 **`entries`** 列表（r248 消费链律）。
- 过闸后续链（声明·不属本批判据）：过 G2 → CN-DIV-LOWVOL-ROT 纸盘账户（¥1M·CN-* 族独立车道·PROS 白名单范式）+组合判决台入池；不过=判负照登收线。

## §7 跑后实证【跑前为空——写数字即造假】

**池执行留痕**：入池 R251 2026-09-26 14:39:04（entry 46）→ autofill 发射 14:50:27（bm-a pid 43612；本 tick 因 r252 autofill 反饿死修复得以越过 T80 熔断头批）→ 落地 14:50:53（sim 墙钟 18.4s·workers 1·65 units fresh·0 resumed·双跑字节恒等由 selftest 锁）。**N_trials=54 入账**：ledger 185798+54=185852（runner `append_ledger` 自动）；attrition 行入 `entries`（第 44 行·r248 消费面可见证）。

**四格×三成本面（x2=判决面）**：

| cell | x1 | **x2** | x3 | x2 ann_ret | x2 maxDD | x2 n_trades |
|---|---|---|---|---|---|---|
| W63_bare | 0.4881 | **0.4596** | 0.4311 | 6.36% | −18.18% | 405 |
| W252_bare | 0.7416 | **0.7371** | 0.7326 | 10.63% | −19.89% | 50 |
| W63_gate | 0.2029 | **0.1699** | 0.1368 | 1.40% | −25.85% | 388 |
| W252_gate | 0.2907 | **0.2716** | 0.2526 | 2.78% | −24.61% | 135 |

**skill_line 读数**：n_eff=185802·line=0.9527·passive_term=0.4792·null_term=0.9527（μ_null=0.3862·σ_null=0.115·pool=core48·ledger head=grid_sleeve_p1.json）。

**G1'/G2/D6 数值**：G1'v2 **0/4 过线**（W252_bare 0.7371 最强：CI95 [0.0139, 1.4851] 下沿为正但 line 0.9527 未达；W63_bare 0.4596 CI [−0.3084, 1.2146]；trade_gate 四格 dual_ok 全过：n_trades 405/50/388/135≥30、n_entries 274/47/230/72≥30）。DSR 四格全 0.0（sr_star=0.520325·T=1861·n_trials=185802）。G2 四格 ineligible（g1 未过·missing_inputs 如实披露）。family PBO=0.0（CSCV 8 块·70 组合·n_trials=4）。D6 vs 在册 6 员 max|corr|：W63_bare 0.2358/W252_bare 0.2583/W63_gate 0.2233/W252_gate 0.2289（argmax 均 VOLATILITY-CE-01·<0.7 无拒收）；同批族内相关 0.81-0.91（族面预期·由 family PBO 承载非 D6 面）。**null K50**：μ=0.3862·σ=0.1150（seeds 20260980+i·x2 face·W63-bare warmup）。**基线** EW pair 5050 x2 Sharpe 0.4972（ann 6.86%·maxDD −18.92%·192 trades）。

**门轴读数**：market_v3_axis 逐年状态分布入档（2019-2025 GREEN/YELLOW/RED/ORANGE 计数面）；rotation_gate_axis 载明 MA200 门跳过日面；descriptive 四格 full_ann_positive/oos_dual_positive/max_dd_line_pass/no_crash_year（crash_year_line −0.3）全 true，x1/x3 年度符号稳定 W252_bare 8/8、8/8（W63_bare 8/8、7/8）。

**fill_days 面**：W63_bare fill_days_max=17·mean=4.05（n_transitions 30·2020-2021 排队实证）；W252_bare fill_days_max=2·mean=1.25（首入场日 273=2020-03 后·n_transitions 6）；W63_gate fill_max 17·mean 2.92；W252_gate fill_max 11·mean 3.89。truncated 全 false（无强平截断）。

**极端日法证**：三件套执行面=分布界 median/p99.9 主责+max 配危机豁免（crash_year_line −0.3 单列）+跑前先验三条（§5.6）在案；四格 no_crash_year=true=极端日未击穿分布界主判。

## §8 批后复盘【跑后必填·s7-T】

**§5 逐条对账**：
1. bare ∈ [0.3, 1.0]：**HIT**（0.4596 / 0.7371 双落带内）。
2. MA200 门 maxDD 收窄≥25% + Sharpe 变化 ∈ [−0.2, +0.3]：**双 MISS**——maxDD 反向恶化（W63 −18.18%→−25.85% 恶化 42%；W252 −19.89%→−24.61% 恶化 24%），Sharpe delta −0.29/−0.47 双破下沿；双腿宇宙中 whipsaw 再入场成本 > 趋势破位保护收益（门格不是免费防御）。
3. W252 > W63、W252_bare 四格最强：**HIT**（年窗少 whipsaw 实证）。
4. ×1→×2 Sharpe 衰减 <15%：**HIT**（W63 −5.8%、W252 −0.6%；低换手 50 trades/7.7y≈6.5 次/年）。
5. 2020-2021 512890 fill_days>0：**HIT**（W63_bare max 17；W252_bare 首入场已在 2020-03 后 max 仅 2）。
6. 极端日三件套：**按冻结执行**（§7 法证行）。
7. 判负先验：**应验**——0/4 过线照登；W252_bare vs EW pair +0.24（0.7371 vs 0.4972）=轮动增量存在但不达线，非「零增量」。

**skill_line_v2 当批判读**：line 0.9527 全库唯一权威派生（ledger head 60 冻结面 + null 面），判负非线漂移所致——W252_bare 与线距 −0.216，诚实差距。

**gate_attrition 留痕**：runner 已追加第 44 行（`entries` 列表·g1_prime_pass 四格 false·eliminated 54·refs 本 prereg+T-73）。

**判决行**：**CN-DIV-LOWVOL-ROT 判负收线**（0/4 过 G1'v2·§6 过闸后续链不触发=不开纸盘账户不入判决台）。最接近面 W252_bare 0.7371（CI 下沿正、x1/x3 稳定 8/8、族内最强）留档为家族证据；**判负禁翻案律适用**——未来重开须新预注册+新证据面（老窗读数禁复用为过闸证据）。

**收割留痕**：`results/_r252bma_rot_harvest.py` 确定性收割门 PASS（十面重derive：ledger 算术/panel_gates/seed 基/四格×三面/skill_line/D6/nulls50/EW 基线/attrition 消费面可见/发射证据）→ 池 entry+shard 翻 done + harvest_note（r244 律·批不自翻）。

**R252 同轮链修复附录（工程修复·判定面零动）**：收割时发现本批 ledger 块被 runner 嵌在非正典键 `ledger` 下（链头扫描器唯一认 `trials_ledger`）——同病族共五件（t33/div_lowvol/cny_window/cn_rev_tilt/本批）+两处正确键谱系缺口（p1e_zoo 窄域扫描器 157、market_clock run1 并发窗跳过 exit_overlay 30）+t33 被 xstock_synth prev 跳过 40 → 记录头 185798 缺 394。修复=`results/_r252bma_ledger_chain_repair.py`（五件键正典化+真链重锚：本批 prev 185798→186138、total 185852→**186192**=真链头；六 runner 码点改写/续跑检查键正典化）。**判定面字节零动**：skill_line 4dp 不变（本批真 n_eff 186142→线 0.95273→0.9527 同值；CN-REV +4e-5→0.6147 同值），四格判负结论不受影响（裕度 ≥0.1）。§7 「185798+54=185852」为落地时记录事实照留；中间正确键批件（cta_wave1..grid_sleeve）记载数=被超越的历史推导（max-total 链头已真）；复审注册行 T-73-CN-DIV-LOWVOL-ROT-P1 + R252-BMA-LEDGER-CHAIN-REPAIR 同轮落册、复审器 run 全 YES。

—— bm-a 组合与资金部+研究部 R252 收割轮回填（2026-09-26 14:5x · 跑后一次定稿 · 零编数）
