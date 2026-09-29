"""r444 bm-b rebase resolver (wave 2, onto 74da996dd) -- 13 UU faces,
canon recipes per bigmoney-conflict-resolve classifier (13/13 classified).
Side 2 = ours = origin/main (HEAD during rebase); side 3 = theirs = the
replayed 7e2d99e8 S6 lane-sweep adoption commit.  Tie law r140: same-ts ->
HEAD (side 2).  Twins law r98/r99/r100 + r439bmb: .md/.json twins MUST take
the SAME side -> lead json probes once, twins ride the winner side verbatim.
Reuses r443bmb resolver machinery verbatim (lineage r435/r438/r440/r442/r443).
"""
import json
import re
import subprocess

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(side, path):
    h = subprocess.run(["git", "show", f":{side}:{path}"],
                       capture_output=True, cwd=REPO).stdout
    return h


def probe_ts(obj, best=""):
    if isinstance(obj, dict):
        for v in obj.values():
            best = probe_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = probe_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj) and obj > best:
        best = obj
    return best


def write(path, data):
    with open(f"{REPO}\\{path}", "wb") as f:
        f.write(data)
    if path.endswith(".json"):
        json.loads(open(f"{REPO}\\{path}", encoding="utf-8").read())
    print(f"resolved {path}")


def detect_indent(raw):
    for line in raw.decode("utf-8", errors="replace").split("\n")[1:3]:
        m = re.match(r"^ +", line)
        if m:
            return len(m.group(0))
    return 2


def take_new_side(path):
    """Return winning side (2 or 3); tie -> 2 (HEAD, r140 law)."""
    a, b = blob(2, path), blob(3, path)
    try:
        ta = probe_ts(json.loads(a.decode("utf-8")))
    except Exception:
        ta = ""
    try:
        tb = probe_ts(json.loads(b.decode("utf-8")))
    except Exception:
        tb = ""
    return 3 if (tb and (not ta or tb > ta)) else 2


def resolve_union_ledger(path, ledger_keys):
    a = json.loads(blob(2, path).decode("utf-8"))
    b = json.loads(blob(3, path).decode("utf-8"))
    indent = detect_indent(blob(2, path))
    out = {}
    for k in a:
        if k in ledger_keys:
            seen, rows = set(), []
            for row in list(a.get(k) or []) + list(b.get(k) or []):
                key = json.dumps(row, sort_keys=True, ensure_ascii=False)
                if key not in seen:
                    seen.add(key)
                    rows.append(row)
            if rows and isinstance(rows[0], dict) and \
                    any(TS_RE.match(str(v)) for r in rows[:3]
                        for v in r.values()):
                rows.sort(key=lambda r: probe_ts(r))
            out[k] = rows
        else:
            out[k] = a[k]
    for k in b:
        if k in out:
            continue
        out[k] = b[k]
    if probe_ts(a) >= probe_ts(b):
        for k in a:
            if k not in ledger_keys:
                out[k] = a[k]
    else:
        for k in b:
            if k not in ledger_keys:
                out[k] = b[k]
    data = (json.dumps(out, ensure_ascii=False, indent=indent,
                       default=str) + "\n").encode("utf-8")
    la = sum(len(a.get(k) or []) for k in ledger_keys)
    lb = sum(len(b.get(k) or []) for k in ledger_keys)
    lo = sum(len(out[k]) for k in ledger_keys)
    assert lo >= max(la, lb), f"{path}: union loss {lo} < {max(la, lb)}"
    print(f"{path}: ledger union |A|={la} |B|={lb} -> |AUB|={lo}")
    write(path, data)


# ---- rolling-ledger unions (r188/R208 law)
resolve_union_ledger("results/compute_audit.json", {"history"})
resolve_union_ledger("results/regime_state.json", {"history", "transitions"})

# ---- snapshot twins: lead json probes once, md twins ride same side
TWINS = [
    ("docs/daily_report/REPORT-2026-09-30.json",
     ["docs/daily_report/REPORT-2026-09-30.md"]),
    ("docs/live_usage/LIVE-2026-09-30.json",
     ["docs/live_usage/LIVE-2026-09-30.md"]),
    ("docs/live_usage/LIVE-latest.json",
     ["docs/live_usage/LIVE-latest.md"]),
]
for lead, twins in TWINS:
    side = take_new_side(lead)
    print(f"{lead}: winner side={side} ({'ours/origin' if side == 2 else 'theirs/mine'})")
    write(lead, blob(side, lead))
    for tw in twins:
        write(tw, blob(side, tw))

# ---- plain snapshots (take-new via hardened probe)
for p in [
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
]:
    write(p, blob(take_new_side(p), p))

print("resolver done: 13 files (2 ledger unions zero-loss, 3 twin groups "
      "same-side, 5 plain snapshots), parse-verified r185")
