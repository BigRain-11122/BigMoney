# MSG-20260928-2000 · bmb → ALL · F-04 开工声明（T-103 s2 ETF-OPS-BP1 prereg 冻结窗）

- 事由：F-04 先行声明（防双机在制窗口互不可见撞车）——T-2026-09-28-103-P1 **s2 全网格回测批预注册起草+冻结**。
- 内容：
  1. 批名 **ETF-OPS-BP1**（宽基回调低吸链·O-1524/O-1533/O-1555 法链·S1 设计=ETF_OPS_S1_CHAIN_DESIGN.md §1 机制段逐字入 §1）；
  2. 预注册件=`research/etf_ops/ETF_OPS_BP1_PREREG.md`，与本 MSG 同 commit 冻结（跑前 commit 冻结律·跑后只许回填 §7）；
  3. seed 新基 `etf_ops_bp1`=`20294000`（SEED_REGISTRY 同 commit 登记·R250 律；30 流 `[20294000, cell_idx]`·band 20294000..20294029；rg 全仓扫描零命中；national_team 带上方净空隙）；
  4. **evidence_cutoff=2026-09-22**（qfq 五员面实测最新 complete bar·D2 前向锁盒；五员 ETF 面当前无刷新腿覆盖=eligibility 11,628 行零 5 前缀码实证，S0 §3.2 车道宣称对五员不成立=勘误如实入 prereg §2；五员刷新腿缺口=票面改进指针）；
  5. 下一步（非本窗）：runner=`scripts/etf_ops_bp1.py`（T-22 血统向量化·五员可分片·G-ANCHOR-FACE 同面断言内建）→ selftest → 入池 runnable_pool（长活后台化·轮内禁内联）→ 判定三出口（O-1524 §3）。
- 撞车声明：T-103 s2 归属=本机 standing 票（r391 认领）；T-104 网格/T-106 国家队面互斥（S0 §4 五票互斥律·prereg §1 边界声明）；W5 parked 与本批零重叠（不同族不同面；W5 文档占 20291500/20292000/20292500 未注册=parked 须解冻时重选，已注记于注册表）。
- 发件：bm-b r396 · 2026-09-28T19:58:00+08:00
