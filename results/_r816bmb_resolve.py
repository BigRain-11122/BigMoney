"""r816 bm-b rebase-storm canonical resolver (16 UU, bigmoney-conflict-resolve).

Storm: same-window double-S6 (bm-a r940/r941 vs bm-b r816) regenerated the
derived faces in parallel. Recipes per classifier + manual classification:
  - snapshot family -> take-new WHOLE BYTES by named ts key (no json.dumps
    re-serialization; producer format preserved byte-exact, R209/js law)
  - rolling-ledger family (compute_audit.json history, regime_state.json
    transitions/triggers/history) -> full-row-identity union zero loss,
    newest state fields take-new
Receipt: results/_r816bmb_resolve.json. Zero network, deterministic.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEIPT = os.path.join(ROOT, "results", "_r816bmb_resolve.json")

SNAPSHOTS = [
    "docs/live_usage/LIVE-2026-10-10.json",
    "docs/live_usage/LIVE-2026-10-10.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/token_usage.json",
]
# dashboard_status.js twin taken from whichever side's .json twin is newer
DASH_JSON = "results/dashboard_status.json"
DASH_JS = "results/dashboard_status.js"
LEDGERS = {
    "results/compute_audit.json": ["history"],
    "results/regime_state.json": ["history", "transitions", "triggers"],
}
TS_KEYS = ("ts", "generated", "generated_at", "updated", "asof",
           "scan_ts")


def stage_bytes(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def ts_of(raw):
    try:
        d = json.loads(raw.decode("utf-8"))
    except Exception:
        return ""
    for k in TS_KEYS:
        v = d.get(k)
        if v:
            return str(v)
    return ""


def take_new(path):
    a, b = stage_bytes(path, 2), stage_bytes(path, 3)
    if a is None or b is None:
        return ("one-side-missing", a or b)
    ta, tb = ts_of(a), ts_of(b)
    if tb >= ta:                       # newer-or-equal -> mine (same-day idem)
        return (f"take-theirs ts {ta}<{tb}", b)
    return (f"take-ours ts {ta}>{tb}", a)


def union_ledger(path, list_keys):
    a = json.loads(stage_bytes(path, 2).decode("utf-8"))
    b = json.loads(stage_bytes(path, 3).decode("utf-8"))
    counts = {}
    for k in list_keys:
        la_rows, lb_rows = list(a.get(k) or []), list(b.get(k) or [])
        seen, out_rows = set(), []
        for row in la_rows + lb_rows:
            ident = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if ident not in seen:
                seen.add(ident)
                out_rows.append(row)
        assert len(out_rows) >= max(len(la_rows), len(lb_rows)), \
            f"union loss {path}:{k}"
        counts[k] = {"ours": len(la_rows), "theirs": len(lb_rows),
                     "union": len(out_rows)}
        a[k] = out_rows
    # newest state fields: take-theirs (my 04:5x derive) on non-ledger keys
    for k in b:
        if k not in list_keys:
            a[k] = b[k]
    blob = (json.dumps(a, indent=1, ensure_ascii=False) + "\n")
    return (f"union {counts}", blob.encode("utf-8"))


def main():
    receipt = {"resolved": {}, "notes": []}
    for p in SNAPSHOTS:
        how, blob = take_new(p)
        assert blob is not None, f"both sides missing {p}"
        with open(os.path.join(ROOT, p), "wb") as fh:
            fh.write(blob)
        receipt["resolved"][p] = how
    # dashboard twins: pick side by .json ts, take whole bytes both files
    a, b = stage_bytes(DASH_JSON, 2), stage_bytes(DASH_JSON, 3)
    ta, tb = ts_of(a), ts_of(b)
    side = 3 if tb >= ta else 2
    for p in (DASH_JSON, DASH_JS):
        blob = stage_bytes(p, side)
        with open(os.path.join(ROOT, p), "wb") as fh:
            fh.write(blob)
        receipt["resolved"][p] = f"take-{'theirs' if side == 3 else 'ours'} whole-bytes (json ts {ta} vs {tb})"
    for p, keys in LEDGERS.items():
        how, blob = union_ledger(p, keys)
        with open(os.path.join(ROOT, p), "wb") as fh:
            fh.write(blob)
        receipt["resolved"][p] = how
    # validation pass: every .json resolved file must json.loads
    for p in list(receipt["resolved"]):
        if p.endswith(".json"):
            json.loads(open(os.path.join(ROOT, p), "rb").read()
                      .decode("utf-8"))
    js = open(os.path.join(ROOT, DASH_JS), "rb").read().decode("utf-8")
    assert js.lstrip().startswith("window.DASH_DATA"), "js wrapper stripped!"
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(receipt["resolved"], indent=1, ensure_ascii=False))
    print("resolver: ALL PASS (validation json.loads + js wrapper intact)")


if __name__ == "__main__":
    sys.exit(main())
