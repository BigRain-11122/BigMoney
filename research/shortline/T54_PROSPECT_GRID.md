# T-54 PROSPECT 全脸网格证据批预注册（T54_PROSPECT_GRID · 冻结于首跑前）

- 票：T-2026-09-25-54-P1 slice-2（claim r173 bm-b）；令链：O-20260925-1105（R3）+O-20260925-1137 §二.2（**首个 P0 大载体·池入 ready 必带 workers_plan+分片计划·全机队可吃**）
- 性质：**测量/证据注册批——零判据、零准入、零采纳、零接线**。消费面=（a）10-31 J 线复跑 W-GRID **全池面**（解除 T-28 CE-6 受限面·J4 量的是 28 员池广度）（b）T-54 slice-1 多窗口稳定性准入证据。判负线照交禁翻案；本批不产任何判定。

## §1 成员（冻结）

22 员 PROSPECT（level=PROSPECT·TRADERS_DIR 在册·确定性 sorted 序）：
PROS-ANTS-01, PROS-ANTS-CE-01, PROS-BBS-01, PROS-BBS-CE-01, PROS-DOJI-01, PROS-DOJI-CE-01, PROS-DUCK-01, PROS-DUCK-CE-01, PROS-HAM-01, PROS-HAM-CE-01, PROS-IBB-01, PROS-IBB-CE-01, PROS-IMM-01, PROS-IMM-CE-01, PROS-MCB-01, PROS-MCB-CE-01, PROS-OVB-01, PROS-OVB-CE-01, PROS-RSRS-CE-01, PROS-TMU-01, PROS-TMU-CE-01, PROS-VOB-CE-01

## §2 轴与面板（冻结）

- **legacy**=live.paper.load_core()（core48 日线 CSV·零 Money02 争用）；本机枚举=1256 起点（2021-01-15→2026-03-26·cutoff 2026-09-24）
- **deep**=t22._load_axis_prices('deep')（T-18 深轴窗·manifest sha 门·growing-membership 2013 面板）；本机枚举=**1506 起点（2020-01-02→2026-03-24）——与 T-22 冻结 deep 6m canon n=1506 逐位吻合（面板 canonical 验证）**
- 枚举=t22.enumerate_starts（P-5 口径：warmup 252·≥24 员上市·≥126 bars 前瞻）——全机确定性同序→分片=位置区间，零协调数学

## §3 cell 口径（冻结·t22 机件 verbatim 复用）

- 单次 24m 引擎跑切三窗 {6m=126, 12m=252, 24m=504}；t22._run_cell 原样（J18 零改动·四门已过机件）；被动=同窗上市成员 EW buy&hold；regime=MA200 代理（仅报告分段非门）；x2=CostPatch(2.0)（r82 修正后口径）；真实 T+1/13bp/exit 规则
- 行 schema=t22（key=trader|pos·start·face·regime·n_listed·partial_12m/24m·ret_*/p_ret_*/dd_*/sharpe_*/trades_*·beat_6m/12m/24m）——**key 字段行内自带**（r163 律）

## §4 成员门（冻结）

- 逐成员 anchor gate（load_core·P-5 口径）；**FAIL=该员剔除+披露（非整批 abort）**——测量批语义：剔除保全其余成员证据面；剔除名单入 done marker+finalize summary

## §5 分片/续跑/接管协议（冻结）

- 分片=eligible 位置区间 [from,to) 半开；单写者=分片；续跑=行级 done-key 集（t22.load_done_keys·容忍截断尾行）；接管=owner 心跳 stale>20min（O-2100 s2.4）
- 输出命名空间 **results/t54/**（cells_{axis}_{face}_{shard}.jsonl + done_{axis}_{shard}.json + logs/）——**零 t22 canon glob 污染**（t28._load_deep_grid glob 面隔离·消费侧自管）
- **分片计划（冻结）**：legacy 4 片 [0,314)/[314,628)/[628,942)/[942,1256)＝lA/lB/lC/lD；deep 4 片 [0,377)/[377,754)/[754,1131)/[1131,1506)＝dA/dB/dC/dD；每片≈13.8k-16.6k cells；全脸=22×2×(1256+1506)=**121,528 cells**

## §6 账本与 finalize（冻结）

- 账本=finalize 步（分片全完后单独跑）：append_ledger 按**实际 cell 数**计数（禁手抄 prev·r163 律）；finalize 产 results/t54/t54_grid_summary.json（逐员三窗 beat 率+census 门=枚举数对 §2 冻结 census·漂移=abort）
- 复跑纪律：同 prereg 同网格禁重跑（J1 先例 55,132 cells 616s·BelowNormal）

## §7 披露（诚实边界·冻结）

1. **J-1 重叠面**：legacy 轴 6m PROSPECT cells 已由 J-1 批（bm-a R92·p5c leg-L 网格·p5c schema·机本地）产出（promotion-leg 权威不变）；本批 legacy 6m 与其确定性重叠=披露非违例（schema/网格/窗面不同·判定零重复：J-1 无判定线、本批无判定线）
2. **bm-b 本地 cells_deep_*_2.jsonl=dprobe 复现件非 canon**（x2 反高于 base 异源签名·88/554≠冻结 623/1380）——T-52 已如实定界；本批 outputs 隔离不受其染
3. **10-31 消费侧装载建议**：t28._load_deep_grid 当前 glob 全目录——复跑机须持 canon CE deep cells（bm-a/bm-c）或装载器钉 CANON_FILES；bm-b 单独复跑 deep CE 面=dprobe 污染面禁用（装载器加固=复跑准备期另行工单·本批不动 t28 冻结件）
4. PROSPECT 员 deep 轴注册域外延（T-28 旧注「deep 2013-2019=注册域外」）——本批即治此缺口的证据面；证据落地后旧注由 10-31 复跑装载面自然解除

## §8 判据面（零新增·指针）

- 本批零判据线；消费判据=O-1712/T-28 冻结面（J4 0.70 线冻结不动）；slice-1 准入规则（相关性帽/多窗口证据）另由策略部 prereg 冻结——本批只供证据
- 负结果预期：PROSPECT 员 beat 率大概率 <0.70（J-1 legacy 6m 面 0/22≥0.70 先例）——照交不翻案

## §9 验收（机判）

1. 8 分片全 done（markers 齐含 census 对账）；2. 全脸 121,528 cells（±anchor 剔除如实核减）；3. finalize summary 落盘+账本实际计数；4. 10-31 复跑窗全池面可装（装载器适配另票）
