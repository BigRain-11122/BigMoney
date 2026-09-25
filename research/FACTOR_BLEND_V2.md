# FACTOR_BLEND_V2 — 因子复合格批预注册 v2.0（框架稿·冻结窗后置）

> 复活依据链：T-48 v1 §8 裁定原文「复合格入列三军替补席的唯一路径=新预注册版本（DSR 缺口与段专项为下版必修面）」＋ PROFIT_MODEL_MAP（O-20260925-0857 GM 亲执）L3 行「牛市段专才补给…复合格线待新预注册」＝约束①攻击线。
> 票 T-2026-09-25-49（P1·bm-b 认领 r167）· F-04 MSG-20260925-1010。
> **本件=框架稿（原料无关面）：结构规则+账本口径+门禁链现在写死；短名单/参数/§5 预测=【冻结窗补】。**
> **冻结窗（物理依赖·票面在案）＝T-47 wave-6 收线＋T-46 MF_IC_P1 判定落地之后；冻结 commit 先于任何跑批（R99 律）；跑后只许回填 §7/§8，禁改判据禁重跑。**

## §0 批件身份【框架稿·冻结窗后置】

- 批名 / 批号：T48B-factor-blend-v2（T48-factor-blend v1 复活版；v1 链 60,880→61,015 +135 已在账）。
- 认领：票 T-2026-09-25-49 claim 同轮开立（bm-b r167）；F-04 MSG=fleet/inbox/MSG-20260925-1010-bm-b-T49-claimed.md。
- 部门归属：dept:研究+交易（T-48 血统延续）。
- **原料依赖（如实挂）**：①T-47 wave-6 已交片变体卡（LeBaron vol-regime 条件化＝DIGEST-20260925-alphaarchitect L40；vol-targeting+回撤限位＝DIGEST-20260925-quantconnect L38；Lesmond 成本面准入＝DIGEST-20260925-ssrn L31）——v2 即其**设计消费队列**（登记不排批→本批排批，反重复闭环）；②T-46 MF_IC_P1 判定读数＝C3 条件格原料门；③T-47 收线剩余片（PBCSF/CJoE/券商研报 slug 等）＝冻结窗短名单先验面输入；④wave-7 slice-1 cfrc 因子动量证据卡（DIGEST-20260925-wave7-slice1·bm-b r168）＝C2 格冻结窗输入面（A 股「个股动量死+因子动量活」多层结构证据/多头端贡献 79% 纯多可投性/极端行情反增强 vs LeBaron 低波卡=§5 必写张力条/形成期 t-12..t-2 跳 t-1 细节候选；情绪条件化=数据面指针挂起零申请）——预注册前零跑批·J18；⑤wave-7 slice-3 果仁社区证据卡（DIGEST-20260925-wave7-slice3·bm-b r169）＝④的社区独立同向源（因子月度排名反转/衰落→高潮反弹概率轮动实操＝「动量收割上移因子层」结构先验的双源收敛；扎堆因子跌最狠=crowding folklore 佐证；全部社区声称·股票域·2011-2016 窗·零成本口径=诚实标签全挂，§5 预测/张力条输入面·预注册前零跑批·J18）；⑥wave-8 slice-1 Bouchaud/CFM 趋势主源证据卡（DIGEST-20260925-wave8-slice1·bm-a R153·arXiv 1404.3274·全文抽取 assets/lemperiere2014_extract.txt 在案）＝C2 进攻格冻结窗机制先验输入面（期限结构平台区=2-10 月回看 n=3 峰 SR 0.83+~3 日级短趋势 1990 后衰减→趋势腿回看取月级、禁日级追逐的排期依据；tanh 饱和映射=信号非线性截断变体候选；股指期货趋势 SR 0.41=最弱部门→ETF 指数池内趋势腿单部门期望按低档校准+商品/债券 ETF 跨部门替代先验；回撤时长 1/S² 期望数学→§5 期望管理必写行；先验级非采纳·门禁链恒在·预注册前零跑批·J18）；⑦wave-8 slice-2 Wilmott 作者-论文追索证据卡（DIGEST-20260925-wave8-slice2·bm-b r171）＝C1 防御格 drawdown-limit 腿方法学参照（Pospisil-Vecer JCF 2008 最大回撤 PDE 方法+QF 2010 组合敏感性·registry-verified）＋T-28/B_MAXDIV 协方差条件化参照（Wolf SSRN 567785 resampling-vs-shrinkage；core48 n/p~0.1 落大维临界区外→shrinkage=conditioning 卫生面非异象引擎·采纳唯一路径=预注册 A/B 变体批·非本批面）＋§5 必写张力条挂账（LeBaron 低波条件化 vs cfrc 极端行情反增强·两方向叙事先验·我方门禁自裁）。
- 算力预算：≤3 复合格 × x1/x2 双面（≤5min 级；超则入 results\runnable_pool.json 后台化，O-20260924-2100 纪律）；workers=min(worker_cap(),8)；批报告必带 audit 段。
- 复用面（反重复铁律）：scripts/factor_blend.py 范式逐字（blend_score/run_cells_parallel/checkpoint key 律）、T-27 runner 血统、results/factor_registry.json（v1 交付①）、T-33 军种表只读、T-22 分段机（t22_virtual_timepoints）段证据载体、composite_rotation 原语、science_gates 共享库（禁手抄判线）。

## §1 α 机制段【D6】

- [x] **行为偏差＋风险溢价（复合面·v1 §1 血统）**：因子面承载在档溢价（横截面动量/低波异象/短期反转），混合不创造 α——候选收益=面间分散化＋面内加权规则稳健性，由行为人群付费。**v2 新增 wrapper 机制主张（已登记卡机制，非新发明）**：
  - **vol-targeting**：波动聚集期收缩敞口（σ_target/σ_realized 缩放）＝对「无条件持有者承担的方差惩罚」的收割——低波期保敞口、高波期降杠杆，风险溢价的期限结构 harvesting；
  - **drawdown-limit overlay**：深回撤阶梯减仓＝处置效应人群踩踏后修复面的纪律化；
  - **LeBaron vol-regime 条件化**：趋势收益集中于低波期（波动率-序列相关负关系）——动量/趋势短名单腿仅在低波 regime 启用；
  - **Lesmond 成本面准入分层**：大动量股恰是高成本股（成本集中律）——进攻军短名单只收「成本面可收割」成员。
- 诚实边界（v1 同款）：若面溢价在本面板不存在，wrapper 只会改变亏损的形状——诚实零过线=合法批读数。
- **同族相关性准入检查【D6·硬门】**：逐格日收益 sleeve 对在册 6 员（COMPOSITE-CE-01/02、DROUGHT/ENGULF/NEEDLE/VOLATILITY）算 `max|corr|`（日收益序列口径，sleeve-tag 先例）；`max|corr| ≥ 0.7` → 拒收（数值+逐对清单全披露）。**v2 结构非同构预承诺（v1 教训固化）**：v1 的 IC/政体加权变体全数坍缩到 CE-02（corr 0.71-0.87）＝「同构加权规则收敛」实证——v2 的非同构主张**只许走收益过程改造面**（vol-target/drawdown-limit/条件化改变逐日收益序列，非截面权重规则变体）；若 D6 仍拒收＝「wrapper 不足以脱离在册冗余」诚实结论，禁降门。对 v1 15 sleeve 的两两 corr=描述性披露（v1 未入册，不作门）。

## §2 数据与面板【跑前事实·冻结窗补探针】

- 宇宙/池：core48 bare-codes（load_core 正典）；因子面=engine/factors.py FACTORS 28 键（登记簿 results/factor_registry.json）。
- **MF 原料面（T-46 依赖·条件格专属）**：MF_IC_P1 判定读数为冻结窗输入——过线面（mf_main_net_5/10/20＋超大单 pct 族中 G1'v2/G2 判定存活的子集）方可进 C3 格作 additive/conditioning 原料；**判负/未完成→弱检查声明（模板弱检查条款）+C3 整格剔除（格数只减不增）**。MF 面入批不引入新数据源（O-1620 已批域，T-46 批产物消费面）。
- 窗口与 evidence_cutoff：【冻结窗补】＝冻结时面板完整 bar 日；cutoff 后新 bar 不回流本批；结果 JSON 顶层必须带 `science_gates.cutoff_meta(cutoff)`（缺字段=science_audit C2 VIOLATION）。IS/OOS 分界=OOS_START 2025-01-01（仓内正典常数，v1 同款）。
- 数据完备门（不过门禁跑批，exit 2 诚实中止）：①登记簿在位且 engine_faces=28；②短名单键 ⊆ FACTORS 注册键（C3 采纳则另核 MF 面键 ⊆ MF_IC_P1 过线集）；③core48 bar 覆盖至 cutoff（末端缺口 ≤5 交易日）；④格参数冻结面逐字节由本文件派生（构建器禁外部参数）；⑤C1 锚定门=v1 defense|b_IC sleeve 记录值复现（|d|<容差，data-drift tripwire，破=先诊断面板非改判据）。

## §3 方法学【冻结】

- **减格强先验（DSR 缺口修复路径＝更少格＋更强先验，非门放宽）**：≤3 格，每格=强先验构造，格数在冻结窗只减不增：
  - **C1 承载体复活格**：v1 唯一 G1' 过线面（defense 短名单 × IC 加权）＋ **vol-targeting wrapper ＋ drawdown-limit overlay**。血统引用：v1 §7 defense|b_IC 全门读数（full S 1.3084·x2 存活 margin +0.4667·六条款全过·CI 下界>0）；段形态引用（必修面）＝**bull 2.2762 强/bear 0.4691 弱**（v1 §7 实证）——承载体本相=平稳段+牛市段收割者，非承压段专才。短名单与 wrapper 参数【冻结窗补】。
  - **C2 进攻军牛市专才格**（O-0857 约束①主目标面）：attack 族（趋势/动量/突破）短名单 ＋ **Lesmond 成本面准入分层 ＋ LeBaron vol-regime 条件化 ＋ vol-targeting＋回撤限位**（Kakushadze 27y 诚实负教训卡：无风控裸动量=噪声）。段专项目标引用＝**T-22 bull beat 0.471/0.266 缺口**（在册 6 员防御/震荡专才·进攻军崩塌）——本格=牛市段专才补给试炼。短名单与分层参数【冻结窗补】。
  - **C3 MF 原料格（条件格）**：T-46 MF_IC_P1 过线面作 conditioning/additive sleeve 原料；判负/未完成→剔除（§2 弱检查条款）。
- **权重规则**：IC 加权血统（IS 段估计·因果；v1 §7 EW 全军覆没 vs IC 加权一枝独秀——**知情先验如实披露**：此为 v1 结果知情选择，跨版本选择风险由 lineage-inclusive 账本口径买单，见 §4）。x2 面沿用 x1 冻结权重。
- **wrapper 定义框架（参数冻结窗定）**：vol-target=敞口缩放 σ_target/σ_realized(60d)（t−1 数据，因果）；drawdown-limit=组合层回撤阈值触发阶梯减仓；LeBaron 条件化=已实现波 regime 二分（低波期启用动量/趋势腿，高波期该腿停用）。全部 wrapper=引擎外层包裹，**退出优先级零改动**（铁律）。
- **复合格构造**：blend 分数 → top_n_rotation 血统（n/rebal【冻结窗补】）＋ CE 退出机器原样（loss_time 16＋decay 25d/5%＋trail 0.10，max_positions=5，position_size_pct=0.19）；引擎次日开盘执行、真实 T+1。
- null 对照：**零**（≤3 固定候选零搜索；skill_line_v2 以 lineage-inclusive batch_cells 计多重试验线——T-27 §3/T-48 §3 同款裁定）；无新随机族 → SEED_REGISTRY 零登记（g1_prime_v2 内嵌 bootstrap CI 用库正典 ci_seed=20260923）。
- 成本口径：**V1 legacy（13bp×2 压测，x1/x2 双面）**＋×3 面（G2 pack 层复用既有管线）。
- 账本：`science_gates.append_ledger("T48B-factor-blend-v2", N_eff_own, file, evidence_cutoff=...)`（dict schema 唯一）。**N_eff_own 构成**：引擎格 C×2＋排名帧格 C×3＋窗口格 C×6（IS/IS2/OOS/bear/chop/bull）；C=3 时 N_eff_own=33（剔除 C3 则 22，冻结窗按实格数定）。

## §4 判据【跑前写死·框架面，禁看结果调线】

- **主门（逐格，全满足才 eligible）＝G1' v2**：`science_gates.g1_prime_v2(sharpe_full, 日收益, batch_cells, n_trades, n_entries)`——**lineage-inclusive 口径冻结：batch_cells=135（v1 全批血缘格）＋N_eff_own**。全选择路径诚实计数：v2 设计为 v1 结果知情面（复活批），知情选择的试验账不许清零（比 T27-v2 更严——其 v1 为 VOID 零产数无知情面）；此为方向更严非更宽（R117 血统）。六条款（EW6 先例 g1_clauses）＋CI 下界>0＋entries≥30＋benefit>0＋DR>1＋x2 存活（x2 full Sharpe>vi_bar 且 x2 IS2 Sharpe>0）＋稳健（IS Sharpe>0 且 worst_year>−0.30）——v1 §4 逐字范式。
- **G2 注册资格 v2**：`science_gates.g2_registration_v2(g1_pass, DSR, PBO)`——DSR≥0.95 **原始收益跑**（`deflated_sharpe_ratio`，N 口径同上 lineage-inclusive，禁 dsr_from_stats 充数）；家族 PBO≤0.25（CSCV 8 块，家族=本批格 sleeve 集，g25_retro 先例）。v1 缺口=DSR 0.4966——v2 修复路径=wrapper 实质改善收益谱＋减格强先验，**非口径放宽**。
- **军种段专项（T-33 §3 冻结口径逐字）**：beat_rate_12m≥0.50 且 n_startpoints≥30 且 no_blowup（全段全窗 worst_dd≥−0.35）。**主评估载体预承诺＝T-22 harness 适配**（t22_virtual_timepoints 虚拟起点腿接线本批格 sleeve，6m/12m/24m 窗）；接线机制性阻断→诚实回退=全窗 regime_proxy 分段统计＋回退披露，禁静默换判据（v1 §7 同款）。**牛市段主目标面（约束①）**：C2 段读数以 bull 段为主目标；段证据缺或未达=候选不入席（T-33 candidate 语义）。
- **D6 硬门（§1）先于排名**：拒收格入 §7 披露不占 winner 面。三面排名（benefit/drawdown/x2 margin 中位秩，平手→benefit）——v1 §4 逐字；零 eligible→无 winner 诚实收线。
- 同预注册同网格禁重跑；跨版本复活路径=本文件本身（SS4）；成本 ×2/×3 面；零未来数据。

## §5 跑前预测【冻结窗补——含极端日先验（模板三件套 (c)，冻结时必写】

【冻结窗补】（≥3 条方向/量级预测+本批数据窗极端微观结构日形态与量级先验；写死先于跑批。）

## §6 产物

scripts/factor_blend_v2.py（run/status/selftest 子命令·factor_blend.py 范式逐字复用·hermetic 夹具含 wrapper 单元腿）＋ results/factor_blend_v2_cells.json（格 sleeve+门读数+audit 段+evidence_cutoff+cutoff_meta+D6 逐对清单）＋ results/factor_blend_v2_runs.jsonl（checkpoint 行带 key）＋ results/factor_blend_v2_verdict.json（逐格门读数+段专项+winner 裁定）＋ research/shortline/factor_blend_v2_results.csv ＋ gate_attrition.json 追加行 ＋ 本文件 §7/§8 回填。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

## §8 批后复盘【必填·s7-T——跑后回填】

- 预测对账（对/部分/错）＋门禁链损耗账（gate_attrition 追加行）＋skill_line_v2 当批读数（lineage-inclusive 口径数字）＋回执入轮报告＋CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff＋live/paper SIGNAL_BUILDERS 接线＋smoke 锚定门复跑。
