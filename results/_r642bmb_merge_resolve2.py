# -*- coding: utf-8 -*-
"""r642 bm-b merge resolver #2 (origin/main bm-a r654 S6+S7 churn absorb,
second mid-round push-race ring; first ring resolved in
_r642bmb_merge_resolve.py).

Recipes (SKILL.md): bm-a regen ts 02:36-02:39 NEWER than our 02:29-02:33 ->
- derive/status/scorecard/token/attrition/fundamental/futures/lhb/
  update_status/regime(行双侧恒等断言): take-side theirs (newest wins).
- LIVE x4 (LIVE-2026-10-04.* + LIVE-latest.*): take-side OURS -- schema
  supersession, not ts: ours = ceo_live_usage v1_5 payload carrying the
  judgment_burns face (this round's product); theirs = v1.4-code regen
  from bm-a's tree (our v1.5 commit never reached origin -- both pushes
  were lawfully claw-blocked). Replaying theirs = product-face revert
  (r609 stale-snapshot law). Sections 1-4 are deterministic derives of
  the same Sunday faces -> zero information loss taking ours.
- compute_audit.json: rolling-ledger ts-key union again (201|201 -> cap
  201, drop oldest common, latest=theirs 02:36:29 newer).
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL blob {side}:{path}")
    return r.stdout


def take(side, path):
    data = blob(side, path)
    if path.endswith(".json"):
        json.loads(data)                      # r185: parse-verify pre-write
    with open(path, "wb") as fh:
        fh.write(data)
    subprocess.run(["git", "add", "--", path], check=True)


print("== phase 1: take-theirs derive faces (newest regen wins)")
TAKE_THEIRS = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in TAKE_THEIRS:
    if p == "results/regime_state.json":      # equality assert then take new
        a, b = json.loads(blob(2, p)), json.loads(blob(3, p))
        assert a["history"] == b["history"], "regime history diverge ring2"
        assert (a.get("transitions") == b.get("transitions")), \
            "regime transitions diverge ring2"
    take(3, p)
    print(f"  take-theirs ok: {p}")

print("== phase 2: LIVE x4 take-ours (v1_5 schema supersession)")
for p in ["docs/live_usage/LIVE-2026-10-04.json",
          "docs/live_usage/LIVE-2026-10-04.md",
          "docs/live_usage/LIVE-latest.json",
          "docs/live_usage/LIVE-latest.md"]:
    ours = json.loads(blob(2, p)) if p.endswith(".json") else None
    if ours is not None:
        assert ours["schema"] == "ceo_live_usage_v1_5", \
            f"our LIVE side not v1_5: {p}"
        assert "judgment_burns" in ours, f"judgment_burns missing: {p}"
        thrs = json.loads(blob(3, p))
        assert thrs.get("schema") == "ceo_live_usage_v1_4", \
            "their LIVE side unexpected schema (re-adjudicate!)"
    take(2, p)
    print(f"  take-ours ok: {p} (v1_5 kept)")

print("== phase 3: compute_audit union ring 2")
p = "results/compute_audit.json"
ours, theirs = json.loads(blob(2, p)), json.loads(blob(3, p))
ha = {e["ts"]: e for e in ours["history"]}
hb = {e["ts"]: e for e in theirs["history"]}
union = dict(ha)
union.update(hb)
keys = sorted(union)
kept = keys[-201:]
merged = {"latest": theirs["latest"], "history": [union[k] for k in kept]}
assert "2026-10-04 02:29:10" in kept, "our own audit entry lost ring2"
assert "2026-10-04 02:36:29" in kept, "bm-a audit entry lost ring2"
assert merged["latest"]["ts"] == "2026-10-04 02:36:29"
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(merged, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
subprocess.run(["git", "add", "--", p], check=True)
print(f"  union ok: {len(ha)}|{len(hb)} -> {len(kept)} "
      f"(dropped oldest common {sorted(set(ha) | set(hb))[0]}, "
      f"latest=theirs 02:36:29)")

print("== phase 4: conflict state cleared + key faces intact")
out = subprocess.run(["git", "status", "--porcelain"],
                      capture_output=True).stdout.decode("utf-8", "replace")
uu = [l for l in out.splitlines() if l[:2] in
      ("UU", "AA", "DD", "AU", "UA", "DU", "UD")]
assert not uu, f"remaining conflicts: {uu}"
st = json.load(open("state.json", encoding="utf-8"))
assert st["round_no"] == 642
live = json.load(open("docs/live_usage/LIVE-2026-10-04.json",
                      encoding="utf-8"))
assert live["schema"] == "ceo_live_usage_v1_5"
assert len(live["judgment_burns"]["families"]) == 3
print("RESOLVE2_OK")
