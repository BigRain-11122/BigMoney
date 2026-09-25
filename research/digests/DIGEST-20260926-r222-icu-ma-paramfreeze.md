# DIGEST-20260926-r222-icu-ma-paramfreeze — zoo #86 ICU 均线择时深读参数化冻结卡

> 认领：bm-b r222（F-04 声明 MSG-20260926-0415-bm-b 先行）·T-64 slice-5 face (a)/(c)/(d) open-to-any·单写者=本文件+ASTYLE_ZOO #86 行。
> 纪律：QuantsPlaybook 无 license=代码结构性禁抄，只做机制叙述提取+clean-room；外呼全串行 2.5s+（R109）；trees API 权威清单（R216 律）；实现位=vendored src 优先真值源、研报/notebook 叙事=机制叙述源，两源分歧双列披露（R218 律）。

## §〇 通道留痕（fetch 计账）

- trees API `?recursive=1`：2742 entries·truncated=False（与 r216 一致·库存稳定）。
- 实现位命中：`C-择时类/ICU均线/`（notebook `ICU_MA.ipynb` 390KB + vendored `src/{icu_ma,bt_strategy,backtest,bt_icu_ind}.py` + 研报 pdf `参考/20230412_中泰证券_….pdf` + 图 `img/{ma,2}.png`）。
- **通道律新例：QuantsPlaybook raw 直链默认分支=`master` 非 `main`**（trees API 接受 HEAD；raw 字面必须 master——main 5 连 404 后 master 5/5+2 图全 200）。
- 计账：trees 1 + main 404×5 + master 成功×7 = 13 外呼（全串行）。

## §一 实现位真值源（vendored src = 参数冻结真值）

**构造**（`src/icu_ma.py` + `bt_icu_ind.py`）：
- ICU 均线(N) = `price.rolling(N)` 窗口内做 **Siegel(1982) Repeated-Median 稳健回归**，取端点拟合值 `intercept + slope×(N−1)`（`scipy.stats.siegelslopes`, method='hierarchical'）。本质=RM 回归外推均线：对窗口内离群点稳健（剔尖刺）、比 SMA 更贴价、拐点处超调（图 1 复现对比目测验证：「大势一致、局部放大、贴价+超调」）。
- 复现者解读留痕（MD[3]）：「中泰写的有点绕，应该是使用重复中位数（RM）下的稳健回归」——构造命名=复现者 clean-room 判读，非研报原文逐字。

**信号**（`src/bt_strategy.py`）：close **上穿** ICU(N) → 买入（`order_target_percent(0.95)`）；**下穿** → 平仓；纠缠维持原仓。=「close vs 单线」交叉（docstring「10日均线上穿5日均线」为陈旧注释，非实现）。

**成交与成本**（`src/backtest.py`）：
- `cerebro.broker.set_coc(True)`=**T 日收盘信号当日收盘成交**——MD[10] 明示「根据研报给出的回测规则 T 日信号 T 日 close 买入」→ coc=True 是研报口径忠实实现 ✓。
- 成本：佣金万 3 双边+印花税千 1 仅卖出+滑点万 1；初始 1 亿；仓位 0.95。

**两源分歧双列（R218 律）**：①成交口径：实现位真值=coc 当日收盘 ✓（研报口径）；`bt_strategy.py` docstring「T+1 日开盘买入」=陈旧注释面（非真值）。②参数 N 三套并存：研报正文叙述 N=5（「过去 5 个交易日」）；复现者 backtrader+skopt 贝叶斯寻参 Best **N=120**（score 10.30）；可微目标函数（信号×对数收益相关）Best **N=15, M=20**（score 0.0529）——消费位冻结须按三套并存披露+snooping 折价评估。

## §二 宣称数字（D 级目测·零采信面）

研报图 7（样本窗 2005-01-04→2023-04-06，沪深300）：策略累计净值 ~10 vs 基准 ~4；策略最大回撤 ~−20% vs 基准 ~−60%+。图内无年化/夏普/胜率正文数字（pdf 正文未提取——按律宣称数字 D 级零采信，绝对收益导向/回撤减半=叙事面）。资料来源标注：Wind，中泰证券研究所。

## §三 黑名单四死路径对照 + D6 机制段

- **单一读数警示（ta.py 判定律 2）**：close×ICU 单线交叉=单一趋势读数——**须带确认构造**才可独立成策略；消费位=T-34 前置快线候选（快线族=前置粗筛候选非独立策略，A/B harness 3,200 起点判据定去留，确认线/刹车/T0 权威全不动）→ 警示已由候选池结构性化解 ✓。
- 无背离（趋势跟随族）✓；低换手（日线择时级）✓；域原生（ETF/指数日线在册面板）✓；算力预算条款：`rolling(N).apply(siegelslopes)` = O(T×N²)（RM 回归逐窗 O(N²) 对），N∈{5,15,120} 在 T≈8.8k 行面板=秒级~分钟级可列 ✓。
- D6=行为偏差（深化 zoo 行初拟）：RM 稳健回归=对窗口内噪声尖刺不敏感的真实趋势估计→快于 SMA 的趋势拐点识别；付费方=无纪律追涨杀跌者（反应不足锚：新信息沿短尺度→长尺度扩散，ICU 贴价性=更早捕扩散起点）。
- 族内 corr 待查：#24/单 MA 择时族、GRID_P1 MA 交叉通道原语（消费切片 T-34 快线池评估时同族合并条款必查）。

## §四 参数化冻结（消费位落地形态）

- **实现位=MA 族参数化变体，禁新引擎件（#81 先例）**：ICU(N) 作为 scr 原语层 rolling-apply 变体入既有 MA 框架表达；T-34 候选池入池形态=快线腿 `ICU(N)` vs 慢线腿 MA20/60（叉快线族内变体，N 按 §一 三套披露面带 snooping 折价，A/B 判据冻结权归 T-34 harness）。
- 本卡=通道级→参数化冻结收口：#86 行状态更新为「深读全档·参数化冻结卡已产」，后续消费切片（T-34 快线池评估）直接引用本卡 §一/§四，禁重复深读（防重复铁律）。
- 复现质量定位：构造对比图形态吻合（趋势/拐点一一对应）；宣称净值曲线未逐数字复现（notebook 无逐年绩效表输出）——**复现面=构造吻合+寻参可跑，绩效宣称面=未实证**（诚实标注，非「复现失败行」亦非「复现成功行」）。
