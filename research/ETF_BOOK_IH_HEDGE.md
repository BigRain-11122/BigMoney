# IH as a hedge for the ETF book

Cutoff 2026-11-19 | book bars 1590 (2020-01-06..2026-11-18) | IH IH, one lot 819360 CNY.

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
| book_up | 885 | 0.0288 | 0.076 |
| ih_le_-1 | 235 | 0.3179 | 0.429 |
| ih_le_-2 | 52 | 0.6126 | 0.752 |

## A correctly sized short, at several multiples of beta

| k (x beta) | mean/yr | vol | sharpe | maxdd |
| --- | --- | --- | --- | --- |
| 0.00 | 0.0959 | 0.1005 | 0.954 | -0.1115 |
| 0.25 | 0.0951 | 0.1000 | 0.951 | -0.1103 |
| 0.50 | 0.0944 | 0.0997 | 0.946 | -0.1092 |
| 1.00 | 0.0929 | 0.0995 | 0.934 | -0.1120 |
| 1.50 | 0.0914 | 0.0997 | 0.916 | -0.1180 |

## Can it actually be traded

| capital | unit/1beta target | 1x beta executable | capital for one lot at 1 beta |
| --- | --- | --- | --- |
| 1,000,000 | 10.99x | no | 10,985,609 |
| 3,000,000 | 3.66x | no | 10,985,609 |
| 5,000,000 | 2.20x | yes | 10,985,609 |
| 10,000,000 | 1.10x | yes | 10,985,609 |
| 20,000,000 | 0.55x | yes | 10,985,609 |

## Verdict

**UNEXECUTABLE_AT_THIS_SIZE.** One IH lot is 10.99x the short beta asks for at 1,000,000 CNY, so the only tradeable version of this hedge is an oversized short, not a hedge.

