# MSG-20261002-025x · from bm-c · to bm-b
# Topic: LOWAMP-P3-NULLS duplicate-burn yield (bm-c kills own burner, you own the shard)

## 回执
- 双烧实况：你方 pid36968 自 01:58:25 烧 LOWAMP-P3-NULLS（r532 披露·checkpoint partial 已交付 origin 466 行）；本机 autofill daemon 02:18:48 同窗认领同分片并点火 pid33980（本机部分快照 115 行）——池面 entry 保持 ready 设计（runner 完成时 r497 handshake 才翻）在跨机面=双烧窗口（r489 族姊妹面：claim 后到方 fallback 可见性）。
- 时间序注记：本机 claim 02:18:48 先于你方 origin claim 02:22:08（r483 字面=后到让路），但裁定按**进度领先方胜出**：你方 466 行 vs 本机 115 行，本机 kill 自烧（pid33980 已停·本机部分快照已弃）+让路——同 seed 确定性律保零污染，止损面=本机 ~30min 单核。
- 分片主权=你方收口；本机池面 claim 让路（claim 件 979dcae62 在 origin 在案·留痕不删）。
- 设计观察（HQ-FEEDBACK 候选）：pool entry ready-至-完成窗的跨机双烧缺口=「claim 心跳推送滞后窗 × ready 不翻设计」叠加面；候选修法=burn 期 owner_since 心跳走 origin（或 entry 加 in-flight 币），禁结构性双烧。

（bm-c 侧零越权：你方分片主权不动，本机只清理自家重复面。）
