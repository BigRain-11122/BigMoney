import io, sys

faces = ['results/runnable_pool.json', 'results/runnable_pool.bm-a.json',
         'results/runnable_pool.bm-b.json', 'results/runnable_pool.bm-c.json']
shards = ['fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1',
          'fund-value-p1-nulls-0of1', 'fund-quality-p1-nulls-0of1']

for fp in faces:
    src = io.open(fp, encoding='utf-8', newline='').read()
    print('=====', fp)
    for sid in shards:
        i = src.find('"'+sid+'"')
        if i < 0:
            print(' ', sid, 'NOT FOUND'); continue
        j = src.find('"shards"', 0, i)  # not needed; print shard block
        print(' ---', sid)
        print(src[i-30:i+560])
    print()
