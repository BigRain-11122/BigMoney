# -*- coding: utf-8 -*-
"""r216 bm-c push-storm resolver (S7 push rejected -> pull --rebase 30-UU vs bm-b r422 same-day S6 faces).

Canonical recipes per Tools/skills/bigmoney-conflict-resolve/SKILL.md:
- 6 ALL_FACES already resolved via scripts/merge_lane_views.py resolve (union recipes, not here)
- snapshot: take-new whole side by deep ts probe (r100 hardening: normalized key prefix,
  value must be ^20\\d{2}- with time-of-day per R350; probe STAGED blobs not working tree;
  same-second tie -> origin side per r140 HEAD law in rebase context)
- twin-regen-md (REPORT/LIVE dated pairs + LIVE-latest pointers): json face decides side,
  md + pointer twins byte-copy from the SAME side (r327/r329: no hybrid twins)
- js-wrapper-snapshot: take winning side WHOLE BYTES (R209: never json.dumps re-wrap)
- append-log jsonl: line-level multiset union zero-loss (r188/r217/r426 multiset law)

Exit 0 = all resolved + parse-verified. Any probe-less face falls back to :3: (replayed
commit = newest work by commit order) with explicit per-file log entry (no blind silence).
"""
import json, re, subprocess, sys
from collections import Counter

def blob(stage, path):
    r = subprocess.run(["git", "cat-file", "-p", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {stage} read fail {path}: {r.stderr.decode(errors='replace')}")
    return r.stdout

TS_RX = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
PREFIXES = ("ts", "generated", "updated", "asof", "lastseen", "lastwrite", "written", "now", "collected", "measured")

def deep_ts(obj, path=()):
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and TS_RX.match(v) and any(nk.startswith(p) for p in PREFIXES):
                if best is None or v > best[0]:
                    best = (v, path + (str(k),))
            sub = deep_ts(v, path + (str(k),))
            if sub and (best is None or sub[0] > best[0]):
                best = sub
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            sub = deep_ts(v, path + (i,))
            if sub and (best is None or sub[0] > best[0]):
                best = sub
    return best

def pick_side(path, log):
    o, m = blob(2, path), blob(3, path)
    def probe(b):
        try:
            return deep_ts(json.loads(b.decode("utf-8")))
        except Exception:
            return None
    po, pm = probe(o), probe(m)
    if po and pm:
        side = 2 if po[0] >= pm[0] else 3   # tie -> origin (:2:=HEAD-in-rebase) per r140
        log.append({"path": path, "probe_origin": po, "probe_local": pm, "side": side, "rule": "deep-ts"})
    elif po or pm:
        side = 2 if po else 3
        log.append({"path": path, "probe_origin": po, "probe_local": pm, "side": side, "rule": "one-sided-probe"})
    else:
        side = 3
        log.append({"path": path, "probe_origin": None, "probe_local": None, "side": 3, "rule": "probe-less-fallback-to-replayed"})
    return (o if side == 2 else m), side

def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)

def verify_json(path, data):
    json.loads(data.decode("utf-8"))  # parse-verify before add (r185)

log = []
# --- snapshot faces (JSON, take-new by deep probe) ---
snaps = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-28.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
]
sides = {}
for p in snaps:
    data, side = pick_side(p, log)
    verify_json(p, data)
    write_bytes(p, data)
    sides[p] = side

# --- twin md + pointer faces: byte-copy from the SAME side as their json anchor (r327/r329) ---
twin_md = {
    "docs/daily_report/REPORT-2026-09-29.md": "docs/daily_report/REPORT-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.md": "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-latest.json": "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-2026-09-29.json",
}
for p, anchor in twin_md.items():
    side = sides[anchor]
    data = blob(side, p)
    if p.endswith(".json"):
        verify_json(p, data)
    write_bytes(p, data)
    log.append({"path": p, "side": side, "rule": f"twin-byte-copy-from-anchor({anchor})"})

# --- js-wrapper: take side whole bytes, probe ts inside payload ---
p = "results/dashboard_status.js"
o, m = blob(2, p), blob(3, p)
def probe_js(b):
    s = b.decode("utf-8", errors="replace")
    i, j = s.find("{"), s.rfind("}")
    try:
        return deep_ts(json.loads(s[i:j+1]))
    except Exception:
        return None
po, pm = probe_js(o), probe_js(m)
side = 2 if (po and pm and po[0] >= pm[0]) or (po and not pm) or (not po and not pm) else 3
data = o if side == 2 else m
write_bytes(p, data)
log.append({"path": p, "probe_origin": po, "probe_local": pm, "side": side, "rule": "js-wrapper-whole-bytes"})

# --- append-log jsonl: line-level multiset union zero-loss ---
p = "results/x2_watch_log.jsonl"
o, m = blob(2, p), blob(3, p)
ol = o.decode("utf-8").splitlines()
ml = m.decode("utf-8").splitlines()
co, cm = Counter(ol), Counter(ml)
union_counts = {k: max(co[k], cm[k]) for k in set(co) | set(cm)}
out, used = [], Counter()
for line in ol + ml:
    if used[line] < union_counts[line]:
        out.append(line)
        used[line] += 1
data = ("\n".join(out) + "\n").encode("utf-8")
write_bytes(p, data)
for line in out:
    json.loads(line)  # per-line parse verify
log.append({"path": p, "rule": "jsonl-multiset-union", "origin_lines": len(ol), "local_lines": len(ml), "union_lines": len(out)})

json.dump({"round": "r216-bmc-pushstorm", "resolved": log},
          open("results/_r216bmc_pushstorm_resolve.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=str)
for e in log:
    print(e.get("path"), "| side:", e.get("side"), "| rule:", e.get("rule"))
print(f"OK resolved={len(log)} files; x2 union {log[-1]['origin_lines']}+{log[-1]['local_lines']}->{log[-1]['union_lines']}")
