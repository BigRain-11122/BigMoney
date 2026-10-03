"""r622 bm-a ghost re-strip (post-union resurrection fix, r616 full-lane law).

Union non-null-first resurrected bm-a claim pairs on shared; R31
take-owner on bm-c lane discarded the earlier strips. Re-strip with
block-bounded extraction (no window-overflow false positives).
"""
import io, json

REL_NOTE = (' | rel-bm-a-r622 11:47: burned on off-caliber cache (40/40 '
            'overlap keys diverged vs bm-b basis), burn killed, rows '
            'discarded, claim released -- bm-b burn is canonical per '
            'MSG-1132/MSG-1155; keep-block note on crash_fuse')

def shard_block(src, sid):
    i = src.find('"key": "' + sid + '"')
    if i < 0:
        return None
    start = src.rfind('{', 0, i)
    j = src.find('\r\n    }', i)
    return start, j + len('\r\n    }') if j >= 0 else None

def strip_face(fp, sids):
    src = io.open(fp, encoding='utf-8', newline='').read()
    changed = 0
    for sid in sids:
        while True:
            b = shard_block(src, sid)
            if not b:
                break
            blk = src[b[0]:b[1]]
            if '"owner": "bm-a"' not in blk:
                break
            n0 = blk.find('"note": "')
            nc = blk.find('",\r\n', n0)
            assert nc > 0, (fp, sid, 'note-end')
            new_blk = (blk[:nc] + (REL_NOTE if 'rel-bm-a-r622' not in blk
                                    else '') + '"\r\n' +
                       blk[blk.find('\r\n    }'):])
            src = src[:b[0]] + new_blk + src[b[1]:]
            changed += 1
            break
    if changed:
        json.loads(src)
        io.open(fp, 'w', encoding='utf-8', newline='').write(src)
    print(fp, 'stripped', changed)

strip_face('results/runnable_pool.json',
           ['fund-value-p1-nulls-0of1', 'fund-quality-p1-nulls-0of1'])
strip_face('results/runnable_pool.bm-b.json', ['fund-value-p1-nulls-0of1'])
strip_face('results/runnable_pool.bm-c.json',
           ['fund-value-p1-nulls-0of1', 'fund-quality-p1-nulls-0of1',
            'fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1'])

# block-bounded verification scan (no window overflow)
print('--- verify ---')
for fp in ('results/runnable_pool.json', 'results/runnable_pool.bm-a.json',
           'results/runnable_pool.bm-b.json', 'results/runnable_pool.bm-c.json'):
    src = io.open(fp, encoding='utf-8', newline='').read()
    for sid, nm in (('fund-value-p1-nulls-0of1', 'value-nulls'),
                    ('fund-quality-p1-nulls-0of1', 'quality-nulls'),
                    ('fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1', 'x2'),
                    ('fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1', 'x1')):
        b = shard_block(src, sid)
        blk = src[b[0]:b[1]] if b else ''
        o = blk.find('"owner": "')
        ow = blk[o:blk.find('"', o+9)] if o >= 0 else 'NO-OWNER'
        print(f'{fp} {nm}: {ow!r} bm-a={"bm-a" in ow}')
