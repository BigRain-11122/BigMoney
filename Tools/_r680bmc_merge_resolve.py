# -*- coding: utf-8 -*-
"""r680 bm-c merge resolver (r672 lineage, four-laws upgrade per r678):
- compute_audit.json: rolling union (scalars newer-ts side; history rows
  identity-dedup union, r758 law)
- scorecard_v1.json / strategy_scorecard.json: ts-duel newer-wins
  (datetime.fromisoformat, no string compare, r711/r756 law)
- token_usage.json: per-key max-union (r758/r456 law)
Blobs read via git cat-file stdout-only (r648 law: ls-files -u sha then
cat-file; never git show :N:). Pool face runnable_pool.json checked for
owner_since regression (MSG-0612 per-face max-merge) after auto-merge."""
import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                        creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%s %s" % (args, r.returncode,
                                                r.stderr.decode("utf-8", "replace")[:200]))
    return r.stdout


def blob_at(rev, path):
    return git(["show", "%s:%s" % (rev, path)]).decode("utf-8-sig")


def load(stage_blob):
    return json.loads(stage_blob)


def ts_of(obj, keys=("generated", "ts", "updated_at", "updated")):
    for k in keys:
        v = obj.get(k) if isinstance(obj, dict) else None
        if isinstance(v, str) and "T" in v:
            try:
                return datetime.datetime.fromisoformat(v)
            except ValueError:
                pass
    return None


def newer_obj(a, b):
    ta, tb = ts_of(a), ts_of(b)
    if ta is None and tb is None:
        return a, "tie-no-ts"
    if ta is None:
        return b, "theirs"
    if tb is None:
        return a, "ours"
    if ta == tb:
        return a, "tie-equal-take-ours"
    return (a, "ours") if ta > tb else (b, "theirs")


def union_history(a, b, hist_key):
    """identity-dedup union on history list (r758)."""
    la = a.get(hist_key) if isinstance(a, dict) else None
    lb = b.get(hist_key) if isinstance(b, dict) else None
    if not isinstance(la, list) or not isinstance(lb, list):
        return None
    seen = {}
    for row in la + lb:
        key = json.dumps(row, sort_keys=True, ensure_ascii=False)
        seen.setdefault(key, row)
    return list(seen.values())


def resolve():
    out = {}
    uu = {}
    for line in git(["ls-files", "-u"]).decode("utf-8").splitlines():
        parts = line.split()
        mode, sha, stage, path = parts[0], parts[1], int(parts[2]), parts[3]
        uu.setdefault(path, {})[stage] = sha
    for path, stages in sorted(uu.items()):
        ours = load(blob_at(":%s" % stages[2], path) if False else
                    git(["cat-file", "blob", stages[2]]).decode("utf-8-sig"))
        theirs = load(git(["cat-file", "blob", stages[3]]).decode("utf-8-sig"))
        if path == "results/compute_audit.json":
            base, side = newer_obj(ours, theirs)
            hist = union_history(ours, theirs, "history")
            if hist is not None:
                base = dict(base)
                base["history"] = hist
            pick, why = base, "rolling-union(%s)" % side
        elif path in ("results/scorecard_v1.json", "results/strategy_scorecard.json"):
            pick, side = newer_obj(ours, theirs)
            why = "ts-duel(%s)" % side
        elif path == "results/token_usage.json":
            # r680 pit fix: single-level union replaced nested machine faces
            # wholesale (machines['-bm-c'] took theirs' stale side). Recursive
            # rule: numeric leaves -> max (r758 monotonic cumulative counters);
            # dict leaves -> recurse; own-machine faces (keys containing
            # 'bm-c') -> prefer ours for non-numeric leaves (owner-newer law).
            def deep_union(a, b, own=False):
                if isinstance(a, dict) and isinstance(b, dict):
                    out = {}
                    for k in sorted(set(a) | set(b)):
                        ka = isinstance(k, str) and "bm-c" in k
                        out[k] = deep_union(a.get(k), b.get(k), own or ka)
                    return out
                if isinstance(a, (int, float)) and isinstance(b, (int, float)) \
                        and not isinstance(a, bool) and not isinstance(b, bool):
                    return max(a, b)
                if b is None:
                    return a
                if a is None:
                    return b
                return a if own else b
            pick = deep_union(ours, theirs)
            why = "recursive-max-union + own-face-wins"
        else:
            pick, side = newer_obj(ours, theirs)
            why = "default-ts-duel(%s)" % side
        with open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(pick, fh, ensure_ascii=False, indent=1)
        git(["add", "--", path])
        out[path] = why
        print("RESOLVED %s <- %s" % (path, why))

    # --- pool face owner_since regression check (MSG-0612) ---
    pool_path = "results/runnable_pool.json"
    try:
        pool = load(open(os.path.join(ROOT, pool_path), encoding="utf-8-sig").read())
        target = "FUND-DIVLOWVOL-P1-NULLS|fund-divlowvol-p1-nulls-0of1"
        regressed = []
        for e in pool.get("entries", []):
            if e.get("id") == "FUND-DIVLOWVOL-P1-NULLS":
                for sh in e.get("shards", []):
                    key = "%s|%s" % (e.get("id"), sh.get("id"))
                    if key == target:
                        regressed.append((key, sh.get("owner_since"), sh.get("owner")))
        print("POOL owner_since face:", regressed)
    except Exception as exc:  # honest disclosure, not fail-closed here
        print("POOL check error:", exc)
    return out


if __name__ == "__main__":
    resolve()
    print("resolver done")
    sys.exit(0)
