# P2 判据基线 nulls K 扩容预注册（P2-NULL-CALIB-EXT-K2200）v1.0

> 2026-09-30 21:2x · bm-c r287 冻结（跑前盲写——本节写数时 canon v2 mu/sigma 数值未读取）。
> 触发=CEO 直令 **O-20260930-2054 §一**（总动员即刻生效·「判据基线扩容（nulls K 值提升）」枚举项）+ O-20260930-1858 §二.e（科学面投资）·CEO 直令对枚举项即刻生效（REEVAL-18 才候 10-03 外审·本批非其面）。
> 设计=**NULL_CALIBRATION.md v1.0（2026-09-23 跑前冻结）逐字继承 + v2 固定引擎律（RW-1..4）**，唯一增量=新种子带扩容。零新方法学。

## §0 批件身份

- 批名：**P2-NULL-CALIB-EXT-K2200**（skill_line_v2 注册判据 null 池扩容）；性质=**判据基线测量批**（非策略臂·零策略格·零 gate_attrition 行）；
- dept:研究（判据基线线）；车道=**lane-free/ANY**（worker_class=self-contained：in-repo core48 裸码面板 data/daily/<6位码>.csv 全机在位）；
- 算力预算：2,200 跑 × ~0.54s ≈ 20-25min 串行 → **池提交**（O-2100 执行面分离·>5min 禁轮内内联）；4 分片 × ~5.5min（A 500+B 50/片）·workers:1 BelowNormal/片·确定性单趟幂等（重跑字节恒等）；
- 任务引用：CEO O-20260930-2054 + O-20260930-1858 §二.e（fleet\tasks 无 open 票=CEO 直令即授权面）。

## §1 科学问题与 α 机制段（D6 面=测量非策略）

- **校准问题**：现行注册判据线 skill_line_v2 = max(passive+0.10, mu_null + sigma_null·√(2·ln N_eff))，其 mu/sigma 来自 **K=120** 的 canon null 池（p2_calibration_v2.json：A 族 100+B 族 20）——σ 抽样噪声 ≈ σ/√(2K) ≈ 6.5%（相对），N_eff≈34 万量级下 √(2 ln N_eff)≈5.05 的放大器把该噪声直接灌入判据线。**K 提升到 K=2,320** 后 σ 噪声 ≈1.5%，判据线不确定性收窄 4×。
- 意义性三验（O-1901/O-1820）：①确定性产出=扩容池 mu/sigma/线移量（无隐藏失败面）②**指名消费面**=skill_line_v2/G1'v2 全部未来预注册判据节 + canon-flip 治理提案（本批不擅自翻 canon·§4）③判负处置=无策略格可判负；若实测 |Δσ|>2·SE（K=120 噪声界）＝canon σ 有偏的**发现**（线不确定性披露）→ flip 提案 P0 消费；若 |Δ|≤2·SE＝稳定性证据。两向皆合法产出，禁粉饰。
- 反重复核查：仓内 rg `skill_line|null_sharpes|p2_calibration` 全量扫描——canon 件仅 v1（09-23）+v2（RW-6 09-30 15:11 bm-a 机读 bm-a）两跑，无任何 K 扩容批次在册/在池（r287 扫池 142 条零同面）。

## §2 数据与面板（G-ANCHOR-FACE）

- 宇宙=core48 裸码（v1.load_core min_listing_days=60 口径），**48 员 fail-closed 断言**；
- 窗口=**2020-01-02 .. 2026-09-22**（evidence_cutoff=2026-09-22 冻结同窗律——canon 池同窗可比性；RW-2 截断：面板新 bar（>cutoff）一律硬截断不回流）；探针实证本地面板尾=cutoff 后（2026-09-29/30）→截断腿必须生效（selftest+in-runner 双断言）；
- 成本=FeeSchedule 单源 Face A（commission+handling+supervision+slippage_a，RW-3 律）；引擎=in-repo run_backtest（v1.run_one 适配器逐字复用·零重实现）。

## §3 方法学（冻结参数·零新方法）

- **A 族扩展 2,000 跑**：j=0..1999，rng seed=**10_100+j**（带 10_100..12_099），p_entry=BASELINE_P[(j//50)%2]∈{0.02,0.05}（50 种子块交替=v1 图案续位），退出=纯引擎规则（exit=False），入场/执行/成本/切分全同 v1；
- **B 族扩展 200 跑**（出场对称化配对差分）：j=0..199，入场 rng=10_100+j（**与 A-ext[j] 同入场矩阵**=v1 配对语义续位），随机退出 rng=**20_100+j**（带 20_100..20_299）p_exit=0.05/日；
- C 族被动基线**不重跑**（v2 注记逐字：构造上与 v2 family C 恒等）；
- 种子纪律：v1 在用带=10_000..10_099/20_000..20_019；ext 带与其不相交且与 SEED_REGISTRY 全 148 整数值零冲突（selftest 断言·r476 种子撞号坑律）；探针种子=95_000/95_001 带外（40_000=new_signal_p1 在册——首次 selftest 实弹拦截后改号）；
- 分片=4×连续切片（A 500+B 50/片·selftest 切片数学腿）；幂等=分片重跑整文件覆写（FACEB 单趟先例）。

## §4 判读表（跑前写死·对号）

| 假说 | 判读 | 处置（预先承诺） |
|---|---|---|
| **H-K1 噪声界内** | 扩容池 Δmu/Δσ 落 K=120 抽样噪声 ±2·SE 内（SE_mu=σ/√120·SE_σ=σ/√238） | canon 稳定性证据入档；flip 提案降优先 |
| **H-K2 σ 实移** | \|Δσ\|>2·SE（小样本 σ 估计有偏——右尾 p95 低估预期） | canon-flip 治理提案 P0（旧 vs 新线数值双列）交 GM/后续窗裁决；**本批不翻 canon** |
| **H-K3 线移量** | 线移 \|Δline\|@同 n_eff（v2 归因律：两侧同 n_eff） | 移量>0.05 Sharpe=判据线实质漂移披露（任何在飞未判批的判据读数面注记义务） |

- **canon 不动铁律**：本批只产 p2_calibration_v2_ext.json（独立件）；p2_calibration{,_v2}.json 零触碰（selftest 路径安全腿）；null_sharpes() 仍读 120 值 canon——**canon-flip=后续治理动作**，须以本批 old-vs-new 数值为证据另窗提案，本批无翻线权。
- 账本：finalize 腿 append_ledger **+2,200**（新种子 null 试验=FUSION_GRID null 计入先例；r259 重执行单计律不适用——本批新种子非重执行）；finalize 前同 n_eff 双线读数（先读数后记账·防 n_eff 错位）。

## §5 跑前预测（写死于烧前·盲写）

1. **P1 mu**：ext 池 mu 与 canon mu 差 ≤0.03（|SE_mu|×2≈0.03 量级·同分布假设）；
2. **P2 sigma**：ext 池 σ 与 canon σ 差在 ±20% 内（SE_σ×2 界）；方向不定（小样本低估或高估皆可能·如实报）；
3. **P3 线移**：|Δline|@n_eff≈34 万 <0.05 Sharpe（H-K1 预期主面）；
4. **P4 右尾**：A 族 ext p95 ≥ canon p95（小样本 p95 低估方向先验——v1 P1 实测 p95≈0.5 史锚旁证）；
5. **P5 配对差分**：B-ext 配对差分（A 引擎退出 − B 随机退出）中位 >0（v1 H2 退出机器贡献结论复现方向）。

## §6 产物

- runner：`scripts/p2_null_calibration_ext.py`（--shard/--nshards · finalize · probe · selftest 四态）；探针件=results/_p2cal_ext_probe.json（95_000/95_501 带外 2 跑·设计验证非试验·账本+0）；
- 分片件：results/p2cal_ext/shard-{0..3}-of-4.json（~180KB/片·git 传输合规）；
- 终件：results/p2_calibration_v2_ext.json（顶层 evidence_cutoff + science_gates.cutoff_meta C2 合法键·含 ledger 回执）；
- §7/§8 跑后回填=烧批落地轮（收割留痕律·批不自翻）。

## §7 跑后实证【r289 bm-c 回填·finalize 落地窗】

**烧批记录**（4/4 分片·确定性单趟）：S0=autofill 车道（产物 21:31:05 落·r288 崩轮抢救 commit be5bf628a 上链）；S1=pool_worker 457.0s exit 0（21:17:16→21:24:53）；S2=autofill tick 认领 21:31:36（commit 1da5d486e）→产物 21:42:53；S3=pool_worker 636.3s exit 0（21:32:18→21:42:54·claim 11a13e876/close 36406f24b outcome=ok）。合计 A-ext 2,000 + B-ext 200 = **2,200 跑**，分片件 4×~319KB 全落盘。

**finalize 腿**（r289 bm-c·merge-only 秒级）：首跑撞 latent bug=`nshards_seen` 收集 `(shard, nshards)` 元组致同 nshards 恒判 mixed（FAIL-CLOSED 误火）——最小修改收 `nshards` 单值（分片完整性四门 untouched）后重跑落地。**账本 362,389 → 364,589（+2,200·单计一次·finalize 无幂等门=禁二次跑 r253 单计律）**。

**核心读数**（results/p2_calibration_v2_ext.json·evidence_cutoff 2026-09-22）：

| 池 | K | mu | sigma |
|---|---|---|---|
| canon v2 | 120 | -0.0912 | 0.2368 |
| ext-only | 2,200 | -0.0909 | 0.2481 |
| **merged** | **2,320** | **-0.0909** | **0.2475** |

**判读表对号**：
- **H-K1 命中**：Δmu=+0.0003 << 2·SE_mu（0.0432）；Δσ=+0.0107 < 2·SE_σ（0.0307）→ **canon 稳定性证据入档**（K=120 的 mu/σ 均在抽样噪声界内·flip 提案降优先）；
- **H-K2 未触发**（|Δσ| ≤ 2·SE）→ 无 P0 flip 提案义务；
- **H-K3 触发**：skill_line_v2 @同 n_eff=362,389：**1.1071 → 1.1613（Δline +0.0542 > 0.05）**=判据线实质漂移——机理=√(2·ln N_eff)≈5.05 放大器把噪声界内的 σ 微增（+4.5%）放大为线级 >0.05 移量（H-K1 与 H-K3 同时合法命中·非矛盾：σ 统计稳但线敏感）；**披露义务已核**：在飞未判批（EXCLUSION-MARGINAL-P1 / CROSS-START-FACEB / W14-draft）rg 零 skill_line_v2 判据消费=本窗零注记对象，**未来预注册判据节引用 skill_line_v2 时须携带 K-lift ±0.054 注记**；
- **canon 不动铁律遵守**：null_sharpes() 仍读 120 值 canon，p2_calibration{,_v2}.json 零触碰（selftest 路径安全腿过）。

**跑前预测对账（P1-P5）**：P1 mu ✓（|Δmu| 0.0003 ≤ 0.03）；P2 sigma ✓（+4.5% 界内）；**P3 线移 ✗**（+0.0542 > 0.05——低估了放大器对小 σ 移的敏感性）；**P4 右尾 ✗**（A-ext p95 0.3194 vs canon 0.3206 微低 0.0012≈平——canon p95 并非小样本低估·先验方向错）；P5 配对差分 ✓（中位 **+0.0845** > 0·正占比 63.5%·v1 H2 退出机器贡献方向复现）。**3/5 中 2 MISS 如实记**。

**工程披露**：①finalize nshards 元组 bug 当窗最小修（分片面零动）；②ext 件 `passive_term` 字段=null（getter 键名差 passive vs passive_term 的 cosmetic 缺口·线值与 Δ 全正确·null_term 两侧主导=max 取值不受影响）；③finalize 无幂等守卫——**任何重跑=账本重记**，重执行须走 r259 prev-echo 面或人工先读账本头。

## §8 批后复盘【r289 bm-c】

1. **P3/P4 双 miss 同根**：先验把「σ 统计稳」直接外推成「线稳」，忽略了 5.05× 放大器——K 提升的真正意义恰是把 σ 估计从 ±6.5% 噪声收到 ±1.5%，顺带暴露 canon σ 虽无偏但线级读数对新池敏感（+0.054）；后续「线稳定性」类预测必须带放大器项 σ·√(2 ln N_eff) 的传播误差计算，不能只看 Δσ。
2. **p95 判读**：canon K=120 的 A 族 p95（0.3206）与 K=2200（0.3194）几乎重合=canon 右尾本来就准，v1 时代「小样本 p95 低估」先验在 canon v2 固定引擎面上不成立——该先验面退役。
3. **治理面**（§4 预先承诺兑现）：H-K1 稳定证据在档→canon-flip 提案**降优先**非关闭；若未来任何批需引用更稳线，消费 p2_calibration_v2_ext.json merged 面（K=2,320）并在判据节双列 old/new 线读数；flip 本身=后续治理窗动作，本批无翻线权（铁律重申）。
4. **可复现性**：4 分片确定性单趟字节幂等+selftest 七腿绿+finalize FAIL-CLOSED 四门全过（shard 集 0..3 完整/A 2,000/B 200/命名唯一）——重跑任一分片字节恒等（r159 族免疫）。
