# AGGR_CAPACITY_FACE_P1 — 激进家族电池批容量面（披露腿）预注册【跑前冻结】

> 令：O-20260926-1332（CEO 直令 six-face canon 条款 1「capacity face（ADV participation caps at 1M scale, DIV_LOWVOL lesson law）」）· 票：T-2026-09-26-80-P1 slice-4（owner bm-b·R258 resume spec 逐字：freeze prereg + runner on battery sleeve machinery + hermetic selftest）· 认领：bm-b R259（F-04 先行=MSG-20260926-1605-bm-b）。
> 跑前冻结：本件 commit 先于任何跑批（R99 律）；跑后只许回填 §7/§8，禁改判据禁重跑（确定性引擎重执行≠结果重跑，按单发守卫+env 豁免律处理）。
> **性质=披露腿（disclosure face）**：测量冻结电池批 20 变体在 ¥1M 规模下的 ADV 参与帽读数；**零改判、零再入账判断格、零采纳零接线**（双轨制不变，T-56 §0 律）；电池批产物 `results/aggr_fullpool_battery.json` **字节冻结不触碰**（容量覆盖翻面记于本批产物，禁改已判件）。

## §0 批件身份【跑前】

- 批名：`AGGR-CAPACITY-FACE-P1`；**判断格=0**（披露腿：电池批 400 判断格已在册，本批零新判断格、零新收益流判读——账本 **+0**，canon 再锚定腿先例）。
- 20 变体×其 w>0 sleeve 的**测量单元**=冻结电池产物 `weights_representative` 逐字消费（291 (变体,sleeve) 对，去重后 **267 个 (sleeve, scale) 测量单元**；单源=电池批冻结件，零重推导）。
- 部门归属：dept:组合与资金（容量读数/披露）+工程（runner）joint。
- 算力预算：267 单元 × ~1.5-2s/单元 ÷ 25 workers ≈ **30-60s 单机分钟级轻批**（电池批同级）——<5min 线下按 O-2100 执行面分离豁免**轮内内联跑**（>5min 才强制入池），RAM 门 4GB 沿用，BelowNormal 优先级，audit 段必带（elapsed/workers/单元数）。
- **车道钉扎**：bm-b-local 合法面=变体代表权面（CE/core48 成员，weights_representative）——本批只消费本机 core48 CSV 与电池冻结件；**canon B_MAXDIV 全池深轴成员容量=bm-a 单独面**（深轴 PROSPECT bars 不在本机），本批零消费零声明。

## §1 α 机制段【D6】

- [x] **微观结构**：本批测量的是**成交约束**本身——变体建仓需求 vs 1% ADV20 参与帽（knowledge/rules.py `ADV_FILL_CAP_RATE=0.01`：超额不成交、零/负 ADV 拒单、缺失 ADV 保守 10bp 不设帽）。零 α 主张、零新信号函数、零新权重向量（全部冻结件逐字复用——反重复律）；由谁付出代价=容量约束是市场微观结构对规模的收费，读数如实披露。
- 同族相关性准入：N/A（零新信号函数零新收益流判读）；V2 成本面 sleeve 收益流为**披露列非判读面**。

## §2 数据与面板【跑前探针事实，非结果】

- 宇宙：core48 本机 CSV 48/48（`load_core()`；`amount` 列=CNY 成交额，engine 口径=ADV(20d) 滚动均 yuan）。
- 窗口：sleeve 域=面板起点（2020-01-02）→ **SLEEVE_CUTOFF=2026-09-23**（电池批冻结口径逐字沿用，T-28 正典可比性）；cutoff 后新 bar 不回流本批。
- **evidence_cutoff=2026-09-24**（最晚消费证据面=core48 面板 bar 至 09-24；sleeve 域截断 09-23 如实分离披露）；产物顶层必带 `science_gates.cutoff_meta` 字段（缺=science_audit C2 VIOLATION）。
- ADV20 面板=逐成员自身 bar 序列 `amount.rolling(20, min_periods=1).mean()`（**成员本位窗口：只含该员真实 bar**，面板=联合索引、缺失日不 ffill——engine 自带 missing-ADV 语义接管：缺失→10bp 不设帽+计数；与 DIV_LOWVOL 家族「raw volume×close 滚动 20」同 raw 面口径）。engine 内部 shift(1) 因果（执行日只见信号日既成 ADV）——调用方传未 shift 的 through-date 面板。
- 跑前定标探针（面板事实·r206 先例，非结果）：ADV20 分年分布——最薄成员 513520：2020 ¥6.41M／2021 ¥6.10M／2022 ¥3.74M／2023 ¥31.8M（1% 帽=¥37K-318K 区间）；成员中位：2020 ¥245M → 2026 ¥833M（帽=¥2.5M-8.3M，对 ≤¥95K 需求结构性不约束）。sleeve sizing 事实：28 员冻结快照 position_size_pct∈[0.10,0.19]（缺省 0.10），sizing_mode 全员缺省=`fixed_initial`。
- 数据完备门（不过门禁跑批）：①电池冻结件在位且 20 变体 weights_representative 逐变体在位；②t56_caliber_registry 快照 manifest 全对（F11 字节哈希门·EOL 传输翻面容差=raw+LF 归一双门，R253 律）；③面板 cutoff ≥ 2026-09-23；④RAM ≥ 4GB。

## §3 方法学【跑前冻结】

- **规模口径（唯一新测量面）**：逐 (变体, sleeve, w>0)：`initial_cash = w × ¥1,000,000`（w=电池冻结件 weights_representative 逐字，6dp 舍入面披露：Σw 偏离 1 ≤ 3e-6/变体 → 规模偏离 ≤¥3，无害如实标注）。sleeve 引擎跑在该变体分配规模上，其余机器逐字复用电池批 sleeve 相位（`build_panels` + 快照 `load_trader` + `SIGNAL_BUILDERS` + `ExitPatch(exit_overrides)` + `dd_control`）。
- **静态初始分配口径（诚实披露面）**：engine sizing=`fixed_initial`（目标名义=initial_cash×pct 恒定）→ 本口径=冻结初始规模面；变体逐日再平衡的资本漂移**不建模**（披露腿保守简化， disclosed limitation——漂移面为二阶，电池判读不受影响）。
- **成本口径=V2（本批即测 V2 面）**：`run_backtest(..., cost_v2={"adv20": 面板})` engine 原生 D5 路径——入场需求超 1%×ADV20 → **截到帽部分成交**（capped_entries 计数）、零/负 ADV → 拒单（dropped_zero_adv）、缺失 ADV → 不设帽+missing 计数、逐侧滑点三层 2/5/10bp（tier 计数）。**无 CostPatch**（V2=固定费+分层滑点，D5 正典；电池 x1/x2 判读面不动）。卖出腿不设量帽（engine 契约：exit 机自有 sizing）。
- 测量单元去重：distinct (tid, scale) 跑一次，跨变体复用（267 单元）；逐单元记录：num_entries/capped_entries/dropped_zero_adv/missing_adv_executions/tier_entries_{2,5,10}bp/末期权益/n_trades。
- 逐成员分年 ADV 分布表（披露面，r206 `_r206_cap_view` 形态）：median/p25/p75 + 1% 帽名义。
- null 对照：N/A（零新信号零 α 主张；电池批 F6/nulls 已在册——本批零判读格）。
- 账本：**+0**（判断格 0；披露腿 canon 再锚定先例）；gate_attrition 追加行入 **`entries`** 列表（r248 消费链律）。

## §4 判据【跑前写死——本批无 G1'/G2（零判读格），判据=完成门+读数标签】

- **完成门（fail-closed）**：267/267 测量单元全部返回（任何缺单元=exit 2 拒出产物）；20 变体聚合块逐变体在位；manifest 门+完备门全过。
- **逐变体容量标签（披露标签，非过闸判）**：`unconstrained` ⟺ 该变体全部 sleeve 的 capped_entries==0 ∧ dropped_zero_adv==0；否则 `constrained`（附 capped/entries 率 + 逐 sleeve 受限计数明细——引擎 D5 计数器面=**无日期粒度**，受限日定位以分年 ADV 分布表并读为推断面如实标注，禁冒充测量）。标签**不改电池批 J1/J2/J3/W-GRID 读数**（零再判律）；六面覆盖翻面=本批产物 `six_face_capacity` 块为权威后继面，电池产物不触碰。
- **采纳/降级裁定权=GM/CEO 面**：constrained 标签对电池批候选资格的影响不在本批权限内（双轨供给面；如实披露后由总经办/月界锦标赛处置）。
- 极端日条款（三件套·披露面）：容量读数无单日 max 主判（计数器面）；分年 ADV 分布即分布界披露；极端日先验见 §5。
- 描述性条款：逐变体逐 sleeve 计数器全披露+V2 面末期权益（描述列，不入判读）。

## §5 跑前预测【冻结——跑后对账】

1. **集中变体早窗受限**：高权 sleeve（CONC-TOP2 w=0.5×pct0.19→单笔需求 ¥95K；TOP3/REGIME 0.148 级→¥28K；VOLATILITY-CE-01 w=0.5×pct0.10→¥50K）若信号入场最薄成员（513520：2020-2022 帽 ¥37-64K）→ capped_entries>0 集中在 2020-2022 早窗（**计数器无日期粒度，早窗定位=分年 ADV 分布并读推断**）；**若这些 sleeve 从未入场薄成员则全批 unconstrained**——两者皆合法读数，方向先验=集中变体至少一次触帽概率中高。
2. **宽基变体预期 unconstrained**：OFFENSE/MOM/GREEN 族最大单笔需求 ≈¥26K（w≤0.137×pct≤0.19）< 全窗成员帽下沿 ¥37K——预期零受限（边界=2022 年 513520 单点）。
3. **中位成员结构性不约束**：帽 ¥2.5M+ vs 需求 ≤¥95K，2024-2026 深水窗全变体零受限。
4. dropped_zero_adv 预期 0（core48 无全零量窗）；missing_adv_executions 预期>0 仅限成员上市前/停牌窗联合索引缺日（计数披露）。
5. **极端日先验**：容量面无 max 硬界（计数器）；2024-09-24→10-08 暴动窗=量能极端放大=帽极端宽松（方向=更不受限），2020-03 COVID=量能放大同向；无「量能枯竭+高需求」已知极端日形态，若出现=超出先验如实记 §8。

## §6 产物

- runner：`scripts/aggr_capacity_probe.py`（run/selftest 子命令；单发守卫 `AGGR_CAP_REFINALIZE=1` 唯一重做口径；RAM 门；shard 备而不分——单机轻批 0of1）。
- 产物：`results/aggr_capacity_face/p1_results.json`（顶层 evidence_cutoff=cutoff_meta(2026-09-24) + prereg sha256 嵌入 + 267 单元明细 + 20 变体聚合/标签 + 分年 ADV 分布表 + audit 段）。
- 账本：+0；`results/gate_attrition.json` entries 追加一行（kind=capacity-disclosure, cells_ledger_delta=0）。
- 本件 §7/§8 回填 + 票 progress_r259 + 轮报告回执。

## §7 跑后实证【跑后回填·一次定稿】

- **完成门**：267/267 测量单元返回（37.6s·12 workers·RAM 空闲 11.6GB·bm-b）；电池冻结件消费 census 291 对/267 单元全对；caliber manifest 29 件 sha 全对；V2 basis 全单元 `v2-adv20-tiered` 在位。
- **标签分布**：**9 unconstrained / 11 constrained**（20 变体）。
- **constrained 家族读数**（capped_entries/entries 率）：CONC-TOP2 24/881=2.72%、TOP2-60 24/881=2.72%、TOP2-80 22/879=2.50%、TOP2-C95 19/881=2.16%、TOP2-C80 17/881=1.93%、TOP3-GRAD 20/1508=1.33%、TOP3 18/1509=1.19%、GREEN-TOP2 6/12270=0.05%、OFFENSE-FULL 2/4309、FULLCE 2/1803、TOP2-MON 3/11940=0.03%。受限单元全部集中在高权 CE sleeve：COMPOSITE-CE-01（scale ¥166K-500K→需求 ¥31.7K-95K）与 VOLATILITY-CE-01（scale ¥400K-800K→需求 ¥40K-80K）。
- **unconstrained 家族**：OFFENSE/MOM/GREEN-MAX/REGIME/REG3/BARBELL/NOCASH/TOP2-WK/FULLCE-C80（宽基权面最大单笔需求 ≈¥26K < 全窗帽下沿）。
- **dropped_zero_adv=0（20/20 变体）**；**missing_adv_executions=0（20/20）**——core48 成员共享交易日历、联合索引无缺口，缺失面零触发。
- **受限位置结构推断**（推断面如实标注，计数器无日期粒度）：全表唯一 cap1pct_median 低于 CE sleeve 最大需求（¥95K）的成员-年=**513520（日经ETF）2020/2021/2022：帽 ¥64.1K/¥61.0K/¥37.4K**（p25 帽 2022 低至 ¥32.1K）——受限入场大概率全部落在 513520 早窗；2023 起 513520 帽 ¥318K+、其余成员帽 ¥2.5M+，结构性不约束。
- 产物：`results/aggr_capacity_face/p1_results.json`（evidence_cutoff=2026-09-24 顶层在位·prereg sha 嵌入·267 单元明细·分年 ADV 分布表）；gate_attrition entries 追加行（cells_ledger_delta=0·ledger_total_after=186592 不变）；账本 +0 如冻。

## §8 批后复盘【s7-T】

- **§5 预测对账**：#1 ✓（集中变体 constrained 概率中高→实证 11 受限全为集中族）；#2 ✓（宽基 9 员全 unconstrained）；#3 ✓（2023+ 无结构约束面）；#4 **部分错**：dropped_zero_adv=0 ✓ 但 missing_adv_executions 预测>0 实际=0——预测假设了成员上市前/停牌联合索引缺口，实勘 core48 全员共享日历无缺口，预测错在面板形态假设非机制假设；#5 ✓ 无量能枯竭+高需求极端形态（V2 权益面正常）。
- **判线 v2 当批读数**：N/A（零判读格——披露腿，电池批 400 格判读不动）。
- **门禁链损耗账**：gate_attrition entries 行已落（kind=capacity-disclosure）；完成门 fail-closed 全过零损耗。
- **消费面声明**：20 变体容量标签已测；六面正典容量面=本批产物 `six_face_capacity` 块为权威后继面（电池产物字节冻结未触碰）；canon B_MAXDIV 全池深轴成员容量=bm-a 单独面未开（车道律）。constrained 标签对电池候选资格的影响=GM/月界锦标赛裁定面（双轨律，本批零采纳零接线）。
- 回执：轮报告 r259 + 票 T-80 progress_r259 + attrition 行在案。
