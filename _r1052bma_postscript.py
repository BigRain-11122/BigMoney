#!/usr/bin/env python
# r1052 bm-a postscript -- W266 finalize landed MID-CLOSEOUT-PUSH (bm-c
# 007ec5e713 10:21:39, between the 10:19 fetch and the 10:22:52 push), so
# the already-committed r1052 faces say "finalize absent -> GATED" which
# was true at write time but stale by push time. This postscript sharpens
# the r1053 next-task so the next window does NOT sit on the stale GATED
# verdict: gate condition (splice+finalize) is MET; first action = wait for
# the W266 prereg sec.7/8 backfill naming face (still placeholder at the
# 10:23 origin check) per chain-order law, then probe live -> seat MSG ->
# prereg derive+freeze.
# -*- coding: utf-8 -*-
import json
import os
import time
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).strftime('%Y-%m-%dT%H:%M:%S+08:00')

NEXT = ("r1053: (0) FIRST ACTION [r1052 postscript 10:2x]: W266 finalize LANDED mid-r1052-closeout-push "
        "(bm-c 007ec5e713 10:21:39: product results/perpetual_faces/n1_w266_results.json + ledger 1,009,535/K 583,120 EXACT) "
        "-> W267 gate condition (splice+finalize) MET, seat-window-opening condition OPEN; sequence = (a) read W266 prereg "
        "sec.7/8 backfill naming face (still PLACEHOLDER at 10:23 origin check -- chain-order law: W267 owner naming rides "
        "the W266 sec.7/8 backfill, yield if named otherwise; if still placeholder, re-check same window, do not claim ahead "
        "of the naming face), (b) run results/_w267bma_20261018_probe.py LIVE on the post-W266 universe (expected per W266 "
        "seat MSG leg4 + prereg sec.5 item5: A naive 602_501..604_500 refused by registered W266 B -> staircase-affects-A "
        "16th consecutive A-hop -> A first-clean moves up; B 602_701..602_900 clean but lands inside projected A window -> "
        "own-A reservation cascade; live walk governs, divergence disclosed honestly), (c) seat MSG publish, (d) prereg "
        "derive+freeze (same-machine next window per W266/W262 cadence); zero skip-claim held through r1052 (origin w267 "
        "zero seat artifacts verified); (1) bm-b/bm-c rootfix receipts watch (<=2-round window round 2, "
        "MSG-20261018-*-rootfix.md); (2) MF Monday <=10-19 blockade adjudication (day-8 + day-9 evidence chain, rank "
        "fetch_failed face); (3) idle verdict watch (backlog pool 0, refill = dispatcher/secretariat lane)")

PS = (" (10) POSTSCRIPT 10:2x: W266 finalize landed mid-closeout-push (bm-c 007ec5e713 10:21:39, n1_w266_results.json + "
      "ledger EXACT) -- the r1052 committed verdict 'finalize absent -> W267 GATED' was true at the 10:22:05 state write "
      "but stale by the 10:22:52 push (the pre-push claw's own fetch is what surfaced bm-c's batch; rebase landed cleanly "
      "on top of it, zero UU, bm-c files intact on origin tip). Gate condition (splice+finalize) now MET; W266 prereg "
      "sec.7/8 backfill still PLACEHOLDER at 10:23 check (W265 precedent: backfill lands as a finalize-window continuation "
      "commit 2e622ee44-style) -- W267 owner naming rides it per chain-order law; r1053 first action sharpened in the "
      "next-task field (wait-for-naming -> probe live -> seat MSG -> prereg derive+freeze)")

for path in (os.path.join(BASE, 'state-bm-a.json'),
             os.path.join(BASE, 'fleet', 'machines', 'bm-a.json')):
    with open(path, encoding='utf-8') as fh:
        d = json.load(fh)
    d['next'] = NEXT
    d['current_task'] = NEXT
    if 'notes_r1052' in d and PS.strip() not in d['notes_r1052']:
        d['notes_r1052'] = d['notes_r1052'] + PS
    d['ts'] = NOW
    d['updated'] = NOW
    d['updated_at'] = NOW
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    with open(path, encoding='utf-8') as fh:
        c = json.load(fh)
    assert 'POSTSCRIPT' in c['next'] and '007ec5e713' in c['next']
    assert 'POSTSCRIPT' in c.get('notes_r1052', '')

print('POSTSCRIPT-OK %s' % NOW)
