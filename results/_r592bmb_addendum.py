# -*- coding: utf-8 -*-
# r592 addendum line: integration window disclosure (bytes-level append, CRLF preserving)
import datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

now = datetime.datetime.now().astimezone()
line = (
    "2026-10-02T" + now.strftime('%H:%M') + "+08:00 | r592 addendum | "
    "push window origin advanced x4 mid-round (bm-a r591 de7a9e482 W112 finalize + 12 shard products, ledger head 610,948 K=244,320, "
    "chain W1..W112 fully closed; bm-a r591 seat-archive 1c6a4cd81; bm-c engine append 76401aee7 W113 shards, burn 9/12 in-flight; "
    "bm-a r592 2cd67216a W114 seat published): first push claw-intercepted as r374 diverged-base deletion-set artifact "
    "(bm-a's n1_w112 shard products misjudged as my deletions from stale base) -> integrated per r589 reset-FF-reland loop: "
    "reset --mixed HEAD~1 + 4 AA host-faces restored to origin per r366 origin-canonical law (dashboard_status.js/json + "
    "scorecard_v1.json + strategy_scorecard.json, all bm-a-hosted single-writer faces; my 20:10 versions were legal "
    "stale-takeover derives at the 32min-stale window but host revived and pushed = origin canonical, idempotent L1 zero "
    "scientific loss, my .bm-b.json per-machine faces carry the S6 evidence) + merge --ff-only origin/main + repush; "
    "W114 seat MSG-20261002-2014-bma read + cross-verified (A 271_004..273_003 / B 62_201..62_400 hops 0/0 == the W114+ "
    "projection bm-c disclosed in the W113 seat = dual-window derive identity; W115+ projection A 273_004..275_003 CLEAN / "
    "B first-clean 62_601..62_800 hops=1 per D-20261002-05 noted for the next freezer -- machine-derive never transcribe); "
    "first r592 commit 5d6e6da5c orphaned-never-visible (push rejected at claw), this repush commit = only published face"
)

p = r'logs\iteration-loop\round_reports.md'
raw = open(p, 'rb').read()
crlf = b'\r\n' in raw[:2000]
sep = b'\r\n' if crlf else b'\n'
if not raw.endswith(b'\n'):
    raw += sep
raw += line.encode('utf-8') + sep
open(p, 'wb').write(raw)
print('addendum appended, crlf=', crlf, 'len=', len(line))
