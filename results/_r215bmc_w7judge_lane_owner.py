# -*- coding: utf-8 -*-
"""r215 bm-c W7-JUDGE lane_owner amendment (null -> "bm-b").

Laws applied:
  - r201 车道门修法 data-level leg: pool entries whose runner data face
    is physically single-machine MUST carry lane_owner=<that machine>
    (autofill F-08/R31/R65 lane guard: lo not in (None, "", "ANY", myid)
    -> skip -- Tools/autofill.py L797).
  - W5-JUDGE precedent: TRIAL-LABOR-W5-JUDGE lane_owner="bm-b" for the
    same Money02 t18_deep_panel dependency; .gitignore L9
    "Money02/data/*" = cache never travels via git = physical-only-bm-b.
  - W6/W7 mirror pair: W6-JUDGE (lane_owner None) cost one 20-min
    dead-hand window (bm-c 06:58 cache-less crash -> bm-b 07:20 retake);
    W7-JUDGE (lane_owner None) cost one 20-min dead-hand window
    (bm-c 11:30:05 staleness takeover -> P5C-GATE cache-less instant
    exit -> crash-fuse fix-first refusal -> bm-b retake window
    11:50:05+). This amendment closes the live risk of bm-a (also
    cache-less) claiming the shard in the 11:50:05+ stale window and
    burning a THIRD 20-min dead-hand window before bm-b converges.
  - W6 no-manual-release law: shard owner stamp (owner=bm-c since
    11:30:05) is LEFT UNTOUCHED -- bm-b's staleness retake path is
    unchanged; this edit only restricts FUTURE claims to bm-b.
"""
import json
import os

POOL = "results/runnable_pool.json"
pool = json.load(open(POOL, encoding="utf-8-sig"))

# ---------- three-way verification (precedent vs gap vs physical face)
w5 = [x for x in pool["entries"] if x["id"] == "TRIAL-LABOR-W5-JUDGE"][0]
assert w5["lane_owner"] == "bm-b", w5["lane_owner"]          # precedent
ent = [x for x in pool["entries"] if x["id"] == "TRIAL-LABOR-W7-JUDGE"][0]
assert ent["lane_owner"] in (None, "", "ANY"), ent["lane_owner"]  # the gap
assert ent["status"] == "ready", ent["status"]
sh = ent["shards"][0]
assert sh["key"] == "judge-0of1" and sh["status"] == "ready", sh
assert sh["owner"] == "bm-c", sh                             # my dead-hand
assert sh["owner_since"] == "2026-09-29 11:30:05", sh
src = open("scripts/p5c_virtual_timepoint.py", encoding="utf-8").read()
assert ('LEG_D_CACHE = os.path.join("Money02", "data", "cache", '
        '"t18_deep_panel", "ohlcv")') in src
gi = open(".gitignore", encoding="utf-8").read()
assert "Money02/data/*" in gi          # cache never travels via git
assert not os.path.isdir(os.path.join(
    "Money02", "data", "cache", "t18_deep_panel"))  # bm-c cache-less
print("three-way OK: W5 lane_owner=bm-b precedent | W7 null gap "
      "confirmed | LEG_D_CACHE=Money02 t18 gitignored + absent on bm-c")

# ---------- amendment (entry metadata only; shard stamp untouched)
ent["lane_owner"] = "bm-b"
ent["data_gates"] += (
    " | r215 bm-c lane_owner amendment null->bm-b (W5-JUDGE precedent: "
    "same Money02 t18_deep_panel physical-only-bm-b data face, "
    ".gitignore Money02/data/* = cache never via git; W6 r414 + W7 r214 "
    "cache-less crash-cycle mirror pair each cost one 20-min dead-hand "
    "window; prevents bm-a cache-less claim in the 11:50:05+ stale "
    "window; shard owner stamp untouched = no manual release, bm-b "
    "staleness retake path unchanged)")

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)

# ---------- re-read verify
pool2 = json.load(open(POOL, encoding="utf-8-sig"))
j2 = [x for x in pool2["entries"]
      if x["id"] == "TRIAL-LABOR-W7-JUDGE"][0]
assert j2["lane_owner"] == "bm-b", j2["lane_owner"]
assert j2["status"] == "ready"
assert j2["shards"][0]["owner"] == "bm-c"          # dead-hand stamp intact
assert j2["shards"][0]["owner_since"] == "2026-09-29 11:30:05"
w5b = [x for x in pool2["entries"]
       if x["id"] == "TRIAL-LABOR-W5-JUDGE"][0]
assert w5b["lane_owner"] == "bm-b"                 # precedent untouched
print("re-read verify OK: W7-JUDGE lane_owner=bm-b | shard owner=bm-c "
      "stamp intact | W5 precedent intact")
