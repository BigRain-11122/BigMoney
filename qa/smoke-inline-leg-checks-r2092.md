# QA — smoke_inline_leg_checks (r2092, bm-c)

**对象**：`scripts/smoke_inline_leg_checks.py`（新增，r2091b 六条「无命令」腿的独立 check 入口）

## 验收清单

| # | 判据 | 证据 | 结论 |
|---|---|---|---|
| 1 | 六条腿各有一个可独立运行的入口 | `LEGS` 六项；`python scripts\smoke_inline_leg_checks.py` 依次打印六行 PASS/FAIL | PASS |
| 2 | 每条腿能红（负控） | `--selftest`：合成绿文档 → 只改坏一个字段 → 断言 judge 返回 False；六条各一 | PASS 18/18 |
| 3 | 缺面不崩、且判红（r98 族） | `--selftest` 第三组：六条腿各以 None/空文档调用，断言返回 `(False, …)` 而非异常 | PASS |
| 4 | 读的与 suite 读的是同一批面 | 逐条对照 `smoke_test.py` 原块（3649-3681 / 4042-4052 / 4641-4671 / 6824-6857 / 7689-7734 / 10541-10593） | PASS |
| 5 | 红项必须点名到数 | toll 腿打印五格各自的「阶梯值 vs 臂面重算值」，不是只报 FAIL | PASS |
| 6 | 产物落盘 | `results/smoke_inline_leg_checks.bm-c.json`（schema / machine_id / generated / n_legs / n_pass / n_fail / legs[]） | PASS |
| 7 | exit 码语义 | 全绿 0；有红 1（当前 1）；用法错 2 | PASS |

## 未做（如实）

- 未接链腿、未接冒烟腿：两者都要改 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`，本轮 `repo_write_contention` rc=3 CONTENTION（对端宿主 pid=93460），按 r1907 只落新增文件面。
- 六条红本身未修：修法全部落在共享面（卡面 / k-gap 面 / CEO 页 / 阶梯面 / 三节链腿）。
- 全量冒烟未跑；上读数 767 腿 760 PASS / 7 FAIL @15:05:57。
