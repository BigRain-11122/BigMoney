# STRATEGY_SCORECARD_CALIB — 交易员卡/组合卡首届分布校准预注册（T-2026-09-25-63 deliverable③·§8.5 校准律）

> 正典：firm/STRATEGY_EVALUATION.md v2.0 §8.5（「总分与权重带=首届对象分布校准后预注册再启用；校准前=读数卡」）。
> 性质：**校准程序预注册（跑前冻结）**——本件冻结校准批的程序与带构造规则；冻结 commit 后才可跑校准批；跑后只许回填 §7，禁改程序禁看结果调带（数据窥探红线同源 §1.3）。
> 输入：results/strategy_scorecard.json（三卡读数面，scripts/strategy_scorecard.py 产物）——**零新回测零引擎零账本增量**（校准=纯读数统计批）。

## §0 批件身份【跑前冻结】

- 批名：`SCORECARD_CALIB_P1`；性质=纯聚合统计批（读数分布+带构造），ledger +0、N_eff 无涉（零选择试验——带构造不选对象、只定标尺）。
- 首届对象（冻结）：
  - **交易员卡队列=28**：在册 6（COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01）+ PROSPECT 22（corps_roster prospect 面全列）；
  - **组合卡队列=7**：IV6、EW6、A_IV、B_MAXDIV、C_IVMOM、D_REGIME、E_EW。
- evidence_cutoff=跑批时 strategy_scorecard.json 输入源的最旧 cutoff（跑前实读登记，前向锁盒 D2）。

## §1 校准程序【冻结·五步】

1. **读数面物化**：从 results/strategy_scorecard.json 提取每对象每维度读数（含 ⬜ 未测态标记）。未测态计 0 分入分布（策略面 §1.5 未测零分先例），同时单独报**可用率**（tested 面占比）。
2. **分布披露**：逐维度报告首届队列分布（n/min/q25/median/q75/max + tested-n）；⬜ 面不进分位数分母、零分面进总分分布。
3. **权重带草案**（程序约束冻结，非数值冻结）：①纪律面=否决门**不占权重**（§8.2 恒 gate）；②单一维度权重 ≤50%（≥2 维呈报律 §8.1 的带面化）；③继承面（交易员卡）与质量面（组合卡）=主导维（建议带 35-45%，按分布离差收敛）；④其余面按分布区分度（q75-q25 跨度）分配余量；⑤一切数值=看到分布后一次定稿、冻结 commit 后**禁再调**。
4. **分级带构造规则（跑前写死）**：总分分级带按首届总分分布分位构造——**S ≥ p80、A ≥ p60、B ≥ p40、C 余**（分位法非手拍）；附加条件=硬否决面全过（§8.2）。带数值在校准批内一次算出并冻结。
5. **启用门**：校准批冻结（commit）→ 下一版 strategy_scorecard 输出交易员/组合卡总分与分级 → 10-31 首检消费。启用前任何总分排名面=违 §8.5。

## §2 边界与诚实条款【冻结】

- 校准批**不改变**策略面 v1.0 八维权重/分级（修订律保护·O-1823 在册）；本件只立交易员/组合卡两面。
- PROSPECT 未测面（纸盘/g25/分段证据）构造性 ⬜：其总分将结构性偏低=诚实呈现，禁以「样本不足」为由豁免或折算平均。
- 组合卡跨期面（T-28 J4）=在册诚实负结论（NOT-DEMONSTRATED）：校准读数如实继承负读数，禁美化。
- 校准批后若首届队列扩张（新注册/新组合）→ 带不重算（带冻结）；≥6 个月或队列翻倍时另开 v2 校准预注册。
- 禁未来数据：校准输入 cutoff 后新落账证据不回流本批。

## §3 跑前预测【≥3 条】

1. 交易员卡分布将呈**双团**：在册 6 员（全维 tested）vs PROSPECT 22 员（多数面 ⬜）——总分分布左尾厚（PROSPECT 零分堆积），p40 带或被 ⬜ 团压低；预测 median 总分落在 PROSPECT 团内。
2. 组合卡 7 员分布区分度主贡献=quality/x2 面（IV6/EW6/B_MAXDIV 高位团 vs A_IV/C_IVMOM/E_EW 低位团）。
3. 未测零分惯例下首届 S 带（p80）将主要由在册团独占；若 S 带含 PROSPECT=分布异常信号（校准批如实报告、不翻案）。

## §4 产物

- 校准 runner：scripts/strategy_scorecard.py 后续版本新增 `calibrate` 子命令（读 §0 输入→§1 五步→写 results/strategy_scorecard_calib.json）；
- 结果件：results/strategy_scorecard_calib.json（分布全表+权重带数值+分级带数值+可用率+evidence_cutoff）；
- 本件 §7 回填一次定稿。

## §5 审计

- 校准批审计段必含：输入 strategy_scorecard.json 的 generated/cutoff、队列计数（28/7 实数）、⬜ 面计数、elapsed、零回测声明。

## §6 修订

- 本件修订=预注册+7 天否决窗（charter §1.3）；带数值修订=v2 校准批（§2 条件触发）。

## §7 跑后实证【跑前必须为空——写数字即造假】

（校准批跑后一次回填：分布表+权重带数值+分级带数值+对账。）

**SCORECARD_CALIB_P1 实跑回填（2026-09-25 bm-a R181·一次定稿）**——runner=scripts/strategy_scorecard.py `calibrate`；产物=results/strategy_scorecard_calib.json；input strategy_scorecard.json generated=2026-09-25T18:08:47；evidence_cutoff=**2026-09-22**（最旧源=portfolio_blend_tournament/iv6/ew6；前向锁盒 D2 登记）；elapsed 0.0s；零新回测零引擎 ledger+0。

**分布（tested 面分位；availability=tested/队列）**：

- 交易员 28 员（在册 6+PROSPECT 22）：
  | 面 | tested-n | min | q25 | median | q75 | max | availability |
  |---|---|---|---|---|---|---|---|
  | inherited | 28 | 18.8 | 23.18 | 29.55 | 44.33 | 87.0 | 1.00 |
  | live_paper | 6 | 29.9 | 29.92 | 30.0 | 30.0 | 30.0 | 0.214 |
  | progress | 6 | 0.0 | 0.0 | 0.0 | 0.0 | 20.0 | 0.214 |
  | profile | 6 | 82.7 | 83.08 | 83.55 | 85.52 | 88.3 | 0.214 |
- 组合 7 员（IV6/EW6+锦标赛 5 法）：
  | 面 | tested-n | min | q25 | median | q75 | max | availability |
  |---|---|---|---|---|---|---|---|
  | quality | 7 | 29.8 | 36.1 | 45.8 | 52.35 | 59.3 | 1.00 |
  | cost | 7 | 3.0 | 5.5 | 17.2 | 24.85 | 58.4 | 1.00 |
  | segment_coverage | 5 | 100 | 100 | 100 | 100 | 100 | 0.714 |
  | cross_period_j4 | 7 | 0 | 0 | 0 | 0 | 0 | 1.00 |
  | marginal | 7 | 0.0 | 0.0 | 0.0 | 10.0 | 20.0 | 1.00 |
  | statistical | 7 | 86.0 | 86.85 | 87.6 | 87.6 | 87.6 | 1.00 |

**权重带数值（冻结）**：交易员 inherited=0.40、profile=0.50、live_paper=0.10、progress=0.00（跨度分配：profile 2.44 拿满余量触 0.50 帽、超额按 live 跨度归 live；progress q75-q25=0 → 零权重如实）；组合 quality=0.40、cost=0.3857、marginal=0.1993、statistical=0.015、segment_coverage=0、cross_period_j4=0（后两面全队列恒 0=零区分度如实归零）。单维 ≤50% 帽全过；纪律面=否决门零权重（§8.2）。

**分级带数值（p80/p60/p40 分位法·冻结）**：交易员 S≥50.6、A≥14.4、B≥10.4、C 余；组合 S≥38.0、A≥30.4、B≥22.0、C 余。首届落带：交易员 S=6（全部在册）/A=5（PROS-DUCK-01、DUCK-CE、OVB-01、OVB-CE、BBS-01）/B=6/C=11；组合 S=2（B_MAXDIV 46.2、IV6 39.4）/A=1（EW6）/B=1（D_REGIME）/C=3（C_IVMOM、A_IV、E_EW）。纪律否决命中=0。

**§3 预测对账（3/3 成立·不翻案）**：①双团实证=median 总分 11.8 落 PROSPECT 团内、在册团 71.8-79.7 与 PROSPECT 团 7.5-18.7 完全分离，S 带 0 PROSPECT（无异常旗）；②组合区分度 top2 跨度面=cost 19.35+quality 16.25（预测 quality/x2 主贡献成立）；③S 带在册独占成立。诚实注记：progress 面零权重=首届在册 g25 全 fail 的结构性零区分度（非门禁松动，g25/hr 权威不变）；组合 j4 面全 0=T-28 NOT-DEMONSTRATED 诚实负结论继承（§2 禁美化实证）。

**run-once 律**：本节数值随本次 commit 冻结；队列扩张不重算带（§2）；≥6 个月或队列翻倍才许 v2 校准预注册（§6）。启用门下一版=strategy_scorecard run() 读本批冻结权重/带输出总分分级。
