# -*- coding: utf-8 -*-
# r788 bm-a S5/S7 bookkeeping: state round 786->788 (dead-r787 absorb), heartbeat refresh,
# round-report r787 recovery line + r788 main line appended via this script (multi-writer
# append-only law: single-file fresh-read-modify-write, python only).
import json, time, datetime, os, psutil

now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S%z')  # T-separated per F5 law
epoch = int(time.time())

# ---- state file (root state-bm-a.json) ----
sp = 'state-bm-a.json'
s = json.load(open(sp, encoding='utf-8'))
s['round_no'] = 788
s['loop_round'] = 788
s['last_round'] = 'r788'
s['last_round_at'] = iso
s['last_round_ts'] = iso
s['ts'] = iso
s['updated'] = iso
s['last_seen'] = iso
s['last_run'] = iso
s['heartbeat_epoch_utc'] = epoch
s['last_action'] = ('r788: W162 finalize one-pass (ledger 759,612->761,812, K=354,320, skill 1.1829->1.1828) '
                    '+ dead-r787 S7 tail absorb (T-173 ticket done-flip 17:45 + zero r787 report line)')
s['current_task'] = 'W162 finalize landed; next = W163 seat+freeze per never-dry engine line'
s['did'] = ('W162 finalize one-pass rc0 (r708 double-probe GREEN preflight, 12/12 shards consumed, '
            'K=354,320==prereg projection, 4/4 s5 keys pass, s7/s8 backfilled, n1+pf selftest green) '
            '+ S6 38/38 rc0 101.1s + attrition guard CLEAN + T-173 dead-session tail committed')
s['verify'] = ('ledger_head()=761,812 file=n1_w162_results.json; preflight receipt '
               'results/_r788bma_w162_preflight.json GREEN; S6 facts results/_r788bma_s6_facts.json')
s['next'] = ('(1) W163 seat+freeze+ignition (staircase 22nd anticipated: naive A 373_204..375_203 refused by '
             'W162 B band 373_204..373_403, hops=1 expected; own-A reservation leg2 for B) '
             '(2) 10-07 12:00 D-06 closeout window (3) 5x=r790 HANDOVER check')
s['notes'] = 'dead-r787 session absorbed: freeze+ignition landed on origin 55e45ce48, report line added by r788'
json.dump(s, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-a.json ----
hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
try:
    g = [x for x in psutil.process_iter(['name']) if 'python' in (x.info['name'] or '')]
except Exception:
    g = []
h['machine_id'] = 'bm-a'
h['clock_read'] = iso
h['ts'] = iso
h['last_seen'] = iso
h['last_heartbeat_epoch_utc'] = h.get('heartbeat_epoch_utc')
h['heartbeat_epoch_utc'] = epoch
h['cpu_pct'] = cpu
h['cpu_util_pct'] = cpu
h['cpu_load_pct'] = cpu
h['free_ram_gb'] = round(vm.available / 1024**3, 1)
h['ram_free_gb'] = round(vm.available / 1024**3, 1)
h['idle_ram_gb'] = round(vm.available / 1024**3, 1)
h['health'] = 'ok'
h['last_round'] = 'r788'
h['last_action'] = s['last_action']
h['now_active'] = 'W162 finalize landed (ledger 761,812; chain W1..W162 fully closed, zero in-flight seats)'
h['verdict'] = 'W162 finalize one-pass rc0; S6 38/38 green; smoke 48/48; watermark green'
h['latest_artifact'] = 'results/perpetual_faces/n1_w162_results.json + research/PERPETUAL_N1_W162_PREREG.md s7/s8 (' + iso + ')'
# orders_ack: no new orders this round; keep existing set verbatim
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# epoch int self-check (R170/R178 law)
h2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in h2['clock_read'][10], 'clock_read must be T-separated'
print('state+heartbeat written; epoch int OK; clock T OK; cpu=%.1f free_ram=%.1f' % (cpu, vm.available/1024**3))
