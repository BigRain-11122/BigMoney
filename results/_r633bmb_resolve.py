"""r633 bm-b merge resolver (push-rejection recovery, bigmoney-conflict-resolve skill).

Collision: bm-b r633 vs origin/main (bm-c r427 x3 + bm-a r640 addendum) same-window
S6 regen of shared faces. Recipes per classifier + manual qualification:
- snapshot / same-day idempotent twin / scan evidence -> take-new by embedded ts
  (verified: stage2=bm-b side is newer on every comparable face; whole-side bytes)
- rolling-ledger (compute_audit history, regime_state lists) -> zero-loss union by
  row identity + take-new scalar/latest fields (law r188/R208/R216; tie->HEAD r140)
"""
import json
import re
import subprocess
import sys

MARKER_RE = re.compile(r"^(<<<<<<<|=======|>>>>>>>)", re.M)
SNAPSHOT_TAKE_SIDE = {
    "results/update_status.json": 2,
    "results/lhb_update_status.json": 2,
    "results/futures_update_status.json": 2,
    "results/fundamental_b_layer_filter.json": 2,
    "results/_attrition_guard_scan.json": 2,
    "docs/daily_report/REPORT-2026-10-03.json": 2,
    "docs/daily_report/REPORT-2026-10-03.md": 2,
}


def stage_bytes(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"stage read fail {path} stage {stage}")
    return out.stdout


def row_key(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)


def union_lists(mine, theirs):
    seen, merged = set(), []
    for row in theirs + mine:  # mine last so identical rows keep mine
        k = row_key(row)
        if k not in seen:
            seen.add(k)
            merged.append(row)
    return merged


def dump_json(obj, ref_bytes):
    txt = json.dumps(obj, indent=2, ensure_ascii=False)
    if b"\r\n" in ref_bytes:
        txt = txt.replace("\n", "\r\n")
    return txt.encode("utf-8")


def main():
    receipt = {}
    for path, side in SNAPSHOT_TAKE_SIDE.items():
        data = stage_bytes(side, path)
        if MARKER_RE.search(data.decode("utf-8", errors="replace")):
            raise SystemExit(f"marker-bearing side refused: {path} stage {side}")
        other = stage_bytes(3 if side == 2 else 2, path)
        with open(path, "wb") as fh:
            fh.write(data)
        receipt[path] = f"take-stage{side}-bytes ({len(data)}B, other {len(other)}B)"

    # compute_audit.json: history union by ts identity, latest take-new (mine newer)
    p = "results/compute_audit.json"
    a, b = stage_bytes(2, p), stage_bytes(3, p)
    da, db = json.loads(a), json.loads(b)
    hist = {}
    for row in db["history"] + da["history"]:
        hist[row["ts"]] = row  # mine overwrites same-ts (tie->HEAD)
    merged = da if da["latest"]["ts"] >= db["latest"]["ts"] else db
    merged["history"] = sorted(hist.values(), key=lambda r: r["ts"])
    assert len(merged["history"]) >= max(len(da["history"]), len(db["history"]))
    with open(p, "wb") as fh:
        fh.write(dump_json(merged, a))
    receipt[p] = f"union history {len(da['history'])}+{len(db['history'])}->{len(merged['history'])}, latest ts {merged['latest']['ts']}"

    # regime_state.json: list union zero-loss, scalars take-new by updated
    p = "results/regime_state.json"
    a, b = stage_bytes(2, p), stage_bytes(3, p)
    da, db = json.loads(a), json.loads(b)
    merged = da if da["updated"] >= db["updated"] else db
    for key in ("triggers", "transitions", "history"):
        base = da if merged is da else db
        other = db if merged is da else da
        u = union_lists(base.get(key, []), other.get(key, []))
        assert len(u) >= max(len(base.get(key, [])), len(other.get(key, [])))
        merged[key] = u
    with open(p, "wb") as fh:
        fh.write(dump_json(merged, a))
    receipt[p] = f"union lists, updated {merged['updated']}"

    # post-write validation: every resolved file parses, no markers anywhere
    for path in list(SNAPSHOT_TAKE_SIDE) + ["results/compute_audit.json", "results/regime_state.json"]:
        raw = open(path, "rb").read()
        assert not MARKER_RE.search(raw.decode("utf-8", errors="replace")), f"marker in {path}"
        if path.endswith(".json"):
            json.loads(raw.decode("utf-8"))
    print(json.dumps(receipt, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
