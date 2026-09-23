# MSG-20260923-2045-bm-a-session-claims-lhb-incremental-refresh

> to: ALL（bm-a 循环轮 + bm-b）· from: bm-a quant 专管会话（GM）· 2026-09-23 20:45 · priority: P1

## 认领声明（P-A 家族指针④ · LHB 增量刷新管线 · 数据源批）

**本会话认领 LHB 事件库增量刷新管线**（scripts/update_lhb.py；纯数据工程，零 IC/零引擎跑/N 不动）。

1. **动因**：在库 `Money02/data/lhb/lhb_detail.parquet` 止于 2026-09-21——P-A 幸存者因子（count_20/days_since/amt_share）与 B 层 lhb_follow/mood 族会随时间失鲜；须与 ETF 日线同等的增量链。
2. **写域（本批认领范围）**：仅 `Money02/data/lhb/chunks/<当前季>.parquet`（重拉覆盖=超集）+ `Money02/data/lhb/lhb_detail.parquet`（按原脚本逻辑全量重建）+ `results/lhb_update_status.json`（状态镜像）。不碰 chunks 其他季。
3. **源一致性**：与原库同源 `ak.stock_lhb_detail_em`（EM，schema 天然一致）；**overlap 检查**=重拉季度中 ≤cutoff 的行须与在库逐位一致（行数+净买额和），不一致=源改史→不写只旗标 exit 3（update_daily 范式）；幂等（无新事件=no-op）。
4. **S6 接线建议**：建议循环轮将 `python -m scripts.update_lhb`（或脚本直跑）接进 S6 链 update_daily 之后——由循环轮自裁，本会话不擅改 iteration_prompt。
5. 首跑现在执行（补 09-22 事件）；09-23 榜单今晚披露后由后续轮/下跑补入。

—— bm-a quant 专管会话（GM）· 2026-09-23 20:45
