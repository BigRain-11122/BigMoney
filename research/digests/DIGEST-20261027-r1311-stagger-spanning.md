# r1311 — the staggered book's intercept, and the page that was not on the register

Window: 2026-10-27 16:25→ (bm-c). Machine id anchored from `fleet/machine.json` before
anything else; state `round_no=1310` at open, so this window executed r1311.

## Product 1 — the stagger arm on the same four-beta regression

r1301's verdict was "mechanism gain, not a strategy gain": the 6+6 clock split buys
−34 % turnover and −1.4 pp drawdown, and the published 20.77 % quote was retired as a
width artefact. That left exactly one open question: **is the intercept the same?** If it
is, the turnover saving is the only edge; if it is not, the clock split changes the book's
exposure and deserves its own test.

`scripts/etf_book_spanning.py` now prices both arms through one regression path
(`arm_from_returns`) and publishes them side by side. Configuration is read off the stagger
face's own artefact (`machinery` block) — never typed in.

| arm | CAGR | Sharpe | maxDD | alpha | alpha t | resid vol | R² |
|---|---|---|---|---|---|---|---|
| single sleeve (published card) | 9.62 % | 0.99 | −11.8 % | +5.85 %/yr | 1.94 | 7.7 % | 0.43 |
| staggered 6+6, offset 10 bars | 10.61 % | 1.07 | −10.4 % | **+6.77 %/yr** | **2.36** | **7.3 %** | 0.50 |

Window 2020-01-03..2026-10-27, 1646 paired days, close-t decision → open-t+1 fill,
10 bp/side, 8 % de-lever-only overlay, same universe and score.

Reading: the split clock pushes the intercept **over** a t of 2 (+0.92 pp/yr) where the
single sleeve does not clear it, with *lower* residual vol. That is a strategy difference,
not a free lunch — one arm over a threshold is a hypothesis. It also means r1301's
"turnover saving is the entire effect" is now too strong: the saving is real, but it is
not the whole difference. Next question is whether it survives a walk-forward refit and a
compare against the pre-2020 window (E148's request for the single sleeve).

Control: this window re-prices the *published* stagger book and asserts it (mine 10.61 %
vs published 10.41 %, Δ0.20 pp, tolerance 0.5 pp pinned in code). Without that assertion
an "arm" is just something that looks like the book (r1297's rule, now on its second face).

## Product 2 — the page a human reads was the one face outside the register

`etf_book_registry.py` listed four faces (ticket / card / forward / staggered); the CEO
one-page (`docs/live_book/`) was the fifth and was only checked inside smoke. Its lag was
therefore invisible in the artefact a reader actually opens. Registered as `ceo_page`,
derived from its own pointer → dated page, with `as_of` taken from **priced_bar** (not
`generated_for_date`: a page written today against yesterday's bar is current, one written
today against last week's bar is the r1290 failure).

Live register now, one screen:

```
trade              as_of       names  rule  in_chain
ticket             2026-10-27  5      beta  True
card               2026-10-27  12     vol   True
forward            2026-10-27  12     vol   True
staggered          2026-10-27  10     vol   True
ceo_page           2026-10-26  5      beta  True      <- one bar behind, writer=bm-a
```

The rule is read from the ticket the page *names*, not guessed from its name count; a
missing/unreadable reference is disclosed instead of defaulted.

## Defect found and fixed in-window — a GB-named key carrying a MiB number

Smoke red: `GPU face self-consistent on heartbeat` (free family spread 207 MiB). Two
faults, one root: `gpu_vram_free_gb` was on `FREE_KEYS` but not on `GB_KEYS`, so `apply()`
wrote **15099** into a key whose name promises GB, and `audit()` read it back as MiB — the
writer and the checker agreed with each other while the face said "15099 GB free" to any
reader who trusted the name. A second key (`gpu_free_vram_mb`) still carried an older
probe's 14877.

Fix: the unit is derived from the spelling (`key_unit()` → `gpu_mem_family()`), used by
both `fields_from()` and `_mb()`. `GB_KEYS` stays only as a fallback for keys the token
rule cannot classify. Selftest 28 → 30 legs, incl. "every GB-named key carries GB" and
"a MiB number under a GB name is caught, not agreed with". After apply: all five GB
spellings 14.7, audit 0 findings, 30 keys.

## Verification

- `etf_book_spanning.py --selftest` 23/23 (new: one regression path, identity control,
  planted +5 bp/day detected, short arm refused, three readings of two intercepts).
- `etf_book_registry.py --selftest` 36/36 (new: priced bar vs write day, rule from the named
  ticket, unreadable reference disclosed, page reaches the rendered register).
- `Tools/gpu_face.py selftest` 30/30; apply → audit clean.
- Smoke 89/91 → both reds repaired in-window (spanning selftest leg was my own failing leg;
  GPU face healed), full re-run below.

Artifacts: `results/etf_book_spanning.json` (schema v1, now carries `arms` +
`stagger_control`), `results/etf_book_registry.json`, `fleet/machines/bm-c.json`.