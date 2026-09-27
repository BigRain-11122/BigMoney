import json, io, sys, time, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

now = datetime.datetime.now()
ts_hm = now.strftime('%H:%M')
ts_hms = now.strftime('%H:%M:%S')
clock_read = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
epoch = int(time.time())

# state-bm-a.json
sp = r'state-bm-a.json'
st = json.load(io.open(sp, encoding='utf-8'))
st['did'] = st['did'] + ' + PASS-3 collision (bm-c r93 chain 17:57-58 landed mid-push): retry allowance exhausted -> escape valve origin machine/bm-a-r341 @9a65a94a per D-20260925-01iii + r334bmb/r93bmc precedent; pass-2 resolve complete on branch (13 snapshot take-ours / compute_audit union 229 / CODELY keep-set 5057B + archive 26th renumber r176)'
st['next'] = ('(1) NEXT ROUND FIRST DUTY = fold-landing: git pull --rebase onto origin/main (bm-c r93 chain + any new), resolve third wave (CODELY trim vs bm-c 9995B face / autofill identity-key variants / compute_audit), land machine/bm-a-r341 content, THEN push main; '
              '(2) T-91 s3 auto-fires Mon 09-28 09:15 first-marks; (3) W2-A bm-b finalize window ~18:10-21:10 + UNC follow-up per sec.9.3; (4) bm-b dual-evidence watch continues; (5) next 5x = round 345')
st['last_round_at'] = '2026-09-27 ' + ts_hm
st['current_task'] = 'r341 done on machine/bm-a-r341 (escape valve, 3-machine storm); fold-landing next round first duty; T-91 armed Mon 09:15'
with open(sp, 'wb') as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1).encode('utf-8'))

# round report: append escape-valve note to r341 line
rp = r'logs\iteration-loop\round_reports-bm-a.md'
raw = open(rp, 'rb').read()
nl = b'\r\n' if b'\r\n' in raw else b'\n'
txt = raw.decode('utf-8')
addition = ('; (K) 三推三拒（bm-b r333-336 链+bm-c r93 链 17:57-58 连续落）->重试额度尽->D-20260925-01iii 逃生舱 origin machine/bm-a-r341@9a65a94a 推成（r334bmb/r93bmc 同窗先例）；'
            'pass-2 解已全在支（13 快照 take-ours/compute_audit 229 union/CODELY 5057B+archive 26 批 r176 让号）；下轮首务=折降落支内容')
lines = txt.split(nl.decode('utf-8'))
assert 'R341 bm-a' in (lines[-2] if lines[-1] == '' else lines[-1]), 'r341 line not tail'
if lines[-1] == '':
    lines[-2] = lines[-2] + addition
else:
    lines[-1] = lines[-1] + addition
open(rp, 'wb').write((nl.decode('utf-8').join(lines)).encode('utf-8'))

# heartbeat
hp = r'fleet\machines\bm-a.json'
hb = json.load(io.open(hp, encoding='utf-8'))
hb['last_seen'] = '2026-09-27 ' + ts_hms
hb['current_task'] = 'r341 done on machine/bm-a-r341 escape valve (3-machine push storm, 3 rejections); next round first duty = fold-landing onto origin/main; T-91 armed Mon 09-28 09:15'
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock_read
hb['round_no'] = 341
hb['task'] = 'escape-valve branch machine/bm-a-r341 landed; fold-landing next round; board 0 open; W2-A bm-b in-flight'
with open(hp, 'wb') as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1).encode('utf-8'))
chk = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int) and 'T' in chk['clock_read'][:11]
print('closeout files written', clock_read)
