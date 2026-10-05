# QA: open-market-readiness-r714

## What was delivered (bm-a r714, dept:研究)

10-08 复市窗就绪探针（r713 month_exam_readiness 探针范式血统复用）：

- `scripts/open_market_readiness.py` — run + selftest 双子命令
- `results/open_market_readiness.json` — 探针数据面
- `docs/open_market/READINESS-2026-10-05.md` — CEO 白话面（当日重生成字节幂等）

## Verification evidence

| check | evidence |
|---|---|
| selftest 21 legs | `python scripts\open_market_readiness.py selftest` → `selftest: ALL PASS`（21/21；含 L5b 他机车道面板缺席合法腿） |
| run rc | `python scripts\open_market_readiness.py run` → exit 0, verdict=AMBER（6 GREEN + 2 in-flight AMBER, 0 RED） |
| md byte-idempotent | 同日双 run SHA256 恒等（MD_IDEMPOTENT=True） |
| 两 AMBER 面归属 | moneyflow 面板 53/5222（EM 源断流自愈中，r710 已知事实）；trio NULLS bm-b canonical 在烧（finalize 窗 10-05..09）——均为已知在途面非新红 |
| 车道法合规 | R31 判例：`data/fund_premium`=bm-c 本地面板，本机缺席=合法态（other_lane 事实记录不判红）；探针零 spawn 零网络零 trial 零 marks |
| REGIME_GUARD 常量读 | live/paper.py 文本读 ENFORCE_ACTIVE_FROM=2026-10-01 + regime_enforce_approved.json 在位（零 import 副作用，r694 冻结态实读先例） |
| 日期锚 | MARKET_DATE=2026-10-08（国庆 10-01..07 休市后首个交易日）；HOLIDAY_FLOOR=2026-09-30 与 ETF 面板尾 bar 实测恒等 |

## Face inventory (8 faces)

1. ETF 日线主时钟 — GREEN（尾 bar=09-30 假期地板+五员冻结面板在位）
2. S6 数据 gates 复活组 — GREEN（14 gate 脚本+10 本机面板）
3. moneyflow 面板 — AMBER（已知在途）
4. 纸盘 marks 续跑面 — GREEN（34 账户 AGGR20+ALLOC7+GRID5+SYSV1 2 全停 09-30 地板）
5. REGIME_GUARD v3 — GREEN（日期门开+批准件在位）
6. 外源双腿 run-11/run-7 — GREEN（jisilu_feed_run.py+hibor_radar.py 在位）
7. 判决/供给线 — AMBER（trio 在烧+W117 GATED，已知在途）
8. 饱和引擎守护 — GREEN（engine_alive+heartbeat fresh）

## Self-check against charter

- 探针=read-only L1 聚合：+0 trials +0 marks +0 registration +0 spawn ✓
- 判据面无手抄：所有数字 import 派生自仓内产物（面板/marks/pool/face 件实测） ✓
- 诚实性：他机车道面缺席=事实记录；面板 incomplete=如实 AMBER ✓
