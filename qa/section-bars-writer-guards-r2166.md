# r2166 bm-c — the CEO page's last two unowned sections get named owners, and one of their producers learns to answer in 1.5s

## What the smoke suite had been saying

`product: the CEO page's sections each name the bar they were priced on` was red on three rounds
with two names:

```
section 'bets' is behind the page and no chain leg re-runs it;
section 'derisk' is behind the page and no chain leg re-runs it
```

`results/live_book_section_bars.json` agreed: `n_no_writer = 2`, `no_writer = ['bets','derisk']`,
both on bar 2026-11-25 while the page head said 2026-11-26.

## Diagnosis (both halves were wrong in different ways)

1. **The chain legs exist.** `etf_book_bets_face` has been in `LEGS` since r1275-era wiring
   (`L760`) and `derisk_rule` / `derisk_rule_write` since r1917. The smoke leg's own message
   ("no chain leg re-runs it") was therefore wrong about the world.
2. **The name probe could not see either.** `guarded_by()` matches a section key against leg
   names only when the key is ≥ `MIN_NAME_FOR_MATCH` (8). `bets` is 4 characters, `derisk` is 6,
   and neither section carries an `artifact` field, so `probes_for()` returned `[]` for both and
   the probe answered "nothing matches" about two faces that do get re-run. This is the r1623
   lesson in its other direction: an empty `guarded_by` is a *claim*, and here it was false.
3. **One of the two producers really was unable to answer cheaply.** `etf_book_derisk_rule.check`
   opened with `F.check_panel_stamp()`, which calls `panel_stamp()` → rebuilds the panel →
   **46.9 s measured today**. A check that costs 47 s is a check nobody wires into a 10-minute
   loop; that is why the face sat at 03:25 (its `run` leg) while its `check` leg was expensive
   and answered only "the digest moved".

## The fix

| file | change |
| --- | --- |
| `scripts/etf_book_forward.py` | new `panel_last_bar()` — newest date across the frozen core48 CSVs, **0.28 s** measured — and `check_panel_bar(doc, label)`, which returns 0 / 2 / `None` |
| `scripts/etf_book_derisk_rule.py` | `run()` publishes `inputs.panel_last_bar`; `check()` asks the cheap question first (1.5 s) and only pays `check_panel_stamp()`'s ~47 s when the face never recorded a bar (`None`) |
| `scripts/live_book_section_bars.py` | `LEG_ALIASES["bets"] = ["etf_book_bets_face"]`, `LEG_ALIASES["derisk"] = ["derisk_rule"]` — names written down, held against the live leg list by the L21 selftest |
| (reverted) | an `etf_book_derisk_rule` leg I added to `Tools/s6_chain_bmc.py` before finding `derisk_rule`/`derisk_rule_write` already there — removed the same round, not shipped |

## Evidence

> `results/_r2166bmc_derisk_bar_probe.py` is a one-shot probe left on disk, not committed:
> `.gitignore` rule `_r[0-9]*` is the birth gate for scratch probes (r1081). The behaviour it
> proves is pinned in git by `etf_book_derisk_rule.py`'s selftest L14, which needs no panel.

```
$ python scripts/etf_book_derisk_rule.py selftest
selftest 48/48            (L14 new: same bar -> 0, moved bar -> 2 with the word `stale`, no bar -> None)

$ python results/_r2166bmc_derisk_bar_probe.py     (real published face, restored byte-for-byte)
PASS pinned to the live bar is green                      | check 0 in 1.5s
PASS and it answers cheap (47s digest gate skipped)       | 1.5s
PASS an old bar is STALE, not a defect                    | "priced 1999-01-01, the live panel is 2026-11-26"
PASS the published face is restored byte-for-byte         | 38b86f4f0a575720
PASS the published face as it stands (recorded)           | STALE (old face predates the anchor)
5/5

$ python Tools/s6_chain_bmc.py --only=derisk_rule_write,derisk_rule
  0 derisk_rule_write     89.1s
  0 derisk_rule            1.5s CHECK_OK rules=5 answer=NO_RULE_CLEARS_BOTH
chain: 2/2 rc0  (90.8 s)

$ python scripts/live_book_section_bars.py --selftest   ->  58/58 PASS (incl. L21 alias-vs-live-legs)
$ python scripts/live_book_section_bars.py run          ->  n_no_writer = 0
    bets 2026-11-25 ['etf_book_bets_face'] chain_leg
    derisk 2026-11-25 ['derisk_rule']       chain_leg

$ python scripts/chain_contract_word_audit.py check     ->  {"ok": true, "n_current": 16}
```

The derisk face was rebuilt on the live panel by its own write leg:
`evidence_cutoff 2026-11-26`, `inputs.panel_last_bar 2026-11-26`, answer still
`NO_RULE_CLEARS_BOTH` (five priced rules, none clears both gates — unchanged reading, now
re-derived on today's panel).

## What is still behind, and it is a data lane, not a missing writer

Both sections now read 2026-11-25 because the **CEO page** has not been re-rendered since the
derisk face moved to 11-26; the page is the section's source of record. That is the page
leg's job (`etf_book_ceo_page`), which runs later in the same chain — the smoke leg will show
them on the headline bar once it does. They are labelled `chain_leg` now, so the "no chain leg
re-runs it" red is gone regardless of which bar they sit on.

## Cost note

`derisk_rule.check` went from **51.4 s to 1.5 s** per chain pass (the only remaining expensive
call is the writer's own 89.1 s rebuild, paid once per moved panel). At 144 chain passes a day
that is roughly 10 minutes of CPU a day returned, and — more to the point — a probe that can
now say "the panel moved" before it spends the money to say it.
