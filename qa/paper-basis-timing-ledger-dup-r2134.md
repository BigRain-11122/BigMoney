# QA r2134 · 基差定仓位纸盘台账重复计收益

轮号 r2134（bm-c）｜发现日期 2026-11-26｜发现者：做「carry 里成本吃掉多少」时的逐日对撞
证据面：`results/paper_basis_timing_cost_split.json` → `ledger_health`
读者页：`research/PAPER_BASIS_TIMING_COST_SPLIT.md`
工具：`scripts/paper_basis_timing_cost_split.py`（`--selftest` PASS / `--check` rc0 / `--ledger-gate` rc4）

## 一句话

纸盘台账 `results/paper_basis_timing/LEDGER.json` 里**同一个交易日存了两行**，
而读者页把每一行都乘进 (1+carry)，所以它印的 IC「累计 carry 370.06%」是重复计出来的，
**一天一行的真读数是 155.92%**（年化 10.66% → 10.07%）。

## 数字（可逐项复算）

| 品种 | 台账行数 | 不同日期 | 重复行 | 台账印的累计 | 去重后累计 | 台账印年化 | 去重后年化 |
|---|---|---|---|---|---|---|---|
| IC | 3728 | 2390 | 1338 | 370.06% | 155.924% | 10.66% | 10.07% |
| IM | 2103 | 1052 | 1051 | 116.862% | 47.000% | 9.40% | 9.35% |

重复区间：IC 2017-01-18 → 2022-07-22（IM 上市前那一段，是全段的两倍）；
IM 2022-07-25 → 2026-11-24（几乎整段两倍）。

## 根因（两行）

`scripts/paper_basis_timing.py`

- L91 `marks = {m["date"]: m for m in ledger.get("marks", [])}` —— 读回来的索引键是**日期**
- L109 `key = f"{code}:{d}"` + L110 `if key in marks:` —— 写出/查重的键是**品种:日期**

两把钥匙不同，于是**读回来的每一行都通不过存在性检查**：每次运行都把它当新的一天重算、
在 `"IC:2017-01-18"` 这个新键下再写一份，而原来那份仍留在字典里，最后
`ordered = sorted(marks.values())` 把两份一起落盘。下一次运行重复同一件事。

连带效应（解释为什么一直没人发现）：年化 = `((1+cum) ** (TRADING_DAYS/行数) - 1)`，
行数和连乘次数被同一个倍数一起放大，于是**年化几乎不动**（10.66% vs 10.07%），
只有累计 carry 翻了两倍多。读者页最显眼的那个数，恰好是受影响最大的那个数。

## 影响面

- `research/PAPER-BASIS-TIMING.md`：累计 carry 与天数两列失真（年化基本可用）。
- `results/paper_basis_timing/STATE.json`：`products.<code>.days / cumulative_carry_pct` 同上。
- 台账本身的**逐日 marks 值是对的**：本轮用独立镜像重放，1.5bp/边口径下
  2390（IC）+1052（IM）个交易日 carry 与台账**逐日零差**（`max_abs_carry_diff_pct = 0.0`）。
  错的只是「同一天被写了两次」这一件事，不是算错。
- 结论方向不变：这条线仍然全段为正、年化约 10%（净），GO 不翻案。

## 修法（已写好，本轮未动）

1. L91 改成 `marks = {f"{m['product']}:{m['date']}": m for m in ...}`；
2. 存量去重一次（同日同品种只留一行，两行内容当前逐字相同，留哪行都一样）；
   存量改写要先过 `python Tools\treasure_guard.py prescan`，删除走 quarantine 模式；
3. 改完重跑 `python scripts\paper_basis_timing.py`，读者页与 STATE 自然回到 2390/1052 行口径。

**为什么本轮没动**：同机另有执行体（pid 107624，11:49 起）正握着这批共享面，
竞争探针 rc=3 CONTENTION，按 r1907 同树多宿主律本轮只落新增文件面。

## 防复发

- 本面 `--ledger-gate`：台账还有重复日 → rc4，修完之后一轮可以拿它当验收门。
- 本面 `--check`：台账健康状态若从 DUPLICATE_DATES 变成别的（=有人修了），
  会自己报 STALE 要求重发，不会静默停在旧发现上。
- 教训（入知识库候选）：**同一份 append-only 台账，读的键和写的键必须是同一个**；
  凡是「读回来当缓存、写出去按复合键」的实现，都要有一条自检证明
  「昨天写的那行今天读得回来」。
