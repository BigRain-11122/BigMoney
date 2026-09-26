# AGGR_FULLPOOL_BATTERY — 激进家族全池 W-GRID 电池批预注册（跑前冻结）

> 令：O-20260926-1332（CEO 直令「backtest R&D full throttle；comprehensive multi-sample backtesting as the quality gate；本批=real ammunition」）· 票：T-2026-09-26-80-P1（P1·immediate）· 认领：bm-b R252（claim b84f8636）；本件=runner 构建轮 R253 冻结。
> 双轨制不变（T-56 §0 律）：本批=候选供给面测量；零采纳零接线；月界入 T-27 锦标赛池=常设候选；采纳仍走 GM 批准+7 天否决窗。
> 跑前冻结：本文件 commit 先于任何跑批（R99 律）；跑后只许回填 §7/§8，禁改判据禁重跑（确定性引擎重执行≠结果重跑，按单发守卫+env 豁免律处理）。

## §0 批件身份【跑前】

- 批名：T80-AGGR-FULLPOOL-BATTERY；判断格=**400 聚合判断单元**（20 变体 × 20 T-28 口径格：W-CUR {x1,x2}=2 + W-SEG 3 段类×{x1,x2}=6 + W-GRID {legacy,deep}×{6m,12m,24m}×{x1,x2}=12；T-28 口径逐字沿用，per-cell N 沿用 P5C/t22/t54 已计账本不重复计数）。
- 20 变体=T-56 五（AGGR-CONC-TOP2/OFFENSE/MOM/NOCASH/REGIME，含今晨 top-3）+ T-58 十五（FAM_VARIANTS 全表，冻结 sha 门 19 向量+2 规则）；**零新权重向量零新信号函数**——全部冻结件逐字复用（反重复律）。
- W-GRID 面升级=本批唯一新测量面：CE-6 受限面（`_ce6_restrict` 6 员限制归一）→ **全池 28 员面**（T-54 PROSPECT 网格证据 121,528 cells 入位后的消费面，t54 prereg §8 消费判据面=10-31 J 线重跑同款面的先行扫）。
- sleeve 域（W-CUR/W-SEG）=o1600 口径复现 56 sleeve → 账本 **+0**（T-56 先例）；canon B_MAXDIV 全池网格再推导=验证腿 **+0**；账本入账=400 判断格。
- 部门归属：dept:组合与资金（变体判决）+研究（网格证据消费）+工程（runner/pool）joint。
- 算力：56 sleeve ≈8.6s（25 workers）+ 121,528+18,072+15,036 行网格装载 ≈10s + 21 权面×12 网格单元算术 → 预估 <90s 单机；**分钟级轻批**（T-56 R41 同级），池入口登记 workers_plan（O-2130）供自动续批器拾取；分片协议 `--shard/--shards`（变体作业切分）已备，本批登记 0of1。
- **车道钉扎（R188 先例）**：烧机=持 canon CE deep cells 之机（bm-a/bm-c；bm-b 本地=680/1506 部分 dprobe 复现件，按 t54 prereg §7-3 判为污染面禁用）——runner 数据门 fail-closed（canon 缺件=exit 2 诚实拒跑），lane_owner=bm-a。

## §1 α 机制段【D6】

- [x] **风险溢价**（T-56 §1 逐字先例）：混合不创造 α——20 变体全部=已注册 28 员 sleeve 上的**权重集中/政体切腿规则**，零新信号函数、零搜索、零 null 族（SEED_REGISTRY 零登记）。激进≠新 α 主张；本批 KPI=全池网格面读数修正（CE-6 近似面的诚实再测量）+ 收益天花板/牛市增量，非过闸数。
- 同族相关性准入：N/A（零新信号函数）；替代披露=20 变体日收益两两 corr（描述性，T-56 §7 已有 0.72-0.99 高共线披露沿用）。

## §2 数据与面板【跑前事实】

- **legacy 轴全池网格**=p5c leg-L checkpoint（6 CE × 1253 起点 × {x1,x2}=15,036 行，机器本地件）∪ t54 legacy cells（22 PROSPECT × 1256 起点 × {base,x2}，本机 16 分片 census 121,528 对账）。
- **deep 轴全池网格**=t54 deep cells（22 PROSPECT × 1506 起点 × 2 面）∪ **canon CE deep cells（钉清单装载：非 glob；期望=6 CE × 1506 起点 × 2 面=18,072 行；dprobe 部分签名〔680 起点位区间〕=拒收 exit 2）**。canon 件路径钉 `results/t22/cells_deep_base.jsonl`+`cells_deep_x2.jsonl`（无 `_2` 后缀正典名），env 覆盖面 `AGGR_FP_CANON_DEEP_BASE/X2` 供持机如实改指（audit 记录实路径）。
- **passive 基准跨源恒等门（硬门）**：同起点同窗 p_ret 两源逐位一致（跑前实勘：p5c legL vs t54 legacy 0/314 mismatch；deep 同机件两源同断言，任一 mismatch=exit 2 拒批——beat 比较必须同基准）。
- sleeve 面板：live.paper.load_core() core48（o1600 口径）截断 SLEEVE_CUTOFF=W_CUR_END=2026-09-23（T-28 冻结窗正典可比性；cutoff 后新 bar 不回流本批）；完备门=面板 cutoff ≥ 2026-09-23。
- evidence_cutoff=**2026-09-24**（消费证据最晚面=t54 网格 cutoff）；逐源 cutoff 披露 map：p5c/t22-canon=2026-09-22、t54=2026-09-24、sleeve 域=2026-09-23。

## §3 方法学【跑前】

- 权重向量：T-56 六 sha 门 + T-58 十九 sha 门（17 向量+2 规则）跑时逐门断言（冻结表逐字复用 `aggressive_lab.FROZEN_SHA/FAM_FROZEN_SHA`，零重写）。
- 判决帧：静态面=`_blend_daily_ret`（t27 语义）；政体面=`_regime_blend`/`_legs_blend`（v3 原始四态 shift(1) 因果）；轮动面=`_rotation_blend`（冻结规则文本 sha 门）。x2 成本面沿用 x1 冻结权重（13bp×2，CostPatch 语义在 sleeve 层已 baked）。
- 全池网格单元：`t28._grid_unit` 逐字复用，`traders=ROSTER`（28 员），`w=rep_w`（静态面=冻结向量；政体/轮动面=时间平均权 ā_i，T-27 D 先例）——**无 CE-6 限制归一**；起点入池=该起点 28 员该窗全备（_grid_unit 语义逐字）。
- 六面样本正典（O-1332 条款 1）覆盖表逐变体披露：massive virtual timepoints ✓（2762 网格起点）/ designated windows=当前政体窗 ✓（year-first-day 起点窗不在 T-28 口径=如实披露缺）/ 25y deep ✓ / regime segments ✓（W-SEG+逐起点 regime）/ cost stress ✓（x2 双面）/ capacity face ✗（ADV 参与率帽未接线=缺）→ **面不全=verdict 一律 incomplete-face 诚实标注**（正典律：缺面即不完整判决，不假装全格）。
- 落地钩子（票 (3)）：CN models（T-73 s3）/ grid sleeve（T-78）/ wild-route 幸存者（T-57 s3 门修复后）——runner 输出 hooks 状态块（在场性如实报），入电池=各自另开预注册（三线律），本批零消费。

## §4 判据【跑前写死·T-28 J 线逐字同门】

- **W-CUR**=2026-01-05→2026-09-23（T-28 冻结窗）；**J1**：x1 净收益>0 且 |maxDD|≤5%；**J2**：x2 净收益>0。
- **W-SEG**=v3 段类（REGIME_MAP bull/chop/bear）；**J3**：各段类累计净贡献 ≥ −5%（两成本面全段类，任一破界=FAIL）。
- **W-GRID**=全池 28 员面 {legacy,deep}×{6m,12m,24m}×{x1,x2}；beat=blend>per-start passive（t22 口径）；12m pooled beat 全披露（对照：CE-6 受限面记录 CONC 0.5389/REGIME 0.5848/canon 0.4854；t54 全池 PROSPECT 单员 12m pooled 0.36-0.51）。
- **J5 D7 四必报**逐变体逐网格单元：OOS 笔数池化/覆盖年数/独立政体窗数/CI95 宽度（Wilson）。
- **canon 再锚定（票 verbatim：B_MAXDIV/NOCASH face comparison=canon re-anchor）**：canon B_MAXDIV 28 员向量全池网格 12 单元再推导（+0 验证腿）；AGGR-NOCASH（同 sha 向量）全池网格面与 canon **逐位恒等断言**；NOCASH sleeve 域 W-CUR/W-SEG 读数与冻结件 `results/aggressive_lab.json` **逐位恒等断言**（确定性锚定门，任一漂移=exit 2 拒批）；15 家族变体 W-CUR x1 读数与 `results/aggressive_family.json` 冻结值逐位恒等断言。
- **硬界三件套**（T-56 §4 沿用）：max 硬界=J1 dd≤5%（sleeve 域不变，无新 max 面）；分布界=逐变体日收益 median/p99.9 描述性；危机日=J3 段类面。网格面=聚合算术无单日极端面，无新 max 界。
- KPI（非过闸数）：①12m pooled beat 全池面读数（vs CE-6 受限记录差=「近似面修正量」本批主读数）；②收益天花板+牛市段增量（sleeve 域，预期与冻结件逐位同）。
- 判定输出=逐变体 J1/J2/J3 布尔 + 全池 W-GRID 12 单元 + 六面覆盖表 + D7 + KPI；**零采纳动作**。

## §5 跑前预测【冻结】

1. sleeve 域读数（W-CUR/W-SEG/J1-J3）与冻结件逐位恒等（同面板截断+同机件复现）；任何漂移=工程病非市场读数（锚定门拒批）。
2. 全池 12m pooled beat：CE 质量集中面（CONC-TOP2/TOP2 族/FULLCE 族）≈受限面读数±采样漂移（限制=恒等、仅起点集由 6 员全备收窄为 28 员全备）；PROSPECT 军团质量面（OFFENSE/REGIME/GREEN 族）**预期低于受限面读数**（受限归一曾把 PROSPECT 质量重归一到 CE 员上抬高了读数；t54 全池 PROSPECT 单员 12m pooled 0.36-0.51 低于 CE 单元记录）——「cures the CE-6 restricted face」=诚实再测量，方向预期=下修。
3. canon/NOCASH 全池网格面逐位恒等（同向量）；canon 12m pooled 全池预期 ≈0.48 量级（CE-6 面 0.4854 的同向量重采样）。
4. pooled n12（全池 28 员全备起点）≤ CE-6 面 n=2507（起点集收窄），预期 2300-2530 区间；deep 12m 完整窗计数预期 ≈1380（1506−partial，canon 冻结签名 623/1380 同族量级）。
5. 极端日先验：无新极端面（sleeve 域窗不变；网格=聚合算术无单日 max 界）。
6. 全 20 变体 verdict=incomplete-face（capacity face 缺）——正典律诚实标注，非批失败。

## §6 产物【跑前】

- runner：scripts/aggr_fullpool_battery.py（selftest/run 子命令；池分片 `--shard/--shards`；单发 finalize 守卫 `AGGR_FP_REFINALIZE=1` 唯一重做口径）。
- 产物：results/aggr_fullpool_battery.json（顶层 evidence_cutoff=2026-09-24+逐源 cutoff map+audit+prereg sha 嵌入）+ gate_attrition 追加行 + 本文件 §7/§8 回填。
- pool 入口：results/runnable_pool.json 登记 T80-AGGR-FULLPOOL-BATTERY（lane_owner=bm-a；workers_plan 实填；F-04 MSG 先行）。

## §7 跑后实证【跑后回填——占位纪律：写数字即造假】

（待烧机轮回填）

## §8 批后复盘【s7-T】

（待烧机轮回填）
