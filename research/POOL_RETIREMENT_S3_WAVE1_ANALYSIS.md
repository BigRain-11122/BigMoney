# POOL_RETIREMENT_S3_WAVE1_ANALYSIS —— T-116 s3 wave-1 决策读点切换安全分析（settle-vs-merge 重入序）

- 法源：T-2026-09-29-116-P1 s3（"reader migration in two waves with dual-run reconciliation"）＋普查件 research/POOL_RETIREMENT_S1_CENSUS.md §四（wave 划分=本件的输入）＋D-20260928-03(1) 结构终态。
- 产出轮：bm-c r196（2026-09-29）。本件=wave-1 **切换前置件**：只做安全分析与对账仪器接线，**不改任何读点**（flip 按门判另轮执行）。
- 工程件零回测零引擎零判据面；正典引用实读=Tools/autofill.py（r388 后）、Tools/fill_ladder.py、scripts/compute_audit.py、scripts/merge_lane_views.py（L351 merge_runnable_pool / L593 face_view / L607 sync_face）。

## 一、wave-1 读点形状（代码实读，行号=当前 HEAD）

| 读点 | 形状 | flip 后读源 |
|---|---|---|
| autofill tick 主读 L1122 | 单次 `open(POOL)` 全量读，一份数据喂 `_pick`/`_keepalive_claims`/`_confirm_crashes` 三腿 | `face_view("runnable_pool")`（合并视图） |
| autofill claim 鲜读 L843 | 变更基（mutation base）+ `prev` 共享字节（回滚用） | 基=合并视图；`prev` 字节对回滚律**不动**（F7） |
| autofill keepalive L992 | 只读 prev 字节；变更基=入参（tick 主读那份） | 随主读翻转 |
| autofill harvest L1347 | 独立全量读 | 合并视图 |
| fill_ladder 读侧 L184-185 | 共享面全量读（ready 计数+existing_ids 幂等+judge 族扫描） | 合并视图（写侧 double-file 律不动） |
| compute_audit ready 扫描 L193-200/L291-313 | 共享面 status 扫描（审计样本） | 合并视图（L501-524 sync_face 写手不动） |

## 二、settle-vs-merge 重入序八判（F1-F8）

- **F1 定点律（切换的代数基础）**：r388 后每条写路径终点都是 settle（`_pool_settle`→`sync_face` 联合并集写回）——所有外部可见态满足 `shared == union(lanes)`。并集幂等、全写原子（os.replace）、两侧字节回滚（`_pool_rollback`）恢复同一化 → **合并视图读与共享读在一切 settle 态下语义恒等**，切换是读源换名不是语义变化；对账仪器的任务就是把这条等式做成经验证据。
- **F2 外部可见窗不存在 lane-ahead**：r388 自提交把 lane+shared 落进**同一个 commit** → origin 可见态永远 settle 过。lane-ahead 只存在于 (a) 单进程内微秒窗（跨机不可观测）(b) 降级回退（settle 故障→内存直写共享，已文档化的最后手段）。两窗都不被对账采样捕获=证据面的合法盲区，如实注记。
- **F3 tick 进程内自洽**：keepalive 写 lane→settle 后，claim 鲜读（flip 后=合并视图）读到的是 settle 并集——与 flip 前共享鲜读同一状态。**翻转不引入任何新的读写交错面**。
- **F4 降级模式反而改善**：flip 前降级直写共享的内存副本来自可能过时的共享读（r348/r120/r375 盲覆盖族的降级复活面）；flip 后变更基本身=并集 → 降级直写携带并集=吞行风险单调收窄。
- **F5 回滚律不受影响**：claim/keepalive 的 `prev`/`prev_lane` 是**文件字节**（回滚还原文件），视图是派生量——字节还原后合并视图随派生源自动还原。零改动。
- **F6 origin 守卫必须同 commit 扩径（唯一硬前置）**：`_pool_origin_stale` 现只 diff 共享 relpath（HEAD...origin/main）。flip 后决策数据**还**派生自三条 lane relpath → 守卫须一次 diff 四径（`git diff --quiet HEAD...origin/main -- <shared> <lane-a> <lane-b> <lane-c>`，defer-yield 语义/幂等再认领律全不变）。**autofill flip 与 F6 必须同一 commit 落地，禁止分开。**
- **F7 dispatcher churn gate（#3 读者）不随 wave-1 动**：锚=「池 mtime/origin sha 变化」；option (a) 下共享面仍是 settle 工件，锚存活。s4 若选 (b) 才需重锚（普查 §四事实重述）。
- **F8 pool_worker origin-blob 协议（#2 读者）不随 wave-1 动**：git 传输面（普查 wave-1 划分重述），跟随 s4 拍板。

## 三、flip 计划（门判后执行，非本件动作）

1. **门**：`pool_dualrun_reconcile.py status` 三机 streak ≥3 连续绿＋三机 harness selftest 绿＋flip commit 当轮 smoke 绿。
2. **序**：compute_audit ready 扫描（纯读最低险）→ fill_ladder 读侧 → autofill 三读点+F6 守卫扩径（一个 commit）。
3. **回退**：读点类改动=单 commit revert 即回滚（无状态迁移、无数据改写）；证据 jsonl 保留作审计轨迹。
4. **验收口径**：科学面（entries/status/shards 字节）全程零改写——证据行 sha_shared==sha_merged 即字节级证明。

## 四、对账仪器契约（本轮已接线）

- `scripts/pool_dualrun_reconcile.py`：run（采样+追加 `results/pool_dualrun.<本机>.jsonl` 尾留 50 行·行带 evidence_cutoff=共享面 updated_at·consecutive_green 连绿计数 drift 即清零）/ status（只读门判·三机聚合）/ selftest（离线 10 腿全绿 r196 实测）。
- 比较语义=merge_lane_views 本体（load_sources+merge_face）——**零重实现**；r374 一次性 CLI 探针（`reconcile --face`）保留不替代，本件加的是**留痕 streak 证据面**。
- **链序律：必须排在 compute_audit 之前**（后置=sync_face settle 先愈漂移=证据空洞）。
- drift=观察相数据非故障：exit 0 照录（行内 drift=true 诚实携带），仅机制故障 exit 2。
- 反重复：全仓 scan 零既有 dualrun 仪器（r196 实测）。

## 五、遗留与下轮指针

- bm-c streak 1/3 已起算（r196 首行 ZERO-DRIFT·107 entries·cutoff 2026-09-29T01:00:30+08:00）；bm-a/bm-b 待其轮链自然起算（prompt 腿随 git 分发）。
- 三机 streak 齐 3 后：按 §三 flip 序开刀；fill_ladder/compute_audit 的 flip 同门同判。
- s4 拍板输入齐全（普查 §四+本件 F7/F8）；option (a) 证据倾向维持。
