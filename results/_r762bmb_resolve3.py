# r762 onto-rebase batch-3: r761-replay vs bm-c r595 UU resolution (same recipes as batch-1)
import subprocess, json, sys, re
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def norm_ts(v):
    if v is None:
        return None
    s = str(v).strip()
    s2 = s.replace(" ", "T", 1) if "T" not in s else s
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s2, fmt)
        except ValueError:
            continue
    return None

TS_KEYS = ["generated_at", "generated", "ts", "updated", "scan_ts", "last_scan", "run_ts"]
def find_ts(obj, depth=0):
    if depth > 3 or not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        if k in obj and norm_ts(obj[k]):
            return (k, obj[k])
    for v in obj.values():
        if isinstance(v, dict):
            got = find_ts(v, depth + 1)
            if got:
                return got
    return None

def take_new_ts(path):
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    oo, tt = json.loads(o), json.loads(t)
    to = norm_ts(find_ts(oo)[1]); ttn = norm_ts(find_ts(tt)[1])
    if to is None or ttn is None:
        raise RuntimeError(f"{path}: no parseable ts")
    return ("ours" if to >= ttn else "theirs", o if to >= ttn else t, to, ttn)

def md_take_new(path):
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    pat = re.compile(r"(20\d{2}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})")
    mo = pat.search(o.decode("utf-8", "replace")[:400]); mt = pat.search(t.decode("utf-8", "replace")[:400])
    if not mo or not mt:
        raise RuntimeError(f"{path}: no md ts")
    do = datetime.strptime(mo.group(1) + "T" + mo.group(2), "%Y-%m-%dT%H:%M:%S")
    dt = datetime.strptime(mt.group(1) + "T" + mt.group(2), "%Y-%m-%dT%H:%M:%S")
    return ("ours" if do >= dt else "theirs", o if do >= dt else t, do, dt)

def ledger_union(path):
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    oo, tt = json.loads(o), json.loads(t)
    doc_o = norm_ts(find_ts(oo)[1]); doc_t = norm_ts(find_ts(tt)[1])
    newer = oo if (doc_o or datetime.min) >= (doc_t or datetime.min) else tt
    out = {}
    for k in (oo.keys() | tt.keys()):
        ov, tv = oo.get(k), tt.get(k)
        if isinstance(ov, list) and isinstance(tv, list):
            seen, un = set(), []
            for el in ov + tv:
                key = json.dumps(el, sort_keys=True, ensure_ascii=False)
                if key not in seen:
                    seen.add(key); un.append(el)
            def el_ts(e):
                g = find_ts(e)
                return norm_ts(g[1]) if g else None
            if all(el_ts(e) is not None for e in un):
                un.sort(key=lambda e: el_ts(e))
            out[k] = un
        else:
            out[k] = newer.get(k, ov if ov is not None else tv)
    blob = (json.dumps(out, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    json.loads(blob)
    return ("ledger-union", blob, None, None)

SNAP = ["results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json", "results/lhb_update_status.json",
        "results/update_status.json", "results/token_usage.json",
        "docs/daily_report/REPORT-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.json",
        "docs/live_usage/LIVE-latest.json"]
MDS = ["docs/daily_report/REPORT-2026-10-06.md", "docs/live_usage/LIVE-2026-10-06.md",
       "docs/live_usage/LIVE-latest.md"]
LEDGERS = ["results/compute_audit.json", "results/regime_state.json"]

lines = []
for p in SNAP + MDS:
    side, blob, a, b = (take_new_ts(p) if p in SNAP else md_take_new(p))
    open(p, "wb").write(blob)
    subprocess.run(["git", "add", p], check=True)
    lines.append(f"{p}: {side} (ours={a} theirs={b})")
for p in LEDGERS:
    side, blob, _, _ = ledger_union(p)
    open(p, "wb").write(blob)
    subprocess.run(["git", "add", p], check=True)
    lines.append(f"{p}: {side}")
print("\n".join(lines))
print("OK-3")
