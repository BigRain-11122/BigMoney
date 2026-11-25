# QA — 竞争窗寿命面（r2070 bm-c）

工作面：`scripts/contention_window.py` · 面 `results/contention_window.json` · 页面 `research/CONTENTION_WINDOW.md`

## 为什么要这张面

`Tools/repo_write_contention.py` 每轮只答一句「现在有没有冲突」。本线自 r2065 起连续 14 轮读到 rc3 CONTENTION，于是每轮都只能写新增文件面、S6 链与全量冒烟连续 14 轮没跑 —— 但**没有人知道这个窗还要开多久**。窗口的来源可能是几小时前的一次写入，也可能是对端每 10 分钟一次活体写入，两种情况的应对完全不同（前者该按分钟计划，后者该考虑接管）。这张面把「等」变成可读的数字：对端是谁、最后写了什么、多久没写、窗口几分几秒后自然关闭。

## 判据（写死在 `classify()`，不读墙钟以外的任何活盘）

| 情形 | 判词 |
|---|---|
| 无其他宿主 | `NO_PEER` |
| 对端进程已不在，且窗内无可归因写入 | `PEER_EXITED` |
| 对端仍活，最近写入在回看窗内 | `WINDOW_OPEN`（印关闭时刻与剩余分钟） |
| 对端最近写入早于回看窗 | `WINDOW_CLOSED`（若壳仍活着，附一句「下一次写入会重开窗口」） |

边界刻意钉死：`静默 == 回看窗` 判 **CLOSED**（不是 OPEN）。

## 证据

- `--selftest` **16/16 OK**（11 条行为腿：孤立宿主、5 分钟前写入、50 分钟前写入、对端已死、边界整分、活对端无写入、字符串 mtime、摘要顺序无关且能抓到变更、页面块含判词与关闭时刻、建议语不是常量、pid 0 判死）
- `run` rc0 → `verdict=WINDOW_OPEN closes_at=2026-11-25T04:56:42`
- `--check` rc0（面与页面块逐字复核）
- 负控 `results/_r2070bmc_contention_window_negctl.py` **15/15 OK**：
  - 改面一个字 → rc3 且句含 `CHECK FAILED` 且**不含** `STALE`
  - 改页面 marker 块一个空格 → rc3 且句子点名 page block
  - 动 `inputs_digest` → rc3 且含 `STALE` 且不含 `CHECK FAILED`
  - 每次复原后重跑 → rc0
  - `_pid_alive(0)` / 狂野 pid 判死；`classify` 在空 hosts 上确定性返回 `NO_PEER`

## 自捕（已修）

1. 第一版 `_digest_probe` 只吃 `mtime` 字段，而生产探针给的是 `mtime_epoch` → 摘要对写入时间完全不敏感，负控第 8 腿当场判红；改为同时吃两者。
2. 第一版 `--check` 拿**当前钟**重渲染页面，于是每过一分钟就红一次（假红族 r1854/r1860）；改为拿面自己的 `generated` 重渲染，页面与面同代比对。
3. 负控首版写了一条 `assert ... or True` 的假腿 —— 那是「只会自我一致」的同族缺陷（r1935），当场删掉换成「篡改后重跑必须 rc0」。

## 它不声称什么

- 不改律法：读到 `WINDOW_OPEN` 的轮仍只许写新增文件面（r1907/r1927）；这张面只给结束时刻，不放宽执法
- 不替代探针：探针判「有无冲突」，本面判「冲突寿命」
- 窗口关闭 ≠ 对端安全：对端壳仍活着时下一次写入会重开窗口，开工前必须重跑探针
