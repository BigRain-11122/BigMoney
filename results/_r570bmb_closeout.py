# -*- coding: utf-8 -*-
"""r570 bm-b closeout: state round_no + heartbeat (epoch int, T-clock) + report line."""
import json
import time
import datetime

STATE = 'state.json'
HB = 'fleet/machines/bm-b.json'

now_local = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

d = json.load(open(STATE, encoding='utf-8'))
d['round_no'] = 570
json.dump(d, open(STATE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

h = json.load(open(HB, encoding='utf-8'))
h['last_seen'] = now_local
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now_local
h['current_task'] = ('W70 finalize landed (chain head 518,548) + W72 freeze+burn 12/12 '
                     '(finalize waits bm-c W71) + pool_core_samples corruption repair; '
                     'next bm-b wave W74 (bm-a W73 in flight)')
h['round_no'] = 570
h['round_no_label'] = 'r570'
h['verdict'] = ('healthy: W70 finalize one-pass landed (head 518,548, K=151,920, S5 4/4), '
                'W72 full lifecycle frozen+burned 12/12 (finalize chain-pending W71 bm-c), '
                'pool_core_samples blob-corruption cured fleet-wide, S6 all-green after repair')
json.dump(h, open(HB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

ck = json.load(open(HB, encoding='utf-8'))
assert isinstance(ck['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert 'T' in ck['clock_read'] and ' ' not in ck['clock_read'], 'clock T-separator law (R262)'
print(f'state round_no=570; heartbeat epoch={ck["heartbeat_epoch_utc"]} (int ok) '
      f'clock={ck["clock_read"]} (T ok)')
