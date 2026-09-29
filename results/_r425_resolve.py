# r425 rebase storm resolver -- non-ALL_FACES legs (snapshot deep-ts + js same-side whole-bytes + twin-regen-md side-coupling)
# Laws: r188/R208 snapshot take-new; R209 js wrapper whole-bytes; r327/r329 twin md same-side byte-copy;
#       r100/R350 hardened probe (strip _/- before prefix match, value ^20\d{2}- + time-of-day required, staged blob only);
#       r185 parse-verify before write-back; r140 same-second tie -> take :2: base-side (HEAD in merge, base in rebase).
import json, re, subprocess, sys

def stage_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {stage}:{path}: {r.stderr[:200]!r}")
    return r.stdout

TS_SHAPE = re.compile(r"^20\d{2}-")
HAS_TOD = re.compile(r"[T ]\d{1,2}:\d{2}")
PREFIXES = ("asof", "generated", "updated", "ts", "cutoff", "lastrun", "checked")

def deep_ts(obj, best):
    # collect max wall-clock ts among string values under keys that (normalized) start with a clock prefix
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

# --- snapshot faces: take-new whole doc ---
SNAPSHOTS = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
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

print("\n".join(report))
print(f"RESOLVED {len(SNAPSHOTS)+1+len(TWINS)*2} files; ALL parse-verified / byte-copied")
