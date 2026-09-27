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

## 记账

- 总登记面: A28 + B(zoo85×2, zoo92, zoo93 家族) + C 三族 + D 四档 + E 两面 + F 2 —— s2 普查 N 以 prereg 冻结时的逐行可计算清单为准（本件为单源母面，prereg 引用行号枚举）
- 修订律: append-only；新增面必须先入本登记簿再入普查（零发明律）；源码变动致口径变=frozen 面禁改、新面加行注记血统
- **s2 wave-1 消费清单（2026-09-27 R286 冻结）**: 候选原子面 = A 行 28 + G 行 1（29 面）→ C(29,2)+C(29,3)=4,060 组合；F 行 2=对照组（基准序列，不入候选枚举，仅 58 对照 pair）；D/E/B 行=股票截面域不入 wave-1（core48 无此数据面）
- **s2 wave-2 枚举规则（wide universe·T-87 面板完备门后）**: B4 + D 四档净额/占比 8 + E 2 + C 三族各 top-10（按 P-1/P-2 筛查在档产物 IC IR 排序·工件锚零发明）≈44 面 → 组合数按规则推导，精确 roster+组合数于 wave-2 追加节冻结后跑（R99 每 wave 一冻）
- **s2 wave-2 冻结指针（2026-09-27 R325 bm-a·append-only）**: T-87 门开（面板 complete 2026-09-24·5,228 员·bm-b 本地）→ 精确 roster 冻结=CENSUS_FUSION_S2_PREREG.md §9.3+results/census_fusion_s2/w2_roster.json（scripts/census_w2_roster.py 确定性导出·p1c/a158 工件 sha 锚）——W2-A 32 面（B4+C-GTJA191 10+C-WQ101 10+C-A158 全 7 诚实欠额+E-LHB 1·候选 5,456+对照 64+null 400=N 5,920·seed census_fusion_s2_w2=20281500·lane=bm-b）；W2-B 9 面（D8+E-heat）门未开预declare（sina MF 2775/5222+heat 局域性·跑前须 §9.4 confirm）；A158 在档仅 7 格<top-10 规则=诚实欠额照登
- **s2 wave-2 W2-B confirm 指针（2026-09-27 R344 bm-a·append-only）**: §9.4 append-confirm 冻结=CENSUS_FUSION_S2_PREREG.md §9.4+results/census_fusion_s2/w2b_roster.json（scripts/census_w2b_roster.py 确定性导出·w2_roster/sina_construct_p1 工件 sha 锚）——sina MF 门开（complete 5,228/5,228 @2026-09-24）→ **W2-B=D8-only 8 面诚实降案**（E-heat census-infeasible OUT：popularity 3 快照+rank_history 试点 97/5,228·HEAT spec §3.2 P-C 不入 IS 律·驱动=结构性数据可得性零格已烧非结果驱动·全宇宙 rank_history 回填=未来修正案选项→潜在 W2-C）；D8 符号先验=sina_construct_p1 h10 IS IC 工件派生（r0/r1 +·r2/r3 −·全族 standalone REJECT 随批披露）；候选 5,204（pairs 284+triples 4,920·含 ≥1 D 面）+对照 16+null 400（强制 ≥1 D 同覆盖窗基线）=**N 5,620**（CENSUS_FUS_S2_W2B·seed census_fusion_s2_w2b=20282500 band 零命中·R250 同 commit 登记）；lane=bm-b（D 面输入=bm-a 小工件导出+TRANSFER·sha in-runner fail-closed）；跑前顺序律=§9.4 冻结→runner build→跑（R99）
