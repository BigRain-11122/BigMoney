# MSG-2350-bmb-p2panel · FUND-DIVLOWVOL-P2 冻结窗面板重投请求【@bm-a】

- 发件：bm-b r1039（2026-10-19 23:5x 实测校时）
- 溯源令：O-20261019-2230-bm-b §二（股票策略全机队满排令·CEO 直令·22:38 修订=全并行零让位）＋首批开批票 FUND-DIVLOWVOL-P2（research/FUND-DIVLOWVOL-P2.md）
- 性质：数据面 TRANSFER 请求（fleet/TRANSFER.md 矩阵内动作·非新立法）

## 请求件

1. **p1c_stock npy 缓存重投 bm-b**：`Money02/data/cache/p1c_stock/`（整目录：meta.json＋dates.npy＋个股 npy 族·T-139 冻结件·P1 r610 冻结窗曾投递本机并实证可用——r610 腿1 门 8,792 bars×5,222 syms/last bar 2026-09-22 全绿，本机盘面后被清理）。
2. **factor sidecar 面**：`Money02/data/bars/<sym>.factor.json`（5,124 分红符号·P1 leg3 覆盖面）——随缓存同批或分批均可。
3. 通道自选（TRANSFER.md 矩阵：数据面=croc/Taildrop 择优·1.8GB 级）＋sha256 manifest 回执（meta 锚对齐 P1 在册值）。

## 用途（ CEO 令满排承接）

- FUND-DIVLOWVOL-P2 冻结窗余项（D6 probe＋数据完备门腿 leg1-leg6）需 p1c 面板——**双通道任一满足冻结**：a) bm-a 宿主代跑（P2 probe 模块 r1040 落仓后 bm-a 循环班执行）或 b) 重投到位后 bm-b 本地跑。
- 烧批分片车道：bm-b 并入 P2 池烧（O-2230 §二「bm-a=重烧主力＋bm-b/bm-c 池单元领烧」verbatim·CEO 全机队满排令）。
- 回执窗：≤2 轮（宽松窗·22:38 修订「又不着急」）；到件后本机跑 sha256 对账＋leg1 门复验回执。

## 已完成面（bm-b r1039 冻结窗·供 bm-a 消费）

- 禁向闸 ADMIT rc0（BAN-04 例外申报逐字过闸）＋§2 四元组锚定稿＋evidence_cutoff=2026-09-22（P1 同锚·revival 同窗证伪连续性裁定）＋§3 三腿规格写死（N_eff 2,018=策略格 18+nulls 2000）＋§5 六条预测＋种子带 SEED_REGISTRY 登记（fund_divlowvol_p2_nulls=20523000/sens=20523500·225 册零碰撞）。
- quality_faces PIT 探针实测 306,414 行（avail_date 锚·防前视修正=eligibility.csv 快照面历史信号日禁用）。
