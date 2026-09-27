"""r351 bm-b rebase-conflict resolver (bigmoney-conflict-resolve skill recipes).

Families handled (classifier-first; per-face identity keys probed, never
hardcoded -- r360 law):
  runnable_pool.json    entries union by entry-id identity; same-id merge =
                       done-flip precedence (r180), then freshest shard
                       owner_since; |union| == |A_ids u B_ids| assertion.
  autofill_state.json   launches union (per-face row identity probe) -> ts
                       desc cap 50 (keep-newest semantics) -> re-sort ts asc
                       before write (r245); last_tick = whole-dict by internal
                       ts compare, same-second tie -> HEAD/ours (r140);
                       newline+indent mirrored from the base blob (r223/r234).
  p1d_gates.json        snapshot -> take-new (latest meta.date).

Usage:  python results/_r351bmb_resolve.py <path>
Stages :2 (ours/onto) and :3 (theirs/replayed) are read via git show bytes.
Zero-network, deterministic; parse-verify before write (r185).
"""
import json
import subprocess
import sys


def _stage(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None, None
    b = r.stdout
    try:
        return json.loads(b.decode("utf-8")), b
    except Exception:
        return None, b


def _probe_newline(blob: bytes) -> bool:
    return b"\r\n" in blob[:4000]


def _write(path, obj, crlf):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    if crlf:
        data = open(path, "rb").read().replace(b"\n", b"\r\n")
        open(path, "wb").write(data)


def _resolve_pool(path):
    ours, ob = _stage(path, 2)
    theirs, tb = _stage(path, 3)
    if ours is None or theirs is None:
        print(f"SKIP {path}: a stage unparseable (manual face)")
        return False
    a = {e["id"]: e for e in ours.get("entries", [])}
    b = {e["id"]: e for e in theirs.get("entries", [])}
    merged = {}
    for k in sorted(set(a) | set(b)):
        ea, eb = a.get(k), b.get(k)
        if ea is None:
            merged[k] = eb
            continue
        if eb is None or json.dumps(ea, sort_keys=True) == json.dumps(eb, sort_keys=True):
            merged[k] = ea
            continue

        # same-id divergence: done-flip precedence, then freshest owner_since
        def _rank(e):
            owners = [s.get("owner_since") or "" for s in e.get("shards", [])]
            return (1 if e.get("status") == "done" else 0,
                    max(owners) if owners else "")
        merged[k] = ea if _rank(ea) >= _rank(eb) else eb
    union_ids = set(a) | set(b)
    assert set(merged) == union_ids and len(merged) == len(union_ids), \
        "pool identity-union assertion failed"
    out = dict(ours)
    out["entries"] = [merged[k] for k in sorted(merged)]
    _write(path, out, _probe_newline(ob))
    print(f"pool union: |A|={len(a)} |B|={len(b)} |AuB|={len(merged)}")
    return True


def _resolve_autofill(path):
    ours, ob = _stage(path, 2)
    theirs, tb = _stage(path, 3)
    if ours is None or theirs is None:
        print(f"SKIP {path}: a stage unparseable (manual face)")
        return False
    out = dict(ours)
    la, lb = ours.get("launches", []), theirs.get("launches", [])
    if la:
        keys = [k for k in ("ts", "machine", "entry", "shard", "verdict", "cmd")
                if k in la[0]]
        def ident(r):
            return tuple(r.get(k) for k in keys)
    else:
        def ident(r):
            return json.dumps(r, sort_keys=True)
    seen, union = set(), []
    for r in sorted(la + lb, key=lambda r: str(r.get("ts", ""))):
        i = ident(r)
        if i in seen:
            continue
        seen.add(i)
        union.append(r)
    union.sort(key=lambda r: str(r.get("ts", "")), reverse=True)
    union = union[:50]                       # cap semantics = keep newest 50
    union.sort(key=lambda r: str(r.get("ts", "")))   # producer order = ts asc
    out["launches"] = union
    ta, tbt = ours.get("last_tick"), theirs.get("last_tick")
    if isinstance(tbt, dict) and (ta is None or
                                  str(tbt.get("ts", "")) > str(ta.get("ts", ""))):
        out["last_tick"] = tbt
    assert isinstance(out.get("last_tick"), dict), "last_tick not a dict"
    _write(path, out, _probe_newline(ob))
    print(f"autofill_state: launches |A|={len(la)} |B|={len(lb)} -> "
          f"{len(union)}; last_tick ts={out['last_tick'].get('ts')}")
    return True


def _resolve_snapshot_new(path):
    ours, ob = _stage(path, 2)
    theirs, tb = _stage(path, 3)
    if ours is None or theirs is None:
        print(f"SKIP {path}: a stage unparseable (manual face)")
        return False
    da = str((ours.get("meta") or {}).get("date", ""))
    db = str((theirs.get("meta") or {}).get("date", ""))
    take = theirs if db >= da else ours
    _write(path, take, _probe_newline(ob))
    print(f"{path}: take-new date {max(da, db)}")
    return True


FAMILIES = {
    "results/runnable_pool.json": _resolve_pool,
    "results/autofill_state.json": _resolve_autofill,
    "results/p1d_gates.json": _resolve_snapshot_new,
}


def main():
    path = sys.argv[1]
    fn = FAMILIES.get(path)
    if fn is None:
        print(f"UNKNOWN family {path} -- manual classification (fail-closed)")
        return 2
    ok = fn(path)
    json.load(open(path, encoding="utf-8"))     # parse-verify (r185)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
