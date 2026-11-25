# IH as a hedge for the ETF book

Cutoff 2026-11-24 | book bars 1594 (2020-01-06..2026-11-24) | IH IH, one lot 812580 CNY.

## What the hedge would have to be

| reading | value |
| --- | --- |
| book beta to IH | 0.0748 |
| correlation | 0.141 |
| share of book variance an index hedge could remove | 2.0% |
| splice days dropped | 85 |

## Same beta on the days that hurt

| slice | n | beta | corr |
| --- | --- | --- | --- |
| book_down | 708 | 0.0792 | 0.203 |
| book_up | 886 | 0.0290 | 0.077 |
| ih_le_-1 | 235 | 0.3179 | 0.429 |
| ih_le_-2 | 52 | 0.6126 | 0.752 |

## A correctly sized short, at several multiples of beta

| k (x beta) | mean/yr | vol | sharpe | maxdd |
| --- | --- | --- | --- | --- |
| 0.00 | 0.0931 | 0.1008 | 0.924 | -0.1115 |
| 0.25 | 0.0924 | 0.1003 | 0.920 | -0.1103 |
| 0.50 | 0.0916 | 0.1000 | 0.916 | -0.1092 |
| 1.00 | 0.0901 | 0.0998 | 0.903 | -0.1121 |
| 1.50 | 0.0885 | 0.1000 | 0.885 | -0.1180 |

## Can it actually be traded

| capital | unit/1beta target | 1x beta executable | capital for one lot at 1 beta |
| --- | --- | --- | --- |
| 1,000,000 | 10.87x | no | 10,868,586 |
| 3,000,000 | 3.62x | no | 10,868,586 |
| 5,000,000 | 2.17x | yes | 10,868,586 |
| 10,000,000 | 1.09x | yes | 10,868,586 |
| 20,000,000 | 0.54x | yes | 10,868,586 |

## Verdict

**UNEXECUTABLE_AT_THIS_SIZE.** One IH lot is 10.87x the short beta asks for at 1,000,000 CNY, so the only tradeable version of this hedge is an oversized short, not a hedge.

