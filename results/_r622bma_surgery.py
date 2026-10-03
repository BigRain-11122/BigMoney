"""r622 bm-a surgical release + keep-block pins (r603/r616/r617 laws).

Pool faces: strip bm-a ghost owner pairs (value-nulls, quality-nulls, x2)
across all lane faces; x1/x2 shard blocks in SHARED face <- origin verbatim
(bm-b canonical: x1 done 11:36:04, x2 owner 11:40:22).
Fuse faces: install/re-arm keep-block sigs for fund_divlowvol family +
note the value-nulls sig (already count=1 from the 11:40 kill).
"""
import io, json, subprocess, datetime, hashlib, sys

NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
REL_NOTE = (' | rel-bm-a-r622 ' + NOW + ': off-caliber burn killed '
            '(all 150 burned rows diverged vs bm-b basis n_engine_syms '
            '2483vs2473), rows discarded, nulls restored to origin 164-row '
            'canonical, yield to bm-b per MSG-1132, keep-block pinned on '
            'bm-a pending T-156 cache swap')

POOL_FACES = ['results/runnable_pool.json', 'results/runnable_pool.bm-a.json',
              'results/runnable_pool.bm-b.json', 'results/runnable_pool.bm-c.json']
FUSE_FACES = ['results/crash_fuse.json', 'results/crash_fuse.bm-a.json',
              'results/crash_fuse.bm-b.json', 'results/crash_fuse.bm-c.json']

STRIP_SHARDS = ['fund-value-p1-nulls-0of1', 'fund-quality-p1-nulls-0of1',
                'fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1',
                'fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1']

DIV_SHA = hashlib.sha256(open('scripts/fund_divlowvol_p1.py', 'rb').read()).hexdigest()
assert DIV_SHA.startswith('2744ee59'), DIV_SHA

def rd(fp):
    return io.open(fp, encoding='utf-8', newline='').read()

def wr(fp, s):
    with io.open(fp, 'w', encoding='utf-8', newline='') as f:
        f.write(s)

def origin_blob(fp):
    return subprocess.run(['git', 'show', 'origin/main:' + fp],
                          capture_output=True).stdout.decode('utf-8')

def shard_block(src, sid):
    """Return (start, end) of the shard object block containing key sid.
    Block = from the '{' line before the key line to the first '    }' after."""
    i = src.find('"key": "' + sid + '"')
    if i < 0:
        return None
    start = src.rfind('{', 0, i)
    # walk to the closing of this object: first '\r\n    }' after i
    j = src.find('\r\n    }', i)
    end = j + len('\r\n    }')
    return start, end

# ---------- Part 1: pool faces ----------
osrc = origin_blob('results/runnable_pool.json')
report = []
for fp in POOL_FACES:
    src = rd(fp)
    orig = src
    # x1/x2 in SHARED face only <- origin verbatim (lane faces: strip bm-a ghosts only)
    if fp == 'results/runnable_pool.json':
        for sid in ('fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1',
                    'fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1'):
            ob = shard_block(osrc, sid)
            lb = shard_block(src, sid)
            assert ob and lb, (fp, sid)
            src = src[:lb[0]] + osrc[ob[0]:ob[1]] + src[lb[1]:]
            report.append((fp, sid, 'origin-verbatim'))
    for sid in STRIP_SHARDS:
        while True:
            b = shard_block(src, sid)
            if not b:
                break
            blk = src[b[0]:b[1]]
            if '"owner": "bm-a"' not in blk:
                break
            # strip owner + owner_since lines; fix note trailing comma
            assert '"note": "' in blk, sid
            n0 = blk.find('"note": "')
            nc = blk.find('",\r\n', n0)  # end of note value (note followed by owner)
            assert nc > 0, sid
            # construction blk[:nc] + tail already drops the owner/owner_since
            # lines (they lived between the note's '",' and the closing).
            new_blk = (blk[:nc] + REL_NOTE + '"\r\n' +
                       blk[blk.find('\r\n    }'):])
            src = src[:b[0]] + new_blk + src[b[1]:]
            report.append((fp, sid, 'stripped-bm-a-pair'))
            break  # one strip per shard per face
    if src != orig:
        json.loads(src)  # validity assert
        wr(fp, src)
    else:
        report.append((fp, '-', 'no-change'))

# ---------- Part 2: fuse faces ----------
FUSE_NOTE = ('keep blocked on bm-a r622 ' + NOW + ': OFF-CALIBER basis '
             'suspicion (bm-a fund-family cache pending T-156 swap); '
             'divlowvol family owned+burned by bm-b; bm-a detached '
             'launches die anyway; prevent bm-a burn (r617 pin law)')
PINS = {
    'scripts/fund_divlowvol_p1.py|run,--cell,DIVLOWVOL-YIELDVOL,--face,x1': {
        'count': 1, 'refusals': 0, 'code_sha256': DIV_SHA, 'last_crash_ts': NOW,
        'entry': 'FUND-DIVLOWVOL-P1-CELL-DIVLOWVOLYIELDVOL-X1',
        'shard': 'fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1',
        'machine': 'bm-a', 'note': FUSE_NOTE},
    'scripts/fund_divlowvol_p1.py|run,--cell,DIVLOWVOL-YIELDVOL,--face,x2': {
        'count': 1, 'refusals': 0, 'code_sha256': DIV_SHA, 'last_crash_ts': NOW,
        'entry': 'FUND-DIVLOWVOL-P1-CELL-DIVLOWVOLYIELDVOL-X2',
        'shard': 'fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1',
        'machine': 'bm-a', 'note': FUSE_NOTE},
    'scripts/fund_divlowvol_p1.py|run,--nulls': {
        'count': 1, 'refusals': 0, 'code_sha256': DIV_SHA, 'last_crash_ts': NOW,
        'entry': 'FUND-DIVLOWVOL-P1-NULLS', 'shard': 'fund-divlowvol-p1-nulls-0of1',
        'machine': 'bm-a', 'note': FUSE_NOTE},
    'scripts/fund_divlowvol_p1.py|run,--sensitivity': {
        'count': 1, 'refusals': 0, 'code_sha256': DIV_SHA, 'last_crash_ts': NOW,
        'entry': 'FUND-DIVLOWVOL-P1-SENS', 'shard': 'fund-divlowvol-p1-sens-0of1',
        'machine': 'bm-a', 'note': FUSE_NOTE},
}
VAL_NOTE = ('keep blocked on bm-a r622 ' + NOW + ': OFF-CALIBER CACHE '
            'containment (all 40 overlap keys 124..163 diverged vs bm-b '
            'basis; burn killed ' + NOW + ', 150 rows discarded, nulls '
            'restored to origin 164-row canonical; yield to bm-b per '
            'MSG-1132; unblock only after T-156 cache swap + four-point '
            'verify)')

fuse_changed = {}
for fp in FUSE_FACES:
    src = rd(fp)
    probe = json.dumps(json.loads(src), indent=2).replace('\n', '\r\n')
    if probe == src:
        fuse = json.loads(src)
        sigs = fuse.setdefault('sigs', {})
        n = 0
        for k, v in PINS.items():
            if k not in sigs:
                sigs[k] = dict(v); n += 1
            elif sigs[k].get('code_sha256') != DIV_SHA:
                sigs[k].update(dict(v)); n += 1
        vk = 'scripts/fund_value_p1.py|run,--nulls'
        if vk in sigs and 'note' not in sigs[vk]:
            sigs[vk]['note'] = VAL_NOTE; n += 1
        out = json.dumps(fuse, indent=2).replace('\n', '\r\n')
        if out != src:
            wr(fp, out); fuse_changed[fp] = (n, 'json-probe-ok')
    else:
        fuse_changed[fp] = (0, 'PROBE-FAIL-raw-insert-needed')

for r in report:
    print(r)
for k, v in fuse_changed.items():
    print('FUSE', k, v)
print('DIV_SHA', DIV_SHA[:16], 'NOW', NOW)
