import io

path = "knowledge/METHODOLOGY_ASSETS.md"
card = """
## E329 -- two vintages of one family: the choice has to be made by something, and only one shape in the tree makes it by order

E328 measured numbers sitting on a stale cut and assumed one file per source. A source can name two
cuts of the same stem: a `*_latest` pointer plus a pinned dated fallback, or two dated cuts side by
side. When it does, *something* picks, and the tree only has four ways to pick: a fallback chain
(first existing handle wins), a same-target rebound (the last assignment wins), separately named
targets (a role, not a race), or a plain ordered list where the order is presentational and nothing
is decided at all.

Population: 228 sources name a face, forming 597 (source, family) pairs. **9 name two vintages of
one stem** -- 8 with two dated cuts, 1 with a pointer pair; only **2 have both cuts on disk** (the
rest are fixtures that build their cuts in a tempdir). 2 pairs bind the cuts to separately named
roles, 4 have no static winner, **1 is a real fallback chain** -- and that chain's order is covered
by no selftest leg.

Reading (results/state_tilt/TWOVINTAGE-2026-11-01.json): `scripts/e242_omission_inflation_sweep.py`
resolves `_face_file(stem)` by trying `"%s_latest.json" % stem` first and falling back to a pinned
`"%s-2026-10-29.json" % stem`. Its four call-site stems are all served from the pointer today, so
nothing is stale **now**; but 2 of the 4 (owncross, sharediff) hold a `2026-10-30` cut beside the
pinned `2026-10-29` one, so the fallback branch would silently serve a cut its own family has
outgrown. `scripts/sscombo_pit_drift_audit.py` is the opposite shape and the safe one: it binds
`DEFAULT_ASOF = REGIME5-2026-09-30` and `DEFAULT_FRESH = REGIME5-2026-10-19` to names that say which
vintage plays which part, so the stale file cannot win by accident -- it is asked for by name.

Three rules had to be measured, not assumed. (a) **A stem is not case-stable on this disk**:
`OWNCROSS-2026-10-29.json` sits beside `owncross_latest.json`, so an exact-case index reported the
family as having no cuts at all and the exposure as zero -- the index had to become case-insensitive
before the measurement existed. (b) **An ordered container is not an order**: a loop over
`("AAA-2026-02-02.json", "REPLAYCENSUS-2026-02-02.json", "REPLAYCENSUS-2026-02-03.json", ...)` has
an order and decides nothing; only a container the source then probes with `os.path.isfile` is a
fallback chain, and folding the two together would have credited a fixture with a resolution rule.
(c) **One assignment of a tuple of cuts is not a rebound** -- the first classifier read
`NAMES = (a, b)` as the same target bound twice and printed a load-order winner for a tuple that has
no second assignment.

How to apply: when two references to a family are bound in one source, ask three questions in this
order -- is anything actually chosen (existence test / rebound), is the chooser's order pinned by a
leg, and is the losing branch still reachable? A named-role pair needs no test; a fallback chain
needs one, because its pinned branch is the one that fires in a tree where the pointer is missing,
and that is exactly the tree a stale checkout has.

Evidence: scripts/e329_two_vintage_binding.py (selftest 28/28, verify problems=[]) ->
results/state_tilt/TWOVINTAGE-2026-11-01.json + twovintage_latest.json; S6 leg two_vintage_binding
(~7s); smoke leg "product: every source that names two vintages of one family is classed by how the
choice is made, and the stale cut is measured on today's disk";
research/digests/DIGEST-20261101-r1349-e329-two-vintage.md
"""

with io.open(path, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(card)
print("appended", len(card), "chars")