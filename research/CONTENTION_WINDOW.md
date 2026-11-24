# 竞争窗还有多久

一张面，回答每轮都要问的那句话：另一个宿主还在写吗，窗口还有几分钟自然关闭。
由 `scripts/contention_window.py` 渲染；只描述不修板、不杀进程、不放宽律法。

<!-- BEGIN contention_window -->
generated 2026-11-25T04:25:39 | verdict **WINDOW_OPEN** | machine bm-c | inputs 73318826afbd

| 项 | 读数 |
|---|---|
| 对端进程 | 79608 |
| 对端仍存活 | 79608 |
| 对端最后写入 | 2026-11-25T04:11:42 |
| 那张面 | research/ARBITER-BOARD.md |
| 静默时长 | 14.0 分钟 |
| 回看窗 | 45 分钟 |
| 窗口自然关闭于 | 2026-11-25T04:56:42 |
| 距关闭 | 31.0 分钟 |

**判词**：WINDOW_OPEN

> peer wrote 14.0 min ago and is still alive -- new files only until 2026-11-25T04:56:42

**本轮可做什么**：只写新增文件面；禁改共享面、禁重跑 S6 链（r1907/r1927）。到期后重跑探针再判。
<!-- END contention_window -->

## 它不声称什么

- 不替代 `Tools/repo_write_contention.py`：那个回答「现在有没有冲突」，这个回答「冲突还有多久」
- 不杀进程、不改共享面、不改 r1907/r1927 的执法口径
- 窗口关闭不等于对端安全：对端壳仍活着时，下一次写入会重开窗口，所以开工前要重跑探针
