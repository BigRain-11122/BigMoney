# r798 bm-b close driver: state 796->798 honest jump (dead r797 absorb) + heartbeat + round report + commit/push/verify
import json, subprocess, time, os

NOW = time.time()
EPOCH = int(NOW)
import datetime
ISO = datetime.datetime.fromtimestamp(NOW).astimezone().replace(microsecond=0).isoformat()

# ---------- state.json ----------
st = json.load(open('state.json', encoding='utf-8'))
st['round_no'] = 798
st['note'] = ("r798: dead-r797 absorb guard round: 05:52 session killed by 25min timeout at 05:57 after S0 churn-absorb only; "
              "absorbed per r792 precedent honest jump 796->798; orders 163/163 round-start + close double-scan zero-delta; "
              "D-19 REGRESSION tri-source verified: group origin history surgery (tip c7012f1 00:19:56 predates r793-r796 watermarks "
              "7FFC880/F1B0CC59 now unreachable at origin; ls-remote + temp-clone fetch + real-tree fetch all agree); "
              "watermarks follow origin current truth 635C3024/9BE6A74F per r701 law; content already consumed r789/r792 zero new action; "
              "smoke 48/48; S6 35/35 rc0; QA r798 5/5 (93 trades determinism=True, --round 798 explicit detached); "
              "trio probe Q1963/D1630/V2000 (D accelerated 0.318->1.0/min eta ~12:22, Q eta ~07:47); S7 quartet 4/4 + attrition CLEAN")
st['last_round_at'] = ISO
st['ts'] = ISO
st['updated'] = ISO
st['last_seen'] = ISO
st['last_decisions_sha'] = "635C3024A95E4487A08E55BE9DAD3A97E41C73726A9D82D955986D95EF6F6AF6"
st['last_decisions_at'] = ISO
st['round_no_label'] = "r798"
st['clock_read'] = ISO
st['last_decisions_read_at'] = ISO
st['last_orders_sha'] = "9BE6A74F882866653504717DBAA2E52FAA92D913699BFEE22BB767E0AAF6CE21"
st['last_orders_read_at'] = ISO
st['last_orders_sha_note'] = ("r798: orders 163/163 zero-delta (round-start + close double-scan, .md-suffix per r767); "
                              "D-19 REGRESSION: origin history surgery tri-source verified (ls-remote direct + temp-clone fetch + real-tree "
                              "C:\\Users\\Administrator\\FluxGroup fetch all = tip c7012f1 00:19:56); dual-face now 635C3024/9BE6A74F = content "
                              "already consumed r789/r792 (BigMoney rows D-20261007-01/02/03 receipted r793, token CEO row receipted r789) = "
                              "zero new dispatch zero action; watermarks follow origin current truth per r701 law")
st['next'] = ("(1) trio Q first-to-2000 ~10-07 07:47 (rate 0.387/min @06:11 probe, 1963/2000; same-window pool dual-flip per r668 law; "
              "G1 pending Q+D; G2 integrity + G3 rehearsal green; G4 PENDING r638 fallback armed); "
              "(2) D finalize ~10-07 12:22 (1630/2000 rate accelerated 1.0/min); "
              "(3) trio close -> G1 green when Q+D both 2000 -> trio finalize round same-window (window 10-05..10-09); "
              "(4) O-20261006-2358 trio self-claim law: post-trio-close <=1h claim one backlog item; "
              "(5) market reopen 10-08: S6 legs 25-28 resume + REGIME_GUARD v3 first new bar enforce; "
              "(6) D-06 group closeout 10-07 12:00 (bm-c lane; CODELY 29,255B compliant)")
st['did'] = ("r798: S0 dead-r797 absorb (churn-absorb 4c397fae + pull clean) + orders 163/163 + D-19 regression tri-source "
             "(watermarks -> origin truth 635C3024/9BE6A74F) + smoke 48/48 + S6 35/35 rc0 + QA r798 5/5 + trio probe "
             "Q1963/D1630/V2000 + S7 quartet 4/4 + attrition CLEAN")
st['verdict'] = ("green: dead-r797 absorb guard round; trio Q/D burns alive (Q 1963/2000 eta ~07:47, D 1630/2000 accelerated "
                 "1.0/min eta ~12:22, V complete); orders 163/163; smoke 48/48; QA r798 5/5; satengine alive rc0 idle; "
                 "boards 0 open (176 tasks all done); CODELY <=cap compliant; D-19 regression adjudicated per r701 law")
st['current_task'] = ("r798 closed; next = Q first-to-2000 ~10-07 07:47 same-window pool dual-flip per r668 / trio finalize when "
                      "Q+D both 2000 (D ~12:22 accelerated) / market reopen 10-08 S6 legs 25-28 + REGIME_GUARD v3 first new bar enforce")
json.dump(st, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- heartbeat ----------
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = ISO
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = ISO
hb['free_ram_gb'] = 7.33
hb['gpu_free_vram_gb'] = 3.654
hb['gpu_free_vram_mb'] = 3654
hb['verdict'] = ("green: dead-r797 absorb guard round r798; trio Q/D burns alive (Q 1963/2000 eta ~07:47 rate 0.387/min, "
                 "D 1630/2000 accelerated 1.0/min eta ~12:22, V 2000 COMPLETE); orders 163/163; smoke 48/48; QA r798 5/5; "
                 "satengine alive rc0 idle; boards 0 open; CODELY <=cap compliant; D-19 regression adjudicated per r701 law")
hb['current_task'] = ("r798 closed; next = Q first-to-2000 ~10-07 07:47 same-window pool dual-flip per r668 / trio finalize when "
                      "Q+D both 2000 (D ~12:22) / market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD v3 first new bar enforce)")
hb['last_round_at'] = ISO
hb['round_no'] = 798
hb['round'] = 798
hb['last_action'] = ("r798: dead-r797 absorb (honest jump 796->798) + orders 163/163 double-scan zero-delta + D-19 regression "
                     "tri-source verified (watermarks -> origin truth 635C3024/9BE6A74F per r701) + smoke 48/48 + S6 35/35 rc0 + "
                     "QA r798 5/5 + S7 quartet 4/4 + attrition CLEAN")
hb['now_active'] = ("FUND trio NULLS judgment batch in-flight: Q 1963/2000 (rate 0.387/min, ETA ~07:47) / D 1630/2000 (rate 1.0/min "
                    "accelerated, ETA ~12:22) / V 2000/2000 COMPLETE; G1 pending Q+D, G2+G3 green, G4 PENDING r638 fallback armed; "
                    "finalize window 10-05..10-09")
hb['latest_artifact'] = ("qa/smoke-r798.md 5/5 + qa/equity-curve-r798.png (93 trades determinism=True, --round 798 explicit) + "
                         "results/_r798bmb_s6_chain.log (35 legs all rc0 306s) + results/_r798bmb_d19_read.json (D-19 regression "
                         "tri-source evidence) @" + ISO)
hb['next_milestone'] = ("trio Q first-to-2000 ~10-07 07:47 same-window pool dual-flip per r668 law + D ~12:22 (accelerated) + trio "
                        "finalize when Q+D both 2000 + post-trio-close O-20261006-2358 self-claim <=1h + market reopen 10-08 "
                        "(S6 legs 25-28 + REGIME_GUARD v3) - within 48h window")
hb['task'] = "r798 closed; see state.next"
hb['ts'] = ISO
hb['updated'] = ISO
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int'

# ---------- round report ----------
RR = ("{ts} | round 798 (bm-b, dept:engineering, dead-r797 absorb + D-19 regression adjudication guard round) | "
      "[watermark verdict: GREEN (red=false lane healthy; satengine alive rc0 idle queue_depth=0; boards 0 open both boards "
      "(job_list empty + fleet tasks 176 files zero status=open mechanical scan); trio Q/D in-flight multiproc burning = "
      "trial-labor line satisfied)] | "
      "CEO three-line: current-work = FUND trio NULLS judgment batch in-flight (Q 1963/2000 rate 0.387/min ETA ~07:47 / "
      "D 1630/2000 rate 1.0/min ACCELERATED ETA ~12:22 / V 2000/2000 COMPLETE; burns ALIVE (pid 57116 fund_quality pool "
      "still writing @06:01 face mtime); G1 pending Q+D, G2 integrity + G3 rehearsal green, G4 PENDING r638 fallback armed; "
      "finalize window 10-05..10-09) | "
      "latest-artifact = qa/smoke-r798.md + qa/equity-curve-r798.png (QA charter pack 5/5: 3 syms x 800 bars real backtest "
      "93 trades determinism=True sharpe 0.159, detached --round 798 explicit per r758 law, pid 47580 terminal-state "
      "poll-verified) + results/_r798bmb_s6_chain.log (35 executed legs all rc0 306s wall, lineage r796 verbatim) + "
      "results/_r798bmb_d19_read.json (D-19 regression tri-source evidence) | "
      "next-milestone = trio Q first-to-2000 ~10-07 07:47 same-window pool dual-flip per r668 law + D ~12:22 accelerated + "
      "trio finalize when Q+D both 2000 + post-trio-close O-20261006-2358 self-claim <=1h + D-06 group closeout 10-07 12:00 "
      "(bm-c lane) + market reopen 10-08 (S6 legs 25-28 resume + REGIME_GUARD v3 first new bar enforce) | "
      "S0: identity=bm-b anchored (machine.json first-read); dead r797 takeover (05:52 session killed by 25min ROUND TIMEOUT "
      "at 05:57 after S0 churn-absorb only, run log evidence; absorb per r792 precedent honest jump 796->798); own daemon "
      "faces (8: autofill/satengine/nulls-lanes/p1d_gates + inbox processed move MSG-0547) churn-absorbed pre-pull 4c397fae "
      "(r642 law) -> pull --rebase clean up-to-date | "
      "S0.5: orders 163/163 zero-delta round-start + close double-scan (.md-suffix normalized per r767 law); "
      "D-19 REGRESSION: group origin history surgery detected -- origin tip c7012f1 (00:19:56) predates r793-r796 watermarks "
      "(dec 77FFC880 / ord F1B0CC59 -> unreachable blobs at origin); TRI-SOURCE verified (git ls-remote direct + temp-clone "
      "cached-fetch + real-tree C:\\Users\\Administrator\\FluxGroup fetch+show, all agree c7012f1e); current origin dual-face = "
      "635C3024/9BE6A74F = 00:16/00:19 batch content already consumed with receipts r789/r792 (BigMoney rows D-20261007-01/02/03 "
      "receipted r793; token CEO row receipted r789) = zero new dispatch zero action; watermarks follow origin current truth "
      "per r701 regression law (consumed receipts live in round reports); inbox 0 unread | "
      "S1: smoke 48/48 | "
      "S2: job_list 0 + fleet tasks 176 files 0 open mechanical scan | "
      "S3: satengine alive rc0 idle queue_depth=0; watermark red=false; trial-labor line trio in-flight satisfied zero new "
      "drafting legal (board/bandit empty, trio owns lane) | "
      "S6: 35 executed legs all rc0 (39 minus 25-28 golden-week honest-skip, cutoff 2026-09-30 unchanged, reopen 10-08); "
      "dualrun before compute_audit per T-116 s3 ordering law; leg39 trio probe Q 1963/D 1630/V 2000 dup_k=0 x3 integrity "
      "True mechanical_ready=False (G1=False G2=True G3=True) G4=PENDING; D rate acceleration 0.318->1.0/min eta "
      "10-08 01:40->12:22 (r796 estimate superseded by fresh @06:11 probe) | "
      "S7: quartet 4/4 (IterationLoop pin=2 no-op first-fire 06:12 + LoopWatchdog re-registered first-fire 06:12 + "
      "precommit/prepush claws LF-normalized reinstall) + attrition guard CLEAN rc0 (4 ledgers, healed rows historical, "
      "evidence results/_attrition_guard_scan.json) + state 796->798 honest jump per r714/r792 absorb law + heartbeat "
      "epoch 1791324797+ int self-verified + orders_ack 163 self-verified | "
      "treasure zero-hit claim: zero sweep/archive/delete actions this round | "
      "verification: smoke 48/48 + QA r798 5/5 + S6 35 legs rc0 x35 + attrition CLEAN + D-19 triple-source agreement | "
      "local undelivered-to-origin commit count: PENDING_FILL_R798 (post-push self-verify below) | "
      "product score 2 (S6 35-leg product chain regen + QA pack r798 real-backtest evidence + D-19 regression tri-source "
      "adjudication evidence)\n").format(ts=ISO)
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(RR)

# ---------- commit / push / verify ----------
def run(cmds):
    return subprocess.run(cmds, capture_output=True, text=True, encoding='utf-8', errors='replace')

r = run(['git', 'add', '-A'])
print('add rc=', r.returncode, r.stderr[-200:] if r.stderr else '')
r = run(['git', 'commit', '-m', 'round 798: dead-r797 absorb guard (orders 163/163 + D-19 regression tri-source adjudicated per r701 + smoke 48/48 + S6 35/35 rc0 + QA r798 5/5 + quartet 4/4 + attrition CLEAN) [via bm-b r798]'])
print('commit rc=', r.returncode, (r.stdout[-150:] + r.stderr[-150:]) if r.returncode else r.stdout[:80])
if r.returncode == 0:
    p = run(['git', 'push'])
    print('push rc=', p.returncode, (p.stderr or p.stdout)[-200:])
    if p.returncode != 0:
        rb = run(['git', 'pull', '--rebase'])
        print('rebase rc=', rb.returncode)
        if rb.returncode == 0:
            p2 = run(['git', 'push'])
            print('push2 rc=', p2.returncode)
            if p2.returncode != 0:
                fb = run(['git', 'push', 'origin', 'machine/bm-b-r798'])
                print('fallback-branch rc=', fb.returncode)
        else:
            print('REBASE-CONFLICT: read-only closeout, report and stop')
    if p.returncode == 0:
        f = run(['git', 'fetch'])
        ls = run(['git', 'ls-tree', 'origin/main', 'state.json'])
        print('delivery ls-tree:', ls.stdout.strip()[:80])
        behind = run(['git', 'rev-list', '--count', 'origin/main..HEAD'])
        print('undelivered count =', behind.stdout.strip())
