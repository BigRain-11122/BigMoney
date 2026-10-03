import json, datetime

now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')

# round report addendum
rp = 'round_reports-bm-a.md'
b = open(rp, 'rb').read()
eol = b'\r\n' if b.count(b'\r\n') > (b.count(b'\n') - b.count(b'\r\n')) else b'\n'
if not b.endswith(eol):
    b += eol
add = (
    'r657 addendum (' + iso + '): closeout commit 2c0c6dcf5 delivered via origin machine/bm-a-r657 (second main-push '
    'rejection in active treadmill race -> D-20260925-01iii fallback; ls-remote self-proof 2c0c6dcf5). main integration '
    '= next round S0 FIRST merge origin/machine/bm-a-r657 THEN origin/main. rebase surgery: 16 UU regenerable faces '
    'origin-wins per r440 two-bucket law (my owned bookkeeping faces applied clean); git rebase --continue false-'
    'rejection (r305 family, all staged + ls-files -u empty) healed via manual commit --no-edit + rebase --quit + '
    'branch -f + symbolic-ref (r624 law). origin/main 1 ahead at close; 3 satengine treadmill faces left for next '
    'round absorb. 本地未达 origin commit 数（main 口径）=2（closeout+本 addendum·经 machine 分支已达·下轮 S0 吸收）'
).encode('utf-8')
b += add + eol
open(rp, 'wb').write(b)
print('report addendum appended')

# state next pointer
p = 'state-bm-a.json'
s = json.load(open(p, encoding='utf-8'))
s['next'] = ('S0 FIRST merge origin/machine/bm-a-r657 (r657 closeout 2c0c6dcf5 delivered via machine branch after '
             'second main push rejection) THEN origin/main; then theme-ring R5 methodology chapter (three sentences '
             'per Sec.8: famous-theme hold-first / wave-ride beats random / constants unresolved) to close T-165; '
             'fund trio NULLS bm-b ETA 10-05..09 -> judged finalize (rehearsal ready); 10-31 monthly exam prep')
json.dump(s, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state next pointer updated')
