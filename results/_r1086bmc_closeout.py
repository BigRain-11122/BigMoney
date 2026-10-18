# -*- coding: utf-8 -*-
# r1086 bm-c closeout writer: state round_no advance + heartbeat + round-report row.
import io
import json
import time
import datetime
import os

now = datetime.datetime.now()
iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

DID = ("r1086: 58th-gen absorb + W266 FULL CYCLE COMPLETE + W267 SEAT: dead 09:25-09:50 window estate "
       "(W266 five-face splice + engine self-burn 12/12, killed by the v1 25-min wall clock per "
       "O-20261018-0948 root-cure diagnosis) hash-verified then landed dc71ecc3f9 + iteration_loop v2 "
       "root-cure pulled same window; sixgate PRE-FINALIZE 29th consecutive ALL PASS with single-token "
       "post-splice heal (H1 _set_wave(265)->(266) W266 section -- r1076-family 3rd recurrence; minimality "
       "proof landed-blob+heal==healed-worktree CR-normalized; prereheal FAIL evidence preserved) 839bf365f; "
       "finalize one-pass ledger 1,007,335+2,200=1,009,535 EXACT / K 580,920+2,200=583,120 EXACT "
       "(n1_w266_results.json, w266 mu -0.0988/sigma 0.2536, K-lift +0.0001); fivekeys 6/6 ALL PASS "
       "(key3 A p95 0.3149->0.3268 in-band / key4 K-lift +0.0001 / key5 se_mu held-flat 0.000321); "
       "sec.7/8 backfilled placeholders=0; W267 SEAT published 942ebd5885 (probe live ADMIT A "
       "602_701..604_700 SIXTEENTH consecutive A-hop / B 604_701..604_900 SEVENTEENTH above-own-A, "
       "seed_admit FREE x2, origin vacancy four-check)")

NEXT = ("r1087: (1) W267 PREREG DERIVE = FIRST ACTION per seat MSG-20261018-1025-bmc-w267-seat.md "
        "(bands A 602_701..604_700 / B 604_701..604_900; post-W266 universe; frozen tpl = W266 prereg "
        "595433d63c pre-backfill face per r1052/r1049 law); then splice -> burn -> sixgate (30th target) "
        "-> finalize -> fivekeys -> sec.7/8 -> W268 seat; (2) O-20261018-0948-bm-a receipt duties (P0, "
        "SLA <=2 rounds): adoption-verify = NEXT firing spawning line must show 'hard-cap 240min, "
        "silence-kill 25min' (v2 on disk since this window's rebase) + local TIMEOUT census (grep "
        "logs/iteration-loop/run_*.log ROUND TIMEOUT; count + most-recent) + MiniGame-family same-pattern "
        "audit (EngineTick/ComfyDraftTick/AuditTick/GateTick/RadarTick/RadarDeepTick/SiliconWatchTick "
        "runners: grep WaitForExit / $RoundTimeoutMinutes / '= 25'; found=same v2 recipe in-place fix; "
        "none=zero-adaptation note) -> fleet/inbox/MSG-20261018-<HHMM>-bmc-rootfix.md + order-file "
        "receipt-section append; (3) d19 ORD/DEC watermark advance owed (state still holds ord 8f6162d9 "
        "/ dec 0ad85a30; rows since = O-20261018-0948 root-cure row + memory-gov row, committee/bm-a-"
        "executed, zero bm-c action beyond receipt duties); (4) S6 chain + smoke 49/49 deferred to r1087 "
        "honest (absorb-window product priority); (5) Monday 10-20 15:30 bars window: full papers chain "
        "(weekend 10-18/19 no bars, cutoff 10-16, papers debt=0)")

VERDICT = ("green: r1086 = 58th-gen absorb continuation window (counter 1086 at open per state, executed "
           "r1086, advanced 1086->1087 so next=r1087); product = W266 FULL CYCLE (splice absorbed+landed / "
           "burn 12/12 / sixgate 29th PRE-FINALIZE + single-token heal / finalize EXACT / fivekeys 6/6 / "
           "sec.7-8 backfill) + W267 seat published; engine daemon alive; v2 root-cure on disk "
           "(O-20261018-0948); CEO gaming yield standing (loop CPU-only, GPU gen-only); short-video lane "
           "DISABLED standing per O-20261017-1741")

# --- state ---
sp = 'state-bm-c.json'
st = json.load(io.open(sp, encoding='utf-8'))
st['round_no'] = 1087
st['round_no_label'] = 'r1086 closeout -> counter 1087'
st['last_round'] = 'r1086'
st['last_round_at'] = iso
st['last_seen'] = iso
st['ts'] = iso
st['updated'] = iso
st['clock_read'] = iso
st['current_task'] = 'r1086 closeout: W266 CYCLE COMPLETE + W267 seat published; next = W267 prereg derive r1087 FIRST ACTION'
st['current_task_at'] = iso
st['did'] = DID
st['last_round_summary'] = DID
st['next_pointer'] = NEXT
st['next'] = NEXT
st['verdict'] = VERDICT
st['latest_artifact'] = ("results/perpetual_faces/n1_w266_results.json (ledger 1,009,535 / K 583,120) + "
                        "results/_w267bmc_20261018_probe_receipt.json (W267 seat ADMIT) + "
                        "research/PERPETUAL_N1_W266_PREREG.md sec.7/8 backfilled (origin 942ebd5885)")
st['last_artifact'] = st['latest_artifact']
st['next_milestone'] = ("W267 prereg derive + freeze (r1087, within 48h); O-20261018-0948 receipt (r1087, "
                       "SLA 2 rounds); Monday 10-20 15:30 bars papers chain")
st['r1086_closeout_note'] = DID + " | counter 1086->1087 | deferrals honest: d19 watermark advance + S6 chain + smoke + 0948-receipt census/audit -> r1087"
io.open(sp, 'w', encoding='utf-8', newline='\n').write(json.dumps(st, indent=1, ensure_ascii=False))

# --- heartbeat ---
hp = 'fleet/machines/bm-c.json'
h = json.load(io.open(hp, encoding='utf-8'))
h['last_seen'] = iso
h['ts'] = iso
h['clock_read'] = iso
h['heartbeat_epoch_utc'] = epoch
h['current_task'] = 'r1086 closeout: W266 cycle complete + W267 seat; next = W267 prereg derive FIRST ACTION'
h['did'] = 'r1086: W266 CYCLE COMPLETE (sixgate 29th + H1 heal + finalize 1,009,535/K 583,120 EXACT + fivekeys 6/6 + sec78) + W267 seat ADMIT + v2 root-cure pulled'
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['verdict'] = 'green r1086 product window (W266 full cycle + W267 seat; 58th-gen absorb)'
io.open(hp, 'w', encoding='utf-8', newline='\n').write(json.dumps(h, indent=1, ensure_ascii=False))
assert isinstance(json.load(io.open(hp, encoding='utf-8'))['heartbeat_epoch_utc'], int), 'epoch must be int'

# --- round report row (canonical path per r750 law) ---
cands = ['logs/iteration-loop/round_reports-bm-c.md', 'round_reports-bm-c.md']
rp = next((c for c in cands if os.path.exists(c)), None)
assert rp, 'round report file not found in candidate paths'
raw = io.open(rp, encoding='utf-8', newline='').read()
eol = '\r\n' if '\r\n' in raw[:3000] else '\n'
row = (iso + " | r1086 | 58th-gen absorb + W266 FULL CYCLE (splice estate landed dc71ecc3f9 / sixgate 29th "
       "PRE-FINALIZE ALL PASS + single-token H1 heal / finalize 1,009,535 + K 583,120 EXACT / fivekeys 6/6 / "
       "sec.7-8 placeholders=0) + W267 SEAT (A 602_701..604_700 16th A-hop / B 604_701..604_900 17th "
       "above-own-A) + iteration_loop v2 root-cure pulled | evidence: n1_w266_results.json + "
       "_r1086bmc_w266_sixgate.json + _r1086bmc_w266_selftest_heal.json + _w267bmc_20261018_probe_receipt.json "
       "(origin 942ebd5885, all pushed 0/0) | next: W267 prereg derive FIRST ACTION + O-20261018-0948 receipt "
       "(adoption-verify/TIMEOUT census/MiniGame audit) + d19 watermarks + S6/smoke deferred-to-r1087")
with io.open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write(eol + row.strip())
print('CLOSEOUT-WRITTEN: state 1086->1087 | heartbeat epoch-int ok | report row ->', rp)
