# -*- coding: utf-8 -*-
"""r1240 bm-c: closeout — round report line, state round_no advance, heartbeat, 5x checkpoint.

Absorb note: the r1239 window froze the W329 prereg (c337566e2b) + five-face spliced
(624c3d99a9) + let the engine self-burn 12/12 (10:26..10:39), then died pre-closeout with
state frozen at round_no 1238. This window executed as r1240 and closes the W329 cycle.
Idempotent guards: refuses to append the same round line twice; state round_no is only
advanced if it is still at the pre-round value (1238).
"""
import io
import json
import time
from datetime import datetime

NOW = datetime.now().astimezone()
TS = NOW.isoformat(timespec='seconds')

ROUND = 1240
REPORT = 'round_reports-bm-c.md'
STATE = 'state-bm-c.json'
HB = 'fleet/machines/bm-c.json'
HANDOVER = 'research/HANDOVER.md'

line = (
    f"{TS} | r{ROUND} | W329 CYCLE CLOSED (ledger 1,145,941 + 2,200 = 1,148,141 EXACT / "
    "merged K 719,520 + 2,200 = 721,720 EXACT) + W330 SEAT ADMIT -- dead-window absorb, zero "
    "reburn. "
    "(0) ABSORB: the r1239 window landed the W329 prereg (c337566e2b) and the five-face splice "
    "(624c3d99a9), the engine self-burned 12/12 shards (10:26..10:39, min 109,471B), then died "
    "before any closeout (state round_no 1238, heartbeat 10:10). Estate machine-verified before "
    "landing per the bm-c absorb lineage; executed as r1240, counter advanced 1238->1240 so "
    "next=r1241. Zero double-count: S0.5 D-19 both faces unchanged (dec 0bf59c3c92 / ord "
    "8ff7de47), orders unacked=0. "
    "(1) adjudication PASS: replay reproduces pre AND post freeze faces on the receipt's declared "
    "LF basis, replay_lf_eq_landed true, 0 heal deltas, 0 unexplained deltas -- after fixing the "
    "invocation: the tool builds `git show <splice>:<path>` from the RAW argument, so Windows "
    "backslash paths fail with 'exists on disk, but not in <sha>'; forward-slash paths fix it. "
    "(2) six-gate 93rd consecutive ALL PASS: row faces 7/7, E94 row-law face 4/4 (W328 clauses "
    "absent in the W329 row; FIRST CLEAN WINDOW + EMPTY seed-hop clauses present), materializer "
    "asserts 4/4 exact, W328 boundary kept, setwave birth-station 1/1 + absence gates, 12/12 "
    "shards >100KB, banned ADMIT rc0, pf 9/9 + n1 selftest rc0, worktree==landed with EMPTY diff "
    "(no heal this window). "
    "(3) finalize one-pass EXACT: w329-only mu -0.09100177 / sigma 0.24087907 vs merged mu "
    "-0.09285308 / sigma 0.24519051 / se_mu@721,720 0.000289; A p95 0.3051 p99 0.4550; K-lift "
    "-0.0001 at held n_eff 1,145,941 (W328's ledger, machine-read). "
    "(4) fivekeys 6/6 PASS with ZERO prose deviations. "
    "(5) W330 SEAT ADMIT (seat-first, published before any freeze): A 744,901..746,900 (83rd "
    "consecutive A-hop, hops=1 -- naive 744,701..746,700 refused at start by the registered W329 "
    "B band 744,701..744,900 plus seed point 744,701) / B 746,901..747,100 (84th above-own-A, "
    "hops=1, SECOND consecutive INSIDE face: naive 744,901..745,100 lies wholly inside own-A -> "
    "cascade to own-A tail+1, EMPTY seed-hop); universe owner_rows=319 (bm-a 130 / bm-b 41 / bm-c "
    "148) ordinal 320, owner_row_holes [15]; seed_admit FREE x2; leg3 bands_clear true; "
    "projection W331 A 746,901..748,900 hops=0 / B 747,101..747,300 hops=0 (inside own-A naive). "
    "S0 HEAD==origin on open, dirty set = own S6 products + own scripts, all committed here; "
    "round-zero orphan probe py_faces=5 orphans=0 resident_servers=2 killed=[]; S1 smoke 57/57 "
    "PASS; S6 39/39 rc0 (dualrun ZERO-DRIFT streak 51 / compute_audit cpu 20.0% py 6.9% / "
    "py_watermark sample at 27% / update_daily no-op 2026-10-23 cutoff / regime ORANGE breadth "
    "0.85 / clock ORANGE_HOT / scorecard 6/28/7 / REPORT-2026-10-25 / LIVE-2026-10-25 / token "
    "delta 0); S7 attrition 4 ledger files CLEAN (3 historical shrinks healed); scheduled tasks "
    "NOT re-registered per the 2026-10-17 CEO cleanup order; D-19 dual scan MATCH at open and "
    "close, fleet/orders 109 files / 234 acks / unacked=0. 5x checkpoint written to "
    "research/HANDOVER.md. "
    "POOL TAKEOVER (D-20261024-15): the 12:00 deadline has NOT passed at this window's close "
    "(11:1x) -- standing escalation unchanged (first window at/after 12:00 with bm-b still "
    "silent claims E93 before any other work). "
    "PRODUCT the CEO can see: results/perpetual_faces/n1_w329_results.json (cumulative null pool "
    "K=721,720, ledger 1,148,141), results/_r1240bmc_w329_sixgate.json (93rd ALL PASS), "
    "results/_r1240bmc_w329_fivekeys.json (6/6), results/_n1_face_adjudication_w329.json, "
    "fleet/inbox/MSG-20261025-1105-bmc-w330-seat.md, research/PERPETUAL_N1_W329_PREREG.md sec.7/8 "
    "backfilled (0 placeholders, 83 lines preserved). "
    "PIT: (1) the freeze-face adjudicator takes RAW path args into `git show <sha>:<path>` -- "
    "backslash paths silently miss the blob ('exists on disk, but not in <sha>'); pass "
    "forward-slash paths. (2) finalize again timed out the foreground tool at 5 silent minutes -> "
    "detached DETACHED_PROCESS|CREATE_NO_WINDOW + python -u + poll, never restart (restart = "
    "ledger double-burn). (3) INSIDE face is now two consecutive waves: read "
    "B_naive_inside_own_A / B_naive_below_own_A / B_seed_hop_disclosure together. "
    f"next=r{ROUND + 1} W330 freeze (canon-clone of the W329 post-run face) + five-face splice + "
    "engine self-ignite 12/12. "
    "| CEO face: 当前活=W329 已闭环（账本 1,148,141 / 合并池 K 721,720）+ W330 席位已发；"
    "最近实物=results/perpetual_faces/n1_w329_results.json（2026-10-25 11:02）+ "
    "fleet/inbox/MSG-20261025-1105-bmc-w330-seat.md；下个里程碑=W330 冻结+splice+12/12 烧录（≤48h） "
    "| watermark verdict: GREEN (red=false; lane healthy) "
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
assert st.get('round_no') == 1238, ('unexpected state round_no', st.get('round_no'))
st['round_no'] = ROUND
st['round'] = ROUND
st['ts'] = TS
st['updated'] = TS
st['updated_at'] = TS
st['clock_read'] = TS
st['status'] = 'green'
st['verdict'] = 'GREEN'
st['activity_now'] = (
    "W329 CYCLE CLOSED (ledger 1,148,141 / merged K 721,720); W330 seat ADMIT A 744_901..746_900 / "
    "B 746_901..747_100; next = W330 freeze")
st['verify'] = (
    "W329 finalize one-pass 1,145,941+2,200=1,148,141 EXACT / K 719,520+2,200=721,720 EXACT | "
    "adjudication PASS (0 heal / 0 unexplained) | six-gate 93rd ALL PASS (empty landed diff) | "
    "fivekeys 6/6 zero deviations | prereg sec.7/8 backfilled 0 placeholders 83 lines held | "
    "W330 seat ADMIT | smoke 57/57 | attrition CLEAN | orphan 0 | S6 39/39 rc0")
st['sync'] = {'origin_tip': None, 'ts': TS}
st['last_decisions_sha'] = '0bf59c3c92a370cc@5a8c28d/215741'
st['last_orders_sha'] = '8ff7de47df154ffa@5a8c28d/370071'
st['last_decisions_read_note'] = 'r1240 dual-delta (open+close): DEC content face unchanged (0bf59c3c hold), zero action'
st['last_orders_read_note'] = 'r1240 dual-delta (open+close): ORD content face unchanged (8ff7de47 hold), unacked=0'
st['r1240_closeout_note'] = (
    "r1240: dead-window absorb. The r1239 window committed the W329 prereg (c337566e2b) and the "
    "five-face splice (624c3d99a9), the saturation engine self-burned 12/12 shards (10:26..10:39, "
    "min 109,471B), then the window died before closeout (state round_no stayed 1238, heartbeat "
    "10:10). This window machine-verified the estate (freeze receipt, splice on disk == landed "
    "blob byte-exactly, 12 shards present) and executed the closure WITHOUT re-splicing or "
    "re-burning: (1) freeze-face adjudication PASS after passing forward-slash paths (the tool "
    "feeds raw args to `git show <sha>:<path>`, so backslash paths miss the blob); (2) six-gate "
    "93rd consecutive ALL PASS (results/_r1240bmc_w329_sixgate.json) with row faces 7/7, E94 "
    "row-law 4/4, materializer asserts 4/4 exact, W328 boundary kept, setwave birth station 1/1 + "
    "absence gates, 12/12 shards >100KB, banned ADMIT rc0, pf 9/9 + n1 selftest rc0 and EMPTY "
    "landed diff; (3) finalize one-pass EXACT ledger 1,145,941+2,200=1,148,141 / merged K "
    "719,520+2,200=721,720, w329-only mu -0.09100177 sigma 0.24087907, merged mu -0.09285308 "
    "sigma 0.24519051, se_mu@721,720 0.000289, A p95 0.3051 p99 0.4550, K-lift -0.0001 at held "
    "n_eff 1,145,941; (4) fivekeys 6/6 with ZERO prose deviations; (5) sec.7/sec.8 backfilled from "
    "machine faces, zero placeholders, 83-line structure card held (sec.7=9 / sec.8=14); (6) W330 "
    "SEAT ADMIT seat-first: A 744,901..746,900 (83rd consecutive A-hop, hops=1, naive "
    "744,701..746,700 refused by the registered W329 B band 744,701..744,900 plus seed point "
    "744,701) / B 746,901..747,100 (84th above-own-A, hops=1, SECOND consecutive INSIDE face -- "
    "naive 744,901..745,100 wholly inside own-A -> own-A reservation cascade to own-A tail+1 "
    "EXACT, EMPTY seed-hop); owner_rows=319 (bm-a 130 / bm-b 41 / bm-c 148), ordinal 320, "
    "owner_row_holes [15], seed_admit FREE x2, bands_clear true; W331 projection A "
    "746_901..748_900 hops=0 / B 747_101..747_300 hops=0 (lands inside own-A naive). S6 39/39 rc0 "
    "this window (results/_r1240bmc_s6_chain.json; dualrun zero-drift streak 51, compute_audit cpu "
    "20.0% / py 6.9%, clock ORANGE_HOT cell, scorecard 6/28/7, REPORT-2026-10-25, "
    "LIVE-2026-10-25). 5x checkpoint (ROUND % 5 == 0) appended to research/HANDOVER.md. current="
    "W329 CLOSED, chain head free; next=r1241 W330 freeze (canon-clone of the W329 post-run face) "
    "+ five-face splice + engine self-ignite 12/12")
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
    'current_task': ('W329 cycle closed (ledger 1,148,141 / K 721,720); W330 seat ADMIT; '
                     'next = W330 freeze'),
    'cpu_cores': 32,
    'idle_rounds': 0,
    'agenda_starved': False,
    'round_no': ROUND,
    'last_round': ROUND,
    'last_round_at': TS,
    'recent_artifact': 'results/perpetual_faces/n1_w329_results.json',
    'latest_artifact': 'results/perpetual_faces/n1_w329_results.json',
})
json.dump(hb, io.open(HB, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
check = json.load(io.open(HB, encoding='utf-8'))
assert isinstance(check['heartbeat_epoch_utc'], int), type(check['heartbeat_epoch_utc'])

# ---- 5x HANDOVER checkpoint ----
cp = f"""
## 5x checkpoint -- bm-c r{ROUND} ({NOW.strftime('%Y-%m-%d %H:%M')})

- authority = round_reports-bm-c.md full window log + state-bm-c.json closeout notes (r1236..r1240)
- product summary: W327 closed (r1236), W328 closed (r1238, dead-window absorb), W329 closed (r1240, dead-window absorb). Seat-first kept: W328 seat (MSG-0910), W329 seat (MSG-1005), W330 seat (MSG-1105) each published before its freeze.
- chain state: ledger 1,148,141 trials / merged K 721,720 / merged mu -0.09285308 / sigma 0.24519051 / se_mu 0.000289 / skill line 1.2023 (K-lift -0.0001) / canon flip NOT performed
- registry: owner_rows 319 (bm-a 130 / bm-b 41 / bm-c 148), ordinal 320, holes [15]; W330 bands A 744,901..746,900 (83rd A-hop) / B 746,901..747,100 (84th above-own-A, INSIDE cascade)
- health: smoke 57/57, dualrun ZERO-DRIFT streak 51, compute_audit rc0 (cpu 20.0%, py 6.9%), attrition 4 files CLEAN, orphan faces=0, S6 39/39 rc0, D-19 dec 0bf59c3c92 / ord 8ff7de47 both MATCH (unacked=0 of 109 order files)
- honest faces: detach-only finalize (foreground cancel at 5 silent minutes); freeze-face adjudicator needs forward-slash paths; RAM pressure keeps green_idle false at idle_trigger sampling
- next milestone: W331 seat probe + W330 freeze/splice/burn; <=48h
"""
ht = io.open(HANDOVER, encoding='utf-8').read()
if f"bm-c r{ROUND}" not in ht:
    if not ht.endswith('\n'):
        ht += '\n'
    io.open(HANDOVER, 'w', encoding='utf-8', newline='\n').write(ht + cp)

print(json.dumps({'round_no': st['round_no'], 'epoch': epoch, 'ts': TS,
                  'report_line_chars': len(line), 'handover_appended': True}, indent=1))