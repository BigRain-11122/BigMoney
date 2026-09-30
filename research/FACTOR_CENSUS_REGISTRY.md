# FACTOR_CENSUS_REGISTRY — 单源因子普查登记簿 v1.0

- 票据: T-2026-09-26-86-P1 s1（CEO 直令 O-20260926-2320 因子级融合普查）· 交付轮 R279 bm-a
- 律法: **零发明律**——登记簿外的因子面禁入 s2 组合普查；每行以源码/正典件为锚，票面 progress_r277 盘点+bm-b r279 交叉见证（union 后实证本件此前缺位、R278 死轮未及写盘）
- 消费契约（s2 组合普查）: 登记行全量 C(n,2) 两两 + 三元组合 · dual-sort 条件收益 · rank-IC · 含成本多头腿 blend 收益 · core48 复权面 + 更宽 daily-CSV 宇宙（B 层过滤律）· 判据按 prereg 冻结后跑（R99 律，judged 前先冻）

## A. 引擎因子库（28）— engine/factors.py `FACTORS`

mom_20, mom_60, mom_120, mom_12_1, rev_5, rev_10, vol_20, vol_60, amt_20, ma_bias_20, ma_bias_60, adx_14, vol_price_corr, gap_overnight, intraday_range, volume_trend, price_position, mom_accel, vol_regime, up_day_ratio, extreme_freq, drawdown_60, vol_price_diverge, return_skew, return_kurt, overnight_minus_intraday, ma_slope_20, amihud_illiq

## B. 风格动物园 zoo（scripts/p1e_factors.py，frozen r218）

| 面 | 构造器 | 注记 |
|---|---|---|
| zoo85_stv | build_zoo85_stv | 社区共识 #85 |
| zoo85_terrified | build_zoo85_terrified | #85 恐慌变体 |
| zoo92_coin_team | build_zoo92_coin_team | #92 抱团 |
| zoo93_arc 家族 | build_zoo93_arc_family | ARC/CGO+矩变体（vwap 口径冻结；vrc/src/krc 为比率幂变体·close 口径=经典 Grinblatt-Han 披露不入批 v1）；60 行有效窗·长停股缺行律 |

## C. 学术/工业 alpha 族（T-48 登记 scripts/factor_registry.py r162 + alpha158_compare.py）

| 族 | 规模锚 | 证据件 |
|---|---|---|
| GTJA191 | 191 表达式族 | factor_registry.py 枚举 |
| WQ101 | 101 表达式族 | factor_registry.py 枚举 |
| A158-truegap | 158 式真缺口面 | research/shortline/A158_TRUEGAP_IC.md |

## D. sina 资金流四档（T-72 已采面）

超大单/大单/中单/小单 净额与占比族 — spec=research/shortline/SINA_MF_PREREG.md · 采集器=scripts/update_sina_mf.py（5222 全宇宙·面板在位为 census 输入门槛）

## E. LHB/人气面

席位与榜单族 — research/shortline/LHB_SEAT_PULL.md · 人气榜 research/shortline/HEAT_ATTENTION_SPEC.md（数据面 cutoff 09-24 在位）

## F. bench 基准 rs 面（2）

factor_registry.py 内 bench 登记行（T-48 r162 同源·对照组非候选）

## G. quick-strike 先验面（v1.1 修订·2026-09-27 R286 bm-a·append-only）

| 面 | 构造 | 注记 |
|---|---|---|
| lowamp20 | 20 日 mean((high−low)/close)·低=溢价（sign prior −） | CEO 令票 spec 原文点名「formal census must cover lowamp/trend fusion families on core48 with x2 cost」；原始 GM scratch（23:05·.codely-cli/scratch/fusion_explore_p0/ gitignored）配方不可恢复=经济面重建披露：低振幅稳定族；与 A 行 intraday_range/vol_20/vol_60 同族但不同窗不同量纲（振幅均值非方差、非归一化 range）=非重复面；血统锚=票 spec 原文+本注记 |

## H. G2 矿源普查新面（2026-09-30 bm-a r493·G2_OVERLAP_CENSUS_P1·append-only）

- 血统：M1 Vibe-Trading HEAD 18027a0c（r492 装锚 ls-remote 验）×478 面公式级重叠普查（prereg=research/G2_OVERLAP_CENSUS_P1.md 冻结后跑·工件 results/g2_overlap_census_p1.json）——**431 面 DUP 撞号引用在库 C 行三族 verdict 不重烧**（WQ101 86 VERIFIED+15 书写变体 DRIFT·19 skip 面=在库 neutralized/cap 判决空间一部分如实并入；GTJA191 191/191；A158 qlib 名集 154/154 命中·BETA5/10/20/30/60 五面 Qlib 语义漂移旗=ROC 型非 REGBETA 型披露）；本节只登记 12 个 NEW-FACE（零撞号面）。

| 面 | 构造（源文件 formula/说明锚） | DATA_GATE | 注记 |
|---|---|---|---|
| academic_bab | Frazzini-Pedersen 低贝塔异象 OHLCV 简化版（等权市场收益滚动 beta 截面负排序） | 否（OHLCV 可算） | SLOT 泊位候选·机制段待 prereg |
| academic_corr_rewire | 事件窗 vs 平静基线相关行 \|Δρ\| 均值（纯滚动因果版） | 否 | kin 豁免面（token 撞 vol_price_corr 但构造异质·普查豁免表白名单） |
| academic_high52w | close/ts_max(close,252)（George-Hwang 2004） | 否 | mom 族机制近亲（名字零撞号如实） |
| academic_mkt_rf | 21 日收益截面 z 分（MKT_RF 代理） | 否 | **ETF 截面域全员同值风险注记**：core48 截面无区分度概率高，SLOT 轮如实判 |
| academic_cma | FF5 投资因子（Conservative Minus Aggressive） | **是（基本面缺位·D-41 §五 DATA_GAP）** | 数据不采集=不开烧 |
| academic_hml | FF5 价值因子（B/M） | 是 | 同上 |
| academic_rmw | FF5 盈利因子 | 是 | 同上 |
| academic_smb | FF5 规模因子 | 是 | 同上 |
| fund_asset_growth | 资产增长（fundamental 目录） | 是 | 同上 |
| fund_earnings_yield | 盈利收益率（E/P） | 是 | 同上 |
| fund_gross_profitability | 毛利润率（Novy-Marx） | 是 | 同上 |
| fund_roe | ROE | 是 | 同上 |

- 消费契约：OHLCV-ready 4 面（bab/corr_rewire/high52w/mkt_rf）=SLOT 泊位候选（逐族三验+预注册后烧·G2 spec §四.1；mkt_rf 带区分度存疑注记照登）；DATA_GATE 8 面=数据缺口显式锁定（基本面采集管线立项前禁入任何烧批——D-41 §一.2/§五 DATA_GAP 纪律）；DUP-FAMILY-DRIFT 19 面（WQ101 15 书写变体+ACADEMIC 4 名字近亲）+M3 16 面=构造验证留 SLOT 轮（名字级/书写级近亲非语义等价·不引用族 verdict 亦不判负）。
- 供料池 ready 面账：3→**7 级**（+4 OHLCV-ready；G2 spec §四.1 目标 30+ 级的 23%——M1 三主矿=在库三族第三方重实现为主价值=431 面防重烧；扩面缺口如实披露归 M4(initial-d 213)/M5(JunQHuang 120) 后续普查片）。

## 记账

- 总登记面: A28 + B(zoo85×2, zoo92, zoo93 家族) + C 三族 + D 四档 + E 两面 + F 2 —— s2 普查 N 以 prereg 冻结时的逐行可计算清单为准（本件为单源母面，prereg 引用行号枚举）
- 修订律: append-only；新增面必须先入本登记簿再入普查（零发明律）；源码变动致口径变=frozen 面禁改、新面加行注记血统
- **s2 wave-1 消费清单（2026-09-27 R286 冻结）**: 候选原子面 = A 行 28 + G 行 1（29 面）→ C(29,2)+C(29,3)=4,060 组合；F 行 2=对照组（基准序列，不入候选枚举，仅 58 对照 pair）；D/E/B 行=股票截面域不入 wave-1（core48 无此数据面）
- **s2 wave-2 枚举规则（wide universe·T-87 面板完备门后）**: B4 + D 四档净额/占比 8 + E 2 + C 三族各 top-10（按 P-1/P-2 筛查在档产物 IC IR 排序·工件锚零发明）≈44 面 → 组合数按规则推导，精确 roster+组合数于 wave-2 追加节冻结后跑（R99 每 wave 一冻）
- **s2 wave-2 冻结指针（2026-09-27 R325 bm-a·append-only）**: T-87 门开（面板 complete 2026-09-24·5,228 员·bm-b 本地）→ 精确 roster 冻结=CENSUS_FUSION_S2_PREREG.md §9.3+results/census_fusion_s2/w2_roster.json（scripts/census_w2_roster.py 确定性导出·p1c/a158 工件 sha 锚）——W2-A 32 面（B4+C-GTJA191 10+C-WQ101 10+C-A158 全 7 诚实欠额+E-LHB 1·候选 5,456+对照 64+null 400=N 5,920·seed census_fusion_s2_w2=20281500·lane=bm-b）；W2-B 9 面（D8+E-heat）门未开预declare（sina MF 2775/5222+heat 局域性·跑前须 §9.4 confirm）；A158 在档仅 7 格<top-10 规则=诚实欠额照登
- **s2 wave-2 W2-B confirm 指针（2026-09-27 R344 bm-a·append-only）**: §9.4 append-confirm 冻结=CENSUS_FUSION_S2_PREREG.md §9.4+results/census_fusion_s2/w2b_roster.json（scripts/census_w2b_roster.py 确定性导出·w2_roster/sina_construct_p1 工件 sha 锚）——sina MF 门开（complete 5,228/5,228 @2026-09-24）→ **W2-B=D8-only 8 面诚实降案**（E-heat census-infeasible OUT：popularity 3 快照+rank_history 试点 97/5,228·HEAT spec §3.2 P-C 不入 IS 律·驱动=结构性数据可得性零格已烧非结果驱动·全宇宙 rank_history 回填=未来修正案选项→潜在 W2-C）；D8 符号先验=sina_construct_p1 h10 IS IC 工件派生（r0/r1 +·r2/r3 −·全族 standalone REJECT 随批披露）；候选 5,204（pairs 284+triples 4,920·含 ≥1 D 面）+对照 16+null 400（强制 ≥1 D 同覆盖窗基线）=**N 5,620**（CENSUS_FUS_S2_W2B·seed census_fusion_s2_w2b=20282500 band 零命中·R250 同 commit 登记）；lane=bm-b（D 面输入=bm-a 小工件导出+TRANSFER·sha in-runner fail-closed）；跑前顺序律=§9.4 冻结→runner build→跑（R99）

### H-P2. G2 矿源普查新面·P2 批（2026-10-01 bm-a r499·G2_OVERLAP_CENSUS_P2·append-only）

- 血统：M4 initial-d/ml-quant-trading HEAD a770825f（r494 装锚）×M5 JunQHuang HEAD b3e37129 ×237 面公式级重叠普查（prereg=research/G2_OVERLAP_CENSUS_P2.md 冻结后跑·工件 results/g2_overlap_census_p2.json）——**4 面 DUP-FORMULA-VERIFIED 撞号引用在库 verdict 不重烧**（add_013/old_041→WQ#41·old_042→WQ#42·stock_009→GTJA#46）；38 面 DRIFT（M4-WQ101 8 简化重实现+MARKET 6 kin 名字级+M5 24 同号异构 demo）与 69 面 UNVERIFIABLE（散文/条件式/省略式 docstring=公式源缺·不入池不烧）留 SLOT/未来代码面腿；本节只登记 126 个 NEW-FACE（零撞号面）。

| 面 | 构造（M4 源 docstring 公式锚） | DATA_GATE | 注记 |
|---|---|---|---|
| add_001 | rank(Δclose, 5) * rank(Δvolume, 5) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| add_002 | -(close - ts_mean(close, 10)) / ts_mean(close, 10) * rank(volume) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_003 | sign(Δclose, 1) * (1 + \|Δclose/close\|) * Δvolume/volume | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| add_004 | ts_rank(volume, 20) * ts_rank(-close_loc, 10) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_005 | ts_sum(close > delay(close, 1), 12) - ts_sum(close < delay(close, 1), 12) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_006 | ewma(close/delay(close,1)-1, 1/12) - close/delay(close,12)-1 | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_007 | corr(rank(close), rank(volume), 5) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_008 | ts_std(close/delay(close,1)-1, 20) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_009 | (high + low) / 2 - delay((high + low) / 2, 3) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_011 | ts_corr(vwap, volume, 10) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_012 | rank(open - mean(open,10)) * rank(abs(close-vwap)) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_015 | open / delay(close, 1) - 1 | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_016 | ts_max(vwap, 10) - vwap | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_017 | vwap - ts_min(vwap, 10) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_018 | mean(abs(close - open) / (high - low + 1e-9), 5) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_021 | rank(corr(close, volume, 20)) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_023 | close - ts_mean(close, 5) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_024 | close - ts_mean(close, 20) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_025 | mean(close, 5) / mean(close, 20) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_026 | ts_std(volume, 5) / ts_mean(volume, 5) (volume CV) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_027 | rank(-delta(close, 3) * Δvolume) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| add_028 | (close - open) / (high - low + 1e-9) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_029 | ts_mean((close - open) / (high - low + eps), 10) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| add_030 | rank(sum(ret, 5)) * rank(sum(ret, 20)) | 否（OHLCV+amount/vwap 可算） | add 族·SLOT 泊位候选 |
| best_004 | Delta(close_loc, 3) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_005 | Delta(close_loc, 5) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_008 | ts_mean(vwap / close, 3) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_009 | EWMA(vwap, 5) / EWMA(close, 5) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_010 | (vwap / close - 1) * volume | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_011 | cs_rank(open / delay(close, 1) - 1) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_012 | ts_mean(open / delay(close, 1) - 1, 5) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_013 | EWMA(open / delay(close, 1) - 1, alpha=1/5) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_015 | cs_rank((high - low) / close) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_016 | (high - low) / close / (1 + sqrt(volume)) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_018 | Delta(EWMA(close, alpha=1/10), 1) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_019 | Delta(EWMA(close, alpha=1/20), 1) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| best_021 | max((vwap-close)*vol, 3) + min((vwap-close)*vol, 3) * delta(volume, 3) | 否（OHLCV+amount/vwap 可算） | best 族·SLOT 泊位候选 |
| better_001 | (open/delay(close,1) - 1) * log2(volume + 1) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_002 | (open/delay(close,1) - 1) * volume / mean(volume, 5) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_003 | (open/delay(close,1)-1) * (vwap-close) * (high-low) / close | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_005 | -(vwap_loc - delay(vwap_loc, 5)) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_006 | mean((2*vwap - low - high) / (high - low), 5) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_007 | (high-low)/close * (volume - delay(volume, 1)) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_008 | (high-low)/close / log2(volume + 1) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_013 | (vwap/close - 1) * log2(amount + 1) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_014 | mean((vwap/close - 1) * log2(amount + 1), 4) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_015 | ewma((vwap - mean(vwap,10))/mean(vwap,10) delta 5, 1/20) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_016 | ewma((vwap - mean(vwap,6))/mean(vwap,6) delta 3, 1/12) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_017 | ewma((amount - mean(amount,6))/mean(amount,6) delta 3, 1/12) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_018 | ewma((amount - mean(amount,10))/mean(amount,10) delta 5, 1/20) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_021 | vwap / delay(close, 1) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_022 | (vwap/delay(close,1) - 1) * log2(amount + 1) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_023 | mean((vwap/delay(close,1) - 1) * log2(amount + 1), 4) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_024 | (max(vwap-close, 5) + min(vwap-close, 5)) * Δvolume_5 | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| better_025 | (max(vwap-close, 5) + min(vwap-close, 5)) * (volume - mean(volume, 5)) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| better_026 | ewma((high-low)/close, 2/5) / ewma(ewma((high-low)/close, 2/5), 2/20) | 否（OHLCV+amount/vwap 可算） | better 族·SLOT 泊位候选 |
| change_004 | (high - low) / ts_mean(high - low, 20) | 否（OHLCV+amount/vwap 可算） | change 族·SLOT 泊位候选 |
| change_005 | ts_sum(sign(Δclose), 5) | 否（OHLCV+amount/vwap 可算） | change 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| extra_001 | Delta(close_loc, 1) | 否（OHLCV+amount/vwap 可算） | extra 族·SLOT 泊位候选 |
| extra_002 | rank(max(vwap-close, 3)) + rank(min(vwap-close, 3)) * rank(Δvolume, 3) | 否（OHLCV+amount/vwap 可算） | extra 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| extra_003 | open / delay(close, 1) - 1 | 否（OHLCV+amount/vwap 可算） | extra 族·SLOT 泊位候选 |
| extra_005 | amount / ts_mean(amount, 20) - 1 | 否（OHLCV+amount/vwap 可算） | extra 族·SLOT 泊位候选 |
| extra_008 | sum(max(high-delay(close,1), 0), 5) / sum(max(delay(close,1)-low, 0), 10) * 100 | 否（OHLCV+amount/vwap 可算） | extra 族·SLOT 泊位候选 |
| extra_012 | high / open | 否（OHLCV+amount/vwap 可算） | extra 族·SLOT 泊位候选 |
| extra_013 | vwap / close | 否（OHLCV+amount/vwap 可算） | extra 族·SLOT 泊位候选 |
| old_027 | rank(volume) * rank(vwap - close) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_028 | corr(rank(open), rank(volume), 10) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_029 | ts_min(rank(corr(close, volume, 5)), 12) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_030 | sign(Δclose, 5) * (1 - rank(Δvolume, 5)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| old_031 | rank(Δclose, 10) * rank(Δvolume/vol, 10) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| old_032 | ts_mean(close, 7) - close + corr(vwap, delay(close,5), 230) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_033 | rank(-1 + open/close) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_034 | rank(1 - rank(std(ret, 2)/std(ret, 5)) + 1 - rank(Δclose, 1)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| old_035 | ts_rank(volume, 32) * (1 - ts_rank(close + high - low, 16)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_036 | rank(corr(delay(open-close,1), close, 20)) + rank(open-close) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_037 | -rank(open - delay(high, 1)) * rank(open - delay(close, 1)) * rank(open - delay(low, 1)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_038 | -(rank(open) ^ rank(close/vwap)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_039 | -rank(Δclose, 7) * (1 - rank(ewma(volume*ret/close, 1/20))) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| old_040 | -rank(std(high, 10)) * corr(high, volume, 10) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_043 | ts_rank(volume / mean(volume, 20), 20) * ts_rank(-Δclose, 7) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| old_044 | -corr(high, rank(volume), 5) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_045 | -rank(sum(delay(close,5), 20)/20) * corr(close, volume, 2) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_046 | (mean(close,3)+mean(close,6)+mean(close,12)+mean(close,24))/(4*close) - 1 | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_047 | (ts_max(high, 6) - close) / (ts_max(high, 6) - ts_min(low, 6) + eps) * 100 | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_048 | (-Δclose, 1) * volume / ewma(volume, 1/20) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| old_050 | -ts_max(rank(corr(rank(volume), rank(vwap), 5)), 5) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_052 | (sum(max(0, high-delay(close,1)), 26) / sum(max(0, delay(close,1)-low), 26) - 1) * 100 | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_053 | ts_sum(close > delay(close, 1), 12) / 12 * 100 | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_054 | (-1 * rank(std(\|close-open\|,10) + \|close-open\|) + rank(corr(close,open,10))) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_055 | corr(rank(close-ts_min(low,12))/(ts_max(high,12)-ts_min(low,12)), rank(volume), 6) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_057 | close / ewma(close, 1/30) - 1 | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_058 | -volume * (close - delay(close,1)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_060 | 2 * (rank(open - min(open, 12)) - rank((sum(ret, 60)/60 + 1)^2)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_061 | rank(vwap - ts_min(vwap, 16)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_062 | rank(corr(vwap, sum(mean(volume,20), 23), 5)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_063 | max(rank(corr(rank(vwap), rank(volume), 4)), 8) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_064 | rank(corr(sum(open*0.178 + low*0.822, 15), sum(mean(volume,60), 9), 11)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_065 | rank(corr(((open*0.147) + (vwap*0.853)), sum(mean(vol,6), 2), 6)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_066 | rank(delta(vwap, 4)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_067 | (high - ts_max(high, 6)) / (ts_max(high, 6) + eps) * rank(corr(vwap, mean(vol,20), 4)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_068 | (rank(corr(high, mean(volume,15), 9)) * rank(corr(close, volume, 4))) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_069 | sum(max(rank(corr(ts_rank(close,5), ts_rank(volume,5), 4)), 0), 3) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_070 | rank(delta(vwap, 2)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_071 | ts_rank(corr(ts_rank(close, 3), ts_rank(volume, 3), 18), 4) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_072 | rank(ewma(corr(mean(volume,40), low, 4), 1/20)) + rank(ewma(corr(rank(vwap), rank(volume), 4), 1/7)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_073 | -ts_rank(ewma(Δ(vwap, 5), 1/2), 3) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| old_074 | rank(corr(close, sum(mean(volume,30), 37), 15)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选 |
| old_076 | rank(Δ(corr(vwap, volume, 4), 3)) | 否（OHLCV+amount/vwap 可算） | old 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| original_021 | close[t] / close[t-10] - 1 | 否（OHLCV+amount/vwap 可算） | original 族·SLOT 泊位候选 |
| original_022 | close[t] / close[t-5] - 1 | 否（OHLCV+amount/vwap 可算） | original 族·SLOT 泊位候选 |
| original_023 | close[t] / close[t-3] - 1 | 否（OHLCV+amount/vwap 可算） | original 族·SLOT 泊位候选 |
| original_024 | close[t] / close[t-1] - 1 | 否（OHLCV+amount/vwap 可算） | original 族·SLOT 泊位候选 |
| stock_001 | Corr(Δlog(volume), (close-open)/open, 4) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| stock_002 | Corr(Δlog(volume), (close-open)/open, 6) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| stock_003 | rank(close - ts_max(vwap, 15)) ^ delta(close, 5) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_005 | (close - delay(close, 6)) / delay(close, 6) * (volume + 1) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_006 | (close - mean(close, 12)) / mean(close, 12) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_007 | (delay(ts_min(low,5), 5) - ts_min(low,5)) * rank((sum(ret,60)-sum(ret,20))/40) * rank(volume) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_010 | std(log(amount+1), 6) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_013 | Δ(vwap - close) / Δ(vwap + close) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选·Δ 符号书写变体披露 |
| stock_014 | (close / delay(close, 12) - 1) * volume | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_017 | -ret * mean(volume, 20) * vwap * (high - close) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_019 | (low - close) * open^5 / ((close - high) * close^5) | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_020 | (close - delay(close,1)) / delay(close,1) * volume | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_021 | ((high-low) - ewma(high-low, 2/11)) / ewma(high-low, 2/11) * 100 | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |
| stock_022 | corr(mean(volume,20), low, 5) + (high+low)/2 - close | 否（OHLCV+amount/vwap 可算） | stock 族·SLOT 泊位候选 |

- 消费契约：126 面全数=泊位候选非入册资格——逐族 SLOT 三验+预注册后烧（G2 spec §四.1·O-1901 ① 禁一次性全量判决烧·优先序按消费面紧迫度）；69 UNVERIFIABLE 面=M4 代码面提取腿未来批选项（本批公式源缺如实不入池）；38 DRIFT 面=名字级/同号级近亲非语义等价（不引用族 verdict 亦不判负，构造验证留 SLOT 轮）。
- 供料池 ready 面账：7→**133 级**（+126 P2 OHLCV+amount/vwap 可算面；G2 spec §四.1 目标 30+ 超标——富集面全数未过 SLOT 三验如实标注）。

### G 行 lowamp 概念族消费注记（2026-10-01 bm-b r490·append-only·T-86 普查 lowamp 列 verbatim 消费回执）

- LOWAMP-P1 专用判决批（T-132·verdict=judged-negative·fast-track O-2026-09-30-2230）已消费低振幅族 judged faces：W∈[77,104] 滚动收益 std 振幅排序变体（judged cells W∈{89,104}+sensitivity W∈[77,104]·close-to-close std 构造；与 G 行 lowamp20=mean((high−low)/close) 20 日窗为**不同构造同族概念**——消费声明按族概念立、构造差异如实注记）——**禁重跑**（TRIAL_GRAMMAR_LEDGER LOWAMP-P1 行同立）；⚠ verdict 完整性 UNDER REVIEW（bm-b r490 审计·修复单 T-2026-10-01-135-P0·裁定前禁据本 verdict 作族间 meta 结论）。
