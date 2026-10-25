# -*- coding: utf-8 -*-
"""r1240 bm-c: round-report addendum — mid/close-window D-19 decisions delta consumed."""
import io
from datetime import datetime

TS = datetime.now().astimezone().isoformat(timespec='seconds')
P = 'round_reports-bm-c.md'
line = (
    f"{TS} | r1240-addendum | D-19 CLOSE-WINDOW DECISIONS DELTA CONSUMED (decisions.md "
    "0bf59c3c92->f94a284c1b5531ba, blob 215,741->222,683B, source commit 49d7f11 — landed "
    "mid-round, caught by the S7 tail scan). New rows D-20261025-05..08 reviewed: "
    "(a) D-20261025-05 group ledger split thresholds = HQ/night-round file-governance face, "
    "**zero action here** (not our repo's ledgers); "
    "(b) D-20261025-06 27 UNEXPECTED-DISABLED classification -> **BigMoney owner confirmation "
    "issued this window** (HQ-FEEDBACK F-20261025-02): the 7 Bigmoney-* tasks are DESIGN-STATE "
    "disabled by the 2026-10-17 CEO cleanup order, whitelist them (owner=BigMoney, review "
    "2026-11-08); no blind re-enable requested — restoring them needs a CEO word; "
    "(c) D-20261025-07 MV V5 receipt overdue = BigStream director seat, zero action here; "
    "(d) D-20261025-08 D-19 watermark quartet -> **implemented this window**: "
    "Tools/d19_check.py now writes state d19_watermark_v2.{decisions,orders} = {repo(origin url), "
    "commit_sha(40), blob_bytes, sha256, path, fetch_command} with the law's compare order "
    "(repo+commit+bytes first, then sha256; source mismatch = stale, never advance) while keeping "
    "the legacy triple fields; verified live: --update wrote decisions f94a284c1b… / 222,683 B / "
    "commit 49d7f11 and the follow-up run prints D-19 MATCH on the v2 face "
    "(HQ-FEEDBACK F-20261025-03). "
    "PIT: the mid-round decisions advance is exactly the 'ghost sha' scenario D-08 targets — a "
    "round that scans decisions only at open would have missed it; the S7 double-scan caught it. "
    "| watermark verdict: GREEN (v2 quartet MATCH) "
    "| local-not-on-origin commits=0 (post-push self-proof) | dept:工程/研究"
)
t = io.open(P, encoding='utf-8').read()
assert 'r1240-addendum' not in t, 'addendum already present'
if not t.endswith('\n'):
    t += '\n'
io.open(P, 'w', encoding='utf-8', newline='\n').write(t + line + '\n')
print('appended', len(line))