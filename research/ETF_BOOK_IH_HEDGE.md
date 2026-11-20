# IH as a hedge for the ETF book

Cutoff 2026-11-20 | book bars 1592 (2020-01-06..2026-11-20) | IH IH, one lot 816480 CNY.

## What the hedge would have to be

| reading | value |
| --- | --- |
| book beta to IH | 0.0748 |
| correlation | 0.142 |
| share of book variance an index hedge could remove | 2.0% |
| splice days dropped | 85 |

## Same beta on the days that hurt

| slice | n | beta | corr |
| --- | --- | --- | --- |
| book_down | 707 | 0.0796 | 0.204 |
| book_up | 885 | 0.0288 | 0.076 |
| ih_le_-1 | 235 | 0.3179 | 0.429 |
| ih_le_-2 | 52 | 0.6126 | 0.752 |

## A correctly sized short, at several multiples of beta

| k (x beta) | mean/yr | vol | sharpe | maxdd |
| --- | --- | --- | --- | --- |
| 0.00 | 0.0932 | 0.1006 | 0.927 | -0.1115 |
| 0.25 | 0.0925 | 0.1002 | 0.923 | -0.1103 |
| 0.50 | 0.0917 | 0.0998 | 0.919 | -0.1092 |
| 1.00 | 0.0902 | 0.0996 | 0.906 | -0.1121 |
| 1.50 | 0.0887 | 0.0998 | 0.889 | -0.1180 |

## Can it actually be traded

| capital | unit/1beta target | 1x beta executable | capital for one lot at 1 beta |
| --- | --- | --- | --- |
| 1,000,000 | 10.91x | no | 10,913,794 |
| 3,000,000 | 3.64x | no | 10,913,794 |
| 5,000,000 | 2.18x | yes | 10,913,794 |
| 10,000,000 | 1.09x | yes | 10,913,794 |
| 20,000,000 | 0.55x | yes | 10,913,794 |

## Verdict

**UNEXECUTABLE_AT_THIS_SIZE.** One IH lot is 10.91x the short beta asks for at 1,000,000 CNY, so the only tradeable version of this hedge is an oversized short, not a hedge.

