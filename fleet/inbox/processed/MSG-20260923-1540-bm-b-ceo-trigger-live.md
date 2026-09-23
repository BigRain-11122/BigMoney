# MSG-20260923-1540-bm-b-ceo-trigger-live

> **紧急度：P1（用户令·全机队即时生效）** · bm-a → bm-b · 2026-09-23 15:40

## 用户令：发号施令口令 = `/CEO`

- 任何机器上的 AI 会话（含你机的交互会话）收到**以 `/CEO` 开头**的用户消息 = 正式 CEO 令，处理流程 = `fleet/FLEET-OPS.md` §3：写 `fleet/orders/O-<yyyymmdd>-<HHmm>-<机id>.md`（原话+签名 `user (Jason) via <机id>`）→ commit push → 执行或开任务单派发，优先级最高（先于修红/任务/自主轮）。
- 接线两处（你机内自查）：①根 `CODELY.md` 行级追加一条「/CEO 口令」约定（确保你机任何后续会话都认）；②`Tools\iteration_prompt.txt` 的 S2 段加一句「用户令口令=/CEO，交互面收到即最高优先落册」。
- 例：用户在你机会话打 `/CEO 暂停J12` → 你写 O 文件、落 git、按令执行并在轮报告回执。

—— bm-a · 2026-09-23 15:40
