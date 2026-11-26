# QA — r2160：控制臂「没复现发布书」的 0.60pp，其实是两个面差了一根 bar

日期 2026-11-27（轮 r2160，bm-c）｜触发 = r2159 留下的最重欠账「`etf_book_rebal_adoption` 控制臂 10.89% vs 发布 11.49%，差 0.60pp」

## 一、先纠正上一轮记录里的那个 11.49

r2159 写下的「发布面 11.49%」**不是从面上读来的**，是从记忆里 r1934 条目的旧数字搬来的。今日实测：

| 来源 | nobond_vt08 CAGR | evidence_cutoff |
|---|---|---|
| `git show HEAD:results/etf_nobond_vt.json` | 10.96% | 2026-11-25 |
| 重跑后工作树上面的 | 10.89% | 2026-11-26 |

两条都是 10.9% 量级，从来没有 11.49%。11.49% 是 r2048 那一代面板的读数——**「发布书」不是一个冻结数字，它每轮被链腿重算**。

## 二、真因：链序，不是算术

`Tools/s6_chain_bmc.py` 里这条腿原来排在 2075 行，而它复现的那本书的写者腿 `etf_nobond_vt` 排在 2658 行。于是：

1. 面板推进一根 bar；
2. 本轮的 `rebal_adoption` check 先跑，读到的是**上一轮**写下的发布面（旧 bar）；
3. 重算用的是**本轮**面板；
4. 两本书差一根 bar → 0.07pp 差异 ≫ 0.05pp 容差 → 脚本印 `CONTROL_FAILED`；
5. 而 `run_leg::_repairable` 只认 `stale` / `face missing` 两个词 → 链**永远不买重生** → 面冻在旧 bar 上，只有人手动跑一次才绿。

这正是 r1850 / r1934 立的那条规矩的反面实例，与 r2159 修掉的五条同类。

## 三、修法（四个面，逐条可查）

| # | 位置 | 改动 |
|---|---|---|
| 1 | `compare_faces()` | 新增：两本书是否在同一根 bar 上（`SAME_FACE` / `FACE_LAG` / `UNKNOWN`）。不同 bar 上算出来的差不是算术差 |
| 2 | `book_moved()` | 新增：**外部锚**——盘上发布面现在停在哪天 vs 本面写下的那一天。前进 = `STALE`（重跑本面能修）；倒退 = `FACE_LAG`（本面修不了，要上游腿） |
| 3 | `check()` | 先问外部锚，再问自身自洽；`reproduces_published` 改为**重算**而非信任面里存的字（r1935 族：只会自我一致的守卫没有「我过期了」这个状态） |
| 4 | `refresh()` | 面自称 `FACE_LAG` 且书比本面还旧 → 拒绝白跑 68s，点名上游腿；书追上了 → 判 `REFRESH_STALE` 并重生 |
| 5 | `Tools/s6_chain_bmc.py` | 两条腿（`rebal_adoption_write` / `rebal_adoption`）**从 2075 行移到 `etf_nobond_vt` 之后**，原位置留说明 |

设计取舍：`FACE_LAG` 刻意**不含 STALE 字样**。说 STALE 会让链付一次 68s 重生，而重生改不了「对面那本书是旧的」——那是用钱买一个不变的红。

## 四、验证证据（逐条实跑）

- `selftest`：**25/25 PASS**。新增六腿——P/Q/R 纯函数（lag / same / unknown）、V 发布面自称可读、W 前进=STALE·倒退=LAG、S/U/T 三条**行为腿**（把真面拷到临时路径、改一格、置 `globals()["OUT"]` 与 `globals()["CONTROL_RECEIPT"]`、调真 `check()`、断言 rc 与词在场/不在场、finally 复原）。
- `check`（绿态）：`CHECK_OK verdict=PHASE_DEPENDENT cells=20 phases=5 pass_share_10bp=0.20`。
- 链腿实跑（`--only=etf_nobond_vt,rebal_adoption_write,rebal_adoption`）：**3/3 rc0，65.5s**（nobond_vt 54.2s → adoption_write 10.3s `REFRESH_NOOP` → adoption 0.9s `CHECK_OK`）——次序修正确认生效。
- **端到端自愈实证**（手动把发布面退回 2026-11-25、把本面 face_state 改成 FACE_LAG）：
  1. `check` → `FACE_LAG … repricing this file cannot change that` rc=1（**不是** STALE）
  2. `refresh` → `FACE_LAG the published book is on 2026-11-25, behind this face's 2026-11-26` rc=1（**拒绝白跑**）
  3. 上游腿 `etf_nobond_vt` → 54.0s 重生，书回到 11-26
  4. `refresh` → `REFRESH_RAN 2026-11-26 -> 2026-11-26 (74.6s) rc=0` → `check` 绿
- 下游两枚消费者（`etf_book_cadence_comparable` / `etf_book_cadence_start_dates`）在面推进后先报 STALE，重生后各自 `CHECK OK`（5 rungs / 200 matched pairs；42 cells / 22 starts）。

## 五、如实记的欠账（本轮未做）

1. **未跑全量冒烟**：本轮改动集中在一条腿与其下游，逐腿实跑为证（selftest 25/25、三腿链跑、四步自愈），不宣称套件总数。
2. `etf_book_cadence_comparable` / `etf_book_cadence_start_dates` **没有链腿**（r1282 孤儿类）：它们的输入一推进就 STALE，只能人工重跑。本轮已重跑至 11-26，是否接链需另轮评估。
3. r2159 的另外三条欠账（CEO 页 declared starting book、`bets`/`derisk` 两节无链腿、`ah_panel` 采样尾记录）本轮未动。
4. 本次上移的两条腿依赖 `etf_nobond_vt` 腿本轮成功；若上游腿失败，本面会以 `FACE_LAG` rc=1 挂红——这是设计意图（红在出错的那一环），但不是自愈。
