# QA — 冒烟内联腿地图（r2091b · bm-c）

对象：`scripts/smoke_inline_leg_map.py` → `results/smoke_inline_leg_map.bm-c.json` + `research/SMOKE_INLINE_LEG_MAP.md`

## 判据与证据

| 判据 | 证据 |
|---|---|
| 工具能跑且自检全绿 | `python scripts\smoke_inline_leg_map.py --selftest` → **selftest 17/17 PASS**（rc0） |
| 真源能解析、两类腿都识别 | `SMOKE-INLINE-LEG-MAP legs=647 table=325 inline=322 (ready 266 / one_hop 24 / chained 32)` |
| 判决面被消费而不是重造 | 排序首 6 行判决全部来自 `results/smoke_red_recheck.bm-c.json`（NO_CHECK_ENTRY），工具零重跑 |
| 只读、零共享面写 | 本轮只新写 4 个新文件（脚本/结果面/文档/本 QA）；未跑 S6、未跑冒烟、未改 state/心跳 |
| 「ready」的语义经人工抽查 | 抽查 `smoke_test.py` 3649-3681（`_PO2/_f64/_b64/_bad64` 全在该 try 块内定义）→ 块自含，可整段搬出 |

## 已知边界（不宣称）

- 静态解析只认字面 `check("腿名", …)`；suite 运行时腿数（767）多于本表（647），差额为运行时拼名腿，静态看不见，未补。
- `ready` 只说明「这段代码自含」，不说明「这条腿值得搬」；是否动，取决于 recheck 面是否判红。
- 本工具无链腿、无冒烟腿（本轮竞争窗，共享面禁改），接线留下一轮。
