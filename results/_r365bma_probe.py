# -*- coding: utf-8 -*-
"""r365 bm-a storm probe (rebase replay of b4c72760 onto origin/main 2c32dd96 = bm-c r117).
Stage sourcing: :2: = ours = origin (bm-c r117 chain ~23:50:28 commit),
               :3: = theirs = mine (bm-a R365 chain 23:49-23:54).
Deep wall-clock ts probe per r100/R350 hardened law:
  - normalized key: lowercase, strip '_'/'-' before prefix match
  - value must be ts-shaped ^20\d{2}- AND contain time-of-day ([T ]HH:MM) to feed max
  - NO key-name exclusion lists; probe STAGED blobs only
Reports per-file fresher side + ledger/union faces shape for the resolver."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROBE_PREFIXES = ("ts", "asof", "updated", "generated", "lastwritten", "lastseen",
                  "saved", "written", "clock", "now", "timestamp", "statets")
TS_SHAPE = re.compile(r"^20\d{2}-")
HAS_TOD = re.compile(r"[T ]\d{2}:\d{2}")


def git(*args):
    p = subprocess.run(["git"] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={p.returncode}: {p.stderr[:300].decode('utf-8', 'replace')}")
    return p.stdout


def blob(stage, path):
    return git("show", f"{stage}:{path}").decode("utf-8", "replace")


def deep_ts(obj, path=()):
    """yield (path, value) for wall-clock ts values under probe-eligible keys"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and any(nk.startswith(p) for p in PROBE_PREFIXES):
                if TS_SHAPE.match(v) and HAS_TOD.search(v):
                    yield (path + (str(k),), v)
            yield from deep_ts(v, path + (str(k),))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from deep_ts(v, path + (i,))


def probe(stage, path):
    try:
        raw = blob(stage, path)
    except Exception as e:
        return None, str(e)
    try:
        obj = json.loads(raw)
    except Exception as e:
        return ("RAW", raw[:80]), None
    hits = list(deep_ts(obj))
    if not hits:
        return None, "no-wallclock-ts"
    best = max(hits, key=lambda h: h[1])
    return best[1], "/".join(str(x) for x in best[0])


SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]

print("== snapshots deep-ts probe (ours=:2: origin/bm-c | theirs=:3: mine) ==")
for p in SNAPSHOTS:
    ta, ka = probe(":2", p)
    tb, kb = probe(":3", p)
    if ta is None and tb is None:
        side = "TIE(no-ts)->HEAD"
    elif ta is None:
        side = "MINE(ours-no-ts)"
    elif tb is None:
        side = "OURS(mine-no-ts)"
    elif ta == tb:
        side = "TIE->HEAD(ours)"
    else:
        side = "OURS" if ta > tb else "MINE"
    print(f"{side:22s} | ours={ta} @{ka} | mine={tb} @{kb} | {p}")

print()
print("== ledger faces ==")
# compute_audit history
for stage, name in ((":2", "ours"), ((":3"), "mine")):
    d = json.loads(blob(stage, "results/compute_audit.json"))
    h = d.get("history", [])
    top = {k: d.get(k) for k in ("ts", "machine")}
    print(f"compute_audit[{name}]: history={len(h)} top_ts={top}")
a = json.loads(blob(":2", "results/compute_audit.json")).get("history", [])
b = json.loads(blob(":3", "results/compute_audit.json")).get("history", [])
ka, kb = {r.get("ts") for r in a}, {r.get("ts") for r in b}
print(f"compute_audit: |A|={len(a)} |B|={len(b)} distinct-union={len(ka | kb)} overlap={len(ka & kb)} only-ours={sorted(ka - kb)} only-mine={sorted(kb - ka)}")
diff_rows = [t for t in (ka & kb) if next(r for r in a if r.get('ts') == t) != next(r for r in b if r.get('ts') == t)]
print(f"compute_audit: same-ts content-diff rows: {diff_rows}")

# regime_state
for stage, name in ((":2", "ours"), (":3", "mine")):
    d = json.loads(blob(stage, "results/regime_state.json"))
    print(f"regime_state[{name}]: keys={sorted(d.keys())}")
ra = json.loads(blob(":2", "results/regime_state.json"))
rb = json.loads(blob(":3", "results/regime_state.json"))
for k in set(ra) | set(rb):
    if ra.get(k) != rb.get(k):
        va, vb = ra.get(k), rb.get(k)
        la = len(va) if isinstance(va, list) else ("dict" if isinstance(va, dict) else str(va)[:40])
        lb = len(vb) if isinstance(vb, list) else ("dict" if isinstance(vb, dict) else str(vb)[:40])
        print(f"regime_state DIFF key={k}: ours={la} mine={lb}")

# autofill_state
for stage, name in ((":2", "ours"), (":3", "mine")):
    d = json.loads(blob(stage, "results/autofill_state.json"))
    lt = d.get("last_tick") or {}
    lts = lt.get("ts") if isinstance(lt, dict) else lt
    launches = d.get("launches", [])
    keys = [tuple(str(l.get(f)) for f in ("ts", "machine", "pid", "runner_sha256", "entry", "shard")) for l in launches]
    print(f"autofill[{name}]: launches={len(launches)} distinct-compkeys={len(set(keys))} last_tick.ts={lts} top-keys={sorted(d.keys())[:8]}")
aa = json.loads(blob(":2", "results/autofill_state.json"))
ab = json.loads(blob(":3", "results/autofill_state.json"))
la, lb_ = aa.get("launches", []), ab.get("launches", [])
ka = {tuple(str(l.get(f)) for f in ("ts", "machine", "pid", "runner_sha256", "entry", "shard")) for l in la}
kb = {tuple(str(l.get(f)) for f in ("ts", "machine", "pid", "runner_sha256", "entry", "shard")) for l in lb_}
print(f"autofill: launches |A|={len(la)} |B|={len(lb_)} union={len(ka | kb)} only-ours={len(ka - kb)} only-mine={len(kb - ka)}")
sa = {json.dumps(l, sort_keys=True, ensure_ascii=False) for l in la}
sb = {json.dumps(l, sort_keys=True, ensure_ascii=False) for l in lb_}
print(f"autofill: identical-line overlap={len(sa & sb)}")

# x2_watch_log
xa = blob(":2", "results/x2_watch_log.jsonl").splitlines()
xb = blob(":3", "results/x2_watch_log.jsonl").splitlines()
sa, sb = set(xa), set(xb)
print(f"x2_watch: |A|={len(xa)} |B|={len(xb)} union-lines={len(sa | sb)} only-ours={len(sa - sb)} only-mine={len(sb - sa)}")
print("x2_watch only-ours tail:", sorted(sa - sb)[-2:])
print("x2_watch only-mine tail:", sorted(sb - sa)[-2:])
