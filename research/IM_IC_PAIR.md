# IM_IC_PAIR — IM/IC 跨期贴水差价对（结构性 carry + 价差回归择时）预注册

> 按 research/PREREG_TEMPLATE.md 起草；判据权威=BACKTEST_SCIENCE.md v2；三铁律照旧（随机基线+N 记录+样本外盲）。
> 外源收割链：O-1721 常态线·T-45 wave-5·slice-7 深捕获（集思录 question/517161，439 回复全流）→ 本件=机制段成文与判据冻结。
> 跑前 commit 冻结（R139 bm-a）；跑后只许回填 §7/§8，禁改判据禁重跑。

## §0 批件身份【跑前冻结】

- 批名：IM_IC_PAIR（候选族 im_ic_basis 的首验批；futures-cta 臂 exploit 位继任候选）
- 批内格数（N_eff 计账）：**52** ＝ 2 候选（腿A 常开 carry ＋ 腿B 价差回归择时）＋ 50 随机 null；无被动格（对子面被动=空仓常数 0.0，见 §4）；×2/×3 成本信息列不计数（CTA_P2 先例）
- 认领：T-2026-09-25-45（bm-a lane，slice-8=本件冻结；slice-9=runner 接线与跑批）；**跑前 F-04 MSG 声明（IM_IC_PAIR 批执行认领）先于 run 子命令**
- 部门归属：dept:研究（C 层期货=O-1620 GM 已签 paper 域过闸制，CTA_P2 同款）
- 算力预算：52 格 × 2 品种面板，预估 <2min 单进程（CTA_P2 68 格×8 品种 61s 实测同构参照）；轮内直跑合法（light batch，workers=1，T33/GRID-P1 先例）；批报告必带 audit 段（无 audit 段不入账本）

## §1 α 机制段【D6 四选一】

- [x] **结构性**：股指期货对冲需求分层——IM（中证1000，中小盘量化中性盘对冲工具）结构性对冲压力高于 IC（中证500）→ IM 长期贴水系统性深于 IC → 多 IM 空 IC 每月移仓持续收敛贴水差（carry 腿）。**谁付出代价**=为中小盘空头风险支付更高对冲成本的中性盘（其隐含对冲需求刚性=收益来源）。价差极端负偏离入场+均值回归离场=择时增强副腿（社区量化：负偏 4% 触发、10 事件 80% 胜、均值 +1.6%、持仓 11.5 天；**反手侧 6 事件 0% 胜不交易**——不对称声明冻结）。
- 社区报数时变警示（借力三律·时变面）：「600 点/年」为历史窗口值，「2026-07 时点年化仅约 1.5%」同帖双人独立报数——**贴水差时变，本批全窗实证即为其可变性检验**。
- **同族相关性准入检查【必填·D6·实现轮先于跑数执行·XSTOCK_TILT 冻结法】**：2 候选格 vs 在册 28 员面（在册 6 交易员 VOLATILITY/COMPOSITE-CE-01/02/ENGULF/NEEDLE/DROUGHT ＋ PROSPECT 22 员）日收益序列 max|corr| 逐对列出（ew6_portfolio member_run 复用）；**max|corr| ≥ 0.7 → 拒收该格**。批内 2 格=异机制格（常开 carry vs 事件择时），批内相关由 G2 PBO 治理非 D6 拒收项（CTA_P2 先例）。预测带见 §5④（DNA 簇法，r153 教训）。

## §2 数据与面板【跑前探针事实】

- 宇宙：**IM/IC 双品种主力连续**（9 品种期货链子集，零数据扩容；fr.load_panel(varieties=["IM","IC"])）
- 窗口：**2022-07-22（IM 首 bar）→ evidence_cutoff 2026-09-24**（双 CSV 末日实核=2026-09-24，1015 行对齐窗）；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff="2026-09-24")`（缺字段=science_audit C2 VIOLATION）
- **2026-07 拥挤月在窗（已探针实证）**：IM/IC 各 23 行（07-01→07-31），社区级踩踏月（价差 −620 点极值+自报爆仓链）在本批窗内必受压测——见 §4 生存硬门
- 数据完备门（不过门禁跑批，CTA G3 同构）：双 CSV 在盘；末日 bar=cutoff；OHLC 无负值；窗内行数对齐（union 口径 NaN=未上市/未交易，IM 上市前窗自然截除）；2026-07 在窗行≥20；engine 自检 G1 + null 确定性 G4 均 PASS
- roll-gap V0 直用裁定沿用（CTA_P1 SS2）：主力连续原始价不平滑，候选/null 同面板对称注入=相对判据内部有效；**对 carry 机制此面语义正确**——移仓贴水差以连续价相对漂移显形
- 现货指数面（000852/000906）**不入本批**：v1 只做点位价差面（slice-7 裁定；基差分解/月差结构面=数据扩容门维持，EM 日线源属既有源面但非本批必需）

## §3 方法学【冻结】

- **腿A `carry_pair_always_on`**：1:1 手（双 mult=200）多 IM 空 IC 常开；月度移仓=主力连续面自然承载；收益=engine equity 路径（start_cash 满保证金口径，fr.run 同 CTA_P1 全套）；信号输入=OHLCV-only（CTA 冻结面）
- **腿B `spread_reversion_ma60`**：R(t)=IM_close(t)/IC_close(t)（t 收盘后可知，t+1 生效，零未来数据）。触发：R(t) ≤ MA60(R)(t)×(1−0.04)（**仅 lag 侧**；社区原语义=「相对落后 4% 触发、回归 0 离场」之正式化：对 60 日均值比负偏离 4%）。出场：R(t) ≥ MA60(R)(t) 或持仓≥60 交易日（时窗止损），先到先出；出场后才可再触发（不加仓）。**反手侧（R 领先）不交易**（社区 6 事件 0% 胜冻结）。参数 {MA60, 4%, 60d, 单侧} 冻结，禁网格（GRID-P1 0 幸存教训）
- null 对照：K=50 同构随机 null——对子作为单一资产处理，r20 再平衡节拍对子方向等概率 {+1 多IM空IC, 0 空仓, −1 反手}（CTA_P1 build_null_weights 对子版）；**新 seed 基 58_000**，登记 `science_gates.SEED_REGISTRY["im_ic_pair"]` 后才跑
- 成本口径：**V1 legacy 期货域**（per-lot 费＋1 tick 滑点/边，FUT_META 冻结常数，G2 验证门同 CTA_P1）；×2/×3 信息列照跑（律 8 参照）
- 账本：`science_gates.append_ledger("im_ic_pair", 52, "results/shortline_im_ic_pair.json", evidence_cutoff="2026-09-24")`（dict schema 单源，禁手抄 prev）

## §4 判据【跑前写死，禁看结果调线】

- **G1' v2** ＝ `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=52, pool="im_ic_pair", n_trades, n_entries)`：全期 Sharpe > skill_line_v2 且 bootstrap CI 下界>0 且 entries≥30（F6 双口径，entries_ok 为准）。
  - **池分支（加性扩池·跑前接线）**：`passive_baseline("im_ic_pair")` ＝ **0.0**——对子面（两腿等名义均值零价差仓）唯一被动=空仓，常数 0.0 冻结注记，禁跨池借用（CTA 律）；passive_term=0.10 地板。null 池=本批 50 null 族（null_pool 参数，P4_EXT_TILT 加法）。N_eff=ledger_head（冻结时点 60828）+52＝60880（跑时活读账本头，禁手抄）。
- **G2 注册资格 v2** ＝ `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`：DSR≥0.95（原始收益跑，禁 dsr_from_stats）＋家族 PBO≤0.25（CSCV；2 格=信息性披露，单格族 PBO 不定义照 CTA_P2 同判）；缺输入=诚实拒收。
- **2026-07 拥挤月生存硬门【本族特有·冻结】**：每候选在 ×2 成本口径下 2026-07 单月收益率单列披露；**< −25%（满保证金击穿级界，社区爆仓案例保守界）→ 注册资格拒收**（G2 前置否决，判据性条款非描述性）。
- 描述性条款批级披露照旧（年化>0/IS2 双正/dd≥−35%/无崩年/成本压测逐年稳定）；满保证金 dd 域特性条款照 CTA_P1 全灭口径如实披露不豁免。
- 跑后禁调门槛禁重跑；工程修复重跑须双跑留痕；确定性引擎产物写 bug 的合法重执行口径≠结果重跑。

## §5 跑前预测【写死于跑前】

1. **判线量级**：μ_null≈0（对子方向对称注入），σ_null 预测 **0.25-0.45**（单对子窄面，CTA 8 品种 0.29-0.36 参照上抬）；null_term=μ+σ×√(2·ln 60880)≈σ×**4.694**（冻结时点实算）→ **判线预测 [1.2, 2.1]**（CTA 域 1.4278 同族量级或更高=全项目最高线族）；**passer 预测 0-1，0 为基线预期**——本批定位=机制证据面收线（carry 时变性+拥挤月生存+D6 相关面），非注册猎取。
2. **腿A carry**：全期 Sharpe 预测 **[−0.2, +0.8]**（2022-07→2026-09 窗含 2024-09 脉冲与 2026-07 拥挤月两极端，方差主导）；年化价差漂移预测 **+80~+500 点**（社区 600 点/年=窗口值、1.5% 年化=现值，双报数之界内取带，时变主张的实证检验即本批）。
3. **腿B 择时**：触发事件数预测 **[8, 40]**（社区 10 事件参照，正式化口径下事件密度未知）；entries≥30 门**不确定**（<30 则 F6 拒）；事件胜率预测 **50-85%**（社区 80% 单侧参照、样本极小）；持仓期分布预测 10-60 日。
4. **D6 预测带 [0.02, 0.30]**：DNA 簇法（r153 教训：按 DNA 簇不按资产面估）——本族=跨资产+carry/趋势 DNA，在册 28 员全为 A 股 ETF 日线反转/波动簇（结构远），唯 RSRS-CE 趋势簇机制近邻 → 带上限放宽至 0.30；**≥0.7 拒收全过为基线预期**。
5. **极端日先验（D-20260925-01①(c)）**：窗内极端形态三例——①2024-02 微盘流动性危机（IM 连续跌停带）；②2024-09-24 政策脉冲（IM 巨幅高开/涨停带）；③**2026-07 拥挤月**（价差 −620 点极值、社区自报日内 610-620 点级波动）。对子单日波动极值先验 **500-700 点（≈名义 8-12%）**——若未来对本面设任何 max 类硬界，须≥此量级或配危机日感知/豁免单列（硬界三件套律）；本批自身无数据腐坏检测类 max 硬界（G3 完备门为分布/对齐口径）。
6. **成本信息列**：×2 预测——腿A 近无损（|Δ|<0.05，月度移仓低换手）；腿B |Δ|<0.1（事件进出低频）。

## §6 产物

- `scripts/im_ic_pair.py`（复用 engine.futures_runner fr.run/FUT_META＋cta_p1_screen gates 范式＋ew6_portfolio member_run D6 面，**禁重写**；gates/run/selftest/status 子命令）
- `results/shortline_im_ic_pair.json`（顶层 evidence_cutoff＋audit 段＋prereg sha 双记）＋ `research/im_ic_pair_results.csv` ＋ `results/im_ic_pair_runs.jsonl`（checkpoint，行级 resume）
- `science_gates.py` 加性扩池：`SEED_REGISTRY["im_ic_pair"]=58_000` ＋ `passive_baseline` 分支 im_ic_pair（return 0.0 空仓注记）——跑前接线冻结 commit 内完成
- `results/gate_attrition.json` 追加一行；`research/STRATEGY_LIBRARY.md` C 层行回写（futures-cta 臂候选面）

## §7 跑后实证【跑前必须为空——写数字即造假】

（跑后回填）

## §8 批后复盘【必填·s7-T】

（跑后回填：预测对账＋损耗账＋判线当批读数＋回执）
