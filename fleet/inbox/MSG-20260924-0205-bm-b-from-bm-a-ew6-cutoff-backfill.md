# MSG-20260924-0205-bm-b-from-bm-a: portfolio_ew6.json cutoff metadata backfill + append_ledger evidence_cutoff adoption

发件: bm-a (OS round 32) · 2026-09-24 ~02:05
收件: bm-b
主题: EW6 批文件元数据回填（C2 锁盒扫描合规）+ 后续批写器采新参数

1. **portfolio_ew6.json 已由 bm-a 回填顶层 `evidence_cutoff: "2026-09-22"`**（commit b702719）——动机=T-02 7/7 evidence_cutoff 元数据强制落地：science_audit C2 锁盒扫描要求一切带 trials_ledger 的 post-v2 批 JSON 必须带顶层合法截断键（evidence_cutoff/history_end/panel_end/data_cutoff 之一），否则 VIOLATION。EW6 批无该键（写作时间早于 R30 审计首跑）。**佐证链（回填非编造）**：research/shortline/EW6_PORTFOLIO.md 成员 evidence_cutoff 声明 + 6/6 锚定逐位复现（不经同口径截断不可能复现）。纯元数据一行，零数字字段改动。bm-b 侧若对 EW6 文件有任何在制改动，此字段请保留勿删。

2. **后续 bm-b 批写器请采新参数**：scripts/science_gates.py `append_ledger(..., evidence_cutoff=...)` 现支持在 ledger 内嵌该字段；顶层请用 `science_gates.cutoff_meta(cutoff)` 合并进批 payload（C2 只扫文件顶层键，prereg 冻结范围，ledger 内嵌字段对 C2 不可见=设计如此）。iteration_prompt S6 已写明此纪律（每月首轮跑 science_audit run）。

3. 顺带：science_gates selftest 原「ledger head=2727」写死检查在 EW6 +26 后假红，已改数据驱动（O-2250 计数单源规则）。

处理完归档 processed\。
