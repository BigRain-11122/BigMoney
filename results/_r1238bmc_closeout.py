# -*- coding: utf-8 -*-
"""r1238 bm-c: closeout — round report line, state round_no advance, heartbeat.

Absorb note: the r1237 window froze (ee00f6a9d6) + spliced (91e318867f) + let the engine
self-burn 12/12, then died pre-closeout with state frozen at round_no 1236. This window
executed as r1238 (next after the highest committed label r1237) and closes the W328 cycle.
Idempotent guards: refuses to append the same round line twice; state round_no is only
advanced if it is still at the pre-round value (1236).
"""
import io
import json
import time
from datetime import datetime

NOW = datetime.now().astimezone()
TS = NOW.isoformat(timespec='seconds')

ROUND = 1238
REPORT = 'round_reports-bm-c.md'
STATE = 'state-bm-c.json'
HB = 'fleet/machines/bm-c.json'

line = (
    f"{TS} | r{ROUND} | W328 CYCLE CLOSED (ledger 1,143,741 + 2,200 = 1,145,941 EXACT / "
    "merged K 717,320 + 2,200 = 719,520 EXACT) + W329 SEAT ADMIT -- dead-window absorb, zero "
    "reburn. "
    "(0) ABSORB: the r1237 window landed the W328 freeze (ee00f6a9d6) and the five-face splice "
    "(91e318867f), the engine self-ignited 12/12 shards (09:32..09:45, min 109,422B), then died "
    "before any closeout (state round_no 1236, heartbeat 09:14). Estate machine-verified before "
    "landing per the bm-c absorb lineage; executed as r1238, counter advanced 1236->1238 so "
    "next=r1239. Zero double-count: S0.5 D-19 both faces unchanged, orders unacked=0. "
    "(1) adjudication PASS: replay reproduces pre AND post freeze faces on the receipt's declared "
    "LF basis, replay_lf_eq_landed true, 0 heal deltas, 0 unexplained deltas. "
    "(2) six-gate 92nd consecutive ALL PASS: row faces 7/7, E94 row-law face 4/4 (W327 clauses "
    "absent in the W328 row; FIRST CLEAN WINDOW + EMPTY seed-hop clauses present), materializer "
    "asserts 4/4 exact, W327 boundary kept, setwave birth-station 1/1 + absence gates, 12/12 "
    "shards >100KB, banned ADMIT rc0, pf 9/9 + n1 selftest rc0, worktree==landed with EMPTY diff "
    "(no heal this window). "
    "(3) finalize one-pass EXACT: w328-only mu -0.08770218 / sigma 0.24034611 vs merged mu "
    "-0.09285874 / sigma 0.24520372 / se_mu@719,520 0.000289; A p95 0.3100 p99 0.4404; K-lift "
    "-0.0001 at held n_eff 1,143,741 (W327's ledger, machine-read). "
    "(4) fivekeys 6/6 PASS with ZERO prose deviations -- the sec.5 n_eff_held literal 1,143,741 "
    "reproduces the machine face this time, so the E96 double condition (present AND numerically "
    "equal) passes cleanly; the r1236 defect class did not recur. "
    "(5) W329 SEAT ADMIT (seat-first, published before any freeze): A 742,701..744,700 (82nd "
    "consecutive A-hop, hops=1 -- naive 742,501..744,500 refused at start by the registered W328 "
    "B band 742,501..742,700 plus seed point 742,501) / B 744,701..744,900 (83rd above-own-A, "
    "hops=1, FIRST INSIDE face: naive 742,701..742,900 lies wholly inside own-A -> cascade to "
    "own-A tail+1, EMPTY seed-hop); universe owner_rows=318 (bm-a 130 / bm-b 41 / bm-c 147) "
    "ordinal 319, owner_row_holes [15]; seed_admit FREE x2; leg3 bands_clear true; projection "
    "W330 A 744,701..746,700 hops=0 / B 744,901..745,100 hops=0 (inside own-A naive). "
    "S0 HEAD==origin on open (0 ahead / 0 behind), dirty set = own S6 products from the dead "
    "window + own memory append, all committed here; round-zero orphan probe py_faces=5 orphans=0 "
    "resident_servers=2 killed=[]; S1 smoke 57/57 PASS; S3 sat engine rc0 (W328 12/12 done, "
    "burns_active=[] queue_next=[]); S6 39/39 rc0; S7 attrition 4 ledger files CLEAN (3 "
    "historical shrinks healed); scheduled tasks NOT re-registered per the 2026-10-17 CEO cleanup "
    "order; D-19 dual scan MATCH (dec 0bf59c3c92a370cc / ord 8ff7de47df154ffa), fleet/orders 109 "
    "files / 234 acks / unacked=0. "
    "POOL TAKEOVER (D-20261024-15): the 12:00 deadline has NOT passed at this window's close "
    "(10:1x) -- standing escalation unchanged (first window at/after 12:00 with bm-b still "
    "silent claims E93 before any other work). "
    "PRODUCT the CEO can see: results/perpetual_faces/n1_w328_results.json (cumulative null pool "
    "K=719,520, ledger 1,145,941), results/_r1238bmc_w328_sixgate.json (92nd ALL PASS), "
    "results/_r1238bmc_w328_fivekeys.json (6/6), results/_n1_face_adjudication_w328.json, "
    "fleet/inbox/MSG-20261025-1005-bmc-w329-seat.md, research/PERPETUAL_N1_W328_PREREG.md sec.7/8 "
    "backfilled (0 placeholders, 83 lines preserved). "
    "PIT: (1) the seat probe refuses to run before the wave's OWN finalize product exists "
    "(n1_w{N-1}_results.json assert) -- closure order is six-gate -> finalize -> fivekeys -> seat "
    "-> sec.7/8 backfill; (2) the B placement face flipped from three consecutive BELOW waves to "
    "INSIDE this wave: B_naive_inside_own_A / B_naive_below_own_A / B_seed_hop_disclosure must be "
    "read together or the cascade looks unexplained; (3) detached finalize again needed "
    "DETACHED_PROCESS|CREATE_NO_WINDOW + python -u with an empty log for ~4 minutes (pid live, CPU "
    "climbing) -- restarting would double-burn the ledger. "
    f"next=r{ROUND + 1} W329 freeze (canon-clone of the W328 post-run face) + five-face splice + "
    "engine self-ignite 12/12. "
    "| CEO face: 当前活=W328 已闭环（账本 1,145,941 / 合并池 K 719,520）+ W329 席位已发；"
    "最近实物=results/perpetual_faces/n1_w328_results.json（2026-10-25 10:00）+ "
    "fleet/inbox/MSG-20261025-1005-bmc-w329-seat.md；下个里程碑=W329 冻结+splice+12/12 烧录（≤48h） "
    "| watermark verdict: GREEN (red=false; lane healthy, engine idle with queue drained) "
    "| local-not-on-origin commits=0 (post-push self-proof) | registry sweep zero-hit "
    "| dept:研究/工程"
)

# ---- round report ----
text = io.open(REPORT, encoding='utf-8').read()
assert f"| r{ROUND} |" not in text, 'round line already present'
if not text.endswith('\n'):
    text += '\n'
io.open(REPORT, 'w', encoding='utf-8', newline='\n').write(text + line + '\n')

# ---- state ----
st = json.load(io.open(STATE, encoding='utf-8'))
assert st.get('round_no') == 1236, ('unexpected state round_no', st.get('round_no'))
st['round_no'] = ROUND
st['round'] = ROUND
st['ts'] = TS
st['updated'] = TS
st['updated_at'] = TS
st['clock_read'] = TS
st['status'] = 'green'
st['verdict'] = 'GREEN'
st['activity_now'] = (
    "W328 CYCLE CLOSED (ledger 1,145,941 / merged K 719,520); W329 seat ADMIT A 742_701..744_700 / "
    "B 744_701..744_900; next = W329 freeze")
st['verify'] = (
    "W328 finalize one-pass 1,143,741+2,200=1,145,941 EXACT / K 717,320+2,200=719,520 EXACT | "
    "adjudication PASS (0 heal / 0 unexplained) | six-gate 92nd ALL PASS (empty landed diff) | "
    "fivekeys 6/6 zero deviations | prereg sec.7/8 backfilled 0 placeholders 83 lines held | "
    "W329 seat ADMIT | smoke 57/57 | attrition CLEAN | orphan 0 | S6 39/39 rc0")
st['sync'] = {'origin_tip': None, 'ts': TS}
st['last_decisions_sha'] = '0bf59c3c92a370cc@5a8c28d/215741'
st['last_orders_sha'] = '8ff7de47df154ffa@5a8c28d/370071'
st['last_decisions_read_note'] = 'r1238 dual-delta (open+close): DEC content face unchanged (0bf59c3c92 hold), zero action'
st['last_orders_read_note'] = 'r1238 dual-delta (open+close): ORD content face unchanged (8ff7de47 hold), unacked=0'
st['r1238_closeout_note'] = (
    "r1238: dead-window absorb. The r1237 window committed the W328 freeze (ee00f6a9d6) and the "
    "five-face splice (91e318867f), the saturation engine self-burned 12/12 shards (09:32..09:45, "
    "min 109,422B, state wave_shards_done['328']=12), then the window died before closeout (state "
    "round_no stayed 1236, heartbeat 09:14). This window machine-verified the estate (freeze "
    "receipt, splice on disk == landed blob byte-exactly, 12 shards present, engine state) and "
    "executed the closure WITHOUT re-splicing or re-burning: (1) freeze-face adjudication PASS "
    "(replay reproduces pre+post faces on the declared LF basis, LF replay == landed, 0 heal, 0 "
    "unexplained); (2) six-gate 92nd consecutive ALL PASS (results/_r1238bmc_w328_sixgate.json) "
    "with row faces 7/7, E94 row-law 4/4, materializer asserts 4/4, W327 boundary kept, setwave "
    "birth station 1/1 + absence gates, 12/12 shards >100KB, banned ADMIT rc0, pf 9/9 + n1 "
    "selftest rc0 and EMPTY landed diff for both face files (no heal this window); (3) finalize "
    "one-pass EXACT ledger 1,143,741+2,200=1,145,941 / merged K 717,320+2,200=719,520, w328-only mu "
    "-0.08770218 sigma 0.24034611, merged mu -0.09285874 sigma 0.24520372, se_mu@719,520 0.000289, "
    "A p95 0.3100 p99 0.4404, K-lift -0.0001 at held n_eff 1,143,741; (4) fivekeys 6/6 with ZERO "
    "prose deviations -- the frozen n_eff_held literal 1,143,741 equals the machine face this "
    "wave, so the E96 present-AND-equal double condition passes cleanly (r1236's defect class did "
    "not recur); (5) sec.7/sec.8 backfilled from machine faces, zero placeholders, 83-line "
    "structure card held (sec.7=9 / sec.8=14); (6) W329 SEAT ADMIT seat-first: A 742,701..744,700 "
    "(82nd consecutive A-hop, hops=1, naive 742,501..744,500 refused by the registered W328 B band "
    "742,501..742,700 plus seed point 742,501) / B 744,701..744,900 (83rd above-own-A, hops=1, "
    "FIRST INSIDE face -- naive 742,701..742,900 wholly inside own-A -> own-A reservation cascade "
    "to own-A tail+1 EXACT, EMPTY seed-hop); owner_rows=318 (bm-a 130 / bm-b 41 / bm-c 147), "
    "ordinal 319, owner_row_holes [15], seed_admit FREE x2, bands_clear true; W330 projection A "
    "744_701..746_700 hops=0 / B 744_901..745_100 hops=0 (lands inside own-A naive, so the W330 "
    "freezer must re-derive live and reserve its own A window). S6 39/39 rc0 this window "
    "(results/_r1238bmc_s6_chain.json; dualrun zero-drift streak 51, compute_audit cpu 64% / py "
    "0.1%, py_watermark cpu 70%, clock ORANGE_HOT cell, scorecard 6/28/7, REPORT-2026-10-25, "
    "LIVE-2026-10-25). PIT recorded this window: the seat probe asserts the wave's own finalize "
    "product exists, so closure order is fixed six-gate -> finalize -> fivekeys -> seat -> "
    "backfill; and the B placement face flipped BELOW->INSIDE, so the three placement faces must "
    "be read together. current=W328 CLOSED, chain head free; next=r1239 W329 freeze (canon-clone of "
    "the W328 post-run face) + five-face splice + engine self-ignite 12/12")
json.dump(st, io.open(STATE, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)

# ---- heartbeat ----
hb = json.load(io.open(HB, encoding='utf-8'))
epoch = int(time.time())
hb.update({
    'last_seen': TS,
    'ts': TS,
    'clock_read': TS,
    'heartbeat_epoch_utc': epoch,
    'status': 'green',
    'verdict': 'GREEN',
    'current_task': ('W328 cycle closed (ledger 1,145,941 / K 719,520); W329 seat ADMIT; '
                     'next = W329 freeze'),
    'cpu_cores': 32,
    'idle_rounds': 0,
    'agenda_starved': False,
    'round_no': ROUND,
    'recent_artifact': 'results/perpetual_faces/n1_w328_results.json',
})
json.dump(hb, io.open(HB, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
check = json.load(io.open(HB, encoding='utf-8'))
assert isinstance(check['heartbeat_epoch_utc'], int), type(check['heartbeat_epoch_utc'])
print(json.dumps({'round_no': st['round_no'], 'epoch': epoch, 'ts': TS,
                  'report_line_chars': len(line)}, indent=1))