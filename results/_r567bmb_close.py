import json, time, os, shutil

now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# --- state.json (bm-b uses state.json) ---
state = json.load(open('state.json', encoding='utf-8'))
state['round_no'] = 567
state['note'] = ("r567: W65 12/12 burn complete + tail shards 9/10/11 delivered (ride ad6569e78->918957e0e rebased); "
                 "W66 same-window draft YIELDED zero-cost to bm-c r359 b35b0ee35 (bands bit-identical = r530 12th "
                 "deterministic cross-validation; FIX-A origin-blob freshness abort caught it BEFORE any local edit: "
                 "zero burns/ledger/seat-MSG = pure-draft yield, evidence scripts archived); W67 FREEZE delivered "
                 "551ced1b1 (FIFTY-SIXTH engine wave, bm-b 21st owned, A 177_004..179_003 / B 50_201..50_400 both "
                 "arithmetic no-skip, seat MSG-20261002-0945-bmb, ADMIT receipt _r567bmb_w67_band_gate.py, selftest "
                 "W2..W67 PASS, banned gate ADMIT) + ignition verified 3 shards landed + queue 9 self-continuing; "
                 "next = W67 burn watch (12/12) + W65 finalize one-pass AFTER W64 bm-a lands (chain order W64->W65->"
                 "W66->W67, r538 one-pass law, FAIL-CLOSED r307)")
state['last_round_at'] = epoch
state['last_round_ts'] = now_iso
state['ts'] = now_iso
state['updated'] = ("r567 bm-b: W66 zero-cost yield (FIX-A live-fire catch) + W67 freeze delivered + ignition "
                    "verified; W65 finalize watch on W64")
state['updated_at'] = now_iso
# last_decisions_sha unchanged (verified MATCH this round via raw-bytes python)
json.dump(state, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json round 567 written')

# --- heartbeat fleet/machines/bm-b.json ---
hb_path = 'fleet/machines/bm-b.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now_iso
hb['current_task'] = ("W67 burn in flight via engine tick (12 shards, ignition verified 3 landed); "
                      "r567 W66 zero-cost yield + W67 freeze delivered; W65 finalize watch on W64 bm-a")
hb['round_no'] = 567
hb['round_no_label'] = 'r567'
import psutil
hb['cpu_util_pct'] = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
hb['free_ram_gb'] = round(vm.available / (1024**3), 1)
hb['idle_ram_gb'] = hb['free_ram_gb']
hb['ram_free_gb'] = hb['free_ram_gb']
hb['verdict'] = 'loaded_ok'
json.dump(hb, open(hb_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178)'
print('heartbeat written, epoch int-verified:', chk['heartbeat_epoch_utc'])

# --- move consumed MSG-0919 to processed ---
src = 'fleet/inbox/MSG-20261002-0919-bmb-w65-yield-w65-seat.md'
if os.path.exists(src):
    shutil.move(src, 'fleet/inbox/processed/')
    print('MSG-0919 moved to processed (consumed by all parties: author served + bm-c r359 consumed)')
else:
    print('MSG-0919 already moved')
