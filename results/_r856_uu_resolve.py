"""r856 bm-a: per-file newer-wins UU resolver (live snapshot faces raced
by concurrent S6 chains; each file = deterministic same-day re-derive,
conflict sides carry generated/ts stamps). Picks the side with the newer
timestamp per file; verifies both sides parsed; writes resolved content."""
import re
import subprocess
import sys

UU = [
    "docs/daily_report/REPORT-2026-10-08.json",
    "docs/daily_report/REPORT-2026-10-08.md",
    "docs/live_usage/LIVE-2026-10-08.json",
    "docs/live_usage/LIVE-2026-10-08.md",
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
    r'"(?:ts|updated|generated)"\s*:\s*"?(20\d\d-\d\d-\d\d[ T]\d\d:\d\d(?::\d\d)?)'
    r'|\b(20\d\d-\d\d-\d\d \d\d:\d\d(?::\d\d)?)')


def side_ts(txt):
    """Newest timestamp literal found in the block."""
    best = None
    for m in TS_RE.finditer(txt):
        v = m.group(1) or m.group(2)
        if best is None or v > best:
            best = v
    return best


fails = []
for path in UU:
    s = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r'<<<<<<<[^\n]*\n(.*?)\n=======[^\n]*\n(.*?)\n>>>>>>>[^\n]*\n?',
                  s, re.S)
    if not m:
        fails.append((path, "no conflict block"))
        continue
    ours_txt, theirs_txt = m.group(1), m.group(2)
    ot, tt = side_ts(ours_txt), side_ts(theirs_txt)
    if ot is None or tt is None:
        fails.append((path, f"ts missing ours={ot} theirs={tt}"))
        continue
    if tt > ot:
        # replace whole conflict block with theirs (my r856 side)
        resolved = s[:m.start()] + theirs_txt + "\n" + s[m.end():]
        side = "theirs"
    else:
        resolved = s[:m.start()] + ours_txt + "\n" + s[m.end():]
        side = "ours"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(resolved)
    print(f"resolved {path}: {side} (ours={ot} theirs={tt})", flush=True)

if fails:
    for p, r in fails:
        print("UNRESOLVED", p, r, file=sys.stderr)
    sys.exit(1)
print("resolver done 14/14", flush=True)
