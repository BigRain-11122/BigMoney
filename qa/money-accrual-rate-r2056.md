# QA evidence -- scripts/money_accrual_rate.py (r2056 bm-c)

## 1. baseline

```
run rc=0
saved results/money_accrual_rate.json | THE_FLOOR_CANNOT_BE_MEASURED | median -0.1561 | accrues 1 level did not move 27 of 59
saved research/MONEY_ACCRUAL_RATE.md (rewritten, 8.1 KB)

check rc=0
check ok: 59 rows (28 measurable: 1 accrue / 27 level did not move), verdict THE_FLOOR_CANNOT_BE_MEASURED, median -0.1561 pp, doc verbatim
```

## 2. control A: one row's floor moved by +0.90pp

```
rc=1
check FAILED:
  - 511930: floor_accrual_pct 0.9095 != re-derived 0.0095
  - doc table is not the face's table
```

- verdict: PASS (FAILED without STALE)

## 3. control B: one byte appended to results/money_shelf_placement.json

```
rc=3
check STALE: this face was written against inputs that have since moved:
  - results/money_shelf_placement.json moved since this face was written
rerun: python scripts/money_accrual_rate.py run
```

- verdict: PASS (STALE without FAILED)

## 4. restored

```
check rc=0
check ok: 59 rows (28 measurable: 1 accrue / 27 level did not move), verdict THE_FLOOR_CANNOT_BE_MEASURED, median -0.1561 pp, doc verbatim

selftest rc=0
selftest: 17/17 PASS
```

- verdict: PASS

## 5. summary

- all controls as designed: **YES**
