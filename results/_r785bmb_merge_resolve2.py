# r785 bm-b resolver-2: 16 UU second absorb (origin bm-a r796 S6 chain 22:21-22:23 > ours 21:44-21:56).
# Recipes (probed, R350 staged-blob law):
#   - 13 snapshot faces: THEIRS whole-blob (ts-newer-wins; strategy/scorecard also host=bm-a law r378)
#   - REPORT/LIVE md twins: byte-copy stage3 (twins follow json same side)
#   - compute_audit/regime_state: THEIRS state fields + history/transitions/triggers ROW UNION (zero-loss)
#   - token_usage: THEIRS base (newer generated) + per-key numeric max-union overlay (ours holds fresh
#     bm-b leaves from dead r784 meter that never reached origin; r781 recipe, direction-agnostic)
import subprocess, json, hashlib

def blob(stage, path):
    h = subprocess.run(["git", "rev-parse", "-q", "--verify", f":{stage}:{path}"],
                       capture_output=True, text=True).stdout.strip()
    assert h, f"stage {stage} missing for {path}"
    return subprocess.run(["git", "cat-file", "blob", h],
                          capture_output=True).stdout.decode("utf-8", "replace")

def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

receipt = {"round": "r785-2", "faces": {}}

THEIRS = ["docs/daily_report/REPORT-2026-10-06.json", "docs/daily_report/REPORT-2026-10-06.md",
          "docs/live_usage/LIVE-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
          "results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/lhb_update_status.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/update_status.json"]
for p in THEIRS:
    b = blob(3, p)
    write(p, b)
    receipt["faces"][p] = {"recipe": "THEIRS ts-newer-wins (22:2x > 21:5x)" if p.endswith((".json",)) else "THEIRS md twin byte-copy",
                           "sha16": hashlib.sha256(b.encode()).hexdigest()[:16]}

# ledger unions: state=theirs, rows=union
for p, keys in [("results/compute_audit.json", ["history"]),
                ("results/regime_state.json", ["history", "transitions", "triggers"])]:
    jt = json.loads(blob(3, p))
    jo = json.loads(blob(2, p))
    for k in keys:
        vo, vt = jo.get(k) or [], jt.get(k) or []
        seen, un = set(), []
        for row in vo + vt:
            sig = json.dumps(row, ensure_ascii=False, sort_keys=True)
            if sig not in seen:
                seen.add(sig)
                un.append(row)
        receipt["faces"][f"{p}::{k}"] = {"ours_rows": len(vo), "theirs_rows": len(vt), "union_rows": len(un)}
        jt[k] = un
    out = json.dumps(jt, ensure_ascii=False, indent=1) + "\n"
    write(p, out)
    receipt["faces"][p] = {"recipe": "THEIRS state + row-union zero-loss",
                           "sha16": hashlib.sha256(out.encode()).hexdigest()[:16]}

# token_usage: theirs base + numeric max overlay
o, t = json.loads(blob(2, "results/token_usage.json")), json.loads(blob(3, "results/token_usage.json"))
def overlay(newer, older):
    out = dict(newer)
    for k, v in older.items():
        if k not in out:
            out[k] = v
        elif isinstance(v, (int, float)) and isinstance(out[k], (int, float)) and not isinstance(v, bool) and not isinstance(out[k], bool):
            out[k] = max(out[k], v)
        elif isinstance(v, dict) and isinstance(out[k], dict):
            out[k] = overlay(out[k], v)
    return out
merged = overlay(t, o)
changed = {k: {"theirs": t.get(k), "ours": o.get(k), "merged": merged.get(k)}
           for k in set(o) | set(t) if merged.get(k) != t.get(k)}
out = json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
write("results/token_usage.json", out)
receipt["faces"]["results/token_usage.json"] = {
    "recipe": "THEIRS base (22:23:07) + numeric max-union overlay (r781, preserves dead-r784 bm-b leaves)",
    "sha16": hashlib.sha256(out.encode()).hexdigest()[:16],
    "keys_changed_vs_theirs": {k: str(v["merged"])[:60] for k, v in changed.items()}}

with open("results/_r785bmb_merge_resolve2.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("resolver-2 done: THEIRS x%d + union x3" % len(THEIRS))
print("token keys changed vs theirs:", list(changed.keys()))
print("compute_audit history:", receipt["faces"]["results/compute_audit.json::history"])
print("regime lists:", {k: receipt["faces"][k] for k in receipt["faces"] if k.startswith("results/regime_state.json::")})
