# OG1_OVERNIGHT_IC 预注册：隔夜/日内分解族 IC 预测批（zoo #78 升级 · 跑前写死）

> 令源：O-20260924-1721（CEO 借力令·常态外调链波-3）· T-31 deliverable-5（「upgrade wave-2 family overnight_gap to IC-pretest prereg（建投 32 因子子族选 3-5）」）
> 认领：**MSG-20260924-1922-bm-c-T31-claim**（先于本批 commit，F-04）· T-2026-09-24-31（bm-c r65 认领锁 eebcda6）
> 性质：**因子/统计层 IC 预测批**（零引擎跑→引擎账本 N 不动；IC≠策略，**本批不注册交易员不接线策略**；PASS 仅入候选货架，策略转化另走预注册+G1' v2 门禁链）
> 命名消歧：批号 OG1（Overnight Gap 1）——zoo #78 `overnight_gap` 族的 IC 预测批判号；与 PA1（溢价）、PA1E（溢价事件）、PA2_LHB_SYNTH 零撞名。

## §0 批件身份【必填·跑前】

- **批名/批号**：og1_overnight_ic；**批内格数（N_eff）=55**：1 primary（on_mom_20 @h10）+4 同族 sensitivity（in_mom_20/on_vol_20/on_in_div_20/onin_corr_20——全部同源报告列非独立假设，不判不独立计格）+50 matched-mask null；primary 过 V1 后 h5/h20 报告列 +2（上限 57）。
- **认领**：F-04 先行——fleet/inbox/MSG-20260924-1922＋任务板引用=T-31 deliverable-5。
- **部门归属**：dept:研究（外调链·T-31 车道）。
- **算力预算**：1632 日×48 员面板全向量化+K=50 白噪 null，单进程预估 <3min（R41 免后台化）；批报告必带 audit 段（无 audit 段结果件不入账本）。

## §1 α 机制段【必填·D6——四选一】

- [ ] 风险溢价：
- [ ] 行为偏差：
- [x] **结构性**：A 股 T+1 制度 → 当日买入者被迫隔夜承险 → 隔夜段系统性负溢价（chaoe.net 11 年解剖：全 A 等权隔夜累积 −77.7% vs 日内 +1397.5%·大票 −96.4%/小票 +48.9%【第三方回测·未实证】）；LPS 2019 JFE「A Tug of War」隔夜/日内分解框架 + Aboody 隔夜动量（美股隔夜具持续性）→ chaoe 拔河姊妹篇称 A 股截面「隔夜成分是动量、日内成分是反转」【社区研究·未实证】；清华 PBCSF 月频动量消失论文（日内/隔月动量+T+1 强反转关系【wave-2 矩阵收录·原文 PDF 本轮未达】）。**机制性摩擦非纯行为异象，T+1 不废则不自衰减**。信号付费方=为隔夜跳空风险提供流动性的对手方+T+1 锁仓补偿错位。
- [ ] 微观结构：

**同族相关性准入检查【必填·D6】**：
- 批内冗余（冻结披露）：5 因子全部同源于 ON/IN 分解（ON=open/prev_close−1·IN=close/open−1）——动量（on_mom/in_mom）/背离（on_in_div）/波动率（on_vol）/相关性（onin_corr）四子族为建投「逐鹿」#29 32 因子族的日线可算子集（clean-room 逻辑提取：公开描述级子族标签，零专有表格复制）。**同族=4 sensitivity 报告列不独立计假设**，N_eff 已按此记 55。
- 跨批同族：与 PA1 premium 族（close/NAV 血缘）不同源（OHLC 价格分解非折溢价）；与既有动量因子族（rma/ratt，全日收益口径）成分重叠披露——on_mom 为分解子成分，全日动量=on_mom+in_mom 合成；**IC 预测批不做策略级 corr 逐对**（转化批届时按 PREREG_TEMPLATE D6 条款做 max|corr|≥0.7 逐对）。
- **primary 方向冻结=正 IC**（隔夜动量延续：过去强隔夜成分 → 未来强）——单侧判。

## §2 数据与面板【必填·跑前探针事实，非结果】

- **宇宙**：core48 全体 48 员（面板即全员，无扩池）。
- **面板**：价格面=data/fund_premium/panel/panel.csv 的 close/div_per_unit/cons_flag（r53 建成 2020-01-02..2026-09-23·1632 td）；开盘面=data/daily/<code>.csv 48 件 no-prefix OHLCV 按 panel 日历 reindex join。
- **evidence_cutoff=2026-09-23**（前向锁盒 D2 同 PA1）；结果 JSON 顶层必须带 `science_gates.cutoff_meta(evidence_cutoff)`。
- **因子定义（冻结·日线 OHLCV 可算）**：ON(t)=open(t)/close(t−1)−1；IN(t)=close(t)/open(t)−1；K=20：on_mom_20=expm1(Σlog1p(ON))；in_mom_20 同构；on_vol_20=std(ON)；on_in_div_20=on_mom_20−in_mom_20；onin_corr_20=配对完备 20 日 corr(ON,IN)。open≤0 坏点→双腿 NaN。**信息时点：因子于 t 收盘后已知（IN(t) 需 close(t)），入场 close(t)→close(t+h)，零未来数据。**
- **跑前探针事实（2026-09-24 19:5x 采样·样本量非结果）**：T=1632×N=48；daily-join coverage=**0.9708**（panel 行有对应日线有限 open+close 的比例；2.92% 缺口=源差日（EM 面板 vs 日线 CSV 源差）+晚上市首日窗，**掩码职责非数据病**（r55 行/矩形律））；on_mom_20 有限格占比=0.9509（20 日 warmup+join 缺口）；mask10 cells=73,790·中位截面=47·IS 期数(n≥5)=1192·OOS=410。IS/OOS 切分=composite_ic.IS_END=2024-12-31 全公司口径。
- **数据完备门（不过门禁跑批·探针校准值跑前冻结）**：①panel summary verdict=PASS 且 evidence_cutoff=2026-09-23 且 members=48 ②join coverage≥**0.95**（探针 0.9708 留裕量；阈值选于产数前非事后）③on_mom_20 有限格占比≥**0.90**（探针 0.9509）。
- 样本窗诚实披露：6.75 年政体覆盖有限（同 PA1 §2）；48 员截面以指数 ETF 为主体、共同运动高（PA1 平价员稀释教训在案）；T+0 员（债/跨境/金）与 T+1 员结构相反=类间噪声源（zoo #78 注记）。

## §3 方法学【必填】

- **前瞻收益（冻结，PA1 逐字）**：fwd_ret_h=分红包容=(close[t+h]+Σ_{t<d≤t+h} div_per_unit[d])/close[t]−1；cons 窗排除：(t,t+h] 内该员 cons_flag=1 任一日→剔除该 (t,员) 对。h10=唯一门控期限；h5/h20=primary 过 V1 后报告列（snooping 折价标签）。
- **估计量**：逐日横截面 Spearman IC（mask-first 后排名·n≥5·零方差→NaN）；IS 段（≤2024-12-31）池化 ic_mean/ic_ir（primary 判据）+OOS 段（V3）。
- **mask（冻结）**：on_mom_20 有限 ∧ close 有限 ∧ fwd_h10 可算 ∧ (t,t+h] 无 cons；K=50 null **同 mask**（P-A 律：窄截面须同 mask 带）。
- **null（白噪·冻结）**：K=50；每 null i（**seed=20260927+i，i=0..49；新基已登记 `science_gates.SEED_REGISTRY["og1_overnight_ic"]=20260927`**（rg 全 repo 扫描 2026-09-24 19:4x 确认空闲，非 registry-only 双查 r54 坑律））：mask 内标准正态噪→IS 段 |ic_mean| p95。白噪选择=PA1 连续 IC 先例（PA1E 圆移位为事件聚簇设计，本批连续口径无聚簇结构）。
- **等价门（先跑）**：−60d 动量探针（close 面·零接触 open 列）400 日随机子样 vs composite_ic.ic_series 参照；max|diff|>1e-6→中止零产数。
- **成本口径声明**：IC=信息层零成本；经济地板 0.02=因子层墙（非可交易利润）；转化批届时走 ETF 域成本模型。
- **账本**：零引擎跑→引擎账本 N 不动；因子账本 added=55（±2 报告列）——`science_gates.append_ledger("og1_overnight_ic", ...)`（prev=max(results, results/shortline) 双目录 r60 惯例）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **期数门**：IS n_periods ≥500（探针 1192 预期过门）。
- **h10=唯一门控期限**（h5/h20 报告列带 snooping 折价标签）。
- **V1（经济+null 门·单侧正向）**：IS ic_mean > max(0.02 地板, 同 mask null p95 |ic|)；
- **V2（统计墙·单侧）**：IS ic_ir ≥ 0.30；
- **V3（留存）**：OOS ic_mean > 0 且 OOS ic_mean ≥ 0.5×|IS ic_mean|；
- **PASS = 期数门∧V1∧V2∧V3**（primary 判；4 sensitivity 只报告不判——同族变换非独立假设）。
- 判据口径：因子批（IC 型）三门口径（模板 §4 末行）；**零策略级评估不触及 g1_prime_v2/g2_registration_v2**（共享库门属策略转化批）。
- **PASS →** on_mom_20 入 ETF 域素材货架（策略转化另开预注册：G1' v2+DSR+PBO+成本模型+D6 逐对 corr）；**FAIL →** zoo #78 行记「IC 预测批判负（48 员截面稀释/组件动量信号弱），机制知识面保留（chaoe 分解事实/建投子族标签），无预注册禁翻案」。**禁翻案条款**：任何 K 值/期限/子族变体翻案须另开预注册——禁止跑到达标为止；sensitivity 列强读数不构成翻案（另开预注册正道）。

## §5 跑前预测【必填·写死于跑前，跑后 §7 对账】

1. **primary 方向=正**（隔夜动量延续）——置信 **45%**（机制对齐但两重压制：①48 员指数 ETF 截面共同运动高=PA1 平价员稀释同构风险；②T+0/T+1 员结构相反掺噪声。chaoe 拔河截面动量主张本身【未实证】）。
2. 量级：|IS IC| ∈ [0.005, 0.025]（PA1 premium_z 0.0033 同截面量级参照；动量族分解子成分预期弱于全日动量）。
3. null 带：p95|ic| ∈ [0.008, 0.02]（PA1 null p95 0.0083·同中位截面 47）→ V1 地板 0.02 大概率主导。
4. **过门预测：0-1/1 primary，偏 0**（稀释先例在案：PA1 0/1、PA1E 0/1、P2 合成 0/3——本批基线预期判负诚实收线；若 V2 真门可达则见 §5.2 上沿）。
5. sensitivity 读数预测：in_mom_20 负号（日内反转主张）；on_vol_20 负号（低波溢价）；on_in_div_20 正号（ON−IN 背离=动量-反转拔河净值）；onin_corr_20 无方向预测（纯报告）。
6. 多重性声明：隔夜分解族**首测**（zoo #78 登记后首个批测）；FAIL 时 sensitivity 读数不构成任何翻案。

## §6 产物【必填】

- `scripts/og1_overnight_ic.py`（一次性定稿：probe/selftest/run 三态；数据门→等价门→null→primary+sensitivity→门判定→账本，全链一脚本；selftest 子命令产数前先跑）；
- `research/shortline/og1_overnight_ic_results.csv` + `results/shortline/og1_overnight_ic.json`（顶层 evidence_cutoff+`science_gates.cutoff_meta`+null 阈值/门判定全输入/audit 段）；
- verdict 入轮报告+CODELY.md 行级留痕；`gate_attrition.json` 追加行；zoo #78 行按 verdict 更新注记（PASS=候选货架/FAIL=IC 预测批判负+机制保留）；funnel 双列（T-31 §7）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（2026-09-24 20:0x r65 一次定稿回填；判据零改动）

- **数据门**：g1 panel summary PASS/cutoff=2026-09-23/48 员 ✓｜g2 join_cov=0.9708≥0.95 ✓｜g3 on_mom_20 有限格 0.9509≥0.90 ✓——三门全过。
- **等价门**：−60d 动量探针 n=383 common，max|diff|=2.22e-16 ≤1e-6 ✓（与 PA1 同探针同量级）。
- **null 带**：K=50 白噪（seed 20260927+i），IS p95|ic|=**0.0086** → V1 阈=**0.02（地板主导）**。
- **primary on_mom_20 @h10**：IS ic_mean=**+0.0127**、ic_ir=**0.045**、n=1192；OOS ic_mean=**−0.0075**、n=410。判据：期数门 1192≥500 **PASS**；V1 0.0127<0.02 **FAIL**（差 1.6×）；V2 0.045<0.30 **FAIL**（差 6.7×）；V3 OOS 反号 **FAIL**；**总判 FAIL**——h5/h20 按冻结协议未解锁。
- **sensitivity 报告列（不判）**：in_mom_20 IS +0.018/OOS **+0.0598**（双段正号——chaoe 日内反转主张在 ETF 域不支持，域错配披露）；on_vol_20 IS +0.0003/OOS +0.0352（IS 平塌）；on_in_div_20 IS +0.0058/OOS −0.0339；onin_corr_20 IS **+0.0461**（族内最强 IS 读数、超 V1 地板）/OOS **−0.0194 反号**——即便判也 V3 死；全部同族报告列，**禁翻案条款生效**：任何单列变体须另开预注册。
- **账本**：因子链 5709→**5764**（+55）；引擎账本 N 不动（零引擎跑）；audit 段已嵌结果 JSON；gate_attrition 已追加 OG1_OVERNIGHT_IC 行；批 elapsed 9s。

## §8 批后复盘【必填·s7-T】

（2026-09-24 20:0x r65 回填）

**§5 预测逐条对账**：
1. primary 方向正（45% 置信）→ **命中**：IS +0.0127 正号，但量级在 null 带缘。
2. |IS IC|∈[0.005,0.025] → **命中**（0.0127 带内）。
3. null p95∈[0.008,0.02] → **命中**（0.0086 触下沿；与 PA1 0.0083 同中位截面 47 自洽）；地板 0.02 主导 → **命中**。
4. 过门 0-1/1 偏 0 → **命中**（0/1）。
5. sensitivity 预测：in_mom_20 负号 → **未中**（+0.018，且 OOS +0.0598 双正=chaoe「日内反转」截面主张在 ETF 域无支持）；on_vol_20 负号 → **未中**（IS 0.0003 平塌，无方向）；on_in_div_20 正号 → **方向命中**（+0.0058 微弱，OOS 反号）；onin_corr_20 无预测 → 披露：IS +0.0461 族内最强但 OOS −0.0194 反号，单列无 OOS 留存不构成候选。
6. 首测即判零重跑 ✓（一次定稿 9s，selftest 9/9 先行，两处断言侧笔误修复发生于产数前零数字产出——PA1E 同范）。

**判线当批读数**：V1 阈 0.02（地板主导）｜primary IS +0.0127｜V2 0.045 vs 墙 0.30｜V3 反号 −0.0075。

**损耗账**：1 primary 死于 V1+V2+V3 三杀（1.6×/6.7×/反号，无近线争议）；4 报告列如实记录不判；50 null 带健康。

**机制层诚实归因与收线**：隔夜成分动量在 core48 ETF 域因子层仅存 null 带缘的微弱正迹（+0.013），无 OOS 留存——ON/IN 分解信息若存在，在 48 员指数代理截面不可开采（PA1 平价员稀释同构 + T+0/T+1 员结构相反掺噪声）。**域错配披露**：chaoe 分解的负隔夜集中在大票/高成交额半池（−96.4% vs 小票 +48.9%）——单票/大票域的结构效应不迁移到指数 ETF 代理面；日内反转主张同不迁移（IS/OOS 双正）。zoo #78 行已记「IC 预测批判负（r65 OG1）·机制知识面保留·域错配披露」；**禁翻案条款重申**：onin_corr_20 IS 读数与任何 K/期限/子族变体须另开预注册，禁止跑到达标为止。OG1 线收线；外调链归 T-31/T-32 波次推进（本批=T-31 deliverable-5 兑现）。
