# 调研纪要 DIGEST-20260923-ta-styles · 技术分析与操作风格（CEO 令 O-20260923-1828）

> 主题：3-15 日 ETF 波段域的经典技术分析（TA 指标/K 线形态/量价确认）与操作风格族谱——为 P-4 批 2A（A 层技术分析迁族海选）提供出处与素材裁定。纪律：生产采纳一律走 G1'/G2；本文只做知识收拢，不做任何「有效」宣称（宣称须证据指针，诚实律）。

## 一、外部来源

| # | 来源 | 要点 | 评级 | 建议动作 |
|---|---|---|---|---|
| 1 | Wikipedia: MACD（Gerald Appel 1970s）<https://en.wikipedia.org/wiki/MACD> | DIF=EMA(fast)−EMA(slow)；DEA=EMA(DIF,signal)；**信号线金叉**（DIF 上穿 DEA）=趋势加速读法；**零轴上穿**=多头动能确认。本批 `macd_trend` = 金叉态+零轴确认双条件 | A（日线即用） | 迁 M0923 `MacdTrend` 骨架入 `strategies/ta.py` 过闸 |
| 2 | Wikipedia: Stochastic Oscillator（George Lane 1950s）<https://en.wikipedia.org/wiki/Stochastic_oscillator> | %K=(C−Low_N)/(High_N−Low_N)×100；%D=SMA₃(%K)；**KDJ 中国市场变体**：K=SMA(RSV,3,1)、D=SMA(K,3,1)、**J=3K−2D**（超钝化放大）；J<0 超卖区。本批 `kdj_rev` = J 超卖+趋势均线过滤 | A | 迁 M0923 `KdjReversal` 骨架过闸 |
| 3 | Wikipedia: Candlestick pattern <https://en.wikipedia.org/wiki/Candlestick_pattern> | **锤子线**=小实体近高+长下影（下影≈实体 2-3 倍）+下跌趋势中出现=多头反转；**阳包阴**（bullish engulfing）=阳线实体吞没前阴线实体；晨星=大阴+小实体+收盘深入阴体的阳线。两库（本仓 36 骨架+M0923 35 族）均无 K 线形态族=真实缺口 | A | 新设计 `hammer_reversal` / `engulf_reversal` 入批 |
| 4 | 光大证券金融工程 2017《基于阻力支撑相对强度（RSRS）的市场择时》（公开研报，M0923 `RsrsTiming` docstring 出处，In-库：`Money0923/quant/strategies.py` L282） | N 日 high~low 回归斜率 β=支撑阻力相对强度；β 的滚动 z-score 上穿买入阈值持有、下穿离场阈值清仓；时序择时（横截面无关）。M0923 版 target=单 ETF（510300 等） | A | 面板化适配（逐 ETF 自算 β z 态）预注册后入批 |
| 5 | M0923 系统审计（`Money0923/SYSTEM_AUDIT.md` §4，35 族 sane 回测）+ 游资/极端风格节（strategies.py L774-887） | **尾盘强势 strong_close**：收盘位于日内区间顶部 (close−low)/(high−low)≥pos + 放量 + 收阳 → 博次日惯性（日频诚实近似）；**连阳 streak**：连续 N 日收阳接力（与累计动量不同维度）；**放量突破 vol_break**：创 N 日新高+量≥均量×倍数（量价确认，无量突破=假突破常客） | A（ETF 域第一优先，playbook §1.2 早已点名） | 三族迁骨架入批 |
| 6 | George & Hwang 2004（52 周高点锚定）/ Blitz et al. 2011（残差动量）——学术锚（In-库语境：M0923 high_52/resid_mom sane +43.9%/+28.5%） | 高点接近度/剔β动量的学术出处。**但本仓已筛**：high252_prox@ce=NSP1 G1' 候选（0.438/0.889）；动量域变体双筛（xsec_mom P1+sharpe_mom NSP1 0.028≈0） | D（知识储备：本仓已消化，重跑=dredging） | **出批**，理由入 P4_BATCH2A.md §2 |

## 二、内部证据链（本仓已立机制读数——读结果时的先验）

- **CE 增益=砍笔减成本通道**（P4 批一 §8.3）：CE 机传输通道是换手削减量；状态制族 CE 增益≈0，轮动族增益来自砍笔。本批 6 迁族全为状态制→预期 CE 增益小，×2 成本压力是主死因候选（J15 成本弹性律）。
- **族依赖**（NSP1 §五修正）：事件/短趋势族可达与在册 3 员低相关（袖珍候选池）；轮换族难。本批 hammer/engulf/streak/strong_close 皆事件/短状态族→袖珍标签可期。
- **反转族全期被 IS 拖累**（批一预测⑤）：kdj_rev/hammer 等反转族预期全期低于 vi，OOS 或正——预注册预测如实写。
- **日线铁律**（ASTYLE_ZOO）：一切信号仅日线 OHLCV+amount 可算，持有≥3 交易日，无盘中信号。

## 三、操作风格族谱结论（「操作风格分析」）

当前风格覆盖=8 流派（趋势/均值回归/动量/波动率/情绪资金/日历/宏观/事件）+动物园 42 族登记。本批补齐的**技术分析风格缺位**：①经典指标系（MACD/KDJ/RSRS）；②K 线形态系（锤子/阳包阴）；③量价确认系（尾盘强势/放量突破/连阳）。三系全部 3-15 天波段语义（信号收盘算、引擎 T+1 开盘执行）。批后动物园 §新 TA 系登记行补齐。

## 四、采纳管线

纪要 →（本批）动物园登记+预注册 P4_BATCH2A → 骨架 `strategies/ta.py` → core48 海选（G1' 记录门常数+随机基线 seed 42_000 系）→ 幸存者=G1' 候选（G2 另开预注册）。禁：跑后调门槛/重跑/挑口径。

—— quant 专管 GM 会话 · 研究部（外调轮·专项） · 2026-09-23 18:45
