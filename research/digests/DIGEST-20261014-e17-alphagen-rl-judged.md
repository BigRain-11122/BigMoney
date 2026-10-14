# DIGEST-20261014-e17-alphagen-rl-judged —— N2U3-ALPHAGEN-RL-P1 判决批收口

- **批件**：N2 U3 通道①「全新语法」alphagen RL 公式因子主考批（E16 census_holds=true 开窗承接·supply-floor chain leg-5·prereg FROZEN r892 commit 8f49d6eea·judged 面 evidence_cutoff 2026-10-09）
- **链条**：leg-1 runner r891（selftest 46/46）→leg-2 训练探针（256 eps·marginal flat 0.0001-0.0002）→leg-3 完整训练（4096 eps·autofill 01:06/05:02 断点续跑）→export-topk（n_unique=32·n_skip=0）→judged（r923c→r925 链·07:42:26 JUDGED-2026-10-09.json 落地 114KB）→r933 判负收口（§7/§8 回填+attrition 双面行+EXCLUSION_BOOK+TRIAL_GRAMMAR_LEDGER+METHODOLOGY E65+本 digest）
- **判决**：**0/32 registered 判负**——门禁链：D6 拒 18（max|corr| vs 在册 0.706-1.000）→M1 t≥3 过 9（t 10.416-13.227）→G1'v2 过 0（best QTLD(low,60) sharpe_full_x1 0.5435 vs skill_line_v2 2.952 @ N_eff 940,821·批内 scrnull μ=-0.2571/σ=0.6119·CI95 下界 -0.1707≤0）→G2 0（DSR max 0.2355<0.95 且 family PBO 0.2714>0.25 双 fail）。账本 940,789→940,821（+32 EXACT·RL 搜索面与 nulls 不计=E16 trial_budget_law）
- **预测对账**：P2 对（G1' 0/32·差距巨大）/P1 错（RL 收敛价格字段 {close 13/high 7/open 6/low 3/vwap 3} 非量能/换手族；|ICIR| med 0.178·带内 14/32 部分）/P3 错（核心 license 面判负：RL 边际 flat=无反馈基线不可超越）/P4 过（极端日四日全 false·x2/x3 逐年稳定 32/32）/P5 过（n_unique=32·n_skip=0）
- **全起点分布（best 格）**：fullstart_6m best +0.1753/p25 -0.0043/中位 +0.0193/p75 +0.0402/worst -0.1301；滚动最差 3y -0.0201/5y +0.0228；beat 3m 0.5708/6m 0.5337/12m 0.4906；max_dd_x1 -13.71%
- **一句话定谳**：RL 反馈搜索在该语法空间不产生高于无反馈采样的可注册信号——负即止 RL 线（EXCLUSION_BOOK 收口·G2 fallback 学术引用面·same-grammar rerun FORBIDDEN）
- **证据**：results/alphagen_rl_p1/JUDGED-2026-10-09.json + TOPK-2026-10-09.json + research/N2U3_ALPHAGEN_RL_P1.md §7/§8 + gate_attrition 双面行（r933 bm-b）
