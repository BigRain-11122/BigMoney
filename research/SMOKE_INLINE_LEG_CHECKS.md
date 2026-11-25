# 六条「没人能给它们跑一次」的冒烟腿，现在各有一条命令

r2091b 把 647 条字面腿分了类：325 条声明式（命令写在表里，任何人可逐字重跑）、322 条内联块（只有整套冒烟能重问）。上一轮的红名单里 **6 条腿红了却没有任何可执行入口**——不是它们依赖太深，而是从来没人给它们写过 check。

本轮脚本 `scripts/smoke_inline_leg_checks.py` 给这六条各配一个 check 入口，读的是**同一批已发布面**，并做了一件 suite 块做不到的事：每条腿拆成纯函数 `judge_*`（入参是解析好的文档），于是自检可以用「合成一份绿的 → 只改坏一个字段 → 断言它变红」来证明这条腿真的能红（r1282 / r1935 族：不能变红的守卫不是守卫）。

## 实跑读数（2026-11-25 16:5x，bm-c）

| 腿 | 判决 | 面自己说的问题（逐字出自 detail） |
|---|---|---|
| 起点是声明，不是成交 | **FAIL** | 持仓页写了，CEO 页没写（`起点是声明，不是成交` 缺席）|
| 中文 CEO 页无新增英文散文 | **FAIL** | `day=2026-11-24 hits=10 inherited=8 new=2 first_new=LIVE-2026-11-24.md:24` |
| 纸面账本拥有卡面卖的那本书 | **FAIL** | `gate=NAV_IDENTITY_BROKEN(rc1)`、`decision_bar=2026-11-11`、`navdev=6.5e-09` |
| 订单页印出地板逐名切单 | **FAIL** | k-gap 面停在 `2026-11-20`，订单页已到 `2026-11-24` |
| toll 阶梯判决可从臂面重算 | **FAIL** | 五格逐条点名：cost0 阶梯 6.895pp / 臂面重算 6.87pp；cost05 6.05 / 6.005；cost20 6.085 / 3.58；cost40 3.29 / 3.49（仅 cost10 6.755 对上）|
| CEO 页每节自报 bar | **FAIL** | `bets` / `derisk` / `k_gap` 三节落后且 `provenance=no_writer` |

六条全红，**没有一条是我这条新腿算错**——它们本来就是红的，只是此前没有命令能问出来。

## 为什么这算产出而不是记账

- 红名单从「6 条无入口」变成「6 条有入口且各带一行读数」；`smoke_red_recheck` 的 `NO_CHECK_ENTRY` 桶因此可以直接清到 0（需要改 recheck 的入口映射，属共享面，本轮竞争窗未改）。
- toll 阶梯那条给出了**可下单的证据**：阶梯面印的 spread 与臂面重算差到 3.5pp 量级（cost20 6.085 vs 3.58），而它自己的 `--check` 是绿的——这正是 r1935「自检只重算自己」的第二个实例。
- 修这六条各自需要的动作（重 derive 卡面/订单 k-gap/CEO 页散文、给三节补链腿、阶梯面重生）**全部落在共享面上**，本轮实测 `repo_write_contention` rc=3 CONTENTION（对端交互宿主 pid=93460 仍在写），按 r1907 同树多宿主律不做。

## 用法

```
python scripts\smoke_inline_leg_checks.py --selftest    # 18/18：每腿绿控 + 负控 + 缺面即红
python scripts\smoke_inline_leg_checks.py               # 六腿逐条重问，写 results/smoke_inline_leg_checks.<id>.json
```

exit 0 = 六条全绿；1 = 至少一条红（当前态）；2 = 用法错误。

## 下轮指针

1. 把 `scripts/smoke_red_recheck.py` 的入口映射接上本脚本（`NO_CHECK_ENTRY 6 → 0`）；
2. 六条红里四条是「面对另一天」（卡面 11-11、k-gap 11-20、CEO 页两处），竞争解除后按面代差统一重 derive；
3. toll 阶梯面重生一次，让 `spread_pp` 与臂面同源（重生后本腿应自绿，可作本工具的端到端正控）。
