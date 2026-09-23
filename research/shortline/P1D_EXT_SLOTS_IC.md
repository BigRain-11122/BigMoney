# P-1d 扩展槽因子批（两融/大宗/股东户数）IC 海选 · 预注册（跑前写死）

- 机器/车道：bm-b 循环轮（dept:研究）· round 45 认领 MSG-20260923-2155（commit 928ced5 锁）
- 令链：O-1819（24h 连续回测·队列永不空·回填本批）→ O-1850（热度/注意力因子域，HEAT_ATTENTION_SPEC §L14 扩展槽登记「源审计后定」）→ r39 源审计（DIGEST-20260923-heat-source-audit.md：三槽 2010/2013/2015 深度门全过=backtestable B 级）→ round-44 next_pointer 指针
- 范式：P-A LHB 批（IC 因子海选）一脉——零引擎跑、账本 N 不动、IC 计数记 JSON audit；**非数据源扩容新案**（源已在 O-1850 域登记并完成审计，本批=审计后预注册执行）

## §1 素材与口径（2026-09-23 探针实证）

| 槽 | 接口 | 粒度 | 史深 | 拉法 | 形状实测 |
|---|---|---|---|---|---|
| 大宗 mrmx | `stock_dzjy_mrmx(symbol='A股', start, end)` | 每笔 | 2013-01-04+ | 日期区间；**pageSize=5000 单页截断→rows==5000 必须二分重拉** | datacenter-web 域（bm-b r39 验通） |
| 两融明细 | `stock_margin_detail_sse(date)`+`stock_margin_detail_szse(date)` | 日频截面 | 2010-03-31+（探针 2010-03-31=25 行） | 逐交易日（交易日历=Money02 bars 日期轴）；空日=诚实跳过记账 | SSE 探针 1.0s/日 1740 行 |
| 股东户数 | `stock_zh_a_gdhs(symbol=季末)` | 季频截面 | 2015-09-30+（探针 2454 行） | 季末枚举 2015Q3→2026Q2=44 请求（8.1s/季，内部分页 11 页） | 列含 统计截止日-本次/上次、增减比例、户均持股数量/金额、总股本 |

- 价格/成交额基准面：Money02 bars 前复权面板（P-1c 缓存范式；**688xxx volume=100×股数坑 MSG-1945 强约束：一切 volume/vwap 消费先修 688**）
- 宇宙：bars 全池（P-1c 口径 ok 5129）∩ b_layer 掩码 ok_static 3517（O-1820 件3b）；因子逐日掩码分层 A=数据可得全截面、B=数据覆盖≥60% 的日子、C=强覆盖（P-A 掩码分层范式）
- cutoff：evidence_cutoff=2026-09-22（数据落盘允许到当日，因子矩阵截断到 cutoff 防未来）

## §2 因子（冻结定义，跑后不改）

**大宗族（日频，可用日=T+1 盘后披露→T+2 生效，P-A 滞后 1 交易日先例）**
1. `dzjy_count_20`：20 日大宗成交笔数（注意力计数，lhb_count_20 同构）
2. `dzjy_amt_share_20`：20 日大宗成交额/同窗 bars amount（占比类>方向类，P-A 教训）
3. `dzjy_prem_mean_20`：20 日 PREMIUM_RATIO 均值（折溢价=机构急于程度；预期正号=溢价大宗偏多）
4. `dzjy_deep_disc_5`：5 日内出现 PREMIUM_RATIO≤-5% 深折大宗的次数（知情卖出，预期负号）

**两融族（日频，可用日=T+1，余额披露同日盘后）**
5. `margin_buy_int_5`：5 日融资买入额均值/bars amount 均值（杠杆拥挤度，预期负号=拥挤反转）
6. `margin_bal_chg_20`：融资余额 20 日对数变化（杠杆追涨，预期负号）
7. `margin_short_int_20`：20 日融券卖出量/融券余量占比（卖空压力；预期负号；稀疏掩码诚实）

**户数族（季频，可用日=统计截止日+45 自然日→次一交易日，冻结保守规则）**
8. `gdhs_chg_q`：最近季股东户数增减比例（户数降=筹码集中，预期负号）
9. `gdhs_chg_2q`：两季累计增减比例
10. `gdhs_level`：log(股东户数/总股本)（散户密度水平，预期负号）

- 户数可用日规则说明（跑前冻结理由）：EM `更新日期` 列=行刷新时间戳非首发披露日（实证：2023-06-30 计数行更新日期 2024-03-08，用它=摧毁时效性；定期报告 1 个月披露期→+45 自然日保守截止），残余提前披露风险如实披露为偏保守（信号衰减方向）。
- 全部因子 h10 主口径 + h20 报告列（P-1a/P-1b 先例：h20 越线只留档带 snooping 折价声明，不翻案）。

## §3 门与零假设（P-A/P-B 口径原文）

- V1：|IS IC| > max(0.02, null p95)（K=50 白噪声 null，逐因子同掩码匹配）
- V2：|IC_IR| ≥ 0.30（真门）
- V3：OOS（2025-01-01+）同号且留存≥0.5
- IS=面板起点→2024-12-31；OOS=2025-01-01→cutoff。掩码分层 null（P-A：V2 才是真门）；多重性=n_factors×horizon 计数如实记。
- 账本：因子账本（IC 计数）记 results JSON audit；引擎账本 N 不动（零引擎跑）。

## §4 数据完备门（批跑前置条件）

- dzjy：覆盖交易日 ≥95%（相对 bars 日历 2013+）或覆盖缺口如实降档
- margin：SSE+SZSE 双所覆盖 ≥90%（2010-03-31 起算）；单日 0 行=诚实空日
- gdhs：有效季（行数>500）≥40
- 完备门不过=批不跑，继续回填/如实报告，**禁半数据跑批**

## §5 拉取纪律

- 限速 ≥2.5s/请求 + 指数退避 + 连续 5 失败保险丝停发；checkpoint 断点续拉（r41 长批后台化教训）；单进程串行三槽（EM datacenter 公民义务，禁并发轰源）
- 大宗 5000 行截断门：月区间 rows==5000 → 二分重拉至不触帽
- 产物：`data/ext_slots/dzjy/mrmx_YYYYMM.parquet` + `data/ext_slots/margin/sse_YYYY.parquet|szse_YYYY.parquet` + `data/ext_slots/gdhs/gdhs_YYYYQn.parquet`（gitignored，data/.gitignore 追加）+ `results/ext_slots_pull_status.json` 状态留痕

## §6 预测（跑前写死，§6 禁含结果数字）

- 户数族 gdhs_chg_q 最可能过门（A 股经典民间因子+O-2134 民间梳理语境）；预期 IS IC 负号、|IC| 0.03-0.08 带宽
- 大宗族 amt_share_20 占比类比 lhb_amt_share（P-A 强员同构）有中等机会；count_20 与 lhb_count_20 信息可能重叠（相关性须测，重叠则标注非独立）
- 两融族：拥挤类预期负号薄边际；2010-2015 早段覆盖少（融资标的少）→掩码 C 稀疏，V2 大概率不过
- 三槽合计过门预测 1-2 个（含 V2）；全灭概率 ≈35%
- 大宗折溢价 prem_mean_20：方向不确定（折价=机构出货 vs 折价吸筹两说），如实跑
- 主要风险：户数族+45 天保守滞后吃掉时效→真实 IC 被衰减稀释（这是规则选择的代价，非数据问题）

## §7 执行序

1. R45：本预注册 + 拉取器 `scripts/backfill_ext_slots.py`（checkpoint+selftest 离线）+ 后台拉取链点火（dzjy→gdhs→margin 串行）
2. 完备门过（预计 R46+）→ 批跑 P-1d IC 海选一次定稿（10 因子×双 horizon+null）
3. 幸存者→P-2 型合成批另开预注册；0 幸存→诚实收线

## s9 bm-b 裁定补遗（2026-09-24 02:4x · 跑前元数据增补 · MSG-0226 应答）

本预注册冻结于 2026-09-23 22:10，早于 O-2215 回测科学 v2 落地（~22:3x）——
按 BACKTEST_SCIENCE s8 祖父条款，**P-1d 批按冻结时的 V1/V2/V3 IC 门常数执行**
（recorded-constants 口径，与 GTJA191/WQ101 批同代判据）；不追认 v2（skill_line_v2/
DSR/PBO），原因：判据换轨=跑后换秤=数据窥探红线。批跑时（margin 门转绿后）在结果
JSON 顶层按 C2 合法键补 evidence_cutoff 元数据。本节为唯一增补，跑后禁再动。
