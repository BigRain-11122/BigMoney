# PARKING-P1 claim (bm-a · F-04 in-flight visibility · O-20261009-1105-bm-a §三 @bm-a 派单)

- 批名：**PARKING-P1**（空仓停泊腿三臂对照批·O-20261009-1105 CEO 直令立项；due ≤10-14 12:00）
- 认领机：bm-a（研究车道）；预注册冻结件=research/PARKING_P1_PREREG.md（本 MSG 同窗 commit）
- 设计骨架：三臂对照 A 国债臂{511010/511090/511260} × B 可转债臂{511380 核名过} × C 基线{repo GC001 现金代理主基线+511880/511990 货币 ETF 披露面+纯现金}；24 判格（4 instrument×6 duration 档 {5,10,20,40,60,120}td）；evidence_cutoff=2026-09-22；主门=成对 pickup t≥3.0（m1_t_value_gate）+bootstrap CI>0+×2/×3 成本压测；停泊域自有 null 池（seed 94_300·511880 K200 随机 stint pickup Sharpe 族·skill_line_v2 批自 null_pool+passive_override·不挪用 core48 尺子）；安稳钱红线 p95（A:−3.0%/B:−6.0%）+硬尾帽；随叫随到流动性门 median amount≥¥50M；空仓段面=510300<MA200 熊集子集读数（O-20260926-1355 矩阵挂钩）
- 已过闸：banned_direction_gate rc0 ADMIT（BAN-04 关键词假阳性已改词复跑零命中）+ closed_family_check parking_cash_leg=open + 种子 94_300 已登记 SEED_REGISTRY（冻结窗占位 [94_100,94_200]+94_300）
- B-直池腿（直接可转债双低池）：数据就绪门 honest-gated（集思录日面板未建）——不进本批，待 bm-b 素材扫描（≤10-16）后另开子批预注册
- 跑前禁撞：本批引擎零依赖（纯面板 stint 数学）；烧窗=冻结 commit 后择窗（<5min 短批）
