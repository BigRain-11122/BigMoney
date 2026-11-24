# QA evidence — money_shelf_placement (bm-c r2054)

Scope: one new face plus its two upstream reproductions. The charter's comp line is
`python -m smoke_test`, which could not be run this round (a peer host was writing shared
faces, so the round was restricted to new-file landings); these four legs are what can be
verified in isolation, and they are printed verbatim below rather than summarised.

## run — rc=0

```
wrote research/MONEY_SHELF_PLACEMENT.md (7340 bytes)
THE_SCREEN_PAYS_IN_PREMIA -> results/money_shelf_placement.json
  MOST_OF_THE_SHELF_IS_NOT_A_PARKING_SPOT / THE_GATE_PAYS
  17/59 admitted; screen pick 511770 (printed 8.44 -> realized 0.62); gate pick 511930 (2.65)
  phantom on the screen pick 44231 CNY/yr; the gate is worth 11498 CNY/yr on a 565246 CNY ticket
```

## check — rc=0

```
CHECK OK 59 money codes re-derived, 17 admitted, cutoff 2026-11-20
```

## selftest — rc=0

```
selftest 34/34 PASS
```

## negative controls — rc=0

```
  PASS L1 arithmetic lie -> rc3
  PASS L1 text says CHECK FAILED
  PASS L1 text does not say STALE
  PASS L2 upstream moved -> rc3
  PASS L2 text says STALE
  PASS L2 text names the file
  PASS L2 text does not say CHECK FAILED
  PASS L2 upstream restored byte-identical
  PASS L3 without the gate an equity tape is admitted
  PASS L3 without the gate the count rises
  PASS F1 face restored byte-identical
  PASS F2 final check rc0
negative controls 12/12 PASS
```

