# -*- coding: utf-8 -*-
# r866 bm-c rebase resolver: 31 UU shared regen faces (bm-b r873 same-window S6 co-run)
# bloodline: _r856bmc_rebase_resolver.py (ts-audited newer-wins per face, md/js twins follow json,
#            compute_audit history ts-key UNION per r773 law, x2_watch_log line-union r855 law).
# STAGE SEMANTICS VERIFIED LIVE THIS ROUND (probe: stage2 daily_report prev=09:14:34 = bm-b lineage,
# stage3 prev=09:53:45 = my r865 lineage) -> :2: = base (bm-b origin/main side),
# :3: = replayed commit (MY r866 side). Standard rebase inversion CONFIRMED.
import subprocess, json, re, io

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"
BASE_STAGE, MY_STAGE = 2, 3  # base=bm-b origin side, mine=replayed r866 commit

TS_AUDIT_JSON = [
    "docs/daily_report/REPORT-2026-10-11.json",
    "docs/live_usage/LIVE-2026-10-11.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/daily_scorecard.json",
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
]
TWIN_OF = {  # follower -> authority
    "docs/daily_report/REPORT-2026-10-11.md": "docs/daily_report/REPORT-2026-10-11.json",
    "docs/live_usage/LIVE-2026-10-11.md": "docs/live_usage/LIVE-2026-10-11.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}

TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}(?::\d{2})?)")

def norm_ts(s):
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
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, ("marker in staged side blob", path, side)
    write_bytes(path, raw)
    # marker-guard leg (r808 law): verify disk face clean BEFORE add
    full = REPO + "\\" + path.replace("/", "\\")
    body = io.open(full, "r", encoding="utf-8", errors="replace").read()
    assert "<<<<<<<" not in body and ">>>>>>>" not in body, ("marker on disk after resolve", path)
    git_add(path)
    report.append((path, why))

# ---- phase 1: json faces ts-newer-wins (skip union + twins) ----
json_side = {}
for p in TS_AUDIT_JSON:
    o, t = ts_of(stage_bytes(BASE_STAGE, p)), ts_of(stage_bytes(MY_STAGE, p))
    if o is None and t is None:
        side, why = MY_STAGE, "no-ts-both->mine"
    elif o is None:
        side, why = MY_STAGE, "base-no-ts->mine"
    elif t is None:
        side, why = BASE_STAGE, "mine-no-ts->base"
    else:
        side = MY_STAGE if t >= o else BASE_STAGE
        why = "ts base=%s mine=%s -> %s" % (o, t, "mine" if side == MY_STAGE else "base")
    json_side[p] = side
    resolve_side(p, side, why)

# ---- phase 2: twin followers take authority's side (r708/r939) ----
for p, auth in TWIN_OF.items():
    side = json_side.get(auth, MY_STAGE)
    resolve_side(p, side, "twin-follows %s -> %s" % (auth, "mine" if side == MY_STAGE else "base"))

# ---- phase 3: compute_audit.json = history ts-key union (r773) ----
o_raw, t_raw = stage_bytes(BASE_STAGE, "results/compute_audit.json"), stage_bytes(MY_STAGE, "results/compute_audit.json")
o_d, t_d = json.loads(o_raw.decode("utf-8")), json.loads(t_raw.decode("utf-8"))
o_hist, t_hist = o_d.get("history", []), t_d.get("history", [])
union = {}
for e in o_hist:
    union[e.get("ts")] = e
for e in t_hist:  # mine wins same-ts collision (newer replay)
    union[e.get("ts")] = e
merged = sorted(union.values(), key=lambda e: str(e.get("ts")))
merged = merged[-201:]  # match writer cap shape
base = t_d if (ts_of(t_raw) or "") >= (ts_of(o_raw) or "") else o_d
base["history"] = merged
write_bytes("results/compute_audit.json", json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
git_add("results/compute_audit.json")
report.append(("results/compute_audit.json",
               "UNION ts-key base=%d mine=%d -> union=%d (cap 201) latest-base=%s" %
               (len(o_hist), len(t_hist), len(merged), "mine" if base is t_d else "base")))

# ---- phase 4: x2_watch_log.jsonl = line-content union across all 3 stages (r855 law) ----
def jsonl_union(path):
    seen, out = set(), []
    for stage in (1, 2, 3):  # ancestor, base(bm-b), mine
        raw = stage_bytes(stage, path)
        if raw is None:
            continue
        for line in raw.decode("utf-8", "replace").splitlines():
            line = line.strip()
            if not line or line in seen:
                continue
            seen.add(line)
            try:
                key = norm_ts(json.loads(line).get("ts")) or line
            except Exception:
                key = line
            out.append((key, line))
    out.sort(key=lambda kv: kv[0])
    body = "\n".join(kv[1] for kv in out) + "\n"
    write_bytes(path, body.encode("utf-8"))
    # marker-guard before add
    full = REPO + "\\" + path.replace("/", "\\")
    chk = io.open(full, "r", encoding="utf-8", errors="replace").read()
    assert "<<<<<<<" not in chk and ">>>>>>>" not in chk, ("marker on disk after union", path)
    git_add(path)
    report.append((path, "line-union 3-stage dedupe -> %d lines" % len(out)))

jsonl_union("results/x2_watch_log.jsonl")

for p, why in report:
    print("%s: %s" % (p, why))
print("RESOLVED %d files (31 UU expected)" % len(report))
assert len(report) == 31, "expected 31 resolved faces, got %d" % len(report)
