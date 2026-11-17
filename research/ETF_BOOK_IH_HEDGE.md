# IH as a hedge for the ETF book

Cutoff 2026-11-17 | book bars 1662 (2020-01-06..2026-11-17) | IH IH, one lot 818880 CNY.

## What the hedge would have to be

| reading | value |
| --- | --- |
| book beta to IH | 0.0719 |
| correlation | 0.137 |
| share of book variance an index hedge could remove | 1.9% |
| splice days dropped | 1 |

## Same beta on the days that hurt

| slice | n | beta | corr |
| --- | --- | --- | --- |
| book_down | 737 | 0.0758 | 0.195 |
| book_up | 925 | 0.0311 | 0.084 |
| ih_le_-1 | 254 | 0.3105 | 0.419 |
| ih_le_-2 | 57 | 0.6116 | 0.753 |

## A correctly sized short, at several multiples of beta

| k (x beta) | mean/yr | vol | sharpe | maxdd |
| --- | --- | --- | --- | --- |
| 0.00 | 0.0950 | 0.0998 | 0.952 | -0.1177 |
| 0.25 | 0.0949 | 0.0994 | 0.955 | -0.1136 |
| 0.50 | 0.0949 | 0.0991 | 0.957 | -0.1095 |
| 1.00 | 0.0947 | 0.0989 | 0.958 | -0.1023 |
| 1.50 | 0.0945 | 0.0991 | 0.954 | -0.1082 |

## Can it actually be traded

| capital | unit/1beta target | 1x beta executable | capital for one lot at 1 beta |
| --- | --- | --- | --- |
| 1,000,000 | 11.40x | no | 11,395,937 |
| 3,000,000 | 3.80x | no | 11,395,937 |
| 5,000,000 | 2.28x | yes | 11,395,937 |
| 10,000,000 | 1.14x | yes | 11,395,937 |
| 20,000,000 | 0.57x | yes | 11,395,937 |

## Verdict

**UNEXECUTABLE_AT_THIS_SIZE.** One IH lot is 11.40x the short beta asks for at 1,000,000 CNY, so the only tradeable version of this hedge is an oversized short, not a hedge.

