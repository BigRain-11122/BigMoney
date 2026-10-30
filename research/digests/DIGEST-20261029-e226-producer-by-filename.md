# E226 — the coverage audit keyed on a study literal, not on the face (r1338 bm-c)

**Card:** E226 in `knowledge/METHODOLOGY_ASSETS.md`.
**Code:** `scripts/e97_routing.py` — selftest 128 → 129 (new leg L37b), producer lookup gained
a filename-witness fallback.
**Was:** the only red in the full suite (`smoke 203/204`), `e97 selftest 127/128`.

## The red

```
[FAIL] product: e97 sign-growth gate (crossing detection contract) | exit=1 | selftest: 127/128
FAIL L37 on the real disk every quoting face has a producer and E177 joins resolve
```

The leg's own reading named two faces with no producer:

| face | study string |
|---|---|
| `results/e43_tilt_4member/LADDERDROPCARRIER-20261027.json` | `E196 carrier-month identifiability` |
| `results/e43_tilt_4member/LADDERDROPCURVE-20261027.json` | `E190 ladder-drop fragility curve` |

Neither producer is missing — `run_tilt3ladderdropcarrier` and
`run_tilt3ladderdropfragility` both exist in `scripts/e39_panel_census.py` and both wrote the
files. The audit builds its producer index by matching each face's `study` value against string
literals of the form `"e190_*"` inside a `def`. E190 and E196 publish **human titles**, so the
key the audit looks for is not in the source and the faces read as orphaned.

## What changed, and the trap the first draft fell into

`producer_index_by_filename` indexes the writer's output-filename literal instead. The first
version was wrong in a way that would have been invisible: the literal sits in the mode dispatch,
so the owning def came back as `main`, and `main` reaches every arithmetic helper in the module —
the face would have silently inherited "producer uses daily terms" and been relabelled.

So the fallback resolves through the call: when the owner is `main`, walk back to the nearest
`run_*` call on that dispatch branch (≤ 4 lines). Reading now:

- `LADDERDROPCARRIER` → `run_tilt3ladderdropcarrier`
- `LADDERDROPCURVE` → `run_tilt3ladderdropcurve` + `run_tilt3ladderdropfragility` (two writers
  share the prefix; the set is published rather than one being guessed)

`unindexed=[]`, `faces_quoting_derived_without_offset=0`. The leak count did not move, so this is
coverage restored, not an assertion relaxed. No face's `study` string was renamed to make the
audit happy.

## Leg L37b

Asserts the carrier face resolves to its writer, that `main` is never the producer, and that the
curve face resolves to the fragility writer — the three ways this fix can regress.