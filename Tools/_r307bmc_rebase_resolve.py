"""r307 bm-c wave-3 rebase resolver (4 faces, r457/r469 canon).

- _attrition_guard_scan.json: latest-scan-wins raw blob (:2: ts newer).
- compute_audit.json: latest = newer ts; history union by ts.
- regime_state.json: scalars from newer 'updated'; history union.
- token_usage.json: machines = per-machine newest generated; scalars newer.
Format preservation: union faces re-serialized with origin-blob indent +
line-ending probe (r289 shared-JSON rewrite law).
"""
import subprocess
import json
import sys


def blob(ref):
    return subprocess.check_output(["git", "show", ref])


def load(path):
    return (json.loads(blob(":2:" + path)),
            json.loads(blob(":3:" + path)))


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


log = {}

# attrition scan evidence: latest scan wins, raw blob (no reformat)
p = "results/_attrition_guard_scan.json"
ours_ts = json.loads(blob(":2:" + p)).get("ts", "")
mine_ts = json.loads(blob(":3:" + p)).get("ts", "")
src = ":2:" if str(ours_ts) >= str(mine_ts) else ":3:"
with open(p, "wb") as f:
    f.write(blob(src + p))
log[p] = f"latest-scan {'ours' if src == ':2:' else 'mine'} ({ours_ts} vs {mine_ts})"

# compute_audit: latest=newer ts, history union by ts
p = "results/compute_audit.json"
ours, mine = load(p)
keep, other = ((ours, mine) if str(ours.get("latest", {}).get("ts", ""))
               >= str(mine.get("latest", {}).get("ts", ""))
               else (mine, ours))
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
keep, other = ((ours, mine) if str(ours.get("updated", ""))
               >= str(mine.get("updated", "")) else (mine, ours))
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
keep, other = ((ours, mine) if str(ours.get("generated", ""))
               >= str(mine.get("generated", "")) else (mine, ours))
out = dict(keep)
m = {}
for srcd in (keep, other):
    for k, v in (srcd.get("machines") or {}).items():
        if k not in m or str(v.get("generated", "")) >= str(m[k].get("generated", "")):
            m[k] = v
out["machines"] = m
indent, nl = fmt_probe(blob(":2:" + p))
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(serialize(out, indent, nl))
log[p] = f"keep={'ours' if keep is ours else 'mine'} machines={len(m)}"

with open("results/_r307bmc_rebase_resolve.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
for k, v in log.items():
    print(k, "->", v)
sys.exit(0)
