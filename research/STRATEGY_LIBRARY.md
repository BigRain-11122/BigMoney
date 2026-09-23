# Bigmoney 策略与因子总库 STRATEGY_LIBRARY（v1.0 · 2026-09-23 · CEO 令 O-20260923-2210「全面健全的库」）

> 一册总目=全部策略/因子/门禁/判定律的索引与判定状态。数值唯一权威指针到各权威文件，禁双源漂移（RULES §5 薄法）。
> 试验账本 N=**2521**（`results/shortline_p4_queue.json` 链头，零假设全记账）；账本史与批次链见 §八。

## 一、策略工厂：**77 函数 / 12 模块**（11 流派 75 + 组合引擎 2·O-2250 审计实况计数）（`strategies/`）

| # | 流派（模块） | 函数 | 判定状态（批次证据） |
|---|---|---|---|
| 1 | 趋势跟踪 `trend.py` | 5 | P1 筛；donchian_20_10=NSP1 袖珍；triple_ma_5_20_60@ce=NSP1 候选→G2_NSP1 FAIL（邻域 5/6 红） |
| 2 | 均值回归 `mean_reversion.py` | 5 | P1 筛（rsi2/zscore_revert 在池）；bollinger_breakout=J19 迁移底座 |
| 3 | 动量轮动 `momentum.py` | 5 | P1 筛（xsec_mom_120_20 族=动量域双筛弱） |
| 4 | 波动率 `volatility.py` | 4 | **low_vol_long(n=60,top_k=5)=VOLATILITY-CE-01 注册员底座**；vol_target/vol_breakout/vol_regime_switch P1 筛 |
| 5 | 情绪资金 `sentiment.py` | 5 | P1 筛；price_volume_trend=NSP1 袖珍 |
| 6 | 日历季节 `seasonal.py` | 5 | P1 筛（month_end default OOS −0.47 负先验 NSP1 弃选） |
| 7 | 宏观过滤 `macro.py` | 4 | P1 筛（J7 对齐坑 0 笔案已修；432 基线死族语境） |
| 8 | 事件缺口 `event.py` | 3 | P1/NSP1 筛；double_bottom=NSP1 袖珍；breakout_confirm=vol_breakout 同族锚 |
| 9 | 技术分析经典 `ta.py` | **13** | 批2A+排队批：**engulf_reversal=ENGULF-CE-01 注册员**；rsrs_timing 袖珍/hammer 袖珍/bb_squeeze 袖珍；strong_close/macd_trend/kdj_reversal/streak_up/cci/williams/nr7/rsi_divergence 判负；vol_breakout=G1' 候选→**G2_FOLK FAIL**（邻域 4/6+×2 0.201） |
| 10 | K 线形态 `patterns.py` | **18** | 民间批：**needle_probe=NEEDLE-DE-01 / vol_drought_reversal=DROUGHT-CE-01 注册员**；inside_bar/doji/three_methods/ma_converge/immortal_guide 袖珍×5；duck_head=G1' 候选→**G2 FAIL（×2 0.258 成本条款单杀）**；morning_star/soldiers/piercing/island/yang_break/box/n_shape/big_yin/macd_div/obv_div 判负×10 |
| 11 | 民间手法 `folk.py` | **8** | 民间批：ants_climb 袖珍；low_suction 惜败（0.390 差 vi 一线）；lian_yin/false_break/volume_mound/second_wave/gap_up_hold/rsi_low_flat 判负×6 |
| — | 组合引擎 `composite_rotation.py` | 2 | J6 复合因子 Top-N 轮动=COMPOSITE-CE-01/02 注册员底座（40d 存活上限） |

**判定分布**：注册员底座 4 函数 + 判负 34 + 袖珍 11 + 候选归档 2 + 研究池余量 24。

## 二、在册交易员（6 名 · 全 INTERN · `firm/traders/`）

| ID | 名 | 入场族 | 退出机 | IS Sharpe | OOS Sharpe | ×2 | 诚实注记 |
|---|---|---|---|---|---|---|---|
| VOLATILITY-CE-01 | 组合软化一号 | low_vol_long | CE | 1.0275 | **2.0568** | 0.534 | 项目首个 G2 通过者（J15） |
| COMPOSITE-CE-01 | 复合软化一号 | composite_top5 | CE | 0.4514 | 1.6085 | 0.523 | — |
| COMPOSITE-CE-02 | 复合软化二号 | composite_top8 | CE | 0.4585 | 1.4853 | 0.431 | ×2 余量 +0.031 薄=watchdog 必设 |
| **ENGULF-CE-01** | 阳包阴一号 | engulf_reversal | CE | 0.6239 | 0.2944 | 0.402 | ×2 剃刀线 +0.002；首个 K 线形态员 |
| **NEEDLE-DE-01** | 金针探底一号 | needle_probe | default | 0.7781 | 0.4089 | **0.574** | **×3 0.483 亦越线=成本厚度史上最厚**；OOS 23 笔<30=晋升条款短板（paper 自然积累） |
| **DROUGHT-CE-01** | 地量反转一号 | vol_drought_reversal | CE | 0.5538 | **1.213** | 0.590 | 「地量出地价」民谚出厂实证；×3 0.454 亦越线 |

编制扩容 3→6（2026-09-23 G2_FOLK，锚定门 6/6 逐位复现+smoke 20/20）。全员 paper 0 月（残月不计）；**2026-10-31 首月晋升检查**（hr.py 自动裁决）。

## 三、候选池与袖珍池

- **G1' 候选归档（G2 FAIL 不复活）**：vol_breakout@ce（0.467）、duck_head 双制（0.682/0.535）——成本厚度条款杀。
- **袖珍池累计 23 格**（max|corr|<0.30 低相关分散化素材）：NSP1 6 + 批2A 3 + 民间 12 + 排队 2。**P3 并入决策=条款性不成立零跑收线**（SLEEVE_P3 修正案准入条款：成员 ×2>vi 0.4004——23 格无一达标，最高 oversold 0.142/bb_squeeze −0.016）。

## 四、因子库

| 层 | 数量 | 状态 |
|---|---|---|
| 内部因子引擎 `engine/factors.py` | **28**（实测导入） | 动量6/波动5/量价6/偏度峰度2/微观结构2/其他7；J6 复合因子（低波0.3+低振幅0.3+动量0.2+价位0.2）=注册员底座 |
| GTJA191 | 89 宽筛池 | 单因子严口径 0/183（双库实证「单因子过墙无望，合成是唯一路径」）；合成 P-2 判负（弱尾稀释） |
| WorldQuant101 | 36 池 | 严口径 0/82 同判；跨库联合合成=开放池（bm-b 车道） |
| 龙虎榜 LHB | **幸存 3** | lhb_count_20（IS IC −0.0642/IR **−0.84**=项目最强单因子证据）/lhb_days_since/lhb_amt_share_20（占比类>方向类）；合成双机双路判负→定案单因子用法 |
| 涨停/情绪族 | 7 登记 | zt_count_60/zt_dist/lb_height/zt_premium/mood_temp/lhb_follow/bias_extreme（B 层配套，批二后按先验降级） |
| 热度/注意力 | L1+L2 | 人气榜日快照前向采集+单股 366 日史回填（O-1850）；L2 首场 IC 批=**0/4 pass 诚实判负**（PC_L2_IC·2026-09-24·V2 IR 线瓶颈·mom_20 IR−0.193 最强·素材池留档带幸存者折价） |

## 五、门禁链与常数（唯一权威=`p2_calibration.json`+各预注册）

> **判据管辖（O-2215/O-2250）**：新批次判线以 `research/BACKTEST_SCIENCE.md` D1 技能线 v2（随账本 N 抬升·science_gates.py 数据驱动）为准；下述 0.4004/0.3521 等=**v2 前历史常数，仅存量复现用**。注册判据=DSR≥0.95+CI 下界>0+PBO≤0.25（G2.5 三检）。

- **G1' 六条款**：全期>max(随机 p95)·年化>0·回撤≥−35%·≥30 笔·OOS 双正·全期>被动+0.1；**记录门常数**：default i 线 **0.3521** / vi 技能线 **0.4004** / CE i 线 **max(本批 CE p95, 0.4474, 0.4229, 0.3521)**。
- **G2 出厂门**（五条款）：中心复现逐位+邻域红点不过半+×2>vi+逐年无崩年（>−35%）+≥30 笔。
- **口径铁律**：OOS=2025+ 恒盲；成本 13bp 恒开；evidence_cutoff=2026-09-22 锚定；随机 null n=50/退出制逐批新抽样（seed 40k→44k 链）；预注册跑前写死禁调门槛禁重跑；账本 N 全试验记账（作废跑也计）。
- 交易红线=`firm/risk/iron_rules.md`（配置三红线 T0+10 铁律+熔断（AI 自动复盘）+合规边界）。

## 六、引擎与退出机

- `engine/backtester.py`：T 信号收盘算→T+1 开盘成交；T+1 规则；13bp 成本模型；fill_guard（B 层附加，None=逐字节不变）。
- 退出优先级冻结：熔断>止损>时间>兜底（`engine/exit_rules.py` 禁改）。
- 退出机谱系：default（引擎默认）/ **CE 注册机**（loss_time 16+time_decay 25d/5%+trailing 0.10，桥接+ExitPatch 工厂补丁）/ 432 均线基线（全灭参照系）。

## 七、判定律（机制法=批批实证固化，动物园维护）

1. **确认构造谱系**（出厂实证）：形态确认类（吞没/次日收复/极缩量首阳）> 形态+语境类 > 指标超卖类——三确认族全部注册出厂，无确认同族全弱。
2. **振荡超卖类四族全灭律**：kdj/rsi 系（批2A）+cci/williams（排队批）单一超卖读数在 48 池无一立起。
3. **背离域双负律**：macd_divergence −0.611 + rsi_divergence −0.508=日线近似构造下背离在宽基 ETF 域不成立。
4. **跨域单向门**：股票域「强势延续」行为类（strong_close/streak/soldiers/lian_yin）迁 ETF 域深负；接力/打板系同判（批二 B 层 0/19 佐证）。
5. **CE 增益=砍笔减成本通道**：增益=砍笔量函数；零咬合=零增益（三批实证）。
6. **成本弹性律**（J15）：α 厚度必须过 ×2 线才有出厂资格；「好信号坏成本」标本=duck_head（邻域全绿+最差年绿，纯死于 ×2 0.258/947 笔 churn）→ 新构造须前置换手预算。
7. **52 周极值单边性**：近高点=趋势延续 α，近低点=接飞刀（George-Hwang 只在强手侧成立）。

## 八、批次史（预注册→一次定稿全链 · 账本 N 演进）

| 批 | 判决 | N 后 |
|---|---|---|
| 432 基线 | 0/432 全灭（换血起点） | 432 |
| P1 海选（J7）59 跑 | G1 0（诚实）→观察名单 | 521 |
| P2 零假设校准（J8）122 跑 | **G1' 门立**：幸存 3 | 643 |
| G2 深化（J10）27 跑 | 3→0（成本×2 全灭） | 670 |
| J14/J15/J16-J19 | **VOLATILITY-CE-01+2 员注册**（编制 1→3） | 727 |
| P3 组合（EW/IV） | EW validated；真独立引擎 1.5 个 | 727+ |
| J9a/LFC/NSP1/G2_NSP1/SLEEVE_P3 | 候选 2→G2 双 FAIL；袖 6；策略线收线 | 1073 |
| P-1a/b GTJA191/WQ101（因子线） | 0/183+0/82 双库严口径 | 1435 |
| P-4 批一（A 层易族）121 跑 | 0 候选+袖 2 | 1556 |
| P-5 随机起点实战检验 203 跑 | 3 员全 FAIL 0.70 线（诚实） | 1883 |
| P-4 批 2A（TA 迁族）137 跑 | 候选 3（engulf 双制/vol_breakout）+袖 3 | 2020 |
| P-4 批二 B 层（bm-b）70 跑 | 0/19 七族全负 | 2090 |
| P-4 民间大扩容 209 跑 | 候选 6（3 族双制）+袖 12 | 2299 |
| **G2_FOLK 出厂门 94 跑（47 有效+47 作废双跑）** | **3 注册（编制 3→6）+2 FAIL** | 2393 |
| **P-4 排队批 128 跑** | 0 候选+袖 2（bb_squeeze） | **2521** |

## 九、开放池（认领制 · 「队列永不清空」O-1819）

跨库联合合成（GTJA89+WQ36+LHB3·bm-b）/~~热度 L2 因子首场 IC 批~~（已收线 2026-09-24：0/4 pass·PC_L2_IC·bm-a）/袖珍 P3 类并入（×2 条款当前 0/23 达标·若未来袖珍 ×2 达标另开预注册）/CCI·威廉·收缩变体（按判定律降先验）/P-6 记分卡补课/日线源双腿/现金腿引擎特性预注册/paper 薄余量 watchdog/月度经营简报。

—— quant 专管 GM 会话 · 2026-09-23 22:55 · 维护=周进化轮（动物园/本册同步），新族先入动物园再入厂
