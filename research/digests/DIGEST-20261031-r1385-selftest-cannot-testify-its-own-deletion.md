# r1385 bm-c — a selftest cannot testify to its own deletion; the witness has to be a consumer

**Date** 2026-10-31 · **Round** 1385 · **Machine** bm-c · **Dept** 研究/工程

## What was wrong

The window opened on a tree whose `scripts/etf_book_ceo_page.py` and
`scripts/etf_book_leg_attribution.py` were **one commit behind HEAD** (hash identity with
`1b0728461c:scripts/...`, exact blob match). Between them the `leg_split` feature was gone:

* `etf_book_leg_attribution.money_split_face` did not exist — the single implementation of
  "where in the day does this book's money accrue";
* `etf_book_ceo_page.render_md` no longer printed the section that quotes it;
* the three legs that guarded both (`L60`, `L61`, `L62`) had gone away **with** the feature.

Nothing was red. `python scripts/etf_book_ceo_page.py selftest` on those exact stale bytes
prints `Summary: 62/62 PASS` (rc 0) — measured over the legs that still exist. The only
visible trace was in the artifact: the regenerated live page had lost 19 markdown lines and
66 json lines, i.e. the CEO's page quietly stopped telling him which part of the day the
money is earned in.

The blast radius was one `git add -A` wide: r1384's closeout would have committed the revert,
which is the r609 law (a stale tree face replayed over a healthy one) in its commit-side form.

## What r1385 did

1. **Diagnosed by hash, not by opinion**: `git hash-object <path>` vs
   `git rev-parse <candidate>:<path>` across `HEAD`, `HEAD~2`, `HEAD~5`, `HEAD~10` — `HEAD~5`
   matched, so this was a restore artefact and the files were re-derived from `HEAD`
   (`git checkout --`), along with the two published page files that had been regenerated
   from the stale code. Verified `git diff` zero on all four.
2. **Moved the witness outside the thing it watches** — a new smoke leg
   `product: the CEO page still prints where in the day the money is earned`:
   * renders the page with a fixture `leg_split` face and requires the section heading, the
     four buckets, the quiet-bar count and the one-sentence reading to reach the reader;
   * renders it with `status="broken"` and requires `无法核验` **and no bucket numbers**;
   * loads the live artifact, requires `status="ok"`, then perturbs one bucket by +5.0 and
     requires the reader to REFUSE it (`status="broken"`, no arms).
   Deleting the section from `render_md` or deleting `money_split_face` turns this leg red
   although its own body is untouched — which is precisely what L60-L62 could not do.
3. **Proved the leg against the real incident, not a hand-made one**: the actual stale blobs
   were loaded from git (`scripts/_r1385_stale_pg.py` / `_r1385_stale_la.py`, then removed)
   and run through the leg's own assertions: `money_split_face` absent, tokens
   `[False, False, False, False]`, while the stale file's own selftest still says 62/62 PASS.

## Verification

| Check | Result |
|---|---|
| `smoke_test.py` full suite | see round report (new leg is one more than r1384's 280) |
| `scripts/etf_book_ceo_page.py selftest` | **65/65 PASS** (62 stale + the 3 restored legs) |
| `scripts/etf_book_leg_attribution.py --selftest` | **SELFTEST OK (0 fails)** |
| `scripts/etf_book_leg_attribution.py --check` | FACE-OK 2026-10-30 (3 arms, production 8.21pp/yr) |
| Page build on this host | `leg_split.status=ok`, section present, 0.79 s |
| `git diff` on the four restored paths | 0 |
| `Tools/card_text_hygiene.py scan` | 414 files, 0 control characters |
| `python -m Tools.card_ledger_guard` | CLEAN, max 309→**310**, lost=[] |

## Reusable rule (card E310)

A selftest cannot testify to its own deletion: `N/N PASS` is computed over the legs that
exist, so removing a leg is always a silent success. Durable witnesses are consumer-side —
render the product and look for what the reader was promised, and hand the reader an input
that must be refused. And when a tree disagrees with `HEAD`, settle it with blob hashes
before forming a theory: stale is not intent, and `add -A` is how stale becomes shipped.