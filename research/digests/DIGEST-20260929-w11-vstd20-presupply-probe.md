# DIGEST 2026-09-29 W11 预选探针：census VSTD20_q20 低波族跨血统锚裁定（bm-c r234·**W11 候选家族甄别件**）

> 执行者：bm-c（OS iteration loop r234 · TRIAL_LABOR_LAW §1 常供线供给步 · W11 supply window 开窗前的家族甄别）。
> 性质：内部研究用途，不构成决策建议；确定性零网络探针（in-repo synthesis face）——本窗零 fetch 如实注记（O-1721 每日 ≥1 源常态线 2026-09-29 已由 bm-a T-102 lane-1/lane-4 两件消化覆盖·本件=仓内探针/结果合成面非外源采集面）。
> 探针=results/_r234bmc_vstd20_w11_probe.py + 事实件 results/_r234bmc_vstd20_w11_probe_facts.json（r431 七门血统+r228 MOM 探针范式·确定性交叉核 r417/r423/r431/r228 四件全绿）。
> 甄别对象=census O-1855④ 四正信号族最后一个未消耗族 VSTD20_q20（r231/W10 digest「三重近邻风险暂缓」的悬案）。

## 〇、采集面 funnel（收割数 vs 过闸数·采集≠入册）

- 本窗 fetch 0 次（仓内探针面）；仓内证据消费 4 件：results/a158_tsgate_p1.json（bm-a r438/439 今日烧毕）+ r417/r423/r431/r228 四冻结探针事实件（逐位复现全绿）。

## 一、家族定义（结构移植零发明+命名撞车声明）

- **VSTD20_q20 门**（census 族·O-1855④）：`vstd20(d)=20 日收益样本 std（含 d·min_periods=20·ddof=1）`——与 W4 冻结 vol20 **同一序列**（构造恒等·如实注记）；`q20_ref=vstd20.rolling(252,min_periods=120).quantile(0.20)`；**vstd_low（门开）=vstd20<q20_ref**（低波分位门·普查正信号方向）。预热律：ret 首有效 bar-idx 1→vstd20 首有效 idx 20→q20_ref 首可判 **bar-idx==139**（与 MOM r228 锚同位·探针 fail-closed 断言实测）。census 侧精确定义复核（工具件在 bm-a toolstack/research/gate_census.py·本机不可达如实）=W11 候选复用清单项（W10 item-ix 同款）。
- **命名撞车声明**（A158_TSGATE_P1 prereg §1 D6 逐字血统）：A158 `VSTD20`=**成交量**标准差比（Std($volume,20)/($volume+1e-12)）≠census `VSTD20_q20`（价格波动分位）——两构造不同，结果表按各自定义。

## 二、三面弱复现链+邻接坍缩实证（裁定证据面）

- **三面弱复现（时序判别力面）**：① census 原信号 +1.746 中位 t（61% 工具·**in-sample 描述面**）；② gate_verify/A8（09-29 定谳）=PARTIAL——**IS 反号**→降格 C1 输入特征非独立臂；③ **今日 A158-TSGATE-P1**（bm-a r438/439·1,724 码 314 门·IS/OOS 分诊）最近亲 STD20_q10（价格 std 低侧）=**PARTIAL：IS med_t −1.204 / OOS med_t +0.924 / med_thin −0.00067（成本面吃净）/ pos_share 0.58**（A158 成交量面 VSTD20_q10 同窗=PARTIAL·IS +0.41/OOS +0.20 近零）。三面合读=正信号不稳健，census 面为 in-sample 偏乐观读数。
- **邻接坍缩实证（本探针主发现·r231 悬案了结）**：510300 全史（3,483 行·cutoff 2026-09-22 冻结·decidable 3,344 日）上——**vstd_open 840 日中 724 日（98.5%）落在 W4 VOL calm 面内**；wild 面内 vstd 开窗率仅 **0.76%**；**vstd∧wild 独立增量日=11 日/2,964 联合可判日≈结构性空集**（vs MOM 的 121 mom-独有日=条件空间增量非空的对照面）。VSTD 低波分位门≈W4 calm 面的子集门：**坍缩邻接成立，三重近邻风险（W4 VOL/W9 AMP narrow）中主邻接 VOL 实锤**。
- **锚面前向差分（描述面）**：20 日前向 open +0.6586% vs closed +0.5345%（差 +0.124%·Welch t=**0.623**）；5 日差 +0.0055%（t=**0.054**≈零）——510300 锚面信号弱于 census 宇宙面宣称且 5 日窗近零（vs MOM 探针同面 20d t=1.34）。
- **政体/极端日面**：bear 27.53% vs bull 23.93%（弱载息）；**七极端日 7/7 vstd=closed（ratio 1.2-5.9 倍于 q20_ref）**——低波门危机日结构性回避（vs AMP 7/7 wide/MOM 2/7 open）=calm 子集的防御性继承面非独立增量。
- core48 员级开窗率 min 16.53%/median 21.10%/max 33.91%（48 员全非退化）；八门 256 格交叉 88 非空/168 空（min 1/max 59·全可判 3,305 日）。

## 三、门裁定：**DEMOTE（家族甄别判负·非关线）**

- **裁定：VSTD20_q20 不入 W11 试用语法轴候选**——(a) 坍缩邻接实证（98.5% ⊂ W4 calm·增量 11 日）=作为独立语法轴≈W4 条件空间的近重跑（TRIAL_LABOR_LAW §4 同语法禁重跑精神·防重复开发律）；(b) 三面弱复现链（census in-sample 乐观 vs gate_verify IS 反号 vs A158-TSGATE STD20_q10 PARTIAL 成本吃净）；(c) 锚面前向差分弱（t=0.62/0.05）。** lawful 重开通道不变**（RANDOM_LARGE_SAMPLE_LAW s5：新 prereg+新工具面=合法重开·本裁定=候选甄别非审判线关闭）。
- **W11 候选池转向（家族甄别的正面产出）**：census 四正信号族全数消账（MAD60/RSV60→W8 TSTATE 已烧·ROC20→W10 在途·VSTD20→本件 DEMOTE）——**W11 轴族料面=今日 A158-TSGATE-P1 48 PASS 门池**（top：STD20_q90/STD10_q90 高波动侧 OOS med_t +2.06/+2.04·RSQR20/10_q90 趋势拟合·SUMN/SUMP 量族 10-30 窗）——**首级消费面=bm-a GATE-RECHECK-A158 复核队列**（r439 in-册·高波动侧 STD20_q90 已指名）；试用语法轴面=不同消费面（W8 TSTATE vs A8 降格先例=合法），W11 起草窗（W10 screen 落地带 arrive 后）从 48 PASS 池选族须带：与 W3-W10 已烧轴的 D6 邻接披露+跨血统锚复用（ROC20_q10 锚 r228 已由 A158-TSGATE live-reproduce）+GATE-RECHECK 复核结果对齐披露（避免双头烧）。
- **诚实注记**：本件=candidate-family triage face（探针事实面非结果面·marks +0·SEED +0·账本 +0）；W11 波的开窗条件不变（W10 GENERATE→SCREEN→JUDGE 落地后 screen null p95 带 + 本件池指名）。

## 四、结论应用表（P-65 强制·落点四选一）

| # | 结论 | 落点 |
|---|---|---|
| 1 | VSTD20_q20 跨血统锚甄别=DEMOTE（坍缩邻接 98.5%+三面弱复现+锚面弱差分） | **判负留痕（终态·候选甄别面）**：W11 轴候选池除名；lawful 重开=新 prereg+新工具面（s5 通道不变） |
| 2 | census 四正信号族全数消账；W11 族料面=A158-TSGATE 48 PASS 门池 | **任务单候选指名**：W11 candidate drafting 窗（W10 screen 带落地后）从 48 PASS 池选族·D6 邻接披露+GATE-RECHECK 对齐双带·首级消费面 bm-a 复核队列披露随附 |
| 3 | A158-TSGATE STD20_q10（低波侧）PARTIAL/STD20_q90（高波侧）PASS 同窗双读 | **证据升级注记**：高波动侧 OOS 强读数归 bm-a GATE-RECHECK 车道（r439 已指名·本件不重复立项不撞车道） |

— bm-c r234 落盘；W11 开窗精确续作点=W10 SCREEN/JUDGE 落地（bm-b 车道）+本件 §三池指名。
