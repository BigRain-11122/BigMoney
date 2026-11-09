# DIGEST 2026-11-09 r1640 bm-b · E622 — 死代码的宿主跑不跑

**一句话**：E619 找到的 36 条「赋了值再没读」的面键局部量，31 个宿主函数里 **29 个从模块级可达**——所以那 **34 条是真缺陷、2 条零成本**；同一解析器下全体函数可达率 **86.7%（16,596 / 19,146）**。

**产物**
- `scripts/e622_deadlocal_reach.py`（selftest 34/34，verify problems=[]）
- `results/state_tilt/DEADLOCALREACH-2026-11-09.json` + `deadlocalreach_latest.json`
- `scripts/run_e622_smoke_leg.py`（PASS；`--doctor` 1/1 红，面 sha 还原）
- smoke_test.py leg E622 · S6 leg `dead_local_reach`（0.05s，rc=0）

**分档读数（facekey 档，31 个持有者）**
| 档 | 个数 |
|---|---|
| 模块顶层直接调用 | 0 |
| 经调用链可达 | 28 |
| 只经 argparse `set_defaults(func=)` 交接 | 1 |
| 只被「自己不跑」的函数调用 | 2 |

宽档 49 个持有者：45 活 / 4 惰；54 条死行里 48 条落在活函数。

**四条自踩（都改过读数）**
1. `sys.exit(_canonical.main())` 是本仓的家规入口——首版只让类内定义接受属性调用，把整条 main 链判死（1 个持有者错判）。
2. 反向收紧：首版对任何属性调用都放行，把 `d.get()` 当成本模块函数的调用，多算 84 个「可达」（基数 16,646→16,596）。
3. `set_defaults(func=F)` 是真实交接但不是调用边，单独成档。
4. dict 调度表（`{"run": cmd_run}`）不跟 → 惰性是**上界**：2 个惰性持有者其实在表里（宽档 3 个惰性持有者落在有 dict 表的模块），产物带计数披露。

**下一步**：E623（ready，cpu-only）问「如果把这 34 条活缺陷按最小改动修掉，能不能用同一张图证明它们不会再回来」——即修补后的回退守卫。