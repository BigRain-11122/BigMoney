# -*- coding: utf-8 -*-
import json, time, datetime
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())
# --- state heal 839->841 ---
p = 'state-bm-a.json'
d = json.load(open(p, encoding='utf-8'))
assert d['round_no'] == 839, 'unexpected state round %s' % d['round_no']
d['round_no'] = 841
d['round'] = 841
d['loop_round'] = 'r841'
d['last_round'] = 'r841'
d['last_round_at'] = now
d['last_round_ts'] = now
d['last_run'] = now
d['updated'] = now
d['ts'] = now
d['clock_read'] = now
d['last_heartbeat_epoch_utc'] = epoch
d['current_task'] = 'W177 seat chain landed (probe rc0 ADMIT + seat MSG published=reserved, push 780a0cd30); next = W177 prereg build + freeze per two-window law r797/r799'
d['did'] = 'r841: W177 pre-seat probe on post-W176 universe (re-derive MANDATORY) rc0 ADMIT + seat MSG 3-item payload push-delivered (rebase 1-UU orphan-probe ts-resolve + r835 three-step heal + r624 branch-f reattach); S6 37/37 rc0; S7 quartet green; state heal 839->841 (r840 state write lost in postscript surgery, report+commits real)'
d['last_action'] = 'W177 seat: A 404_204..406_203 hops=1 (staircase 37th E36) / B 406_204..406_403 hops=1 own-A reservation; conflicts=0, origin-vacancy held; ledger anchor 793,105 machine-read'
d['next'] = 'W177 prereg build next window (buildgen r833 bloodline, facts=probe receipt + seat 780a0cd30) then freeze 5-face window (r797/r799 two-window law) + 10-08 market-reopen data chain re-arm (first trading day after golden week), window <=48h'
d['now_active'] = 'W177 seat published=reserved r841; prereg+freeze next windows'
d['verify'] = 'probe 5-leg machine-derive all-PASS; seat push delivered be03d92d6..48810198a behind-0/ahead-0 fetch+rev-list; smoke 48/48; S6 37/37 rc0; dualrun ZERO-DRIFT streak 51; attrition CLEAN x4; quartet green; orphan face=0'
d['latest_artifact'] = 'fleet/inbox/processed/MSG-2026-10-07-2031-bma-w177-seat.md + results/_r841bma_w177_probe_receipt.json @2026-10-07T20:31+08:00'
notes = d.get('notes', '')
heal_note = (' r841: state heal 839->841 -- r840 session completed (report line + 3 commits on origin) '
             'but its state write was lost in the 20:24 postscript push-race rebase surgery '
             '(r624 branch-f reattach restored the r839-time blob); sequence honest per round_reports r840 line.')
d['notes'] = notes + heal_note if notes else heal_note.strip()
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state healed -> r841 @', now)
# --- heartbeat ---
h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
h['last_seen'] = now
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now
h['ts'] = now
h['current_task'] = 'W177 seat chain landed; prereg+freeze next windows (two-window law)'
h['cpu_cores'] = 32
h['verdict'] = 'green'
json.dump(h, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
print('heartbeat updated, epoch int + T-sep self-check PASS:', epoch)
