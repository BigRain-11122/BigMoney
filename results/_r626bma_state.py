import json, time
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
epoch = int(time.time())

# state file
p = 'state-bm-a.json'
d = json.load(open(p, encoding='utf-8'))
d['round_no'] = 626
d['round'] = 580
d['loop_round'] = 580
d['did'] = ('S0 pull --rebase (tick commit first: 6 runtime-state files r109 targeted add; 5 origin commits absorbed, '
            'rebase clean) + S0.5 orders 151/151 zero-unacked + D-19 python raw-bytes hash UNCHANGED zero-consume + '
            'smoke 47/47 + satengine alive (queue 0 idle since 05:40 honest) + T-156 kill-advice MSG-1410 sent '
            '(receiver pid 67588 camping 31+min no-pairing, MSG-1214 sec.4 trigger crossed, three-check evidence) + '
            'S6 29 legs rc0 (ZERO-DRIFT streak 5, moneyflow detached refresh spawned = 30min self-heal engaged, AH '
            'refresh spawned, LIVE/REPORT regenerated) + engine-idle root-cause diagnosed (perpetual generator '
            'starve-verdict false-negative: fuse-gated ready entries counted as live supply) + T-145 gate-state '
            'progress note + S7 4/4 + attrition CLEAN')
d['verify'] = ('smoke 47/47; S6 29 legs rc0 (dualrun ZERO-DRIFT streak 5 @362 entries; audit rc0 py 0.2% board-clear '
               'legal idle; regime ORANGE shadow; clockcall ORANGE_COOL 4 sleeves 0 activated); T-156 receiver '
               'evidence: netstat ESTABLISHED 10.86.98.91:51921->5.78.134.116:9009 pid 67588 banner waiting-for-sender '
               'crocv 11.5.3; attrition guard CLEAN rc0; loop pin 8 no-op + watchdog + dual claws reinstalled')
d['next'] = ('T-156: bm-b kill+re-fire per MSG-1410 (same code within ~14:50 window else fresh code MSG -> re-arm '
             'receiver) -> on bytes: manifest verify vs T-2026-10-03-156-sender.json (13 files/1,836,548,747B) -> '
             'quarantine swap -> four-point verify (vwap_688_check/hashes/688 magnitude/2020-12 cohort) -> clear '
             'divlowvol 4 fuse sigs -> re-claim QUALITY-SENS + 90-row nulls redo; W14 zero-touch pending GM '
             'dual-ruling (MSG-0436); N2-W15 runner deferred same ruling; NULLS 2000-draw ETA 10-06/10-08 bm-b')
d['current_task'] = ('r626: T-156 kill-advice fired (31+min no pairing, three-check law); all bm-a furnace legs '
                     'transfer-gated; engine idle diagnosed = generator starve-verdict counts fuse-gated entries '
                     'as live supply (observation recorded T-145 note, no unilateral generator semantics change); '
                     'S6 29 legs rc0')
d['last_round_at'] = now
d['updated'] = now
d['last_round'] = 'r626 bm-a'
d['last_round_ts'] = now
d['last_seen'] = now
d['last_run'] = now.replace('T', ' ')
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# heartbeat
hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
h['last_seen'] = now
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now
h['verdict'] = ('py_low_board_clear (legal idle: FUND-* furnace legs transfer-gated on T-156 p1c swap; divlowvol '
                'fuse keep-blocks live; kill-advice MSG-1410 sent awaiting bm-b re-fire; W14 parked GM ruling)')
h['current'] = ('T-156 kill-advice sent (receiver camping pid 67588); S6 29 legs rc0; engine idle root-cause '
                'diagnosed (generator starve false-negative)')
assert isinstance(h['heartbeat_epoch_utc'], int), 'epoch must be int'
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state+heartbeat written; round_no', d['round_no'], 'epoch', epoch, 'clock', now)
