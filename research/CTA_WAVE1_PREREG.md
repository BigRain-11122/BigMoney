# CTA_WAVE1 — 波-1 期货复活批预注册（跑前冻结）

> 按 research/PREREG_TEMPLATE.md 起草。**本件 commit 即冻结**；跑后只许回填 §7/§8，禁改判据禁重跑。
> 复活律：CE_ADMISSION_V1 §3「判负线禁翻案·复活唯新预注册（house law）」——本批=新 prereg+新 pattern 集+新证据面（深史窗+TS 品种+降杠杆变体+基差新维度）；旧判负三档案**并排保留**：CTA_P1（R50·G1' 0/16·skill_line **1.1463**）/ CTA_P2_NOAU（R53·0/16·**1.4278**）/ IM_IC_PAIR（R140·0/2·**2.278** 对子 carry 臂），判负结论不触碰不翻案。
> CEO 授权链：O-20260925-1158（全品种回溯验证令）→ T-2026-09-25-65-P1 s2（immediate 票·census §六波-1 定稿：唯一 data-ready×去相关×百万三维全高域）。

## §0 批件身份【跑前冻结】

- 批名：CTA_WAVE1（波-1 期货复活批·T-65 s2）。
- **批内格数=78**：候选 26（Leg A 16＋Leg B 8＋Leg C 2）＋随机 null K=50＋被动基线 2。每格计入 N_eff（append_ledger 单源；×2/×3 成本信息列不计数，CTA_P1 先例）。
- 认领：F-04 先行=MSG-20260925-1950-bm-a（fleet/inbox/）；票 T-2026-09-25-65-P1（claimed_by=bm-a R184，CEO immediate 票认领与开动同窗已毕）。部门归属：**dept:研究+数据**（联合票 note：prereg=研究部、TS 数据腿=数据部）。
- 合法性链：O-1620 期货域 GM 署名 → O-1158 品种扩容 CEO 令（TS+金融期货新员=CTA_P2_NOAU §8「新品种扩容（P1 署名门）」由 CEO 令兑现）→ census s0/s1（R184/R185：数据面探针实证+三维排序波-1 定稿）。
- 算力预算：面板 4561 union 日 ×10 品种 ×78 格——CTA_P1 同构 68 格@2353 日面板 64.6s 实测先例 → 估 **150-300s 单进程**（bars×1.94·cells×1.15）；实现切片以实测冒烟裁定：>5min 入 runnable_pool 分片（O-1137 载体）禁轮内内联代跑；批报告必带 audit 段（无 audit 段不入账本）。

## §1 α 机制段【D6】

- [x] **行为偏差（Leg A/B 主）**：反应不足/锚定——趋势延续（CTA_P1 §1 逐字沿用：新信息在期货价格中缓慢扩散、保证金强平放大趋势；代价支付方=追涨杀跌散户与扛回调锚定持仓者）。**Leg B 非新 α 主张**：同一趋势机制的**风险变换**（保证金占用帽 50%/30%=降杠杆变体，CTA_P1 §7 复活条件②直引——检验的是 dd 结构可达性非新 α）。
- [x] **风险溢价（Leg C 主）**：股指期货**对冲压力贴水补偿**——机构空头套保压力使期货价格系统性低于现货（贴水），多头收取贴水收敛的对冲保险溢价；代价支付方=付保费的对冲空头（保险卖方收费逻辑）。CN 股指期货贴水历史实证面（2015 限制后贴水常态化）。
- **同族相关性准入【跑后必填】**：批内 26 候选 pairwise 全披露（CTA_P1 先例）；在册 6 员（core48 ETF 域）corr 仅对 passer 计算（跨资产类先验低相关，CTA_P1 §1 预注沿用）；≥0.7 拒收。跑前预注：Leg B 四基信号与既往 tsmom/vol_target 族同 DNA（去杠杆版），批内 corr 预期高（≥0.9 面在 tsmom_60 与 vol_target_tsmom_60 间，CTA_P1 实测 0.9357 同族先例）——**帽变体与无帽变体不同批**（本批无 CTA_P1 无帽 8 族），批内重复度可控。

## §2 数据与面板【跑前探针事实·results/cta_wave1_probe.json】

- 宇宙：**10 品种主力连续**＝9 在轨（IF/IC/IH/IM/T/TF/RB/AU/SC）＋**TS 新腿**（futures_zh_daily_sina('TS0') 变体——futures_main_sina 无 TS 面；2018-08-17→2026-09-24 1967 行，R184 普查探针先验+本批 p3 实拉落盘 data/futures_daily/TS.csv）。
- **窗口裁定（与两前批的结构性差异=深史维度）**：面板=**全史 union 起点 2008-01-09**（AU 2008-01-09 起 4560 行/RB 2009-03-27 起 4251 行=CTA_P1 判据窗 2017-01-17 弃用的深史，本批评据面**纳入**；IF/IC/IH/T/TF 本源面 2017-01-17 起/IM 2022-07-22/SC 2018-03-26/TS 2018-08-17=上市后自然进入，warmup 自适应 n_alive 加权）。
- **诚实边界（O-1158 纪律锚）**：票面「25y 深史」在本数据面**不可达**——sina 主力连续面最长=AU 18.7y；25y=测量器械边界如实标注（代理纪律：深史维度以本面全史兑现，非裁剪选择）。**深窗集中度披露（冻结）**：2008 存活 1 品种（AU 单独）、2009-2016 存活 2 品种（AU+RB）——前段=单/双品种账本集中度极高，**全期 pooled 判据为主、2008-2016 深窗段/2017+ 宽窗段分段描述性披露并列**（非判据变更）；alive breadth 实测 yearly mean=2008:1.0/2009:1.78/…/2017:6.76/2023+:10.0。
- **evidence_cutoff=2026-09-24**（09-25 中秋休市=最后完整 bar 日；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-24")`）。
- **信号输入裁定：OHLCV 五列 only**（oi/settle/hold 退出信号输入——覆盖参差实证：TS hold 在而 CFFEX settle 全 0；CTA_P1 §2 冻结沿用）。
- **roll-gap V0 直用裁定**（CTA_P1 §2 逐字沿用）：原始连续价不平滑不掩蔽，候选/null/被动同面板对称注入=相对判据内部有效；G2 注册前置数据债条款不变（分合约 roll 平移复权）。
- **数据完备门（不过禁跑批）**：①10/10 CSV 在场且末 bar=evidence_cutoff（TS 2026-09-24 ✓探针）；②span 内缺口=**冻结豁免集 18 cell**：2017-10-09×5（IF/IC/IH/T/TF 源端日历缺口）+2019-04-22×3（AU/RB/SC）+RB 深窗 10 日（2009-05-01/2010-05-03/2010-10-07/2013-09-19/2013-10-01/2013-11-20/2014-01-16/2014-03-07/2014-03-13/2015-07-02）——引擎语义=缺行品种当日不可交易 carry+ffill 盯市（候选/null/被动全对称）；其余任何洞=FAIL；③OHLCV 无负值（探针 p1 全 10 品种 none ✓）；④逐品种行数/首末 bar 披露进 audit 段（探针 p1 head/tail repr 已固化）。
- **现货代理面（Leg C）**：510300/510500 ETF 日线（data/daily/，**2020-01-02 起 1633 行** cut 09-24）→ **基差腿窗=2020-01-02→cutoff**（两腿短者；期货面 2017 起但代理面 2020 起=诚实收窄）；期货日历重叠比 1.0（探针 p4）；**代理律**：ETF≠指数（跟踪/分红/费率面），基差=期货对 ETF 溢价代理非对指数真基差，scale-free 比率口径，如实标注。
- **国债 carry 面（wave-1b 数据门·未过）**：chinabond 收益率曲线探针 FAIL（"No tables found"，探针 p5）→ **国债期限结构 carry 族不在本批**（阻塞面不立终判 r186 对称律）；复探过=wave-1b 子票另开预注册。

## §3 方法学【跑前冻结】

- **信号族（Leg A：趋势参数面扩容 8 新 pattern·既往 8 族零重复；冻结参数）**：
  1. `tsmom_20`：20d 累计收益>0→+1，<0→−1，否则 0（短周期动量——ETF 域 J6 警示 2025+ 短趋势失效，期货域未扫）
  2. `tsmom_40`：同上 h=40
  3. `donchian_20_10`：20d 通道突破入场/10d 反向通道退出（短通道）
  4. `donchian_120_50`：120d 入场/50d 退出（Turtle 经典长通道——既往 55/20 外延）
  5. `dual_ma_20_100`：MA20/MA100 金叉+1/死叉−1（慢速交叉）
  6. `dual_ma_50_200`：机构级长均线对
  7. `ma_slope_200`：MA200 的 20d 斜率符号 ±1/0（趋势 regime 面，区别于 price-vs-MA）
  8. `channel_pos_55`：55d 通道位置 pos=(close−low55)/(high55−low55)，pos>0.8→+1/pos<0.2→−1/中间持前态（连续位置 state 型）
  - 评估制式 2 档 {daily, r20}（CTA_P1 同款）→ **16 格**。
- **Leg B（降杠杆 vol-target 变体·CTA_P1 §7 复活条件②直引）**：基信号 4＝{tsmom_60, tsmom_120, vol_target_tsmom_60, vol_target_tsmom_120}（vol_target=方向×min(1, 1%目标日波/60d 实波)）；**保证金总占用帽 2 档 {cap50, cap30}**（Σ|手数|×乘数×价×保证金率 ≤ cap×上日权益，超限按占用最大品种逐手缩减——CTA_P1 §3 缩减律沿用；cap=1.0 即 CTA_P1 原语义=引擎加性参数默认 1.0 既往批字节不变）→ 4×2=**8 格**，daily 制式 only（期货域 daily>>r20 律 8 实证；闲置现金 0 利保守口径不变）。
- **Leg C（股指基差 carry·新维度）**：`basis_if_510300`/`basis_ic_510500`：比率 r=F_close/S_close（scale-free），m=60d 滚动均值，dev=r/m−1：dev<−0.002→+1（深贴水做多收贴水）/dev>0.002→−1/中间 0（死区 20bp 冻结）→ **2 格**，daily 制式；窗=2020-01-02+（§2 代理面裁定）。
- **执行语义（futures_runner 移植沿用）**：T 信号→T+1 开盘调仓；T+0 双向；手数=带符号整数；单品种保证金份额=等权 1/n_alive×权益（Leg B 全局帽叠加）；涨跌停近似=开盘触昨收±品种限幅不开新仓（平仓恒允许）。
- **TS 器械常数（provisional·G2 交易所核验门前置）**：mult=20_000（面值 200 万/百元报价）/margin=0.005/tick=0.005/limit=0.005/fee_lot=3.0——实现切片 G2 门：对照交易所现值，偏差>30%→冻结核验值+如实披露（CTA_P1 G2 先例），不过门禁跑批。
- null 对照：K=50 同面板随机信号（每 20d 重抽样、存活品种等概率三态 ±1/0），**seed=SEED_REGISTRY["cta_wave1"]=62_000（62_000+k；登记+rg 全仓扫描空闲 2026-09-25 19:5x 后冻结——唯一 rg 命中=数据文件数字巧合非 RNG，t34/wild_route 先例）**；同 seed 双跑逐位确定性=硬门。
- 被动基线 2：`passive_long_r20`＋`passive_long_monthly`（存活品种等保证金 long-only，深史全窗）→ 写 results/shortline_cta_wave1.json，池分支 `cta_wave1` 单源读取（science_gates 加性分支已接线，selftest 34/34）。
- **成本口径：V1 legacy 期货域**（per-lot 费 FUT_META 冻结常数+1 tick 滑点/边，CTA_P1 G2 核验门同款）＋**×2/×3 信息列**（律 8：期货近免费先验；breakout@daily ×2 深负例外在案=本批 Leg A 高换手格照跑信息列）。
- 引擎载体：engine/futures_runner.py **加性扩展**（TS 入 FUT_META+margin_cap 参数默认 1.0+Leg C 双输入信号接口；ETF 引擎零触碰）；scripts/cta_wave1.py（gates/run/selftest 三态子命令，CTA_P1 先例）。
- 账本：`science_gates.append_ledger("cta_wave1", 78, "results/shortline_cta_wave1.json", evidence_cutoff="2026-09-24")`（dict schema 单源，禁手抄 prev）。

## §4 判据【跑前写死】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=78, pool="cta_wave1", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据驱动=max(本批被动 strict-max+0.10, μ_null+σ_null·√(2·ln N_eff))）**且**平稳 bootstrap CI 下界>0**且 entries≥30（F6 双口径）。**期货域自有 null+被动，禁跨域套用 core48/股票线**（CTA_P1 律沿用）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线**且** DSR≥0.95（原始收益 deflated_sharpe_ratio）**且**家族 PBO≤0.25（CSCV 8 块；Leg A=8 pattern 参数族 16 格/族内 2 制式、Leg B=帽族 8 格、Leg C=2 格族 g25_retro 2-cell 先例）；缺输入=诚实拒收。
- 描述性条款（批级披露）：年化>0；IS2 段（2025+）双正；回撤≥−35%（**Leg B 帽变体的检验点**——CTA_P1 满保证金 dd 全灭 −0.66~−0.96 的结构病，cap50/30 预期实质改善）；无崩年；×2/×3 信息列；per-variety 归因（**CTA_P2_NOAU §7 路径依赖警示带入**：品种归因是账本组合路径函数非结构常量，AU 腿贡献须与深窗段披露并列解读）；**深窗段（2008-2016 AU/RB 1-2 品种期）与宽窗段（2017+）分段 Sharpe 并列披露**（§2 集中度裁定的判读配套，非门）。
- **硬界设计三件套对照（D-20260925-01①）**：本批数据健康门=完备性（缺口∈冻结 18 cell 豁免集**精确集合匹配**）+非负性+末 bar 新鲜度——无裸 max 价格跳变门（分布界主责条款不适用：本批无腐坏检测型判线）；极端日先验入 §5(c)（预案=豁免单列披露非整批判负）。

## §5 跑前预测【写死，跑后对账】

1. **被动（深史）**：AU 2008-2016 含 2011-2015 金价熊段+RB 长熊 → 本批被动 Sharpe 预测 **0.5-0.9**（CTA_P1 2017+ 窗 0.9337 的深史版，贴水/熊段拖累方向）。
2. **null 带**：10 品种宽宇宙+深窗前段 1-2 品种高集中 → σ_null 预测 **0.30-0.45**（宽于 9 品种 0.2901：深窗集中度放大单品种随机账本波动）；N_eff≈3100-3250 → null_term 预测 **0.9-1.3**；skill_line=max(被动+0.10, null_term) 预测 **1.0-1.4**。
3. **Leg A 最优格**：donchian_120_50@daily 或 tsmom_40@daily（中频带既往未扫）；全期 Sharpe 预测 **0.4-0.8**（CTA_P1 无帽最优 0.74 同量级）；tsmom_20 高换手×成本深负风险（breakout@daily ×2 −0.68 先例）。
4. **Leg B 帽变体**：Sharpe 预测与无帽同族同量级（**0.6-0.8**，杠杆水平缩放收益/波动同缩）但 **margin_usage_max≤0.5/0.3 实测达标**+dd 预测 −0.25~−0.45（帽变换主检验点：dd 描述条款首次结构性可达）。
5. **Leg C 基差**：2020-2024 IC 深贴水窗利好做多收贴水 → 预测 Sharpe **0.3-0.7**、entries 40-80；死区 20bp 下换手中低。
6. **家族 PBO**：Leg A 8-pattern 参数族选择脆弱性高 → PBO 预测 **0.3-0.7**（fail 带风险）；Leg B 帽族机制单一 → 0.0-0.2；Leg C 2 格族信息列。
7. **passer 预测 0-2**：null 主导线 ~1.0+ 结构性高（两前批判负的线形态延续）；批科学价值=pattern 面证据+帽变体 dd 可达性+基差面首测，非注册预期。
8. **极端日先验（硬界三件套 (c)·本批窗内可能击穿任何跳变阈值的形态）**：SC 2020-03/04 原油崩盘主连切换（|r1| 可达 20-30% 级）；RB 2016-03 螺纹涨停熔断潮（±7% 限幅日连发）；AU 2013 断崖（单日 −5%+ 级）；roll-gap 换月跳空 |open/prev_close−1|>3×60d std 日（CTA_P1 敏感性条款同源）——豁免单列披露预案在册。

## §6 产物【跑前声明】

- scripts/cta_wave1.py（gates/run/selftest 三态子命令；复用 cta_p1_screen 构建器与 futures_runner，零重写）
- engine/futures_runner.py 加性扩展（TS 常数+margin_cap 默认 1.0+双输入信号接口；既往批语义字节不变=selftest 断言）
- results/shortline_cta_wave1.json（顶层 evidence_cutoff+audit 段+verdicts+null_pool+passives+per-variety 归因+深窗/宽窗分段+prereg_sha256_at_run）
- research/cta_wave1_results.csv（78 行全列）＋本件 §7 回填
- results/gate_attrition.json 追加一行；STRATEGY_LIBRARY C 层行回写

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（跑后回填）

## §8 批后复盘【s7-T 必填】

- 预测对账（§5 逐条对/部分/错）＋gate_attrition 条目＋判线 v2 当批读数（skill_line 数字）＋D6 同族逐对清单＋深窗/宽窗分段读数。
- 回执入轮报告+CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff+live/paper SIGNAL_BUILDERS 接线+smoke 锚定门复跑。

---

## 实现轮前置门（gate list，跑批前全过才许 run）

- G0：smoke 全绿
- G1：futures_runner 加性自检=合成面板确定性双跑逐位+margin_cap 语义单元断言（cap=1.0 与既往批逐位恒等）+TS 手数/预算/涨跌停单员断言+Leg C 双输入信号滞后断言（T 信号 T+1 开盘，禁未来数据）
- G2：TS 器械常数交易所核验门（§3 provisional 对照，>30% 偏差冻结核验值）
- G3：数据完备门（§2 四条+18 cell 豁免集精确匹配）
- G4：null/被动确定性（同 seed 双跑逐位）
- 审计段必带（compute_audit run 嵌批内）
