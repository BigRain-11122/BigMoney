# -*- coding: utf-8 -*-
# r907 bm-a rebase resolver: 13 regenerable shared faces take-MINE(stage3, newer-wins r440)
# + compute_audit.json rolling-history UNION by ts (zero-loss, r813 x2_watch precedent)
# + token_usage.json take-newer snapshot (per-machine sections identical both sides,
#   -bm-a delta = aggregation estimate noise <1%, sources = per-machine .bm-*.json faces no conflict)
import subprocess, json, io, sys

def blob(spec):
    p = subprocess.run(["git", "show", spec], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git show {spec} rc={p.returncode}")
    return p.stdout

SIMPLE_TAKE_MINE = [
    "docs/daily_report/REPORT-2026-10-09.json",
    "docs/daily_report/REPORT-2026-10-09.md",
    "docs/live_usage/LIVE-2026-10-09.json",
    "docs/live_usage/LIVE-2026-10-09.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
UNION_FACES = ["results/compute_audit.json"]

for f in SIMPLE_TAKE_MINE:
    with io.open(f, "wb") as fh:
        fh.write(blob(f":3:{f}"))
    print(f"take-mine(stage3): {f}")

for f in UNION_FACES:
    d2 = json.loads(blob(f":2:{f}").decode("utf-8-sig"))
    d3 = json.loads(blob(f":3:{f}").decode("utf-8-sig"))
    h2, h3 = d2["history"], d3["history"]
    merged = {e["ts"]: e for e in h2}
    for e in h3:
        merged[e["ts"]] = e  # same-ts: stage3 (later aggregation) wins
    keys = sorted(merged.keys())
    history = [merged[k] for k in keys]
    latest = d3["latest"] if d3["latest"]["ts"] >= d2["latest"]["ts"] else d2["latest"]
    out = {"history": history, "latest": latest}
    assert history[-1]["ts"] == max(d2["history"][-1]["ts"], d3["history"][-1]["ts"])
    assert len(history) >= max(len(h2), len(h3)), "union shrink"
    with io.open(f, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"union: {f}: {len(h2)}+{len(h3)} -> {len(history)} entries, latest {latest['ts']}")

# zero-conflict-marker assert on all resolved faces
MARK = ("<<<<<<<", "=======", ">>>>>>>")
for f in SIMPLE_TAKE_MINE + UNION_FACES:
    body = io.open(f, "r", encoding="utf-8", errors="replace").read()
    for m in MARK:
        assert m not in body, f"conflict marker in {f}"
print("RESOLVER rc0: 13 take-mine + 1 union, zero markers")
