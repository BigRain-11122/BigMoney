"""r340 bm-b rebase-stop forensics: reconstruct sides (blind-add destroyed :1:/:2:/:3:) and
zero-loss audit staged content vs canonical union recipes (r335/r336 law, SKILL.md). READ-ONLY."""
import subprocess, json, sys

def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def jload(b):
    if b is None:
        return None
    try:
        return json.loads(b.decode("utf-8"))
    except Exception as e:
        return {"__parse_error__": str(e)}

BASE, OURS, THEIRS = "557b8cce", "aee0fa02", "fc0e784b"
FILES = ["results/autofill_state.json", "results/runnable_pool.json",
         "results/compute_audit.json", "results/regime_state.json",
         "results/astock_daily_update_status.json"]

def rowkey(row, cand_keysets):
    """Try composite keysets in order; return (keyset_name, key_tuple)."""
    for name, fields in cand_keysets:
        try:
            return name, tuple(row.get(f) for f in fields)
        except Exception:
            continue
    return "fallback:str", (json.dumps(row, sort_keys=True)[:120],)

def ledger_audit(name, sides, keysets, label):
    """Union audit: staged/worktree must be a superset of ours UNION theirs, dedup by composite key."""
    print(f"--- {name} ({label}) ---")
    sets = {}
    for tag in ("base", "ours", "theirs", "staged"):
        d = sides.get(tag)
        if d is None:
            print(f"  {tag}: ABSENT")
            continue
        rows = d if isinstance(d, list) else None
        if rows is None:
            print(f"  {tag}: not-a-list type={type(d).__name__} keys={list(d)[:8] if isinstance(d, dict) else '?'}")
            continue
        ks = {}
        for r in rows:
            kn, k = rowkey(r, keysets)
            ks.setdefault(kn, {})
            ks[kn][k] = r
        sets[tag] = ks
        kn0 = list(ks)[0] if ks else "-"
        print(f"  {tag}: rows={len(rows)} dedup[{kn0}]={len(ks.get(kn0, {}))} first_ts={rows[0].get('ts') if rows and isinstance(rows[0], dict) else '?'} last_ts={rows[-1].get('ts') if rows and isinstance(rows[-1], dict) else '?'}")
    if "ours" in sets and "theirs" in sets and "staged" in sets:
        kn0 = list(sets["ours"])[0]
        o, t, s = sets["ours"][kn0], sets["theirs"][kn0], sets["staged"][kn0]
        union = dict(o); union.update(t)
        missing = [k for k in union if k not in s]
        only_staged = [k for k in s if k not in union]
        print(f"  UNION[{kn0}]: |ours|={len(o)} |theirs|={len(t)} |ours∪theirs|={len(union)} |staged|={len(s)}")
        print(f"  staged MISSING from union: {len(missing)} -> {missing[:6]}")
        print(f"  staged-only (post-18:48 tick appends legit): {len(only_staged)} -> {only_staged[:6]}")
        print(f"  VERDICT: {'ZERO-LOSS-OK' if not missing else 'LOSS-DETECTED'}")

for path in FILES:
    print(f"===== {path} =====")
    sides = {}
    for tag, rev in (("base", BASE), ("ours", OURS), ("theirs", THEIRS)):
        sides[tag] = jload(blob(rev, path))
    sides["staged"] = jload(blob(":0", path) if blob(":"+path, path) is None else None) if False else jload(subprocess.run(["git", "show", f":0:{path}"], capture_output=True).stdout or None)
    try:
        with open(path, "rb") as f:
            sides["worktree"] = jload(f.read())
    except FileNotFoundError:
        sides["worktree"] = None
    # top-level shape
    top = {}
    for tag in ("base", "ours", "theirs", "staged", "worktree"):
        d = sides.get(tag)
        if isinstance(d, dict):
            top[tag] = {k: (f"list[{len(v)}]" if isinstance(v, list) else type(v).__name__[:6] + (f"={v}" if not isinstance(v, (dict, list)) else "")) for k, v in list(d.items())[:12]}
        else:
            top[tag] = "ABSENT/parse-err"
    print(f"  top-level: {json.dumps(top, ensure_ascii=False, default=str)[:900]}")
    if path.endswith("autofill_state.json"):
        ledger_audit("launches", {t: (sides[t] or {}).get("launches") if isinstance(sides[t], dict) else None for t in sides},
                     [("id+ts", ("id", "ts")), ("batch_id+ts", ("batch_id", "ts")), ("label+ts", ("label", "ts")), ("ts", ("ts",))], "mixed-dict+ledger")
        for tag in ("ours", "theirs", "staged"):
            lt = (sides[tag] or {}).get("last_tick") if isinstance(sides[tag], dict) else None
            if isinstance(lt, dict):
                print(f"  last_tick[{tag}]: ts={lt.get('ts')} id={lt.get('id') or lt.get('batch_id')} epoch={lt.get('epoch_utc') or lt.get('epoch')}")
            else:
                print(f"  last_tick[{tag}]: {type(lt).__name__} {str(lt)[:80]}")
    if path.endswith("compute_audit.json"):
        d = sides.get("staged") or {}
        for k, v in (d.items() if isinstance(d, dict) else []):
            if isinstance(v, list) and len(v) > 3:
                ledger_audit(k, {t: (sides[t] or {}).get(k) if isinstance(sides[t], dict) else None for t in sides},
                             [("ts", ("ts",)), ("asof+ts", ("asof", "ts")), ("key", ("key", "ts"))], "rolling-ledger")
    if path.endswith("regime_state.json"):
        d = sides.get("staged") or {}
        for k, v in (d.items() if isinstance(d, dict) else []):
            if isinstance(v, list) and len(v) > 3:
                ledger_audit(k, {t: (sides[t] or {}).get(k) if isinstance(sides[t], dict) else None for t in sides},
                             [("ts", ("ts",)), ("date", ("date", "ts")), ("asof", ("asof",))], "rolling-ledger")
    if path.endswith("runnable_pool.json"):
        for tag in ("ours", "theirs", "staged", "worktree"):
            d = sides.get(tag)
            if isinstance(d, dict):
                items = d.get("batches") or d.get("pool") or d.get("items")
                if isinstance(items, list):
                    print(f"  pool[{tag}]: n={len(items)} ids={[ (i.get('id') or i.get('batch_id') or '?') for i in items ][:8]}")
                else:
                    print(f"  pool[{tag}]: dict keys={list(d)[:10]}")
                    for k2, v2 in list(d.items())[:6]:
                        vdesc = ("list[%d]" % len(v2)) if isinstance(v2, list) else str(v2)[:100]
                        print(f"    {k2}: {vdesc}")
            elif isinstance(d, list):
                print(f"  pool[{tag}]: list n={len(d)} ids=[{(i.get('id') or i.get('batch_id') or '?') for i in d if isinstance(i, dict)}] sample={json.dumps(d[0], ensure_ascii=False, default=str)[:200] if d else ''}")
print("FORENSICS-DONE")
