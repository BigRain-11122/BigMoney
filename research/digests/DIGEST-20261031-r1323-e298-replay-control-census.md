# DIGEST 2026-10-31 r1323 (bm-b) -- E298: how many published controls can say which panel they used

**Question.** r1316 diagnosed E243's replay control as re-deriving over the live panel and reading
its own vintage as a reproduction failure. The repair added `window_used` / `window_source` /
`live_panel_last` / `sessions_past_the_pinned_window` to *that one block*. Nobody counted the class.

**Answer (arithmetic over published JSON only).** 90 dated faces under `results/state_tilt`
(67 `*_latest.json` mirrors and the census's own two faces excluded) carry **26 control blocks in 23
faces**:

| kind | n | what a vintage can do to it |
|---|---|---|
| identity check | 12 | nothing -- it re-derives from the face's own published records |
| replay of an upstream face | 14 | everything -- it depends on which panel it read |

Of the 14 replays, **7 declare their basis** (6 carry their own `window` / `pin` / `vintage` field;
1 names the live panel *and* its overshoot) and **7 publish no basis at all**:

```
ADDOS-2026-10-29.json              /e240_replay
AGGATT-2026-10-29.json             /designs/share_book_reproduction
BANDARRIVALATE-2026-10-29.json     /reproducibility
BANDPATH-2026-10-29.json           /focus_replay_of_e230_global_path
BANDPATH-2026-10-30.json           /focus_replay_of_e230_global_path
REPRO-2026-10-29.json              /reproduction
REPRO-2026-10-30.json              /reproduction
```

Those seven are published as **unmeasurable**, not as safe and not as broken: "cannot tell which
panel it used" is a different statement from "used the wrong panel", and collapsing the two would
either hide a real defect or convict a control that may be perfectly pinned.

**The repair is visible as a transition, not as a claim.** ADDOS published the same control path
twice and the basis moved `undeclared` (10-29) -> `live_declared` (10-30):

```
10-29: {"cell": "all_five", "tolerance": 1e-09, "status": "reproduced", "reproduced": true}
10-30: ... "window_used": {"first": "2020-11-17", "last": "2026-10-29"},
            "window_source": "e240_reference.window", "live_panel_last": "2026-10-30",
            "sessions_past_the_pinned_window": 1 ...
```

That is the only direct evidence in the tree that the r1316 fix landed rather than being described
in a digest: the block now says its window, where the window came from, and how many sessions the
live panel has grown past it.

**Two rules earned this round.**

1. **A path is not an identity.** Two vintages of one study carry the same control path, so keying
   the census (or the smoke join) on `path` alone silently collapses them and lets an at-risk row
   inherit the *other* vintage's basis. Rows now repeat their face and every join is on
   `(face, path)`; selftest L21 pins that a shared path is two controls. This is the E1280 family
   ("the table key must include the arm") arriving in a new file.
2. **A census that lives in the directory it scans must exclude itself.** The first run graded 26
   controls; the second run graded 27, because the face it wrote matched the dated-face pattern and
   entered its own scan -- so `verify` could never pass. `self_faces_excluded` is now published and
   asserted (L11), separately from `mirror_files_excluded`.

**Deliverables.** `scripts/e298_replay_control_census.py` (run / verify / selftest 21/21),
`results/state_tilt/REPLAYCENSUS-2026-10-30.json` + `replaycensus_latest.json`,
`Tools/s6_chain_bmb.py` leg `replay_control_census`, smoke leg E298 (standalone PASS),
knowledge card E298, pool E298 done + E303 seeded (recover the seven from the code that wrote them).