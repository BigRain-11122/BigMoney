import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))


def stage(n, p):
    return subprocess.check_output(["git", "show", f":{n}:{p}"])


def write_bytes(p, b):
    with open(p, "wb") as f:
        f.write(b)


def write_stage(n, p):
    write_bytes(p, stage(n, p))
    if p.endswith(".json"):
        json.load(open(p, encoding="utf-8"))  # parse-validate


# --- 1. take-:3 (mine, newer) faces ---
TAKE3 = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/fundamental_b_layer_filter.json",
    "results/_attrition_guard_scan.json",
]
for p in TAKE3:
    write_stage(3, p)
    print("take3:", p)

# --- 2. lane-backed faces: write :3 then sync_face merged-view re-derive ---
LANE_FACES = ["compute_audit", "regime_state", "token_usage",
              "update_status", "lhb_update_status", "futures_update_status"]
for f in LANE_FACES:
    p = f"results/{f}.json"
    write_stage(3, p)
    print("stage3-then-sync:", p)

# pool: write :2 (origin side parseable) then sync
write_stage(2, "results/runnable_pool.json")
print("stage2-then-sync: results/runnable_pool.json")

# --- 3. p1d_gates: daemon may have freshly rewritten disk copy ---
gp = "results/p1d_gates.json"
raw = open(gp, "rb").read()
if b"<<<<<<<" in raw or b"=======" in raw or b">>>>>>>" in raw:
    write_stage(3, gp)
    print("p1d_gates: markers found -> take3")
else:
    d = json.loads(raw.decode("utf-8"))
    print("p1d_gates: disk clean (daemon-fresh derive kept), keys:",
          sorted(d)[:6])

# --- 4. sync_face canonical merged-view settle ---
from merge_lane_views import sync_face  # noqa: E402

for f in LANE_FACES + ["runnable_pool"]:
    r = sync_face(f)
    print("sync_face", f, "->", r.get("status"),
          "shared=", r.get("wrote_shared"), "lane=", r.get("wrote_lane"),
          (r.get("notes") or [""])[0][:60])

# --- 5. post-verify pool ---
pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
ents = pool.get("entries", [])
by_id = {e.get("id"): e for e in ents}
n = by_id.get("LOWAMP-P2-NULLS")
assert n and n.get("status") == "done", "NULLS not done!"
print("verify: LOWAMP-P2-NULLS", n.get("status"),
      n["shards"][0].get("status"), n["shards"][0].get("done_at"))
w9 = [e for e in ents if "N1-W9" in str(e.get("id", ""))]
print("verify: W9 entries =", len(w9),
      {e.get("status") for e in w9})
assert len(w9) == 12, "W9 supply lost in merge!"
rev2 = [e for e in ents if "REV-P2" in str(e.get("id", ""))]
print("verify: REV-P2 entries =", len(rev2),
      [(e.get("id"), e.get("status"),
        (e.get("shards") or [{}])[0].get("owner")) for e in rev2][:4])
w14 = by_id.get("TRIAL-LABOR-W14-GENERATE")
print("verify: W14 =", w14.get("status") if w14 else "ABSENT",
      "| park_note kept =", bool(w14 and w14.get("park_note")))
la = [e for e in ents if str(e.get("id", "")).startswith("LOWAMP-P2-")]
done_ct = sum(1 for e in la if e.get("status") == "done")
print(f"verify: LOWAMP-P2 family {done_ct}/{len(la)} done")
assert done_ct == len(la) == 18, "LOWAMP-P2 family incomplete!"

# compute_audit zero-loss spot: history count >= both sides
ca = json.load(open("results/compute_audit.json", encoding="utf-8"))
h2 = json.loads(stage(2, "results/compute_audit.json")).get("history", [])
h3 = json.loads(stage(3, "results/compute_audit.json")).get("history", [])
print("verify: compute_audit history rows:",
      len(ca.get("history", [])), ">= max(", len(h2), ",", len(h3), ")")
assert len(ca.get("history", [])) >= max(len(h2), len(h3)), "history loss!"

print("RESOLVE_OK")
