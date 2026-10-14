# W20 挂载 slice-1 普查收据 —— tick-stock-panel 外源收割 digest 族级撞号定谳（r937 bm-b）

> 供给律=TRIAL_LABOR_LAW §5 外源收割 digest（O-1721 常态线）·链=T-2026-10-14-186-P1 W19→W20 挂载链 slice-1（r936 起窗被杀窗续作）
> 源=github.com/shy3130/tick-stock-panel @tree `3d8a42617759b227d036e31f3c821ffcca014ebe`（26 件经 api.github.com blobs API 逐件取证入 `results/_r937bmb_w20_tsp_corpus/`）
> 烧面=core48 ETF 日线面板（试工期 tl1 底盘）·普查域=四面：D1 数据面可行性 / D2 仓内 77 (module,fn) 孪生清单（W1-W16 已烧）/ D3 CLOSED_FAMILIES 9 键机器门 / D4 排除书 N1-N7 路线指纹
> 机读件=`results/_r937bmb_w20_census.json`（逐面证据引文+特征面+孪生引用+closed 门探针）·词面消化件=`_r937bmb_w20_tsp_entryfaces.txt`·孪生 docstring 证据=`_r937bmb_w20_twin_docstrings.txt`

## 定谳一句话

**45 面（25 fixture 策略 + 20 默认信号种子）→ 0 幸存**：该外源目录=与仓内 W1-W16 语法同源的民间 TA 轴系正典（19 面精确/近精确孪生 + 1 同轴变体 + 3 面叠加 N4 短线反转负读数 + 1 面命中 lowamp 族级关线），另有 9 面涨停机制族在 core48 ETF 烧面上无数据面（诚实不可行，非科学判负）。**W20 挂载：本源零预注册候选——起草即撞 D2/D3/D4 冻结门，零烧退回=排除书把沉没成本变节省的预期执法路径。**

## 族级普查表（fixtures 25）

| # | fixture | 入场机制（证据级消化） | 判 | 撞号域 |
|---|---|---|---|---|
| 1 | active_limit_gene | 60日涨停计数≥N + 未涨停休整 | INFEASIBLE_FACE | D1 涨停机制（stock-only） |
| 2 | boll_breakout | 收盘突破布林上轨 + 量比 | COLLIDE_TWIN | D2 `ta.bb_squeeze_breakout`/`mean_reversion.bollinger_breakout`（双方向已烧） |
| 3 | breakout_new_high_60d | 破前 60 日高 + 涨幅 + 量 | COLLIDE_TWIN | D2 `trend.donchian_breakout`+`event.breakout_confirm` |
| 4 | broken_board_recovery | 涨停锁板 + 量 + 涨幅 | INFEASIBLE_FACE | D1 `limit_up_locked` |
| 5 | bullish_alignment | MA5>10>20>60 多头排列 | COLLIDE_TWIN | D2 `trend.triple_ma`+`patterns.yang_break_3ma` |
| 6 | consecutive_limit_ups | 涨停 + 连板数≥N | INFEASIBLE_FACE | D1 连板特征 |
| 7 | high_turnover_surge | 换手率>5% + 涨幅 | COLLIDE_TWIN | D2 `sentiment.turnover_surge`（名同机制） |
| 8 | limit_up_momentum | 连板≥1 + 涨幅 | INFEASIBLE_FACE | D1 连板特征 |
| 9 | long_lower_shadow_reversal | 长下影≥3% + 跌幅 + 量 + 收盘上半区 | COLLIDE_TWIN | D2 `ta.hammer_reversal`+`patterns.needle_probe`（needle docstring 自注 hammer 同族折价） |
| 10 | low_volatility_leader | 年化波动<0.30 + 动量 + MA20 上 | COLLIDE_TWIN+CLOSED | D2 `volatility.low_vol_long` + D3 `lowamp_daily_xs`/`lowamp_deep_xs`（族级判负关线·机器门探针在 census JSON） |
| 11 | ma_convergence_breakout | 均线粘合 N 日 + 放量脱带 | COLLIDE_TWIN | D2 `patterns.ma_converge_break`（名同）+`ta.bb_squeeze_breakout` |
| 12 | ma_golden_cross | MA5/20 金叉 + 量 + MA60 上 | COLLIDE_TWIN | D2 `trend.dual_ma_cross` |
| 13 | macd_below_zero_revival | 20日新低 + DIF<0 + DIF 抬升 | COLLIDE_TWIN | D2 `patterns.macd_divergence`（新低+动量背离=同解剖） |
| 14 | macd_golden | DIF/DEA 金叉 + 量 | COLLIDE_TWIN | D2 `ta.macd_trend` |
| 15 | n_day_low_reversal | 60日新低 + 阳线 + 量 | COLLIDE_TWIN+N4 | D2 超卖反转族 + D4 N4-4 单标的短线反转 ETF 判负 |
| 16 | near_limit_up | 涨幅逼近涨停带 | INFEASIBLE_FACE | D1 `price_limit_pct` |
| 17 | oversold_bounce | RSI<30 + 阳线 + 量 | COLLIDE_TWIN+N4 | D2 `rsi2`/`rsi_revert` + N4-4 |
| 18 | oversold_reversal | RSI<30 + 涨幅 + MA5 上 | COLLIDE_TWIN+N4 | D2 `rsi_revert` + N4-4 |
| 19 | platform_consolidation_breakout | N日平台 + 破平台上沿 + 量 | COLLIDE_TWIN | D2 `patterns.box_breakout`（名同） |
| 20 | pullback_ma20_bounce | 贴 MA20±2% + 多头排列 + 阳 | COLLIDE_TWIN | D2 `mean_reversion.pullback_bounce`+`folk.low_suction` |
| 21 | pullback_to_support | 缩量回踩 MA20 + MA60 上 | COLLIDE_TWIN | D2 `folk.low_suction`+`patterns.vol_drought_reversal`（缩量面） |
| 22 | rsi_midline_pullback | MA60 上 + RSI∈[45,60] + 5日内 RSI>65 记忆 | COLLIDE_AXIS | D4 N2 同轴指纹：RSI 入场轴已烧 4 面（`rsi2`/`rsi_revert`/`folk.rsi_low_flat`/`ta.rsi_divergence`），中轴窗=同轴换参窗；**最近幸存候选但无精确孪生**——日收益相似度可测证非孪生前，冻结门按 N2 零增量拒 |
| 23 | strong_open | 高开≥3% + 收>开 + 涨幅 | COLLIDE_TWIN | D2 `folk.gap_up_hold`+`sentiment.overnight_drift` |
| 24 | trend_breakout | MA60 上 + 60日高 + 量 | COLLIDE_TWIN | D2 `trend.donchian_breakout`+`event.breakout_confirm` |
| 25 | volume_price_surge | MA20 破位交叉 + 量≥2x + 阳 | COLLIDE_TWIN | D2 `ta.vol_breakout`+`trend.dual_ma_cross`+`sentiment.price_volume_trend` 合成 |

信号种子 20 面（`backend/app/strategy/signal_seeds.py`）：布林 2 面（孪生）/涨停族 4 面（D1 不可行）/MA 级位 6 面+MA 交叉 3 面（`trend.dual_ma_cross` 孪生）/MACD 2 面（`ta.macd_trend` 孪生）/60日高低 2 面（donchian+超卖族孪生）/放量 1 面（`vol_breakout`+`turnover_surge` 孪生）→ **0 新族**（全部为 fixture 族成员面）。

## 路线判读（下一步供给面）

1. **本源关闭**：tick-stock-panel=民间 TA 正典第二实例，与仓内语法（W1-W16 · 77 fn · 945,735 SCREEN+948,047 JUDGE 链头已烧）同轴同族——外源收割 digest 路线对**该源**在 core48 面上零增量。排除书 KPI 口径（过预滤新鲜度）：0/45。
2. **N2 重开律的消费**：外源想法目录本为合法新机制面通道——本普查证明「换目录不等于换轴系」；后续外源收割须先过本普查式族级撞号（同律=供给预滤三步的族键查+路线查先于任何起草）。
3. **涨停机制族（9 面）的唯一解锁面=股票宇宙烧面**：core48 ETF 面无涨停/连板特征；个股日线面板（T-87 bm-b 车道·全史 qfq）+ 涨停价规则可派生，但试工期底盘换宇宙=新引擎面工程（P1 级新方向，须署名任务单才开工）——本轮不动，留 W20 挂载决策点呈报（48h CEO W19 报告 10-16 13:49 到期，本普查结论随报告呈报）。
4. **W20 预注册起草**：零候选=不起草（起草即撞门）；供给 refill 转向=新机制语法族（非民间 TA 轴）/REFINE_BENCH 存活变体/T-86 存活因子腿（§5 其余供给源），或股票宇宙面署名票（路线 3）。

## 收尾自证

- 普查脚本=`results/_r937bmb_w20_census.py`（含 closed_family_check 机器门探针·lowamp 双键 rejected 态在 census JSON `closed_gate_probe` 字段）
- 证据完备性=26 源件全量入仓（blobs API 逐件 SHA 取证）+25 面 compute_signals 消化件+27 孪生 docstring 件
- 零烧声明=本轮零新回测零新烧录零账本变动（纯普查·纯预滤·排除书预期执法路径）
