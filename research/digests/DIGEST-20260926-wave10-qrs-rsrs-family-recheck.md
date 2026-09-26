# DIGEST-20260926-wave10-qrs-rsrs-family-recheck · QRS 深读复核位收线：RSRS 族变体实证确认+「分位数回归」定性翻案（bm-b r264 · T-76 wave-10 face (c) 后续）

> 执行人：bm-b（OS iteration loop r264 · r263 下窗指针「QRS=RSRS 族疑似变体深读复核位」·开工前双板核：任务板无 open 票、复核位仍【未实证】标记、本机=T-76 owner 单写者零撞车）。
> 性质：族裁定证据卡，登记≠采纳；**本片零跑批零引擎零账本零台账**，funnel 过闸数维持 0；产物=ASTYLE_ZOO §十五波-10 bullet 翻正 + #24 行复核注记。
> 纪律：QuantsPlaybook 全库零 LICENSE=代码结构性禁抄（r218 实证维持），本卡只做机制叙述+参数语义提取+clean-room；外呼全串行 3s 间距（R109）；trees API 权威清单（R216 律）。

## 〇、通道实况（trees 1 调 + raw 3 件全 200 · SignalMaker 2 件 404 诚实记录）

- trees API master recursive：QRS 目录 16 entries（QRS.ipynb + backtrader_utils×4 + src×5 + strategy×2 + requirements.txt + 参考 PDF）。
- gh-proxy raw 3 件：QRS.ipynb（1.05MB·40 cells 全量提取）、strategy/rsrs_strategy.py（5.9KB·bt 包装器）、src/utils.py（2.2KB）。
- **SignalMaker/qrs.py + __init__.py 双 404（诚实披露）**：HEAD notebook `from SignalMaker.qrs import QRSCreator` 引用悬空=库内不可跑面；机制全量由 notebook markdown 数学叙述+调用签名 fit(18, 600, adjust_regulation=True)+bt 包装器承载——通道质量降 B+（机制完整可裁定，运行面缺失如实披露）；README 侧自证「RSRS 累积复现 4 版本链：原始版→修正版→QRS版→本土改造版」（营销计数诚实注记 r263 已立，此处仅作族链佐证）。

## 一、质量门/AI 污染扫描

真人复现叙述特征齐全：中金研报精确口径注记（2021-01-21 量化择时系列(1)）+ 反直觉发现诚实讨论（R0 无惩罚时年化反而高→定位为惩罚项量级未归一→归一后 R0→R2 单调改善、R2 后回落=参数面真实验证痕迹）+ 动态阈值权衡如实报劣（年化 8.48%<固定约 1%，换回撤 50.21%→39.30%）。无占位码/方法学空洞红旗。**质量门 PASS（B+ 通道·登记级）**；宣称数字照旧零采信【未实证】。

## 二、裁定：QRS=RSRS 族变体【实证确认】，双面翻正「分位数回归」初读

- **同基确认（族并入成立）**：本体论同一=支撑/阻力相对强度（δhigh/δlow 读数）·High~Low 回归斜率·窗 **N=18**（同光大正典窗）；README 版本链把 QRS 列为 RSRS 复现第 3 版。
- **估计器翻案（核心）**：实现层无 QuantReg/quantile/OLS 拟合调用——**解析式闭型斜率**：指标=(σh/σl)·corr(h,l)^R，惩罚力度轴 R∈{0,1,2,3} 扫描。数学恒等式展开：
  - **R1 = corr·σh/σl ≡ β_OLS = 原始版 RSRS 斜率**（解析恒等）；
  - **R3 = β·corr² = β·R² ≡ 修正版 RSRS 加权**（解析恒等）；
  - 复现者实测选 **R2**（量级归一 adjust_regulation=True 后：指标=信号项×(惩罚项/惩罚项滚动均值)，R0→R2 效果随惩罚力度增强、R3 回落）=族加权轴的中间档——**QRS 实质=RSRS 族「修正版 R² 加权」轴的一般化参数化变体，非异族**。
- **「Q」的定性翻案**：研报/复现实现均取**正态标准化 z-score（M=600 窗）±S=0.7 穿越触发**（同光大 RSRS 标准分 M=600 面）；「分位数」仅作为标准化备选在研报叙述中被提及、**未进实现**——r261 二扫「分位数回归斜率 vs OLS」初读按报告标题臆读，深读翻案（防臆测标记律的正工作产品：初读存疑→深读实证→翻正登记）。
- 参数冻结候选（消费时点用）：N=18、M=600、S=0.7、R=2（量级归一面）、基准 000300.SH、bt 包装器佣金 1%、动态阈值备选（1 年滚动 σ 边界：年化 −1% 换回撤 −10.9pp，研报权衡面记录）。
- 本片不改 #24 行登记批构造基（同主题禁另立行；RSRS 行 P-4 批 2A 判负/OOS 强 0.840@ce 读数维持——QRS 为族内变体证据，非新候选面）。

## 三、登记行状态翻转

- ASTYLE_ZOO §十五 波-10 bullet：QRS 由「疑似变体·未实证=深读复核位」→**「族变体实证确认·复核位收线」+分位数定性翻案注记**；#24 行追加复核实证注记（消费路由不变）。
- funnel 记账（O-1721 双列）：本片深读收割 0（族裁定非新登记）/过闸 0（登记≠采纳维持）。

## 四、遗留与移交

- referee deep-read（A-lead 2609.27051 anytime-valid）=可选下窗（r260 指针维持）；#86 ICU 均线/#90 AO 二选一=r218 遗留 open-to-any 照旧。
- T-76 face (a) 常设通道 09-28 周一开窗照旧（jisilu run-9/hibor run-5/guorn run-3 + jin-gong post-holiday verify）。
