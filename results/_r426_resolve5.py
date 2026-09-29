# r426 rebase storm-5 resolver -- non-ALL_FACES legs
# Recipes: snapshot deep-ts take-new (r188/R208); R209 js wrapper whole-bytes coupled;
#          r327/r329 twin md same-side byte-copy; r188 append-log multiset union vs base;
#          b_layer_mask.csv = row-order face (multiset-identical) -> take :2: base-side whole bytes;
#          HANDOVER.md anchor-insert (R210): origin lines keep position + latecomer lines appended, bytes-level.
# Probes: r100/R350 hardened (strip _/- prefix match, value ^20\d{2}- + time-of-day, staged blob only);
#         r185 parse-verify; r140 tie -> :2: base-side.
import json, re, subprocess, collections

def stage_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {stage}:{path}: {r.stderr[:200]!r}")
    return r.stdout

TS_SHAPE = re.compile(r"^20\d{2}-")
HAS_TOD = re.compile(r"[T ]\d{1,2}:\d{2}")
PREFIXES = ("asof", "generated", "updated", "ts", "cutoff", "lastrun", "checked")

def deep_ts(obj, best):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and any(nk.startswith(p) for p in PREFIXES):
                if TS_SHAPE.match(v) and HAS_TOD.search(v):
                    if v > best[0]:
                        best[0] = v
            else:
                deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts(v, best)

def probe(path):
    b2, b3 = stage_blob(2, path), stage_blob(3, path)
    ts2, ts3 = [""], [""]
    deep_ts(json.loads(b2), ts2)
    deep_ts(json.loads(b3), ts3)
    side = 2 if ts2[0] >= ts3[0] else 3  # tie -> :2: base-side (r140)
    return side, ts2[0], ts3[0], (b2 if side == 2 else b3)

report = []

# --- snapshots: take-new whole doc ---
SNAPSHOTS = [
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
for p in SNAPSHOTS:
    side, t2, t3, blob = probe(p)
    with open(p, "wb") as f:
        f.write(blob)
    json.loads(blob)  # parse-verify (r185)
    sides[p] = side
    report.append(f"snapshot {p}: :{side}: taken (ts2={t2!r} ts3={t3!r})")

# --- js wrapper: whole bytes from SAME side as its .json twin (R209 + coupling) ---
p = "results/dashboard_status.js"
side = sides["results/dashboard_status.json"]
blob = stage_blob(side, p)
with open(p, "wb") as f:
    f.write(blob)
assert blob.startswith(b"window.") or b"DASH_DATA" in blob[:64], "js wrapper shape lost"
report.append(f"js-wrapper {p}: :{side}: whole-bytes (coupled to dashboard_status.json)")

# --- twin-regen-md: json side by deep probe, md byte-copy SAME side (r327/r329) ---
TWINS = [
    ("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md"),
    ("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]
for jp, mp in TWINS:
    side, t2, t3, jblob = probe(jp)
    with open(jp, "wb") as f:
        f.write(jblob)
    json.loads(jblob)  # parse-verify
    mblob = stage_blob(side, mp)
    with open(mp, "wb") as f:
        f.write(mblob)
    report.append(f"twin {jp} + md: :{side}: (ts2={t2!r} ts3={t3!r}) md byte-copied same side")

# --- append-log jsonl: multiset union vs base, chronological tail by embedded ts (r188) ---
p = "results/x2_watch_log.jsonl"
b1, b2, b3 = [stage_blob(s, p).decode().splitlines() for s in (1, 2, 3)]
m1, m2, m3 = map(collections.Counter, (b1, b2, b3))
orig_new, mine_new = list((m2 - m1).elements()), list((m3 - m1).elements())
def _ts(line):
    try:
        return json.loads(line).get("ts", "")
    except Exception:
        return ""
tail = sorted(orig_new + mine_new, key=_ts)
result_lines = b1 + [l for l in b2 if l not in m1][:0] or b1  # base first
result_lines = b1 + tail
blob = ("\n".join(result_lines) + "\n").encode()
with open(p, "wb") as f:
    f.write(blob)
assert collections.Counter(result_lines) == m1 + collections.Counter(orig_new) + collections.Counter(mine_new), "jsonl union multiset mismatch"
report.append(f"append-log {p}: base={sum(m1.values())} + orig_new={len(orig_new)} + mine_new={len(mine_new)} -> {len(result_lines)} lines, multiset-verified, tail chronologically sorted")

# --- b_layer_mask.csv: row-order face (verified multiset-identical) -> take :2: whole bytes ---
p = "data/fundamental/b_layer_mask.csv"
c2, c3 = stage_blob(2, p), stage_blob(3, p)
assert collections.Counter(c2.decode().splitlines()) == collections.Counter(c3.decode().splitlines()), "mask multiset mismatch -- do NOT blind-take"
with open(p, "wb") as f:
    f.write(c2)
report.append(f"row-order-csv {p}: :2: taken whole-bytes (multiset-identical verified, order-only face)")

# --- HANDOVER.md anchor-insert (R210): origin lines keep position, latecomer lines appended (bytes-level) ---
p = "research/HANDOVER.md"
raw = open(p, "rb").read()
pat = re.compile(rb"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>>[^\r\n]*\r?\n", re.DOTALL)
blocks = pat.findall(raw)
assert len(blocks) == 1, f"expected exactly 1 conflict block in HANDOVER, found {len(blocks)}"
origin_blk, mine_blk = blocks[0]
resolved = pat.sub(lambda m: m.group(1) + b"\n" + m.group(2) + b"\n", raw, count=1)
assert b"<<<<<<<" not in resolved and b">>>>>>>" not in resolved, "markers remain in HANDOVER"
with open(p, "wb") as f:
    f.write(resolved)
report.append(f"anchor-insert {p}: 1 block -> origin {len(origin_blk)}B + latecomer {len(mine_blk)}B both kept (R210)")

print("\n".join(report))
print(f"RESOLVED {len(SNAPSHOTS)+1+len(TWINS)*2+3} files; ALL verified")
