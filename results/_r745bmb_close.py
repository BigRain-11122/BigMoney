# r745 bm-b close: state round_no->745 + round report line append + heartbeat update
# Laws: r563 EOL probe (host EOL for append), r485 binary write, R170/R178 epoch int type,
#       r744 round-line format, GBK-contaminated ledger -> binary append only (no full decode).
import json, time, datetime, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# ---- 1) state.json
sp = os.path.join(ROOT, 'state.json')
with open(sp, 'rb') as f:
    st = json.loads(f.read().decode('utf-8'))
st['round_no'] = 745
st['note'] = ("r745: golden-week steady-state + r744-dead-tail absorb round. S0: identity bm-b anchored; "
              "churn-absorb ec6e03faf (r744 close tail 39 files: S6 35-leg products + state 744 + heartbeat + report line + daemon faces) "
              "-> merge#1 behind-12 e2cd857d2 (11 UU daemon faces resolved, r743 bloodline receipt _r745bmb_merge_resolve.json: 5 theirs-newer doc/status + 2 ours-newer attrition/fundamental + 2 rolling unions + token per-key max-union) "
              "-> push#1 claw-block deletion-set = pure behind-signal (bm-a r742 W137 files born on origin AFTER merge base 520d0faa9; ls-tree three-point probe; r524 law, zero --no-verify) "
              "-> merge#2 364ededcb clean rc0 zero-UU -> push#2 LANDED, post-push fetch+rev-list 0/0. "
              "S0.5: orders 154/154 zero unacked; D-19 decisions+orders both sha MATCH (D14DCC74872A/E79E15F9, r631 sparse-clone recipe, d19 read script _r745bmb_d19_read.py). "
              "S1 smoke 48/48. S2: job_list 0, tickets 0 open-unclaimed, satengine alive rc0 idle. "
              "S6 chain 39 legs ALL rc0 20:39:48-20:46:38 (lineage r744 verbatim, 3 label lines only): dualrun ZERO-DRIFT streak 38; compute_audit CLEAN (py 86% burning-healthy, pool_ready 3, effective_cores 13.24); "
              "py_watermark py_low_with_work_cands legal (local_batch_running=true trio burns); leg39 mechanical_ready=False (G1 F burn, G2 T, G3 T, G4 PENDING r638 armed). "
              "Trio V1533/Q1249/D1015 of 2000 (+14/+11/+10 vs r744). S7 quartet 4/4 (watchdog false-OK corrected: Invoke-SilentExe positional-arg binding error caught, re-verified rc0 via -Exe/-ArgString named-params) + attrition CLEAN. "
              "Inbox 3/3 bm-a W135/W136/W137 seat announcements archived (M-lane processed in-window). Zero new pits.")
st['round_no_label'] = 'round 745 (bm-b)'
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['ts'] = iso
st['updated'] = iso
st['last_seen'] = iso
st['clock_read'] = iso
st['last_decisions_read_at'] = iso
st['round_no_gap_note'] = ('none; r744 dead-tail (complete bookkeeping, missing close commit) absorbed at r745 S0 via churn ec6e03faf; '
                          'r745 = clean sequential +1 (double merge window, zero skipped rounds)')
st['next'] = ("(a) per-family nulls finalize as trio hits 2000/2000: V 1533 now (recent 0.42/min -> ETA ~10-06 afternoon, fluctuates), "
              "Q 1249 (~10-07), D 1015 (~10-08) -- leg39 probe every round; governance G4 PENDING -> r638 single-read fallback armed; "
              "(b) D-06 closeout report to group 10-07 12:00 (20 pit-*.md <=30KB re-verify holds); "
              "(c) 10-08 market reopen window (external data legs + paper marks resume + REGIME_GUARD v3 first new bar); "
              "(d) V finalize first: on mechanical_ready + governance resolved, per-family finalize per prereg.")
buf = json.dumps(st, ensure_ascii=False, indent=1) + '\n'
with open(sp, 'wb') as f:
    f.write(buf.encode('utf-8'))
json.loads(open(sp, 'rb').read().decode('utf-8'))

# ---- 2) round report line (binary append, host-EOL probe per r563)
rp = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
with open(rp, 'rb') as f:
    tail = f.seek(0, io.SEEK_END); f.seek(max(0, tail - 4)); last = f.read()
eol = b'\r\n' if last.endswith(b'\r\n') else b'\n'
line = ("{ts} | round 745 (bm-b, dept:engineering, golden-week steady-state + dead-tail absorb round) | "
        "[watermark verdict: GREEN (red=false lane healthy; satengine alive rc0 idle 0; board 0 open-unclaimed; trio in-flight = trial-labor line satisfied)] | "
        "CEO three-line: current-work = FUND trio NULLS burns V1533/Q1249/D1015 of 2000 (+14/+11/+10 vs r744, autofill+workers alive, 26 py procs) | "
        "latest-artifact = results/_r745bmb_s6_chain.log (39 legs ALL rc0 20:39:48-20:46:38, lineage r744 verbatim legdiff 3 label lines only) + docs REPORT/LIVE-2026-10-05 regen | "
        "next-milestone = trio V finalize ~10-06 afternoon @0.42/min, Q ~10-07, D ~10-08; D-06 group closeout 10-07 12:00; market reopen 10-08 (REGIME_GUARD v3 first new bar) | "
        "S0: churn-absorb ec6e03faf = r744 dead-tail absorb (39 files: r744 S6 products + state 744 + heartbeat + report line landed uncommitted, close commit missing; r714 pattern) "
        "-> merge#1 behind-12 e2cd857d2 11-UU daemon faces (r743 bloodline receipt _r745bmb_merge_resolve.json: 5 theirs-newer doc/status + 2 ours-newer attrition/fundamental + 2 rolling unions compute_audit/regime_state + token per-key max-union picked_theirs=2; readback+marker+twin asserts PASS) "
        "-> push#1 pre-push claw-block deletion-set = pure behind-signal (bm-a r742 W137 trio files born on origin AFTER merge base 520d0faa9; ls-tree 3-point probe: origin-tip has, base lacks, HEAD lacks; r524/r704-1 law, zero --no-verify) "
        "-> merge#2 364ededcb clean rc0 zero-UU -> push#2 LANDED, post-push fetch+rev-list 0/0 self-verified | "
        "S0.5: orders 154/154 head-scan zero unacked; D-19 decisions+orders sha both MATCH (D14DCC74872A599/E79E15F9, r631 sparse-clone, _r745bmb_d19_read.py) | "
        "S1 smoke 48/48 | S6: dualrun ZERO-DRIFT streak 38; compute_audit CLEAN (py 86.0% burning-healthy, pool_ready 3/3, parallel_eff 13.24 eff cores, zero flags); "
        "py_watermark py_low_with_work_cands legal (local_batch_running=true, trio burns actively consumed); leg39 VERDICT mechanical_ready=False (G1 burn F, G2 T, G3 rehearsal T, G4 PENDING r638 armed; window 10-05..10-09) | "
        "S7 quartet 4/4 (IterationLoop pin=2 no-op first-fire 20:52; watchdog re-verified rc0 after false-OK catch: Invoke-SilentExe positional-arg binding error -> corrected -Exe/-ArgString named-params, M-lane had archived inbox in-window 3/3 bm-a W135/136/137 seats; precommit+prepush claws CR-normalized MATCH) + attrition guard CLEAN (4 ledgers) | "
        "product score 2 (S6 product chain 39 rc0 + trio burn advance + CEO faces regen + dead-tail recovery)").format(ts=iso)
with open(rp, 'ab') as f:
    f.write(line.encode('utf-8') + eol)

# ---- 3) heartbeat
hp = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
with open(hp, 'rb') as f:
    hb = json.loads(f.read().decode('utf-8'))
hb['last_seen'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['round_no'] = 745
hb['round'] = 744
hb['last_round_at'] = iso
hb['ts'] = iso
hb['updated'] = iso
hb['last_action'] = ("r745 closed: dead-tail absorb + double-behind merge round -- churn ec6e03faf (r744 tail) + merge e2cd857d2 (11 UU canon resolver) "
                     "+ behind-signal claw-block (r524 law) + merge 364ededcb + push LANDED 0/0; S6 39 legs rc0; trio V1533/Q1249/D1015")
hb['current_task'] = "r745 golden-week steady-state closeout (S6 chain 39 rc0, trio in-flight)"
hb['now_active'] = "FUND trio NULLS burns V1533/Q1249/D1015 of 2000 (autofill+workers alive)"
hb['latest_artifact'] = "results/_r745bmb_s6_chain.log (39 legs ALL rc0) + docs/live_usage/LIVE-2026-10-05.md " + iso
hb['next_milestone'] = "trio V finalize ~10-06 afternoon, Q ~10-07, D ~10-08; D-06 closeout 10-07 12:00; market reopen 10-08"
hb['verdict'] = "GREEN steady-state; free RAM below 4GB heavy-work gate = no new heavy jobs this round (fleet discipline), trio burns continue"
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
buf = json.dumps(hb, ensure_ascii=False, indent=1) + '\n'
with open(hp, 'wb') as f:
    f.write(buf.encode('utf-8'))
rb = json.loads(open(hp, 'rb').read().decode('utf-8'))
assert isinstance(rb['heartbeat_epoch_utc'], int), 'readback epoch int check'

# ---- 4) report marker verify (binary tail, r743 disclosure-2 law)
with open(rp, 'rb') as f:
    t = f.seek(0, io.SEEK_END); f.seek(max(0, t - len(line.encode('utf-8')) - 8)); tb = f.read()
assert tb.count(b'round 745 (bm-b, dept:engineering') == 1, 'report line count==1'
print('CLOSE OK: state 745, report line appended (eol=%s), heartbeat epoch=%d int' % (repr(eol), epoch))
