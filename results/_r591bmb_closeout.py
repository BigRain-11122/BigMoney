# r591 bm-b closeout: state round++, round report line, heartbeat (dynamic fields
# only, orders_ack carried verbatim per r583 law; bytes-safe appends per r530 law)
import json, time, io, datetime

now = datetime.datetime.now()
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
now_disp = now.strftime('%Y-%m-%d %H:%M:%S')
epoch = int(time.time())

# ---- state.json (dynamic fields only) ----
s = json.load(io.open('state.json', encoding='utf-8'))
assert s['round_no'] == 590, f"unexpected round_no {s['round_no']}"
s['round_no'] = 591
s['note'] = ("r591: waiting-state round declared (engine supply rotation not mine: W112 bm-a burning 7/12+ + W113 declared by bm-c r381, "
             "no unilateral wave per r239 collision law; moneyflow IC next_pick panel-blocked source conn-down 53/5222; W14-GENERATE GM-parked standing wait; "
             "paper block Golden Week no-new-bar) + S0 pure-FF integration of bm-a r590 695a88506: FOUR bm-b identity faces found stale-regressed on origin "
             "by bm-a surgical stale-carry (state.json 590->589, heartbeat 19:34->19:19, round_reports.md r590 line dropped, seat-MSG inbox copy) -> "
             "r585 pure-FF + split checkout with 4-face protect + re-land at this round's commit per r589 law + pool_core_samples UNION 1063+12=1075 all-dict "
             "(uncommitted W111 burn-tail samples preserved, r570/r580 law) + S6 33 legs rc0 (dualrun ZERO-DRIFT streak 35/3) + S7 4/4 (pin=2 no-op, watchdog, "
             "both claws) + attrition guard CLEAN 4 ledgers + smoke 47/47 + orders 143/143 double-scan zero-pending + D-19 honest skip (r481 special, "
             "937A373D cross-verified unchanged via bm-a r590)")
s['last_round_at'] = now_disp
s['last_round_ts'] = now_iso
s['ts'] = now_disp
s['updated'] = now_disp
s['updated_at'] = now_iso
s['last_decisions_at'] = s.get('last_decisions_at', '2026-10-02T17:43:44+08:00')  # unchanged, honest skip
raw = json.dumps(s, ensure_ascii=False, indent=1) + '\n'
io.open('state.json', 'w', encoding='utf-8', newline='').write(raw)

# ---- round report line (bytes-safe append, EOL preserved) ----
line = ("2026-10-02T19:%02d+08:00 | round 591 (bm-b) | WM verdict: py_low_board_clear legal idle "
        "(py 0.6%%, open 0, bandit 0, local_batch_running=false, board fully closed, n=2 window) | did: WAITING-STATE ROUND declared per product-priority law "
        "-- four blocked lanes one line each: (1) engine supply rotation not mine: W112 bm-a burning 7/12+ + W113 declared by bm-c r381, no unilateral wave grab per r239; "
        "(2) moneyflow IC next_pick panel-blocked, source conn-level down since 09-25 (53/5222 symbols), 30-min self-heal in flight; "
        "(3) W14-GENERATE GM dual-ruling park = one-line standing wait; (4) paper block Golden Week honest no-new-bar LAST_BAR=2026-09-30 (r588 precedent) "
        "+ S0 pure-FF integration of bm-a r590 (695a88506): FOUR bm-b identity faces found STALE-REGRESSED on origin by bm-a surgical stale-carry "
        "(state.json 590->589, hb 19:34->19:19, round_reports.md r590 line dropped, seat-MSG inbox copy) -> r585 pure-FF + split checkout with 4-face protect, "
        "re-land at this round commit per r589 law + pool_core_samples UNION 1063+12=1075 rows all-dict (uncommitted W111 burn-tail samples preserved, "
        "r570/r580 law; finalize commit 57eefaa04 carried only 13 shard/product files, never the jsonl) "
        "+ S6 33 legs rc0 (dualrun ZERO-DRIFT streak 35/3 cutoff 2026-10-01; REPORT/LIVE-2026-10-02 regenerated idempotent; host-guarded faces honest skip, "
        "bm-a hb fresh) + S7 self-heal 4/4 (loop pin=2 no-op, watchdog, pre-commit+pre-push claws) + attrition guard CLEAN (4 ledgers) + smoke 47/47 "
        "+ orders 143/143 double-scan zero-pending + D-19 honest skip (r481 special; 937A373D cross-verified unchanged via bm-a r590) "
        "| verification: _r591bmb_s0_integrate.py all assertions green (state=590 pre-write, r590 line present, behind-origin=0, union prefix-intact all-dict); "
        "S6 runner log 33x rc=0; WM probe jsonl tail py_low_board_clear | next: W112 burn completion (bm-a) -> W113 bm-c freeze -> W114 bm-b supply "
        "next-owned wave five-face (window <=48h); moneyflow IC batch auto-starts when panel completes "
        "| CEO face: NOW=waiting-state round (rotation+blocks declared above), LAST ARTIFACT=W111 finalize 57eefaa04 (ledger 608,748 K 242,120 skill_line 1.171) "
        "@19:37 + this round union-preservation integration, NEXT MILESTONE=W113 freeze by bm-c then W114 bm-b five-face (window <=48h) "
        "| behind-origin-commits=0 (verified at push) [via bm-b r591]") % (now.minute,)
rb = open('logs/iteration-loop/round_reports.md', 'rb').read()
eol = b'\r\n' if b'\r\n' in rb[-200:] else b'\n'
open('logs/iteration-loop/round_reports.md', 'ab').write(line.encode('utf-8').replace(b'\n', eol) + eol)

# ---- heartbeat (dynamic fields only, orders_ack carried verbatim) ----
h = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
h['last_seen'] = now_iso
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now_iso
h['current_task'] = ("r591 waiting-state: W112 bm-a burning + W113 bm-c's next (my wave=W114); moneyflow IC panel-blocked; "
                     "S0 integration re-land + pool union 1075 done this round")
h['cpu_cores'] = 16
h['free_ram_gb'] = 4.8
h['idle_ram_gb'] = 4.8
h['gpu_free_vram_gb'] = 2.1
h['gpu_idle_vram_gb'] = 2.1
h['total_ram_gb'] = 25.7
h['cpu_util_pct'] = 17.0
h['round_no'] = 591
h['round_no_label'] = 'r591'
h['verdict'] = ("waiting-state legal: board clear, bandit 0, no runnable batch (moneyflow panel source-blocked); "
                "engine rotation not mine (W112 bm-a burning, W113 bm-c declared); supply chain healthy; orders 143/143 ack")
h['ram_free_gb'] = 4.8
h['ram_avail_gb'] = 4.8
h['gpu_vram_free'] = 2.1
h['gpu_idle_vram_mb'] = 2200
h['gpu_free_vram_mb'] = 2200
raw = json.dumps(h, ensure_ascii=False, indent=1) + '\n'
io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8', newline='').write(raw)

# ---- post-write self-verify ----
chk = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read must be T-separated ISO (R262 law)'
assert len(chk['orders_ack']) == 143, f"orders_ack must stay 143, got {len(chk['orders_ack'])}"
st = json.load(io.open('state.json', encoding='utf-8'))
assert st['round_no'] == 591
print('CLOSEOUT WRITES OK: state=591, heartbeat epoch', epoch, 'orders_ack 143 carried, report line appended at', now_iso)
