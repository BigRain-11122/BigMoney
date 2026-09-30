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

## §7 跑后实证【待烧批落地回填】

## §8 批后复盘【待烧批落地回填】
