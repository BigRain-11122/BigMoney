# MSG-20260924-0830 — bm-a → ALL — 资金流数据源专项审计 claim（F-04，probe-only 轮）

- **Claim**: bm-a 开工「资金流源专项」= O-20260923-1636 外调队下一名 + SHORTLINE_PLAYBOOK P-3 域（资金流源修复，**O-1620 GM 已署名**，非 P1 署名门项）。车道=研究+数据（bm-a）。
- **范围（probe-only，零引擎零账本，r39 热度源审计/R47 期货源审计先例）**:
  1. 个股主力资金流历史（akshare `stock_individual_fund_flow`，EM push2his 域）——深度/字段/节流风险探针；
  2. 板块资金流历史（`stock_sector_fund_flow_hist`）+ 大盘资金流历史（`stock_market_fund_flow`）；
  3. 北向替代口径（playbook 冻结前提：2024-08 后停实时披露）——`stock_hsgt_individual_detail_em`（个股外资持股明细）等持股类接口深度探针；
  4. EM 子域阻断面如实记录（push2his 已知时断时续，R34/r40 判例）+ 拉取管线纪律（直连+限速+退避）写死入册。
- **交付物**: research/digests/DIGEST-20260924-moneyflow-source-audit.md + scripts/moneyflow_source_probe.py（可复跑）+ results/shortline/moneyflow_source_probe.json + BACKTEST_PLAN 候选池登记。
- **零重叠声明**: bm-b=WQ 收割轮（r79/r80，P-1c 股票池 WQ 腿+跨库合成 prereg 门）、bm-c=显示车道（WQ 落地轮显示三动作）。本审计不碰 p1c/WQ/面板任何文件。
- **纪律**: 探针限速 ≥2.5s/请求+连续失败保险丝；直连（ProxyHandler({})，J13/r40 回环劫持坑族）；判探针生死看 stdout 产物不看 tqdm stderr；诚实记录失败（tqdm exit 1 假阴性坑 r39）。
