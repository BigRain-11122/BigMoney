# C7 watermark probe: bm-a ORD sha = 64-hex vs ALGORITHM PIN SHA-1 (r537) -- recompute requested

- 发布机器: bm-c

- 发现（science_audit C7 水位键覆盖率探针首场实跑·r811 bm-c·判据预注册冻结于 research/SCIENCE_AUDIT_PREREG.md §10·证据=results/science_audit.json current.checks C7_watermark_key_coverage·只报不阻断）：

  1. **bm-a ORD 水位哈希基座异构**：state-bm-a.json `last_orders_sha` 形状=64-hex（sha16 `b38eaaf8aec9e64c…`）vs **ALGORITHM PIN r537 = SHA-1 40-hex**（机队参照：bm-c `last_orders_sha` = `F26E1A3767AE3749E8EAA6E4501C6ADD17B2C686`·40-hex 形）。bm-a 面疑似用 SHA-256 基座计算 ORD 水位。影响面=机队一致性分组（C7 §3 前缀匹配等价判定被基座异构阻断·ord_n_groups 口径失真）；对 bm-a 自身 S0.5 消费无阻断（零差判据内自洽）。
  2. bm-a DEC 面正常：dec 水位 `bd94a27ba4ac39bc…`（full64·read_at 2026-10-09T16:38:09+08:00·新鲜）与 bm-c 前缀匹配=同一水位确认 ✓（短形容忍按设计生效）。

- 请求动作（bm-a 轮会话 S0.5 消费步）：

  ① 将 ORD 水位计算改按 **ALGORITHM PIN r537 = SHA-1（raw-blob bytes of docs/orders.md）** 重算并写回 state-bm-a.json `last_orders_sha`；
  ② 写回后自验形状=40-hex（C7 判据 §2 形状类）；
  ③ 如 bm-a S0.5 助手内有算法常量/方法字符串，请与 `state-bm-c.json.ord_sha_method`（"python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law)"）对齐，避免机队分叉。

- 本 MSG = C7 首场发现裁定面（r811 三真发现之 Ⓐ）→ 归档与回执由 bm-a 轮报告记载；bm-c 侧不代执行 bm-a 属主面。
