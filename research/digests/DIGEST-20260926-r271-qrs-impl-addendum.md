# DIGEST-20260926-r271-qrs-impl-addendum · QRS 复核位补录：SignalMaker/qrs.py 实现件 200 落地=r264「运行面缺失」披露收口 + #86 陈旧指针勘误（bm-b r271 · T-76 wave-10 face (c) 后续补录）

> 执行人：bm-b（OS iteration loop r271 · r264 下窗指针维持面复核·开工前反重复双验：r264 复核位已收线（DIGEST-20260926-wave10-qrs-rsrs-family-recheck）+ referee deep-read 已收线（DIGEST-20260926-wave10-referee-deepread-2609-27051）=本片不重开任何已闭面，只做两件增量：①r264 时双 404 的实现件本轮 200 实取=证据升级+披露收口 ②r263/r264 遗留段 #86 陈旧指针勘误=防未来轮重复认领）。
> 性质：证据补录卡，登记≠采纳；**本片零跑批零引擎零账本零台账零 zoo 改写**（r264 裁定不变，证据面升级）；funnel 过闸数维持 0。
> 纪律：QuantsPlaybook 全库零 LICENSE=代码结构性禁抄（r218 实证维持），本卡只做机制叙述提取+clean-room；temp 留存不入 git。

## 〇、通道实况（3 外呼全串行 3s · 全 200）

- trees API master `?recursive=1`：2742 entries·truncated=False（r216/r218/r263 四读一致·库存稳定）；QRS 目录 16 entries + `SignalMaker/qrs.py` 在树（r264 记双 404 的件**本轮同 gh-proxy 配方 200 直通**=彼次 404 为瞬态/取数面抖动，非库缺件）。
- gh-proxy raw：`C-择时类/QRS择时信号/QRS.ipynb`（1,051,168B·40 cells）+ `strategy/rsrs_strategy.py`（5,993B）+ `SignalMaker/qrs.py`（12,122B）全 200。
- raw 取数配方=percent-encode CJK 路径 + master 分支字面（r222 通道律照旧）。

## 一、实现件证据升级（r264 §〇「SignalMaker/qrs.py 404→机制由叙述承载」收口）

r264 裁定面（族变体实证确认·非分位数回归）当时由 notebook 数学叙述+解析恒等式承载；实现件落地后**四项主张全部在代码层坐实**：

- **β_OLS 解析闭式=代码字面**：`calc_beta(low,high) = np.std(high)/np.std(low) × corrcoef(high,low)`——单变量 OLS 斜率的解析恒等式（β=σh/σl·ρ）直接落码，非任何分位数回归调用；**库内零 QuantReg/quantile loss 症迹**（全文件检索无 statsmodels QuantReg/quantile 调用）=「非分位数回归」翻案在实现层终审坐实。
- **实现自证腿**：`test_func` 用 `statsmodels OLS(high, add_constant(low))` 取 `res.params[-1]` 与 qrs.beta 对照=作者自己把实现锚定在 OLS 语义上（实现↔研报关系=OLS 特例面，研报「分位数框架」=方法论叙述层）。
- **惩罚力度轴落码**：`regulation = corr^n`（`fit` 默认 n=2；notebook R0..R3 扫描=n∈{0,1,2,3}）；`adjust_regulation=True` → `regulation / regulation.rolling(regression_window).mean()`（量级归一=r264 叙述的逐字实现）。**zscore 窗精确定位**：`calc_zscore` 只作用于 beta 序列（M=600），惩罚项外乘——r264 恒等表的 zscore 面在「β 之后、惩罚之前」，修正版（zscore(β×R²)）与实现（zscore(β)×corr^n）的差异=zscore 作用点，族内参数化面不入另立行判据。
- **消费面参数全落码**：N=18（regression_window）/M=600（zscore_window）/±S=0.7（notebook `upperbound/lowerbound`）/长多规则=`RSRSStrategy` CrossUp(信号,0.7) 买入·CrossDown(信号,−0.7) 平仓（长多·T+1 开盘执行·佣金 1% 预留=bt 包装器面）——r264 参数冻结候选五项（N/M/S/R=2/量级归一）全部实现层在位，消费时点可直接引用本卡。

通道质量面：r264 因「运行面缺失」如实降 B+ 维持；实现件落地后机制+实现双在位，**质量门 B+ 维持不再有降级理由**（升 A− 无必要=宣称数字照旧零采信【未实证】）。

## 二、勘误：r263/r264 遗留段 #86 指针陈旧（防重复认领面）

- r263 §五 / r264 §四 均写「#86 ICU 均线仍通道级（r218 遗留 open-to-any）」——**陈旧**：#86 已于 r222 深读参数化冻结交付（DIGEST-20260926-r222-icu-ma-paramfreeze：RM 稳健回归 ICU(N)+上穿买/下穿平+三套 N 并存 snooping 披露），zoo #86 行已翻冻结级。两 digest 属已 commit 流水不回改（append-only 纪律），本卡为唯一有效勘误载体：**#86=已闭，未来轮禁按 r263/r264 遗留段重复认领**。
- #90 AO 构造分歧二选一（TradingView SMA(H+L) vs 研报 SMA(H−L)）=**真 open 维持**（随 T-34 快线池评估一并定，r218 指针照旧有效）。

## 三、遗留与移交

- T-76 face (a) 常设通道 09-28 周一开窗照旧（jisilu run-9/hibor run-5/guorn run-3 + jin-gong post-holiday verify）；face (c)/(d) 及其后续（二扫+paramfreeze 95/96+QRS 复核+referee 深读+本补录）全收线。
- funnel 记账（O-1721 双列）：本片深读收割 0（证据补录非新登记）/过闸 0（登记≠采纳维持）。
