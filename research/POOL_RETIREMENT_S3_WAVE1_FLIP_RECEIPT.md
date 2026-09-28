# POOL_RETIREMENT_S3_WAVE1_FLIP_RECEIPT —— T-116 s3 wave-1 读点切换执行回执

- 法源：T-2026-09-29-116-P1 s3＋安全分析件 `research/POOL_RETIREMENT_S3_WAVE1_ANALYSIS.md` §三 flip 计划（门判后另轮会话动作）＋D-20260928-03(1) 结构终态。
- 执行轮：bm-c r203（2026-09-29 晨）。执行体=当轮 OS 循环会话（r202 addendum 预告的 executing-session checklist 即本件）。
- 工程件零回测零引擎零判据面；科学面（entries/status/shards 字节）全程零改写。

## 一、门判三证（§三.1）

| 门 | 证据 |
|---|---|
| 三机 streak ≥3 连续绿 | `pool_dualrun_reconcile.py status` @flip 前一刻：bm-a 3（05:28:00·cutoff 2026-09-29T01:00:30+08:00）/ bm-b 3（06:29:57·cutoff 06:00:54）/ bm-c 8（06:31:20·cutoff 06:00:54）→ **wave-1 flip gate: READY**（零漂移证据行=三机 `results/pool_dualrun.<mid>.jsonl`，行带 evidence_cutoff+consecutive_green，drift 清零律在位） |
| 三机 harness selftest 绿 | 同一代码经 git 分发三机同字节；执行轮复跑 `pool_dualrun_reconcile.py selftest` ALL PASS（10 腿） |
| flip commit 当轮 smoke 绿 | 落地前 `python -m smoke_test` 26/26 PASS（两次：轮首+flip 编辑后） |

## 二、切换面（§三.2 序：compute_audit → fill_ladder → autofill+F6，单 commit）

| 读点（分析件 §一表） | 切换 | 文件 |
|---|---|---|
| compute_audit ready 扫描 ×2（pool_ready_count / pool_ready_entries） | → `_merged_pool()`（face_view 合并视图；全源缺位=None 保持 pre-flip missing-shared parity；损坏/身份矛盾=fail-closed None） | scripts/compute_audit.py |
| fill_ladder 读侧（existing_ids 幂等+floor/judge 门） | → `_merged_pool_view()`（写侧 double-file 律不动） | Tools/fill_ladder.py |
| autofill tick 主读（L~1122） | → `_pool_merged_view()`（{}=全源缺位=pool_absent 诚实 no-op；损坏=ABORT rc2·r201 refuse-act-on-unknown 诚实扩至全部源面） | Tools/autofill.py |
| autofill claim 鲜读（L~843） | 变更基=合并视图；**prev/prev_lane 文件字节=回滚律不动（F5/F7）**；合并视图不可得=yield 下轮重试 | Tools/autofill.py |
| autofill keepalive（L~992） | 零改动（变更基=入参=tick 主读那份，随主读翻转——分析件 §一原判） | — |
| autofill submit 重复检查（L~1347） | → 合并视图（lane-only 条目正确拒同 id 双加）；损坏=ABORT rc2 | Tools/autofill.py |
| **F6 origin 守卫** | `_pool_origin_stale` 一次 diff 四径（shared+三 lane relpath）——**与读点切换同 commit 落地（F6 同 commit 硬律）**；defer-yield/幂等再认领语义不变 | Tools/autofill.py |

Selftest 夹具卫生（hermetic 完整性）：`_pool_lane_clear()` 帮手+8 个直写位——每腿 plant 决策态于共享面并清陈 lane，使 merged==bare（合并律自有 selftest 承载，claim/tick/submit 腿只测各自决策逻辑）。

## 三、验证回执（执行轮实跑）

- `Tools/autofill.py selftest` ALL PASS（S15-S19 全腿含 lane-primary/回滚/settle 腿）；
- `Tools/fill_ladder.py selftest` 全断言 PASS；
- `scripts/compute_audit.py selftest` 26/26 PASS；
- `scripts/pool_dualrun_reconcile.py selftest` ALL PASS；
- `python -m smoke_test` 26/26 PASS；
- 实弹只读验证：`merge_lane_views.py reconcile --face runnable_pool` → **ZERO-DRIFT（4 sources，merged==shared）**；`fill_ladder.py --dry-run` 合并基幂等 honest no-op（compatible_ready=0<3）；compute_audit 探针 ready_count=2/entries=2（与水位面 2 ready bm-b 车道一致）。

## 四、回退与遗留

- 回退=单 commit revert（§三.3：读点类改动无状态迁移无数据改写）；零漂移证据 jsonl 保留作审计轨迹。
- **s4 已拍板 CLOSED（bm-c r204·2026-09-29）**：共享面处置=**option (a) derived-view-only 保留**——依据=`POOL_RETIREMENT_S1_CENSUS.md` §四.3（(a) 保 pool_worker 单 blob origin 读协议〔F8〕+dispatcher churn gate 锚〔F7〕+三机 git 传输契约；(b) 三面全破且代价集中跨公司工人端）+flip 后 dualrun streak 9 GREEN 零漂移实证 merged==shared（F1 定点律）=保留零成本；手写白名单=fill_ladder double-file 写侧（律定不动）+会话一次性 defer/flip 脚本+未来批 runner 注册件，此外共享面零手写；法注已落 `fleet/README.md` §4（v1.2）。
- flip 后观察相：三机 dualrun 链腿继续逐轮采样（链序律：排 compute_audit 之前不变）；任何 drift 行=观察相数据如实照录。
