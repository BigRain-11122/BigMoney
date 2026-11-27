# IH as a hedge for the ETF book

Cutoff 2026-11-26 | book bars 1596 (2020-01-06..2026-11-26) | IH IH, one lot 814800 CNY.

## What the hedge would have to be

| reading | value |
| --- | --- |
| book beta to IH | 0.0752 |
| correlation | 0.142 |
| share of book variance an index hedge could remove | 2.0% |
| splice days dropped | 85 |

## Same beta on the days that hurt

| slice | n | beta | corr |
| --- | --- | --- | --- |
| book_down | 710 | 0.0797 | 0.204 |
| book_up | 886 | 0.0290 | 0.077 |
| ih_le_-1 | 236 | 0.3162 | 0.426 |
| ih_le_-2 | 52 | 0.6126 | 0.752 |

## A correctly sized short, at several multiples of beta

| k (x beta) | mean/yr | vol | sharpe | maxdd |
| --- | --- | --- | --- | --- |
| 0.00 | 0.0909 | 0.1008 | 0.902 | -0.1115 |
| 0.25 | 0.0902 | 0.1004 | 0.899 | -0.1103 |
| 0.50 | 0.0895 | 0.1000 | 0.894 | -0.1091 |
| 1.00 | 0.0880 | 0.0998 | 0.882 | -0.1121 |
| 1.50 | 0.0865 | 0.1000 | 0.865 | -0.1181 |

## Can it actually be traded

| capital | unit/1beta target | 1x beta executable | capital for one lot at 1 beta |
| --- | --- | --- | --- |
| 1,000,000 | 10.83x | no | 10,832,486 |
| 3,000,000 | 3.61x | no | 10,832,486 |
| 5,000,000 | 2.17x | yes | 10,832,486 |
| 10,000,000 | 1.08x | yes | 10,832,486 |
| 20,000,000 | 0.54x | yes | 10,832,486 |

## Verdict

**UNEXECUTABLE_AT_THIS_SIZE.** One IH lot is 10.83x the short beta asks for at 1,000,000 CNY, so the only tradeable version of this hedge is an oversized short, not a hedge.

