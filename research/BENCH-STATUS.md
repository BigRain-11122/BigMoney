# 策略试验场状态（bench hub）

updated 2026-11-24T21:33:19+08:00 | 细胞数 26

| id | 状态 | 判决 | 最近跑 | 秒 | 问题 |
|---|---|---|---|---|---|
| fut_trend | done | tsmom=NO_EDGE, ma_cross=NO_EDGE_REPACKAGES_BETA, donchian=NO_EDGE, reversal=NO_EDGE, xs_mom=NO_EDGE | 2026-11-22T23:10:08+08:00 | 4.8 | 在已有真实日线的10个期货品种（股指4+国债3+商品3）上，5种经典风格里有没有哪一种值得单独开一条线？ |
| bond_curve | done | T-TF:zrev=NO_EDGE, T-TF:trend=NO_EDGE, T-TS:zrev=NO_EDGE, T-TS:trend=NO_EDGE, TF-TS:zrev=NO_EDGE, TF-TS:trend=NO_EDGE | 2026-11-22T23:10:26+08:00 | 2.8 | T/TF/TS 三对价差上，反转或趋势有没有净后仍为正的收成？ |
| astock_lowvol | done | verdict=NO_EDGE, H5_excess_ge_2pp=False, ann_pct=6.12, excess_pp=0.93, excess_t=0.45 | 2026-11-22T22:20:29+08:00 | 172 | A股IC表里最干净的因子（低波动）用宽篮子、20日换手、10bp/边成本做，扣费后能不能跑赢同池等权2pp以上？ |
| bond_defensive | done | NO_EDGE | 2026-11-22T23:10:28+08:00 | 2.3 | 把 T/TF/TS 当作防守腿（6%波动目标、周频再打、1.5bp/边），是不是比现金（GC001 1.38%）更好的防 |
| revalidate | done | ALL_HOLD | 2026-11-24T10:22:14+08:00 | 60.5 | 新 bar 落地后，已发布的判决会不会翻转？翻转就是警报。 |
| idx_fut_basis_reuse | done | kind=reuse, IC_net_carry_pp=4.15, IM_net_carry_pp=5.89, IF_net_carry_pp=0.74, IH_net_carry_pp=1.74, booked=IC/IF/IM admi | — | — | IC/IF/IH/IM 的贴水是不是一项可下注的收成？ |
| cb_dual_low_reuse | done | verdict=NO_EDGE, ann_pct=7.64, vs_equal_weight_pp=0.83 | — | — | 转债双低轮动是否值得投产？ |
| astock_resid_industry_reuse | done | verdict=ONE_YEAR_STORY, ann_pct=3.76, ex_best_year_pct=0.14 | — | — | 行业内残差反转是不是一条能单独下注的腿？ |
| basis_capacity | done | verdict=CAPACITY_OK_AND_SIZED, IC_multiple=1754.5, IM_multiple=2577.5, total_multiple=4332.0, annual_cny_if_10m_each_leg | 2026-11-22T23:19:09+08:00 | 3 | IC/IM 的贴水在 1% ADV / 5% OI 两条硬规则下能装多大资金，10M 下年收多少？ |
| basis_timing_size | done | verdict=GO, IC_weighted=10.09, IC_always_on=2.73, IM_weighted=9.3, IM_always_on=5.63 | 2026-11-22T23:34:59+08:00 | 2 | 贴水窄的时候把仓位降下来，能不能比常驻持有多吃 1pp 以上、且回撤不更差？ |
| repo_ladder | done | GC001=BASELINE_REFERENCE, GC003=NO_EDGE, GC004=NO_EDGE, GC007=NO_EDGE, GC014=NO_EDGE, GC028=NO_EDGE, GC091=NO_EDGE, GC18 | 2026-11-23T09:39:11+08:00 | 13.4 | 在已有11个逆回购期限（GC 1/3/4/7/14/28/91/182 + R 1/3/7）上，锁长期限扣掉佣金与闲置日 |
| cb_floor | done | CLOSED_AT_POWER | 2026-11-23T09:59:42+08:00 | 105.1 | 只做「收盘价<=105 且纯债溢价>=0」的债底券、等权、每 5 个交易日重打、扣佣金后，能不能比同口径全池等权多赚 > |
| pair_index_60d | done | NO_EDGE | 2026-11-24T21:24:50+08:00 | 1.3 | 四个股指期货之间做横截面强弱对冲（多最强、空最弱，60日排序），扣费后有没有净收成？ |
| pair_all10_60d | done | NO_EDGE | 2026-11-24T21:25:19+08:00 | 1.5 | 十个品种一起做横截面强弱（多前2、空后2，60日），净后是否为正？ |
| pair_commodity_60d | done | NO_EDGE | 2026-11-24T21:25:26+08:00 | 1.3 | 商品三品种（金/螺纹/原油）横截面强弱对冲，净后有没有收成？ |
| trend_single_IC_long | done | NO_EDGE | 2026-11-24T21:25:34+08:00 | 1.1 | 单做中证500期货的均线趋势（只做多、50/200），净后与买入持有比有没有超额？ |
| trend_single_AU_long | done | NO_EDGE | 2026-11-24T21:25:43+08:00 | 1.2 | 黄金期货单品种均线趋势（只做多），净后是否跑赢买入持有？ |
| trend_single_T_long | done | NO_EDGE | 2026-11-24T21:25:51+08:00 | 1.2 | 十年国债期货单品种趋势（只做多），净后是否跑赢持有？ |
| reversal_index_5d | done | NO_EDGE | 2026-11-24T21:25:59+08:00 | 1.4 | 股指期货五日反转（多跌得多的、空涨得多的），净后有没有收成？ |
| robust_ma_index | done | UNSTABLE_ACROSS_PARAMS | 2026-11-24T21:27:02+08:00 | 2.1 | 股指期货趋势的符号在 20/50、50/100、50/200 三组均线下是否稳定？ |
| robust_tsmom_commodity | done | UNSTABLE_ACROSS_PARAMS | 2026-11-24T21:27:12+08:00 | 2.1 | 商品趋势的符号在 60/120/250 日回看下是否稳定？ |
| robust_donchian_index | done | UNSTABLE_ACROSS_PARAMS | 2026-11-24T21:27:22+08:00 | 2.1 | 股指期货唐奇安通道的负结论在三组通道参数下是否稳定（负得稳才叫判死）？ |
| census_index_futures | done | CENSUS_UNPOWERED | 2026-11-24T21:29:06+08:00 | 6.7 | 四个股指期货上，趋势规则×窗口×多空共 20 种组合的整片地形：有几条是功效够的正边，还是整片噪声？ |
| census_commodity | done | CENSUS_SIGN_MIXED | 2026-11-24T21:29:18+08:00 | 5.9 | 金/螺纹/原油上，趋势规则×窗口×多空 14 种组合的整片地形：有没有稳定正边？ |
| basis_timing_perm | done | verdict=SIGNIFICANT, IC_pp=7.36, IM_pp=3.64, p=0.0, draws=5000 | 2026-11-24T21:40:00+08:00 | 1.7 | 按分位定仓比常驻多出的 7.4/3.6pp 是真实对齐还是权重自相关？ |
| census_bond_futures | done | CENSUS_LEANS_POSITIVE | 2026-11-24T21:33:19+08:00 | 5.0 | 国债期货（T/TF/TS）只做多的趋势地形：5 种组合里有没有功效够的正边？ |

## 队列规则

- 每 20 分钟一次静默 tick，只跑第一条 pending；队列空则毫秒退出。
- 新格必须先写脚本 + 在 BENCH-QUEUE.json 登记（问题、判据、数据车道、时限）。
- 判负的格子保留脚本与结果，不删；重开要新 id，禁改旧结论。
- 判据在跑之前写死在脚本顶部；改判据要留痕。
