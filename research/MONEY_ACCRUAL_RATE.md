<!-- BEGIN:MONEY-ACCRUAL-RATE -->

# does the shelf's price accrue what the shelf says it carries

generated 2026-11-24T21:55:19+08:00 | evidence_cutoff **2026-11-20** | window 2020-07-16..2026-11-20

r2050 zeroed every bar more than 1% from its own trailing median and priced what survived;
r2051 measured what the band leaves behind and wrote its own blind spot into the file. Both
read a **sum of returns**. A sum cannot tell a price that accrues from a price standing above
par -- and the repair that forgives a premium's climb while zeroing its giveback (or the money
reader's reset rule, which zeroes the deepest givebacks outright) manufactures a rising line.

This face reads the **level**: each raw close is cut into 250-bar blocks, each block's 5th
percentile is taken, and a line is fitted through log(floor) against block index. A premium is
a minority of any block and cannot lift its floor; accrual lifts every block's floor.

- 59 rows, **28 measurable**: **1 price accrues**, **27 whose level did not move** (their
  price cannot show the income -- a distribution or a share count leaves this panel)
- verdict **THE_FLOOR_CANNOT_BE_MEASURED** on the accruing names only (median carried - floor = -0.1561 pp/yr)
- **THE_FLAT_NAMES_PRINT_NOTHING** · {"flat_names": 27, "flat_printing": 10, "flat_carried_median_pct": 0.1059, "worst": "511930", "worst_carried_pct": 2.6504}
- **SOME_FLAT_NAMES_HAVE_A_DISTRIBUTION_SHAPE** · {"names_with_3plus_drops": 14, "codes": ["511930", "511920", "511880", "511950", "511970", "511820", "511770", "511960"], "owner": "r2047 (cash_shelf_total_return_audit) owns the cash-income question; this face only says the price cannot answer it"}
- **THE_TWO_RULERS_SPLIT** · {"names_compared": 27, "names_split": 1, "split_codes": ["511880"]}
- **A_BOOK_LEG_PRINTS_CARRY_ITS_PRICE_CANNOT_SHOW** · {"legs": {"511880": {"klass": "LEVEL_DID_NOT_MOVE", "floor_accrual_pct": -0.0248, "cagr_repaired_pct": 1.4973}, "511360": {"klass": "PRICE_ACCRUES", "floor_accrual_pct": 2.4742, "cagr_repaired_pct": 2.3181}}, "legs_that_do_not_price": ["511880"]}

## the parking number

- best admitted price-accruing name: **511360 短融ETF海富通 par floor 2.47%/yr (13985.31 CNY/yr on the ticket's 565246 CNY cash) -- carried 2.32%/yr**
- the shelf's top name by carried is **511930 货币ETF国联 at 2.65%/yr -- class LEVEL_DID_NOT_MOVE, price floor 0.01%/yr**

## the table

<!-- ACCRUAL-TABLE:BEGIN -->
| code | name | admission | class | blocks | par floor %/yr | quiet drift %/yr | carried %/yr | printed %/yr | carried - floor (pp) |
|---|---|---|---|---|---|---|---|---|---|
| 511360 | 短融ETF海富通 | ADMIT | PRICE_ACCRUES | 5 | 2.47 | 2.02 | 2.32 | 2.32 | -0.16 |
| 511930 | 货币ETF国联 | ADMIT | LEVEL_DID_NOT_MOVE | 4 | 0.01 | 0.00 | 2.65 | 5.41 | 2.64 |
| 511920 | 货币ETF广发 | ADMIT | LEVEL_DID_NOT_MOVE | 5 | 0.00 | 0.00 | 1.88 | 4.34 | 1.88 |
| 511880 | 银华日利ETF | ADMIT | LEVEL_DID_NOT_MOVE | 6 | -0.02 | 1.49 | 1.50 | 1.53 | 1.52 |
| 511950 | 添利货币ETF广发 | ADMIT | LEVEL_DID_NOT_MOVE | 4 | -0.00 | 0.00 | 1.36 | 5.08 | 1.36 |
| 511970 | 国寿货币ETF | ADMIT | LEVEL_DID_NOT_MOVE | 4 | 0.01 | 0.00 | 0.73 | 5.25 | 0.72 |
| 511820 | 鹏华添利ETF | ADMIT | LEVEL_DID_NOT_MOVE | 5 | 0.00 | 0.00 | 0.72 | 2.48 | 0.72 |
| 511770 | 金鹰增益货币ETF | ADMIT | LEVEL_DID_NOT_MOVE | 4 | 0.01 | 0.00 | 0.62 | 8.44 | 0.61 |
| 511960 | 货币ETF嘉实 | ADMIT | LEVEL_DID_NOT_MOVE | 4 | 0.01 | 0.00 | 0.54 | 4.76 | 0.53 |
| 511910 | 融通货币ETF | ADMIT | LEVEL_DID_NOT_MOVE | 4 | 0.01 | 0.00 | 0.40 | 3.07 | 0.39 |
| 511600 | 华安日日鑫ETF | ADMIT | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | 0.34 | 3.25 | 0.33 |
| 511860 | 货币ETF博时 | ADMIT | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | 0.16 | 0.16 | 0.16 |
| 511980 | 货币ETF汇添富 | ADMIT | LEVEL_DID_NOT_MOVE | 5 | 0.00 | 0.00 | 0.16 | 0.82 | 0.15 |
| 511830 | 货币ETF华泰柏瑞 | ADMIT | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | 0.13 | 1.96 | 0.13 |
| 511900 | 富国货币ETF | ADMIT | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | 0.11 | 0.11 | 0.10 |
| 511670 | 华泰天天金ETF | ADMIT | LEVEL_DID_NOT_MOVE | 4 | 0.00 | 0.00 | 0.04 | 5.63 | 0.04 |
| 159001 | 货币ETF易方达 | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 511700 | 货币ETF平安 | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 511660 | 货币ETF建信 | ADMIT | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | 0.00 | 0.34 | -0.00 |
| 159005 | 快钱ETF汇添富 | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 6 | -0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 511810 | 货币ETF南方 | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | 0.00 | 0.00 | -0.00 |
| 511650 | 货币ETF华夏 | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 5 | 0.00 | 0.00 | 0.00 | 0.00 | -0.00 |
| 159003 | 招商快线ETF | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | -0.00 | -0.00 | -0.01 |
| 511690 | 交易货币ETF大成 | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | -0.00 | -0.00 | -0.00 |
| 511850 | 招商财富宝ETF | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 5 | 0.01 | 0.00 | -0.00 | -0.00 | -0.01 |
| 511800 | 易方达货币ETF | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | -0.00 | -0.00 | -0.00 |
| 511990 | 华宝添益ETF | REFUSE_FIXED_FACE | LEVEL_DID_NOT_MOVE | 6 | 0.00 | 0.00 | -0.01 | -0.01 | -0.01 |
| 511620 | 货币ETF国泰 | REFUSE_NEGATIVE_CARRY | LEVEL_DID_NOT_MOVE | 5 | 0.00 | 0.00 | -0.02 | 2.45 | -0.03 |
| 561420 | 300现金流ETF汇添富 | REFUSE_THIN | - | - | - | - | 43.17 | 139.92 | - |
| 159166 | 现金流ETF长城 | REFUSE_THIN | - | - | - | - | 26.05 | 93.32 | - |
| 560120 | 中证500现金流ETF华夏 | REFUSE_NOT_MONEY | - | - | - | - | 24.99 | 213.54 | - |
| 563620 | 全指现金流ETF兴业 | REFUSE_NOISY_TAPE | - | - | - | - | 23.33 | 119.51 | - |
| 159119 | 800现金流ETF招商 | REFUSE_THIN | - | - | - | - | 22.97 | 119.57 | - |
| 563900 | 300自由现金流ETF摩根 | REFUSE_NOT_MONEY | - | - | - | - | 22.17 | 106.84 | - |
| 563680 | 800现金流ETF汇添富 | REFUSE_NOISY_TAPE | - | - | - | - | 22.08 | 127.38 | - |
| 563990 | 800现金流ETF富国 | REFUSE_NOT_MONEY | - | - | - | - | 21.86 | 134.85 | - |
| 159276 | 现金流ETF汇添富 | REFUSE_NOISY_TAPE | - | - | - | - | 21.00 | 132.85 | - |
| 561870 | 现金流全指ETF华富 | REFUSE_NOT_MONEY | - | - | - | - | 20.56 | 129.04 | - |
| 159221 | 现金流ETF嘉实 | REFUSE_NOT_MONEY | - | - | - | - | 20.44 | 126.76 | - |
| 159223 | 现金流ETF永赢 | REFUSE_NOISY_TAPE | - | - | - | - | 20.13 | 132.87 | - |
| 563760 | 全指现金流ETF中银 | REFUSE_NOISY_TAPE | - | - | - | - | 20.13 | 119.85 | - |
| 512130 | 全指现金流ETF鹏华 | REFUSE_NOT_MONEY | - | - | - | - | 20.12 | 137.00 | - |
| 159229 | 自由现金流ETF广发 | REFUSE_NOT_MONEY | - | - | - | - | 20.11 | 128.98 | - |
| 159232 | 自由现金流ETF南方 | REFUSE_NOT_MONEY | - | - | - | - | 19.83 | 127.32 | - |
| 563390 | 全指现金流ETF华泰柏瑞 | REFUSE_NOT_MONEY | - | - | - | - | 19.73 | 120.30 | - |
| 159235 | 中证现金流ETF大成 | REFUSE_NOT_MONEY | - | - | - | - | 19.19 | 123.13 | - |
| 159399 | 现金流ETF国泰 | REFUSE_NOISY_TAPE | - | - | - | - | 18.89 | 97.19 | - |
| 159222 | 自由现金流ETF易方达 | REFUSE_NOT_MONEY | - | - | - | - | 18.82 | 130.18 | - |
| 563830 | 全指现金流ETF博时 | REFUSE_NOISY_TAPE | - | - | - | - | 18.67 | 127.45 | - |
| 561080 | 全指现金流ETF华安 | REFUSE_NOT_MONEY | - | - | - | - | 18.42 | 117.03 | - |
| 159201 | 自由现金流ETF华夏 | REFUSE_NOT_MONEY | - | - | - | - | 17.86 | 134.67 | - |
| 516460 | 现金流ETF800鹏华 | REFUSE_NOT_MONEY | - | - | - | - | 17.84 | 127.11 | - |
| 562080 | 300现金流ETF华宝 | REFUSE_NOT_MONEY | - | - | - | - | 17.76 | 110.09 | - |
| 159225 | 现金流ETF银华 | REFUSE_NOT_MONEY | - | - | - | - | 17.54 | 130.04 | - |
| 563580 | 自由现金流800ETF万家 | REFUSE_NOT_MONEY | - | - | - | - | 17.53 | 127.05 | - |
| 563780 | 现金流全指ETF方正富邦 | REFUSE_NOISY_TAPE | - | - | - | - | 16.87 | 119.21 | - |
| 159236 | 自由现金流ETF工银 | REFUSE_NOT_MONEY | - | - | - | - | 16.32 | 120.95 | - |
| 563770 | 全指现金流ETF招商 | REFUSE_NOT_MONEY | - | - | - | - | 16.26 | 116.38 | - |
| 159233 | 自由现金流ETF平安 | REFUSE_NOT_MONEY | - | - | - | - | 15.90 | 125.66 | - |
<!-- ACCRUAL-TABLE:END -->

## what this does not claim

- dividends are not in the price: every number here is price-only, as the shelf's are
- a share count and a cash distribution are both invisible to a price panel: when the level did not move this face has proved nothing about the fund's income
- a PERMANENT relabelled par leaks into the floor -- half the blocks stand higher forever
- 250 bars is a choice: a premium lasting longer than a year is a level to this ruler
- an unmeasured row is 'cannot answer', never zero

<!-- END:MONEY-ACCRUAL-RATE -->
