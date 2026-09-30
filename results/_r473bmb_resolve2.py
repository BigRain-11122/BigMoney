# r473 bm-b rebase-collision resolver ROUND 2: replay f5b5885f3 onto 3a39cfd77 (bm-a r484)
# sides INVERTED vs round 1: ours(stage2)=bm-a r484 (newer ~18:0x), theirs(stage3)=my r472 (17:4x-17:5x)
import subprocess, json, sys

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    assert r.returncode == 0, ("blob fail", stage, path)
    return r.stdout

def wb(path, data):
    with open(path, "wb") as f:
        f.write(data)

TS_KEYS = ["generated", "generated_at", "updated", "updated_at", "ts", "asof", "scan_time"]

def ts_probe(obj, depth=0):
    hits = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (str, int, float)) and k in TS_KEYS:
                hits[k] = str(v)
            elif isinstance(v, dict) and depth < 2:
                for kk, vv in ts_probe(v, depth + 1).items():
                    hits[k + "." + kk] = vv
    return hits

rep = {}

SNAP = [
    ("docs/daily_report/REPORT-2026-09-30.json", "docs/daily_report/REPORT-2026-09-30.md"),
    ("docs/live_usage/LIVE-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]
SINGLE = [
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
JS_TWIN = "results/dashboard_status.js"

def pick_newer(path, md_twin=None):
    a, b = blob(2, path), blob(3, path)
    ta = ts_probe(json.loads(a))
    tb = ts_probe(json.loads(b))
    va = max(ta.values()) if ta else ""
    vb = max(tb.values()) if tb else ""
    side = 2 if va >= vb else 3
    data = a if side == 2 else b
    if path.endswith(".js"):
        assert data.lstrip().startswith(b"window.DASH_DATA"), "js wrapper stripped"
    else:
        json.loads(data)
    wb(path, data)
    rep[path] = {"recipe": "take-%s" % ("ours(bm-a-r484)" if side == 2 else "theirs(r472)"),
                 "ts_ours": va, "ts_theirs": vb}
    if md_twin:
        tblob = blob(side, md_twin)
        if md_twin.endswith(".js"):
            assert tblob.lstrip().startswith(b"window.DASH_DATA"), "js wrapper stripped"
        wb(md_twin, tblob)
        rep[md_twin] = {"recipe": "take-%s (paired with json twin)" % ("ours" if side == 2 else "theirs"),
                        "bytes": len(tblob)}

for pair in SNAP:
    pick_newer(pair[0], pair[1])
pick_newer("results/dashboard_status.json", JS_TWIN)
for p in SINGLE:
    pick_newer(p)

# ---- rolling ledgers: identity-keyed union, cap mirror, scalars take-newer side
def fmt_probe(obj, orig_bytes):
    for ind in (2, 1, None, 4):
        for ea in (False, True):
            s = json.dumps(obj, indent=ind, ensure_ascii=ea)
            for crlf in (False, True):
                body = s.replace("\n", "\r\n") if crlf else s
                for tail in ("", "\n", "\r\n"):
                    if (body + tail).encode("utf-8") == orig_bytes:
                        return (ind, ea, crlf, tail)
    return None

def union_ledger(path, listkey, cap=None):
    a = json.loads(blob(2, path))
    b = json.loads(blob(3, path))
    la, lb = a.get(listkey, []), b.get(listkey, [])
    # scalar freshness decides whose base dict wins
    ta = max(ts_probe(a).values()) if ts_probe(a) else ""
    tb = max(ts_probe(b).values()) if ts_probe(b) else ""
    base = a if ta >= tb else b
    ident = lambda it: json.dumps(it, sort_keys=True, ensure_ascii=False)
    merged = {}
    for it in la:
        merged[ident(it)] = it
    for it in lb:
        merged.setdefault(ident(it), it)
    items = list(merged.values())
    rep[path] = {"recipe": "union-" + listkey, "ours_len": len(la), "theirs_len": len(lb),
                 "union_len": len(items), "scalars_from": "ours" if ta >= tb else "theirs",
                 "ts_ours": ta, "ts_theirs": tb}
    tsk = [it.get("ts") for it in items]
    if all(isinstance(t, str) for t in tsk):
        items.sort(key=lambda it: it["ts"], reverse=True)
        if cap and len(items) > cap:
            rep[path]["capped_to"] = cap
            rep[path]["dropped_oldest"] = len(items) - cap
            items = items[:cap]
        ref = [it.get("ts") for it in lb if isinstance(it.get("ts"), str)]
        if ref == sorted(ref):
            items = list(reversed(items))
    final = dict(base)
    final[listkey] = items
    refside = blob(2, path) if base is a else blob(3, path)
    idb = {ident(it) for it in (la if base is a else lb)}
    if {ident(it) for it in items} <= idb and len(items) == len(la if base is a else lb):
        wb(path, refside)
        rep[path]["write"] = "base-side-verbatim (union identical)"
    else:
        fmt = fmt_probe(base, refside)
        assert fmt, ("format probe failed", path)
        ind, ea, crlf, tail = fmt
        body = json.dumps(final, indent=ind, ensure_ascii=ea)
        if crlf:
            body = body.replace("\n", "\r\n")
        wb(path, (body + tail).encode("utf-8"))
        rep[path]["write"] = "re-serialized (indent=%s crlf=%s)" % (ind, crlf)
        json.loads(open(path, "rb").read())

union_ledger("results/compute_audit.json", "history", cap=201)
union_ledger("results/regime_state.json", "history")

print(json.dumps(rep, ensure_ascii=False, indent=1))
print("RESOLVE2_OK", file=sys.stderr)
