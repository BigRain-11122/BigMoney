# Premium vs the fund's own purchase channel -- 2026-11-10

**Answer (derived):** 5/5 legs show no open primary subscription anywhere in coverage; hard-suspended on their latest stamp: 513100; exchange-only on their latest stamp: 159501, 513690, 159577, 159263; closed channel is consistent with a standing premium, not a verdict on it

Ruler: panel close / the newest unit NAV stamped strictly before that close - 1. Status joined on: 申购状态 printed on the NAV stamp the premium used.

| leg | class | amount CNY | premium (NAV ruler) | board (price/IOPV) | ruler gap pp | stamp | 申购状态 on stamp | hard-suspended sessions | premium>=10% sessions | share closed at high | window verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 159501 | crossborder | 78,501 | +24.40% | +20.29% | +4.11 | 2026-11-06 | 场内买入 | 29 | 82 | 100% | CHANNEL_CLOSED_THROUGHOUT |
| 513100 | crossborder | 78,611 | +22.40% | +18.30% | +4.10 | 2026-11-06 | 暂停申购 | 679 | 163 | 100% | CHANNEL_CLOSED_THROUGHOUT |
| 513690 | crossborder | 78,588 | -0.78% | +0.12% | -0.90 | 2026-11-09 | 场内买入 | 64 | 0 | n/a | CHANNEL_CLOSED_THROUGHOUT |
| 159577 | crossborder | 78,504 | +12.07% | +9.48% | +2.59 | 2026-11-06 | 场内买入 | 58 | 2 | 100% | CHANNEL_CLOSED_THROUGHOUT |
| 159263 | equity | 78,522 | -0.54% | -0.14% | -0.39 | 2026-11-09 | 场内买入 | 0 | 0 | n/a | CHANNEL_CLOSED_THROUGHOUT |

## Within-leg contrast: hard-suspended vs exchange-only

| leg | verdict | median premium, 暂停申购 | median premium, 场内买入 | gap pp | n |
|---|---|---|---|---|---|
| 159501 | BLOCK_DOES_NOT_WIDEN | +1.50% | +1.28% | +0.22 | 29 / 796 |
| 513100 | BLOCK_WIDENS_PREMIUM | +5.04% | +0.54% | +4.50 | 679 / 1223 |
| 513690 | BLOCK_DOES_NOT_WIDEN | +0.50% | -0.02% | +0.52 | 64 / 1264 |
| 159577 | BLOCK_DOES_NOT_WIDEN | +1.18% | +1.79% | -0.60 | 58 / 600 |
| 159263 | NO_CONTRAST | n/a | +0.10% | n/a | 0 / 326 |

## What this face refuses to claim

* A closed channel is **consistent with** a standing premium; it does not make the
  premium fair, and it is not a sell signal. What it does establish is that the
  creation valve an arbitrageur would need was not listed as open on any session
  this face can see -- so 'the premium should already have been arbitraged away'
  is not an argument this data supports.
* The status word is as published on each NAV row; it is not a statement about
  creation limits, quotas, or how much would be accepted if it reopened.
* A same-session open state would falsify the hypothesis. None appears in coverage:
  the only words present are 场内买入 (exchange-only) and 暂停申购 (suspended).
* 'share closed at high' is a census, not a contrast: on a leg with no hard-suspended
  sessions it reads 100% by construction, because every session is exchange-only.
  The only column that carries a difference is the within-leg contrast above, and
  there it is printed as measured -- 159501 and 159577 come out flat or negative.
* The two premium columns are different quantities and are never added: this face
  divides the panel close by the disclosed unit NAV; the board divides price by
  intraday IOPV. The gap column prices how far apart those rulers sit on one session.
