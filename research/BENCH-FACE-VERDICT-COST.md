# 面判词值不值得再烧（纯读出）

- 17 张面判词里 17 张不值得再烧（其中 1 张根本不是在说这张票）、0 张值得、0 张本面定不了价
- 取证截止 2026-11-26；本面只读已发布字段，不复算任何臂

| 卡 | 面判词 | 臂 GO | 最弱未过臂 | 分辨率 | 要多少年 | 值得再烧 |
|---|---|---|---|---|---|---|
| census_bond_futures | CENSUS_LEANS_POSITIVE | 0/5 | ma_cross|{'fast': 50, 'slow': 200}|long 4.02% / 线 4.14pp | MEASURED_AND_EMPTY | - | 不值得 |
| census_commodity | CENSUS_LEANS_POSITIVE | 2/14 | tsmom|{'lookback': 250, 'skip': 21}|long 4.54% / 线 2.78pp | MEASURED_AND_EMPTY | - | 不值得 |
| census_index_futures | CENSUS_UNPOWERED | 0/20 | ma_cross|{'fast': 50, 'slow': 200}|ls 6.78% / 线 7.61pp | SHORT_OF_RESOLUTION | 22.8 | 不值得 |
| pair_all10_60d | NO_EDGE | 0/1 | - 1.41% / 线 6.29pp | SHORT_OF_RESOLUTION | 83 | 不值得 |
| pair_bond_curve_60d | NO_EDGE | 0/1 | - -1.91% / 线 3.67pp | SHORT_OF_RESOLUTION | 14.8 | 不值得 |
| pair_commodity_60d | NO_EDGE | 0/1 | - 1.3% / 线 5.22pp | SHORT_OF_RESOLUTION | 57.2 | 不值得 |
| pair_index_60d | NO_EDGE | 0/1 | - 2.97% / 线 9.19pp | SHORT_OF_RESOLUTION | 92.5 | 不值得 |
| reversal_commodity_5d | NO_EDGE | 0/1 | - -4.2% / 线 3.91pp | SHORT_OF_RESOLUTION | 32.1 | 不值得 |
| reversal_index_5d | NO_EDGE | 0/1 | - 2.28% / 线 5.78pp | SHORT_OF_RESOLUTION | 36.6 | 不值得 |
| robust_donchian_index | UNSTABLE_ACROSS_PARAMS | 0/3 | 55_20 -0.11% / 线 7.58pp | SHORT_OF_RESOLUTION | 22.7 | 不值得 |
| robust_ma_index | UNSTABLE_ACROSS_PARAMS | 0/3 | 50_200 6.78% / 线 7.61pp | SHORT_OF_RESOLUTION | 22.8 | 不值得 |
| robust_tsmom_commodity | UNSTABLE_ACROSS_PARAMS | 2/3 | 60d 1.52% / 线 3.86pp | MEASURED_AND_EMPTY | - | 不值得 |
| trend_single_AU_long | NO_EDGE | 0/1 | - 7.95% / 线 3.85pp | MEASURED_AND_EMPTY | - | 不值得 |
| trend_single_IC_long | NO_EDGE | 0/1 | - 2.99% / 线 5.01pp | SHORT_OF_RESOLUTION | 9.9 | 不值得 |
| trend_single_RB_long | NO_EDGE | 0/1 | - 0.5% / 线 3.3pp | MEASURED_AND_EMPTY | - | 不值得 |
| trend_single_SC_long | NO_EDGE | 0/1 | - -1.03% / 线 4.82pp | MEASURED_AND_EMPTY | - | 不值得 |
| trend_single_T_long | NO_EDGE | 0/1 | - 3.09% / 线 2.79pp | MEASURED_AND_EMPTY | - | 不值得 |

- **census_bond_futures**：面判 **CENSUS_LEANS_POSITIVE**，而它自己的臂 0/5 GO、0 臂过 H1 —— 面的话比臂的读数乐观，这一关是真障碍
- **census_commodity**：面判 **CENSUS_LEANS_POSITIVE** 说的是空间，不是这张票；它自己的臂里已有 2/14 臂 GO、0 臂过 H1 线，矛盾面判 **AGREES** —— 为这句话再烧一次只会得到第三次复述，缺的是一张票，不是证据
- **census_index_futures**：面判 **CENSUS_UNPOWERED**，它自己的 20 臂里 0 臂 GO —— 面与臂一致，这个空间是空的；不是判词和证据打架，是没有东西可烧
- **pair_all10_60d**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；按 1/sqrt(T) 要 83 年数据才可能看见它——这是信息，不是复验计划
- **pair_bond_curve_60d**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；按 1/sqrt(T) 要 14.8 年数据才可能看见它——这是信息，不是复验计划
- **pair_commodity_60d**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；按 1/sqrt(T) 要 57.2 年数据才可能看见它——这是信息，不是复验计划
- **pair_index_60d**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；按 1/sqrt(T) 要 92.5 年数据才可能看见它——这是信息，不是复验计划
- **reversal_commodity_5d**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；按 1/sqrt(T) 要 32.1 年数据才可能看见它——这是信息，不是复验计划
- **reversal_index_5d**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；按 1/sqrt(T) 要 36.6 年数据才可能看见它——这是信息，不是复验计划
- **robust_donchian_index**：面判 **UNSTABLE_ACROSS_PARAMS**，最弱的未过臂 55_20 年化 -0.11%、分辨率线 7.58pp 粗于目标 5.0pp —— 按 1/sqrt(T) 要把它拉进目标分辨率需约 22.7 年数据；超过二十年不是计划，是愿望
- **robust_ma_index**：面判 **UNSTABLE_ACROSS_PARAMS**，最弱的未过臂 50_200 年化 6.78%、分辨率线 7.61pp 粗于目标 5.0pp —— 按 1/sqrt(T) 要把它拉进目标分辨率需约 22.8 年数据；超过二十年不是计划，是愿望
- **robust_tsmom_commodity**：面判 **UNSTABLE_ACROSS_PARAMS**，最弱的未过臂 60d 年化 1.52%、它自己的分辨率线 3.86pp 已细于目标 5pp —— 分辨率已经够，读出来就是没有；再烧一遍同样的配方只会得到第二个负数
- **trend_single_AU_long**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；分辨率已经够，读出来就是没有——这是信息，不是复验计划
- **trend_single_IC_long**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；按 1/sqrt(T) 要 9.9 年数据才可能看见它——这是信息，不是复验计划
- **trend_single_RB_long**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；分辨率已经够，读出来就是没有——这是信息，不是复验计划
- **trend_single_SC_long**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；分辨率已经够，读出来就是没有——这是信息，不是复验计划
- **trend_single_T_long**：面判 **NO_EDGE**：这条配方已被答案簿判为已烧完（EXHAUSTED），再跑同一套参数只会得到第二个负数；分辨率已经够，读出来就是没有——这是信息，不是复验计划

**本面不主张**：
- 不复算任何臂，不改任何判词；读数全部取自面自己已发布的字段
- years_to_resolve 是 1/sqrt(T) 的算术外推，不是承诺：数据质量不变、edge 不变的前提下才成立
- 「不值得再烧」只针对同一个配方；换参数区间=新问题，须另行预注册
- 空间词被判「被自家臂支持」不等于这张票可下——资本线、成本、容量各自还要过
- 二十年计划窗是本司设定的门槛（MAX_WAIT_YEARS），不是统计量；改窗会改变判词
