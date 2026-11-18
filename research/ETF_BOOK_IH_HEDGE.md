# IH as a hedge for the ETF book

Cutoff 2026-11-17 | book bars 1589 (2020-01-06..2026-11-17) | IH IH, one lot 819360 CNY.

## What the hedge would have to be

| reading | value |
| --- | --- |
| book beta to IH | 0.0746 |
| correlation | 0.142 |
| share of book variance an index hedge could remove | 2.0% |
| splice days dropped | 85 |

## Same beta on the days that hurt

| slice | n | beta | corr |
| --- | --- | --- | --- |
| book_down | 705 | 0.0793 | 0.204 |
| book_up | 884 | 0.0288 | 0.076 |
| ih_le_-1 | 235 | 0.3179 | 0.429 |
| ih_le_-2 | 52 | 0.6126 | 0.752 |

## A correctly sized short, at several multiples of beta

| k (x beta) | mean/yr | vol | sharpe | maxdd |
| --- | --- | --- | --- | --- |
| 0.00 | 0.0957 | 0.1005 | 0.952 | -0.1115 |
| 0.25 | 0.0950 | 0.1001 | 0.949 | -0.1103 |
| 0.50 | 0.0942 | 0.0998 | 0.944 | -0.1092 |
| 1.00 | 0.0927 | 0.0995 | 0.932 | -0.1120 |
| 1.50 | 0.0912 | 0.0998 | 0.914 | -0.1180 |

## Can it actually be traded

| capital | unit/1beta target | 1x beta executable | capital for one lot at 1 beta |
| --- | --- | --- | --- |
| 1,000,000 | 10.99x | no | 10,985,881 |
| 3,000,000 | 3.66x | no | 10,985,881 |
| 5,000,000 | 2.20x | yes | 10,985,881 |
| 10,000,000 | 1.10x | yes | 10,985,881 |
| 20,000,000 | 0.55x | yes | 10,985,881 |

## Verdict

**UNEXECUTABLE_AT_THIS_SIZE.** One IH lot is 10.99x the short beta asks for at 1,000,000 CNY, so the only tradeable version of this hedge is an oversized short, not a hedge.

