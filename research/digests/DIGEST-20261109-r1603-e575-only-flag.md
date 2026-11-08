# DIGEST-20261109-r1603-e575-only-flag

**轮**：r1603 bm-b（2026-11-09）　**卡**：E575　**dept**：研究+工程
**问题**：E573（r1601）分出 11 个「链脚本带 `--only` 开关」的轮，却没有一个轮的报告行印刷了开关。于是「报告沉默」有两种可能——那一跑跑了全链，或跑了子集但没说——报告面本身不可判。

**做法**：三条机械臂，都不跑 runner。

| 臂 | 口径 | 结果 |
|---|---|---|
| 轮行臂 | 该轮自己的行 + 同轮 sibling 行里印刷的调用 | 0 处带开关 |
| 盘上臂 | `results/*r<N>bm<X>*s6*.log` / `*s6_chain*.json` | 11 轮一份都没有 |
| 执行臂 | 本机 601 份会话快照里 `run_shell_command` 的 `args.command`，只认**执行行** | 490 条链执行，291 条带 `--only` |

归属规则（唯一让该臂能说话的东西）：一条执行属于**同一台机器的、时间在其之后的第一条轮行**（容差 6h）。轮行是在一轮结束时写的，命令在之前跑——「命令之后的第一行」就是跑它的那一轮。容差外的一律记为 unattributable（38 条），不猜。

**落到 11 轮**：

| 类 | 数 | 说明 |
|---|---|---|
| 有执行且带开关 | 1 | r1373：两次 `--only gate_state_census` |
| 有执行但没带开关 | 0 | — |
| 本机无该链执行 | 4 | r1447 / r1481 / r1544 / r1594 |
| 另一台机（off-host） | 6 | bm-c 六轮：命令跑在别人的机器上，本机没有它 |

**三条教训（首版全是自己踩出来的）**
1. **单位是执行行，不是命令**。一条 tool call 常常先 `git add` 再跑链两次（一次带开关、一次不带）。命令级答案只能挑其中一跑来描述，等于凭空丢一次。
2. **「提到脚本」不是「跑脚本」**。`\bpy\b` 会匹配 `Tools/card_ledger_guard.py` 的扩展名，首版把 4 条 `git add` 数成跑了链；解释器锚必须是行首或分隔符之后，且其后有空白。
3. **时区**。transcript 的 tool call 时间戳是 UTC（`...Z`），轮行是 `+08:00`。当成本地钟读，整窗命令前移 8 小时、被归到上一轮（首版实证：r1594 的执行被划走）。附：另一台机的轮记 **off-host**，不记「没跑」——absent 不是 silent。

**证据**
- `scripts/e575_only_flag.py`（build/check/check-fast/verify/selftest 37/37）
- `results/state_tilt/ONLYFLAG-2026-11-08.json` + `onlyflag_latest.json`（CHECK/VERIFY 全绿）
- S6 腿 `only_flag`（rc=0，`python scripts/e575_only_flag.py check`）
- smoke `#E575` 块 + `scripts/run_e575_smoke_leg.py`（PASS；`--doctor` 红如设计）
- 卡：`knowledge/METHODOLOGY_ASSETS.md` E575

**未主张**：没有任何执行记录的 4 轮究竟是跑了全链还是跑了子集，本窗不作推断；38 条 unattributable 执行的实际归属是 E576 的人口。