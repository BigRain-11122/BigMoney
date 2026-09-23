# CTA_P1 · C 层期货 CTA 策略 P1 海选 · 预注册（跑前冻结）

> 按 research/PREREG_TEMPLATE.md 起草。**本件 commit 即冻结**；跑后只许回填 §7，禁改判据禁重跑。
> 状态：**SPEC FROZEN 2026-09-24 06:45（bm-a round 49），未跑**——实现轮另行认领（F-04），批报告须引用本 sha。

## §0 批件身份【跑前】

- 批名：CTA_P1（期货主力连续 9 品种时间序列策略海选）。
- **批内格数=68**：候选 16（8 信号族 × 2 评估制式）＋K=50 同面板随机 null＋被动基线 2。每格计入 N_eff（prev=2858 → 冻结预期 2926）。
- 认领：F-04 先行=MSG-20260924-0646（fleet/inbox/，0645 撞号让位改号）；实现轮另发 MSG。部门归属：**dept:研究**（C 层新车道，PLAN §7 期货 CTA，GM 署名 O-1620）。
- 合法性链：O-1620 期货 CTA 已批 → R47 数据门审计 PASS（9/9 探针深度，sina 主力连续）→ R48 全量拉取器落地（data/futures_daily/ 9 CSV，cutoff 2026-09-23，bit-exact 对探针）。
- 算力预算：9 品种 × ~2.4k bars × 68 格 ≈ 2-3min 串行，无需 parallel_runner；批报告必带 audit 段（compute_audit，无 audit 段不入账本）。

## §1 α 机制段【D6】

- [x] **行为偏差（主）**：反应不足/锚定——新信息（供需/政策/资金流）在期货价格中缓慢扩散，价格呈趋势而非即时跳均衡；代价支付方=追涨杀跌的散户（RB/SC 商品品种散户主导尤甚）与杠杆过拟合交易者（保证金制度下爆仓强平**放大**而非打断趋势）。
- [ ] 风险溢价（次，趋势策略的 crisis-alpha 期权属性非本批主张）。
- **同族相关性准入【实现轮跑后必填】**：新函数与在册 6 员（VOLATILITY/COMPOSITE×2/ENGULF/NEEDLE/DROUGHT）＋同批全部函数逐对 max|corr|（日收益口径，sleeve-tag 先例）；≥0.7 拒收。跑前预注：股指期货四品种（IF/IC/IH/IM）=core48 β 变体（R47 §⑥ 提示），与 COMPOSITE-CE 双员相关性风险最高；但 CTA 双向（±1）＋空仓中间态＋商品/国债腿过半数，β 耦合结构上低于纯多头 ETF 员——以实测为准，逐对清单入批报告。

## §2 数据与面板【跑前探针事实】

- 宇宙：**9 品种主力连续**（data/futures_daily/{IF,IC,IH,IM,T,TF,RB,AU,SC}.csv，R48 update_futures.py 产物，sina 同源、append-only、overlap 四价比对过）。
- **窗口裁定（跑前定案）**：主面板=**公共起点 2017-01-17**（IF/IC/IH/T/TF/RB/AU 同窗在场；SC 2018-03-26、IM 2022-07-22 上市后 NaN→数据进入=合法结构洞，warmup 自适应）；AU（2008-01-09 起）/RB（2009-03-27 起）深史**不入主判据**，仅作单品种描述性报告列（入判据的窗口异质性会使 pooled 口径复杂化，弃深史保内部一致）。面板终点=**evidence_cutoff=2026-09-23**（数据末 bar；结果 JSON 顶层必须带 `science_gates.cutoff_meta("2026-09-23")`）。
- **信号输入裁定：OHLCV 五列 only**——oi/settle 列覆盖参差（实证：IF oi 2019-04-25 起才非零 1801/2352 行、IF settle 全 0；RB oi/settle 全史在），禁入信号输入（防覆盖期偏差/幸存者结构），仅作披露元数据。
- 数据完备门（不过禁跑批）：①9/9 品种文件在场且末 bar=evidence_cutoff；②列内 NaN 洞=0（上市前缺席不算洞）；③OHLCV 无负值；④逐品种行数/首末 bar 披露进 audit 段。
- **roll-gap 裁定（V0 直用）**：主力连续价在换月日含合约价差跳空=**伪收益源**（真实交易者同时平旧开新不承受该跳空）。V0=**原始价直用、不平滑、不掩蔽**——候选/null/被动全同面板对称注入 → 相对判据（vs null 带、vs 被动+0.10）内部有效；绝对水平（年化/Sharpe）受跳空噪声污染**如实披露**。敏感性报告列=剔除「|open/prev_close−1|>3×60d 滚动 std」日的变体（描述性列，非判据）。**G2 注册前置数据债条款：任何幸存者进 G2 必须拉分合约数据精确标注 roll 日并做换月平移复权复跑，禁带 V0 跳空噪声注册**（M0923 拼接算法=持仓量最大 roll+换月价差平移，参照件在库）。

## §3 方法学【跑前冻结】

- **信号族（时间序列制，非横截面；每品种独立计算；冻结参数）**：
  1. `tsmom_120`：120d 累计收益>0 → +1，<0 → −1，否则 0
  2. `tsmom_60`：同上 h=60
  3. `tsmom_252`：同上 h=252
  4. `donchian_55_20`：55d 通道突破入场 / 20d 反向通道退出（state 型 ±1/0）
  5. `dual_ma_10_60`：金叉 +1 / 死叉 −1（state 型）
  6. `triple_ma_5_20_60`：三线同多 +1 / 同空 −1（NSP1 判负族迁移探针）
  7. `breakout_20`：20d 高点突破 +1 / 20d 低点破位 −1 / 区间内 0
  8. `vol_target_tsmom_60`：tsmom_60 方向 × (1% 目标日波 ÷ 60d 实波) 权重上限 [−1,+1]（连续权重唯一格）
  - **评估制式 2 档**：`daily`（日频评估调仓）与 `r20`（信号每 20d 冻结评估，持有期内仓位不变）→ 8×2=**16 候选格**。
- **执行语义（M0923 futures_backtest.py 移植适配）**：T 信号 → T+1 开盘调仓；**T+0 双向**（同日可开可平）；手数=带符号整数；**保证金份额语义**：单品种目标保证金份额=等权 1/n_alive×权益，手数=份额÷(乘数×开盘价×保证金率)；单品种保证金份额 ≤20% 权益（max_etf_position_pct 红线对应纪律，M0923 同款）；Σ|手数|×乘数×价×保证金率 ≤ 上日权益（超限按占用最大品种逐手缩减）。
- **涨跌停近似（V1 简化）**：开盘触及昨收±品种涨跌幅（FUT_LIMITS 表，M0923 同源）→ 当日不开新仓（平仓始终允许）。
- **闲置现金 V0=计 0 利**（保守；保证金占用仅 10-15% 权益，85%+ 现金 0 利压低全员 Sharpe=对称保守；GC001 逆回购腿=G2 深化项，M0923 全史利率库在库）。
- null 对照：K=50 同面板随机信号（每 20d 重抽样、存活品种等概率三态 ±1/0），**seed=SEED_REGISTRY["cta_p1"]=50_000（50_000+k；冻结前已查空闲并登记入册）**；同 seed 双跑逐位确定性=硬门。
- 被动基线 2：`passive_long_r20`（全存活品种等保证金 long-only、20d 再平衡）＋`passive_long_monthly`（月度再平衡）。
- **成本口径**：期货专用=fee_lot（M0923 FUT_UNIVERSE 2026-09 交易所公示近似：IF 27.6 / IC 34.6 / IM 36.8 / IH 26.0 / T 4.2 / TF 3.7 / RB 4.3 / AU 10.1 / SC 20.0 元/手）＋滑点 1 最小变动价位/边。**跑前核验门**：fee_lot/乘数/保证金率/涨跌幅对照交易所现值核验，偏差>30% → 冻结为核验值＋如实披露（不中止批）；×2 成本压测=G2 条款（本批报告列 ×2 信息列）。
- 引擎载体：**新模块 engine/futures_runner.py**（M0923 futures_backtest.py 移植适配 BigMoney 面板约定＋audit 段＋账本接线）；**现有 engine/backtester.py 零改动**（O-2250 加性铁律：ETF 域逐字节不动）。
- 账本：`science_gates.append_ledger("cta_p1", 68, "results/shortline_cta_p1.json", evidence_cutoff="2026-09-23")`（dict schema 唯一禁手抄 prev）。

## §4 判据【跑前写死】

- **G1' v2 = `science_gates.g1_prime_v2(...)`**：全期 Sharpe > skill_line_v2 **且** 平稳 bootstrap CI 下界>0 **且** entries≥30（F6 双口径）。skill_line_v2=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))——**期货域自有 null 池+被动**，禁跨域套用 core48 0.4004/0.3521（LFC 金池 1.285 / 股票域 0.561 先例）。批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（原始收益 deflated_sharpe_ratio）**且** 家族 PBO≤0.25（CSCV 8 块；同族网格=双制式 2 格/族，g25_retro 先例）；缺输入=诚实拒收。
- 描述性条款（批级披露不替代 v2 门）：年化>0；IS2 段（2025+ 降格段，D2 禁再称样本外）双正；回撤≥-35%；无崩年；×2 成本信息列；逐年稳定。
- 附加披露条款（域特性）：per-variety 归因（9 品种各自贡献；股指腿 vs 商品/国债腿分账）；roll-gap 敏感性列；闲置现金摊薄披露。

## §5 跑前预测【写死，跑后对账】

1. null 带：K=50 随机 ±1/0 双向信号 pooled 全期 Sharpe p95 预计 **0.3-0.8**（双向三态使日收益波动低于股票域单边随机；85%+ 闲置现金 0 利进一步摊薄——全员同摊薄=内部一致）。
2. 被动 long-only 等保证金 Sharpe 预计 **0.2-0.6**（股指期货 β 漂移为主、商品/国债中性拖累）。
3. 幸存者族排序预判：tsmom_120/252（低频低成本）> donchian_55_20 > tsmom_60/vol_target > dual_ma > breakout_20 > triple_ma（ETF 域 G2_NSP1 窄带证据迁移弱预判）。
4. 评估制式：r20 普遍优于 daily（成本弹性谱系推论：日频 churn 死于 fee+滑点；J14/J15 一脉）。
5. ×2 成本对高换手格深负；tsmom_252@r20 存活机会最大。
6. D6 相关性预判：不触 0.7 拒收线，但 IF/IC/IH/IM 腿与 COMPOSITE-CE 员 |corr| 若 ≥0.5 须品种级归因披露（股指腿剥离后商品/国债腿独立评估）。
7. 幸存者数预测 **0-2**（N_eff 已 2926 深度使 D1 校正线严苛；期货域 null 带未知先验）。

## §6 产物【跑前声明】

- scripts/cta_p1_screen.py（探针先行纪律：实现轮先 gates 后 run；含 selftest 子命令离线）
- engine/futures_runner.py（新模块，ETF 引擎零改动）
- results/shortline_cta_p1.json（顶层 evidence_cutoff + audit 段 + verdicts + null_pool + passives + per-variety 归因 + prereg_sha256_at_run）
- research/cta_p1_results.csv（68 行全列）＋本件 §7 回填

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（实现轮回填；一次定稿；工程修复重跑须双跑留痕如实记账）

## §8 批后复盘【s7-T 必填】

- 预测对账（§5 逐条）＋gate_attrition.json 条目（measurement 型）＋判线当批读数全披露＋D6 同族逐对清单。

---

## 实现轮前置门（gate list，跑批前全过才许 run）

- G0：smoke 23/23
- G1：futures_runner 移植自检=合成面板确定性双跑逐位＋手数/保证金预算/涨跌停不开新仓/双向平仓 单元断言（M0923 语义逐条）
- G2：tick/fee/乘数/保证金率核验门（交易所现值对照，>30% 偏差冻结核验值）
- G3：数据完备门（§2 四条）
- G4：null/被动确定性（同 seed 双跑逐位）
- 审计段必带（compute_audit run 嵌批内）
