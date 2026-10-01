# PERPETUAL_FACES（常供面法典）v1.0 — T-133 s2 面级冻结件

- 票据：T-2026-09-30-133 s2（CEO 直令 O-2026-09-30-2340 满负荷根治·机队 CPU 严重闲置）
- 立法源：GM 派工 + bm-b 认领（slice-declared，2026-09-30 23:55 commit 1b430e777）
- 冻结纪律：本件=**面级冻结一次**（ticket 原文 "face-level prereg frozen once"）；每个 face 的每一波批另有波级 prereg（R99 纪律，从 PREREG_TEMPLATE.md 起草），判线一律调 `scripts/science_gates.py` 共享库（g1_prime_v2 / g2_registration_v2 / dsr_from_stats / null_sharpes / skill_line_v2），**禁手抄判线**。
- 性质：TRIAL_LABOR_LAW v1.0 §1 常供律的供给面扩展——四条永不断供的面（never-dry），供给触发=生成器自动化，禁等 CEO 提醒。

## §1 供给律（supply_floor 触发）

- 判据（三腿同真）：`results/runnable_pool.json` 无 status∈{ready,waiting,running} 条目（池饿） ∧ 本机/车道 py CPU < 70%（算力有承接） ∧ 无同 face 在飞波（波间禁重叠双烧同带）。
- 触发动作：生成器 `python scripts/perpetual_faces.py supply` 对**已落地 runner 的 face** 按优先序 N1>N3>N2>N4 物化下一波池条目（§3 契约）。
- **诚实律**：runner 未落地的 face = `faces_pending` 如实披露，禁假物化（物化一个无 runner 的池条目=autofill 空转=违 CEO 令）。
- supply_floor / pool_starved 两旗 = 生成器每次 supply/status 运行写 `results/perpetual_faces_state.json`（s3 面消费：daily report 首行 + CEO 面常设行，由运营面接线）。

## §2 四面定义（face table）

| 面 | 定义 | 复用基（verbatim import 禁重写） | 判线（共享库调用） |
|---|---|---|---|
| N1 nulls-deepening | 对 judged/in-flight 零假设族按新种子带重bootstrap加深（p95/p99 越压越准，K 随之抬升） | `p2_null_calibration.py`（frozen v1 设计）+ `p2_null_calibration_ext.py`（波扩展范式：run_one 同源、shard 切片、disjoint 种子带、append-only 分片件） | `null_sharpes` / `passive_strict_max` / `skill_line_v2`（既有 G1' 六条有效技能线不重定义，加深后 p95 面自动更准） |
| N2 random-subspace furnace | 冻结语法轴系的随机子空间组合采样（探索面；语法轴=W1-W14 冻结语法全库） | trial_labor_w1..w14 链 import 面（tl1 枚举/锚/信封原语 + 逐波 overlay）+ mass_trial_w1 Sobol 采样范式 | 波级 prereg 判据节调 `g1_prime_v2` / `g2_registration_v2`（初筛面+全量判决两段制=TRIAL_LABOR_LAW §2） |
| N3 neighborhood robustness grid | 在册成员冻结参数邻域应力网格（G2 证据供给面：neighborhood/cost_x3/per_year） | `t24_g2_pack.py`（PROS 面 G2 pack 既有机器）推广到注册面 | `g2_registration_v2` + `bootstrap_ci_sharpe` |
| N4 bootstrap alternate-history | bar 重采样→平行宇宙重放在册成员（前向不改史，纯重放测量面） | engine/run_backtest 同源 + 重采样层新写（resample 面为本 face 新机制，波级 prereg 冻结采样算法规格） | `bootstrap_ci_sharpe` / `dsr_from_stats` |

- 同族 max|corr|≥0.7 拒收（D6 机制门槛）与去重门 T-84s3 持仓指纹：**只约束候选判决面（N2）**；N1/N3/N4 为测量加深面（对既有族重新测量），产物=更深置信面非新注册件，不入候选漏斗，不占语法消耗登记簿行。

## §3 生成器契约（scripts/perpetual_faces.py）

- 子命令：`status`（只读：池饿判定+面注册态+旗面）/ `supply`（§1 触发判定→物化）/ `selftest`（离线自检：面注册完整性、种子带 disjoint 性 vs SEED_REGISTRY、池解析、状态件往返）。
- 物化律：池条目结构=runnable_pool schema v1 既有字段（id/prereg_ref/runner/runner_args/lane_owner/priority/status/entered_at/data_gates/shards/workers_plan）；`worker_class=self-contained`（in-repo 数据、clone-and-run 任何机）；`lane_owner=ANY`（R31/R65 合法）；single_writer=车道机写池文件、autofill 只读（既有律不变）。
- 饱和上限：单波物化 shard 数受 RAM/核预算约束（workers_plan 沿用池内既有先例 12×BelowNormal 起档，重面自降）；物化后返回，**禁轮内内联代跑**（O-20260924-2100 批执行纪律）。
- 波账：每波 materialize 记 `results/perpetual_faces_state.json` waves[] append-only（face/wave/bands/N_entered/ticket_ref）。

## §4 种子带预指派台账（append-only；波级 prereg 引用本表，R250 one-step 律=冻结后禁再挑）

种子带全部与 `science_gates.SEED_REGISTRY` 既有值 disjoint（selftest 腿强制校验）：

- N1 波2：A-ext j=0..1_999 seed=**12_100..14_099**；B-ext j=0..199 exit seed=**21_100..21_299**
- N1 波3：A-ext seed=**14_100..16_099**；B-ext exit seed=**21_300..21_499**
- N1 波4：A-ext seed=**16_100..18_099**；B-ext exit seed=**21_500..21_699**
- N1 波5+：顺延 +2_000/+200 续带，落波级 prereg 时先行 SEED_REGISTRY 登记（禁先跑后登记）
- N1 波5（r307 bm-c 落 prereg 时展行）：A-ext seed=**21_900..23_899**；B-ext exit seed=**21_700..21_899**。注记：A 带 +2_000 顺延算术位（18_100..20_099）撞 v1 B 在用带 20_000..20_019 与 SEED_REGISTRY 值 20000 及 ext W1 B 带 20_100..20_299——本表 disjoint 硬律（selftest 机闸）优先于步长惯例，A 跳位至全部已预留带后首个连续 2,000 窗（21_900=本波 B 尾+1）；非重挑（W5 带从未指派·测量面零结果可钓）。**W6+ 警示**：B +200 顺延算术位（21_900..22_099）将落入本波 A 带——W6 波级 prereg 须同法跳位 B 带并如实注记。
- N2/N4 波带：各自波级 prereg 冻结时从 **30_000+ / 40_000+（40_000/40_001 设计探针保留）** 域外顺延分配，本表不预占（探索面种子面广，逐波登记防撞）

## §5 计账（跨波累计 N_eff 恒不重置）

- 每波 finalize 后：`science_gates.append_ledger` 落行（face/wave/N/k_eff/evidence_cutoff/result_ref）；累计 N_eff 供 `dsr_from_stats` 消费——**波与波间不许重置计数**（TRIAL_LABOR_LAW §4 同律）。
- 预期假阳性数随 N 如实披露；负波照报；1000/5000=上限非凑数。
- attrition 账本完整性 tripwire（r448 律）覆盖本面波产物件。

## §6 诚实待命律（legal idle 判据收窄后的白名单）

板全闭环 ∧ 池空 ∧ **四面均无未决波**（faces_pending 空）∧ 无其他在飞批 = 唯一合法闲置；任一面有可跑波而池空=违令（生成器 status 面必须点名）。I/O-bound 采集器不算 CPU 忙（cpu/py 面为唯一真值，s1 律同源）。

## 冻结签名

- 冻结时刻：2026-09-30 23:5x bm-b r484（claim 同轮开工=O-1730 即时律）；冻结 commit=本波提交哈希（git 可验）。
- 波级 prereg 起草顺序：N1-W2 → N3-R1 → N2-W15 → N4-B1（按判据成熟度与复用基就绪度排序；runner 落地一批物化一批）。
