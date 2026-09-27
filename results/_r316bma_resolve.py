"""R316 bm-a S6-mirror batch resolver (rebase replay vs bm-b r318 closeout, 14 UU).

Classifier (bigmoney-conflict-resolve): 10 classified + 4 UNKNOWN
hand-adjudicated here. Rebase stage direction: :2: = HEAD = origin/main
(bm-b r318 closeout face); :3: = replayed commit (bm-a R316 face).

Recipes (SKILL.md law + r317 bm-b mirror precedent):
  compute_audit.json           rolling-ledger: history union by ts
                               (zero row loss), non-history top-level
                               fields from newest-ts side.
  regime_state.json            rolling-ledger: transitions union +
                               take-new by ts.
  dashboard_status.js          js-wrapper-snapshot: whole-bytes
                               take-side by inner ts (no json rewrite).
  *_status/update_status/
  fundamental_b_layer_filter/
  token_usage.json             snapshot: take-new by ts candidate.
  REPORT-2026-09-27.json/.md   UNKNOWN -> hand-adjudicated snapshot
                               take-new (same-day regeneration, newest
                               generated face wins).
  scorecard_v1/strategy_...    UNKNOWN -> hand-adjudicated snapshot
                               take-new (deterministic L1 re-derivation;
                               drift reported, newest generated face =
                               newest input state incl. bm-b T-89/T-90
                               harvest finalize landed 11:33:24).
Fail-closed: unknown ts key or parse failure = abort, no write.
"""
import json
import re
import subprocess
import sys

TS_KEYS = ("ts", "generated", "generated_at", "updated_at", "updated",
           "asof", "checked_at", "generated_ts")


def stage(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8-sig")


def ts_of(obj):
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and v:
            return v
    meta = obj.get("meta")
    if isinstance(meta, dict):
        v = meta.get("generated_at")
        if isinstance(v, str) and v:
            return v
    return None


def take_new_json(path, drift_report=None):
    a, b = stage(path, 2), stage(path, 3)
    da, db = json.loads(a), json.loads(b)
    ta, tb = ts_of(da), ts_of(db)
    assert ta and tb, f"{path}: no ts candidate ({ta!r}/{tb!r})"
    win = db if ta < tb else da          # tie -> HEAD side (r140)
    if drift_report is not None and isinstance(da, dict) \
            and isinstance(db, dict):
        diff = [k for k in set(da) | set(db) if da.get(k) != db.get(k)]
        drift_report[path] = diff
    open(path, "w", encoding="utf-8", newline="").write(
        json.dumps(win, ensure_ascii=False, indent=1) + "\n")
    return f"take-new ts={ts_of(win)}"


def take_new_bytes(path, ts_pat):
    a, b = stage(path, 2), stage(path, 3)
    ma = re.search(ts_pat, a)
    mb = re.search(ts_pat, b)
    assert ma and mb, f"{path}: inner ts not found"
    win, wts = (b, mb.group(1)) if ma.group(1) < mb.group(1) else (a, ma.group(1))
    open(path, "w", encoding="utf-8", newline="").write(win)
    return f"take-side bytes inner-ts={wts}"


def resolve_compute_audit(path):
    da, db = json.loads(stage(path, 2)), json.loads(stage(path, 3))
    ha, hb = da.get("history"), db.get("history")
    assert isinstance(ha, list) and isinstance(hb, list)
    seen, union = {}, []
    for e in ha + hb:
        k = e.get("ts")
        assert k, "history entry without ts"
        if k not in seen:
            seen[k] = e
            union.append(e)
    union.sort(key=lambda e: e["ts"])
    newest_side = da if ts_of(ha[-1]) >= ts_of(hb[-1]) else db
    out = dict(newest_side)
    out["history"] = union
    open(path, "w", encoding="utf-8", newline="").write(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    return f"history union {len(ha)}+{len(hb)}->{len(union)} " \
           f"zero-loss; state fields from {ts_of(newest_side)} side"


def resolve_regime_state(path):
    da, db = json.loads(stage(path, 2)), json.loads(stage(path, 3))
    ta, tb = ts_of(da), ts_of(db)
    assert ta and tb
    win = da if ta >= tb else db                   # take-new state
    for side in (da, db):                         # union transitions
        tr = side.get("transitions") or []
        seen = {(t.get("ts"), t.get("from"), t.get("to"))
                for t in win.get("transitions") or []}
        for t in tr:
            k = (t.get("ts"), t.get("from"), t.get("to"))
            if k not in seen:
                win.setdefault("transitions", []).append(t)
                seen.add(k)
    open(path, "w", encoding="utf-8", newline="").write(
        json.dumps(win, ensure_ascii=False, indent=1) + "\n")
    return f"state take-new ts={ts_of(win)}; transitions union"


def main():
    drift = {}
    report = {}
    report["results/compute_audit.json"] = resolve_compute_audit(
        "results/compute_audit.json")
    report["results/regime_state.json"] = resolve_regime_state(
        "results/regime_state.json")
    report["results/dashboard_status.js"] = take_new_bytes(
        "results/dashboard_status.js", r'"ts":\s*"([^"]+)"')
    for p in ("results/dashboard_status.json",
              "results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json",
              "results/heat_update_status.json",
              "results/lhb_update_status.json",
              "results/update_status.json",
              "results/token_usage.json",
              "results/scorecard_v1.json",
              "results/strategy_scorecard.json",
              "docs/daily_report/REPORT-2026-09-27.json"):
        report[p] = take_new_json(p, drift)
    report["docs/daily_report/REPORT-2026-09-27.md"] = take_new_bytes(
        "docs/daily_report/REPORT-2026-09-27.md",
        r"生成\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
    for p, v in report.items():
        print(f"{p}: {v}")
    for p, keys in drift.items():
        print(f"  drift {p}: keys={keys}")
    # post-write parse validation (r185 law)
    for p in report:
        if p.endswith(".json"):
            json.load(open(p, encoding="utf-8-sig"))
    print("ALL RESOLVED + PARSE-VALIDATED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
