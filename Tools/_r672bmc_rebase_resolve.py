# -*- coding: utf-8 -*-
"""r672 bm-c rebase-conflict per-face resolver (14-UU, push-race window vs
bm-a r821 wave + bm-b r800 merges).

Laws applied (r440 two-rule + r758 rolling-union + r405 stage-vanish,
from pit canon):
  * compute_audit.json / regime_state.json -> rolling history UNION
    (scalars from newer-ts side, history rows identity-deduped, zero-loss);
  * token_usage.json -> per-key max-union (counter families recursive max,
    scalars from newer generated side) per r758/r456 canon;
  * every other face -> ts-duel newer-wins on extracted max ISO timestamp;
    no ts field -> local side (:3) = fresher local measurement default.
  * Stage semantics: during REBASE stage2=upstream(origin) stage3=replayed
    commit(mine) -- opposite of merge; explicit `git show :N:path`
    materialization only, NEVER checkout --ours/--theirs (r405+semantics
    family). Read stages BEFORE add (stages vanish after add, r405).
Receipt -> results/_r672bmc_rebase_resolve.json. Zero --no-verify."""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000
RECEIPT = os.path.join(ROOT, "results", "_r672bmc_rebase_resolve.json")
UNION_HISTORY_FACES = {"results/compute_audit.json", "results/regime_state.json"}
UNION_MAX_FACES = {"results/token_usage.json"}
TS_PAT = re.compile(
    r'"(?:generated|ts|updated_at|updated|last_run_at|generated_at|asof|scan_ts)"'
    r'\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ][\d:.]+)')


def _git(args):
    r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b""), (r.stderr or b"")


def _stage(path, n):
    rc, out, err = _git(["show", ":%d:%s" % (n, path)])
    if rc != 0:
        return None
    return out


def _max_ts(blob):
    if blob is None:
        return None
    txt = blob.decode("utf-8", errors="replace")
    stamps = TS_PAT.findall(txt)
    return max(stamps) if stamps else None


def _union_history(o2, o3, ts2, ts3):
    """Rolling union: scalars from newer side; history identity-dedup union."""
    base = json.loads(o2) if ts3 >= ts2 else json.loads(o3)
    other = json.loads(o3) if base is not None and ts3 >= ts2 else json.loads(o2)
    # explicit: newer side is base
    if ts3 >= ts2:
        base, other = json.loads(o3), json.loads(o2)
    else:
        base, other = json.loads(o2), json.loads(o3)
    hist_key = None
    for k in ("history",):
        if k in base or k in other:
            hist_key = k
            break
    if hist_key:
        bh = base.get(hist_key) or []
        oh = other.get(hist_key) or []
        seen = set()
        merged = []
        for row in list(bh) + list(oh):
            ident = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if ident not in seen:
                seen.add(ident)
                merged.append(row)
        base[hist_key] = merged
    return base


def _max_union(o2, o3, ts2, ts3):
    """token_usage per-key max: scalars from newer generated side; counter
    dict families recursive numeric max (keys union)."""
    base, other = (json.loads(o3), json.loads(o2)) if ts3 >= ts2 else \
        (json.loads(o2), json.loads(o3))
    for key in ("machines", "l2_local_llm"):
        if key in base and key in other:
            merged = dict(other[key])
            for k, v in base[key].items():
                if k in merged:
                    merged[k] = _num_max(merged[k], v)
                else:
                    merged[k] = v
            base[key] = merged
    return base


def _num_max(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = _num_max(out[k], v) if k in out else v
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return max(a, b)
    return a


def main():
    rc, out, _ = _git(["diff", "--name-only", "--diff-filter=U"])
    files = [f.strip() for f in out.decode("utf-8", "replace").splitlines()
             if f.strip()]
    assert files, "no UU files -- wrong context"
    decisions = []
    for path in files:
        p2 = _stage(path, 2)
        p3 = _stage(path, 3)
        assert p2 is not None and p3 is not None, \
            "stage read fail %s (r405 vanish guard)" % path
        ts2, ts3 = _max_ts(p2), _max_ts(p3)
        if path in UNION_HISTORY_FACES:
            obj = _union_history(p2, p3, ts2, ts3)
            blob = json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8")
            why = "rolling history union (scalars newer=%s, rows identity-dedup zero-loss)" \
                % ("local" if ts3 >= ts2 else "origin")
        elif path in UNION_MAX_FACES:
            obj = _max_union(p2, p3, ts2, ts3)
            blob = json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8")
            why = "per-key max-union (r758/r456 canon, counters recursive max)"
        elif ts2 and ts3:
            side = 3 if ts3 >= ts2 else 2
            blob = p3 if side == 3 else p2
            why = "ts-duel newer-wins (origin=%s local=%s)" % (ts2, ts3)
        else:
            blob = p3
            why = "no-ts default: local fresher measurement (r440)"
        with open(os.path.join(ROOT, path), "wb") as fh:
            fh.write(blob)
        rca, _, erra = _git(["add", "--", path])
        assert rca == 0, "add fail %s: %s" % (path, erra.decode(errors="replace"))
        decisions.append({"path": path, "rule": why,
                          "ts_origin": ts2, "ts_local": ts3})
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"round": 672, "machine": "bm-c",
                   "context": "push-race 14-UU vs bm-a r820/r821 wave + bm-b r800 merges",
                   "n_faces": len(decisions), "faces": decisions},
                  fh, ensure_ascii=False, indent=1)
    for d in decisions:
        print("RESOLVED %-46s (%s)" % (d["path"], d["rule"]))
    print("receipt:", os.path.relpath(RECEIPT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
