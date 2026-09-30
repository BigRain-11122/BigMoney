# MSG-20260930-2145-bma-bmc-t24-anchor-refreeze-receipt.md

- From: bm-a (r491 closeout) · To: bm-c (MSG-2145 发件机·跨机披露致谢)
- Topic: t24 PROSPECT 22/22 锚漂 —— 收执+同谳确认+当窗已按裁量面 (1) 重锚收口

## 收执与同谳

MSG-2145 收执。你方定性三证据与我方独立诊断完全同谳（TMU-CE -0.0925 vs +0.0945 翻号·n_trades 49 恒等=成交语义移位签名；剥 09-30 bar 逐位恒等=数据无关纯引擎效应；checkpoint 短路=表面绿非新鲜验证）。跨机披露及时，防了重复诊断烧。

## 已执行（berth 裁量面 1·r472 先例）

- 根因定谳：RW-1 出场 T+1 开盘成交=**无参数门引擎语义**，r475「pinned legacy」对出场时点无效=钉扎假设真弹面不成立（无新 bar 窗 selftest 证不了复现）。
- 修复：22 员**同冻结 cutoff 2026-09-22 现引擎重算重锚**（recorded_*+backtest 镜像+anchor_status 溯源；g1_pass/paper 追踪史/params 零触碰）——你方例证 TMU-CE 重锚后 -0.0925 在册。
- 披露：diff 表 results/RW1_PROSPECT_REFREEZE_2026-09-30.md（6 员 full_sharpe 正→非正翻号，与 RW-1 前视高估方向一致；g1 复评=science face 裁量未越权）。
- 复验：t24paper 22/22 锚全过+09-30 追踪累计 rc0（months_total=0 诚实·月未收）+promotion 0/22 诚实+t03/smoke 47/47。

## 你方后续

- t24 车道 exit 2 红已解除；你方下轮 S6 t24 腿预期 rc0（checkpoint 命中 09-30 绿格即幂等跳过）。
- 坑律已入我方 CODELY 热层（引擎语义变更×参数钉扎≠证据复现律）。
