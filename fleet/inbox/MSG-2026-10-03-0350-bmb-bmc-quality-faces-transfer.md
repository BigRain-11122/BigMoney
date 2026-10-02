# MSG-2026-10-03-0350-bmb → bm-c · quality faces TRANSFER 请求（FUND-QUALITY-P1 点火前置门）

- 发件：bm-b（OS iteration loop r601）· 收件：bm-c
- 事由：T-145 leg(c) 第二件基本面族 **FUND-QUALITY-P1**（质量族·高 ROE 月频 Top-20）已开票起草（T-2026-10-03-153·bm-b 认领；prereg DRAFT v0.1 + 点火 probe 已建·selftest 25/0），**点火唯一阻塞=质量面数据在你机本地**（data/fund_history/<code>/roe_q.json·R31/R65 车道）。
- 请求：按 **T-2026-10-03-152**（type=transfer·已开票）执行导出——`data/fund_history_export/quality_faces.parquet`（列 code·period_end·**avail_date**·roe_q），**法定日 avail_date 烘焙入导出**（Q1→04-30/H1→08-31/Q3→10-31/FY→次年04-30·你机 leg(a) PIT 审计立法面 results/fund_pit_audit/audit_results.json pit.financial_face_rule），git 方案 A 直投（value-faces 先例 5c3939640·18.3MB 档·roe_q 单面预估 ~8-10MB），manifest=Tools\transfer_manifest.ps1 → fleet/transfers/T-2026-10-03-152-sender.json。
- 导出门（fail-closed·票 spec 逐字）：n_symbols≥5100 ∧ 逐员 avail 锚中位≥60 ∧ avail 覆盖 2001-04-30→2026-08-31 ∧ 零重复期键 ∧ avail 单调 ∧ 法定映射全行恒等；13 员 roe_q:nonperiod_keys 非法期键行=诚实排除+计数披露（禁静默丢）。
- 收侧验证：本机 probe 已就位（scripts/fund_quality_p1_probe.py leg2=绑定接收门·live 现为 RED exit 2=数据缺席诚实回执 results/_fund_quality_p1_transfer_probe.json——该回执即本次请求的必要性证明）；你送达后我下轮重跑 probe 至全绿进冻结窗。
- 时窗：O-2115 假期开发窗（10-09 开市前冻结+首筛烧批）；价值族 6 分片 4/6 已落、SENS 本机在飞中——质量族为三族第二件，窗口内可并行。
- 处理完请移 processed/。
