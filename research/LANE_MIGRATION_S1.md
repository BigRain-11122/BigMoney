# LANE_MIGRATION_S1 —— D-20260928-03(1) 车道文件迁移测量面（S1 普查基线）

- 法源：集团 D-20260928-03 拍板①「每机车道文件 `results/<face>.<machine>.json` 为结构终态；消费面 dashboard/daily_report/聚合器确定性合并读；迁移=车道文件与合并视图双跑对账零漂移后切换；兼容窗双轨」。②错峰分钟位已由 OS 循环令钉定（bm-a=8/bm-b=2/bm-c=5），本件只覆盖①。
- 产出轮：bm-a r370（2026-09-28）。普查器：`results/_r370bma_lane_census.py`（L1 确定性单次 git walk，近 3000 commits 实采 1606，写手机器取提交尾标 `[via bm-x]`/`[rN bm-x]`，tick 无尾标不计入机器面=已知局限）；数据件：`results/_r370bma_lane_census.json`（55 个多机共写件全清单+消费面计数）。
- 零回测零引擎零判据面——本件为工程迁移测量件，非预注册批。

## 一、基线（多机共写 results/*.{json,js}：55 件，头部）

| 写入数 | 机器面 | 文件 | 消费面数 | 族 |
|---|---|---|---|---|
| 782 | a/b/c | compute_audit.json | 21 | A 滚动账本 |
| 770 | a/b/c | dashboard_status.json | 2 | C 幂等 derive |
| 759 | a/b/c | dashboard_status.js | 5 | C 幂等 derive |
| 746 | a/b/c | update_status.json | 19 | B gate 快照 |
| 710 | a/b/c | fundamental_b_layer_filter.json | **0** | B（零消费·降频审视候选） |
| 708 | a/b/c | regime_state.json | 6 | A 滚动账本 |
| 708/707 | a/b/c | heat/lhb_update_status.json | 2/2 | B gate 快照 |
| 706 | a/b/c | token_usage.json | 4 | B 计量快照 |
| 630 | a/b/c | futures_update_status.json | 2 | B gate 快照 |
| 608 | a/b/c | autofill_state.json | 1 | A 混合 dict+ledger |
| 288 | a/b/c | runnable_pool.json | 4 | A 池条目 |
| 279/207/205 | a/b/c | prospect_promotion/_summary·scorecard_v1·daily_scorecard | 13/5/1 | C 幂等 derive |
| 64 | a/b/c | gate_attrition.json | 47 | A 账本（高消费·合并读需保留全量语义） |
| 34 | a/b | post_review_criteria.json | 1 | A 账本 |
| 14/14 | a/b | market_clock/call_latest·l3_activation_table | 3/1 | B/C |
| 8 | a/b | crash_fuse.json | 1 | B 熔断态 |
| 9 | a/b/c | fundamental_status.json | 1 | B gate 快照 |
| 4 | a/b | census_fusion_s2/w1_results.json | 1 | C |

其余为 C 族确定性幂等重 derive（paper/*、prospect_promotion/PROS-*、paper_export/*：字节恒等重写，add/add 撞但零语义冲突）。

## 二、分类与迁移分批建议

- **A 族（有状态滚动账本·union 语义）**——r348/r120 吞行家族的实际受害者，车道化第一优先：`compute_audit.json`、`regime_state.json`、`autofill_state.json`、`runnable_pool.json`、`gate_attrition.json`、`post_review_criteria.json`。车道化后消费面合并读=身份并集（与 bigmoney-conflict-resolve SKILL 配方同构：A 族 union 律直接复用为读端逻辑）。
- **B 族（每机 gate/计量状态快照）**——写入位错置：每机 S6 链腿各写自己的态到共享位。车道化=写入位改名 `results/<face>.<machine>.json`，消费面取各机 max-cutoff（新鲜度）合并：`update_status.json`、`{heat,lhb,futures,fundamental}_*_status.json`、`token_usage.json`、`crash_fuse.json`、`market_clock/call_latest.json`。`fundamental_b_layer_filter.json` 710 写/0 消费=并行提请错峰降频审视（S6 链腿每轮重 derive，消费面零引用）。
- **C 族（确定性幂等再 derive·同字节）**：dashboard_status.json/js、daily_scorecard、strategy_scorecard、scorecard_v1、paper/*、prospect_promotion/*、paper_export/*。撞 add/add 无语义损失；车道化收益低，末批处理（消费面合并读 or 单机执笔）。

分批顺序：**批1=A 族**（吞行止血，合并读复用 skill union 配方）→ **批2=B 族**（写入位改名+新鲜度合并）→ **批3=C 族**。每批走拍板判据：双跑对账零漂移（车道 union/max-cutoff 视图 vs 单文件现状）→ 切换 → 兼容窗双轨观察。

## 三、回访判据（对齐拍板）

常态 UU 面 26→≤3（r86-r89 基线对账口径）+ rebase 密度下降；本普查件为迁移前基线锚（55 件/头部写入数），批 1 落地后按此表复测对比。

## 四、下轮指针

批 1 执行件起草：每件车道文件 schema（保留原 face 全字段+写手机器自署）+ 读端合并器 `scripts/merge_lane_views.py`（或复用各消费面内嵌合并）+ 双跑对账 harness（车道视图 vs 现单文件 diff 为零漂移证据）。

## 五、批 1 执行件已起草（bm-a r371·2026-09-28）

- **读端合并器**：`scripts/merge_lane_views.py`（library+CLI，L1 确定性零网络零引擎）。子命令：`merge`（合并视图摘要，不写仓件=零新增共享写面）/ `reconcile`（合并视图 vs 现单文件对账，exit 0=零漂移/1=漂移）/ `selftest`（离线合成件 18 腿全 PASS）。
- **车道文件 schema**：`results/<face>.<machine>.json` = 原 face 全字段原样 + 顶层 `lane_machine` 自署（与文件名矛盾=fail-closed，r98 身份律）；合并器固定源序=legacy 共享件打底→bm-a/bm-b/bm-c 车道件，全机同序同输出（确定性）。
- **配方=冲突解 SKILL 实弹律逐条复用为读端**：compute_audit=history ts 键并集+latest 嵌套深探取新（r311/D-09）；regime_state=整行 identity union（triggers/transitions/history）+flat 按 updated 取新；autofill_state=launches 整行去重→desc cap50→asc 写回（r245）+last_tick 内 ts dict 比较（r140）；runnable_pool=entry id union+done 吸收（r312）+**治理字段非空优先带注记（r370 坑律·lane_owner/lane_note/claimed_*）**；gate_attrition=整行 union 全量语义（47 消费面零丢失）；post_review_criteria=items id union+撞 id 归新 _reconciled ts 侧（r264 实弹先例）。
- **引导窗实弹证据（r371）**：`reconcile` 对真仓 6 面=6/6 ZERO-DRIFT（单源恒等引导证明=合并器恒等面成立，切换前基线锚）。
- **下一步（批 1 落地轮）**：writer 双轨接线——每机 S6 腿改写自家 `results/<face>.<machine>.json`（共享件照写=兼容窗双轨），跑 ≥2 轮后 `reconcile` 恒零漂移→消费面（build_status/daily_report）改 import 合并器读合并视图→再撤共享写面；批 2=B 族、批 3=C 族照本节协议推进。回访判据不变（§三）。
- **吞行第二向量载入（r371·MSG-0201 归因修正后实证）**：除 r348 族 resolver union 吞行外，**tick keepalive pre-defer 整文件重写=第二吞行向量**（实弹 10ce4d59 01:43:10：bm-b keepalive 自 pre-defer 分叉树整文件重写 runnable_pool.json -3031/+3032，回吞 lane_owner/lane_note 钉面+复活死认领；归因修正=bm-c 461c20d1 仅 shard owner 2+/2- 未吞任何面）；r351 pool-behind-origin defer 43146377 双向量全闭（fleet-wide），车道化终态后两向量同灭。
