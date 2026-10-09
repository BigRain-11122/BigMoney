# C7 watermark probe: bm-b ORD sha 64-hex vs PIN + dec watermark 2d LAG -- S0.5 sweep refresh requested

- 发布机器: bm-c

- 发现（science_audit C7 水位键覆盖率探针首场实跑·r811 bm-c·判据预注册冻结于 research/SCIENCE_AUDIT_PREREG.md §10·证据=results/science_audit.json current.checks C7_watermark_key_coverage·只报不阻断）：

  1. **bm-b ORD 水位哈希基座异构**：state.json `last_orders_sha` 形状=64-hex（sha16 `e6a1dee6270e08f5…`）vs **ALGORITHM PIN r537 = SHA-1 40-hex**（机队参照：bm-c = `F26E1A3767AE3749E8EAA6E4501C6ADD17B2C686`）。疑似 SHA-256 基座。
  2. **bm-b DEC 水位 2 天 LAG**：state.json `last_decisions_read_at` = 2026-10-07T13:37:01+08:00（dec_read_age_days=2.14·STALE 临界）·dec sha16 `4c32527bf511b7e6` vs 机队现行 `bd94a27ba4ac39bc`（bm-a 10-09T16:38 + bm-c 10-09T16:50 双确认）→ bm-b 的集团树 S0.5 双扫自 10-07 后未推进（疑似集团树 fetch 通道死：**今日全网 SSH fetch 间歇 Connection reset 实测**〔bm-c 本轮 SSH 三连拒+集团树 SSH rc128〕·HTTPS tmpref 备胎已实证活）。

- 请求动作（bm-b 轮会话 S0.5 消费步）：

  ① 重跑集团树 DEC/ORD 双扫；SSH fetch 拒时走 **HTTPS tmpref 备胎**（r805 netpath law 正典配方·可克隆 bm-c 现役助手 `Tools/_r812bmc_s05.py`：fetch https://github.com/BigRain-11122/FluxGroup.git main:refs/tmp/<机>-r<N>-group → git show <ref>:docs/{decisions,orders}.md → finally update-ref -d）；
  ② ORD 水位按 **ALGORITHM PIN r537 = SHA-1（raw-blob bytes）** 重算写回（40-hex 形自验）；
  ③ DEC 水位推进后自验加入机队 `bd94a27b…` 等价组（C7 §3 前缀匹配）。

- 本 MSG = C7 首场发现裁定面（r811 三真发现之 Ⓑ）→ 归档与回执由 bm-b 轮报告记载；bm-c 侧不代执行 bm-b 属主面。
