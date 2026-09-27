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
- **writer 双轨接线已落地（bm-a r372·2026-09-28 批1 writer 面）**：`config/lane_io.py`（共享库：machine_id 恒取 fleet/machine.json〔r98〕+write_lane 原子写〔dict-only fail-closed、default=str 对齐 regime 面、故障 stderr 披露不改写手 exit 契约〕+mirror_shared 种子/引导）；接线点=compute_audit.py（S6 腿）+market_regime.py（S6 腿）+Tools/autofill.py（`_save_state` 每跳写 state 车道；claim/keepalive/submit 三写点=镜像恰在 `git add` 前〔车道=本机最后一次提交的字节，反吞行记录〕；六处 byte-restore 点全部接 `_pool_lane_sync()` 防幻影认领；`_tick_owned_dirt` 扩两车道件=r290 自提交律同载）；合并器补丁=load_sources 读入即剥离 `lane_machine`（签名非面数据，不剥离则 reconcile 在真车道在场时必假红）+selftest 两腿；autofill selftest 接线面全 PASS（S15i/S15i2/S17e add 元组扩车道+S15l 认领车道+S15m defer 回滚零幻影+S18d state 车道+S17g submit 车道）；引导窗实弹=r372 S6 链跑后 reconcile 6/6 ZERO-DRIFT（4 面 2 源〔legacy+bm-a 车道〕+2 面单源）。bm-b/bm-c 侧同款接线随其轮次拉取本批代码自动生效（S6 腿/tick 同仓库代码），无需跨机协调。
- **批1 剩余面（下轮指针）**：gate_attrition（写手散布在各批 runner：aggressive_lab/alloc_backtest/bandit_queue/aggr_capacity_probe/aggr_fullpool_battery 等）+post_review_criteria（写手=各批 register 一次性脚本）→ 下一 slice 以 `config.lane_io.write_lane` 逐点接线；消费面切换门槛不变：≥2 轮 reconcile 恒零漂移→build_status/daily_report 改 import 合并器→撤共享写面。
- **散布写手面落地=镜像维护路由（bm-a r373·2026-09-28 批1 收口面）**：GA/post_review 写手≈40 活点+每波 prereg 新增一次性脚本——逐点接线结构性衰减（新写手恒漏接）；改走 `lane_io.mirror_shared_if_changed`（r372 库函数本为此设计）：payload 语义比较幂等（无变化轮零写零 churn、格式无关不受写手 indent 混用影响），宿主=compute_audit S6 腿（每轮每机必跑，r372 接线点同款）——吞行窗口=轮尺（写手轮内写→同轮 S6 腿镜像恰在 push 前→git 提交+union 双兜底）。种子实弹=2 车道件落地（154,233B/120,358B，lane_machine=bm-a 自署）。**观察窗第 2 轮真漂移捕获+合并器修法**：bm-a 池车道件=r372 陈快照（V2-P1 shard owner_since 02:13:19）vs 共享活面（bm-b keepalive 02:33:18）→ shards 整行 identity union（_row_id=全行 JSON）不吸收同 key 异时行→重复行=DRIFT——正是双轨观察窗用途；修法=`_union_shard_rows` **key 分组合并**（key=身份、owner_since=新者基座 r311 latest.ts 律+缺字回填 r370 非空优先律族、无 key 行保整行 append-log union、同侧同 key 重复自愈）；吞行方向不减（共享回吞旧 fork→车道新 keepalive 行胜出恢复）。selftest +3 腿（lag 吸收/keyless 回退/吞行恢复）22/22 PASS；reconcile 修后 6/6 ZERO-DRIFT 且**六面全 2 源**（首读）。消费面切换门槛重锚（诚实口径）：全 6 面 2 源拓扑的零漂移读数从 r373 起算，≥2 轮恒零漂移→build_status/daily_report 改 import 合并器→撤共享写面；bm-b/bm-c 拉取后其车道件自动生效，三源拓扑（legacy+双车道）读数随其后轮次累计。
- **吞行第二向量载入（r371·MSG-0201 归因修正后实证）**：除 r348 族 resolver union 吞行外，**tick keepalive pre-defer 整文件重写=第二吞行向量**（实弹 10ce4d59 01:43:10：bm-b keepalive 自 pre-defer 分叉树整文件重写 runnable_pool.json -3031/+3032，回吞 lane_owner/lane_note 钉面+复活死认领；归因修正=bm-c 461c20d1 仅 shard owner 2+/2- 未吞任何面）；r351 pool-behind-origin defer 43146377 双向量全闭（fleet-wide），车道化终态后两向量同灭。
- **消费面切换已落地（bm-a r374·2026-09-28 批1 consumer-switch 轮）**：门槛达标=r373（六面全 2 源 6/6 ZERO-DRIFT·首读）+r374（reconcile 6/6 ZERO-DRIFT·三核心面已 4 源〔legacy+bm-a/bm-b/bm-c 车道件随 r355/r125 批入树=三源拓扑提前累计〕）=≥2 轮恒零漂移；切换=两消费面 A 族读点全部改走合并视图——`monitor/build_status.py`（4 面 7 读点：compute_audit×2/regime_state/runnable_pool×3/autofill_state，`_lane_view(face)` helper+scripts sys.path 先例=alloc_backtest L64-65 双插法）+`scripts/daily_report.py`（2 面 2 读点：compute_audit/runnable_pool）；行为面=零漂移切换（消费面自身导入路径 FACE-EQ 6/6 断言 merged==shared+编辑前后基线语义 diff：dashboard 11 行全为墙钟派生字段〔age_min/generated_at/token_line 再生链〕、daily_report JSON 孪生 diff=generated_at 唯一行〔文档口径〕+md 面仅生成时间行）+daily_report selftest PASS+合并器 selftest 22/22；fail-closed 保留=lane_machine 矛盾 SystemExit 直传（消费面诚实崩=R209 族零静默降级），无源=诚实 {}（原 not-yet 语义不变）。**共享写面仍双轨在写（writer 面未撤）**——撤共享写面=批1 末步，前置=全机队消费切换代码拉齐+≥N 轮消费面读数稳定（bm-b/bm-c 拉取本批后其 build_status/daily_report 自动走合并视图）；后续观察点=每轮 reconcile 零漂移持续（三源读数随 bm-b/bm-c 消费切换累计）。

## 六、批 2（B 族 gate/计量快照）slice-1 已落地（bm-a r375·2026-09-28）

- **合并器 B 配方**（`scripts/merge_lane_views.py` 扩展，A_FACES 不动）：新增 `B_FACES` 8 面=update_status/heat_update_status/lhb_update_status/futures_update_status/fundamental_status/token_usage/crash_fuse/market_clock·call_latest；三配方类——①`_make_take_new(face, probe)` max-cutoff 整取（census 冻结口径；probe 逐面=updated/updated/ts/updated/generated/asof；tie→first-seen=legacy=单源 reconcile 恒零漂移含 probe 缺失面）；②`merge_heat_update_status`=**宿主车道优先**（R31 法：`_HEAT_HOST="bm-a"`——heat snapshots 派生自宿主机本地 data/heat 面〔gitignored〕，非宿主新 ts no-op 写非权威〔ts新≠数据权威新〕；宿主车道在场=整取，否则回退 max-cutoff=预接线轮保持现状语义如实披露）；③`merge_crash_fuse`=sigs 按 key 并集+同 key newer-event-wins（last_crash_ts/last_refusal_ts 取大侧；fuse=单调计数面禁 last-writer 盲取）。CLI 面 A_FACES→ALL_FACES（merge/reconcile/--face 校验同步）。
- **写手双轨接线（7/8 面）**：`config/lane_io.py` _KNOWN_FACES 扩 8 B 面；写点接线=update_daily（`_write_status_atomic` path==STATUS_PATH 守卫=selftest 隔离面不写车道）/update_lhb（save_status）/update_heat（save_status+**宿主守卫** machine_id()==HEAT_LANE_HOST 才写车道）/update_futures（write_status）/update_fundamental（`_atomic_write_json` path==STATUS_PATH 守卫=PROBE_PATH 写点排除）/token_meter（OUT_PATH 写后）/market_clock_call（run() call_latest 写后；l3_activation_table=census「B/C」双标 C 侧面·确定性重 derive·归批 3）；全部 fail-soft（write_lane 故障 stderr 不破写手 exit 契约）。**crash_fuse 写手（Tools/autofill.py tick 族）未接线**=批 2 尾步（tick 关键码低风险窗口另轮）。
- **验证链**：合并器 selftest 35 腿全 PASS（A 23+B 12：8 面 bootstrap 恒等/take-new 新鲜度/heat 宿主优先〔clobber 0 负面例〕+回退/crashfuse 并集+新事件胜/call_latest asof）；写手 selftest 5 件全 PASS（update_daily 实跑 0 新行 no-op+guards/update_lhb 23 例/update_heat 13 例/update_futures 10 例/market_clock_call 8 腿）；py_compile 9 件 rc=0；smoke 25/25。
- **实弹读数（r375 当轮）**：6 车道件落地（update_status/heat/lhb/futures/token_usage/call_latest 全 lane_machine=bm-a 自署；fundamental=<24h skip 本轮无写=接线待下真实快照窗）；reconcile **14/14 ZERO-DRIFT**（A 6 面 4/4/4/3/2/2 源维持+B 面 6×2 源+2×1 源）——B 族双轨观察窗第 1 读数在案，门槛口径同批 1（≥2 轮恒零漂移→消费面切换→撤共享写面）。
- **观察窗实弹第 2 捕获+合并器修法（r375 收尾窗·r373 同款范式）**：autofill 面 4 源拓扑首读即 DRIFT——根因=merge_autofill_state 原整行 identity union 违 **r322 律**（同复合键行跨源两字段面：V2-P1 02:30:01 崩溃发射行 enriched 面带 crash_counted=true、陈 lane 面缺席→整行并集静默双存同键行→union 51→cap50 挤掉共享件仍在的 09-26 最旧行）；修法=launches 改**复合键去重先行**（六字段 ts/machine/pid/runner_sha256/entry/shard）+**增补字段并集保一条**（字段集差=增补面）+真分歧（公共字段值冲突）=fail-closed SystemExit 旗标升级禁静默双存（R209 族）；selftest +2 腿（去重并集/真分歧 fail-closed）37 腿全 PASS+reconcile 14/14 恢复 ZERO-DRIFT。批 1 时窗（r371-r374）未触发=彼时 autofill 车道源≤2 且无 enriched/陈面分叉窗；4 源拓扑（bm-b/c 车道件随其批入树）首暴露——观察窗判据有效性实证。
- **批 2 收口面已落地（bm-a r376·2026-09-28）：crash_fuse 写手接线 8/8 全通**——`Tools/autofill.py` `_save_fuse` 尾接 `_write_lane_file(FUSE, f)`（三写点 confirm/refuse-count/fix-clear 自动全覆盖·`_save_state` 同构双轨律）+`_tick_owned_dirt` 扩 fuse 车道件（r290 自提交律三车道全载：state/pool/fuse）；selftest +S18e 腿（fuse 车道签名+sigs 字节对齐）62/62 PASS，S15i/S17e add 元组断言六元组更新（S17e 含 `_lane_fu`）。
- **观察窗第 3 捕获（r376·共享件字段面丢失·非合并器缺陷）**：4 源拓扑第 2 读 DRIFT≠合并器配方错——根因=r375 push-storm wave-2 **手工 resolve 脚本整行 tie→HEAD 取侧**（bm-a 本地铁面）丢 V2-P1 02:30:01 发射行 enriched 字段面 `crash_counted=true`（发射机 bm-b 车道=唯一权威真相面），共享件该行裸失字段；风险=发射机 `_confirm_crashes` 重复计数推高 fuse count 污染证据面；修复=`results/_r376bma_state_field_restore.py`（共享件+本机 lane 镜像补字段·他机车道 R31 不碰·reconcile 恢复 all faces zero-drift）+MSG-0350 预警 bm-b pull 自愈。教训入册：**push-storm 手工 resolve 后必须同窗跑 reconcile**（观察窗判据捕捉面=合并器缺陷+resolve 脚本取侧缺陷双面）；resolve 脚本应 import 合并器配方而非整行取侧（防再犯面，归批 3 工程债清单）。
- **下轮指针**：①B 面 reconcile 读数随 bm-b/bm-c 拉取本批后其车道件自动累计（三源拓扑）；②批 1 撤共享写面前置不变（全机队消费切换码拉齐+读数稳定）；③批 3=C 族（dashboard_status/daily_scorecard/paper 族确定性重 derive+l3_activation_table）照 §五协议+resolve 脚本配方统一工程债。
- **resolve 配方统一已落地（bm-a r377·2026-09-28·③工程债收口）**：`scripts/merge_lane_views.py` 新增 `resolve` 子命令——push-storm 撞 UU 时一行收口：直读 rebase 三 stage（:2:=origin 侧/:3:=本地侧·r351 定向律）→merge_face 配方 union→落盘+parse-verify+同窗 reconcile 提示；车道文件/非 ALL_FACES fail-closed（lane 文件=R31 机主权威禁 union、snapshot/twin 类归 skill 配方）；同秒 tie→:2: origin（r140）；`--stageN/--out` 取证回放模式；selftest +7 腿（detect 三腿/r376 双存坍缩/pool 治理钉/tie 定向/无 stage fail-closed）44 全 PASS；**实弹复验**=r376 历史三 blob（:2:=c130be39 bmb 51 双存/:3:=88140393 bma 修复面/:1:=53be4125 base）经 CLI 复算与已落地收口面（63dbbc0e）**语义恒等**（50 launches、V2-P1 enriched 单行保 crash_counted、last_tick 03:30:02）——r376 坑律从「resolve 件应 import 配方」升格为「一行命令收口」，手写 union 面=违反正典。SKILL 双胞胎（Tools+.codely-cli）路由行同步加注。

## 七、批 3（C 族确定性幂等重 derive）slice-1 已落地（bm-a r378·2026-09-28）

- **终态选型=单机执笔（census §二正典二选一）而非车道件**：C 族面全机字节恒等（仅 generated_at/age_min 墙钟包络字段异）——每机车道件=3× 存储 pure churn 零语义收益；且 `dashboard_status.js` 消费面=file:// 静态 HTML（bigmoney/dashboard/town.html 直载）**无法合并读**，车道读端方案对该面结构性不可行。单机执笔按 R31 host-guard 既有判例（sysv1_paper=bm-a/astock=bm-b/fund_premium=bm-c 同款）零消费面改动。
- **守卫件**：`config/lane_io.py` 扩 `C_SINGLE_WRITER_HOSTS`（6 面：dashboard_status.json/.js + daily_scorecard.json/.html + strategy_scorecard.json + scorecard_v1.json）+`C_HOST_STALE_MIN=20.0`（O-2100 s2.4 STALE_MIN 律）+`shared_derive_write_allowed(face)`——host 恒写；非 host 心跳新鲜（<20min）=诚实 stdout skip；host 心跳停/不可读=健康机 stale-takeover（幂等 derive 使接管竞争=平凡近同字节 add/add，非吞行风险）。fail-open 双腿：面不在册=照旧写（逐面显式 opt-in）、machine_id 不可读=照旧写（r98 不猜身份）。`_host_heartbeat_age_min`=heartbeat_epoch_utc int 优先（smoke-F7 面）→last_seen ISO 回退，缺件=死机面接管。selftest 7 腿 hermetic（host 恒许/非 host 新鲜 skip/陈 25min 接管/死机接管/未册面 fail-open/无 mid fail-open/边界=）7/7 PASS。
- **写手接线（3 脚本 4 面）**：`monitor/build_status.py` main() 前置守卫（dashboard_status.json/js 双面）+`scripts/daily_scorecard.py` __main__ 前置（json/html 双面）+`scripts/strategy_scorecard.py` main() run 路径前置（selftest/calibrate 路径不碰；strategy_scorecard.json+scorecard_v1.json 经 sc.run 随刷同守卫覆盖）。非 host 输出=守卫一行诚实 stdout+exit 0（S6 链 rc=0 无感）。
- **验证链**：py_compile 4 件 rc=0；lane_io selftest 7/7；真实 bm-a 心跳年龄实读 7.3min（int epoch 面活数据）；非 host 仿真（mid=bm-b+host fresh）6 面全 False=skip；host 实弹三腿 rc=0（build_status 正常双写/daily_scorecard 6 traders/strategy_scorecard selftest 6+5+10 全 PASS+run 6strat/28trader/7port 8.2s）。
- **写入量预期**：四固定面写入轮频从 3 机×每轮=3× 降至 1×（census 基线 dashboard_status.json 770/js 759/daily_scorecard 207/strategy_scorecard 205/scorecard_v1 207 写）；bm-b/bm-c 拉取本 commit 后其 S6 腿自动 skip（同仓代码生效，无需跨机协调——r372 同款）。回访判据（D-03 拍板）=常态 UU 面 26→≤3+rebase 密度下降，批 3 slice-2 落地后按 §三复测。
- **slice-2 剩余面（下轮指针）**：paper 族（live.paper marks→paper/*_paper.json、prospect_paper/_summary、t35_open_fill_verify）+prospect_promotion/PROS-*族+_summary+paper_export/*（含 latest.json）+market_clock l3_activation_table（r375 批 2 遗留 C 侧腿）+census_fusion 一次性件——全部 bar-gated/新 bar 窗才写，写频低一档，照本节协议（单机执笔+stale-takeover）逐批接线。
- **观察窗第 4 捕获+合并器修法（r378 当轮·r373/r375/r376 同款范式）**：post-chain reconcile 首 DRIFT=runnable_pool 面——根因两层：①**会话面池编辑绕过车道镜像**（bm-b 会话 03:43:45 defer V2-P1→waiting+defer_note 落共享面 4cdc710f，其车道件停 03:43:08 tick 镜像=pre-defer ready；车道写点只在 autofill tick 提交流，会话 defer/flip 一次性脚本不写）；②**合并器异状态枝 rank {ready:2,waiting:1} 复活蓄意 defer**（池级 updated_at 三源同值 00:41:57=无 per-entry ts 可排序，陈 lane bare-ready 无标记证其新）且整侧取侧丢弃败侧治理注记（defer_note 裸丢）。修法=①defer_note 入 GOVERNANCE_FIELDS（r370 非空优先族）；②**marker 律（风险不对称定谳）**：marked-waiting（waiting+非空 defer_note）胜 bare-ready——吞 defer=autofill 重燃蓄意压批（双烧/RAM 挤）高害，吞 un-defer=漏填一轮+镜像自愈低害；双侧有标记→rank 回退；胜侧恒做治理字段并集+shards key-union；③un-defer 惯例=flip 回 ready 必清 defer_note（残留窗=轮尺，reconcile DRIFT=探测器）；④车道滞后根修=runnable_pool 入 compute_audit S6 腿 mirror_shared_if_changed 族（r373 散布写手律：会话写→同轮 S6 镜像）。selftest +3 腿（marker 胜 stale-ready/治理并集/双标记 rank 回退）47 全 PASS+reconcile 14/14 ZERO-DRIFT 恢复+本机车道镜像实弹补齐（bm-a lane V2P1=waiting+defer_note ✓）。坑律入册 CODELY r378 条。
