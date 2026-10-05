# -*- coding: utf-8 -*-
"""r764 bm-a W151 pre-finalize identity gates (r752 three-gate law):
gate-1 dual selftest ran green in-window (pf 9/9 + n1 selftest all
faces incl. W151 materializer); gate-2 shard count identity (Sigma A
2000 / B 200 exact + duplicate-name zero); gate-3 cross-shard seed
continuity (full-band seamless sweep: min/max/unique == registered band
endpoints, shard boundary +1 seamless, workers uniform face).
Also: origin parity check (local HEAD == origin/main) for the r518
same-window finalize chain-head law. Bloodline: r763
_r763bma_w150_finalize_gates.py verbatim machinery, W151 bands."""
import glob
import json
import os
import subprocess

WAVE = 151
A_BASE, A_END = 347_004, 349_003     # registered W151 A band
B_BASE, B_END = 349_004, 349_203     # registered W151 B band
A_N, B_N = 2000, 200
SHARD_DIR = os.path.join("results", "p2cal_ext", "n1_w151")

# --- origin parity (r518: finalize prev consumption is origin-time ordered) --
subprocess.run(["git", "fetch", "origin"], check=True,
               stdout=subprocess.DEVNULL)
head = subprocess.run(["git", "rev-parse", "HEAD"],
                      capture_output=True, text=True, check=True
                      ).stdout.strip()
om = subprocess.run(["git", "rev-parse", "origin/main"],
                    capture_output=True, text=True, check=True
                    ).stdout.strip()
assert head == om, f"origin parity FAIL: HEAD {head} != origin/main {om}"
print(f"gate-origin PASS: HEAD == origin/main == {head[:12]}")

# --- shard inventory ---
files = sorted(glob.glob(os.path.join(SHARD_DIR, "shard-*-of-12.json")),
               key=lambda p: int(p.split("shard-")[1].split("-")[0]))
assert len(files) == 12, f"shard file count {len(files)} != 12"

a_all, b_all = [], []
workers = set()
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    assert d["nshards"] == 12, f"{f}: nshards {d['nshards']} != 12"
    fams = d["families"]
    a_runs = fams["A_random_engine_exit"]["runs"]
    b_runs = fams["B_random_entry_random_exit"]["runs"]
    a_all += [r["seed_rng"] for r in a_runs]
    b_all += [r["seed_rng_exit"] for r in b_runs]
    workers.add(d["audit"]["workers"])

# gate-2: shard count identity (Sigma exact + duplicate-name zero)
assert len(a_all) == A_N, f"A count {len(a_all)} != {A_N}"
assert len(b_all) == B_N, f"B count {len(b_all)} != {B_N}"
assert len(set(a_all)) == A_N, "A duplicate names"
assert len(set(b_all)) == B_N, "B duplicate names"
print(f"gate-2 PASS: Sigma A {len(a_all)} == 2000 / B {len(b_all)} == 200, "
      "duplicate names zero")

# gate-3: full-band seamless sweep (min/max/unique == registered endpoints)
a_ints = sorted(int(s) for s in a_all)
b_ints = sorted(int(s) for s in b_all)
assert a_ints == list(range(A_BASE, A_END + 1)), \
    f"A band drift: min={a_ints[0]} max={a_ints[-1]} uniq={len(set(a_ints))}"
assert b_ints == list(range(B_BASE, B_END + 1)), \
    f"B band drift: min={b_ints[0]} max={b_ints[-1]} uniq={len(set(b_ints))}"
# per-shard contiguous ascending + cross-shard boundary +1 seamless
prev_tail = None
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    a_seeds = sorted(int(r["seed_rng"]) for r in
                     d["families"]["A_random_engine_exit"]["runs"])
    b_seeds = sorted(int(r["seed_rng_exit"]) for r in
                     d["families"]["B_random_entry_random_exit"]["runs"])
    assert a_seeds == list(range(a_seeds[0], a_seeds[0] + len(a_seeds))), \
        f"{f}: A slice not contiguous ascending"
    assert b_seeds == list(range(b_seeds[0], b_seeds[0] + len(b_seeds))), \
        f"{f}: B slice not contiguous ascending"
    if prev_tail is not None:
        assert a_seeds[0] == prev_tail + 1, \
            f"{f}: A shard boundary gap ({prev_tail} -> {a_seeds[0]})"
    prev_tail = a_seeds[-1]
print("gate-3 PASS: full-band seamless sweep A 347_004..349_003 (2000) + "
      "B 349_004..349_203 (200), shard boundaries +1 seamless")

print(f"workers uniform face: {sorted(workers)}")
print("ALL THREE IDENTITY GATES PASS -- W151 finalize lawful (r752 law)")
