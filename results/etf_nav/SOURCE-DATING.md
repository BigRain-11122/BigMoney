# Which day is this NAV from?

board session: 2026-11-27 · rows with a price: 1673 · minimum move that can date a row: 1.0%

## Verdict

- ALL: BOTH_CURRENT_BUT_SINA_LAGS_ON_115 -- board 1371/1439 on today's path, dated sina 1157/1439 on it and 115/1439 on yesterday's close even though it prints today; 59 board rows sit beyond the day's move (44 with the price at the band and both sources agreeing, 15 with the sources disagreeing)
- R2212_GAP_SET: BOTH_CURRENT_BUT_SINA_LAGS_ON_18 -- board 43/47 on today's path, dated sina 28/47 on it and 18/47 on yesterday's close even though it prints today; 3 board rows sit beyond the day's move (2 with the price at the band and both sources agreeing, 1 with the sources disagreeing)

## Counts by group (price-decidable rows only)

| group | rows | decidable | board SAME | board PREV | board beyond: capped | beyond: agreed | beyond: sources disagree | sina SAME | sina PREV | sina missing |
|---|---|---|---|---|---|---|---|---|---|---|
| all tickers | 1673 | 1439 | 1371 | 8 | 21 | 23 | 15 | 1157 | 115 | 180 |
| r2212 gap set | 53 | 47 | 43 | 1 | 0 | 2 | 1 | 28 | 18 | 0 |

Legend: SAME_SESSION = the number sits on today's close path; PREV_SESSION = it
sits on yesterday's close; UNDECIDABLE = the price barely moved, so price alone
cannot tell the two days apart (not agreement). A row BEYOND the day's move is
split three ways because the three cases mean different things:

- `capped` -- the move is >= 9.5% (the band) and both sources agree within 1%: the
  price could not travel to the NAV, so this row is a statement about the band, not
  about a stale number.
- `agreed beyond` -- both sources agree within 1% but the price did not hit a band:
  the NAV moved more than the traded price that day. Not datable from price alone.
- `sources disagree` -- the two sources differ by more than 1% (or one is missing):
  the only case that leaves a real dating question open.

## Rows within 0.05 of a decision line (the cut decided these, not the data)

board 21 and sina 22 of 1439 decidable rows sit this close to a line.

| code | board | sina | board t | sina t | board label | sina label | move% |
|---|---|---|---|---|---|---|---|
| 159010 | 0.6941 | 0.6952 | 1.356 | 1.388 | OVERSHOOT | OVERSHOOT | 5.25 |
| 159089 | 0.8905 | None | 1.303 | n/a | SAME_SESSION | NO_DATA | 4.52 |
| 159135 | 0.6028 | 0.6063 | 1.206 | 1.312 | SAME_SESSION | SAME_SESSION | 5.86 |
| 159166 | 0.8256 | 0.8254 | 1.400 | 1.378 | OVERSHOOT | OVERSHOOT | 1.11 |
| 159239 | 0.5919 | 0.5924 | 1.295 | 1.320 | SAME_SESSION | SAME_SESSION | 3.53 |
| 159259 | 0.8877 | 0.8717 | 1.342 | 1.137 | SAME_SESSION | SAME_SESSION | 9.96 |
| 159311 | 1.1852 | 1.1852 | 1.316 | 1.316 | SAME_SESSION | SAME_SESSION | 10.03 |
| 159312 | 1.0669 | 1.0706 | 1.347 | 1.565 | SAME_SESSION | OVERSHOOT | 1.63 |
| 159399 | 0.9459 | 0.9405 | 0.994 | 0.656 | SAME_SESSION | SAME_SESSION | 1.72 |
| 159537 | 0.6802 | 0.6689 | 1.370 | 1.182 | OVERSHOOT | SAME_SESSION | 10.03 |
| 159538 | 0.6917 | 0.68 | 1.339 | 1.148 | SAME_SESSION | SAME_SESSION | 10.00 |
| 159539 | 1.3617 | 1.3394 | 1.381 | 1.195 | OVERSHOOT | SAME_SESSION | 10.03 |
| 159540 | 1.4716 | 1.4475 | 1.377 | 1.190 | OVERSHOOT | SAME_SESSION | 9.97 |
| 159583 | 1.0708 | 1.0711 | 1.303 | 1.306 | SAME_SESSION | SAME_SESSION | 10.03 |
| 159711 | 1.2014 | 1.1945 | 1.950 | 1.375 | OVERSHOOT | OVERSHOOT | 1.02 |
| 159712 | 1.119 | 1.1124 | 1.909 | 1.309 | OVERSHOOT | SAME_SESSION | 1.00 |
| 159819 | 1.3878 | 1.388 | 1.299 | 1.301 | SAME_SESSION | SAME_SESSION | 10.02 |
| 159849 | 0.4736 | 0.4735 | 1.373 | 1.367 | OVERSHOOT | OVERSHOOT | 3.31 |
| 159913 | 2.252 | 2.2516 | 0.683 | 0.678 | SAME_SESSION | SAME_SESSION | 3.73 |
| 159960 | 0.7706 | 0.7739 | 1.114 | 1.350 | SAME_SESSION | SAME_SESSION | 1.85 |
| 159980 | 1.8829 | 1.9302 | 0.700 | 1.314 | SAME_SESSION | SAME_SESSION | 4.21 |
| 512130 | 1.0581 | 1.0577 | 1.300 | 1.276 | SAME_SESSION | SAME_SESSION | 1.64 |
| 512180 | 1.4742 | 1.4796 | 1.317 | 1.429 | SAME_SESSION | OVERSHOOT | 3.40 |
| 513630 | 1.5584 | 1.5603 | 0.330 | 0.235 | PREV_SESSION | PREV_SESSION | -1.28 |
| 513800 | 1.7488 | 1.7219 | 1.406 | 0.615 | OVERSHOOT | BETWEEN | 2.00 |
| ... | | | | | | | 9 more |

## Dated rows that sit on yesterday's close (the ones to re-date)

| code | board | sina | sina date | prev | last | move% | board t |
|---|---|---|---|---|---|---|---|
| 159012 | 0.6458 | 0.565 | 2026-11-27 | 0.5670 | 0.6510 | 14.81 | -0.024 |
| 159032 | 0.6483 | 0.6118 | 2026-11-27 | 0.6100 | 0.6460 | 5.90 | 0.050 |
| 159117 | 0.997 | 0.9982 | 2026-11-27 | 0.9970 | 0.9870 | -1.00 | -0.120 |
| 159147 | 0.632 | 0.5838 | 2026-11-27 | 0.5840 | 0.6330 | 8.39 | -0.004 |
| 159169 | 0.9002 | 0.8538 | 2026-11-27 | 0.8510 | 0.8990 | 5.64 | 0.058 |
| 159202 | 0.6325 | 0.5976 | 2026-11-26 | 0.6010 | 0.6290 | 4.66 | -0.121 |
| 159215 | 1.1208 | 1.0657 | 2026-11-27 | 1.0630 | 1.1290 | 6.21 | 0.041 |
| 159222 | 1.2142 | 1.1983 | 2026-11-27 | 1.1950 | 1.2160 | 1.76 | 0.157 |
| 159231 | 0.4057 | 0.3749 | 2026-11-27 | 0.3730 | 0.4070 | 9.12 | 0.056 |
| 159240 | 1.1085 | 1.0551 | 2026-11-27 | 1.0550 | 1.1080 | 5.02 | 0.002 |
| 159303 | 1.4464 | 1.3752 | 2026-11-26 | 1.3710 | 1.4460 | 5.47 | 0.056 |
| 159323 | 0.7958 | 0.7616 | 2026-11-27 | 0.7610 | 0.7920 | 4.07 | 0.019 |
| 159360 | 1.1278 | 1.0719 | 2026-11-27 | 1.0710 | 1.1320 | 5.70 | 0.015 |
| 159361 | 1.0625 | 1.0102 | 2026-11-27 | 1.0070 | 1.0690 | 6.16 | 0.052 |
| 159362 | 1.1199 | 1.0642 | 2026-11-27 | 1.0620 | 1.1200 | 5.46 | 0.038 |
| 159369 | 0.9485 | 0.8445 | 2026-11-27 | 0.8440 | 0.9580 | 13.51 | 0.004 |
| 159380 | 1.1655 | 1.1086 | 2026-11-27 | 1.1070 | 1.1680 | 5.51 | 0.026 |
| 159546 | 0.6088 | 0.532 | 2026-11-27 | 0.5310 | 0.5840 | 9.98 | 0.019 |
| 159557 | 1.3179 | 1.2521 | 2026-11-26 | 1.2510 | 1.3200 | 5.52 | 0.016 |
| 159608 | 0.7608 | 0.7098 | 2026-11-27 | 0.7100 | 0.7620 | 7.32 | -0.004 |
| 159615 | 1.0292 | 0.9749 | 2026-11-26 | 0.9740 | 1.0270 | 5.44 | 0.017 |
| 159628 | 1.0922 | 1.0121 | 2026-11-27 | 1.0080 | 1.1090 | 10.02 | 0.041 |
| 159639 | 0.7942 | 0.7654 | 2026-11-27 | 0.7630 | 0.7930 | 3.93 | 0.080 |
| 159661 | 1.2596 | 1.204 | 2026-11-27 | 1.2020 | 1.2620 | 4.99 | 0.033 |
| 159675 | 1.023 | 0.9171 | 2026-11-27 | 0.9180 | 1.0260 | 11.76 | -0.008 |
| ... | | | | | | 90 more |

## Board numbers beyond the day's move, with both sources agreeing

44 of 59 rows: 21 at the price band, 23 beyond it without a band. Both
sources say the same number here, so the date question does not arise -- the
NAV simply moved further than the traded price could.

| code | board | sina | board/sina-1 % | prev | last | move% |
|---|---|---|---|---|---|---|
| 159010 | 0.6941 | 0.6952 | 0.158 | 0.6480 | 0.6820 | 5.25 |
| 159109 | 0.7203 | 0.7164 | 0.544 | 0.7010 | 0.7130 | 1.71 |
| 159166 | 0.8256 | 0.8254 | 0.024 | 0.8130 | 0.8220 | 1.11 |
| 159310 | 2.2232 | 2.2233 | 0.004 | 1.9250 | 2.1180 | 10.03 |
| 159318 | 1.1814 | 1.1856 | 0.354 | 1.1560 | 1.1720 | 1.38 |
| 159325 | 0.8214 | 0.8213 | 0.012 | 0.7120 | 0.7830 | 9.97 |
| 159327 | 0.8644 | 0.8644 | 0.000 | 0.7350 | 0.8090 | 10.07 |
| 159365 | 0.8961 | 0.8994 | 0.367 | 0.8750 | 0.8890 | 1.60 |
| 159516 | 0.5384 | 0.5385 | 0.019 | 0.4590 | 0.5050 | 10.02 |
| 159558 | 0.8448 | 0.8447 | 0.012 | 0.7200 | 0.7920 | 10.00 |
| 159560 | 0.8993 | 0.8994 | 0.011 | 0.7790 | 0.8570 | 10.01 |
| 159582 | 0.6105 | 0.6098 | 0.115 | 0.5190 | 0.5710 | 10.02 |
| 159599 | 2.1934 | 2.194 | 0.027 | 1.9010 | 2.0910 | 9.99 |
| 159665 | 1.8656 | 1.8662 | 0.032 | 1.6160 | 1.7780 | 10.02 |
| 159711 | 1.2014 | 1.1945 | 0.578 | 1.1780 | 1.1900 | 1.02 |
| 159712 | 1.119 | 1.1124 | 0.593 | 1.0980 | 1.1090 | 1.00 |
| 159801 | 0.8721 | 0.8723 | 0.023 | 0.7550 | 0.8310 | 10.07 |
| 159813 | 0.5635 | 0.5635 | 0.000 | 0.4880 | 0.5370 | 10.04 |
| 159849 | 0.4736 | 0.4735 | 0.021 | 0.4530 | 0.4680 | 3.31 |
| 159954 | 0.8315 | 0.8353 | 0.455 | 0.8150 | 0.8260 | 1.35 |
| 159995 | 0.8774 | 0.8775 | 0.011 | 0.7600 | 0.8360 | 10.00 |
| 512330 | 1.4265 | 1.4268 | 0.021 | 1.2490 | 1.3740 | 10.01 |
| 512480 | 0.804 | 0.8039 | 0.012 | 0.6960 | 0.7660 | 10.06 |
| 512760 | 0.8674 | 0.8679 | 0.058 | 0.7530 | 0.8280 | 9.96 |
| 513550 | 1.0163 | 1.0105 | 0.574 | 0.9970 | 1.0080 | 1.10 |
| ... | | | | | | 19 more |

## Board numbers beyond the day's move, sources disagreeing

These are the rows where no date can be assigned from price: the two sources
differ by more than 1.0% of each other.

| code | board | sina | board/sina-1 % | prev | last | move% |
|---|---|---|---|---|---|---|
| 158901 | 0.9995 | None | nan | 0.9820 | 0.9940 | 1.22 |
| 158909 | 1.0049 | None | nan | 0.9620 | 0.9920 | 3.12 |
| 159537 | 0.6802 | 0.6689 | 1.689 | 0.5980 | 0.6580 | 10.03 |
| 159539 | 1.3617 | 1.3394 | 1.665 | 1.1960 | 1.3160 | 10.03 |
| 159540 | 1.4716 | 1.4475 | 1.665 | 1.2940 | 1.4230 | 9.97 |
| 159546 | 0.6088 | 0.532 | 14.436 | 0.5310 | 0.5840 | 9.98 |
| 159850 | 0.7401 | 0.7206 | 2.706 | 0.7220 | 0.7330 | 1.52 |
| 159920 | 1.3375 | 1.3057 | 2.435 | 1.3040 | 1.3250 | 1.61 |
| 510900 | 0.9452 | 0.9205 | 2.683 | 0.9230 | 0.9350 | 1.30 |
| 512220 | 0.9058 | 0.685 | 32.234 | 0.7940 | 0.8730 | 9.95 |
| 513210 | 1.3493 | 1.3174 | 2.421 | 1.3170 | 1.3390 | 1.67 |
| 513600 | 2.4686 | 2.4085 | 2.495 | 2.4110 | 2.4480 | 1.53 |
| 513800 | 1.7488 | 1.7219 | 1.562 | 1.7010 | 1.7350 | 2.00 |
| 560780 | 0.7925 | 0.6751 | 17.390 | 0.6740 | 0.7410 | 9.94 |
| 561980 | 0.5503 | 0.4686 | 17.435 | 0.4670 | 0.5140 | 10.06 |

- A row absent from this table was not compared, not "agreed".
- The judgement rests on the instrument's own traded price, not on either source's label.

