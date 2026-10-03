import io

SHARDS = [('fund-value-p1-nulls-0of1', 'value-nulls'),
          ('fund-quality-p1-nulls-0of1', 'quality-nulls'),
          ('fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1', 'x2'),
          ('fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1', 'x1')]

for fp in ('results/runnable_pool.json', 'results/runnable_pool.bm-a.json',
           'results/runnable_pool.bm-b.json', 'results/runnable_pool.bm-c.json'):
    src = io.open(fp, encoding='utf-8', newline='').read()
    print('=====', fp)
    for sid, nm in SHARDS:
        i = src.find('"'+sid+'"')
        if i < 0:
            print(' ', nm, 'NOT FOUND'); continue
        seg = src[i:i+700]
        has_bm_a = '"owner": "bm-a"' in seg
        rel_note = 'rel-bm-a-r622' in seg
        # extract owner line
        o = seg.find('"owner"')
        oe = seg.find('"', o+9) if o >= 0 else -1
        ow = seg[o:seg.find('"', o+9)+1] if o >= 0 else 'NO-OWNER'
        print(f'  {nm}: owner={ow!r} bm-a-ghost={has_bm_a} rel-note={rel_note}')
