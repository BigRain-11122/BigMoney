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
