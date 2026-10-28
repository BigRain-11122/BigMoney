# DIGEST 2026-10-29 · E198 — the review window does not exist outside the family

Round r1332 (bm-c). Face: `results/reviewwindow_cross/REVIEWWINDOWCROSS-20261028.json`
(mode `reviewwindowcross` in `scripts/e39_panel_census.py`, selftest 682→689).
Card: E198. Upstream: E196 (`LADDERDROPCARRIER-20261027.json`).

## The question

E196 closed with a sentence that was only half usable: *no era claim from the
ladder-drop family may be quoted without naming the month it rests on*. It could
name the month (three distinct carrier months, all inside {6,7,12,1}), but it
had evidence on **two disjoint eras**, and it could not say whether the calendar
label was a **market mechanism** (a scheduled index review reshuffles relative
performance) or **this family's naming** (four cells, three months, nothing).

## What was measured

A panel the ladder-drop family never touched, with the *same* statistic.

- 20 declared ETF codes (declared in the module before any file is read), each
  month's return minus `510300`'s return; cell statistic = mean standardised
  |gap| inside vs outside the window, permutation p within the cell.
- 17 cells measured (2 files absent: `510880`, `510180` — published as
  `missing_files`, **not** replaced by other names), 80 monthly returns each
  (2020-01→2026-09; `588000` has 70), 1,350 member-months pooled.
- Three window definitions, all published: the full 4-of-12 window reused from
  E196, the strict review months {6,12}, and the spill months {7,1}.

## Reading

| reading | p | in/out ratio |
|---|---|---|
| pooled, 4-month window | **0.1885** | 1.148 |
| pooled, strict review {6,12} | 0.41975 | 0.986 |
| pooled, spill {7,1} | 0.126 | 1.251 |
| cross-sectional dispersion, 4-month | 0.36975 | 1.074 (26 in / 54 out) |

- **Cell hits: 3 of 17** at p≤0.10 (`510500` 0.093, `159919` 0.015, `159928`
  0.025). Chance alone would throw **1.7**; binomial tail **0.238**. Three hits
  is not better than chance.
- One cell points the other way hard: `510310` ratio **0.197** — its window
  months are *quieter* than the rest, which a market-wide mechanism would not
  produce.
- Verdict (frozen rule, recomputed by the gate): **`no_outside_family_signal`**.

## The sentence that changes

E196's calendar coincidence is **this family's naming, not a market mechanism**.
So the ladder-drop family gets no calendar waiver: the carrier month can still
be flagged at month-close, but "it happened in a review month" is not evidence
that anything was scheduled, and no era-level claim from that family is quotable
on calendar grounds.

## What this does not say

1. Cross-section on one timeline ≠ disjoint eras: 17 cells share 80 months, so
   the pooled p treats correlated members as separate evidence — which is why
   the verdict also required the per-cell count that chance explains.
2. Monthly ETF-vs-benchmark relative return is not the family's
   book-vs-benchmark level gap; a window effect here would have been a mechanism
   for relative performance, not a licence for the family's arithmetic.
3. 2020-01→2026-09 is one regime (26 window months), and the basket is 17 named
   funds with local files — not a random sample of the ETF universe.

## Cost note

RAM free 0.4–1.2 GB of 23.9 GB all round (CEO desktop); the leg itself is ~2 s
because it reads 20 CSVs and never loads a panel. The full smoke suite run this
window started before the new leg existed and is reported as such.