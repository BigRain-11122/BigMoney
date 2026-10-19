# r1035 S0 rebase UU resolver: per-face ts-probe newer-wins (r1028 law)
# UU faces from rebase replay of 6f947cccd (bm-b r1034) onto origin/main (bm-c r1125 line)
import subprocess, json, re, sys, io

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
FILES = [
    "docs/daily_report/REPORT-2026-10-19.json",
    "docs/daily_report/REPORT-2026-10-19.md",
    "docs/live_usage/LIVE-2026-10-19.json",
    "docs/live_usage/LIVE-2026-10-19.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]

def git(args):
    r = subprocess.run(["git", "-C", REPO] + args, capture_output=True, text=False)
    return r.returncode, r.stdout, r.stderr

TS_PAT = re.compile(r'"(generated|ts|updated|updated_at|asof|as_of|checked_at|built_at|scan_ts|probe_ts|last_scan)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})')
MD_PAT = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')

def ts_of(raw: bytes, name: str):
    if not raw:
        return None
    try:
        txt = raw.decode("utf-8", errors="replace")
    except Exception:
        return None
    best = None
    if name.endswith(".json") or name.endswith(".js"):
        for m in TS_PAT.finditer(txt):
            v = m.group(2).replace(" ", "T")
            if best is None or v > best:
                best = v
    if best is None:
        # md or fallback: latest timestamp anywhere
        for m in MD_PAT.finditer(txt):
            v = m.group(1).replace(" ", "T")
            if best is None or v > best:
                best = v
    return best

report = {}
for f in FILES:
    rc2, ours, e2 = git(["show", ":2:" + f])   # ours = origin/base side (bm-c r1125 line)
    rc3, theirs, e3 = git(["show", ":3:" + f]) # theirs = bm-b r1034 commit side
    to, tt = ts_of(ours, f), ts_of(theirs, f)
    if tt is not None and (to is None or tt >= to):
        winner, side = theirs, "theirs(bm-b)"
    elif to is not None:
        winner, side = ours, "ours(origin)"
    else:
        winner, side = theirs, "theirs(bm-b, no-ts-fallback)"
    with io.open(REPO + "\\" + f.replace("/", "\\"), "wb") as fh:
        fh.write(winner)
    rc_add, _, e_add = git(["add", "--", f])
    report[f] = {"ours_ts(origin)": to, "theirs_ts(bm-b)": tt, "winner": side, "add_rc": rc_add}
    if rc_add != 0:
        report[f]["add_err"] = e_add.decode("utf-8", errors="replace")

print(json.dumps(report, ensure_ascii=False, indent=1))
