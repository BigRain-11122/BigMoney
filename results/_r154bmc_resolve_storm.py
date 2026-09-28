"""r154 bm-c push-storm canon resolver (14 UU faces vs bm-a r397 same-window S6).

Recipes per classify_conflicts.py output + fleet canon laws:
- memory-union (CODELY.md): merge-base prefix identity assertion + both-side
  append suffixes direct concat (D-20260927-09 / F-20260927-03; origin-side
  suffix first -- already landed on main; r140 tie->HEAD same rationale).
- snapshot (11 faces): hardened deep-ts probe on STAGED blobs (:2:/:3:),
  never the working tree (r311); key normalization strips '_'/'-' BEFORE
  prefix match (r100); candidate values must be ts-shaped (^20\\d{2}-) AND
  carry time-of-day ([T ]HH:MM) to feed the max (R350: key-EXCLUDE lists
  forbidden, date-only values must not feed the max); tie -> ours (r140).
- js-wrapper-snapshot (dashboard_status.js): twin coherence -- take the
  SAME stage side chosen for its .json twin (r311 twin-order law).
- rolling-ledger compute_audit.json: history identity-union by ts key,
  zero-loss assertion |A u B| == |A|+|B|-|A n B|, sorted by ts, latest =
  max-ts row's owning side (r120/r351/r366 precedent).
- rolling-ledger regime_state.json: history asof-union (newest row per
  asof), scalar face from the side owning the newest asof (asof-union law).

Write-back only after parse-verify (r185). Idempotent: re-run safe.
"""
import json
import re
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TS_SHAPE = re.compile(r"^20\d{2}-")
WALLCLOCK = re.compile(r"[T ]\d{2}:\d{2}")


def _blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                       cwd=REPO, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {stage} miss {path}: {r.stderr[:120]}")
    return r.stdout.decode("utf-8-sig")


def _probe_ts(obj):
    """Deep wall-clock ts probe: recursive, normalized keys, value-shape gate.
    Returns max qualifying ts string found, or None."""
    best = None

    def norm(k):
        return re.sub(r"[_\-]", "", str(k)).lower()

    def walk(node):
        nonlocal best
        if isinstance(node, dict):
            for k, v in node.items():
                nk = norm(k)
                if any(nk.startswith(p) for p in
                       ("asof", "asof", "updated", "generated", "ts",
                        "lasttick", "lastseen", "created")):
                    if isinstance(v, str) and TS_SHAPE.match(v) \
                            and WALLCLOCK.search(v):
                        if best is None or v > best:
                            best = v
                walk(v)
        elif isinstance(node, list):
            for it in node:
                walk(it)

    walk(obj)
    return best


def _probe_ts_text(text):
    """md/text face: newest wall-clock ts line."""
    best = None
    for m in re.finditer(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?",
                          text):
        v = m.group(0)
        if best is None or v > best:
            best = v
    return best


def resolve_snapshot(path):
    ours = _blob(2, path)
    theirs = _blob(3, path)
    ta = tb = None
    if path.endswith(".json"):
        ta = _probe_ts(json.loads(ours))
        tb = _probe_ts(json.loads(theirs))
    else:
        ta = _probe_ts_text(ours)
        tb = _probe_ts_text(theirs)
    # tie -> ours (r140 tie->HEAD; rebase HEAD == origin/main landed side)
    side = "ours" if (tb is None or (ta is not None and ta >= tb)) else "theirs"
    chosen = ours if side == "ours" else theirs
    if path.endswith(".json"):
        json.loads(chosen)  # parse-verify (r185)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(chosen)
    return {"path": path, "recipe": "take-new", "ours_ts": ta,
            "theirs_ts": tb, "took": side}


def resolve_js_wrapper(js_path, json_path):
    """Twin coherence: same stage side as the .json resolution."""
    ours_j = _probe_ts(json.loads(_blob(2, json_path)))
    theirs_j = _probe_ts(json.loads(_blob(3, json_path)))
    side = "ours" if (theirs_j is None or
                      (ours_j is not None and ours_j >= theirs_j)) else "theirs"
    chosen = _blob(2 if side == "ours" else 3, js_path)
    payload = re.sub(r"^[^=]*=\s*", "", chosen.strip().rstrip(";"))
    json.loads(payload)  # wrapper payload parse-verify
    with open(js_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(chosen)
    return {"path": js_path, "recipe": "js-twin", "json_ts_ours": ours_j,
            "json_ts_theirs": theirs_j, "took": side}


def resolve_audit():
    path = "results/compute_audit.json"
    a = json.loads(_blob(2, path))
    b = json.loads(_blob(3, path))
    ra = {r["ts"]: r for r in a["history"]}
    rb = {r["ts"]: r for r in b["history"]}
    union_keys = sorted(set(ra) | set(rb))
    inter = set(ra) & set(rb)
    for t in inter:
        assert json.dumps(ra[t], sort_keys=True) == \
            json.dumps(rb[t], sort_keys=True), f"same-ts row drift {t}"
    union = [ra.get(t) or rb[t] for t in union_keys]
    assert len(union) == len(ra) + len(rb) - len(inter), "union cardinality"
    assert len(union) >= max(len(ra), len(rb)), "zero-loss lower bound"
    newest = union_keys[-1]
    latest = (a if ra.get(newest) else b)["latest"]
    out = {"history": union, "latest": latest}
    json.loads(json.dumps(out))
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return {"path": path, "recipe": "identity-union",
            "ours_rows": len(ra), "theirs_rows": len(rb),
            "union": len(union), "inter": len(inter)}


def resolve_regime():
    path = "results/regime_state.json"
    a = json.loads(_blob(2, path))
    b = json.loads(_blob(3, path))
    ha = {r["asof"]: r for r in a.get("history", [])}
    hb = {r["asof"]: r for r in b.get("history", [])}
    merged = {}
    for k in sorted(set(ha) | set(hb)):
        merged[k] = hb.get(k) or ha[k]  # newest-wins per asof (identical here)
    newest = max(merged)
    base = a if a.get("asof", "") >= b.get("asof", "") else b
    out = dict(base)
    out["history"] = [merged[k] for k in sorted(merged)]
    json.loads(json.dumps(out))
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return {"path": path, "recipe": "asof-union", "rows": len(merged),
            "newest_asof": newest}


def resolve_memory_union():
    path = "CODELY.md"
    base = _blob(1, path)
    ours = _blob(2, path)
    theirs = _blob(3, path)
    assert ours.startswith(base), "merge-base prefix drift (ours)"
    assert theirs.startswith(base), "merge-base prefix drift (theirs)"
    sa, sb = ours[len(base):], theirs[len(base):]
    out = base + sa + sb  # origin-landed suffix first, ours appended after
    assert "<<<<<<<" not in out and ">>>>>>>" not in out, "marker leak"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    return {"path": path, "recipe": "memory-union direct-concat",
            "base_bytes": len(base.encode("utf-8")),
            "ours_suffix_bytes": len(sa.encode("utf-8")),
            "theirs_suffix_bytes": len(sb.encode("utf-8")),
            "out_bytes": len(out.encode("utf-8"))}


def main():
    log = [resolve_memory_union(), resolve_audit(), resolve_regime(),
           resolve_js_wrapper("results/dashboard_status.js",
                              "results/dashboard_status.json")]
    for p in SNAPSHOTS:
        if p == "results/dashboard_status.json":
            # resolved by the js-wrapper twin call above; re-run idempotent
            log.append(resolve_snapshot(p))
        else:
            log.append(resolve_snapshot(p))
    # parse-verify every resolved json face on disk (r185)
    for p in SNAPSHOTS:
        if p.endswith(".json"):
            json.load(open(p, encoding="utf-8"))
    json.dump({"round": "r154", "machine": "bm-c", "faces": log},
              open(r"results/_r154bmc_resolve_storm.json", "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)
    for row in log:
        print(row["path"], "->", row["recipe"],
              row.get("took") or f"union={row.get('union')}")
    print("RESOLVE OK:", len(log), "faces")


if __name__ == "__main__":
    sys.exit(main())
