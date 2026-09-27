# r88 bm-c closeout: state round bump + heartbeat update (epoch = python int(time()) JSON int law R170/R178)
import json, time, subprocess

now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# --- state-bm-c.json: round 87 -> 88 ---
sp = 'state-bm-c.json'
st = json.load(open(sp, encoding='utf-8'))
assert st['machine_id'] == 'bm-c' and st['round_no'] == 87, f"unexpected state: {st.get('round_no')}"
st['round_no'] = 88
st['updated'] = time.strftime('%Y-%m-%dT%H:%M')
st['note'] = ("r88: fold executed on schedule -- r87 fallback pair d9456e42/c86dfb3d replayed by S0 pull --rebase "
              "into 7405352c/57bf826f (hash-rewrite receipt), push completes fold + GC machine/bm-c-r87 own-branch duty; "
              "identity correction mid-round (machine.json=bm-c authoritative, state files at root are shared faces); "
              "pitlaw r88 triple + CODELY 17th-batch in-window archival (8034B<10KB) incl PS Char-trap same-round catch+restore; "
              "orders 96/96 double-scan; decisions D-04/D-05 maintained-receipts; smoke 25/25; S6 32/32 rc=0 "
              "(resident chain path-adaptive patch); Monday T-91 readiness verified read-only.")
st['last_round_ts'] = now_iso
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state-bm-c.json -> round 88')

# --- fleet/machines/bm-c.json heartbeat ---
hp = 'fleet/machines/bm-c.json'
hb = json.load(open(hp, encoding='utf-8'))
assert hb['machine_id'] == 'bm-c'
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now_iso
hb['current_task'] = ("R88 done: fold of r87 pair via S0 rebase replay (hash-rewrite receipt 7405352c/57bf826f) + GC own stale branch; "
                      "CODELY 17th-batch archival + pitlaw r88; S6 32/32; smoke 25/25; orders 96/96; next: W2-A harvest watch (bm-b), "
                      "Monday fund_premium self-heal 15:30 + new-bar chain")
hb['cpu_util_pct'] = 65.0
hb['free_ram_gb'] = 1.6
hb['gpu_free_vram_mb'] = 1466
hb['cpu_pct'] = 0.0
hb['verdict'] = ("legal idle: board 0 open (30 all-claimed), wm red=false probe 15:44:30 py_low_board_clear legal "
                 "(pool ready=1 W2-A lane_owner bm-b burning since 15:12:44, R31 not burnable here), r88 fold+archival round complete")
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# post-write self-verification (smoke F7 law: epoch must be JSON int)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'EPOCH NOT INT'
assert 'T' in chk['clock_read'] and ' ' not in chk['clock_read']
print(f"heartbeat written: epoch={chk['heartbeat_epoch_utc']} (int OK) clock={chk['clock_read']}")
