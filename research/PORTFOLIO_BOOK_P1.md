# PORTFOLIO_BOOK_P1 · 袖盘组合书构造判决批（预注册·O-20260930-1147 §一.2 L2 执行面）

> 【状态：FROZEN——跑前 commit 冻结】载体票 T-2026-10-01-138（bm-a 认领）。跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。
> 令源：O-20260930-1147（组合融合线令·CEO 原话建议「也需要去进行组合，融合等，单策略不一定合适」·GM 科学采纳 T1）§一.2＋§二.4「循环侧组合线预注册起草」；改革正典 r272 bm-c §6 点名「组合书并轨件独立预注册」；r270 步⑤接线注记「O-1147 L2 组合书 bh_batch_fdr 消费」。
> 模板：research/PREREG_TEMPLATE.md（r483 增 §0.5/§1.2/§8 必填面）。

## §0 批件身份【必填·跑前】

- 批名 / 批号：**PORTFOLIO_BOOK_P1**（批内格数＝**4** 书配置＝D6 阈 δ∈{0.50, 0.70}×权重规则∈{EW, IVOL}；每格计入 N_eff 与 §四闸归因）；
- 认领：F-04 先行＝`fleet/inbox/MSG-20261001-0712-bma-ALL-portfolio-book-prereg-berth.md`（起草窗开启声明·防双机撞车）；任务单引用＝T-2026-10-01-138-P1（open+claim 同轮·O-20260924-1730 即时律）；
- 部门归属：dept:研究/策略（组合线·O-1147 §一.2 袖盘组合书面）；
- 批型：**书级构造判决批（book-construction judgment）非新生成批**——18 袖盘＝REEVAL18 花名册冻结档（drill 判决档案权威·单员改革门 0/18 已收口＝「单袖盘不达线也可入书」的 O-1147 原文适用面）；零新候选生成、零 Sobol 抽取；新增试验＝4 书配置格（重组合面）；
- RW-5 面合规：解冻锚=bm-a r476（RW-1~4 全绿·MSG-20260930-1525 双机印证）后本件=解冻窗内新入库 prereg（先例=REEVAL18_DRILL_P1 自声明首件）；本批无新供给线（18 员全部在库已判决）、无新 SLOT（书上岗=s3 另片·既有纸盘泊位机制）；
- 算力预算：单机内联 <5min（18 员重放主导〔探针实测全批 ~2min〕＋4 书配置×月度再平衡矩阵运算＋LOO 确定性面＋bootstrap 冻结种子族；纯 pandas/numpy 单机；O-2100 长活入池律不适用——实测超 5min 红线则诚实升池化）；批报告必带 audit 段。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/PORTFOLIO_BOOK_P1.md` → exit 0 = 放行。
- 本批机制主张＝**袖盘间协方差结构（组合分散）＋书层月度再平衡结构收益**，非任何已证伪九方向主张；重放对象全部＝已判决档存成员（各自原波预注册过闸在案·verdict 照册不翻案）。
- 命中 BAN-__：无（本节自引段外正文按词面纪律起草：不含九方向任一模式词面）。

## §1 α 机制段【必填·D6——无机制段=批不受理】

- 四选一：☑ **结构性**——①组合分散：不完美相关的收益流组合使组合方差低于方差加权和（协方差结构 α，由「各自持有不同暴露的行为对手盘」付价）；②书层再平衡结构溢价：固定权重月度再平衡在袖盘间波动下产生机械性低买高卖结构收益（行为对手盘=追涨杀跌者）。α 由袖盘间协方差结构承载，非任何新信号主张；单员显著性不必要＝本判据面的定义性特征（O-1147「分散收益=判据组成部分·单袖盘不达线也可入书」原文）。
- **散户凭什么赢【§1.2·必填】**：**制度/容量**——机构委托条款/风控合规/考核周期要求每个持仓有独立显著故事，结构性做不到持有 18 个单员不达线袖盘的组合书；散户资金规模下容量无限、零冲击成本、机械月度再平衡纪律可自由执行（与 ALLOCATION_POLICY_SCAN-P1 §1.2 同款制度面先例）；本市场（A股 ETF 场内）无机构拥挤面。
- §1.1 引用清单：①仓内 `research/ALLOCATION_POLICY_SCAN.md`（13.1 年四资产权重×再平衡全量扫描＝书层再平衡面与成本口径先例·引用不自跑）；②仓外源档 `research/digests/DIGEST-20260928-t102-lane2-institutional.md`（风险平价/ERC/All-Weather 机构结论验证＋**相关性政体突变失效面＝本书主风险面**〔Q1 2020/Callan 政体依赖〕——外源证据面即此引用，不另开新扫描〔借力三律工程版：既有已验外源档复用〕）；③`research/REEVAL18_DRILL_P1.md` §7/§8（单员改革门 0/18＝组合面立项直接证据）；④五员 EW 基线（O-1126 定谳·r271 冻结档窗读数 2.8086%）。例外三问=不重跑任何机构结论（①~④全引用面）。
- **同族相关性准入检查【D6】**：本批 D6 面＝**批内袖盘间 pairwise**（O-1147 §一.2「sleeve 间 D6 ≥0.7 拒收既有机制」原文钉面）：r505 探针全矩阵 153 对——max=0.99259、mean=0.484403、≥0.70 对=31、≥0.50 对=69、<0.30 对=37（逐对数值与 18×18 全矩阵＝探针件 `results/portfolio_book_probe/pairwise_corr_p1.json`·payload_sha256=50b77e2ac98e3be0a702658b3338dcb12149b7f4a2be73a2b770b696ad92a8d4）；**vs 注册六员 corr＝披露列非门**（书=独立纸面账户主张·s3 上岗预检时按 drill 同款 vs-registered 全算逐员呈 GM——舰队重叠面在上岗面把关非本批门；此读法为声明性裁量，接受复审）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 袖盘池：REEVAL18 花名册 18 员（W1:4 / W2:11 / W3:2 / W5:1）——`results/reeval18/ROSTER.json`（G-ANCHOR-FACE 四元组：`results/reeval18/ROSTER.json`＋`reeval18_drill._load_roster`（sha16 恒等断言）＋全档＋预热 0）·roster_sha16=`7c5ac06b3a243450`（drill 同款钉扎）；
- 面板：core48（G-ANCHOR-FACE 四元组：`live.paper.load_core`→`build_panels`＋全史起算＋截断 ≤cutoff）——48/48 员在位、末行==cutoff、OHLCV 齐（drill `_build_state` verbatim import·G-PANEL 同门）；语法面 `results/trial_labor_w1/w1_grammar.json` sha16=`27445dcfd5b3872b`（drill manifest 恒等）；
- 合成分序（贪心选择唯一输入·冻结档）：`results/reeval18/DRILL-2026-09-22.json` `g2_reform.members[<id>].composite`（G-ANCHOR-FACE 四元组：该档件＋json.load＋sha16 断言＋预热 0；drill_results_sha16=`fe131c1a63e1e3d2`〔r505 探针实读钉扎——runner prep 门逐位复核〕）；
- 窗口与 **evidence_cutoff（前向锁盒 D2）=2026-09-22**（EVIDENCE_CUTOFF_GRID 冻结值·与 drill 判决面恒等＝花名册可比性+锚门构造前提）：窗=2026-01-05→2026-09-22（176 窗日·base 2025-12-31·drill manifest 恒等）；cutoff 后新 bar 锁定不回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)` 字段。
- 探针事实（r505 本批专属·`results/_r505bma_book_pairwise_probe.py` 产出）：18/18 员重放 ok、176 窗收益/员、窗内交易数 23–66/员（全部 ≥MIN_WIN_TRADES=10 样本足量）、pairwise 形状统计与全矩阵在探针件（payload_sha256 见 §1 D6 行）；**runner 探针-锚同面断言**：烧前重算 18×18 矩阵 payload_sha256 恒等比对（漂移=配置错配 VOID·fail-closed 拒烧·报「面错配」非「数据腐坏」）。
- 数据完备门（不过门禁烧）：①roster sha16 恒等+18 行+逐行 wave∈{w1,w2,w3,w5}；②面板 48/48+末行==cutoff+OHLCV；③G-ANCHOR 六员 live anchor 门（drill `cmd_prep` 同款·registered 六员重放 vs live anchor 逐员 ok）；④探针矩阵 payload_sha256 恒等；⑤零退化员（窗收益 std>0 全员）。

## §3 方法学【必填】

- 袖盘曲线：18 员全史重放（drill `_wave_run` verbatim dispatch：w1→tl1.run_candidate_curve / w2→tl2 / w3→tl3 / w5→tl5 全族 verbatim import 禁重写），x1 基线＋x2=CostPatch(2) 双曲线（drill `_run_cell` 同款）；窗收益=eq.iloc[wbase:] pct_change（176 值/员）。
- **选择规则（冻结·零研究员自由度）**：贪心前向按 §2 冻结合成分序逐员尝试入书——与已选任何员 |pairwise Pearson corr| ≥ δ → 拒（x1 窗收益面＝探针矩阵同面）；δ∈{0.50, 0.70} 两档；序表冻结（复合分降序 18 员：W1-A-0360 0.802484 → W1-A-0007 0.758170 → W3-A-0325 0.749902 → W2-A-0349 0.716552 → W2-B-1971 0.642794 → W1-A-0048 0.625507 → W5-B-2619 0.564363 → W2-A-0222 0.562843 → W2-A-0116 0.556307 → W2-A-0085 0.428023 → W1-A-0066 0.419346 → W2-A-0456 0.409395 → W3-A-0312 0.362059 → W2-A-0066 0.355229 → W2-A-0486 0.317712 → W2-A-0224 0.277042 → W2-A-0300 0.257859 → W2-A-0006 0.194412）。
- **权重规则（冻结两档）**：EW=所选员等权；IVOL=波动率倒数归一 w_i(t)∝1/σ_i,60d(t−1)（严格因果·60 窗日滚动已实现波动·σ 非有限或=0 该员该期降为等权份额并计数披露）。
- **再平衡（冻结）**：月度＝每月首个面板交易日收盘执行；信号用截至 t−1 收盘信息（IVOL 权重面）→ t 收盘执行（严格因果·一日滞后如实披露）；再平衡日按目标权重置、其余日权重随收益漂移（w_i(t)=w_i(t−1)(1+r_i(t))/(1+r_book(t))）。
- **书层成本【CN-C7】**：再平衡换手成本=Σ_i|w_target,i − w_drift,i|×X1_RATE（`knowledge/cost_spec.py` X1_RATE=0.0013041 **import 派生禁手抄**·runner 断言恒等；ETF=26.082bp/往返 面 A 口径）；**双计披露声明**：袖盘内部换手成本已在袖盘曲线内（曲线面承载），书层成本仅计书层换手；x2 书曲线=Σw_i·r_i,x2 −Σ|Δw_i|×2×X1_RATE；名义档位=¥1,000,000 账户申报（袖盘级已按 Face A 口径）。
- 书日收益：r_book(t)=Σ_i w_i(t−1)·r_i,x1(t) − rebalance_cost(t)；窗首建仓按目标权（建仓成本=Σ|w_target,i|×X1_RATE 一次计·如实披露列）。
- null 对照：K=0 随机 null（**声明性裁量**：重组合面无新信号生成可作 null 检定——运气面由批内 FDR+batch_dsr 承担、平稳面由 bootstrap CI 承担；被动基线=五员 EW 2.8086%＋beat6m passive_rel 口径照用）；零随机自由度（bootstrap 种子=20260923 冻结族〔drill CI_SEED 恒等〕·LOO 确定性·无新 SEED_REGISTRY 登记）。
- **子面（书级窗面）→ science_gates 冻结维度映射**（禁增禁手抄子面集）：
  - ret.sharpe_full_L=书窗 Sharpe（年化·引擎约定）；ret.annualized_ret_L=书窗年化；ret.return_ceiling_O1126=书窗年化−五员 EW 窗年化（2.8086% 冻结档）；ret.beat6m_rate_L=窗内滚动 6m 起点胜被动率（passive_rel 口径·起点 p∈窗且 p+W6−1≤窗末）；**ret.diversification_delta=书窗 Sharpe − Σ_i w̄_i·sharpe_i**（w̄_i=该员窗内实际权重均值·确定性派生；EW 档=员窗 Sharpe 算术均——组合胜其加权成分的纯分散差·O-1147「分散收益=判据组成部分」冻结实现）；
  - robust.cost_x2_sharpe_L=x2 书曲线窗 Sharpe；robust.regime_min_sharpe_L=min(bull/chop/bear 三段窗 Sharpe·REGIME_MAP verbatim·段<20 窗日缺席 renorm)；robust.bootstrap_ci_low_L=`bootstrap_ci_sharpe(书窗收益, seed=20260923)`；
  - anti_overfit.loo_min_sharpe=留一员去重算书 Sharpe 最小值（确定性零随机·逐员移除后同权重规则再归一）；anti_overfit.loo_ratio=loo_min_sharpe/sharpe_full_L；anti_overfit.family_pbo=所选员 family_pbo 冻结档值引用披露（drill 同款「引用非重算」读法）；
  - anti_luck.batch_dsr=`deflated_sharpe_ratio(书窗收益, n_trials=4)`（批内口径·改革法）。
- 批内 FDR：p=单侧 1−Φ(t)，t=`t_from_sharpe(书窗 Sharpe, 176)`（D-37 M1 t 面采纳·drill 同款）；`bh_batch_fdr(p, q=REFORM_Q_LEVEL=0.10)`。
- 合成与 L3 门：`g2_reform_fdr4d(book_metrics, REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS, batch_p_values)`——权重/子权/q 全 science_gates 冻结常数 import 禁手抄。
- 账本：`science_gates.append_ledger("PORTFOLIO_BOOK_P1", 4, file_name, evidence_cutoff="2026-09-22")`（dict schema 唯一·禁手抄 prev）。
- **闭合族对号声明【M3】**：本批 family_key=**portfolio_book_p1**——`science_gates.CLOSED_FAMILIES` 六在册键零命中=open 照跑；与 cn_combo_five_family（REV-TILT/DIV-LOWVOL-ROT/REGIME-POLICY/CORE-SATELLITE/DDCTL 择时政策组合五族 19 格）关系声明＋**新证据增量**（O-20260925-1105 通道）：①彼五族否证时不存在书级判据面（批内 FDR at book level＋分散收益入判据）；②袖盘母体=W1-W13 试用劳动波判决档（非彼五族格）；③单员改革门 0/18 读数=组合面立项直接证据；④CEO 令 O-1147 §二.2「承旧不翻案·新面一律新预注册」原文授权。
- M1 t 面申报：书级 t=t_from_sharpe(书窗 Sharpe, 176) 信息列随批披露（批内 FDR 即 t 面多重检验消费·改革口径 D-37 采纳·drill 同款读法；m1_t_value_gate t≥3.0=旧单点注册线门，改革产品线不适用——声明性裁量接受复审）。
- REGIME_GUARD 仓帽照用（披露面）：当前态钉帽=冻结梯 {GREEN:0.80, YELLOW:0.65, ORANGE:0.50, RED:0.20}[regime_state.state]·帽后年化/Sharpe 披露列**不进合成记分**（drill 同款）。
- 确定性与血统：r446 三命令真数据恒等律——prep（roster/grammar/anchor/矩阵 sha 断言）→run（逐配置 checkpoint append）→finalize（双跑恒等门·漂移=exit 2 如实上报）；全批 L1 确定性零网络零随机自由度。
- s3（若过门·另片执行）：TRIAL-BOOK-* 纸面观察账户上岗（¥1,000,000·marks 范式=aggressive_lab 先例·非试验账本 +0·SEED +0）＋月考=真终审＋48h CEO 白话报告；上岗预检含逐员 vs-registered D6 全算呈 GM。

## §4 判据【必填·跑前写死，禁看结果调线】

- **eligible_book（书级判决门）** = fdr_pass（bh_q≤0.10）∧ composite 完备（四维无缺失）∧ **diversification_delta > 0**（书 Sharpe 胜其加权成分＝分散收益判据组成部分·O-1147 原文）。
- 整体 Sharpe/回撤双列：全配置披露 sharpe_full_L(x1)/sharpe_x2_L 双列＋max_drawdown(x1/x2) 双列（**O-20260929-1116 风险偏好律：回撤=披露+配对考量非关线**）。
- 硬披露门（非淘汰线·逐配置必带）：帽后年化、书层换手成本累计、建仓成本、所选员清单＋逐员 vs 注册六员 corr（drill d6 档值引用）、逐员窗 Sharpe、x2 面、beat6m、LOO 面、n_book_members、月度再平衡次数。
- 全配置判负=合法产出（O-1820 三验③：如实档案化，禁为满载改判线）；单配置过门≠上岗（上岗=s3 另片·月考=真终审·live gate=CEO only）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

1. **选择面量级**：δ=0.70 书员数 ∈ [3, 12]；δ=0.50 书员数 ∈ [2, 8]（探针形状推演：31 对 ≥0.70 集中于同模块孪生簇〔max 对 0.99259=W5-B-2619×W2-B-1971 型〕→贪心序首员保留+孪生剔除；<0.30 对 37 张提供低相关备员池）。
2. **分散主张（核心方向主张）**：δ=0.70 两配置中至少一个书窗 Sharpe **> 最强单员 1.6839**（W1-A-0360 冻结档）——组合方差收缩胜单员最优；若全败=分散主张本窗证伪（诚实收线）。
3. **显著面方向主张**：δ=0.70-EW 配置 p 值 **< 0.0797**（drill 最优单员档）——组合面显著性强于任何单员面；fdr_pass 配置数预测 ∈ [0, 2]（4 格 BH q≤0.10 首序阈≈p≤0.025 量级＝书窗 Sharpe 需 ~2.3+，窗短 176 日为硬约束·如实预期不保证）。
4. **稳健面**：全配置 LOO loo_ratio ≥ 0.5（书 Sharpe 不依赖任一单员）；x2 书 Sharpe 衰减 ≤25%（月度低频书层换手轻成本）。
5. **极端日先验**：窗内已知极端期=2026 年 07 月小盘/科创主极端期（r272 极端日探针档：588000 07-21 +11.07% 唯一 ≥9.5% 级）＋04-08 全员同向簇形态——书层面单日 |r| 可达 ±3–5%（多员同向暴露日；无 max 硬界入判·回撤=披露列＝硬界设计三件套 (b) 披露优先路径）。

## §6 产物

- runner：`scripts/portfolio_book.py`（prep/run/finalize/selftest 子命令族·drill harness import 复用零重实现）；
- 结果：`results/portfolio_book/BOOK-2026-09-22.json`（顶层 `evidence_cutoff`＝science_audit C2 合法键）＋`book_cells.csv`（4 配置全列）＋本文件 §7 回填；
- audit 段随批报告（机器/elapsed/workers/逐配置耗时）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（2026-10-01 08:15 finalize 一次定稿回填·r506 bm-a 烧批+判决同窗；engineering 修复留痕：跑中 `_beat6m_book` 索引空间坑〔书曲线=窗空间 N+1 值·drill 员曲线=全史面板空间——原稿 iloc[p] 直用面板位出界 IndexError 实弹·修正=面板位 p→书位 p−w0+1·selftest 补 k-parity 腿 37/37·修复仅索引翻译零判据触碰·checkpoint 员面 18/18 未受影响照用〕）

- **判决：judged-negative·eligible_book 0/4**（trials ledger 368,815→368,819 +4；evidence_cutoff 2026-09-22；finalize 双跑恒等门=sentinel sha match+4/4 config sha match·多核池烧与串行字节恒等实证）；
- 逐配置（sharpe_full_L x1 / x2｜p｜bh_q｜composite｜div_delta｜loo_ratio｜beat6m rate｜帽后年化 ORANGE 0.50）：
  - delta0.70-EW（n=7）：0.9521 / 0.0469｜p=0.2131｜q=0.2842｜0.3971｜+0.2727｜0.4901｜51 窗 50 胜 0.9804｜1.19%；
  - delta0.70-IVOL（n=7）：0.5201 / −0.6188｜p=0.3319｜q=0.3319｜0.2629｜−0.0799（分散差负）｜0.5463｜0.9804｜0.43%；
  - delta0.50-EW（n=3）：1.8972 / 1.1442｜p=0.0564｜q=0.1934｜0.7371｜+0.4498｜0.8759｜51 窗 51 胜 1.0000｜2.90%；
  - delta0.50-IVOL（n=3）：1.5564 / 0.6292｜p=0.0967｜q=0.1934｜0.6029｜+0.0930｜0.8122｜1.0000｜1.62%；
- 选择面：δ=0.70 与 δ=0.50 同员集前 7/前 3（贪心序=W1-A-0360→W1-A-0007→W2-B-1971→W3-A-0312→…·δ=0.50 在第 4 员 W3-A-0312 处撞 δ 界止步 3 员）；书层换手：9 次月度再平衡·EW 档书层成本 6.6e-05/7.7e-05（近零）·IVOL 档 0.0016/0.00145；建仓成本 4 格同=0.0013041（X1_RATE import 恒等）；
- 月度起点年化分布（9 起点/配置·最好…最坏）：0.70-EW +3.28%…−2.31%｜0.70-IVOL +2.54%…−1.10%｜0.50-EW +7.03%…−2.63%｜0.50-IVOL +5.75%…−1.09%（全起点披露·单一起点结论无效面满足）。

## §8 批后复盘【必填·s7-T】

- **预测对账（§5 五条）**：①选择面量级=对（7∈[3,12]·3∈[2,8]）；②分散主张（δ=0.70 至少一配置 Sharpe>最强单员 1.6839）=**证伪**（0.9521/0.5201 双败·诚实收线——18 个亚阈值袖盘的贪心去相关重组在本窗未能胜过最强单员）；③显著面方向（δ=0.70-EW p<0.0797）=错（0.2131）·fdr_pass 数 0∈[0,2] 预测区间=对；④稳健面=部分（loo_ratio≥0.5 三过一败〔0.70-EW 0.4901〕·x2 衰减 ≤25% 全败〔−95%/符号翻转/−40%/−60%〕——x2 面读数释疑：书 x2 曲线=袖盘 x2 双成本曲线再叠加 2×X1_RATE 书层成本·三层成本复合·预测写时按「书层月频换手轻」单层直觉写就·实测证伪如实记）；
- **判线读数**：bh_fdr_q 全列={0.70-EW: 0.2842·0.70-IVOL: 0.3319·0.50-EW: 0.1934·0.50-IVOL: 0.1934}——最优 0.50-EW p=0.0564 在 4 格 BH 首序阈下无存留（§5 预测自注「窗短 176 日为硬约束」如实兑现）；门禁链损耗账已入 `results/gate_attrition.json`（judgment 行·cells_ledger_delta 4·total_after 368819·08:15:26）；
- **试验量归因**：本批 +4（书配置格·组合重组合面零新生成——袖盘母体已在其原波计数；30 天窗 ≤500 预算账面余量充足·当面实读计数如实入账）；4 格=CEO 令面最小诚实配置集（阈值×权重双档 stress 面·全量公布）；
- **E1 已知答案对账面（r492 律）**：本批无引擎成交/无 picks 面（纯重组合数学·run 与 finalize 同源 `_compute_config` sha 恒等门双跑互证）——无「判出面 P&L×入选员 raw 路径」可对账腿，以双跑恒等门+sha 断言承担仪器完好面；
- **收线**：全配置判负=合法产出（O-1820 三验③如实档案化）；s3 不触发（0 eligible→无 TRIAL-BOOK-* 上岗）；组合书线 L2 面本窗证据=「亚阈值袖盘重组无免费分散午餐」——未来重开须新预注册新窗（承旧不翻案）；回执入轮报告+CODELY.md 行级追加。
