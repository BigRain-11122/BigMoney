import json, re, subprocess

FILES = [
 "docs/daily_report/REPORT-2026-10-10.json",
 "docs/daily_report/REPORT-2026-10-10.md",
 "docs/live_usage/LIVE-2026-10-10.json",
 "docs/live_usage/LIVE-2026-10-10.md",
 "docs/live_usage/LIVE-latest.json",
 "docs/live_usage/LIVE-latest.md",
 "results/_attrition_guard_scan.json",
 "results/_r686bmb_d19_check.json",
 "results/compute_audit.json",
 "results/d19_watermark.json",
 "results/fundamental_b_layer_filter.json",
 "results/futures_update_status.json",
 "results/lhb_update_status.json",
 "results/regime_state.json",
 "results/token_usage.json",
 "results/update_status.json",
]

TS_KEYS = ("ts","updated_at","updated","generated","generated_at","asof","cutoff","scan_ts","probe_ts","last_run","written_at")

def extract_ts(text):
    cands = []
    try:
        obj = json.loads(text)
    except Exception:
        obj = None
    if isinstance(obj, dict):
        stack = [obj]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                for k, v in cur.items():
                    if isinstance(v, str) and (k in TS_KEYS or k.endswith("_ts") or k.endswith("_at")) and re.search(r"2026-10-10T", v):
                        cands.append(v)
                    elif isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(cur, list):
                stack.extend([x for x in cur if isinstance(x, (dict, list))])
    if not cands:
        for m in re.finditer(r"2026-10-10T\d{2}:\d{2}(:\d{2})?", text):
            cands.append(m.group(0))
    cands.sort(reverse=True)
    return cands[0] if cands else ""

def blob(stage, f):
    return subprocess.run(["git","show",":%s:%s"%(stage,f)],capture_output=True).stdout.decode("utf-8","replace")

report = []
for f in FILES:
    ours = blob(2, f)
    theirs = blob(3, f)
    om = (">>>>>>>" in ours)
    tm = (">>>>>>>" in theirs)
    to, tt = extract_ts(ours), extract_ts(theirs)
    if om and not tm:
        winner, why = theirs, "ours-has-markers"
    elif tm and not om:
        winner, why = ours, "theirs-has-markers"
    elif to and tt:
        if to >= tt:
            winner, why = ours, "ours-newer"
        else:
            winner, why = theirs, "theirs-newer"
    else:
        winner, why = theirs, "no-ts-fallback-theirs"
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(winner)
    report.append({"file": f, "ours_ts": to, "theirs_ts": tt, "took": why})

with open("results/_r961bma_uu_resolve.json","w",encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
for r in report:
    print(r["file"], "|", r["ours_ts"], "|", r["theirs_ts"], "|", r["took"])
