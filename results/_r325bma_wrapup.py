# -*- coding: utf-8 -*-
"""r325 bm-a S7 wrap-up: round report line + state bump + heartbeat refresh."""
import json
import time
import datetime
import io

# ---- round report line (append-only, one line) ----
REPORT = 'logs/iteration-loop/round_reports-bm-a.md'
ts_now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
line = (
    " | ".join([
        ts_now,
        "R325 bm-a (dept:研究+工程)",
        "WM first-line verdict: py_low_with_work_cands + audit FLAG:pool_starvation "
        "(probe 13:14 py 0.1%; pool 77/77 done 0 ready; SUPPLY RESPONSE DELIVERED this "
        "round = T-86 wave-2 freeze opens next real carrier; moneyflow-IC next_pick "
        "stays source-blocked on panel, sina_mf A1 repull in flight ~49% ETA ~15:0x "
        "feeds it) | did: (A) S0 pull FF + S0.5 orders scan zero-unacked (96/96) + "
        "decisions P-32 receipts: D-20260926-10 IntradayMarks-E2 closed=HQ-exec "
        "zero-action-ours (ticket-health face, patrol tooling HQ lane), "
        "D-20260927-01 batch receipts verified incl our F-05 counted into 5/8 "
        "(executed HQ, zero-action), D-20260927-02/03 BigCompute/BigDomain "
        "not-our-lane, C-20260927-01 council pricing not-our-face + smoke 25/25 "
        "(B) S3 closed loop = T-86 WAVE-2 WIDE-UNIVERSE ROSTER FREEZE (R99 freeze "
        "precedes runner build): T-87 gate OPEN (astock panel complete 2026-09-24 "
        "n=5,228 bm-b-local) -> scripts/census_w2_roster.py deterministic derivation "
        "+ results/census_fusion_s2/w2_roster.json (p1c sha 45543c539e6a/273 rows + "
        "a158 sha 1394ab0cf560/7 rows artifact anchors): W2-A 32 faces (B4 zoo "
        "sign-P1E-sec5 + C-GTJA191 top-10 |h5_full_ir| + C-WQ101 top-10 + C-A158 "
        "all-7 honest-undercount + E-LHB lhb_count_20) = 5,456 cand + 64 ctrl + "
        "400 nulls = N 5,920; seeds registered same-commit R250 one-step "
        "(census_fusion_s2_w2=20281500 band ..20281899 collision-free above "
        "cn_mkneutral top 20281300; census_fusion_s2_w2_unc=20282000 derive-law); "
        "W2-B 9 faces (D8 sina-MF + E-heat) pre-declared GATED (panel 2775/5222 + "
        "heat bm-a-local, sec.9.4 confirm before run; cross-math 6,024 frozen); "
        "prereg sec.9.3 + registry pointer + ticket progress chain reconciled "
        "(r279-stall -> R290 wave-1 closure documented: prereg sec.7/8/9.2 + UNC "
        "ci_pos 1/4060 honest) (C) S6 chain 32/32 rc=0 (_r324bma_s6_chain.ps1 = "
        "prior scheduled R324 round's committed artifact; DUPLICATE-RUN DISCLOSURE: "
        "scheduled-loop R324 completed 13:02:30 pre-session, my chain rerun "
        "13:14-17 idempotent-legs zero-damage, my session-start misread had me "
        "temp-overwrite their chain script -> RESTORED via git checkout, my "
        "_r324bma-prefixed scratch deleted, ticket field renamed r324->r325) "
        "(D) push lane: 2x rebase collision batches canon-resolved vs bm-b r324 "
        "mirror (15-UU: compute_audit 207+201->208 union 200-key content-identical "
        "r322 + 13 take-theirs) + vs bm-c r82 third-machine mirror mid-resolve "
        "(25-UU: compute_audit ->209 union + x2_watch 684+684->690 line-union + "
        "autofill cap50-asc-r245 last_tick tie->HEAD + t35/daily_scorecard "
        "ts-diffpick S3-newer + 23 take-theirs; resolvers "
        "_r325bma_resolve.py/_r325bma_resolve2.py + probes 1/2) + third rebase "
        "clean vs bm-c r82 addendum + autofill watchdog tick checkpoint commit "
        "(13:20:02 live producer record) -> PUSH LANDED 9739d6ee | verify: smoke "
        "25/25, roster json round-trip + seeds import-verified, chain 32/32 rc=0, "
        "resolver zero-loss assertions all-pass | next: W2-A runner build (bm-a "
        "hermetic, mirrors wave-1 machinery) + pool entry lane_owner=bm-b = next "
        "round primary carrier (pool-starvation remediation); sina_mf repull "
        "terminal window ~15:0x; Monday 09:15 T-91 s3 auto-fire"
    ])
)
with io.open(REPORT, 'a', encoding='utf-8', newline='\n') as fh:
    fh.write(line + '\n')
print('report line appended, len', len(line))

# ---- state round_no bump ----
SP = 'state-bm-a.json'
st = json.load(open(SP, encoding='utf-8'))
st['round_no'] = 325
json.dump(st, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
assert json.load(open(SP, encoding='utf-8'))['round_no'] == 325
print('state round_no -> 325')

# ---- heartbeat ----
HB = 'fleet/machines/bm-a.json'
h = json.load(open(HB, encoding='utf-8'))
epoch = int(time.time())
h['machine_id'] = 'bm-a'
h['last_seen'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
h['current_task'] = 'R325 done: T-86 wave-2 roster freeze landed; next W2-A runner+pool entry'
h['verdict'] = 'py_low_with_work_cands + pool_starvation supply-opened (wave-2 freeze landed; runner next round)'
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
if len(h['clock_read']) > 3 and h['clock_read'][-3] != ':':
    # ensure +08:00 form
    h['clock_read'] = h['clock_read'][:-2] + ':' + h['clock_read'][-2:]
h['round_no'] = 325
json.dump(h, open(HB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# self-verify (R170/R178/R262 law): epoch int + clock T-format + reload parse
h2 = json.load(open(HB, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in h2['clock_read'] and ':' in h2['clock_read'][-6:], 'clock must be T-form with offset'
print('heartbeat ok: epoch int', h2['heartbeat_epoch_utc'], 'clock', h2['clock_read'])
