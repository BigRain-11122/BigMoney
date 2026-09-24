# T28_STABLE_PROFIT · 当前市场稳定盈利报告批（预注册·跑前冻结）

> 票：T-2026-09-24-28-P1（CEO 令 O-20260924-1712 北极星收敛票）· 认领 r89 bm-a（F-04 MSG-20260924-1947 先行）。
> 模板：research/PREREG_TEMPLATE.md · 判据库 science_gates（禁手抄判线）· 权威 research/BACKTEST_SCIENCE.md。
> 本批=收敛装配批（非新信号搜索）：一切成员面均已入账（T-22 P5C/T-27/o1600），本批产出=北极星报告的冻结判据面。

## §0 批件身份

- 批名 T28_STABLE_PROFIT；批内判断格=20 个聚合判断单元（W-CUR {x1,x2}=2；W-SEG 3 段类×{x1,x2}=6；W-GRID {deep,legacy}×{6m,12m,24m}×{base,x2}=12；聚合口径=W-GRID 各单元的 per-cell N 沿用 P5C 已计账本不重复计数，披露 per-cell N）。
- 部门归属：dept:研究+组合+风控 joint（票面）；执行 bm-a r89。
- 算力预算：leg-1（W-CUR/W-SEG）=member_run+t27 原语复用，实测 core48 向量化亚秒/格（R88 坑律①）→ 分钟级；W-GRID=finalize 后纯装配算术（分钟级）；批件后续如需大规模重放再后台化。无 >10min 批件。
- 依赖时序：W-GRID 物理依赖=T-22 finalize（腿L cells 传输在途，MSG-20260924-1946 已请 bm-b；O-1730 暂缓条款留痕）；W-CUR/W-SEG 无依赖即跑。

## §1 α 机制段（D6）

- [x] **风险溢价**：B_MAXDIV=已过门成员风险溢价源的分散化聚合（max-div 权重=溢价来源分散）；谁付代价=各成员机制段原判（T-27 逐员在案），本批不主张新溢价源。
- **本批零新信号族**：D6 同族 corr 检查对装配批不适用（无新函数入册）；blend-vs-IV6 双胎门已由 T-27 跑（twin_gate_vs_iv6 在 results/portfolio_blend_tournament.json）。

## §2 数据与面板

- 宇宙：core48（白名单在册）；evidence_cutoff=**2026-09-23**（本地 bars cutoff；o1600 面同界 end=09-23）；cutoff 后新 bar 禁回流。
- 窗口冻结：
  - **W-CUR**=2026-01-05→2026-09-23（当前 ORANGE regime 窗；起点=2026 首个交易日 bar，o1600/MSG-1630 先例）。
  - **W-SEG**=v3 政体状态段（regime_calibration v3 原语 import-replay 现算无缓存·T-21 语义；段类 GREEN/YELLOW/ORANGE+RED 全披露，CEO 面映射 bull/chop/bear）。
  - **W-GRID**=P5C 虚拟时点格（deep 1506 起点+legacy {1253,1127,875}；窗 {6m=126,12m=252,24m=504}）。
- 数据完备门：W-GRID 起跑前普查漂移门（活面板复现冻结计数即跑，r105 坑律㊀）；逐符号 first_valid_index 后零 NaN 契约（R88 坑律②）；cutoff_meta 字段必带。

## §3 方法学

- 权重冻结：B_MAXDIV 权重向量=results/portfolio_blend_tournament.json `weights["B_MAXDIV"]`（跑前 sha256 记入结果件；x2 面权重同源）。
- 装配：成员 sleeve 日收益序列×冻结权重日合成（t27 权重矩阵原语复用）；成本面 {x1=V1 legacy 13bp×2, x2=CostPatch(2.0) 单源}；guard 面=REGIME_GUARD v3 shadow（决策日状态门控次一执行日·T-21 三重门语义；**enforce 面不在本批跑**——10-01 日期门自动激活后由首个 paper 跑产出，本报告届时增量补面，勿手改日期门）。
- 基线：被动 EW-48（o1600/P-5 口径）；**零新 null**（无新信号族；beat-passive=冻结对照）。
- 账本：`science_gates.append_ledger('T28_STABLE_PROFIT', 20, 'current_market_stable_profit.json', evidence_cutoff=...)`（聚合口径注记）。

## §4 判据（跑前写死·CEO 可读）

- **J1 当前窗盈利**：B_MAXDIV W-CUR x1 净收益>0 **且** |maxDD|≤5%（IV6 -2.4% 历史锚）。
- **J2 x2 成本存活**：W-CUR x2 净收益>0（T-27 x2_margin +0.2137 锚）。
- **J3 政体段稳定**：各 v3 段类（bull/chop/bear 三映射面）累计净贡献≥-5%（「non-deeply-negative」操作化=绑定 J1 同界；全段类披露，任一破界=J3 FAIL）。
- **J4 大规模时点通过率**：blend beat-passive 率 primary=12m 面≥0.70（P-5/P-5B 冻结口径）；{6m,24m} 披露不判；逐员率全披露（P5C 数据）。
- **J5 D7 四必报**：OOS 笔数/覆盖年数/独立政体窗数/CI 宽度（逐员+blend）。
- 判定规则：J1-J4 全过=报告判定 STABLE-PROFIT-DEMONSTRATED；任一 FAIL=诚实负判定全披露（报告照交，禁跑到达标为止）。
- 报告边界（诚实条款）：盈利=成本后净额（x1+x2 双面）；稳定=政体段+窗族稳健非单窗运气；B_MAXDIV 采纳**不接线**（GM 批准+7 天否决窗内零接线，T-27 §7 条款——本报告=证据面非生产面）。

## §5 跑前预测（跑后对账）

1. J1 PASS（o1600 六员全跑赢被动 EW-48 -5.82%，blend dd 历史面 -1.63% 远于 5% 界内）。
2. J2 边缘 PASS（x2_margin 正但 W-CUR 窗更短更波动，余量收窄）。
3. J3 风险点：bear 段（2021-2024 面）最可能贴界，预测至少一段类接近 -5% 界但不过。
4. J4 最不确定：成员级 P-5/P-5B pooled 0.6467/0.6067 FAIL 先例 → 分散化或抬 blend 但 0.70 高栏；预测 12m 面落在 0.60-0.75 带（~50/50）。
5. 权重复用零重训 → 装配确定性双跑逐字节等（t27 先例）。

## §6 产物

- scripts/t28_stable_profit.py（复用 member_run/t27 权重矩阵/regime_calibration 原语·零新引擎码）+ selftest 子命令；
- results/current_market_stable_profit.json（顶层 evidence_cutoff+cutoff_meta）；
- 一页 CEO 报告 research/T28_STABLE_PROFIT_REPORT.md（判定/收益/dd/段稳健/验证链五段）；
- 本件 §7/§8 跑后回填。

## §7 跑后实证（跑前为空——写数字即造假）

（占位）

## §8 批后复盘（s7-T）

（占位；gate_attrition 追加行+预测对账+轮报告回执）
