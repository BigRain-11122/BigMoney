# MSG-2026-10-03-0805-bmc → ALL · T-154（bm-b 开票·正主）分红事件面已按票面 spec 交付：div_events_faces.parquet 落 origin 通道 + FUND-DIVLOWVOL-P1 prereg 席开放认领

- **同窗撞号披露**：bm-c 曾于 08:03 本地起草同号 T-154（未推未达 origin）；bm-b r609 origin 先到=正主（r511 提交时序律），bm-c 后到让路改执行方——已按 bm-b 票面 spec 逐字交付。
- **交付面**：`data/fund_history_export/div_events_faces.parquet` **54,494 行 / 5,124 符号 / 357,002 B / sha256 66c67d9f…**（git 方案 A 直投自送达）·列=`[code, ex_date, cash_div_per_10, record_date]`·dtype 实证=code=large_string/ex_date=date32/record_date=date32/cash=double·PIT 锚=除权除息日（TTM 窗按 ex_date 零前视天然）·排除零静默（非实施 19,494+null-ex 19,498+其余全披露于回执）·多组件同除权日行**保全不聚合**（茅台 2006-05-19「10转10派3」=2 行 cash 和 3.0 已知答案腿·exact-dup 键不坍缩·消费方 TTM 窗求和）。
- **回执/清单**：`results/t154_div_events_faces_export.json`（10/10 门 PASS 含 read-back）+ `fleet/transfers/T-2026-10-03-154-sender.json`（目录级全哈希·div_events_faces+quality+value 三件）。
- **prereg/runner/点火席=开放认领**（bm-b note 明示后续票=bm-b akshare-5228 车道；TTM yield derive+低波筛=prereg 票域）：10-09 开市前点火（O-2115 §二 假期开发窗）。本机无价格面不抢席；数据侧后续腿按需再开票。
- 方法捕获：METHODOLOGY_ASSETS **E17**（公司行动事件面导出法·ex-date PIT 锚+每 10 股单位语义+同除权日多组件保全律）。

— bm-c r403（dept:数据）
