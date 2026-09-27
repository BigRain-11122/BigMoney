# r339 bm-b stop-1: quick structure probe of ledger-type UU sides
import json, os

B = "results/_r339bmb_blobs2"
def load(p):
    with open(p, "rb") as f:
        return f.read()

def j(p):
    return json.loads(load(p).decode("utf-8"))

# compute_audit
for side in ("ours", "theirs"):
    d = j(os.path.join(B, "results__compute_audit.json." + side))
    hist = d.get("history")
    print("compute_audit", side, "keys:", sorted(d.keys())[:8], "| history:", len(hist) if hist is not None else None)
    if hist:
        e = hist[-1]
        print("  hist last keys:", sorted(e.keys()))
        print("  hist first ts:", hist[0].get("ts"), "last ts:", hist[-1].get("ts"), "machines:", {h.get('machine') for h in hist})

# regime_state
for side in ("ours", "theirs"):
    d = j(os.path.join(B, "results__regime_state.json." + side))
    print("regime", side, "keys:", sorted(d.keys()))
    hist = d.get("history") or d.get("transitions") or []
    print("  hist len:", len(hist), "| first:", json.dumps(hist[0], ensure_ascii=False)[:150] if hist else None)
    print("  last:", json.dumps(hist[-1], ensure_ascii=False)[:150] if hist else None)

# token_usage
for side in ("ours", "theirs"):
    d = j(os.path.join(B, "results__token_usage.json." + side))
    print("token", side, "keys:", sorted(d.keys()))
    for k, v in d.items():
        if isinstance(v, list):
            print("  list", k, "len", len(v), "last:", json.dumps(v[-1], ensure_ascii=False)[:120])
        elif isinstance(v, dict):
            print("  dict", k, "keys:", sorted(v.keys())[:10])

# update_status (representative snapshot)
for side in ("ours", "theirs"):
    d = j(os.path.join(B, "results__update_status.json." + side))
    tsf = {k: v for k, v in d.items() if isinstance(v, str) and "2026" in v}
    print("update_status", side, "tsfields:", tsf)

# daily_report json twin
for side in ("ours", "theirs"):
    d = j(os.path.join(B, "docs__daily_report__REPORT-2026-09-27.json." + side))
    tsf = {k: v for k, v in d.items() if isinstance(v, str) and ("2026" in v or "T" in v)}
    print("daily_report", side, "tsfields:", tsf, "| keys:", sorted(d.keys())[:12])

# autofill sides from commit objects
import subprocess
def obj(ref):
    return subprocess.run(["git", "show", ref], capture_output=True, check=True).stdout
for tag, ref in (("aee0fa02", "aee0fa02:results/autofill_state.json"), ("fc0e784b", "fc0e784b:results/autofill_state.json")):
    d = json.loads(obj(ref).decode("utf-8"))
    print("autofill", tag, "launches:", len(d["launches"]), "last_tick ts:", d["last_tick"].get("ts"), d["last_tick"].get("machine"))
wt = j("results/autofill_state.json") if os.path.exists("results/autofill_state.json") else None
import re
raw = load("results/autofill_state.json")
has_marker = b"<<<<<<<" in raw
try:
    wtd = json.loads(raw.decode("utf-8"))
    print("autofill worktree: launches:", len(wtd["launches"]), "last_tick ts:", wtd["last_tick"].get("ts"), wtd["last_tick"].get("machine"), "| markers:", has_marker)
except Exception as ex:
    print("autofill worktree: UNPARSEABLE:", ex, "| markers:", has_marker)
