"""R302 bm-a rebase collision resolver (canon: bigmoney-conflict-resolve).

Collision: bm-b r307 (1a9dda99, same-window S6 fold of my r301 face) vs my
wrap commit 840443ac replay. 14 UU, all regenerated artifacts.
Recipes: classifier 10 GREEN (compute_audit/regime_state rolling-ledger
union; snapshots take-new; dashboard_status.js js-wrapper mirror) + 4
UNKNOWN manually qualified = same-day idempotent regeneration snapshot
take-new-by-ts (daily_report pair mirrors its .json twin; scorecard pair
by generated ts). Rebase stage faces: :2 ours = base (bm-b 1a9dda99),
:3 theirs = my replayed 840443ac (r220 stage discipline).
Blobs read via subprocess bytes (r209 no-PS-redirection law)."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True).stdout


TS_KEYS = ["ts", "generated", "generated_at", "updated_at", "updated",
           "last_updated", "as_of", "time"]


def blob(stage, path):
    out = git("show", f":{stage}:{path}")
    return out.decode("utf-8")


def pick_ts(d):
    for k in TS_KEYS:
        if isinstance(d, dict) and k in d and d[k]:
            return str(d[k])
    return None


def take_new(path):
    a, b = blob(2, path), blob(3, path)
    da, db = json.loads(a), json.loads(b)
    ta, tb = pick_ts(da), pick_ts(db)
    side = 3 if (ta is None or (tb is not None and tb >= ta)) else 2
    # same-second/absent tie -> HEAD side per r140 law => in rebase HEAD is
    # the base (:2) for not-yet-committed replay; but for tie we must keep
    # the replayed content to avoid dropping my round's measurement:
    if ta is not None and tb is not None and ta == tb:
        side = 3
    doc = db if side == 3 else da
    with open(os.path.join(ROOT, path), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    json.load(open(os.path.join(ROOT, path), encoding="utf-8"))
    return f"take-new side={side} ts {ta} vs {tb}"


def union_ledger(path, ledger_keys):
    a, b = blob(2, path), blob(3, path)
    da, db = json.loads(a), json.loads(b)
    out = dict(db if pick_ts(db) and (pick_ts(da) is None
              or pick_ts(db) >= pick_ts(da)) else da)  # newer scalars base
    for key in ledger_keys:
        la = da.get(key, [])
        lb = db.get(key, [])
        seen, merged = set(), []
        for e in la + lb:
            k = e.get("ts", json.dumps(e, sort_keys=True, ensure_ascii=False))
            if k in seen:
                continue
            seen.add(k)
            merged.append(e)
        merged.sort(key=lambda e: str(e.get("ts", "")))
        out[key] = merged
        assert len(out[key]) >= max(len(la), len(lb)), "union zero-loss fail"
    with open(os.path.join(ROOT, path), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    json.load(open(os.path.join(ROOT, path), encoding="utf-8"))
    return (f"union {ledger_keys} |A|={ {k: len(da.get(k, [])) for k in ledger_keys} } "
            f"|B|={ {k: len(db.get(k, [])) for k in ledger_keys} } "
            f"-> { {k: len(out[k]) for k in ledger_keys} }")


def take_side_bytes(path, side):
    raw = blob(side, path).encode("utf-8")
    with open(os.path.join(ROOT, path), "wb") as fh:
        fh.write(raw)
    return f"take-side-{side} whole bytes ({len(raw)}B)"


def mirror_pair_side(json_path, twin_path):
    """Resolve json by ts, then mirror the SAME side's bytes for the twin
    (same producer run wrote both)."""
    a, b = blob(2, json_path), blob(3, json_path)
    ta, tb = pick_ts(json.loads(a)), pick_ts(json.loads(b))
    side = 3 if (ta is None or (tb is not None and tb >= ta)) else 2
    if ta is not None and tb is not None and ta == tb:
        side = 3
    return take_side_bytes(json_path, side), take_side_bytes(twin_path, side)


log = []

# rolling-ledger unions (zero row loss)
for path, keys in [
    ("results/compute_audit.json", ["history"]),
    ("results/regime_state.json", ["history", "transitions"]),
]:
    log.append(f"{path}: {union_ledger(path, keys)}")

# snapshot take-new by ts
for path in [
    "results/dashboard_status.json.__pair__",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]:
    if path.endswith("__pair__"):
        continue
    log.append(f"{path}: {take_new(path)}")

# twin pairs (same-run producer bytes mirror)
j1, j2 = mirror_pair_side("results/dashboard_status.json",
                           "results/dashboard_status.js")
log.append(f"results/dashboard_status.json: {j1}")
log.append(f"results/dashboard_status.js: {j2}  [js-wrapper R209: "
           f"producer bytes, no json.dumps strip]")
j3, j4 = mirror_pair_side("docs/daily_report/REPORT-2026-09-27.json",
                          "docs/daily_report/REPORT-2026-09-27.md")
log.append(f"docs/daily_report/REPORT-2026-09-27.json: {j3}")
log.append(f"docs/daily_report/REPORT-2026-09-27.md: {j4}  [md twin mirrors "
           f"json side]")

# stage all resolved paths
paths = [
    "results/compute_audit.json", "results/regime_state.json",
    "results/dashboard_status.json", "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/heat_update_status.json", "results/lhb_update_status.json",
    "results/token_usage.json", "results/update_status.json",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md",
]
for p in paths:
    r = subprocess.run(["git", "add", p], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, f"add fail {p}: {r.stderr}"

unmerged = git("ls-files", "-u").decode().strip()
assert not unmerged, f"unmerged remain: {unmerged}"

# marker poisoning check on resolved artifacts (D-05③ anchored face)
for p in paths:
    txt = open(os.path.join(ROOT, p), encoding="utf-8", errors="replace").read()
    for ln in txt.splitlines():
        assert not (ln.startswith("<<<<<<< ") or ln.startswith(">>>>>>> ")
                    or ln == "======="), f"marker poison in {p}"

print("RESOLVED 14/14:")
for line in log:
    print(" ", line)
print("zero unmerged; all staged; marker face clean")
