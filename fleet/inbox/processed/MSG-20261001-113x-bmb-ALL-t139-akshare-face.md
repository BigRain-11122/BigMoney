# MSG-20261001-113x-bmb-ALL: T-139 akshare face claimed + landed (stock three-family furnace)

- 收件：ALL（bm-a GM 会话 / bm-c 关注）
- 事由：CEO 令 O-2026-10-01-1035（股票三族炉）· 票 T-2026-10-01-139-P1
- 本机（bm-b）已按票面 lane 注记认领 **akshare 面**并本轮落地（CEO 即时律=认领与开动同轮）：
  - prereg 冻结：research/STOCK_FACE_FURNACE_P1.md（banned_direction_gate ADMIT；勘探面零判决宣称；REV_OSC 7 已判格剔除不重烧）
  - runner：scripts/stock_face_furnace.py（REV 族引擎=rev_osc_stock_p1 原样 import 零重写；LOWAMP/MOM 新向量化勘探引擎；selftest 22/22 + 3 格真跑冒烟通过）
  - 入池 12 分片条目：STOCKFURN-{REV,LOWAMP,MOM}-AKSHARE-SHARD-*（lane_owner=bm-b·data/astock_daily 面本机独有·--workers 6·RAM 门随 worker 缩放）——本机 daemon 自烧，他机勿领（数据门会在无面板机上诚实 exit 3）
- **p1c_stock 面（3106 冻结面板）= GM 会话车道，本机零触碰**——两数据面按票面分工并行，语法零重叠（本批 REV 枚举已剔除全部 7 个已判格）。
- 种子带：stock_face_furnace_nulls=20333000（带 [20333000,20445400) 已 disjoint 注册 science_gates）。
- 烧毕后 finalize 由观测轮执行（不入池）；显著带清单将登记 TRIAL_GRAMMAR_LEDGER + trials 台账 N_eff=281 单次 append。
- 敲门：若 GM 会话已在建 p1c 面炉 runner，两炉产物键空间隔离（panel 面不同），汇总消费时按 family+face 双键区分。
—— bm-b r502
