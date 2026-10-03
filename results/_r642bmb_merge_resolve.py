# -*- coding: utf-8 -*-
"""r642 bm-b merge resolver (origin/main bm-a r654 push-race closeout).

Canonical recipes per .codely-cli/skills/bigmoney-conflict-resolve SKILL.md:
- 14 snapshot faces + _attrition_guard_scan.json (manual UNKNOWN adjudicated
  below): take-side ours WHOLESALE (git checkout --ours = stage-2 bytes,
  R209/R216) -- ours regen ts 02:29-02:33 vs theirs 02:21-02:24, and LIVE
  faces ours = schema v1_5 (judgment_burns face) vs theirs v1_4.
- results/compute_audit.json: rolling-ledger ts-key union (r188/R208),
  producer cap semantics [-200:]+append -> keep 201 newest, latest=ours.
- results/regime_state.json: history/transitions asserted byte-equal both
  sides (same deterministic derive) -> take-ours (trivial union, newer ts).

_attrition_guard_scan.json UNKNOWN adjudication: shape {ts, rc,
active_loss, files} identical both sides, whole-doc re-derived by each
scan run, ts-comparable (ours 02:33:54 > theirs 02:24:25) -> same class as
fundamental_b_layer_filter (R216 snapshot take-new by ts) -> take-ours.

Post-merge verification: every resolved json face json.loads-clean; audit
union zero-loss asserts (both sides' own entries present); auto-merged
bm-b single-writer faces (state.json/heartbeat/nulls/round report)
content-verified.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def sh(*args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL {args}: {r.stderr.decode('utf-8', 'r')[:400]}")
    return r.stdout


def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL blob {side}:{path}: "
                         f"{r.stderr.decode('utf-8', 'r')[:200]}")
    return r.stdout


SNAPSHOTS_TAKE_OURS = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",      # UNKNOWN -> manual take-ours
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/regime_state.json",                # trivial union, see docstring
]

print("== phase 1: take-ours snapshots (stage-2 bytes wholesale)")
for p in SNAPSHOTS_TAKE_OURS:
    ours = blob(2, p)
    theirs = blob(3, p)
    assert ours, f"empty stage2: {p}"
    if p.endswith(".json"):
        a, b = json.loads(ours), json.loads(theirs)
        assert isinstance(a, dict) and isinstance(b, dict)
    if p == "results/regime_state.json":
        a, b = json.loads(ours), json.loads(theirs)
        assert a["history"] == b["history"], "regime history rows diverge"
        assert (a.get("transitions") == b.get("transitions")), \
            "regime transitions diverge"
    with open(p, "wb") as fh:
        fh.write(ours)
    sh("git", "add", "--", p)
    print(f"  take-ours ok: {p} ({len(ours)}B)")

print("== phase 2: compute_audit.json rolling-ledger union (cap 201)")
p = "results/compute_audit.json"
ours, theirs = json.loads(blob(2, p)), json.loads(blob(3, p))
ha = {e["ts"]: e for e in ours["history"]}
hb = {e["ts"]: e for e in theirs["history"]}
union = dict(ha)
union.update(hb)
keys = sorted(union, key=lambda t: t)          # ts strings sort lexically
kept = keys[-201:]                            # producer cap: newest 201
merged_hist = [union[k] for k in kept]
assert len(ha) == 201 and len(hb) == 201
assert len(set(ha) | set(hb)) == 202, "expected 202 unique ts keys"
assert "2026-10-04 02:29:10" in kept, "our own audit entry lost"
assert "2026-10-04 02:21:13" in kept, "bm-a audit entry lost (zero-loss)"
assert kept[0] == sorted(set(ha) | set(hb))[1], "oldest common dropped first"
merged = {"latest": ours["latest"], "history": merged_hist}
assert merged["latest"]["ts"] == "2026-10-04 02:29:10"  # ours newer
json.loads(json.dumps(merged))                 # round-trip sanity
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(merged, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
sh("git", "add", "--", p)
print(f"  union ok: {len(ha)}|{len(hb)} -> {len(merged_hist)} "
      f"(dropped oldest common {kept[0] if False else sorted(set(ha)|set(hb))[0]}, "
      f"kept both sides' own latest)")

print("== phase 3: auto-merged single-writer faces verification")
st = json.load(open("state.json", encoding="utf-8"))
assert st["round_no"] == 642 and "r642" in st["note"], \
    f"state.json merge damaged: round={st.get('round_no')}"
hb2 = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert hb2["round_no"] == 642 and isinstance(hb2["heartbeat_epoch_utc"], int)
for fam in ("fund_quality_p1", "fund_value_p1", "fund_divlowvol_p1"):
    n = sum(1 for _ in open(os.path.join("results", fam, "nulls.jsonl"),
                            encoding="utf-8", errors="replace"))
    assert n >= 370, f"{fam} nulls lines suspicious: {n}"
    print(f"  nulls {fam}: {n} lines (superset ok)")
rr = open(r"logs\iteration-loop\round_reports.md", "rb").read()
assert b"round 642 (bm-b" in rr, "round report r642 line lost in auto-merge"
print("  state/heartbeat/round-report/nulls verified")

print("== phase 4: conflict state cleared?")
out = subprocess.run(["git", "status", "--porcelain"],
                      capture_output=True).stdout.decode("utf-8", "r")
uu = [l for l in out.splitlines() if l.startswith(("UU", "AA", "DD"))]
assert not uu, f"remaining conflicts: {uu}"
print("RESOLVE_OK")
