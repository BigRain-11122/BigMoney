# DIGEST 2026-11-03 r1249 bm-a — a check that re-derives from its own rows is green on any panel

Round pointer inherited from r1248 (note 3): *"exposure_timing / ladder and sleeve_paths sat on
10-30 with green checks, and three smoke legs went red on the page/face mismatch. That stamp gate
is NOT written yet (next round's first pointer)."*

## What was wrong

Three book faces publish their verdict by re-deriving it from the rows they themselves wrote:

| face | `--check` asked | could not see |
|---|---|---|
| `etf_book_exposure_timing` | does the published verdict follow from `arms`/`placebo.rows`, and does the production arm reproduce the engine's nav | which panel those rows were measured on |
| `etf_book_exposure_ladder` | does `criteria` match the module, do the phases reproduce | same |
| `etf_book_sleeve_paths` | does every path judgement / the face verdict / the answer sentence follow from `paths` | same |

Every one of them already wrote `panel.digest` (the content hash of the full repaired panel, the
same value the card prints) — and nothing read it back. So a face left on the 2026-10-30 panel was
green forever, while the book, the ticket and the page priced 2026-11-03.

Two additional defects surfaced while wiring the gate:

1. `etf_book_exposure_ladder` was **not in the chain table at all** (`Tools/s6_chain_bmc.py`).
   Its artifact existed only because a session had run it by hand — so nothing checked it and
   nothing could rebuild it.
2. A `--check` on an absent artifact died with `FileNotFoundError` (rc 1, no words). The chain's
   refresh arm keys on the leg's *output* (`stale` / `face missing`), so that death looked like a
   verdict failure and nothing rebuilt it (r1241 family).

## What was built

One implementation, in the module that already owns the digest (`etf_book_forward.build_inputs`):

* `panel_stamp(load=True)` — the live panel's `{digest, last_bar, bars_named, first_bar}`.
* `check_panel_stamp(doc, stamp=None, label="")` — rc 0 = the face priced the panel it says;
  rc **2** = the panel moved, message contains `stale` so the runner's refresh arm fires.
  rc 1 is deliberately not used: a moved world is not a verdict disagreement, and rebuilding
  must never be able to launder one.
* `check_face_inputs(path, label="")` — an absent / unreadable face says `FACE MISSING … stale`
  and returns 2 (rebuild) instead of a traceback.

All three faces call both at the top of `check()`; the ladder leg was added to the chain with its
refresh command.

## What it costs

`panel_stamp` loads the panel once per `--check` (~21 s measured: `build_inputs` 20.6 s on the
5,272 × 1,618 panel). Three legs = ~60 s per chain run. That is the price of asking a question the
face's own rows cannot answer; the alternative (compare against *another face's* stamp) is the same
defect one level up — two stale faces agreeing.

## Verified

* `scripts/etf_book_forward.py --selftest` — 5 new legs, SELFTEST OK: live stamp passes; an older
  stamp returns 2 (not 1); a face with no stamp returns 2; an unreadable live panel reads as
  *unknown*, not *moved* (rc 0); an absent face returns 2 with `FACE MISSING`.
* Real faces on the live panel: `etf_book_exposure_timing --check` rc 0
  (`AVERAGE_EXPOSURE_ONLY`, timing −0.91pp), `etf_book_exposure_ladder --check` rc 0
  (`CONSTANT_LADDER_DOMINATES`, best fixed 0.70, 3/4 phases), `etf_book_sleeve_paths --check`
  rc 0 (15 paths, `NO_GATE`).
* Fixtures: the same three artifacts with `panel.digest` rewritten to `0ld0dead` return rc 2 from
  each `check()` and the message contains `stale` — i.e. the runner would rebuild them.
* Smoke leg: *"a book face cannot be green on a panel it no longer measures"*.
* Chain table now holds a check **and** a refresh command for all three names.

## Card

`knowledge/METHODOLOGY_ASSETS.md` E372.