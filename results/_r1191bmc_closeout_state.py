# -*- coding: utf-8 -*-
"""r1191 bm-c closeout: state + heartbeat forward write.

Not a restore/rewind -- forward-only bookkeeping for this window's own round.
"""
import io
import json
import time

NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime())
EPOCH = int(time.time())

NOTE = (
    "r1191: W306 CLOSED IN A RESUMED WINDOW (r1181/r1186/r1190 precedent: seat ADMIT "
    "9da7091894 / prereg freeze 7ab2b459e2 / five-face splice aa8e2a8f1f (164 parity rows, "
    "pf 9/9 + n1 rc0) / engine self-burn 12/12 (2,200 trials, shard appends 899a2207d1 + "
    "127f57d70b) were all already landed by the earlier r1191 window; this window ran the "
    "remaining legs only -- no re-burn, no double-burn). S0: HEAD == origin/main at open "
    "(127f57d70b), 14 dirty regenerable faces discarded per r1158 then fetch (0 behind). "
    "S0.5 D-19 watermark UNCHANGED (dec 17c2935984 / ord 00caa3452a, raw subprocess bytes), "
    "unacked orders=0 (109 files / 234 acks). S1 smoke 57/57. round-zero orphan probe "
    "py_faces=6 orphans=1 (external MV lane) zero kill. PRODUCT: (1) freeze-face adjudication "
    "PASS 0 heal / 0 unexplained deltas (results/_n1_face_adjudication_w306.json) -- first run "
    "failed on a Windows backslash path through git show (false 'exists on disk, but not in "
    "commit'); POSIX slashes fixed it. (2) PRE-FINALIZE six-gate 69th consecutive ALL PASS "
    "(results/_r1191bmc_w306_sixgate.json; CR-normalized worktree==landed, bands A "
    "688_501..690_500 / B 690_501..690_700 match the freeze receipt, banned ADMIT rc0, both "
    "selftests rc0, shards 12/12 >100KB, seed_admit FREE x2). (3) finalize one-pass: ledger "
    "1,095,341 + 2,200 = 1,097,541 / merged K 668,920 + 2,200 = 671,120 / merged mu "
    "-0.09284764 sigma 0.24512663 se_mu 0.000299 / W306-only mu -0.08964145 sigma 0.24199611 "
    "/ A p95 0.3090 p99 0.4623 / line 1.1999 -> 1.1999 (K-lift +0.0000); canon flip NOT "
    "performed. (4) fivekeys 6/6 ALL PASS (results/_r1191bmc_w306_fivekeys.json; anchors "
    "machine-read from n1_w305_results.json per r587; one prereg prose deviation disclosed -- "
    "sec.5 n_eff literal carried the W304 value 1,093,141 while W305 reads 1,095,341). "
    "(5) prereg sec.7/8 backfilled, 0 placeholders (28,046B). S6 39 legs ALL rc0 "
    "(results/_r1191bmc_s6_chain.json, 268.8s, per-leg flush): dualrun ZERO-DRIFT 616 entries "
    "streak 51 / compute_audit rc0 (cpu 19.0%, py 6.2%, pool_ready 3) / py_watermark rc0 / "
    "update_daily new rows 0 cutoff 2026-10-23 / regime ORANGE breadth 0.85 / clock "
    "CALL-2026-10-23 ORANGE_HOT sleeves 4 / scorecard 6/28/7 (129s) / lhb+futures no-op cutoff "
    "covers / options RETIRED / lane-guarded no-ops (zt_pool, heat, repo, moneyflow, sina_mf, "
    "astock, etf, thermo, dualarm, revosc, minute, ths, ah, fund_statements, alloc, "
    "system_v1) / fund_premium weekend no-op / fundamental fresh 10.7h skip / b_layer rc0 / "
    "prospect 22/22 drift 0 / promo eligible 0/22 / aggr+grid idempotent no-op at 2026-10-23 / "
    "t35 export-2026-10-23 / daily_scorecard stale-takeover from bm-a (heartbeat 139min, "
    "O-2100 s2.4) / REPORT-2026-10-24 / LIVE-2026-10-24 ORANGE cap 50% / build_status / token "
    "delta 0. S7 attrition 4 ledger files CLEAN (3 historical shrinks healed) / loop pin=5 "
    "no-op (first fire 10:35) / watchdog re-registered (S4U XML flip access-denied standing "
    "face) / both claws LF-normalized installed / orphan face=1 external. PIT: (a) the "
    "freeze-face adjudicator takes repo-relative paths to `git show <sha>:<path>` -- Windows "
    "backslashes read as a literal filename and produce a FALSE 'exists on disk, but not in "
    "commit'; always pass POSIX slashes; (b) the six-gate splice-commit grep must match the "
    "real message verbatim ('W306 five-face freeze splice'), a near-miss grep yields an empty "
    "sha and the resolvability assert fires before any comparison."
)

st = json.load(io.open('state-bm-c.json', encoding='utf-8'))
st['round_no'] = 1192
st['last_round'] = 'r1191'
st['last_decisions_check'] = NOW
st['r1191_closeout_note'] = NOTE
json.dump(st, io.open('state-bm-c.json', 'w', encoding='utf-8', newline='\n'),
          indent=1, ensure_ascii=False)

hb = json.load(io.open('fleet/machines/bm-c.json', encoding='utf-8'))
hb.update({
    'last_seen': NOW,
    'ts': NOW,
    'clock_read': NOW,
    'heartbeat_epoch_utc': EPOCH,
    'last_round': 'r1191',
    'round': 1191,
    'round_no': 1191,
    'last_round_closed': 'r1191',
    'last_round_closed_at': NOW,
    'last_round_at': NOW,
    'last_round_label': 'r1191',
    'last_round_summary': NOTE,
    'last_round_summary_at': NOW,
    'current': 'W306 CLOSED (finalize 1,097,541 / K=671,120 / line 1.1999, fivekeys 6/6, '
               'sec.7/8, S6 39/39, S7 CLEAN); next W307 seat probe',
    'current_task': 'r1191 W306 resumed closeout (sixgate 69th + finalize + fivekeys + S6/S7)',
    'activity_now': 'W306 CLOSED - next = r1192 W307 seat probe + prereg derive + splice',
    'did': 'W306 finalize one-pass (ledger 1,097,541 / K=671,120) + fivekeys 6/6 + sec.7/8 '
           'backfill + six-gate 69th ALL PASS + freeze-face adjudication PASS + S6 39/39 + S7',
    'next': 'r1192 W307 seat probe + prereg derive (post-W306 universe, own-A window reserved) + splice',
    'next_milestone': 'r1192 W307 seat probe + prereg derive + splice (<=48h)',
    'last_artifact': 'results/perpetual_faces/n1_w306_results.json',
    'latest_artifact': 'results/perpetual_faces/n1_w306_results.json',
    'recent_artifact': 'results/_r1191bmc_w306_fivekeys.json',
    'last_artifact_at': NOW,
    'verdict': 'round-complete',
    'health': 'green',
    'orphan_face': 1,
    'orphan_faces': 1,
    'idle_rounds': 0,
    'agenda_starved': False,
    'free_ram_gb': 1.5,
    'ram_free_gb': 1.5,
    'gpu_mem_total_mib': 16384,
    'gpu_mem_used_mib': 15604,
    'gpu_free_vram_mb': 780,
    'gpu_util_pct': 100,
    'gpu_face': 'busy -- external MV i2v lane (h3_i2v_album.py) holds 15604/16384 MiB at 100% util',
    'orders_ack_count': len(st.get('orders_ack') or []),
    'orders_ack_ts': NOW,
    'orders_ack_last': 'O-20261023-2325-bm-a.md',
    'verify': 'smoke 57/57 | sixgate 69th ALL PASS | three ledger identities exact | fivekeys 6/6 | '
              'dualrun streak 51 ZERO-DRIFT | attrition CLEAN | orphan face=1 (external MV lane)',
    'r1191_closeout_note': NOTE,
})
json.dump(hb, io.open('fleet/machines/bm-c.json', 'w', encoding='utf-8', newline='\n'),
          indent=1, ensure_ascii=False)
print('state round_no', st['round_no'], 'epoch', EPOCH, type(EPOCH).__name__)
print('heartbeat epoch', hb['heartbeat_epoch_utc'], type(hb['heartbeat_epoch_utc']).__name__)