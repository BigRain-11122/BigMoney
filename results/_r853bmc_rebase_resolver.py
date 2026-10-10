# -*- coding: utf-8 -*-
# r853 bm-c rebase resolver: 31 UU shared regen faces (bm-b r862 same-window S6 co-run)
# bloodline: _r852bmc_rebase_resolver.py (verbatim clone, face-count 31 (r852 bloodline)) (per-file ts newer-wins, md twins follow json)
# upgrades per law: r773 union duo (compute_audit history ts-key union + x2 jsonl line union),
#                  r711/r756 ts format normalization (space/T dict-order poison),
#                  r708 twin-consistency (js follows json).
# rebase mode: :2: = ours (r853 close), :3: = theirs (bm-b r862). Python bytes IO only (r710 law A).
import subprocess, json, re, sys, io

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

UU_ALL = [
    "docs/daily_report/REPORT-2026-10-11.json", "docs/daily_report/REPORT-2026-10-11.md",
    "docs/live_usage/LIVE-2026-10-11.json", "docs/live_usage/LIVE-2026-10-11.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",            # UNION face (r773)
    "results/daily_scorecard.json",
    "results/dashboard_status.js",           # twin-follows dashboard_status.json (r708)
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-10-09.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/x2_watch_log.jsonl",            # UNION face (r773 jsonl line-union)
]
UNION_FACES = {"results/compute_audit.json", "results/x2_watch_log.jsonl"}
TWIN_OF = {  # follower -> authority
    "docs/daily_report/REPORT-2026-10-11.md": "docs/daily_report/REPORT-2026-10-11.json",
    "docs/live_usage/LIVE-2026-10-11.md": "docs/live_usage/LIVE-2026-10-11.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}

TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}(?::\d{2})?)")

def norm_ts(s):
    """r711/r756 law: normalize space/T + pad seconds + strip tz before compare."""
    if s is None:
        return None
    s = str(s)
    m = TS_RE.search(s)
    if not m:
        return None
    date, hm = m.group(1), m.group(2)
    if len(hm) == 5:
        hm += ":00"
    return date + "T" + hm

def stage_bytes(stage, path):
    r = subprocess.run([GIT, "-C", REPO, "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    return r.stdout

def ts_of(raw):
    if raw is None:
        return None
    try:
        d = json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        m = TS_RE.search(raw[:4096].decode("utf-8", "replace"))
        return norm_ts(m.group(0)) if m else None
    def dig(o):
        if isinstance(o, dict):
            for k in ("ts", "generated_at", "generated", "updated_at", "updated", "asof", "cutoff"):
                if k in o and isinstance(o[k], (str, int, float)):
                    n = norm_ts(str(o[k]))
                    if n:
                        return n
            for v in o.values():
                r = dig(v)
                if r:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = dig(v)
                if r:
                    return r
        return None
    return dig(d)

def write_bytes(path, data):
    full = REPO + "\\" + path.replace("/", "\\")
    with io.open(full, "wb") as f:
        f.write(data)

def git_add(path):
    subprocess.run([GIT, "-C", REPO, "add", path], check=True)

report = []

def resolve_side(path, side, why):
    raw = stage_bytes(side, path)
    assert raw is not None and len(raw) > 0, "empty side %d for %s" % (side, path)
    write_bytes(path, raw)
    git_add(path)
    report.append((path, why))

# ---- phase 1: json faces ts-newer-wins (skip union + twins) ----
json_side = {}
for p in UU_ALL:
    if p in UNION_FACES or p in TWIN_OF or not p.endswith(".json"):
        continue
    o, t = ts_of(stage_bytes(2, p)), ts_of(stage_bytes(3, p))
    if o is None and t is None:
        side, why = 2, "no-ts-both->ours"
    elif t is None:
        side, why = 2, "theirs-no-ts->ours"
    elif o is None:
        side, why = 3, "ours-no-ts->theirs"
    else:
        side = 2 if o >= t else 3
        why = "ts ours=%s theirs=%s -> %s" % (o, t, "ours" if side == 2 else "theirs")
    json_side[p] = side
    resolve_side(p, side, why)

# ---- phase 2: twin followers take authority's side (r708/r939) ----
for p, auth in TWIN_OF.items():
    side = json_side.get(auth, 2)
    resolve_side(p, side, "twin-follows %s -> %s" % (auth, "ours" if side == 2 else "theirs"))

# ---- phase 3: compute_audit.json = history ts-key union (r773) ----
o_raw, t_raw = stage_bytes(2, "results/compute_audit.json"), stage_bytes(3, "results/compute_audit.json")
o_d, t_d = json.loads(o_raw.decode("utf-8")), json.loads(t_raw.decode("utf-8"))
o_hist, t_hist = o_d.get("history", []), t_d.get("history", [])
union = {}
for e in t_hist:
    union[e.get("ts")] = e
for e in o_hist:  # ours wins same-ts collision (newer replay)
    union[e.get("ts")] = e
merged = sorted(union.values(), key=lambda e: str(e.get("ts")))
merged = merged[-201:]  # match writer cap shape (raw_hist[-200:] + latest append)
base = o_d if (ts_of(o_raw) or "") >= (ts_of(t_raw) or "") else t_d
base["history"] = merged
write_bytes("results/compute_audit.json", json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
git_add("results/compute_audit.json")
report.append(("results/compute_audit.json",
               "UNION ts-key ours=%d theirs=%d -> union=%d (cap 201) latest-base=%s" %
               (len(o_hist), len(t_hist), len(merged), "ours" if base is o_d else "theirs")))

# ---- phase 4: x2_watch_log.jsonl = line union merge-sorted by ts (r773/r511) ----
o_raw, t_raw = stage_bytes(2, "results/x2_watch_log.jsonl"), stage_bytes(3, "results/x2_watch_log.jsonl")
o_lines = [l for l in o_raw.decode("utf-8").splitlines() if l.strip()]
t_lines = [l for l in t_raw.decode("utf-8").splitlines() if l.strip()]
seen = set()
merged = []
def line_ts(l):
    try:
        return norm_ts(json.loads(l).get("ts")) or ""
    except Exception:
        return ""
for l in sorted(o_lines + t_lines, key=line_ts):
    if l in seen:
        continue
    seen.add(l)
    merged.append(l)
write_bytes("results/x2_watch_log.jsonl", ("\n".join(merged) + "\n").encode("utf-8"))
git_add("results/x2_watch_log.jsonl")
report.append(("results/x2_watch_log.jsonl",
               "UNION lines ours=%d theirs=%d shared=%d -> %d" %
               (len(o_lines), len(t_lines), len(o_lines) + len(t_lines) - len(set(o_lines) | set(t_lines)) - (len(o_lines)+len(t_lines)) + len(set(o_lines)&set(t_lines)), len(merged))))

for p, why in report:
    print("%s: %s" % (p, why))
print("RESOLVED %d files (31 UU expected)" % len(report))
assert len(report) == 31, "expected 31 resolved faces, got %d" % len(report)
