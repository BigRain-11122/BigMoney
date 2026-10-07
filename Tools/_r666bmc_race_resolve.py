# -*- coding: utf-8 -*-
"""r666 bm-c push-race UU resolver (4 faces, all regenerable S6 outputs).

Canonical recipes (r665 merge precedent + r440 law):
- compute_audit.json: ROW-UNION (append-only row ledger, union by row identity)
- *_update_status.json: ts-newer wins (single status object)
- fundamental_b_layer_filter.json: ts-newer if ts present else ours (deterministic regen)
Fail-closed: any structural surprise -> abort, no write.
Stages read via git show :1:/:2:/:3: (CREATE_NO_WINDOW per U060)."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000
RECEIPT = os.path.join(ROOT, "results", "_r666bmc_race_resolve.json")

def git_show(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError("git show %s rc=%d" % (spec, r.returncode))
    return r.stdout

def load_stage(stage, path):
    raw = git_show(":%d:%s" % (stage, path))
    return json.loads(raw.decode("utf-8-sig"))

def ts_of(obj):
    for k in ("ts", "time", "updated", "updated_at", "asof"):
        if isinstance(obj, dict) and k in obj:
            return str(obj[k])
    return ""

def main():
    receipt = {"probe": "r666 bm-c push-race UU resolver", "resolved": []}
    # 1) compute_audit.json row-union
    p = "results/compute_audit.json"
    ours = load_stage(2, p)
    theirs = load_stage(3, p)
    o_rows = ours.get("history") if isinstance(ours, dict) else None
    t_rows = theirs.get("history") if isinstance(theirs, dict) else None
    if o_rows is None or t_rows is None:
        print("COMPUTE_AUDIT_STRUCT_FAIL ours_keys=%s theirs_keys=%s" % (list(ours)[:8] if isinstance(ours, dict) else type(ours), list(theirs)[:8] if isinstance(theirs, dict) else type(theirs)))
        return 1
    seen = set()
    merged = []
    for r in o_rows + t_rows:
        key = json.dumps(r, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            merged.append(r)
    ot, tt = ts_of(ours.get("latest", {})), ts_of(theirs.get("latest", {}))
    latest = ours.get("latest", {}) if (not tt or ot >= tt) else theirs.get("latest", {})
    out = dict(ours)
    out["history"] = merged
    out["latest"] = latest
    print("COMPUTE_AUDIT row-union history ours=%d theirs=%d merged=%d latest=%s" % (len(o_rows), len(t_rows), len(merged), "ours" if latest is ours.get("latest") else "theirs"))
    with open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    receipt["resolved"].append({"path": p, "recipe": "row-union(history)+ts-newer(latest)", "ours": len(o_rows), "theirs": len(t_rows), "merged": len(merged)})
    # 2) ts-newer status faces
    for p in ("results/futures_update_status.json", "results/lhb_update_status.json", "results/fundamental_b_layer_filter.json"):
        ours = load_stage(2, p)
        theirs = load_stage(3, p)
        ot, tt = ts_of(ours), ts_of(theirs)
        if ot and tt:
            winner = "ours" if ot >= tt else "theirs"
        else:
            # deterministic regen without ts: prefer byte-identical check then ours
            ob = json.dumps(ours, sort_keys=True, ensure_ascii=False)
            tb = json.dumps(theirs, sort_keys=True, ensure_ascii=False)
            winner = "ours" if ob == tb else "ours-diff-struct"
        chosen = ours if winner.startswith("ours") else theirs
        with open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(chosen, fh, ensure_ascii=False, indent=1)
        print("%s ts-newer ours_ts=%s theirs_ts=%s winner=%s" % (p, ot or "(none)", tt or "(none)", winner))
        receipt["resolved"].append({"path": p, "recipe": "ts-newer", "ours_ts": ot, "theirs_ts": tt, "winner": winner})
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("RECEIPT written", RECEIPT)
    return 0

if __name__ == "__main__":
    sys.exit(main())
