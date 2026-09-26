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

## 记账

- 总登记面: A28 + B(zoo85×2, zoo92, zoo93 家族) + C 三族 + D 四档 + E 两面 + F 2 —— s2 普查 N 以 prereg 冻结时的逐行可计算清单为准（本件为单源母面，prereg 引用行号枚举）
- 修订律: append-only；新增面必须先入本登记簿再入普查（零发明律）；源码变动致口径变=frozen 面禁改、新面加行注记血统
