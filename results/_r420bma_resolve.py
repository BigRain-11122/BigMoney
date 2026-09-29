"""r420 bm-a merge resolver: snapshot + js-wrapper + twin-regen faces (skill recipes r100/R209/r327/r329).

Stage law under MERGE: :1:=base, :2:=ours(HEAD=faf91c149 r419 products 07:46-47),
:3:=theirs(origin/main=bm-c r204 dead-window harvest 07:25-31).
Deep-ts probe (r100): key normalize strip '_/-', value must match ^20\\d{2}- (with time-of-day for wall-clock).
Twin law (r329): json face decides side by probe; md face byte-copied from SAME side (no hybrid twins).
Whole-doc byte takes for snapshots/js (no json.dumps rewrite of js wrapper - R209).
"""
import json, re, subprocess, sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def probe_ts(obj, best=("", )):
    """deep probe: return max ts-shaped string under keys matching updated/generated/asof/cutoff family."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and TS_RE.match(v) and any(
                nk.startswith(p) for p in ("updated", "generated", "asof", "cutoff", "last")
            ):
                if v > best[0]:
                    best = (v, )
            else:
                best = probe_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = probe_ts(v, best)
    return best


def take_newer(path, key_hint=None):
    a, b = blob(2, path), blob(3, path)
    ja, jb = json.loads(a), json.loads(b)
    ta, tb = probe_ts(ja)[0], probe_ts(jb)[0]
    side = 2 if ta >= tb else 3
    ts_win = ta if side == 2 else tb
    data = a if side == 2 else b
    open(path, "wb").write(data)
    json.loads(data)  # parse-verify
    print(f"[take-new] {path}: ours_ts={ta} theirs_ts={tb} -> side={':2:ours' if side==2 else ':3:theirs'} ({ts_win})")
    return side


def twin_pair(json_path, md_path):
    side = take_newer(json_path)
    src = blob(side, md_path)
    open(md_path, "wb").write(src)
    print(f"[twin-md] {md_path}: byte-copied from same side :{side}: ({len(src)}B)")


# --- snapshot faces (whole-doc take-new by deep ts probe) ---
snapshots = [
    "results/fundamental_b_layer_filter.json",
    "results/dashboard_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]
for p in snapshots:
    take_newer(p)

# --- js wrapper (R209): whole-byte take-side by embedded ts, no rewrite ---
jsp = "results/dashboard_status.js"
a, b = blob(2, jsp), blob(3, jsp)
ma = re.search(rb"window\.DASH_DATA\s*=\s*(\{.*?\});", a, re.S)
mb = re.search(rb"window\.DASH_DATA\s*=\s*(\{.*?\});", b, re.S)
ja = json.loads(ma.group(1)) if ma else {}
jb = json.loads(mb.group(1)) if mb else {}
ta, tb = probe_ts(ja)[0], probe_ts(jb)[0]
side = 2 if ta >= tb else 3
data = a if side == 2 else b
open(jsp, "wb").write(data)
json.loads((ma if side == 2 else mb).group(1))  # parse-verify wrapper payload
print(f"[js-wrapper] {jsp}: ours_ts={ta} theirs_ts={tb} -> whole-byte side={':2:ours' if side==2 else ':3:theirs'}")

# --- twin-regen pairs (r327/r329): json probe decides, md same-side byte copy ---
twin_pair("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md")
twin_pair("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md")
twin_pair("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")

print("resolver done (CODELY.md handled separately by entry-level union)")
