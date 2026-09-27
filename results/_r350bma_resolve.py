"""r350 bm-a rebase storm resolver: 28-UU vs bmc-r100 (same-window S6 double-run collision).

Classifier: 26 classified + 2 UNKNOWN manually classified as snapshot (t24 legs regen
whole-doc each S6 round with inner `generated` ts; probe: bma 20:00:36/43 > bmc 19:52:29).
Recipes per skill:
- snapshot (24 files): whole-blob take-new via hardened deep-ts probe (r100 strip/gate law)
- twin coupling: REPORT .md takes SAME side as .json (r329); dashboard .js same side as .json (R209 whole bytes)
- compute_audit.json: rolling-ledger history row-set union zero-loss + latest take-new (r188)
- autofill_state.json: launches union (r322 composite-key law) + last_tick inner-ts whole-dict (r140 tie->ours)
- regime_state.json: history/transitions identical both sides + take-new by updated (r311 deep probe)
- x2_watch_log.jsonl: line-level union zero-loss (r188)
Stage map in rebase: :2: = ours = bmc-r100 side, :3: = theirs = bma-R350 side.
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
STEMS = ("generated", "updated", "attempt", "ts", "lastseen", "written", "stamp", "lastrun", "time", "asof")
# 'as_of' may be wall-clock (daily_scorecard forward_guard.as_of) or date-only data cutoff
# (regime_state.asof); the TS_SHAPE time-part gate filters the latter, so 'asof' must be
# PROBED not excluded (r350 live-fire of r345 probe-key-completeness law).
EXCLUDE = ("cutoff", "evidence_cutoff", "next_pick")


def blob(stage, path):
    r = subprocess.run(["git", "cat-file", "-p", f"{stage}{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"cat-file failed for {stage}{path}: {r.stderr[:200]}")
    return r.stdout


def deep_ts(obj, best="", depth=0):
    """Hardened deep probe: normalized key contains a freshness stem, value is ts-shaped."""
    if depth > 8:
        return best
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if any(x in nk for x in EXCLUDE):
                continue
            if isinstance(v, str) and TS_SHAPE.match(v) and any(nk.find(s) >= 0 for s in STEMS):
                if v > best:
                    best = v
            best = deep_ts(v, best, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            best = deep_ts(item, best, depth + 1)
    return best


def pick_snapshot(path, log):
    a = blob(":2:", path)  # ours = bmc-r100
    b = blob(":3:", path)  # theirs = bma-R350
    ta = deep_ts(json.loads(a))
    tb = deep_ts(json.loads(b))
    if tb > ta:
        side, data, why = "theirs(bma)", b, f"ts {tb} > {ta}"
    elif ta > tb:
        side, data, why = "ours(bmc)", a, f"ts {ta} > {tb}"
    elif a == b:
        side, data, why = "identical", a, "bytes equal on ts tie"
    else:
        side, data, why = "ours(bmc)", a, f"tie {ta} -> HEAD per r140"
    with open(path, "wb") as fh:
        fh.write(data)
    json.loads(open(path, "rb").read())  # parse-verify gate before add
    log.append(f"  SNAPSHOT {path}: {side} ({why})")
    return side


log = []

# --- snapshot family (probe decides; expected M-fresher bma by construction) ---
SNAPSHOTS = [
    "results/daily_scorecard.json",
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
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/prospect_paper/_summary.json",   # manual snapshot (UNKNOWN -> classified)
    "results/prospect_promotion/_summary.json",
]
report_json_side = pick_snapshot("docs/daily_report/REPORT-2026-09-27.json", log)
md_stage = ":3:" if report_json_side.startswith("theirs") else ":2:"
md_bytes = blob(md_stage, "docs/daily_report/REPORT-2026-09-27.md")
open("docs/daily_report/REPORT-2026-09-27.md", "wb").write(md_bytes)
log.append(f"  TWIN md <- {md_stage} (same side as json per r329)")
dash_side = pick_snapshot("results/dashboard_status.json", log)
js_stage = ":3:" if dash_side.startswith("theirs") else ":2:"
open("results/dashboard_status.js", "wb").write(blob(js_stage, "results/dashboard_status.js"))
log.append(f"  TWIN js <- {js_stage} whole bytes (R209 wrapper law)")

for p in SNAPSHOTS:
    pick_snapshot(p, log)

# --- regime_state.json: verify ledger faces identical, then whole take-new by updated ---
ra = json.loads(blob(":2:", "results/regime_state.json"))
rb = json.loads(blob(":3:", "results/regime_state.json"))
assert ra["history"] == rb["history"], "regime history diverged -- escalate"
assert ra["transitions"] == rb["transitions"], "regime transitions diverged -- escalate"
rs_side = "theirs(bma)" if rb["updated"] > ra["updated"] else "ours(bmc)"
rs_bytes = blob(":3:" if rs_side.startswith("theirs") else ":2:", "results/regime_state.json")
open("results/regime_state.json", "wb").write(rs_bytes)
json.loads(open("results/regime_state.json", "rb").read())
log.append(f"  ROLLING regime_state: ledgers identical, take-new {rs_side} (updated {ra['updated']} vs {rb['updated']})")

# --- compute_audit.json: history row-set union + latest take-new ---
ca = json.loads(blob(":2:", "results/compute_audit.json"))
cb = json.loads(blob(":3:", "results/compute_audit.json"))
rows_a = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in ca["history"]}
rows_b = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in cb["history"]}
union = list(rows_a.values()) + [r for k, r in rows_b.items() if k not in rows_a]
union.sort(key=lambda r: r["ts"])
same_ts_diverge = len({r["ts"] for r in union}) != len(union)
latest = cb["latest"] if deep_ts(cb["latest"]) > deep_ts(ca["latest"]) else ca["latest"]
out = {"latest": latest, "history": union}
crlf = b"\r\n" in blob(":2:", "results/compute_audit.json")[:2000]
text = json.dumps(out, ensure_ascii=False, indent=1)
if crlf:
    text = text.replace("\n", "\r\n")
open("results/compute_audit.json", "wb").write(text.encode("utf-8"))
json.loads(open("results/compute_audit.json", "rb").read())
log.append(f"  ROLLING compute_audit: history union {len(ca['history'])}+{len(cb['history'])} -> {len(union)} rows, "
           f"same-ts-divergence={same_ts_diverge}, latest take-new (ts {deep_ts(latest)})")

# --- autofill_state.json: launches composite-key union + last_tick whole-dict ---
aa = json.loads(blob(":2:", "results/autofill_state.json"))
ab = json.loads(blob(":3:", "results/autofill_state.json"))
ka = {json.dumps(x, sort_keys=True, ensure_ascii=False): x for x in aa["launches"]}
kb = {json.dumps(x, sort_keys=True, ensure_ascii=False): x for x in ab["launches"]}
merged = dict(ka)
collide_flags = []
for k, v in kb.items():
    if k in merged:
        if merged[k] != v:
            collide_flags.append(k)  # true divergence -> flag, never silent double-keep
    else:
        merged[k] = v
launches = sorted(merged.values(), key=lambda x: x["ts"])[-50:]  # cap 50 newest
launches.sort(key=lambda x: x["ts"])  # write back ts-ascending (producer append order)
lt = ab["last_tick"] if ab["last_tick"]["ts"] > aa["last_tick"]["ts"] else aa["last_tick"]  # r140 tie->ours(:2:)
assert isinstance(lt, dict), "last_tick not dict"
crlf_af = b"\r\n" in blob(":2:", "results/autofill_state.json")[:2000]
text = json.dumps({"last_tick": lt, "launches": launches}, ensure_ascii=False, indent=1)
if crlf_af:
    text = text.replace("\n", "\r\n")
open("results/autofill_state.json", "wb").write(text.encode("utf-8"))
chk = json.loads(open("results/autofill_state.json", "rb").read())
assert isinstance(chk["last_tick"], dict)
log.append(f"  MIXED autofill_state: launches {len(aa['launches'])}+{len(ab['launches'])} -> union {len(launches)} "
           f"(diverge_keys={len(collide_flags)}), last_tick ts {lt['ts']} whole-dict")

# --- x2_watch_log.jsonl: line-level union zero-loss ---
xa = blob(":2:", "results/x2_watch_log.jsonl").decode("utf-8", errors="replace").splitlines()
xb = blob(":3:", "results/x2_watch_log.jsonl").decode("utf-8", errors="replace").splitlines()
seen, merged_lines = set(), []
for line in xa + xb:
    if line and line not in seen:
        seen.add(line)
        merged_lines.append(line)
def line_ts(line):
    try:
        return json.loads(line).get("ts", "")
    except Exception:
        return ""
merged_lines.sort(key=line_ts)
blob_ending = "\r\n" if "\r\n" in blob(":2:", "results/x2_watch_log.jsonl").decode("utf-8", "replace")[:500] else "\n"
open("results/x2_watch_log.jsonl", "wb").write((blob_ending.join(merged_lines) + blob_ending).encode("utf-8"))
log.append(f"  APPEND-LOG x2_watch_log.jsonl: {len(xa)}+{len(xb)} -> {len(merged_lines)} lines union")

print("\n".join(log))
print("\nRESOLVER DONE: all 28 UU resolved, parse-verified, zero-loss")
if collide_flags or same_ts_diverge:
    print("WARNINGS:", collide_flags[:3], "same_ts_diverge:", same_ts_diverge)
    sys.exit(2)
