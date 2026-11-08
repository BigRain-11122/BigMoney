# DIGEST — r1586 bm-b: E560 prices the chain receipt (does it carry enough to triage?)

**轮次** r1586 · **卡** E560 · **面** `results/state_tilt/CHAINRECEIPTSHAPE-2026-11-08.json` ·
`chainreceiptshape_latest.json` · **script** `scripts/e560_chain_receipt_shape.py`（selftest 21/21，
check `problems=[]`，verify 两次 build 字节恒等）

## 一句话

三个链跑器都会在失败后继续跑完剩下的腿，但**没有一台把「谁没跑」写进回执、没有一台留 stderr、
没有一台写明表有多大**，九格三字段里只剩 5 格；盘上 320 份回执里 18 份带非零行，只有 1 份带任何
输出字段。

## 读数（全部可由 `check` 重 derive）

| 跑器 | 表 | 失败策略 | 行键 | 输出预算 | 捕获 | rc 与种类 | 表大小 | 未跑可表示 |
|---|---|---|---|---|---|---|---|---|
| s6_chain_bma | 81（**import 自 bm-c**） | 继续 | leg/rc/elapsed_sec/tail | 220 字符（stdout 末行） | TimeoutExpired | 124 与退出码可区分，但其它异常无回执 | 无 | 有 `MISSING` 占位行（rc=127） |
| s6_chain_bmb | 311（自有） | 继续 | 同上 | 300 字符 | Exception | 全塌缩成 rc=99 | `legs_total=len(rows)`＝跑了几条 | 无 |
| s6_chain_bmc | 81（自有，bm-a 抄它） | 继续 | 同上 | 220 字符 | TimeoutExpired | 同 bm-a | 无 | 无 |

回执观测（不进闸）: 320 份（bm-b 218 / bm-a 53 / bm-c 47 / 1 不可读），18 份含非零行，1 份带输出字段；
bm-a 出现过 dict 与 list 两种形状（历史格式变化），单凭读者「按行数判」会把旧形状读错。

## 为什么「回执够不够」是个真问题

E559 已证：没有任何进程读 rc、没有任务跑链、没有读者打开回执。于是**回执是唯一的记录**。本轮证明
这份记录本身缺三类字段，其中最贵的漏洞是「未跑不可表示」：`except TimeoutExpired` 的两个跑器
遇到别的异常会整轮结束且不落盘，读者看到的是**什么都没有**——与「今天没跑链」同形；而 bm-b 的
`rc=99` 与真实退出码 99 同形。

## 本轮自己的两枚坑（首版实犯，已入闸）

1. **import 出来的表不是「没有表」**：bm-a 写的是 `import s6_chain_bmc as canonical` +
   `LEGS = canonical.LEGS`，只认 `LEGS = [...]` 的扫描把它读成 0 腿——正是这张卡要测的那种
   「不在扫描器射程内就等于没发生」。修法=按 alias 解析到 sibling 模块（深度 ≤2）并发布
   `legs_table_source`。
2. **输出预算在 Slice 的 upper**：`tail[0][:220]` 的第一个下标是 `Constant(0)`、真正的 220
   在 `ast.Slice.upper` 里；只看 `Constant` slice 会把三个跑器全报成「保留 0 字符」。
3. **活目录不能进闸**：首版把回执 census 写进 `summary`，S6 腿自己写的那份回执立刻让 `check`
   报 `summary does not re-derive`。正法=观测面单列（`receipt_census`，drift 只打印），闸只吃
   三个源文件。

## 下一步（E561 候选）

把「历史回执」变成可回溯的证词：按轮号取**当轮的** `Tools/s6_chain_bmb.py` blob（git 历史）数
LEGS，与当轮回执行数比对——量出「有多少轮的回执在静默少报表规模」，也决定旧回执还能不能拿来做
triage。