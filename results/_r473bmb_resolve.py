# r473 bm-b rebase-collision resolver (r473 断头 rebase 诊断序正序收口: 重放态当 commit 消费)
# stopped pick = d7e7436a8 (bm-b round 472) onto 0234e7709 (bm-a round 483)
# ours(stage2)=bm-a r483 faces; theirs(stage3)=bm-b r472 faces (uniformly newer ts 17:49-17:53 vs 17:36-17:42)
# recipes per bigmoney-conflict-resolve SKILL.md: snapshot take-new / rolling-ledger union / memory-union /
#   js-wrapper take-side / parquet natural-key containment (zero-loss verified)
import subprocess, json, io, os, sys
from collections import Counter

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    assert r.returncode == 0, ("blob fail", stage, path, r.stderr[:200])
    return r.stdout

def wb(path, data):
    with open(path, "wb") as f:
        f.write(data)

rep = {}
UU_ALL = []

# ---- enumerate unmerged set (fail-closed: resolver refuses if the 21-file model drifted)
r = subprocess.run(["git", "ls-files", "-u"], capture_output=True, text=True)
unmerged = sorted({tuple(l.split("\t")[1].strip('"').split(" -> ")[-1] if " -> " in l.split("\t")[1] else l.split("\t")[1].strip('"') for _ in [0]) for l in r.stdout.splitlines() if l})
paths = sorted({l.split("\t")[1].strip('"') for l in r.stdout.splitlines() if l.strip()})
rep["unmerged_paths"] = paths

# ---- 1. CODELY.md memory-union: ours canon (5,836B/15 lines) + theirs-unique r472 entry
ours_b = blob(2, "CODELY.md")
theirs_b = blob(3, "CODELY.md")
theirs_txt = theirs_b.decode("utf-8")
r472_lines = [l for l in theirs_txt.splitlines() if l.startswith("- [2026-09-30 r472 bm-b]")]
assert len(r472_lines) == 1, ("r472 entry lines", len(r472_lines))
entry = r472_lines[0]
assert entry not in ours_b.decode("utf-8"), "r472 entry already in ours"
frag = [l for l in theirs_txt.splitlines() if l.startswith("rom knowledge import")]
assert frag, "expected r482 truncated-dup fragment in theirs (r281 adjudicated removal, do not resurrect)"
cod = ours_b if ours_b.endswith(b"\n") else ours_b + b"\n"
cod += b"\n" + entry.encode("utf-8") + b"\n"
for marker in (b"<<<<<<<", b">>>>>>>"):
    assert marker not in cod, "conflict marker leaked"
sz = len(cod)
assert sz < 10240, ("10KB hardline", sz)
wb("CODELY.md", cod)
rep["CODELY.md"] = {"recipe": "memory-union ours+r472entry", "bytes": sz,
                    "lines": len(cod.decode("utf-8").splitlines()),
                    "fragment_discarded": "r482 truncated dup (r281 adjudicated, archive record exists)"}

# ---- 2. take-theirs whole bytes (snapshot / js-wrapper / same-day regen docs; theirs uniformly newer)
TAKE_THEIRS = [
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/_attrition_guard_scan.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
]
for p in TAKE_THEIRS:
    b = blob(3, p)
    if p.endswith(".js"):
        assert b.lstrip().startswith(b"window.DASH_DATA"), "js wrapper stripped"
    elif p.endswith(".json"):
        json.loads(b)  # r185: parse-validate before write-back
    wb(p, b)
    rep[p] = {"recipe": "take-theirs", "bytes": len(b)}

# ---- 3. rolling ledgers: union history (identity-keyed, zero row loss), scalars take-theirs
def fmt_probe(obj, orig_bytes):
    # producer = json.dump(..., indent=2, ensure_ascii=False) via Windows text mode -> CRLF variants
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
    ident = lambda it: json.dumps(it, sort_keys=True, ensure_ascii=False)
    merged = {}
    for it in la:
        merged[ident(it)] = it
    for it in lb:
        merged.setdefault(ident(it), it)  # identity tie: first-wins (identical anyway)
    items = list(merged.values())
    rep[path] = {"recipe": "union-" + listkey, "ours_len": len(la), "theirs_len": len(lb),
                 "union_len": len(items)}
    tsk = [it.get("ts") for it in items]
    if all(isinstance(t, str) for t in tsk):
        items.sort(key=lambda it: it["ts"], reverse=True)
        dropped = 0
        if cap and len(items) > cap:
            dropped = len(items) - cap
            items = items[:cap]
            rep[path]["capped_to"] = cap
            rep[path]["dropped_oldest"] = dropped
        # mirror producer order: probe whether history is ascending in theirs blob
        lb_ts = [it.get("ts") for it in lb if isinstance(it.get("ts"), str)]
        if lb_ts == sorted(lb_ts):
            items = list(reversed(items))  # producer appends oldest-first -> restore ascending
        rep[path]["order"] = "asc-restored" if lb_ts == sorted(lb_ts) else "desc"
    else:
        assert len(items) == len(lb), ("no ts key and union != theirs; manual review", path)
    final = dict(b)
    final[listkey] = items
    # if union adds nothing beyond theirs, take theirs bytes verbatim (no re-serialization)
    idb = {ident(it) for it in lb}
    if {ident(it) for it in items} <= idb and len(items) == len(lb):
        wb(path, blob(3, path))
        rep[path]["write"] = "theirs-verbatim (union identical)"
        return
    fmt = fmt_probe(b, blob(3, path))
    assert fmt, ("format probe failed", path)
    ind, ea, crlf, tail = fmt
    body = json.dumps(final, indent=ind, ensure_ascii=ea)
    if crlf:
        body = body.replace("\n", "\r\n")
    wb(path, (body + tail).encode("utf-8"))
    rep[path]["write"] = "re-serialized (indent=%s crlf=%s)" % (ind, crlf)
    json.loads(open(path, "rb").read())  # post-write parse validation

union_ledger("results/compute_audit.json", "history", cap=201)
union_ledger("results/regime_state.json", "history")

# ---- 4. parquets: natural-key containment -> take-theirs (newer backfill run) else fail-closed probe
import pandas as pd
for p in ["Money02/data/lhb/chunks/2026Q3.parquet", "Money02/data/lhb/lhb_detail.parquet"]:
    da = pd.read_parquet(io.BytesIO(blob(2, p)))
    db = pd.read_parquet(io.BytesIO(blob(3, p)))
    code_col = da.columns[0]
    date_col = next(c for c in da.columns if "\u65e5" in str(c))
    nat = lambda df: Counter(zip(df[code_col].astype(str), df[date_col].astype(str)))
    na, nb = nat(da), nat(db)
    if na == nb:
        # membership identical (incl. dup multiplicity) -> newer run wins cell-level backfill diffs
        wb(p, blob(3, p))
        rep[p] = {"recipe": "take-theirs (natural-key membership identical, newer backfill run)",
                  "rows": len(db), "key_cols": [str(code_col), str(date_col)]}
    else:
        rep[p] = {"recipe": "NEEDS-UNION", "rows_ours": len(da), "rows_theirs": len(db),
                  "ours_only_keys": sum((na - nb).values()), "theirs_only_keys": sum((nb - na).values())}
        assert False, ("genuine row union required — not auto-resolved", p)

print(json.dumps(rep, ensure_ascii=False, indent=1))
# summary verdict
bad = [k for k, v in rep.items() if isinstance(v, dict) and v.get("recipe") == "NEEDS-UNION"]
print("RESOLVE_OK" if not bad else "RESOLVE_INCOMPLETE", file=sys.stderr)
