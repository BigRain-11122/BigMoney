# r395 bm-b rebase stop-3 resolve: 16 UU canon recipes (r372 family)
import json, io, os, subprocess

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")

def raw_side(p, s):
    r = subprocess.run(["git", "show", f":{s}:{p}"], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, (p, s, r.stderr.decode()[:150])
    return r.stdout.decode("utf-8-sig")

def j_side(p, s):
    raw = raw_side(p, s)
    for m in MARKERS:
        assert m not in raw, f"marker in stage{s} {p}"
    return json.loads(raw)

def write(p, text):
    out = os.path.join(ROOT, p.replace("/", os.sep))
    for m in MARKERS:
        assert m not in text, f"marker would be written: {p}"
    tmp = out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, out)

def write_j(p, obj):
    write(p, json.dumps(obj, ensure_ascii=False, indent=1) + "\n")

# --- 1) CODELY.md: mine (:3:) + their r177 62nd pitlaw entry appended
mine_codely = raw_side("CODELY.md", 3)
theirs_lines = [l for l in raw_side("CODELY.md", 2).split("\n")
                if l.startswith("- [2026-09-28 19:5") and "r177 bm-c" in l]
assert theirs_lines, "their 62nd pitlaw entry not found in :2:"
assert len(mine_codely.rstrip("\n")) > 0
if not mine_codely.endswith("\n"):
    mine_codely += "\n"
for l in theirs_lines:
    if l not in mine_codely:
        mine_codely += l + "\n"
write("CODELY.md", mine_codely)
sz = os.path.getsize(os.path.join(ROOT, "CODELY.md"))
assert sz <= 10240, f"CODELY over 10KB: {sz}"

# --- 2) compute_audit.json: history key-union zero-loss, latest = newer ts
a2, a3 = j_side("results/compute_audit.json", 2), j_side("results/compute_audit.json", 3)
hist = {}
for row in a2.get("history", []) + a3.get("history", []):
    k = (row.get("ts"), row.get("machine"))
    hist[k] = row  # later write wins on identical key
union = list(hist.values())
union.sort(key=lambda r: (r.get("ts") or "", r.get("machine") or ""))
latest = a2.get("latest", {})
if str(a3.get("latest", {}).get("ts", "")) >= str(latest.get("ts", "")):
    latest = a3.get("latest", {})
write_j("results/compute_audit.json", {"latest": latest, "history": union})

# --- 3) regime_state.json: flat take-fresher + row-union histories
r2, r3 = j_side("results/regime_state.json", 2), j_side("results/regime_state.json", 3)
new = r3 if str(r3.get("updated", "")) >= str(r2.get("updated", "")) else r2
for k in ("history", "transitions"):
    seen = {(row.get("ts") or row.get("date") or json.dumps(row, sort_keys=True))
            for row in new.get(k, [])}
    for row in (r2 if new is r3 else r3).get(k, []):
        key = (row.get("ts") or row.get("date") or json.dumps(row, sort_keys=True))
        if key not in seen:
            new.setdefault(k, []).append(row); seen.add(key)
write_j("results/regime_state.json", new)

# --- 4) runnable_pool.json: keep :2: (surgical union landed there at stop-2)
write("results/runnable_pool.json", raw_side("results/runnable_pool.json", 2))
pool = json.loads(raw_side("results/runnable_pool.json", 2))
w4 = next(e for e in pool["entries"] if e.get("id") == "TRIAL-LABOR-W4-JUDGE")
assert w4.get("lane_owner") == "bm-b" and w4["shards"][0].get("status") == "done"

# --- 5) deterministic same-day regen faces + snapshot faces: take mine (:3: fresher)
TAKE3 = [
    "docs/daily_report/REPORT-2026-09-28.md",
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/live_usage/LIVE-2026-09-28.md",
    "docs/live_usage/LIVE-2026-09-28.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in TAKE3:
    write(p, raw_side(p, 3))

print("STOP3_RESOLVED: codely_bytes=", sz, "audit_hist=", len(union),
      "regime_updated=", new.get("updated"), "take3=", len(TAKE3),
      "their62=", len(theirs_lines))
