# Survivor-King Contest YTD Table (T-148 interim assembly)
Window 2026-01-05 -> 2026-09-30 | baselines: 510300 -8.51% / 48EW -6.79% | admitted 219 = measured 209 (ranked 185, listed 24) + pending-burn 10
Ranking: composite = mean(rank on YTD return + rank on max drawdown + rank on Sharpe), data decides; tie-break id asc. Caliber: uniform today-engine, cost x1; live members = T-146 spliced legs.

## Ranked table (185)
| rank | composite | id | face | src | seg | ytd% | maxDD% | sharpe | beat300pp | beatEWpp | trades |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 15.00 | MT-W1-W1-08001 | mean_reversion.rsi_revert(n=15,overbought=80,oversold=23;R=bear,S=delever,T=weekly,X=t10) | MT | bt | +3.57 | -0.65 | 2.931 | +12.07 | +10.36 | 448 |
| 2 | 16.67 | MT-W1-W1-27003 | seasonal.trend_by_season(ma_n=226,month=4;R=bear,S=delever,T=daily,X=t10) | MT | bt | +1.85 | -0.24 | 1.641 | +10.36 | +8.64 | 75 |
| 3 | 16.67 | MT-W1-W1-60010 | patterns.needle_probe(drop_th=-0.041963,shadow_pct=0.026839;R=bear,S=delever,T=weekly,X=t10) | MT | bt | +1.43 | -0.13 | 2.414 | +9.94 | +8.22 | 30 |
| 4 | 18.67 | MT-W1-W1-65003 | patterns.vol_drought_reversal(drop_th=-0.077392,vol_floor=0.845383;R=bear,S=delever,T=weekly,X=t5) | MT | bt | +3.36 | -0.75 | 1.884 | +11.87 | +10.15 | 93 |
| 5 | 19.67 | MT-W1-W1-38012 | ta.engulf_reversal(drop_th=-0.027727;R=bear,S=delever,T=weekly,X=t5) | MT | bt | +1.61 | -0.38 | 1.894 | +10.12 | +8.40 | 275 |
| 6 | 22.00 | MT-W1-W1-58009 | patterns.morning_star(big_red=-0.024064,small_body=0.010238;R=bear,S=full,T=weekly,X=t7) | MT | bt | +3.14 | -0.83 | 2.006 | +11.64 | +9.93 | 169 |
| 7 | 23.00 | MT-W1-W1-38000 | ta.engulf_reversal(drop_th=-0.04771;R=bear,S=delever,T=daily,X=t7) | MT | bt | +1.63 | -0.38 | 1.424 | +10.13 | +8.42 | 181 |
| 8 | 24.00 | MT-W1-W1-08006 | mean_reversion.rsi_revert(n=16,overbought=62,oversold=17;R=bear,S=delever,T=weekly,X=t7) | MT | bt | +3.30 | -0.92 | 2.050 | +11.80 | +10.09 | 438 |
| 9 | 24.33 | MT-W1-W1-15006 | volatility.low_vol_long(n=92,top_k=4;R=bear,S=full,T=weekly,X=t10) | MT | bt | +0.99 | -0.31 | 1.661 | +9.49 | +7.78 | 340 |
| 10 | 24.67 | MT-W1-W1-72006 | folk.rsi_low_flat(low_th=26,n=23;R=bear,S=full,T=weekly,X=t7) | MT | bt | +5.41 | -1.19 | 1.863 | +13.91 | +12.20 | 294 |
| 11 | 25.00 | MT-W1-W1-65007 | patterns.vol_drought_reversal(drop_th=-0.090241,vol_floor=1.005492;R=bear,S=delever,T=weekly,X=t7) | MT | bt | +2.74 | -0.82 | 1.631 | +11.25 | +9.53 | 91 |
| 12 | 26.67 | MT-W1-W1-62009 | patterns.piercing_line(big_red=-0.024212;R=bear,S=delever,T=weekly,X=t7) | MT | bt | +1.57 | -0.63 | 1.497 | +10.07 | +8.36 | 85 |
| 13 | 28.00 | MT-W1-W1-37013 | ta.cci_revert(cci_n=23,entry_th=-83.336091,exit_th=113.581736,trend_ma=48;R=bull,S=full,T=daily,X=own) | MT | bt | +1.89 | -0.70 | 1.323 | +10.39 | +8.68 | 87 |
| 14 | 29.00 | MT-W1-W1-37002 | ta.cci_revert(cci_n=22,entry_th=-157.077704,exit_th=185.866796,trend_ma=73;R=bear,S=delever,T=weekly,X=t10) | MT | bt | +2.31 | -0.81 | 1.497 | +10.81 | +9.10 | 269 |
| 15 | 29.67 | MT-W1-W1-03006 | trend.supertrend(mult=5.184024,n=17;R=bear,S=delever,T=weekly,X=own) | MT | bt | +1.45 | -0.62 | 1.224 | +9.96 | +8.24 | 401 |
| 16 | 29.67 | MT-W1-W1-16005 | volatility.vol_breakout(n=34;R=bear,S=delever,T=weekly,X=t7) | MT | bt | +2.62 | -0.96 | 1.842 | +11.12 | +9.41 | 187 |
| 17 | 29.67 | MT-W1-W1-67005 | folk.ants_climb(max_day=0.019238;R=bear,S=delever,T=weekly,X=t10) | MT | bt | +0.94 | -0.50 | 1.508 | +9.45 | +7.73 | 149 |
| 18 | 30.33 | MT-W1-W1-28009 | seasonal.weekday_effect(weekday=2;R=none,S=delever,T=weekly,X=t5) | MT | bt | +1.08 | -0.38 | 1.200 | +9.59 | +7.87 | 31 |
| 19 | 32.67 | LIVE-VOLATILITY-CE-01 | VOLATILITY-CE-01 | LIVE | bt+paper | +2.61 | -0.94 | 1.401 | +11.11 | +9.40 | - |
| 20 | 33.00 | MT-W1-W1-61011 | patterns.obv_divergence(look=33;R=bear,S=full,T=weekly,X=t5) | MT | bt | +4.73 | -1.46 | 1.550 | +13.23 | +11.52 | 307 |
| 21 | 35.67 | MT-W1-W1-25006 | seasonal.month_end_effect(window=4;R=bear,S=delever,T=weekly,X=t20) | MT | bt | +0.15 | 0.00 | 1.619 | +8.65 | +6.94 | 178 |
| 22 | 35.67 | MT-W1-W1-35003 | macro.volatility_regime_filter(n=101;R=bear,S=delever,T=weekly,X=t10) | MT | bt | +1.01 | -0.58 | 1.080 | +9.51 | +7.80 | 281 |
| 23 | 36.00 | MT-W1-W1-37005 | ta.cci_revert(cci_n=21,entry_th=-105.887932,exit_th=156.002372,trend_ma=54;R=bear,S=delever,T=daily,X=t5) | MT | bt | +1.18 | -0.63 | 1.042 | +9.69 | +7.97 | 614 |
| 24 | 36.67 | MT-W1-W1-39009 | ta.hammer_reversal(body_max=0.418943,drop_th=-0.046202,shadow_mult=1.063254;R=bear,S=delever,T=weekly,X=own) | MT | bt | +1.84 | -0.81 | 1.079 | +10.35 | +8.63 | 249 |
| 25 | 38.00 | MT-W1-W1-55009 | patterns.island_reversal(gap=0.005172;R=bear,S=delever,T=daily,X=t5) | MT | bt | +1.50 | -0.87 | 1.267 | +10.01 | +8.29 | 179 |
| 26 | 40.00 | LIVE-AGGR-CONC-TOP2 | AGGR-CONC-TOP2 | LIVE | bt+paper | +3.99 | -1.66 | 1.433 | +12.50 | +10.78 | - |
| 27 | 40.33 | MT-W1-W1-65006 | patterns.vol_drought_reversal(drop_th=-0.054486,vol_floor=0.534276;R=bear,S=delever,T=daily,X=t10) | MT | bt | +0.86 | -0.39 | 0.885 | +9.36 | +7.65 | 35 |
| 28 | 40.67 | MT-W1-W1-65009 | patterns.vol_drought_reversal(drop_th=-0.060433,vol_floor=0.813969;R=bear,S=delever,T=daily,X=t7) | MT | bt | +2.44 | -1.28 | 1.135 | +10.94 | +9.23 | 319 |
| 29 | 41.33 | MT-W1-W1-38008 | ta.engulf_reversal(drop_th=-0.062411;R=bear,S=delever,T=daily,X=t20) | MT | bt | +0.74 | -0.46 | 0.897 | +9.25 | +7.53 | 91 |
| 30 | 43.00 | MT-W1-W1-22000 | sentiment.price_volume_trend(n=18;R=bull,S=full,T=weekly,X=t7) | MT | bt | +9.23 | -2.90 | 1.935 | +17.74 | +16.02 | 553 |
| 31 | 44.33 | MT-W1-W1-33010 | macro.csi300_trend_filter(ma_n=211;R=bear,S=full,T=daily,X=own) | MT | bt | +1.86 | -1.12 | 0.964 | +10.37 | +8.65 | 43 |
| 32 | 45.67 | MT-W1-W1-37004 | ta.cci_revert(cci_n=34,entry_th=-128.585549,exit_th=73.448912,trend_ma=82;R=bull,S=full,T=weekly,X=t5) | MT | bt | +1.23 | -0.95 | 1.072 | +9.73 | +8.02 | 56 |
| 33 | 46.33 | MT-W1-W1-61009 | patterns.obv_divergence(look=42;R=bear,S=delever,T=weekly,X=t10) | MT | bt | +1.65 | -1.17 | 0.970 | +10.15 | +8.44 | 241 |
| 34 | 46.67 | MT-W1-W1-10005 | momentum.cross_sectional_momentum(n=123,skip=38,top_k=9;R=bear,S=delever,T=weekly,X=own) | MT | bt | +3.67 | -2.00 | 1.300 | +12.18 | +10.46 | 463 |
| 35 | 46.67 | MT-W1-W1-29006 | event.breakout_confirm(n=15,vol_mult=2.91151;R=bear,S=delever,T=daily,X=t10) | MT | bt | +0.19 | -0.14 | 0.876 | +8.69 | +6.98 | 47 |
| 36 | 47.67 | MT-W1-W1-65002 | patterns.vol_drought_reversal(drop_th=-0.027565,vol_floor=0.281924;R=none,S=full,T=weekly,X=t7) | MT | bt | +1.17 | -0.77 | 0.629 | +9.68 | +7.96 | 39 |
| 37 | 48.67 | MT-W1-W1-53002 | patterns.immortal_guide(shadow_pct=0.026096;R=bear,S=delever,T=daily,X=t10) | MT | bt | +0.27 | -0.33 | 0.723 | +8.77 | +7.06 | 55 |
| 38 | 49.33 | MT-W1-W1-39001 | ta.hammer_reversal(body_max=0.307988,drop_th=-0.029463,shadow_mult=3.080602;R=bear,S=delever,T=weekly,X=t5) | MT | bt | +0.89 | -0.85 | 0.938 | +9.40 | +7.68 | 236 |
| 39 | 51.33 | MT-W1-W1-11007 | momentum.dual_momentum(n=153,top_k=3;R=bear,S=delever,T=weekly,X=t20) | MT | bt | +1.59 | -1.33 | 0.890 | +10.09 | +8.38 | 355 |
| 40 | 52.00 | MT-W1-W1-61008 | patterns.obv_divergence(look=21;R=bear,S=delever,T=weekly,X=t7) | MT | bt | +1.71 | -1.48 | 1.018 | +10.22 | +8.50 | 484 |
| 41 | 52.67 | LX-LA-EDGE-deep-x2 | LA-EDGE|deep|x2 | LA | bt-la-deep (end 09-22) | +0.51 | -0.65 | 0.622 | +9.01 | +7.30 | 67 |
| 42 | 53.00 | LIVE-DROUGHT-CE-01 | DROUGHT-CE-01 | LIVE | bt+paper | +3.99 | -2.65 | 1.196 | +12.50 | +10.78 | - |
| 43 | 53.00 | LX-LA-EDGE-deep-base | LA-EDGE|deep|base | LA | bt-la-deep (end 09-22) | +0.49 | -0.63 | 0.622 | +9.00 | +7.28 | 67 |
| 44 | 53.33 | MT-W1-W1-29002 | event.breakout_confirm(n=20,vol_mult=2.0113;R=none,S=delever,T=weekly,X=t10) | MT | bt | +3.78 | -2.41 | 1.150 | +12.29 | +10.57 | 187 |
| 45 | 53.67 | MT-W1-W1-38006 | ta.engulf_reversal(drop_th=-0.093325;R=none,S=delever,T=daily,X=t7) | MT | bt | +0.67 | -0.79 | 0.694 | +9.18 | +7.46 | 68 |
| 46 | 53.67 | MT-W1-W1-51010 | patterns.doji_at_low(drop_th=-0.056591;R=bear,S=full,T=weekly,X=t10) | MT | bt | +5.01 | -2.98 | 1.179 | +13.51 | +11.80 | 229 |
| 47 | 53.67 | MT-W1-W1-73001 | folk.second_wave(retest=0.025303;R=none,S=delever,T=weekly,X=t7) | MT | bt | +5.91 | -3.59 | 1.385 | +14.41 | +12.70 | 847 |
| 48 | 54.33 | LIVE-B_MAXDIV | B_MAXDIV | LIVE | bt-leg | +0.95 | -0.92 | 0.647 | +9.45 | +7.74 | - |
| 49 | 55.33 | MT-W1-W1-28002 | seasonal.weekday_effect(weekday=1;R=none,S=delever,T=weekly,X=own) | MT | bt | +0.21 | -0.29 | 0.411 | +8.71 | +7.00 | 60 |
| 50 | 55.33 | MT-W1-W1-51011 | patterns.doji_at_low(drop_th=-0.096857;R=bear,S=delever,T=weekly,X=t7) | MT | bt | +1.01 | -1.19 | 0.770 | +9.51 | +7.80 | 76 |
| 51 | 55.67 | MT-W1-W1-07005 | mean_reversion.rsi2(n=4;R=bear,S=full,T=weekly,X=t7) | MT | bt | +5.23 | -3.55 | 1.221 | +13.73 | +12.02 | 359 |
| 52 | 56.33 | LIVE-AGGR-REGIME | AGGR-REGIME | LIVE | bt+paper | +3.66 | -2.08 | 0.849 | +12.16 | +10.45 | - |
| 53 | 57.33 | LIVE-AGGR-OFFENSE | AGGR-OFFENSE | LIVE | bt+paper | +3.00 | -1.94 | 0.771 | +11.50 | +9.79 | - |
| 54 | 58.33 | LIVE-COMPOSITE-CE-01 | COMPOSITE-CE-01 | LIVE | bt+paper | +5.83 | -3.62 | 1.094 | +14.34 | +12.63 | - |
| 55 | 58.33 | MT-W1-W1-74001 | folk.volume_mound(mound=1.744619;R=bear,S=full,T=daily,X=t7) | MT | bt | +0.76 | -1.21 | 0.857 | +9.26 | +7.55 | 201 |
| 56 | 58.67 | MT-W1-W1-51003 | patterns.doji_at_low(drop_th=-0.090231;R=bear,S=full,T=weekly,X=own) | MT | bt | +3.35 | -2.69 | 1.054 | +11.85 | +10.14 | 73 |
| 57 | 60.00 | MT-W1-W1-36012 | ta.bb_squeeze_breakout(bb_n=38,k=3.203872,width_n=34;R=none,S=delever,T=weekly,X=t7) | MT | bt | +2.39 | -2.54 | 1.099 | +10.90 | +9.18 | 225 |
| 58 | 60.00 | MT-W1-W1-60011 | patterns.needle_probe(drop_th=-0.084555,shadow_pct=0.024365;R=bear,S=delever,T=daily,X=t20) | MT | bt | +0.27 | -0.65 | 0.447 | +8.78 | +7.06 | 34 |
| 59 | 61.00 | MT-W1-W1-09001 | mean_reversion.zscore_revert(entry=-3.487376,n=21;R=none,S=delever,T=daily,X=t20) | MT | bt | +0.46 | -0.77 | 0.419 | +8.96 | +7.25 | 87 |
| 60 | 61.67 | MT-W1-W1-09010 | mean_reversion.zscore_revert(entry=-3.057692,n=37;R=bear,S=delever,T=daily,X=own) | MT | bt | +1.09 | -1.41 | 0.604 | +9.59 | +7.88 | 240 |
| 61 | 62.00 | MT-W1-W1-09007 | mean_reversion.zscore_revert(entry=-1.057617,n=21;R=bear,S=delever,T=weekly,X=t20) | MT | bt | +1.86 | -1.98 | 0.828 | +10.36 | +8.65 | 428 |
| 62 | 63.33 | MT-W1-W1-15001 | volatility.low_vol_long(n=82,top_k=9;R=bear,S=delever,T=weekly,X=t5) | MT | bt | +0.50 | -0.92 | 0.558 | +9.00 | +7.29 | 411 |
| 63 | 63.67 | MT-W1-W1-16012 | volatility.vol_breakout(n=13;R=none,S=full,T=daily,X=t20) | MT | bt | +6.01 | -4.51 | 1.044 | +14.52 | +12.80 | 650 |
| 64 | 63.67 | MT-W1-W1-46002 | ta.strong_close(pos_th=0.596638,vol_len=33,vol_mult=2.194225;R=bear,S=full,T=daily,X=own) | MT | bt | +0.17 | -0.65 | 0.384 | +8.68 | +6.96 | 243 |
| 65 | 64.00 | MT-W1-W1-24001 | seasonal.holiday_effect(pre_days=6;R=bear,S=full,T=weekly,X=own) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 116 |
| 66 | 64.00 | MT-W1-W1-24002 | seasonal.holiday_effect(pre_days=5;R=bear,S=delever,T=weekly,X=t7) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 184 |
| 67 | 64.00 | MT-W1-W1-24004 | seasonal.holiday_effect(pre_days=4;R=bear,S=delever,T=weekly,X=t5) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 109 |
| 68 | 64.00 | MT-W1-W1-24007 | seasonal.holiday_effect(pre_days=3;R=bear,S=delever,T=daily,X=t10) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 295 |
| 69 | 64.00 | MT-W1-W1-26000 | seasonal.month_seasonality(month=9;R=bull,S=delever,T=daily,X=t7) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 46 |
| 70 | 64.00 | MT-W1-W1-26011 | seasonal.month_seasonality(month=12;R=bear,S=delever,T=weekly,X=t5) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 30 |
| 71 | 64.00 | MT-W1-W1-27002 | seasonal.trend_by_season(ma_n=261,month=11;R=bear,S=delever,T=daily,X=t10) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 87 |
| 72 | 64.00 | MT-W1-W1-27008 | seasonal.trend_by_season(ma_n=135,month=11;R=none,S=full,T=weekly,X=t7) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 109 |
| 73 | 64.00 | MT-W1-W1-33001 | macro.csi300_trend_filter(ma_n=130;R=bear,S=full,T=daily,X=own) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 81 |
| 74 | 64.00 | MT-W1-W1-38001 | ta.engulf_reversal(drop_th=-0.08516;R=bear,S=full,T=daily,X=t7) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 48 |
| 75 | 64.00 | MT-W1-W1-38010 | ta.engulf_reversal(drop_th=-0.075972;R=bear,S=full,T=daily,X=t20) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 51 |
| 76 | 64.00 | MT-W1-W1-49000 | patterns.big_yin_shakeout(big_yin=-0.040657;R=none,S=full,T=weekly,X=t5) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 24 |
| 77 | 64.00 | MT-W1-W1-49007 | patterns.big_yin_shakeout(big_yin=-0.033253;R=bear,S=full,T=weekly,X=t7) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 33 |
| 78 | 64.00 | MT-W1-W1-59008 | patterns.n_shape(leg_up=0.064198;R=bear,S=delever,T=weekly,X=t10) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 85 |
| 79 | 64.00 | MT-W1-W1-63001 | patterns.three_methods_up(big_yang=0.027228;R=bear,S=delever,T=weekly,X=t5) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 24 |
| 80 | 64.00 | MT-W1-W1-72010 | folk.rsi_low_flat(low_th=14,n=26;R=bear,S=full,T=daily,X=t20) | MT | bt | +0.00 | 0.00 | 0.000 | +8.51 | +6.79 | 34 |
| 81 | 64.67 | MT-W1-W1-36001 | ta.bb_squeeze_breakout(bb_n=15,k=2.420222,width_n=81;R=bear,S=full,T=daily,X=own) | MT | bt | +0.07 | -0.52 | 0.225 | +8.58 | +6.86 | 85 |
| 82 | 65.33 | MT-W1-W1-54004 | patterns.inside_bar_breakup(;R=bear,S=delever,T=daily,X=own) | MT | bt | +0.38 | -0.86 | 0.411 | +8.88 | +7.17 | 520 |
| 83 | 68.33 | MT-W1-W1-15003 | volatility.low_vol_long(n=57,top_k=8;R=bear,S=delever,T=weekly,X=t5) | MT | bt | +0.21 | -0.81 | 0.298 | +8.72 | +7.00 | 412 |
| 84 | 71.00 | MT-W1-W1-40003 | ta.kdj_reversal(entry_j=23,exit_j=74,kdj_n=18,trend_ma=83;R=bear,S=full,T=weekly,X=own) | MT | bt | +2.68 | -3.56 | 0.711 | +11.18 | +9.47 | 368 |
| 85 | 71.33 | MT-W1-W1-25002 | seasonal.month_end_effect(window=2;R=bear,S=delever,T=daily,X=own) | MT | bt | -0.06 | -0.30 | -0.206 | +8.45 | +6.73 | 185 |
| 86 | 71.67 | MT-W1-W1-43005 | ta.rsi_divergence(look=15,n=16;R=bear,S=delever,T=weekly,X=t10) | MT | bt | +0.91 | -1.57 | 0.499 | +9.42 | +7.70 | 405 |
| 87 | 72.00 | MT-W1-W1-33011 | macro.csi300_trend_filter(ma_n=288;R=bear,S=full,T=weekly,X=own) | MT | bt | +1.36 | -1.96 | 0.462 | +9.86 | +8.15 | 50 |
| 88 | 72.33 | MT-W1-W1-50002 | patterns.box_breakout(box_n=11,box_th=0.040927,vol_mult=0.706328;R=bull,S=delever,T=weekly,X=own) | MT | bt | +2.09 | -3.31 | 0.631 | +10.60 | +8.88 | 363 |
| 89 | 72.67 | LIVE-COMPOSITE-CE-02 | COMPOSITE-CE-02 | LIVE | bt+paper | +4.67 | -5.20 | 0.706 | +13.17 | +11.46 | - |
| 90 | 73.00 | MT-W1-W1-61001 | patterns.obv_divergence(look=47;R=bear,S=delever,T=daily,X=t20) | MT | bt | +1.13 | -2.07 | 0.596 | +9.63 | +7.92 | 330 |
| 91 | 73.33 | MT-W1-W1-52001 | patterns.duck_head(neck=15;R=bear,S=full,T=weekly,X=t20) | MT | bt | +0.34 | -1.12 | 0.243 | +8.84 | +7.13 | 246 |
| 92 | 73.67 | MT-W1-W1-18005 | volatility.vol_target(n=23,target_vol=0.288527;R=bear,S=delever,T=weekly,X=t10) | MT | bt | +0.57 | -1.44 | 0.373 | +9.08 | +7.36 | 449 |
| 93 | 76.67 | MT-W1-W1-17006 | volatility.vol_regime_switch(ma_n=305,n=39;R=bear,S=full,T=weekly,X=own) | MT | bt | +0.69 | -1.55 | 0.356 | +9.19 | +7.48 | 323 |
| 94 | 78.33 | MT-W1-W1-67002 | folk.ants_climb(max_day=0.01696;R=bear,S=delever,T=weekly,X=t5) | MT | bt | -0.17 | -0.51 | -0.311 | +8.33 | +6.62 | 131 |
| 95 | 79.33 | LIVE-ALLOC-P6 | ALLOC-P6 | LIVE | bt+paper | +3.33 | -5.63 | 0.569 | +11.83 | +10.12 | - |
| 96 | 79.67 | MT-W1-W1-62000 | patterns.piercing_line(big_red=-0.032435;R=bear,S=full,T=weekly,X=t7) | MT | bt | -0.10 | -0.74 | -0.133 | +8.40 | +6.69 | 43 |
| 97 | 82.00 | MT-W1-W1-72000 | folk.rsi_low_flat(low_th=36,n=27;R=bear,S=full,T=weekly,X=t10) | MT | bt | +1.69 | -4.08 | 0.570 | +10.20 | +8.48 | 398 |
| 98 | 84.33 | MT-W1-W1-06003 | mean_reversion.pullback_bounce(pullback_n=5,trend_n=105;R=bear,S=delever,T=daily,X=t5) | MT | bt | +0.25 | -1.45 | 0.147 | +8.76 | +7.04 | 154 |
| 99 | 86.00 | MT-W1-W1-31001 | event.gap_fill(n=8;R=bear,S=full,T=weekly,X=t7) | MT | bt | +0.83 | -2.33 | 0.334 | +9.34 | +7.62 | 186 |
| 100 | 87.33 | MT-W1-W1-55002 | patterns.island_reversal(gap=0.011996;R=bull,S=delever,T=daily,X=t20) | MT | bt | +0.16 | -1.46 | 0.105 | +8.66 | +6.95 | 25 |
| 101 | 88.33 | MT-W1-W1-13001 | momentum.relative_strength_rotation(n=22,top_k=6;R=bull,S=delever,T=daily,X=t20) | MT | bt | +2.66 | -8.58 | 0.368 | +11.16 | +9.45 | 668 |
| 102 | 88.67 | LIVE-ALLOC-P5 | ALLOC-P5 | LIVE | bt+paper | +2.51 | -9.42 | 0.392 | +11.02 | +9.30 | - |
| 103 | 88.67 | MT-W1-W1-04010 | trend.triple_ma(n1=7,n2=20,n3=91;R=bear,S=delever,T=weekly,X=t20) | MT | bt | -0.07 | -1.32 | -0.063 | +8.44 | +6.72 | 410 |
| 104 | 88.67 | MT-W1-W1-74004 | folk.volume_mound(mound=1.125972;R=bear,S=delever,T=daily,X=t20) | MT | bt | -0.02 | -1.41 | -0.004 | +8.49 | +6.77 | 557 |
| 105 | 89.00 | MT-W1-W1-72005 | folk.rsi_low_flat(low_th=17,n=14;R=none,S=delever,T=weekly,X=own) | MT | bt | +0.59 | -2.33 | 0.284 | +9.09 | +7.38 | 143 |
| 106 | 90.67 | MT-W1-W1-26007 | seasonal.month_seasonality(month=7;R=bear,S=delever,T=weekly,X=t10) | MT | bt | -0.23 | -0.95 | -0.210 | +8.27 | +6.56 | 48 |
| 107 | 90.67 | MT-W1-W1-27005 | seasonal.trend_by_season(ma_n=304,month=5;R=bull,S=delever,T=daily,X=t7) | MT | bt | +0.26 | -1.74 | 0.168 | +8.76 | +7.05 | 111 |
| 108 | 91.33 | MT-W1-W1-74010 | folk.volume_mound(mound=2.16023;R=bear,S=full,T=weekly,X=t7) | MT | bt | -0.32 | -0.79 | -0.557 | +8.19 | +6.47 | 60 |
| 109 | 93.00 | MT-W1-W1-67003 | folk.ants_climb(max_day=0.010899;R=bear,S=full,T=daily,X=t10) | MT | bt | -0.46 | -0.65 | -0.777 | +8.04 | +6.33 | 70 |
| 110 | 93.33 | MT-W1-W1-59006 | patterns.n_shape(leg_up=0.048968;R=bear,S=delever,T=weekly,X=t5) | MT | bt | -0.29 | -0.34 | -1.860 | +8.22 | +6.50 | 132 |
| 111 | 93.67 | MT-W1-W1-67012 | folk.ants_climb(max_day=0.012201;R=bear,S=full,T=daily,X=t10) | MT | bt | -0.46 | -0.65 | -0.777 | +8.04 | +6.33 | 94 |
| 112 | 94.33 | LIVE-NEEDLE-DE-01 | NEEDLE-DE-01 | LIVE | bt+paper | +0.61 | -3.12 | 0.200 | +9.12 | +7.40 | - |
| 113 | 94.33 | MT-W1-W1-46025 | ta.strong_close(pos_th=0.92208,vol_len=21,vol_mult=2.688457;R=none,S=full,T=weekly,X=own) | MT | bt | -0.50 | -0.65 | -0.706 | +8.01 | +6.29 | 41 |
| 114 | 95.33 | MT-W1-W1-38003 | ta.engulf_reversal(drop_th=-0.034108;R=none,S=full,T=weekly,X=own) | MT | bt | +0.77 | -3.92 | 0.230 | +9.27 | +7.56 | 277 |
| 115 | 95.67 | MT-W1-W1-07001 | mean_reversion.rsi2(n=3;R=bear,S=delever,T=daily,X=t7) | MT | bt | +0.46 | -2.92 | 0.210 | +8.96 | +7.25 | 625 |
| 116 | 96.33 | MT-W1-W1-29008 | event.breakout_confirm(n=39,vol_mult=2.101946;R=bear,S=full,T=weekly,X=t7) | MT | bt | -0.40 | -0.85 | -0.686 | +8.10 | +6.39 | 46 |
| 117 | 96.33 | MT-W1-W1-60009 | patterns.needle_probe(drop_th=-0.052812,shadow_pct=0.012075;R=none,S=full,T=daily,X=t10) | MT | bt | +0.28 | -2.23 | 0.122 | +8.78 | +7.07 | 151 |
| 118 | 96.33 | MT-W1-W1-67000 | folk.ants_climb(max_day=0.009792;R=bull,S=delever,T=daily,X=t10) | MT | bt | -0.13 | -1.49 | -0.107 | +8.37 | +6.66 | 67 |
| 119 | 98.00 | MT-W1-W1-20012 | sentiment.intraday_momentum(n=14;R=bear,S=delever,T=weekly,X=t10) | MT | bt | -0.39 | -1.31 | -0.355 | +8.11 | +6.40 | 413 |
| 120 | 98.33 | MT-W1-W1-61010 | patterns.obv_divergence(look=54;R=bull,S=delever,T=weekly,X=own) | MT | bt | +0.57 | -3.52 | 0.193 | +9.07 | +7.36 | 104 |
| 121 | 98.67 | MT-W1-W1-71002 | folk.low_suction(shrink=0.831435;R=bear,S=delever,T=weekly,X=t5) | MT | bt | -0.48 | -0.70 | -0.900 | +8.03 | +6.31 | 375 |
| 122 | 100.00 | MT-W1-W1-59002 | patterns.n_shape(leg_up=0.025543;R=none,S=delever,T=weekly,X=t7) | MT | bt | +0.97 | -7.40 | 0.224 | +9.48 | +7.76 | 642 |
| 123 | 100.33 | MT-W1-W1-38007 | ta.engulf_reversal(drop_th=-0.056031;R=none,S=delever,T=daily,X=own) | MT | bt | -0.08 | -1.99 | -0.026 | +8.43 | +6.71 | 135 |
| 124 | 100.33 | MT-W1-W1-60006 | patterns.needle_probe(drop_th=-0.047306,shadow_pct=0.03184;R=none,S=full,T=daily,X=own) | MT | bt | -0.01 | -2.15 | 0.004 | +8.49 | +6.78 | 38 |
| 125 | 101.33 | MT-W1-W1-60008 | patterns.needle_probe(drop_th=-0.075481,shadow_pct=0.036788;R=none,S=full,T=daily,X=t7) | MT | bt | -0.41 | -1.34 | -0.413 | +8.09 | +6.38 | 38 |
| 126 | 102.00 | MT-W1-W1-39012 | ta.hammer_reversal(body_max=0.68912,drop_th=-0.07976,shadow_mult=1.673026;R=bear,S=delever,T=daily,X=own) | MT | bt | +0.34 | -3.45 | 0.145 | +8.85 | +7.13 | 98 |
| 127 | 102.33 | MT-W1-W1-23011 | sentiment.turnover_surge(n=27,threshold=2.886098;R=bear,S=full,T=weekly,X=t10) | MT | bt | -0.21 | -1.82 | -0.103 | +8.29 | +6.58 | 63 |
| 128 | 103.00 | MT-W1-W1-47008 | ta.vol_breakout(brk_len=40,exit_len=14,vol_avg_len=33,vol_mult=2.674816;R=bear,S=delever,T=weekly,X=t10) | MT | bt | -0.40 | -0.98 | -0.804 | +8.11 | +6.39 | 102 |
| 129 | 103.00 | MT-W1-W1-67011 | folk.ants_climb(max_day=0.014977;R=none,S=full,T=weekly,X=t5) | MT | bt | +0.44 | -4.15 | 0.214 | +8.94 | +7.23 | 291 |
| 130 | 104.00 | MT-W1-W1-51012 | patterns.doji_at_low(drop_th=-0.084303;R=none,S=full,T=weekly,X=t20) | MT | bt | +0.70 | -5.91 | 0.179 | +9.20 | +7.49 | 191 |
| 131 | 105.00 | MT-W1-W1-58002 | patterns.morning_star(big_red=-0.03659,small_body=0.015977;R=bear,S=delever,T=daily,X=t20) | MT | bt | -0.11 | -2.28 | -0.033 | +8.39 | +6.68 | 105 |
| 132 | 105.33 | MT-W1-W1-05001 | mean_reversion.bollinger_breakout(k=3.458488,n=22;R=bear,S=delever,T=weekly,X=t10) | MT | bt | -0.18 | -2.14 | -0.088 | +8.33 | +6.62 | 428 |
| 133 | 108.33 | MT-W1-W1-33007 | macro.csi300_trend_filter(ma_n=342;R=bear,S=delever,T=weekly,X=t7) | MT | bt | -0.30 | -2.08 | -0.181 | +8.20 | +6.49 | 75 |
| 134 | 110.00 | MT-W1-W1-36000 | ta.bb_squeeze_breakout(bb_n=25,k=2.508295,width_n=64;R=bear,S=full,T=weekly,X=t10) | MT | bt | -0.65 | -0.91 | -1.495 | +7.85 | +6.14 | 114 |
| 135 | 111.33 | MT-W1-W1-71000 | folk.low_suction(shrink=1.438586;R=bear,S=delever,T=weekly,X=t10) | MT | bt | -0.80 | -0.94 | -1.175 | +7.71 | +5.99 | 411 |
| 136 | 112.33 | MT-W1-W1-23009 | sentiment.turnover_surge(n=12,threshold=3.703311;R=none,S=full,T=weekly,X=t10) | MT | bt | -0.56 | -1.60 | -0.521 | +7.95 | +6.23 | 36 |
| 137 | 113.33 | MT-W1-W1-74009 | folk.volume_mound(mound=1.934767;R=bull,S=delever,T=weekly,X=t20) | MT | bt | -0.24 | -3.44 | -0.044 | +8.26 | +6.55 | 136 |
| 138 | 114.67 | MT-W1-W1-25013 | seasonal.month_end_effect(window=2;R=bear,S=full,T=daily,X=t20) | MT | bt | -0.46 | -2.21 | -0.252 | +8.04 | +6.33 | 207 |
| 139 | 115.67 | MT-W1-W1-47001 | ta.vol_breakout(brk_len=19,exit_len=9,vol_avg_len=30,vol_mult=1.392306;R=bear,S=delever,T=weekly,X=own) | MT | bt | -0.98 | -1.30 | -0.982 | +7.53 | +5.81 | 399 |
| 140 | 116.00 | MT-W1-W1-07010 | mean_reversion.rsi2(n=4;R=bear,S=delever,T=daily,X=t7) | MT | bt | -0.36 | -3.32 | -0.139 | +8.15 | +6.43 | 551 |
| 141 | 116.33 | MT-W1-W1-55003 | patterns.island_reversal(gap=0.013619;R=none,S=full,T=daily,X=t5) | MT | bt | -0.81 | -1.56 | -0.693 | +7.70 | +5.98 | 33 |
| 142 | 117.00 | MT-W1-W1-56007 | patterns.ma_converge_break(spread=0.020459;R=bear,S=delever,T=weekly,X=t10) | MT | bt | -0.71 | -1.53 | -0.882 | +7.79 | +6.08 | 352 |
| 143 | 117.67 | MT-W1-W1-31004 | event.gap_fill(n=6;R=bear,S=delever,T=daily,X=t5) | MT | bt | -0.96 | -1.60 | -0.656 | +7.55 | +5.83 | 411 |
| 144 | 118.00 | MT-W1-W1-36013 | ta.bb_squeeze_breakout(bb_n=18,k=1.815385,width_n=119;R=none,S=full,T=daily,X=own) | MT | bt | -0.74 | -2.12 | -0.402 | +7.77 | +6.05 | 399 |
| 145 | 118.00 | MT-W1-W1-56002 | patterns.ma_converge_break(spread=0.011655;R=bear,S=delever,T=weekly,X=own) | MT | bt | -0.74 | -1.47 | -1.028 | +7.77 | +6.05 | 385 |
| 146 | 120.33 | MT-W1-W1-52002 | patterns.duck_head(neck=11;R=bear,S=delever,T=weekly,X=t20) | MT | bt | -1.00 | -1.38 | -1.108 | +7.51 | +5.79 | 244 |
| 147 | 120.67 | MT-W1-W1-45006 | ta.streak_up(min_up=0.0,streak_n=5;R=bear,S=delever,T=daily,X=t20) | MT | bt | -0.99 | -1.37 | -1.246 | +7.52 | +5.80 | 268 |
| 148 | 122.00 | MT-W1-W1-04009 | trend.triple_ma(n1=8,n2=31,n3=51;R=bear,S=delever,T=weekly,X=t5) | MT | bt | -1.10 | -1.51 | -0.939 | +7.40 | +5.69 | 409 |
| 149 | 122.33 | MT-W1-W1-29003 | event.breakout_confirm(n=29,vol_mult=1.863815;R=bear,S=full,T=weekly,X=t7) | MT | bt | -0.91 | -1.67 | -0.891 | +7.60 | +5.88 | 62 |
| 150 | 122.67 | MT-W1-W1-46001 | ta.strong_close(pos_th=0.900587,vol_len=22,vol_mult=1.685873;R=bear,S=full,T=weekly,X=t20) | MT | bt | -0.94 | -1.56 | -0.983 | +7.56 | +5.85 | 119 |
| 151 | 123.00 | MT-W1-W1-65010 | patterns.vol_drought_reversal(drop_th=-0.037573,vol_floor=0.657174;R=bear,S=full,T=weekly,X=t20) | MT | bt | -0.44 | -4.47 | -0.093 | +8.07 | +6.35 | 232 |
| 152 | 123.33 | MT-W1-W1-42005 | ta.nr7_breakout(hold_n=4,nr_n=8;R=bear,S=delever,T=weekly,X=t5) | MT | bt | -1.19 | -1.43 | -1.257 | +7.32 | +5.60 | 387 |
| 153 | 126.00 | MT-W1-W1-27006 | seasonal.trend_by_season(ma_n=379,month=7;R=bear,S=full,T=weekly,X=t20) | MT | bt | -0.77 | -3.94 | -0.200 | +7.73 | +6.02 | 42 |
| 154 | 126.33 | MT-W1-W1-46029 | ta.strong_close(pos_th=0.646659,vol_len=12,vol_mult=1.514583;R=bear,S=delever,T=weekly,X=t20) | MT | bt | -0.93 | -1.73 | -1.063 | +7.58 | +5.86 | 247 |
| 155 | 127.67 | MT-W1-W1-42003 | ta.nr7_breakout(hold_n=7,nr_n=8;R=bear,S=delever,T=weekly,X=t20) | MT | bt | -1.28 | -1.52 | -1.294 | +7.22 | +5.51 | 391 |
| 156 | 129.67 | LIVE-ALLOC-P4 | ALLOC-P4 | LIVE | bt+paper | -1.22 | -3.17 | -0.431 | +7.29 | +5.57 | - |
| 157 | 130.67 | MT-W1-W1-22002 | sentiment.price_volume_trend(n=39;R=bear,S=delever,T=weekly,X=t5) | MT | bt | -1.35 | -1.71 | -1.215 | +7.16 | +5.44 | 411 |
| 158 | 131.00 | LIVE-ENGULF-CE-01 | ENGULF-CE-01 | LIVE | bt+paper | -0.87 | -4.23 | -0.278 | +7.63 | +5.92 | - |
| 159 | 131.33 | MT-W1-W1-45007 | ta.streak_up(min_up=0.0,streak_n=3;R=bear,S=delever,T=weekly,X=t5) | MT | bt | -1.40 | -1.48 | -2.282 | +7.11 | +5.39 | 312 |
| 160 | 133.33 | MT-W1-W1-31013 | event.gap_fill(n=9;R=bear,S=delever,T=daily,X=own) | MT | bt | -1.61 | -1.94 | -1.070 | +6.89 | +5.18 | 507 |
| 161 | 133.33 | MT-W1-W1-52010 | patterns.duck_head(neck=13;R=bear,S=delever,T=weekly,X=own) | MT | bt | -1.32 | -1.72 | -1.881 | +7.18 | +5.47 | 240 |
| 162 | 135.67 | MT-W1-W1-23002 | sentiment.turnover_surge(n=25,threshold=1.946733;R=bear,S=full,T=weekly,X=t10) | MT | bt | -1.49 | -4.06 | -0.361 | +7.02 | +5.30 | 190 |
| 163 | 136.00 | MT-W1-W1-00001 | trend.donchian_breakout(entry_n=34,exit_n=7;R=bear,S=delever,T=weekly,X=own) | MT | bt | -1.56 | -3.36 | -0.664 | +6.95 | +5.23 | 383 |
| 164 | 138.33 | MT-W1-W1-70002 | folk.lian_yin_first_yang(n_down=5;R=bear,S=delever,T=weekly,X=t7) | MT | bt | -1.70 | -1.90 | -2.127 | +6.80 | +5.09 | 174 |
| 165 | 139.33 | MT-W1-W1-52011 | patterns.duck_head(neck=4;R=bear,S=delever,T=daily,X=own) | MT | bt | -1.40 | -2.16 | -1.569 | +7.11 | +5.39 | 387 |
| 166 | 143.00 | MT-W1-W1-39002 | ta.hammer_reversal(body_max=0.27642,drop_th=-0.08294,shadow_mult=1.486158;R=bull,S=full,T=weekly,X=t10) | MT | bt | -2.11 | -4.01 | -0.773 | +6.40 | +4.68 | 32 |
| 167 | 143.00 | MT-W1-W1-58010 | patterns.morning_star(big_red=-0.031798,small_body=0.016469;R=bull,S=delever,T=weekly,X=t20) | MT | bt | -2.26 | -4.92 | -0.490 | +6.25 | +4.53 | 47 |
| 168 | 144.00 | MT-W1-W1-58007 | patterns.morning_star(big_red=-0.044108,small_body=0.005761;R=none,S=delever,T=daily,X=t7) | MT | bt | -2.24 | -3.44 | -1.001 | +6.26 | +4.55 | 56 |
| 169 | 145.00 | MT-W1-W1-59000 | patterns.n_shape(leg_up=0.053869;R=bull,S=delever,T=daily,X=t5) | MT | bt | -2.63 | -8.07 | -0.396 | +5.87 | +4.16 | 339 |
| 170 | 146.00 | LIVE-ALLOC-P1 | ALLOC-P1 | LIVE | bt+paper | -3.12 | -6.60 | -0.446 | +5.39 | +3.67 | - |
| 171 | 146.00 | LIVE-ALLOC-P2 | ALLOC-P2 | LIVE | bt+paper | -2.73 | -10.42 | -0.260 | +5.77 | +4.06 | - |
| 172 | 146.00 | MT-W1-W1-13006 | momentum.relative_strength_rotation(n=19,top_k=9;R=bear,S=delever,T=weekly,X=t10) | MT | bt | -2.32 | -2.32 | -2.175 | +6.19 | +4.47 | 410 |
| 173 | 146.67 | MT-W1-W1-22012 | sentiment.price_volume_trend(n=14;R=bear,S=delever,T=weekly,X=t10) | MT | bt | -2.30 | -2.62 | -2.096 | +6.20 | +4.49 | 383 |
| 174 | 147.33 | MT-W1-W1-74006 | folk.volume_mound(mound=2.099963;R=none,S=full,T=daily,X=t10) | MT | bt | -3.30 | -4.19 | -0.762 | +5.20 | +3.49 | 267 |
| 175 | 150.00 | MT-W1-W1-49011 | patterns.big_yin_shakeout(big_yin=-0.018274;R=bull,S=delever,T=daily,X=t20) | MT | bt | -3.89 | -8.28 | -0.550 | +4.62 | +2.90 | 314 |
| 176 | 152.33 | LIVE-ALLOC-P3 | ALLOC-P3 | LIVE | bt+paper | -4.80 | -8.28 | -0.561 | +3.71 | +2.00 | - |
| 177 | 153.33 | LIVE-ALLOC-P3B | ALLOC-P3B | LIVE | bt+paper | -4.96 | -8.32 | -0.588 | +3.54 | +1.83 | - |
| 178 | 153.33 | MT-W1-W1-27012 | seasonal.trend_by_season(ma_n=242,month=7;R=none,S=delever,T=weekly,X=own) | MT | bt | -3.50 | -4.91 | -0.970 | +5.00 | +3.29 | 72 |
| 179 | 154.33 | MT-W1-W1-58008 | patterns.morning_star(big_red=-0.046642,small_body=0.014394;R=none,S=full,T=daily,X=t10) | MT | bt | -4.09 | -7.36 | -0.859 | +4.42 | +2.70 | 67 |
| 180 | 155.67 | MT-W1-W1-59012 | patterns.n_shape(leg_up=0.068909;R=bull,S=delever,T=daily,X=t7) | MT | bt | -4.56 | -9.99 | -0.751 | +3.95 | +2.23 | 185 |
| 181 | 156.00 | MT-W1-W1-55010 | patterns.island_reversal(gap=0.01029;R=none,S=full,T=weekly,X=t10) | MT | bt | -2.92 | -4.50 | -1.543 | +5.59 | +3.87 | 38 |
| 182 | 156.33 | MT-W1-W1-36003 | ta.bb_squeeze_breakout(bb_n=39,k=1.514807,width_n=110;R=bear,S=full,T=weekly,X=t5) | MT | bt | -3.13 | -3.67 | -2.426 | +5.38 | +3.66 | 272 |
| 183 | 158.67 | MT-W1-W1-01012 | trend.dual_ma_cross(fast=5,slow=36;R=bear,S=full,T=weekly,X=own) | MT | bt | -4.20 | -4.20 | -2.045 | +4.30 | +2.59 | 422 |
| 184 | 159.67 | MT-W1-W1-13005 | momentum.relative_strength_rotation(n=17,top_k=4;R=bull,S=full,T=daily,X=t7) | MT | bt | -8.77 | -15.37 | -0.820 | -0.27 | -1.98 | 862 |
| 185 | 164.67 | MT-W1-W1-36011 | ta.bb_squeeze_breakout(bb_n=35,k=2.235085,width_n=56;R=bull,S=delever,T=daily,X=own) | MT | bt | -6.21 | -7.56 | -2.096 | +2.30 | +0.58 | 339 |

## Paper-only live members (24, short marks window -- listed, rank N/A)
| id | src | seg | ytd% | maxDD% | sharpe | beat300pp | window |
|---|---|---|---|---|---|---|---|
| LIVE-AGGR-BARBELL | LIVE | paper | -0.156 | -0.38 | 2.778 | +8.35 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-FULLCE | LIVE | paper | -0.032 | -0.12 | -0.204 | +8.47 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-FULLCE-C80 | LIVE | paper | -0.025 | -0.09 | -0.204 | +8.48 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-GREEN-MAX | LIVE | paper | -0.409 | -0.51 | -1.565 | +8.10 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-GREEN-TOP2 | LIVE | paper | -0.070 | -0.18 | -1.565 | +8.44 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-MOM | LIVE | paper | -0.165 | -0.28 | -1.211 | +8.34 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-NOCASH | LIVE | paper | -0.021 | -0.07 | -0.193 | +8.48 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-OFFENSE-FULL | LIVE | paper | -0.129 | -0.54 | 6.112 | +8.38 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-REG3 | LIVE | paper | -0.129 | -0.54 | 6.112 | +8.38 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-TOP2-60 | LIVE | paper | -0.091 | -0.19 | -2.359 | +8.41 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-TOP2-80 | LIVE | paper | -0.121 | -0.20 | -3.712 | +8.38 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-TOP2-C80 | LIVE | paper | -0.061 | -0.15 | -1.708 | +8.44 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-TOP2-C95 | LIVE | paper | -0.073 | -0.17 | -1.708 | +8.43 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-TOP2-MON | LIVE | paper | +0.171 | -0.60 | 7.314 | +8.68 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-TOP2-WK | LIVE | paper | -0.498 | -0.57 | -6.556 | +8.01 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-TOP3 | LIVE | paper | -0.063 | -0.23 | -0.204 | +8.44 | 2026-09-24..2026-09-30 (4d) |
| LIVE-AGGR-TOP3-GRAD | LIVE | paper | -0.083 | -0.22 | -1.280 | +8.42 | 2026-09-24..2026-09-30 (4d) |
| LIVE-GRID-159915 | LIVE | paper | -2.507 | -2.51 | -2.021 | +6.00 | 2026-09-28..2026-09-30 (3d) |
| LIVE-GRID-510300 | LIVE | paper | -2.085 | -2.08 | -11.225 | +6.42 | 2026-09-28..2026-09-30 (3d) |
| LIVE-GRID-511010 | LIVE | paper | +0.007 | -0.01 | 7.633 | +8.51 | 2026-09-28..2026-09-30 (3d) |
| LIVE-GRID-512880 | LIVE | paper | -0.508 | -0.68 | 9.428 | +8.00 | 2026-09-28..2026-09-30 (3d) |
| LIVE-GRID-518880 | LIVE | paper | -0.889 | -1.76 | 5.287 | +7.62 | 2026-09-28..2026-09-30 (3d) |
| LIVE-REV-OSC-STD | LIVE | paper | -0.150 | -1.16 | 15.629 | +8.36 | 2026-09-28..2026-09-30 (3d) |
| LIVE-SYSTEM-V1 | LIVE | paper | -0.082 | -0.39 | 15.629 | +8.42 | 2026-09-28..2026-09-30 (3d) |

## Pending burn legs (10, due before 10-08)
- RC-D-15-raw-base-time-h20 -- D-15|raw|base|time|h20 (REV_CENSUS_POSITIVE)
- RC-D-15-raw-liq2-time-h20 -- D-15|raw|liq2|time|h20 (REV_CENSUS_POSITIVE)
- RC-D-15-yang-base-time-h20 -- D-15|yang|base|time|h20 (REV_CENSUS_POSITIVE)
- RC-D-15-yang-liq2-time-h20 -- D-15|yang|liq2|time|h20 (REV_CENSUS_POSITIVE)
- RC-D-25-raw-base-time-h20 -- D-25|raw|base|time|h20 (REV_CENSUS_POSITIVE)
- RC-D-25-raw-liq2-time-h20 -- D-25|raw|liq2|time|h20 (REV_CENSUS_POSITIVE)
- RC-D-25-yang-base-time-h20 -- D-25|yang|base|time|h20 (REV_CENSUS_POSITIVE)
- RC-Dtop10-raw-base-time-h20 -- Dtop10|raw|base|time|h20 (REV_CENSUS_POSITIVE)
- RC-Dtop10-raw-liq2-time-h20 -- Dtop10|raw|liq2|time|h20 (REV_CENSUS_POSITIVE)
- RC-Dtop10-yang-base-time-h20 -- Dtop10|yang|base|time|h20 (REV_CENSUS_POSITIVE)

## Honesty
- contest selection != scientific proof; winners promoted with 'contest-selected' label (O-2150 sec.1)
- paper-only live members (rank N/A): marks windows 3-4 days (live starts 09-24/09-28) are NOT comparable to the 181-day YTD ladder -- listed, not ranked
- B_MAXDIV window ends 09-23 (backtest-leg only member, no separate paper ledger) -- ranked with 177d window disclosed
- frozen signal_sha256 reproduces bit-for-bit only on X=own (34/166); X=t* 132/166 format-divergent by construction (object-dtype pointer hash at generation; value semantics covered by selftest S4/S7)
- pending-leg faces (rev-census / lowamp deep) burn on their frozen panels whose natural end is 2026-09-22 (T-94 / lowamp D2 lockbox): their YTD windows are ~176d vs the 181d contest baselines -- ranked with window end disclosed (B_MAXDIV 177d precedent); beat columns are arithmetic-honest, comparability limited by the window mismatch; each row carries its reuse-parity anchor (published batch stats reproduced)
