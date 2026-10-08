# TRIAL_LABOR_W17 候选稿（CANDIDATE DRAFT·未冻结）——出场规则轴族首烧

> 状态：**DRAFT-BERTH**（funnel leg 1/5：draft → probe → freeze → runner → pool；本件非冻结预注册，冻结时另立 `research/TRIAL_LABOR_W17_PREREG.md` 全模板填齐）。
> 起草：bm-c r786（2026-10-09 01:1x）·dept:研究 ·常供线律=firm/TRIAL_LABOR_LAW.md §1（触发三面坐实：板空〔fleet 票 0 open〕+池饿〔408/408 done·ready=0<floor 3〕+无在飞判决批）·派单=D-20261009-01③ 备货池补货（窗 10-10 00:00·F-20261009-01 承接回执）。
> 供给血统：TRIAL_LABOR_LAW §5 供给面如实盘点（2026-10-09 01:0x 实读）——W16-JUDGE 判决面 `n_eligible_g2=0`（诚实负·无 REFINE_BENCH 存活变体供给）；moneyflow IC reference batch=panel blocked 非可即供（F-20261009-01②）；T-177 leg-2 牛市进攻供给扫描=bm-a 车道、其 leg-1 labeler 落地后才开窗（≤10-14）；外源 digest=零新批。**常供线内部供给=冻结语法库未探索轴空间**：§3 多维律声明轴系「入场过滤×出场规则×仓位法×时机×域」，W1-W16 十六波全部烧在入场过滤轴 face 上，**出场规则轴=声明在册但 W 血统零烧的最大未探索轴**。

## §0 批件身份（草案位）

- 批名：TRIAL_LABOR_W17（出场规则轴族首烧）；批号=冻结时开票 T-2026-10-09-<seq>-P1（开票即认领同轮·O-1730 即时律·W16=T-172 血统延续）。
- 认领：F-04 先行（冻结窗开时 fleet/inbox/ MSG 声明）；lane_owner=起草机 bm-c 或冻结机承袭（W14=screen 烧录机 bm-c/judge 泊位 bm-b 先例·跨机合法）。
- 算力预算：两段制（§2 律）——初筛单轴 6m base 廉价面先行；存活者全量判决。分片入池按 W15 先例（SCREEN 12 shards/JUDGE 12 shards）·池补货目标 ≥10 claimable（D-01③ SLA）。

## §1 意义门三问（TRIAL_LABOR_LAW §4·过门声明）

1. **本批回答什么研究问题**：在受控入场语法（冻结 16 轴库采样·W14/W16 血统）上，**出场规则族（tiered-TP/hard-stop/time-decay/trailing/持有到底/pattern-exit 族）相对引擎缺省出场栈（template_default）的边际贡献是否显著**——出场轴是唯一被测维度，入场面全格恒同（per-cell 配对对照）。
2. **消费方是谁**：①一切未来判决批预注册「出场轴显式门」（O-20261001-1108 三选一）的实证选择基线——①策略自有出场 vs ③template_default 的跨族读数目前只有 LOWAMP 单族孤例；②LOWAMP-P2 出场轴判例（T-140）的跨族泛化证据面；③试用期题库（s4 intake face·G2/reform 链）；④engine/exit_rules.py 缺省栈作为被测对象的稳健性证据（LOWAMP-P1 教训：缺省出场栈把 +15.9% 磨成 -18%=出场轴敏感性实战级实证）。
3. **语法登记簿查重**：TRIAL_GRAMMAR_LEDGER 实读（2026-10-09 01:0x）——W1..W16 全部行=入场语法 face（AMPGATE/MOM/STD/RSQR/SUMN/RESI/CNT/MAX/RANK 族）；W15=N2 随机子空间采样面（机制面非出场轴）；LOWAMP-P1/P2=LOWAMP 单族 family_key 内的出场轴重考（M3 对号边界：本批 family_key=TRIAL_LABOR≠LOWAMP，非同族复跑）。**出场规则族在 W 血统=零烧**。冻结窗 probe 腿强制复扫登记簿断言零出场轴行（fail-closed）。

## §2 α 机制段（D6·冻结时全填·草案方向位）

- α=**行为偏差**（处置效应/锚定）：出场纪律的边际价值来自对手盘处置效应不对称——散户口「赢家过早卖、输家过久拿」；机械化出场族=对处置效应的结构化收割（论证一句话冻结时按 face 逐个展开）。
- **散户凭什么赢（§1.2）**：行为（纪律化出场 vs 情绪化处置）＋制度（T+1 约束由引擎恒开恒承担——成本口径恒开·三铁律）。
- 同族相关性准入检查：冻结时逐对算 max|corr|（在册+同批·日收益口径·≥0.7 拒收）。

## §3 出场轴显式声明（O-20261001-1108 三选一·冻结门必填位）

**双臂对照设计，全场显式零隐用缺省**：
- treatment 臂=**①策略自有出场**：出场规则族 faces（候选 face 集：tiered_tp_only / hard_stop_only / time_decay_only / trailing20 / hold_to_end〔②持有到底声明·runner 显式禁用引擎缺省出场栈〕/ pattern_exit 族——face 清单+参数=冻结窗 probe 腿定稿；逐 face 规避 BAN-08 缓冲带/免交易带形态）；
- control 臂=**③template_default 按设计测**：引擎缺省出场栈=被测基线对照（非隐用）。
- 禁开方向硬闸（§0.5）：出场轴族非新入场方向——九禁向预期零命中；冻结时 `banned_direction_gate.py --prereg` rc0 放行为冻结门必要条件。

## §4 数据与面板（冻结时全填·草案锚位）

- 宇宙=core48 冻结锁盒（RW-4）；evidence_cutoff=P-5C 冻结绑定 2026-09-22（W14/W16 同族绑定先例）；数据锚四元组+探针-锚同面断言（G-ANCHOR-FACE 律）冻结时逐锚填。
- 入场面=冻结 16 轴语法库（W14 grammar lib sha a231bf10940e7878 血统）固定采样（A/B 配比冻结时定）；出场面=§3 face 集。每格=入场 face × 出场 face 配对（出场轴=唯一变量）。
- null 对照=同掩码随机 null（K=冻结时定·新 seed 基先登记 science_gates.SEED_REGISTRY·R250 同 commit 一步律；候选带避开 W16 seeds 20593000/20593500/20594000 与 W192 引擎带 437_204..439_403——冻结窗 probe 腿选带+registry 双扫零命中断言）。

## §5 判据（冻结时按 PREREG_TEMPLATE §4 全填）

G1' v2 + G2 registration v2 共享库 import（r271 单源律·禁手抄判线）；reform 链按 W14/W16 先例（O-1058 五步链）；跨波累计 N_eff 照 TRIAL_LABOR_LAW §4（DSR 链头活读 no-reset）；E[FP] 如实披露；预期假阳性数如实披露；负波照报。

## §6 漏斗续作点（精确续作点·r787+ 承接面）

1. **probe 腿**（L1 零烧·下轮可做）：登记簿出场轴零烧断言复扫＋banned_direction_gate 预跑＋seed 带选位探针＋出场 face 参数面探针（exit_rules.py face 枚举实读）＋入场库采样配比探针（复用 W16 探针血统 `_r720bma_maxrank_w16_probe.py` 范式·probe facts JSON 落盘）。
2. **freeze 窗**：全模板填齐+硬闸 rc0+seeds R250 同 commit 一步律+开票即认领（O-1730）+F-04 MSG。
3. **runner 构建**：clone `scripts/trial_labor_w16.py` import-face 复用机械（w3 先例「零重实现」）+出场 face 层+selftest hermetic 全绿。
4. **入池 ≥10**（D-01③ SLA·窗 10-10 00:00）：GENERATE 1 + SCREEN 分片（W15 12-shard 先例·shard 数按候选格数定）+ JUDGE 分片 → pool claimable ≥10；到窗读数随班回执（F-20261009-01④）。
5. 到窗无回执=升 E1 入 CEO 清单（D-01③ 原文条款）——本草案即承接回执的执行轨迹首锚。

## §7 跑后实证【跑前必须为空——占位纪律】

（冻结时留空·写数字即造假）

## §8 批后复盘【必填·s7-T】

（冻结时按模板填）
