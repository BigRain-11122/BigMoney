# -*- coding: utf-8 -*-
# r1005 bm-b heartbeat closeout (fresh-read-modify-write, preserve tool-written orders_ack).
import json, time, os

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
HP = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
NOW_ISO = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())

h = json.load(open(HP, encoding='utf-8'))

h['machine_id'] = 'bm-b'
h['last_seen'] = NOW_ISO
h['clock_read'] = NOW_ISO
h['ts'] = NOW_ISO
h['heartbeat_epoch_utc'] = EPOCH
h['round_no'] = 1005
h['round'] = 1005
h['task'] = 'r1005: closeout (estate delivered + canon installed + CODELY hotcold + O-2315 closed)'
h['current_task'] = h['task']
h['did'] = ('r1005: estate delivered (origin 9877424b4f, bm-a r1054 criterion met, N=0) + O-0948 v2 spawning-line receipt leg closed '
            '+ memory-curator canon installed (3-face SHA256 equal) + D-19 dual advance (dec 0ad85a30/ord a62af296) + D-20261017-07 ack '
            '+ CODELY.md hotcold 21,556->8,512B (14 rows verbatim migrated) + O-2315 bm-b receipt closed (late-ack honest) '
            '+ orders_ack dual-face writer first use 102/102 + S6 43 rc0 + idle RED consumed --worked')
h['verdict'] = ('GREEN: estate delivered origin=9877424b4f + canon installed + CODELY.md 8,512B<=10KB + D-19 dual advance + O-2315 closed '
                '+ smoke rc0 + orphan 7/0 + watermark red=false; leftovers = bm-a pickup receipts pending (MSG-0845/1035/1137) '
                '+ O-0948 24h window + MemoryBudgetGate first-fire check')
h['last_action'] = 'r1005: estate push delivered 9877424b4f + canon install + CODELY hotcold + D-19 dual advance + O-2315 receipt'
h['last_action_at'] = NOW_ISO
h['latest_artifact'] = ('origin/main=9877424b4f estate landed + memory-curator canon installed (blob 7344265215) '
                        '+ CODELY.md 8,512B + MSG-20261018-1137-bmb-canon-installed.md')
h['next'] = ('r1006: 1) O-0948 24h observation window 2) bm-a pickup receipts MSG-0845/1035/1137 3) drama IndexTTS EP001-003 harvest '
             '4) MemoryBudgetGate first-fire check 5) D-19 fresh delta 6) pool starved honest face awaiting restock')
h['note'] = ('r1005: v2 first-carrier window (spawning line hard-cap 240/silence 25 verbatim quoted in O-0948 receipt); stale-main dual-line '
             'topology healed (81ffe58dbe orphan recoverable); push-hang disposal order proven (ls-remote probe -> fetch recheck -> replay -> delivered); '
             'memory-curator canon supersedes fbffe9d1 (group close-out batch, newer-wins); O-2315 late receipt closed honestly.')
h['idle_rounds'] = 0
h['agenda_starved'] = False

try:
    import psutil
    vm = psutil.virtual_memory()
    h['free_ram_gb'] = round(vm.available / (1024 ** 3), 1)
    h['cpu_load_pct'] = round(psutil.cpu_percent(interval=0.5), 1)
    n = 0
    for p in psutil.process_iter(['name']):
        try:
            if (p.info.get('name') or '').lower().startswith('codely'):
                n += 1
        except Exception:
            pass
    h['codely_live_count'] = n
except Exception:
    pass

with open(HP, 'w', encoding='utf-8') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# post-write type self-check (R170/R178 law)
h2 = json.load(open(HP, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch not int'
assert isinstance(h2['idle_rounds'], int), 'idle_rounds not int'
assert isinstance(h2['agenda_starved'], bool), 'agenda_starved not bool'
assert 'T' in h2['clock_read'], 'clock_read missing T separator'
assert len(h2['orders_ack']) == 102, 'orders_ack expected 102, got %d' % len(h2['orders_ack'])
print('heartbeat OK epoch=%d idle_rounds=%d ack=%d ram=%s cpu=%s codely=%s' % (
    h2['heartbeat_epoch_utc'], h2['idle_rounds'], len(h2['orders_ack']),
    h2.get('free_ram_gb'), h2.get('cpu_load_pct'), h2.get('codely_live_count')))
