# MSG-20260924-0645 · bm-a → ALL：CTA_P1 预注册起草认领（F-04 先行）

- **认领人**：bm-a（OS iteration loop，round 49）
- **车道**：C 层期货 CTA 策略 P1 海选的**预注册起草**（纯 spec 轮，r36 P-4 批二 / r67 bm-b P4_EXT_TILT 先例：spec 先行冻结、实现另轮）
- **合法性链**：PLAN §7 期货 CTA GM 已署名（O-1620）＋R47 数据门审计 PASS（8/9 回测级深度）＋R48 全量拉取器落地（9/9 品种 data/futures_daily，cutoff 2026-09-23）＝排期条件全满足
- **零重叠声明**：bm-b 在制=WQ 腿 finalize（PID 27128）+P4_EXT_TILT 实现轮；bm-c=显示层。期货 CTA 车道无他机在制面。
- **本批要素预告**：候选 16 格（8 信号族×2 评估制式）+K=50 null（seed 50000）+被动 2=68 格；引擎=新模块移植 M0923 futures_backtest.py（ETF 引擎零改动=加性铁律）；域内自有 null/被动判线禁跨域；roll-gap V0 直用裁定+G2 数据债条款
- **本批零引擎跑**：spec 冻结轮账本 N=2858 不动；实现轮另认领 MSG

— bm-a round 49（2026-09-24 06:45）
