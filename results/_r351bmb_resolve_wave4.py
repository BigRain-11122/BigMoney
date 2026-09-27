"""r351 bm-b wave-4 resolver: 19-UU derived-snapshot storm (bm-c r121 + bm-a r369 same window).
Recipes per classifier: pool identity-union / autofill mixed-union /
rolling-ledger identity-union (per-face keys) / CODELY remove+append union
(both sides archived different entries) / archive direct-concat / deep-ts
take-new snapshots / REPORT twins same-side.
Zero-network deterministic; parse-verify before write (r185).
"""
import json, subprocess, sys

def stage(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None, None
    b = r.stdout
    try:
        return json.loads(b.decode("utf-8")), b
    except Exception:
        return None, b

def crlf(blob):
    return b"\r\n" in blob[:4000]

def wjson(path, obj, blob, indent=1):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)
    if crlf(blob):
        d = open(path, "rb").read().replace(b"\n", b"\r\n")
        open(path, "wb").write(d)

def wbytes(path, data):
    open(path, "wb").write(data)

def deep_ts(obj, _best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("ts", "generated", "asof", "generated_at", "date") and isinstance(v, str):
                _best = max(_best, v)
            _best = deep_ts(v, _best)
    elif isinstance(obj, list):
        for v in obj:
            _best = deep_ts(v, _best)
    return _best

def take_new(path, blob2=None, blob3=None):
    a, b2 = stage(path, 2)
    b, b3 = stage(path, 3)
    if b2 is None:
        b2 = subprocess.run(["git", "show", ":2:" + path], capture_output=True).stdout
    if b3 is None:
        b3 = subprocess.run(["git", "show", ":3:" + path], capture_output=True).stdout
    if a is None or b is None:
        wbytes(path, b2 if deep_ts_blob(b2) >= deep_ts_blob(b3) else b3)
        return "take-bytes"
    ta, tb = deep_ts(a), deep_ts(b)
    win = 2 if ta >= tb else 3
    data = b2 if win == 2 else b3
    wbytes(path, data)
    return f"take side{win} ts {max(ta, tb)}"

def deep_ts_blob(b):
    try:
        return deep_ts(json.loads(b.decode("utf-8")))
    except Exception:
        return ""

def resolve_pool(path):
    ours, ob = stage(path, 2)
    theirs, tb = stage(path, 3)
    a = {e["id"]: e for e in ours.get("entries", [])}
    b = {e["id"]: e for e in theirs.get("entries", [])}
    merged = {}
    for k in sorted(set(a) | set(b)):
        ea, eb = a.get(k), b.get(k)
        if ea is None:
            merged[k] = eb; continue
        if eb is None or json.dumps(ea, sort_keys=True) == json.dumps(eb, sort_keys=True):
            merged[k] = ea; continue
        def rank(e):
            ow = [s.get("owner_since") or "" for s in e.get("shards", [])]
            return (1 if e.get("status") == "done" else 0, max(ow) if ow else "")
        merged[k] = ea if rank(ea) >= rank(eb) else eb
    ids = set(a) | set(b)
    assert set(merged) == ids and len(merged) == len(ids)
    out = dict(ours); out["entries"] = [merged[k] for k in sorted(merged)]
    wjson(path, out, ob)
    return f"pool |A|={len(a)} |B|={len(b)} -> {len(merged)}"

def resolve_autofill(path):
    ours, ob = stage(path, 2)
    theirs, tb = stage(path, 3)
    out = dict(ours)
    la, lb = ours.get("launches", []), theirs.get("launches", [])
    keys = [k for k in ("ts", "machine", "entry", "shard", "verdict", "cmd")
            if la and k in la[0]]
    def ident(r):
        return tuple(r.get(k) for k in keys) if keys else json.dumps(r, sort_keys=True)
    seen, union = set(), []
    for r in sorted(la + lb, key=lambda r: str(r.get("ts", ""))):
        i = ident(r)
        if i in seen: continue
        seen.add(i); union.append(r)
    union.sort(key=lambda r: str(r.get("ts", "")), reverse=True)
    union = union[:50]
    union.sort(key=lambda r: str(r.get("ts", "")))
    out["launches"] = union
    ta, tbt = ours.get("last_tick"), theirs.get("last_tick")
    if isinstance(tbt, dict) and (ta is None or str(tbt.get("ts", "")) > str(ta.get("ts", ""))):
        out["last_tick"] = tbt
    assert isinstance(out.get("last_tick"), dict)
    wjson(path, out, ob)
    return f"autofill {len(la)}+{len(lb)}->{len(union)} last_tick {out['last_tick'].get('ts')}"

def resolve_ledger(path, ledger_keys):
    ours, ob = stage(path, 2)
    theirs, tb = stage(path, 3)
    out = dict(ours)
    for key in ledger_keys:
        la, lb = ours.get(key, []), theirs.get(key, [])
        if not isinstance(la, list): continue
        if la:
            probe = la[0]
            idk = [k for k in ("ts", "asof", "date", "machine") if isinstance(probe, dict) and k in probe]
            def ident(r):
                return tuple(r.get(k) for k in idk) if idk else json.dumps(r, sort_keys=True)
        else:
            def ident(r):
                return json.dumps(r, sort_keys=True)
        seen, u = set(), []
        for r in sorted(la + lb, key=lambda x: json.dumps(x, sort_keys=True)):
            i = ident(r)
            if i in seen: continue
            seen.add(i); u.append(r)
        out[key] = u
    wjson(path, out, ob)
    return f"ledger {ledger_keys} unioned"

def resolve_codely(path):
    def raw(n):
        return subprocess.run(["git", "show", f":{n}:{path}"],
                              capture_output=True).stdout.decode("utf-8")
    base, A, B = raw(1), raw(2), raw(3)
    if not base or not A or not B:
        return "CODELY manual (empty stage)"
    bl = base.split("\n"); al = A.split("\n"); bl3 = B.split("\n")
    import difflib
    def diffs(x, y):
        sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
        removed, added = [], []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("delete", "replace"):
                removed.extend(x[i1:i2])
            if tag in ("insert", "replace"):
                added.extend(y[j1:j2])
        return removed, added
    remA, addA = diffs(bl, al)
    remB, addB = diffs(bl, bl3)
    remset = set(remA) | set(remB)
    keep = [l for l in bl if l not in remset]
    added = addA + [l for l in addB if l not in set(addA)]
    out = keep + added
    text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    wbytes(path, text.encode("utf-8"))
    assert "### User" in text and "CEO" in text
    assert len(text.encode("utf-8")) <= 10240, f"CODELY over hard line {len(text.encode('utf-8'))}"
    return f"CODELY keep={len(keep)} added={len(added)} rem={len(remset)} bytes={len(text.encode('utf-8'))}"

def resolve_concat(path):
    base, bb = stage(path, 1)
    A = subprocess.run(["git", "show", ":2:" + path], capture_output=True).stdout
    B = subprocess.run(["git", "show", ":3:" + path], capture_output=True).stdout
    base = base or b""
    def suffix(side):
        return side[len(base):] if side.startswith(base) else None
    sa, sb = suffix(A), suffix(B)
    if sa is None or sb is None:
        # prefix identity failed: union by line-set tails
        bl = base.decode("utf-8").split("\n")
        al = A.decode("utf-8").split("\n"); b3l = B.decode("utf-8").split("\n")
        import difflib
        def tail(x):
            sm = difflib.SequenceMatcher(None, bl, x, autojunk=False)
            j = 0
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == "equal" and i1 == 0:
                    j = j2
            return x[j:]
        ta, tb_ = tail(al), tail(b3l)
        out = bl + ta + tb_
        text = "\n".join(out)
        wbytes(path, text.encode("utf-8"))
        return f"concat via line-tail a={len(ta)} b={len(tb_)}"
    out = base + sa + sb
    wbytes(path, out)
    return f"concat a={len(sa)} b={len(sb)}"

POOL = "results/runnable_pool.json"
AF = "results/autofill_state.json"

def main():
    done = []
    done.append((POOL, resolve_pool(POOL)))
    done.append((AF, resolve_autofill(AF)))
    done.append(("results/compute_audit.json",
                 resolve_ledger("results/compute_audit.json", ["history"])))
    done.append(("results/regime_state.json",
                 resolve_ledger("results/regime_state.json", ["history", "transitions"])))
    done.append(("CODELY.md", resolve_codely("CODELY.md")))
    done.append(("research/memory-archive/202609.md",
                 resolve_concat("research/memory-archive/202609.md")))
    snaps = ["results/dashboard_status.json",
             "results/fundamental_b_layer_filter.json",
             "results/futures_update_status.json",
             "results/heat_update_status.json",
             "results/lhb_update_status.json",
             "results/prospect_promotion/_summary.json",
             "results/scorecard_v1.json",
             "results/strategy_scorecard.json",
             "results/token_usage.json",
             "results/update_status.json",
             "docs/daily_report/REPORT-2026-09-28.json",
             "docs/daily_report/REPORT-2026-09-28.md",
             "results/dashboard_status.js"]
    j2 = subprocess.run(["git", "show", ":2:docs/daily_report/REPORT-2026-09-28.json"],
                        capture_output=True).stdout
    j3 = subprocess.run(["git", "show", ":3:docs/daily_report/REPORT-2026-09-28.json"],
                        capture_output=True).stdout
    side = 2 if deep_ts_blob(j2) >= deep_ts_blob(j3) else 3
    for p in snaps:
        if p.endswith("REPORT-2026-09-28.json") or p.endswith("REPORT-2026-09-28.md"):
            data = subprocess.run(["git", "show", f":{side}:{p}"], capture_output=True).stdout
            wbytes(p, data)
            done.append((p, f"twin side{side}"))
        else:
            done.append((p, take_new(p, None, None)))
    for p, msg in done:
        print(f"{p}: {msg}")
    # parse-verify all json outputs (r185)
    for p in [x[0] for x in done] + [POOL, AF]:
        if p.endswith(".json"):
            json.load(open(p, encoding="utf-8"))
    print("ALL RESOLVED + parse-verified")

if __name__ == "__main__":
    main()
