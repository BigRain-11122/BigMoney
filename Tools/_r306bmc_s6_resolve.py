"""r306 bm-c S6-face rebase resolver v2 (r457/r469/r498 canon).

- .md/.js faces: git checkout --ours (origin take, no JSON parse).
- JSON origin-take faces: write raw :2: blob bytes (zero reformat).
- compute_audit.json: latest = newer ts; history union by ts.
- regime_state.json: scalars from newer 'updated'; history union.
- token_usage.json: machines = per-machine newest generated; scalars from newer.
Format preservation: union faces re-serialized with origin-blob indent + line-ending probe.
"""
import subprocess
import json
import sys

def blob(ref):
    return subprocess.check_output(["git", "show", ref])

def load(path):
    return json.loads(blob(":2:" + path)), json.loads(blob(":3:" + path))

def fmt_probe(raw):
    crlf = b"\r\n" in raw[:2000]
    lines = raw.decode("utf-8", "replace").splitlines()
    indent = 2
    for ln in lines[1:6]:
        stripped = ln.lstrip(" ")
        if stripped and ln != stripped:
            indent = len(ln) - len(stripped)
            break
    return indent, ("\r\n" if crlf else "\n")

def serialize(obj, indent, nl):
    return json.dumps(obj, ensure_ascii=False, indent=indent).replace("\n", nl)

TEXT_FACES = [
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.md",
    "results/dashboard_status.js",
]
ORIGIN_TAKE = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/runnable_pool.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]

log = {}

subprocess.run(["git", "checkout", "--ours"] + TEXT_FACES, check=True)
for p in TEXT_FACES:
    log[p] = "origin-take (text checkout --ours)"

for p in ORIGIN_TAKE:
    raw = blob(":2:" + p)
    with open(p, "wb") as f:
        f.write(raw)
    log[p] = "origin-take (raw blob)"

# compute_audit: latest=newer ts, history union
p = "results/compute_audit.json"
ours, mine = load(p)
keep, other = (ours, mine) if str(ours.get("latest", {}).get("ts", "")) >= str(mine.get("latest", {}).get("ts", "")) else (mine, ours)
hist = {str(r.get("ts")): r for r in keep.get("history", [])}
for r in other.get("history", []):
    hist.setdefault(str(r.get("ts")), r)
out = dict(keep)
out["history"] = [hist[k] for k in sorted(hist)]
indent, nl = fmt_probe(blob(":2:" + p))
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(serialize(out, indent, nl))
log[p] = f"latest={'ours' if keep is ours else 'mine'} hist_union={len(out['history'])}"

# regime_state: newer updated + history union
p = "results/regime_state.json"
ours, mine = load(p)
keep, other = (ours, mine) if str(ours.get("updated", "")) >= str(mine.get("updated", "")) else (mine, ours)
out = dict(keep)
if isinstance(keep.get("history"), list) and isinstance(other.get("history"), list):
    seen = {json.dumps(r, sort_keys=True) for r in keep["history"]}
    merged = list(keep["history"])
    for r in other["history"]:
        k = json.dumps(r, sort_keys=True)
        if k not in seen:
            merged.append(r)
            seen.add(k)
    out["history"] = merged
indent, nl = fmt_probe(blob(":2:" + p))
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(serialize(out, indent, nl))
log[p] = f"keep={'ours' if keep is ours else 'mine'} hist={len(out.get('history', []))}"

# token_usage: per-machine newest union
p = "results/token_usage.json"
ours, mine = load(p)
keep, other = (ours, mine) if str(ours.get("generated", "")) >= str(mine.get("generated", "")) else (mine, ours)
out = dict(keep)
m = {}
for src in (keep, other):
    for k, v in (src.get("machines") or {}).items():
        if k not in m or str(v.get("generated", "")) >= str(m[k].get("generated", "")):
            m[k] = v
out["machines"] = m
indent, nl = fmt_probe(blob(":2:" + p))
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(serialize(out, indent, nl))
log[p] = f"keep={'ours' if keep is ours else 'mine'} machines={len(m)}"

with open("results/_r306bmc_s6_resolve.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
for k, v in log.items():
    print(k, "->", v)
sys.exit(0)
