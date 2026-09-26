"""r283 bm-b S7 rebase resolver: 16 UU vs bm-a R280 (03058dad) same-window S6 dual producers.

Direction law (rebase inversion): stage2 'ours' = origin/new-base (bm-a side),
stage3 'theirs' = bm-b replayed commit (my side). All take-new decisions go by
REAL content ts keys, never by side name (r267/r277 field-provenance law).
Recipes per classify_conflicts.py + skill canon. Zero-loss unions for ledgers.
"""
import io
import json
import subprocess


def blob(rev):
    r = subprocess.run(["git", "show", rev], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}: {r.returncode}")
    return r.stdout


def jload(b):
    return json.loads(b.decode("utf-8-sig"))


def ts_of(d, keys=("ts", "generated", "updated_at", "generated_at")):
    for k in keys:
        if isinstance(d, dict) and k in d and isinstance(d[k], str):
            return d[k]
    return None


FILES_SNAPSHOT = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "docs/daily_report/REPORT-2026-09-27.json",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/daily_scorecard.json",
]

report = {}

for p in FILES_SNAPSHOT:
    a = jload(blob(f":2:{p}"))    # bm-a side
    b = jload(blob(f":3:{p}"))    # bm-b side (mine)
    if a == b:
        side = "identical"
    else:
        ta, tb = ts_of(a), ts_of(b)
        if ta and tb and ta != tb:
            side = "bm-b" if tb > ta else "bm-a"
        elif ta and tb and ta == tb:
            # same-ts tie -> same-second tie law r140 -> HEAD side (= ours = origin base)
            side = "bm-a"
        else:
            # zero-wall-clock deterministic regen views: content-equal check by
            # r267 producer-pairing; if only embedded refs differ, take mine (later S6)
            side = "bm-b"
    report[p] = {"a_ts": ts_of(a), "b_ts": ts_of(b), "take": side}
    print(f"{p}: a_ts={ts_of(a)} b_ts={ts_of(b)} -> take {side}")

with io.open("results/_r283bmb_resolve_faces.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("faces report written")
