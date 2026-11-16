# IH as a hedge for the ETF book

Cutoff 2026-11-16 | book bars 1587 (2020-01-06..2026-11-13) | IH IH, one lot 820020 CNY.

## What the hedge would have to be

| reading | value |
| --- | --- |
| book beta to IH | 0.0745 |
| correlation | 0.142 |
| share of book variance an index hedge could remove | 2.0% |
| splice days dropped | 85 |

## Same beta on the days that hurt

| slice | n | beta | corr |
| --- | --- | --- | --- |
| book_down | 703 | 0.0793 | 0.204 |
| book_up | 884 | 0.0288 | 0.076 |
| ih_le_-1 | 235 | 0.3179 | 0.429 |
| ih_le_-2 | 52 | 0.6126 | 0.752 |

## A correctly sized short, at several multiples of beta

| k (x beta) | mean/yr | vol | sharpe | maxdd |
| --- | --- | --- | --- | --- |
| 0.00 | 0.0974 | 0.1005 | 0.968 | -0.1115 |
| 0.25 | 0.0966 | 0.1001 | 0.965 | -0.1103 |
| 0.50 | 0.0958 | 0.0998 | 0.961 | -0.1092 |
| 1.00 | 0.0943 | 0.0995 | 0.948 | -0.1120 |
| 1.50 | 0.0928 | 0.0998 | 0.930 | -0.1179 |

## Can it actually be traded

| capital | unit/1beta target | 1x beta executable | capital for one lot at 1 beta |
| --- | --- | --- | --- |
| 1,000,000 | 11.00x | no | 11,001,516 |
| 3,000,000 | 3.67x | no | 11,001,516 |
| 5,000,000 | 2.20x | yes | 11,001,516 |
| 10,000,000 | 1.10x | yes | 11,001,516 |
| 20,000,000 | 0.55x | yes | 11,001,516 |

## Verdict

**UNEXECUTABLE_AT_THIS_SIZE.** One IH lot is 11.00x the short beta asks for at 1,000,000 CNY, so the only tradeable version of this hedge is an oversized short, not a hedge.

