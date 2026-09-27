"""r106 bm-c rebase tail-sync resolver: 12-UU vs bma-R354-addendum (same-window S6 double-run collision).

Stage map in rebase (r351 law, side-assert note): :2: = HEAD = already-replayed base =
upstream = bma-R354-addendum face; :3: = the commit being replayed = bmc-r106 (d96915eb).
Assertion: stage-3 blob must byte-equal `git show d96915eb:<path>` (my r106 face) and
stage-2 blob must byte-equal `git show 2c46f5ae:<path>` (upstream face) for every UU file
-- proven before any side-taking.

Recipes per skill catalog (all 12 classified, 0 UNKNOWN):
- snapshot (6 files): whole-blob take-new via hardened deep-ts probe (r100 strip/gate law, R350 exclusion-ban)
- twin coupling: REPORT .md takes SAME side as .json (r329); dashboard .js same side as .json (R209 whole bytes)
- compute_audit.json: rolling-ledger history row-set union zero-loss + latest take-new (r188)
- regime_state.json: identical-assert preferred, divergence -> R208 union + take-new state (r350)
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

REPLAY_SHA = "d96915eb"   # bmc-r106 commit being replayed -> must equal :3:
BASE_SHA = "2c46f5ae"     # upstream origin/main face -> must equal :2:

TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
STEMS = ("generated", "updated", "attempt", "ts", "lastseen", "written", "stamp", "lastrun", "time", "asof")


def blob(stage, path):
    r = subprocess.run(["git", "cat-file", "-p", f"{stage}{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"cat-file failed for {stage}{path}: {r.stderr[:200]}")
    return r.stdout


def show(sha, path):
    r = subprocess.run(["git", "show", f"{sha}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"show failed for {sha}:{path}: {r.stderr[:200]}")
    return r.stdout


def deep_ts(obj, best="", depth=0):
    """Hardened deep probe: normalized key contains a freshness stem, value is ts-shaped.
    No key-EXCLUDE tables (R350 ban); value-shape gate only. r353 law: strip ALL '_','-','/'
    inside the key via regex, not just ends (literal .strip misses 'as_of' middle chars)."""
    if depth > 8:
        return best
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-/]", "", str(k)).lower()
            if isinstance(v, str) and TS_SHAPE.match(v) and any(nk.find(s) >= 0 for s in STEMS):
                if v > best:
                    best = v
            best = deep_ts(v, best, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            best = deep_ts(item, best, depth + 1)
    return best


UU_FILES = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

# --- side-assertion gate (r351 law): provenance of :2:/:3: before any side-taking ---
for p in UU_FILES:
    assert blob(":3:", p) == show(REPLAY_SHA, p), f"side-assert FAIL :3: != {REPLAY_SHA} for {p}"
    assert blob(":2:", p) == show(BASE_SHA, p), f"side-assert FAIL :2: != {BASE_SHA} for {p}"
print(f"side-assert PASS: all {len(UU_FILES)} UU files -- :2:={BASE_SHA}(bma-R354), :3:={REPLAY_SHA}(bmc-r106)")

log = []


def pick_snapshot(path, log):
    a = blob(":2:", path)  # upstream = bma-R354
    b = blob(":3:", path)  # replaying = bmc-r106
    ta = deep_ts(json.loads(a))
    tb = deep_ts(json.loads(b))
    if tb > ta:
        side, data, why = "theirs(bmc-r106)", b, f"ts {tb} > {ta}"
    elif ta > tb:
        side, data, why = "ours(bma-R354)", a, f"ts {ta} > {tb}"
    elif a == b:
        side, data, why = "identical", a, "bytes equal on ts tie"
    else:
        side, data, why = "ours(bma-R354)", a, f"tie {ta} -> HEAD per r140"
    with open(path, "wb") as fh:
        fh.write(data)
    json.loads(open(path, "rb").read())  # parse-verify gate before add (r185 law)
    log.append(f"  SNAPSHOT {path}: {side} ({why})")
    return side


report_json_side = pick_snapshot("docs/daily_report/REPORT-2026-09-27.json", log)
md_stage = ":3:" if report_json_side.startswith("theirs") else ":2:"
open("docs/daily_report/REPORT-2026-09-27.md", "wb").write(blob(md_stage, "docs/daily_report/REPORT-2026-09-27.md"))
md_txt = open("docs/daily_report/REPORT-2026-09-27.md", "rb").read()
assert b"<<<<<<<" not in md_txt and b">>>>>>>" not in md_txt
log.append(f"  TWIN md <- {md_stage} (same side as json per r329)")

dash_side = pick_snapshot("results/dashboard_status.json", log)
js_stage = ":3:" if dash_side.startswith("theirs") else ":2:"
open("results/dashboard_status.js", "wb").write(blob(js_stage, "results/dashboard_status.js"))
js_txt = open("results/dashboard_status.js", "rb").read()
assert b"<<<<<<<" not in js_txt and b">>>>>>>" not in js_txt
# wrapper format law (R209): must remain `window.DASH_DATA = ...;` producer format
assert js_txt.lstrip().startswith(b"window.DASH_DATA"), "js wrapper format lost"
log.append(f"  TWIN js <- {js_stage} whole bytes (R209 wrapper law, format asserted)")

SNAPSHOTS = [
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in SNAPSHOTS:
    pick_snapshot(p, log)

# --- regime_state.json: identical-assert preferred (r350), divergence -> R208 union + take-new ---
ra = json.loads(blob(":2:", "results/regime_state.json"))
rb = json.loads(blob(":3:", "results/regime_state.json"))
if ra.get("history") == rb.get("history") and ra.get("transitions") == rb.get("transitions"):
    rs_path = "identical-ledgers"
    rs_bytes = blob(":3:" if rb.get("updated", "") > ra.get("updated", "") else ":2:", "results/regime_state.json")
else:
    rs_path = "union-ledgers"

    def union_rows(A, B):
        ka = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in A}
        kb = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in B}
        merged = list(ka.values()) + [r for k, r in kb.items() if k not in ka]
        return merged

    hist = union_rows(ra.get("history", []), rb.get("history", []))
    trans = union_rows(ra.get("transitions", []), rb.get("transitions", []))
    base_side = ":3:" if rb.get("updated", "") > ra.get("updated", "") else ":2:"
    out = json.loads(blob(base_side, "results/regime_state.json"))
    out["history"] = hist
    out["transitions"] = trans
    rs_bytes = json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8")
open("results/regime_state.json", "wb").write(rs_bytes)
json.loads(open("results/regime_state.json", "rb").read())
log.append(f"  ROLLING regime_state: {rs_path}, updated {ra.get('updated')} vs {rb.get('updated')} -> take-new state")

# --- compute_audit.json: history row-set union + latest take-new ---
ca = json.loads(blob(":2:", "results/compute_audit.json"))
cb = json.loads(blob(":3:", "results/compute_audit.json"))
rows_a = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in ca["history"]}
rows_b = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in cb["history"]}
union_rows = [rows_a[k2] for k2 in rows_a] + [rows_b[k2] for k2 in rows_b if k2 not in rows_a]
union_rows.sort(key=lambda r: r["ts"])
same_ts_diverge = len({r["ts"] for r in union_rows}) != len(union_rows)
latest = cb["latest"] if deep_ts(cb["latest"]) > deep_ts(ca["latest"]) else ca["latest"]
out = {"latest": latest, "history": union_rows}
crlf = b"\r\n" in blob(":2:", "results/compute_audit.json")[:2000]
text = json.dumps(out, ensure_ascii=False, indent=1)
if crlf:
    text = text.replace("\n", "\r\n")
open("results/compute_audit.json", "wb").write(text.encode("utf-8"))
json.loads(open("results/compute_audit.json", "rb").read())
log.append(f"  ROLLING compute_audit: history union {len(ca['history'])}+{len(cb['history'])} -> {len(union_rows)} rows, "
            f"same-ts-divergence={same_ts_diverge}, latest take-new (ts {deep_ts(latest)})")

print("\n".join(log))
print("\nRESOLVER DONE: all 12 UU resolved, parse-verified, zero-loss")
if same_ts_diverge:
    print("WARNINGS: same_ts_diverge:", same_ts_diverge)
    sys.exit(2)
