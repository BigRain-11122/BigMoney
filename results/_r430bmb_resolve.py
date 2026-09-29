"""r430 bm-b rebase conflict resolver (bm-c r223 vs bm-b r430 replay).

Recipes per bigmoney-conflict-resolve SKILL (classifier output):
- compute_audit.json / regime_state.json : rolling-ledger -> union history rows
  (zero loss, dedupe exact-row identity), snapshot fields take-new by deep ts probe
- fundamental_b_layer_filter.json / futures_update_status.json /
  lhb_update_status.json / update_status.json : snapshot -> take-new whole doc by ts
Laws: r185 parse-verify, r140 same-second tie -> HEAD (ours = base = bm-c side),
r311 deep ts probe, R350 probe staged blob not working tree.
"""
import subprocess, json, os, re

TS_RE = re.compile(r"^20\d{2}-")

def blob(stage, path):
    b = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout
    return json.loads(b.decode("utf-8"))

def deep_ts(d):
    """Deep-scan for newest wall-clock ts value (string starting 20xx-)."""
    best = None
    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for k, v in x.items():
                kk = str(k).replace("_", "").replace("-", "").lower()
                if isinstance(v, str) and TS_RE.match(v) and ("ts" in kk or "time" in kk or "date" in kk or "updated" in kk or "generated" in kk):
                    if best is None or v > best:
                        best = v
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(d)
    return best

def resolve_ledger(path, ledger_keys):
    ours, theirs = blob(2, path), blob(3, path)
    out = dict(ours)  # start from ours (base); state fields decided by ts below
    for key in ledger_keys:
        a_rows = ours.get(key) or []
        t_rows = theirs.get(key) or []
        if not isinstance(a_rows, list):
            continue
        seen = set()
        merged = []
        for r in a_rows + t_rows:
            ident = json.dumps(r, sort_keys=True, ensure_ascii=False)
            if ident not in seen:
                seen.add(ident)
                merged.append(r)
        def rts(r):
            v = deep_ts(r) or ""
            return v
        merged.sort(key=lambda r: (rts(r), json.dumps(r, sort_keys=True)[:40]))
        out[key] = merged
        print(f"  {path}:{key} union |ours|={len(a_rows)} |theirs|={len(t_rows)} -> {len(merged)}")
    # snapshot fields: take-new side by deep ts; same-second tie -> ours (r140)
    ta, tt = deep_ts(ours), deep_ts(theirs)
    newer = theirs if (tt or "") > (ta or "") else ours
    if (tt or "") > (ta or ""):
        print(f"  {path} snapshot take-theirs (ts {ta} -> {tt})")
    else:
        print(f"  {path} snapshot take-ours (base ts {ta} >= theirs {tt}, r140 tie-or-older law)")
    for k in theirs:
        if k not in ledger_keys and k in newer:
            out[k] = newer[k]
    # also fill keys only present in the newer side
    for k in newer:
        if k not in ledger_keys and k not in out:
            out[k] = newer[k]
    return out

def resolve_snapshot(path):
    ours, theirs = blob(2, path), blob(3, path)
    ta, tt = deep_ts(ours), deep_ts(theirs)
    pick = theirs if (tt or "") > (ta or "") else ours
    side = "theirs" if (tt or "") > (ta or "") else "ours"
    print(f"  {path} take-new -> {side} (ours ts={ta} theirs ts={tt})")
    return pick

targets = {
    "results/compute_audit.json": (resolve_ledger, ["history"]),
    "results/regime_state.json": (resolve_ledger, ["history", "transitions"]),
    "results/fundamental_b_layer_filter.json": (resolve_snapshot, None),
    "results/futures_update_status.json": (resolve_snapshot, None),
    "results/lhb_update_status.json": (resolve_snapshot, None),
    "results/update_status.json": (resolve_snapshot, None),
}

for path, (fn, keys) in targets.items():
    out = fn(path, keys) if keys else fn(path)
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    json.loads(txt)  # r185 parse-verify before write
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt + "\n")
    print(f"  WROTE {path} ({len(txt)}B) parse-verify OK")

print("resolver done")
