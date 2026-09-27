# -*- coding: utf-8 -*-
"""r322 bm-a S5/S7 wrap: round report line + state round_no + heartbeat update."""
import json, time, datetime, io, sys

now_local = datetime.datetime.now().astimezone()
stamp = now_local.isoformat(timespec='seconds')   # T-separated, +08:00 offset

# ---- 1. round report line ----
rep_path = r'logs\iteration-loop\round_reports-bm-a.md'
rep = ('{ts} | R322 bm-a S0 MAIN-RELAND (28-UU 3-machine same-window mirror collision canon-resolved) | '
       'watermark VERDICT: GREEN (red=false; audit CLEAN flags=[] @12:43:39; probe insufficient_history @12:43:45 = Sunday legal idle: board 0 open + bandit next_pick claimed + pool done-flip no ready shard) | '
       'S0: pull --rebase vs origin fbef43da (bm-b r322 12:34:29 + bm-c r80 12:37:21, 3-machine same-window S6 mirror triple-collision) -> 28 UU; '
       'probe=results/_r322bma_probe.py: 25 measurement-face files pure-runtime-ts diffs origin-newer (12:33-12:34 vs ours 12:31-12:32) -> take-origin (twins same-side REPORT json+md / dashjs+json / export+latest); '
       '3 true ledgers union zero-loss: autofill 57+50->57 key(ts,machine,entry,shard,pid) last_tick origin@12:30:02; '
       'compute_audit history 202+205->207 collision-200 content-diff=0 verified=shared-ancestor-identical, only-origin 2 + only-r321 5 all kept, latest=origin@12:33:14; x2_watch 648+648->654 line-union; '
       'resolver=results/_r322bma_resolve.py (all json.loads verified) -> rebase --continue clean, 2 addendum replays clean -> push landed fbef43da..b60fd08f = r321 MAIN-RELAND DONE (machine/bm-a-r321 backup plan closed, r321 new hash 4546952c) | '
       'S0.5: orders 96/96 zero unacked; decisions scan: D-20260927-09 receipted (executed r321, re-landed on main, deep-scan probe used this round), D-20260927-07/08/10 executors not BigMoney = zero-action, C-20260927-01 council-seat no in-repo wiring noted honestly | '
       'S1: smoke 25/25 PASS | S6: 32/32 legs rc=0 (Sunday no-op family; sina_mf A1 deep repull in flight = legal occupied) | '
       'S4: CODELY.md 10298B over-10KB-line -> 12th-batch in-window archival (r317/r318/r319/r79 4 lines line-level zero-loss -> research/memory-archive/202609.md 850,047B) + new pitlaw r322 union-collision-content-eq-verify; CODELY.md now 7362B | '
       'NEXT: (a) sina_mf A1 repull completion -> T-72 gate + moneyflow IC reference batch (next_pick claimed); (b) r322 backup-branch cleanup candidate machine/bm-a-r321 (landed, prune decision next rounds); (c) 10-01 regime-guard date-gate proximity: T-21 three-gate auto-activation 4 days out, zero manual action')
with open(rep_path, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + rep + '\n')

# ---- 2. state round_no 322 ----
st_path = r'state-bm-a.json'
st = json.load(open(st_path, encoding='utf-8-sig'))
st['round_no'] = 322
st['updated'] = stamp
with open(st_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- 3. heartbeat ----
hb_path = r'fleet\machines\bm-a.json'
hb = json.load(open(hb_path, encoding='utf-8-sig'))
epoch = int(time.time())
hb['last_seen'] = stamp
hb['current_task'] = ('R322 done: S0 main-reland 28-UU 3-machine collision canon-resolved (push b60fd08f) + S6 32/32 rc=0 + CODELY 12th-batch archival')
hb['cpu_cores'] = 32
hb['cpu_pct'] = 25.7
hb['free_ram_gb'] = 47.6
hb['gpu_free_vram_gb'] = 5.6
hb['verdict'] = ('py_low legal-occupied: sina_mf A1 deep repull in flight (lock alive, panel incomplete 5228 syms, T-72 claim, R314 supply line); board 0 open; pool done-flip no ready; audit CLEAN; Sunday legal idle')
hb['heartbeat_epoch_utc'] = epoch          # MUST be JSON int (smoke F7)
hb['clock_read'] = stamp                  # ISO 8601 T-separated with offset
assert isinstance(hb['heartbeat_epoch_utc'], int)
with open(hb_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---- self-verify (reload + assertions) ----
st2 = json.load(open(st_path, encoding='utf-8-sig'))
hb2 = json.load(open(hb_path, encoding='utf-8-sig'))
assert st2['round_no'] == 322
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'F7: epoch must be int'
assert 'T' in hb2['clock_read'] and '+' in hb2['clock_read'], 'F7: clock_read must be T-separated ISO8601'
assert len(hb2.get('orders_ack', [])) == 96
print('OK: report line appended, state round_no=322, heartbeat epoch=', hb2['heartbeat_epoch_utc'], 'clock=', hb2['clock_read'])
