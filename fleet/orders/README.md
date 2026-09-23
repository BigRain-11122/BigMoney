# fleet/orders/ — 用户令牌台账（追加式 · 永不删除）

- **发令口令 = `/CEO`**：任何机器的 AI 会话收到 `/CEO` 开头的用户消息 = CEO 令，立即落册本台账并按 FLEET-OPS §3 执行/派发。
- 文件名：`O-<yyyymmdd>-<HHmm>-<发令机id>.md`（时间+机器=天然唯一，无撞号）。
- 签名：`user (Jason) via <bm-x>`；用户在任何机器的 AI 会话发言即成令。
- 优先级最高（用户令 > P0 修红 > P1-P3 任务 > 自主维护轮）。
- 受令机：轮报告回执 + `CODELY.md` 行级追加执行记录；心跳 `orders_ack` 字段记进度。
- 机制全文 = `fleet/FLEET-OPS.md` §3。
