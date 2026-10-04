# -*- coding: utf-8 -*-
# r655 bm-b merge resolver: 21 UU same-window S6 derive faces.
# Category law (r440/r652): regenerable derive faces -> take-new-by-ts
# (embedded ts, both sides compared); append-only jsonl ledger -> line union;
# ts unparseable -> origin (theirs) per regenerable-face default.
import re
import subprocess
import sys

FACES = [
    "docs/daily_report/REPORT-20261004.json",
    "docs/daily_report/REPORT-20261004.md",
    "docs/live_usage/LIVE-20261004.json",
    "docs/live_usage/LIVE-20261004.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/post_review.jsonl",
    "results/post_review/REPORT-20261004.md",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

CREATE = 0x08000000
TS_RE = re.compile(
    r'"(?:ts|generated|generated_at|asof|written_at|probe_ts)"\s*:\s*"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})'
    r'|(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})')


def stage(side, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (side, path)],
                       capture_output=True, creationflags=CREATE)
    return r.stdout if r.returncode == 0 else b""


def ts_of(b):
    m = TS_RE.search(b.decode("utf-8", "replace")[:4000])
    if not m:
        return None
    d = m.group(1) or m.group(3)
    t = m.group(2) or m.group(4)
    return d + " " + t if d and t else None


def pick(side, path):
    subprocess.run(["git", "checkout", "--%s" % side, "--", path],
                   capture_output=True, creationflags=CREATE)


log = []
for path in FACES:
    ours, theirs = stage(2, path), stage(3, path)
    if path.endswith(".jsonl"):
        # append-only ledger: line union, ours-first, theirs-new-lines appended
        o_lines = ours.splitlines()
        o_set = set(o_lines)
        t_new = [ln for ln in theirs.splitlines() if ln not in o_set]
        merged = b"\n".join(o_lines + t_new) + (b"\n" if o_lines or t_new else b"")
        with open(path, "wb") as f:
            f.write(merged)
        log.append("UNION   %s (ours=%d + theirs_new=%d)" % (path, len(o_lines), len(t_new)))
        continue
    to, tt = ts_of(ours), ts_of(theirs)
    if to and tt:
        if to >= tt:
            pick("ours", path)
            log.append("OURS    %s (ts %s >= %s)" % (path, to, tt))
        else:
            pick("theirs", path)
            log.append("THEIRS  %s (ts %s < %s)" % (path, to, tt))
    else:
        pick("theirs", path)
        log.append("THEIRS  %s (ts unparseable ours=%s theirs=%s -> origin default)" % (path, to, tt))

for ln in log:
    print(ln)
# marker check on resolved faces (content check, not rc -- r644 --check law)
bad = []
for path in FACES:
    b = open(path, "rb").read()
    if b.startswith(b"<<<<<<<") or b"\n<<<<<<< " in b:
        bad.append(path)
print("marker_residual:", bad or "NONE")
sys.exit(1 if bad else 0)
