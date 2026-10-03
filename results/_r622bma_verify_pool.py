import io

src = io.open('results/runnable_pool.json', encoding='utf-8', newline='').read()
for sid in ('fund-value-p1-nulls-0of1', 'fund-quality-p1-nulls-0of1',
            'fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1',
            'fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1',
            'fund-divlowvol-p1-nulls-0of1', 'fund-divlowvol-p1-sens-0of1'):
    i = src.find('"'+sid+'"')
    if i < 0:
        print(sid, 'NOT FOUND'); continue
    seg = src[i:i+680]
    print('=====', sid)
    print(seg)
    print()
