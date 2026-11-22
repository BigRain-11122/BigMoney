# 策略试验场状态（bench hub）

updated 2026-11-22T23:10:28+08:00 | 细胞数 8

| id | 状态 | 判决 | 最近跑 | 秒 | 问题 |
|---|---|---|---|---|---|
| fut_trend | done | tsmom=NO_EDGE, ma_cross=NO_EDGE_REPACKAGES_BETA, donchian=NO_EDGE, reversal=NO_EDGE, xs_mom=NO_EDGE | 2026-11-22T23:10:08+08:00 | 4.8 | 在已有真实日线的10个期货品种（股指4+国债3+商品3）上，5种经典风格里有没有哪一种值得单独开一条线？ |
| bond_curve | done | T-TF:zrev=NO_EDGE, T-TF:trend=NO_EDGE, T-TS:zrev=NO_EDGE, T-TS:trend=NO_EDGE, TF-TS:zrev=NO_EDGE, TF-TS:trend=NO_EDGE | 2026-11-22T23:10:26+08:00 | 2.8 | T/TF/TS 三对价差上，反转或趋势有没有净后仍为正的收成？ |
| astock_lowvol | done | verdict=NO_EDGE, H5_excess_ge_2pp=False, ann_pct=6.12, excess_pp=0.93, excess_t=0.45 | 2026-11-22T22:20:29+08:00 | 172 | A股IC表里最干净的因子（低波动）用宽篮子、20日换手、10bp/边成本做，扣费后能不能跑赢同池等权2pp以上？ |
| bond_defensive | done | NO_EDGE | 2026-11-22T23:10:28+08:00 | 2.3 | 把 T/TF/TS 当作防守腿（6%波动目标、周频再打、1.5bp/边），是不是比现金（GC001 1.38%）更好的防 |
| revalidate | done | ALL_HOLD | 2026-11-22T22:57:11+08:00 | 60.9 | 新 bar 落地后，已发布的判决会不会翻转？翻转就是警报。 |
| idx_fut_basis_reuse | done | kind=reuse, IC_net_carry_pp=4.15, IM_net_carry_pp=5.89, IF_net_carry_pp=0.74, IH_net_carry_pp=1.74, booked=IC/IF/IM admi | — | — | IC/IF/IH/IM 的贴水是不是一项可下注的收成？ |
| cb_dual_low_reuse | done | verdict=NO_EDGE, ann_pct=7.64, vs_equal_weight_pp=0.83 | — | — | 转债双低轮动是否值得投产？ |
| astock_resid_industry_reuse | done | verdict=ONE_YEAR_STORY, ann_pct=3.76, ex_best_year_pct=0.14 | — | — | 行业内残差反转是不是一条能单独下注的腿？ |

## 队列规则

- 每 20 分钟一次静默 tick，只跑第一条 pending；队列空则毫秒退出。
- 新格必须先写脚本 + 在 BENCH-QUEUE.json 登记（问题、判据、数据车道、时限）。
- 判负的格子保留脚本与结果，不删；重开要新 id，禁改旧结论。
- 判据在跑之前写死在脚本顶部；改判据要留痕。
