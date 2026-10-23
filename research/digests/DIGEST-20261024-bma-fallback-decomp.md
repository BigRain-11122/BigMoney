# DIGEST 2026-10-24 (bm-a r1105) -- who is still on the deadline bound

Face = cross-statement filing-event availability (results/fund_avail_filing_event.json). Question: the residual rows that still fall back to the statutory deadline -- random, or structured by era / industry / earnings tail?

## income: 69166/461679 rows fall back (15.0%); industry mapped 67.2%
- era pre2010: 16036/37858 = 42.4% (lift 2.827)
- era 2010+: 53130/423821 = 12.5% (lift 0.837)
- heaviest year x industry cells (lift>=1.5, n>=30): 2006 银行Ⅱ 64% of 67 (lift 4.284); 2009 家电零部件Ⅱ 64% of 39 (lift 4.279); 2009 游戏Ⅱ 63% of 43 (lift 4.191); 2009 自动化设备 63% of 43 (lift 4.191); 2006 通信服务 62% of 32 (lift 4.172)
- consumable window (last 8 periods, from 2024-09-30): 70023 rows, fallback 0.0187
- NOT industry structure: 2008 unmapped 96% of 871 (lift 6.43); 2009 unmapped 96% of 971 (lift 6.421); 2007 unmapped 95% of 824 (lift 6.327); 2006 unmapped 95% of 768 (lift 6.319) -- the source industry column is only 67% populated for this face, so these cells measure the LABEL HOLE, not a sector effect

## cashflow: 31052/292537 rows fall back (10.6%); industry mapped 99.5%
- era pre2010: 10293/31900 = 32.3% (lift 3.04)
- era 2010+: 20759/260637 = 8.0% (lift 0.75)
- heaviest year x industry cells (lift>=1.5, n>=30): 2009 游戏Ⅱ 63% of 43 (lift 5.915); 2009 自动化设备 63% of 43 (lift 5.915); 2006 银行Ⅱ 61% of 57 (lift 5.785); 2006 通信服务 61% of 31 (lift 5.774); 2008 游戏Ⅱ 61% of 31 (lift 5.774)
- consumable window (last 8 periods, from 2024-09-30): 41848 rows, fallback 0.0058
- NOT industry structure: 2009 unmapped 42% of 53 (lift 3.911); 2012 unmapped 40% of 63 (lift 3.738); 2017 unmapped 37% of 81 (lift 3.489); 2014 unmapped 37% of 65 (lift 3.478) -- the source industry column is only 100% populated for this face, so these cells measure the LABEL HOLE, not a sector effect

## balance: 22235/283955 rows fall back (7.8%); industry mapped 99.5%
- era pre2010: 9150/30880 = 29.6% (lift 3.784)
- era 2010+: 13085/253075 = 5.2% (lift 0.66)
- heaviest year x industry cells (lift>=1.5, n>=30): 2006 银行Ⅱ 57% of 58 (lift 7.266); 2009 塑料 53% of 47 (lift 6.793); 2009 游戏Ⅱ 53% of 34 (lift 6.761); 2009 消费电子 53% of 55 (lift 6.734); 2007 软件开发 52% of 65 (lift 6.68)
- consumable window (last 8 periods, from 2024-09-30): 41701 rows, fallback 0.0022
- NOT industry structure: 2009 unmapped 38% of 50 (lift 4.853); 2012 unmapped 37% of 60 (lift 4.683); 2010 unmapped 35% of 52 (lift 4.421); 2014 unmapped 34% of 62 (lift 4.326) -- the source industry column is only 100% populated for this face, so these cells measure the LABEL HOLE, not a sector effect

## earnings tail (income, roe deciles inside era)
- 2010+: base 11.2%, top-vs-bottom decile spread +24.6%
  - bottom decile (roe -41598.51..-4.47%): 9.5% of 40947
  - top decile (roe 18.72..14185092.68%): 34.1% of 40932
- pre2010: base 56.0%, top-vs-bottom decile spread +47.0%
  - bottom decile (roe -266264.61..-0.73%): 48.0% of 1970
  - top decile (roe 29.74..4571.413%): 95.0% of 1969

## earnings tail controlled for report quarter (income)
- 2010+-03: n=71036, base 6.4%, bottom 7.7% -> top 17.6% (spread +9.9%)
- 2010+-06: n=131004, base 8.8%, bottom 9.0% -> top 20.6% (spread +11.5%)
- 2010+-09: n=65369, base 4.1%, bottom 3.6% -> top 14.0% (spread +10.4%)
- 2010+-12: n=142053, base 19.0%, bottom 11.3% -> top 45.8% (spread +34.4%)
- pre2010-03: n=1099, base 23.3%, bottom 19.1% -> top 52.7% (spread +33.6%)
- pre2010-06: n=7675, base 16.7%, bottom 23.7% -> top 27.6% (spread +3.9%)
- pre2010-09: n=238, base 28.1%, bottom 20.2% -> top 58.3% (spread +38.1%)
- pre2010-12: n=10686, base 88.2%, bottom 79.4% -> top 98.5% (spread +19.1%)

## decision
- income: recent window fallback 0.0187 -> needs_row_flag=False
- cashflow: recent window fallback 0.0058 -> needs_row_flag=False
- balance: recent window fallback 0.0022 -> needs_row_flag=False

keep the never-early deadline bound as is; publish the existing `fallback` boolean as the confidence column instead of inventing a new score -- it is exact (row-level), already materialised in every <face>_avail_event.parquet, and needs no threshold. Only rows in the recent-quarter block with fallback=True should be down-weighted by any consumer that needs true filing dates.
