import json, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# state-bm-a.json: did/verify reflect final post-resolve facts
sp = r'state-bm-a.json'
st = json.load(io.open(sp, encoding='utf-8'))
st['did'] = st['did'].replace(
    'new pitlaw appended CODELY 10141B<10KB',
    'new pitlaw appended (CODELY union 13769B >10KB -> 25th-batch in-window archival SAME round, final 4581B<10KB)'
).replace(
    'S6 33/33 rc=0 Sunday no-op family (no new bar cutoff 09-24)',
    'S6 33/33 rc=0 Sunday no-op family (no new bar cutoff 09-24) + push-reject rebase 4-UU canonical resolve (bigmoney-conflict-resolve skill: regime take-new 17:50:43 / autofill launches union cap50 + last_tick take-new 17:50:02 / compute_audit history union 227+201->228 zero-loss + CODELY memory-union direct-concat then fold 34 rows to archive 25th batch, zero-loss multiset assert)'
)
st['verify'] = st['verify'] + ' + resolver results/_r341bma_resolve.py all-assert pass (4 files, zero-loss, parse-verify)'
st['current_task'] = 'r341 done: maintenance + push-collision resolve + 25th-batch archival; T-91 armed Mon 09:15'
with open(sp, 'wb') as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1).encode('utf-8'))

# round report: append resolution note to the r341 line (CRLF file)
rp = r'logs\iteration-loop\round_reports-bm-a.md'
raw = open(rp, 'rb').read()
crlf = b'\r\n' in raw
nl = b'\r\n' if crlf else b'\n'
txt = raw.decode('utf-8')
addition = ('; (J) push 拒->pull --rebase 撞 bm-b r333-335+tick keepalive=4 UU->bigmoney-conflict-resolve 正典解'
            '(regime take-new 17:50:43/autofill union cap50+last_tick take-new/compute_audit union 228 零丢失/'
            'CODELY memory-union 53 行直拼->超线当窗 25 批整编 34 行外迁 archive·multiset 零丢失断言过·终态 4581B<10KB)')
# append to the LAST line (the r341 line I appended this round)
lines = txt.split(nl.decode('utf-8'))
# find last non-empty line and verify it is the r341 line
assert 'R341 bm-a' in lines[-1] if lines[-1] else 'R341 bm-a' in lines[-2], 'r341 line not at tail'
if lines[-1] == '':
    lines[-2] = lines[-2] + addition
else:
    lines[-1] = lines[-1] + addition
open(rp, 'wb').write((nl.decode('utf-8').join(lines)).encode('utf-8'))
print('state + round report updated')
