"""r629 bm-a closeout: state + heartbeat updates (epoch int law, T-format clock)."""
import json, time
from datetime import datetime, timezone, timedelta

NOW = datetime.now()
CST = timezone(timedelta(hours=8))
now_iso = NOW.astimezone(CST).isoformat(timespec='seconds')
epoch = int(time.time())

# --- state-bm-a.json: round_no 628 -> 629 + round fields ---
SP = 'state-bm-a.json'
s = json.load(open(SP, encoding='utf-8'))
assert s['round_no'] == 628, s['round_no']
s['round_no'] = 629
s['round'] = 'r629'
s['last_round'] = 628
s['last_round_at'] = now_iso
s['last_round_ts'] = now_iso
s['current_task'] = ('r629: divlowvol pool/fuse hygiene per division (SENS fuse tombstone '
                      '+ NULLS keep-block + ghost-claim release x4 faces + host_gates) + '
                      'QUALITY-SENS 500/500 acceptance ALL PASS + DIVLOWVOL-SENS re-burn '
                      'in flight (25w BelowNormal) + T-156 quarantine cleanup 2.02GB')
s['updated'] = now_iso
s['did'] = ('r629: (1) S0 churn absorb + rebase + push (behind-10 wave absorbed); (2) orders '
            '151/151 diff-set 0, D-19 decisions hash MATCH via C: group tree fresh fetch '
            '(K: mount absent this window, honest note); (3) smoke 47/47; (4) satengine alive '
            'rc0 idle-legal; (5) divlowvol hygiene: SENS fuse tombstoned data_fixed (T-156 '
            'four-point + QUALITY-SENS clean-burn precedent), NULLS keep-block note (bm-b '
            'rightful burner in flight r617-r620), ghost-claims released x4 faces raw-text, '
            'host_gates p1c x2 entries; daemon claim_lost_yield root-caused (pre-push origin '
            'invisibility) -> after push claimed+launched DIVLOWVOL-SENS 15:41:47/56; '
            '(6) QUALITY-SENS acceptance ALL PASS (500 rows k0-499 unique contiguous, DONE '
            '1256.3s 25 workers, claim closed 15:15:12, origin blob, T-156 four-point ptr); '
            '(7) S6 29 legs rc0 (paper family skipped: golden week no new bar, cutoff 09-30; '
            'dualrun streak 8; audit FLAG cap_violation 32w BelowNormal honest; ORANGE_COOL '
            '0 activated; REPORT/LIVE twins); (8) T-156 quarantine+incoming deleted 2.02GB '
            '(first clean burn landed = spec authorization); croc recv logs zero-residue; '
            '(9) pit-pool r629 direct-write entry (trailing-comma raw-text pit)')
s['verify'] = ('smoke 47/47; S6 29 legs rc0; pool 4 faces parse+owner None (divlowvol NULLS/SENS '
               'released) with trails; fuse tombstone live-read survived daemon ticks; origin '
               'pool SENS claim bm-a@15:41:47; sens_acceptance.json ALL_PASS; attrition CLEAN; '
               'claws match canon; schtasks both armed (pin :8 / watchdog)')
s['next'] = ('DIVLOWVOL-SENS burn completion verify (~16:05, daemon harvest flip + claim close) '
             '-> fund family finalize waits bm-b nulls 2000-draw x3 (ETA 10-06/10-08); '
             'moneyflow MSG-1452 GM ruling pending (A lane bm-b / B sina IC prereg)')
json.dump(s, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(SP, encoding='utf-8'))
assert chk['round_no'] == 629
print('[state] round_no 629, current_task updated')

# --- heartbeat fleet/machines/bm-a.json ---
HB = 'fleet/machines/bm-a.json'
h = json.load(open(HB, encoding='utf-8'))
h['last_seen'] = now_iso
h['current_task'] = s['current_task']
h['task'] = ('r629: DIVLOWVOL-SENS re-burn in flight (claimed 15:41:47, 25w BelowNormal, '
             'resume-skipped 7); QUALITY-SENS acceptance ALL PASS; divlowvol pool hygiene x4 faces')
h['round_no'] = 629
h['round'] = 'r629'
h['clock_read'] = now_iso
h['heartbeat_epoch_utc'] = epoch
h['verdict'] = ('healthy: DIVLOWVOL-SENS burn in flight (32w plan, BelowNormal); QUALITY-SENS '
                '500/500 accepted; divlowvol ghost-claims released; quarantine cleaned 2.02GB')
json.dump(h, open(HB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk2 = json.load(open(HB, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk2['clock_read'] and '+' in chk2['clock_read']
print('[heartbeat] epoch int verified:', chk2['heartbeat_epoch_utc'], '| clock:', chk2['clock_read'])
