
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
