"""r701 bm-c rebase UU resolver v2 (side-level): each conflicted face is a
machine-generated single snapshot -- pick ONE coherent side per file (ts
newer wins; no-ts/tie -> origin side). Extracts clean sides from git
index stages (2=origin/bm-a, 3=mine) instead of textual block surgery
(v1 block-chimera corrupted 5 JSON faces -- discarded, zero origin harm,
rework same-window). Receipt overwrites v1."""
import datetime as _dt
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TS_RE = re.compile(
    r'"(?:ts|generated|generated_at|asof|updated|updated_at)"\s*:\s*'
    r'"?(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})')
TS_RE2 = re.compile(r'(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})')


def stage(rel, n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, rel)],
                       capture_output=True, cwd=ROOT,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if r.returncode != 0:
        return None
    return r.stdout


def side_ts(raw):
    if raw is None:
        return None
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        return None
    m = TS_RE.search(text) or TS_RE2.search(text)
    if not m:
        return None
    try:
        return _dt.datetime.strptime(m.group(1) + " " + m.group(2),
                                     "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


receipt = {"ts": _dt.datetime.now().isoformat(timespec="seconds"),
           "round": "r701", "machine": "bm-c",
           "law": "side-level ts-resolve v2 (single-snapshot coherence; "
                  "v1 block-chimera discarded same-window)",
           "files": []}
for rel in FILES:
    ours = stage(rel, 2)     # origin/bm-a side
    theirs = stage(rel, 3)   # this round's side
    if ours is None and theirs is None:
        receipt["files"].append({"file": rel, "action": "no-stages"})
        continue
    to, tm = side_ts(ours), side_ts(theirs)
    if to is None and tm is None:
        pick, who = ours, "origin(no-ts)"
    elif tm is None:
        pick, who = ours, "origin(only-origin-ts)"
    elif to is None:
        pick, who = theirs, "mine(only-mine-ts)"
    elif tm > to:
        pick, who = theirs, "mine(newer-ts)"
    else:
        pick, who = ours, "origin(newer-or-equal-ts)"
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    open(path, "wb").write(pick)
    receipt["files"].append({"file": rel, "pick": who,
                             "ts_origin": str(to), "ts_mine": str(tm)})
    print(f"side-resolved {rel}: {who} (origin={to}, mine={tm})")

rp = os.path.join(ROOT, "results", "_r701bmc_uu_resolve.json")
json.dump(receipt, open(rp, "w", encoding="utf-8"), ensure_ascii=False,
          indent=1)
print("receipt ->", rp)
