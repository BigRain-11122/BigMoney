import io

src = io.open('results/runnable_pool.json', encoding='utf-8', newline='').read()
for sid in ('fund-divlowvol-p1-nulls-0of1', 'fund-divlowvol-p1-sens-0of1',
            'fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1',
            'fund-quality-p1-sens-0of1', 'fund-value-p1-sens-0of1'):
    i = src.find('"'+sid+'"')
    if i < 0:
        print(sid, 'NOT FOUND in local shared face'); continue
    seg = src[i:i+420]
    owner = 'NO-OWNER-PAIR' if '"owner"' not in seg else 'HAS OWNER'
    print('---', sid, '|', owner)
    print(seg[:420])
    print()

fsrc = io.open('results/crash_fuse.json', encoding='utf-8', newline='').read()
for key in ('fund_quality_p1.py|run,--sensitivity', 'fund_value_p1.py|run,--sensitivity',
            'fund_divlowvol_p1.py|run,--nulls', 'fund_divlowvol_p1.py|run,--sensitivity'):
    i = fsrc.find(key)
    print('FUSE', key, 'present' if i >= 0 else 'ABSENT')
    if i >= 0:
        print(fsrc[i-30:i+320])

# CRLF check around a shard block
j = src.find('"owner": "bm-a"')
print('bytes around first bm-a owner:', repr(src[j-90:j+70]))
