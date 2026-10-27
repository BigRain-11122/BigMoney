import datetime as dt
import io
import json
import os
import time

NOW = dt.datetime.now().astimezone()
ISO = NOW.isoformat(timespec='seconds')
TS = NOW.strftime('%Y-%m-%d %H:%M')

# ---- state-bm-c.json -------------------------------------------------------
st = json.load(io.open('state-bm-c.json', encoding='utf-8'))
st['round_no'] = 1314
st['last_decisions_sha'] = '6154bf1c683479c074cd2bce809a03e17cd7e38b4258ddf7798214d0452398b2'
st['current_task'] = 'r1314 closeout: card/ledger agreement face + machine-health gate on the S6 chain'
st['current_task_ts'] = ISO
st['clock_read'] = ISO
st['activity_now'] = ('r1314: the card and the forward ledger are one frozen decision recorded twice; '
                      'they now agree (12 names, weights 2.08e-6 apart) and the drift is priced (0.15pp, 0.11bp to undo)')
json.dump(st, io.open('state-bm-c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- heartbeat -------------------------------------------------------------
hb = json.load(io.open('fleet/machines/bm-c.json', encoding='utf-8-sig'))
hb['last_seen'] = TS
hb['ts'] = ISO
hb['clock_read'] = ISO
hb['heartbeat_epoch_utc'] = int(time.time())
hb['current_task'] = st['current_task']
hb['current_task_at'] = ISO
hb['current'] = st['current_task']
hb['activity_now'] = st['activity_now']
hb['did'] = ('inherited the 01:08 window\'s estate and finished it: etf_book_card_track (card vs forward '
             'ledger agreement + drift priced) and machine_health_face gate both on the S6 chain')
hb['did_round'] = 'r1314'
hb['verdict'] = 'green'
hb['busy'] = False
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['behind_origin'] = 0
hb['delivered_head'] = os.popen('git rev-parse HEAD').read().strip()[:10]
json.dump(hb, io.open('fleet/machines/bm-c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- round report row -----------------------------------------------------
ROW = (
    "| %s | 1314 (inherited) | CLOSEOUT + PRODUCT for a dead window: the 01:08 session wrote both faces and "
    "died before commit, so this window read the tree instead of trusting the digest. "
    "① etf_book_card_track (script selftest 19/19, new S6 leg, 2 new smoke legs): the production card and the "
    "forward ledger are two independent records of ONE frozen decision and nothing compared them. It asserts "
    "the paper book owns the book the card sells -- 12 names, same order, max weight diff 2.08e-6, scale "
    "0.7008 vs 0.7008, cash 0.2992 vs 0.2992, same decision bar 2026-10-14 -- re-derives the ledger nav from "
    "those same weights (max dev 1e-10, so a trade the book never published would show) and prices the drift "
    "the frozen decision has carried: worst name 159632 at 0.1451pp, 0.11bp to undo at the next decision, 11 "
    "bars away. Reading: the book is exactly what it advertises and does not need an off-cycle rebalance. "
    "② machine_health_face: D-20261028-02 found fleet/machine-health.json holding a nested "
    "{value:[{value:[...]}]} payload that made the panel fail SOFT (fewer machines instead of UNKNOWN). bm-b "
    "landed the reader + writer contract in the same night; this window healed the live face from heartbeats "
    "(3 machine rows, was 1) and, because a decision that lives only in a receipt is not a gate (r1266), put "
    "the module's fail-closed check on the S6 chain so the face is judged every round instead of only when a "
    "session remembers to run smoke. Duplicate landed by both machines in one night: scripts/machine_health_face.py "
    "(this window) was dropped in favour of bm-b's Tools/machine_health_face.py -- one reader, not two. "
    "ABSORB: origin advanced 5 commits mid-round + 1 more during the rebase; conflicts across 15 faces resolved "
    "as upstream for monitor/build_status.py and the day's post_review report, union for the methodology ledger "
    "and post_review.jsonl, this window's freshly regenerated blobs for bm-c's own derived faces. The rebase "
    "refused to continue with a clean index (r1032/r1048 class) -> quit + commit the resolved tree, main fast-"
    "forwarded onto it. | card_track selftest 19/19; new chain legs 2/2 rc0 (card_track 55.3s, machine_health "
    "0.1s); smoke 107/108 then 1 FAIL = stale panel payload, rebuilt -> see final; panel face=ok 3 machines; "
    "dualrun DRIFT entries[644].done_at (observation phase, streak reset, 647/647); attrition CLEAN; watermark "
    "insufficient_history (first sample of the window) with 2 pool-ready cands and a local astock batch running; "
    "orphan face=0 (py_faces=6); D-19 decisions 6154bf1c changed -> 4 new lines consumed, 2 of them this firm's "
    "(D-20261028-02 dispatched to BigMoney 10-28 12:00 = this round's work; D-20261028-04 group-root resolution "
    "self-check by 10-31 00:00 still owed); local commits behind origin N=0 | next: D-20261028-04 asks this firm "
    "to sweep every resident script that resolves the group root by '..\\..' instead of rev-parse --the lead "
    "candidate is the oversight writer deployment face that just re-broke the face once |\n"
) % ISO
with io.open('round_reports-bm-c.md', 'a', encoding='utf-8', newline='') as fh:
    fh.write(ROW)
print('state/heartbeat/report written; head=%s' % hb['delivered_head'])