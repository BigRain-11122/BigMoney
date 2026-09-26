# -*- coding: utf-8 -*-
"""R262 bm-b: wave-2 finisher -- reconstruct stages from commit objects
(78ccb81c = bm-a closeout, c7df0465 = my wave-1-rebased replay commit),
adjudicate the 7 remaining files take-new by real ts, then verify the whole
tree has zero conflict markers."""
import io
import json
import subprocess

A = "78ccb81c"      # bm-a closeout (origin/main)
M = "c7df0465"      # my wave-1-rebased commit (replay source)


def side(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def deep_ts(d):
    if not isinstance(d, dict):
        return None
    for k in ("ts", "updated", "generated", "generated_at", "as_of"):
        v = d.get(k)
        if isinstance(v, str) and v:
            return v
    for sub in ("meta", "latest"):
        s = d.get(sub)
        if isinstance(s, dict):
            for k in ("ts", "updated", "generated", "generated_at"):
                v = s.get(k)
                if isinstance(v, str) and v:
                    return v
    return None


FILES = ["results/daily_scorecard.json",
         "results/fundamental_b_layer_filter.json",
         "results/futures_update_status.json",
         "results/heat_update_status.json",
         "results/lhb_update_status.json",
         "results/token_usage.json",
         "results/update_status.json"]
for p in FILES:
    ra, rm = side(A, p), side(M, p)
    assert ra and rm, f"stage reconstruction failed for {p}"
    da = json.loads(ra.decode("utf-8-sig"))
    dm = json.loads(rm.decode("utf-8-sig"))
    if p == "results/daily_scorecard.json":
        # ts-less deterministic face BY DESIGN (no wall-clock field) --
        # take bm-a's: their derivation basis is fresher (their 17:2x
        # post_review reviewer run feeds post_review_latest); next round's
        # idempotent S6 leg regenerates it anyway
        io.open(p, "wb").write(ra)
        json.loads(io.open(p, encoding="utf-8-sig").read())
        print(f"{p}: ts-less deterministic face -> take bm-a (fresher "
              f"derivation basis; S6 regenerates idempotently)")
        continue
    ta, tm = deep_ts(da), deep_ts(dm)
    assert ta and tm, f"ts probe failed {p}: {ta} {tm} keys={list(da.keys())[:8]}"
    win, tw = (A, ta) if ta >= tm else (M, tm)
    io.open(p, "wb").write(side(win, p))
    json.loads(io.open(p, encoding="utf-8-sig").read())
    print(f"{p}: take {'bm-a' if win == A else 'mine'} ({ta} vs {tm})")

# ---- whole-tree conflict-marker scan (working tree) ----
r = subprocess.run(["git", "grep", "-l", "-E",
                    r"^(<<<<<<<|=======$|>>>>>>>)", "--", "."],
                   capture_output=True)
print("marker-scan hits:", r.stdout.decode() or "(none)")
assert not r.stdout.strip(), "CONFLICT MARKERS REMAIN IN TREE"
print("ZERO MARKERS VERIFIED")
