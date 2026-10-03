"""r622 bm-a ghost re-strip v2 (EOL-adaptive block extraction)."""
import io, json

REL_NOTE = (' | rel-bm-a-r622 11:47: burned on off-caliber cache (40/40 '
            'overlap keys diverged vs bm-b basis), burn killed, rows '
            'discarded, claim released -- bm-b burn is canonical per '
            'MSG-1132/MSG-1155; keep-block note on crash_fuse')

def eol_of(src):
    return '\r\n' if src.count('\r\n') >= src.count('\n    }') else '\n'

def shard_block(src, sid, eol):
    i = src.find('"key": "' + sid + '"')
    if i < 0:
        return None
    start = src.rfind('{', 0, i)
    j = src.find(eol + '    }', i)
    return (start, j + len(eol) + len('    }')) if j >= 0 else None

def strip_face(fp, sids):
    src = io.open(fp, encoding='utf-8', newline='').read()
    eol = eol_of(src)
    changed = 0
    for sid in sids:
        while True:
            b = shard_block(src, sid, eol)
            if not b:
                break
            blk = src[b[0]:b[1]]
            if '"owner": "bm-a"' not in blk:
                break
            n0 = blk.find('"note": "')
            nc = blk.find('",' + eol, n0)
            assert nc > 0, (fp, sid, 'note-end')
            add = '' if 'rel-bm-a-r622' in blk else REL_NOTE
            new_blk = (blk[:nc] + add + '"' + eol +
                       blk[blk.find(eol + '    }'):])
            src = src[:b[0]] + new_blk + src[b[1]:]
            changed += 1
            break
    if changed:
        json.loads(src)
        io.open(fp, 'w', encoding='utf-8', newline='').write(src)
    print(fp, 'eol=%r' % eol, 'stripped', changed)

strip_face('results/runnable_pool.bm-c.json',
           ['fund-value-p1-nulls-0of1', 'fund-quality-p1-nulls-0of1',
            'fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1'])

print('--- block-bounded verify (all 4 faces x 4 shards) ---')
for fp in ('results/runnable_pool.json', 'results/runnable_pool.bm-a.json',
           'results/runnable_pool.bm-b.json', 'results/runnable_pool.bm-c.json'):
    src = io.open(fp, encoding='utf-8', newline='').read()
    eol = eol_of(src)
    for sid, nm in (('fund-value-p1-nulls-0of1', 'value-nulls'),
                    ('fund-quality-p1-nulls-0of1', 'quality-nulls'),
                    ('fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1', 'x2'),
                    ('fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1', 'x1')):
        b = shard_block(src, sid, eol)
        blk = src[b[0]:b[1]] if b else ''
        o = blk.find('"owner": "')
        ow = blk[o+9:blk.find('"', o+9)] if o >= 0 else 'NO-OWNER'
        print(f'{fp.split(chr(46))[-2]} {nm}: owner={ow!r}')
