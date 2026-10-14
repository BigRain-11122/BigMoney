# r1005 bm-a rebase conflict resolver (estate-absorption commit vs origin/main storm)
# Skill: bigmoney-conflict-resolve. r351: :2:=origin side, :3:=local(mine) side.
# r185: parse-verify before add. r140: same-second tie -> mine. Marker scan before add (r868/r836 law).
import subprocess, json, re, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def run(*a):
    r = subprocess.run([GIT] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

def blob_bytes(stage, path):
    r = subprocess.run([GIT, "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout

TS_SHAPE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def deep_probe(obj, key_list):
    """normalized-key prefix match (r100: strip _/-) + value-shape gate (R350: time-of-day required)."""
    nkeys = [re.sub(r'[_\-]', '', k).lower() for k in key_list]
    best = [None]
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                nk = re.sub(r'[_\-]', '', k).lower()
                if isinstance(v, str) and TS_SHAPE.match(v):
                    for nkx in nkeys:
                        if nk.startswith(nkx):
                            if best[0] is None or v > best[0]:
                                best[0] = v
                            break
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)
    walk(obj)
    return best[0]

# ---- authoritative unmerged list ----
conflicts = [l for l in run("diff", "--name-only", "--diff-filter=U").splitlines() if l.strip()]
print("total unmerged:", len(conflicts))

# ---- face plan ----
ALL_FACES = ["results/compute_audit.json", "results/regime_state.json",
             "results/token_usage.json", "results/update_status.json"]
JSONL_UNION = ["results/x2_watch_log.jsonl"]
PROBES = {  # path -> key list for hardened deep-ts probe (both staged blobs)
    "docs/daily_report/REPORT-2026-10-15.json": ["generated_at"],
    "results/paper/COMPOSITE-CE-01_paper.json": ["updated"],
    "results/paper/COMPOSITE-CE-02_paper.json": ["updated"],
    "results/paper/DROUGHT-CE-01_paper.json": ["updated"],
    "results/paper/ENGULF-CE-01_paper.json": ["updated"],
    "results/paper/NEEDLE-DE-01_paper.json": ["updated"],
    "results/paper/VOLATILITY-CE-01_paper.json": ["updated"],
    "results/paper_export/export-2026-10-14.json": ["state_updated", "generated_from_state_updated"],
    "results/paper_export/latest.json": ["state_updated", "generated_from_state_updated"],
    "results/t35_open_fill_verify.json": ["ts", "as_of", "state_updated"],
    "results/prospect_paper/_summary.json": ["generated"],
    "results/prospect_promotion/_summary.json": ["generated"],
    "results/_attrition_guard_scan.json": ["ts"],
}
# twin coupling: json decides, md + pointer twins byte-copy SAME side
LIVE_DECIDER = "docs/live_usage/LIVE-2026-10-15.json"
LIVE_FAMILY = ["docs/live_usage/LIVE-2026-10-15.json", "docs/live_usage/LIVE-2026-10-15.md",
               "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]
LIVE_KEYS = ["generated"]
REPORT_MD = "docs/daily_report/REPORT-2026-10-15.md"

plan = set(ALL_FACES) | set(JSONL_UNION) | set(PROBES) | set(LIVE_FAMILY) | {REPORT_MD}
unplanned = [f for f in conflicts if f not in plan]
if unplanned:
    print("UNPLANNED CONFLICTS (fail-closed):", unplanned)
    sys.exit(2)

report = []
resolved_ok = []

# ---- 1) ALL_FACES: merge_lane_views resolve (r377: 禁手写 union) ----
for f in ALL_FACES:
    r = subprocess.run(["python", "scripts\\merge_lane_views.py", "resolve", f],
                       capture_output=True, cwd=ROOT)
    out = (r.stdout + r.stderr).decode("utf-8", errors="replace")
    ok = r.returncode == 0
    if ok:
        json.loads(open(f, "rb").read().decode("utf-8", errors="strict"))  # parse-verify (r185)
    report.append("MLV %s rc=%d %s" % (f, r.returncode, out.strip()[-160:]))
    if ok:
        resolved_ok.append(f)
    else:
        print("MLV FAIL", f, out)
        sys.exit(3)

# ---- 2) jsonl line-level union (r188/r217: zero loss) ----
for f in JSONL_UNION:
    o_lines = blob_bytes(2, f).decode("utf-8", errors="replace").splitlines()
    m_lines = blob_bytes(3, f).decode("utf-8", errors="replace").splitlines()
    seen, merged = set(), []
    for ln in o_lines + m_lines:
        t = ln.strip()
        if t and t not in seen:
            seen.add(t)
            merged.append(ln)
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(merged) + ("\n" if merged else ""))
    for ln in merged:  # parse-verify each jsonl line (r185)
        if ln.strip():
            json.loads(ln)
    report.append("JSONL-UNION %s origin=%d mine=%d union=%d" % (f, len(o_lines), len(m_lines), len(merged)))
    resolved_ok.append(f)

def take_side(f, stage):
    r = subprocess.run([GIT, "checkout", ("--ours" if stage == 2 else "--theirs"), "--", f],
                       capture_output=True)
    if r.returncode != 0:
        print("CHECKOUT FAIL", f, r.stderr.decode("utf-8", "replace"))
        sys.exit(4)
    run("add", "--", f)
    return stage

# ---- 3) probed snapshot faces ----
for f, keys in PROBES.items():
    if f not in conflicts:
        continue
    try:
        ts_o = deep_probe(json.loads(blob_bytes(2, f).decode("utf-8")), keys)
        ts_m = deep_probe(json.loads(blob_bytes(3, f).decode("utf-8")), keys)
    except Exception as e:
        print("PROBE FAIL", f, e)
        sys.exit(5)
    if ts_m and (not ts_o or ts_m >= ts_o):
        side = take_side(f, 3); win = "mine"
    elif ts_o and not ts_m:
        side = take_side(f, 2); win = "origin"
    elif ts_o and ts_o > ts_m:
        side = take_side(f, 2); win = "origin"
    else:
        side = take_side(f, 3); win = "mine(tie/default r948)"
    report.append("SNAP %s -> %s (origin=%s mine=%s)" % (f, win, ts_o, ts_m))
    resolved_ok.append(f)

# ---- 4) LIVE twin family: decider json probes, ALL FOUR take same side ----
if LIVE_DECIDER in conflicts:
    ts_o = deep_probe(json.loads(blob_bytes(2, LIVE_DECIDER).decode("utf-8")), LIVE_KEYS)
    ts_m = deep_probe(json.loads(blob_bytes(3, LIVE_DECIDER).decode("utf-8")), LIVE_KEYS)
    win_stage = 2 if (ts_o and (not ts_m or ts_o > ts_m)) else 3
    for f in LIVE_FAMILY:
        if f in conflicts:
            take_side(f, win_stage)
            resolved_ok.append(f)
    report.append("LIVE-FAMILY x%d -> stage%d (origin=%s mine=%s)" %
                  (len([x for x in LIVE_FAMILY if x in conflicts]), win_stage, ts_o, ts_m))

# ---- 5) REPORT md twin: byte-copy same side as json decider ----
if REPORT_MD in conflicts:
    jr = "docs/daily_report/REPORT-2026-10-15.json"
    ts_o = deep_probe(json.loads(blob_bytes(2, jr).decode("utf-8")), PROBES[jr])
    ts_m = deep_probe(json.loads(blob_bytes(3, jr).decode("utf-8")), PROBES[jr])
    win_stage = 2 if (ts_o and (not ts_m or ts_o > ts_m)) else 3
    take_side(REPORT_MD, win_stage)
    if jr in conflicts:
        take_side(jr, win_stage)
        resolved_ok.append(jr)
    resolved_ok.append(REPORT_MD)
    report.append("REPORT-TWIN -> stage%d (origin=%s mine=%s)" % (win_stage, ts_o, ts_m))

# ---- 6) marker scan before final (r836/r868 law) ----
still = [l for l in run("diff", "--name-only", "--diff-filter=U").splitlines() if l.strip()]
if still:
    print("STILL UNMERGED:", still)
    sys.exit(6)

with open(ROOT + r"\results\_r1005bma_rebase_resolve_report.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(report) + "\n")
print("resolved faces:", len(resolved_ok))
print("\n".join(report))
print("RESOLVE_DONE")
