# QA — census headline vs its own arms (r2157, bm-c, 2026-11-27)

**本轮两件产出，都在「判词是否说了它量到的事」这条轴上。**

## 1. 探针 + 面：`scripts/bench_census_arm_contradiction.py`

| 检查 | 命令 | 结果 |
|---|---|---|
| 离线自检 | `python scripts\bench_census_arm_contradiction.py --selftest` | **13/13 PASS** |
| 幂等/新鲜 | `... --check` | **CHECK_OK** 3 faces, 1 flagged |
| 生成面 | `...` | `results/bench_census_arm_contradiction.json` + `research/BENCH_CENSUS_ARM_CONTRADICTION.md` |
| 只读性 | 全文 | 不写任何 screen / face / verdict；只读已发布 `results/bench_*.json` |

读数：读 3 张 `config.type == "census"` 的面（其余 49 个 `bench_*.json` 因类型不符或非 bench 面被诚实列入 `skipped`，逐条带原因）。
**1 张 flagged**：

* `census_bond_futures` — headline `CENSUS_LEANS_POSITIVE`，5 条臂 **0 条 GO**，
  其中 1 条只清过 4.0% 绝对线（4.02%），最好臂 4.02%。
  判词 `LEANS_WITHOUT_A_PASS`。
* `census_commodity` — `CENSUS_LEANS_POSITIVE`，14 条臂 **2 条 GO** → `AGREES`。
* `census_index_futures` — headline 是 `CENSUS_UNPOWERED`（非方向性判词）→ `AGREES`。

**根因（代码级）**：`bench_generic.run_census()` 的面级判词只由

```python
powered = [r for r in rows if r["powered"]]   # 能不能分辨 target_edge
pos     = [r for r in powered if ann_pct > 0] # 符号是不是正
```

决定。`powered` 是**分辨率**陈述（MDE ≤ target_edge），不是**功绩**陈述；
判词里没有任何一处看过臂有没有过闸。于是「+1.2% 且 MDE 3.8」与「+9% 全过五检」
产出同一个判词词。

### 自检抓到的两处自身缺陷（当窗已修）

1. 首版把 `HEADLINE_CONTRADICTS` 排在 `LEANS_WITHOUT_A_PASS` 之后，
   腿 4（正面判词而最好臂 ≤0）被前一分支吃掉 → 调整为「方向相反优先于过不了线」。
   理由写进代码注释：说反了比说过头更严重。
2. 首版判据用「过了 H1 绝对线」代替「GO」，于是现场锚 `census_bond_futures`
   （1 条 4.02% 过线）被误判 `AGREES` —— **正是本轮要找的那个坑被自己的探针踩了**。
   改为按 GO 计数，并保留 `n_clears_h1` 作为次要证据同印。

## 2. 共享面修改：`scripts/bench_generic.py`（只新增字段，不改任何 verdict）

r2152 已量出「H1 那条 4% 线一半在量杠杆」（臂实现波动跨 4.45%–14.68%，
归一后过线 15→11 条），但一直挂在「等无竞争窗落闸」。本轮 `repo_write_contention`
rc=0 CLEAN，落闸如下：

| 新增字段 | 所在面 | 语义 |
|---|---|---|
| `arms[].size_normalized.{k, ann_at_target_pct, realized_vol_pct, declared_vol_pct, off_target, H1_normalized_ge, H1_flips_under_normalisation}` | 每张 bench 面每条臂 | 按面自己声明的 target_vol 重定价后重问 H1 |
| `benchmark_sizing.same_yardstick_is_a_claim_not_a_measurement` | 每张面 | 明写旧字段是对**代码**的陈述，不是对**两本书**的测量 |
| `benchmark_sizing.same_yardstick_measured.{bench_ratio, bench_off_target, arms_off_target, n_arms_with_realized_vol, not_measurable, same_size}` | 每张面 | 实测两本书的实现波动比 |
| `census.{n_arms_go, n_arms_clear_h1, headline_caveat, ...}` | census 面 | 判词旁边带上「几条真过闸」 |
| `run_census(...)` 返回值加 `headline_caveat` | 函数级 | lean 判词且 0 GO 时自动写一句解释 |

**没有改的**：`bc.verdict_of()`、`checks` 的键、`pooled` 判词字符串、
任何已发布 `results/bench_*.json`（本轮一次也没重跑它们）。

### 实弹验证（临时 config，跑完即删，零残留）

| 面 | 关键读数 |
|---|---|
| `reversal_commodity_5d`（pair，声明 8%） | 臂实现 8.66%（k=0.9238，off_target=False）；归一后 `ann_at_target_pct=-3.8535`；**基准实现 8.94% → ratio 1.1175 → bench_off_target=True → same_size=False** |
| `census_bond_futures`（census，声明 6%） | 基准实现 7.87% → **ratio 1.3117（偏 +31.2%）**；5/5 臂无波动数据 → `not_measurable="5 of 5 arms publish no realised vol"`、`same_size=null`（**不当作同尺寸**）；`caveat` 正确落进面：`0 of 5 arms passed all gates (1 cleared only the 4.0% H1 line)` |

第二行是 r2152 提到的具体数（「bond 篮子 4.86%@7.87%，归一 6% 后 3.76%」）的
机器可读版：它是**基准**比声明大 31%，不是臂小。

### 一处假绿在写的时候就拦下

`_same_size_measured` 首版对 census 臂（`run_census` 不保留 series，臂无 `vol_pct`）
会算出 `arms_off_target=0` → `same_size=True`。**沉默被读成达标**（r1311 族）。
改为要求 `n_arms_with_realized_vol == n_arms`，否则 `same_size=null` +
`not_measurable` 明写原因。

## 未做（如实）

1. **未重跑任何已发布 bench 面**，因此 21 张面上的 `size_normalized` / `same_yardstick_measured`
   仍缺，要等各自下一次 re-derive 才带上；本轮只保证新跑的面带全。
2. **未把 H1 改成归一后年化作为主判据**——那会推翻已发布 verdict 集合，
   属另一步（r2152 的「该冻的是归一后年化」仍需一次独立的判决面冻结）。
3. 全量 `python -m smoke_test` 未跑完（>10 min，r9 纪律允许分批），
   本面用 `--selftest 13/13` + `--check rc0` + 两次实弹直证。
4. `census` 臂缺波动，故 census 面无法做尺寸归一化——这是数据面的真实限制，已写进面字段而非隐藏。
