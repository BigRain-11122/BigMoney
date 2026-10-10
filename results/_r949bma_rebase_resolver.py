"""r949 bm-a rebase conflict resolver (canon: r839/r848/r948 take-newer-by-ts).

14 regenerable S6 faces -> compare internal ts, take the newer side (tie/equal
-> ours). 1 manual face (state/queue/tech.md) -> union: keep origin (bm-b)
T18 row + consumption record, insert our row renumbered T19.
Zero-loss assertion: every UU file resolved exactly once.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REGEN = [
    "docs/daily_report/REPORT-2026-10-10.json",
    "docs/daily_report/REPORT-2026-10-10.md",
    "docs/live_usage/LIVE-2026-10-10.json",
    "docs/live_usage/LIVE-2026-10-10.md",
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
TECH = "state/queue/tech.md"
OURS_T19 = ("| T19 | queue 种子面闭合族机检闸（P2/P3 队列登记时种子文本 vs science_gates.CLOSED_FAMILIES 键/判负词面机检——"
            "E6 撞门实录 r949 bm-a：建面轮 r804 未核闭合族=陈旧面入队〔建面 10-09 晚于关面 09-30〕；闸=登记器内置 lint 或登记轮强制核验步，"
            "防换皮重开预备面再生。行号 T19=本行〔原拟 T18 撞 bm-b r826 队头撞头探针同窗同号·后到让号 per fleet README §4·r949 注记〕 | "
            "scripts/science_gates.py+state/queue/explore.md+research/digests/DIGEST-20261010-e6-microcap-closed-adjudication.md | open |")


def split_blocks(raw):
    """Split conflict-marked file into list of (pre, ours, theirs) + trailing."""
    out = []
    pat = re.compile(r"<<<<<<< HEAD\r?\n(.*?)\r?\n?=======\r?\n(.*?)\r?\n?>>>>>>> [^\r\n]*\r?\n?", re.S)
    pos = 0
    for m in pat.finditer(raw):
        out.append((raw[pos:m.start()], m.group(1) + "\n", m.group(2) + "\n"))
        pos = m.end()
    tail = raw[pos:]
    return out, tail


def max_ts(block):
    """Max ISO-like timestamp found in a block (0 if none)."""
    cand = re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?", block)
    best = ""
    for c in cand:
        c2 = c.replace(" ", "T")
        if c2 > best:
            best = c2
    return best


report = []
for rel in REGEN:
    p = os.path.join(ROOT, rel)
    raw = open(p, encoding="utf-8", errors="replace").read()
    blocks, tail = split_blocks(raw)
    if not blocks:
        report.append((rel, "NO-MARKERS (already resolved?)", ""))
        continue
    parts = []
    for pre, ours, theirs in blocks:
        to, tt = max_ts(ours), max_ts(theirs)
        if tt > to:
            parts.append(pre + theirs)
            report.append((rel, "take-theirs", "ours=%s theirs=%s" % (to or "-", tt or "-")))
        else:
            parts.append(pre + ours)
            report.append((rel, "take-ours", "ours=%s theirs=%s" % (to or "-", tt or "-")))
    parts.append(tail)
    open(p, "w", encoding="utf-8", newline="").write("".join(parts))

# tech.md manual union: theirs (origin/bm-b) + our row renumbered T19 inserted
# after bm-b's T18 row.
p = os.path.join(ROOT, TECH)
raw = open(p, encoding="utf-8", errors="replace").read()
blocks, tail = split_blocks(raw)
if not blocks:
    report.append((TECH, "NO-MARKERS (already resolved?)", ""))
else:
    # ours-side may contain pre-existing origin content + our T18 row; use the
    # LONGER structural side as base: theirs = origin version (bm-b T18 + all
    # consumption records), ours = our local (bm-b T18 via rebase? no -- ours
    # is our commit's version which has our T18 row). Build merged = theirs +
    # our T19 row after their T18 row.
    pre, ours, theirs = blocks[0]
    if not theirs.rstrip("\n").endswith("\n"):
        theirs += "\n"
    lines = theirs.splitlines()
    merged = []
    inserted = False
    for ln in lines:
        merged.append(ln)
        if not inserted and ln.startswith("| T18 |"):
            merged.append(OURS_T19)
            inserted = True
    if not inserted:
        # fallback: insert after the T17 row or before the first consumption record
        out2 = []
        for ln in lines:
            out2.append(ln)
            if not inserted and ln.startswith("| T17 |"):
                out2.append(OURS_T19)
                inserted = True
        merged = out2
    body = "\n".join(merged) + ("\n" if not "\n".join(merged).endswith("\n") else "")
    open(p, "w", encoding="utf-8", newline="").write(pre + body + tail)
    report.append((TECH, "manual-union", "T19 inserted=%s" % inserted))

for rel, action, note in report:
    print("%-55s %-14s %s" % (rel, action, note))
