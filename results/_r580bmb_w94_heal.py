# r580 bm-b W94-revert heal (byte-exact extraction from holding commit
# 9a9d05857 + r560-guarded insertion into current tree; idempotent).
# Damage: dead r579 session's replay commit efb7ffcd0 clobbered bm-a's W94
# registration (r560 anchor-replacement family, 7th live instance) --
# canon W94 row + pf N1_BANDS[94] + n1 WAVE_CONFIGS[94] + W94 selftest leg +
# W94 PASS fragment all reverted; W94 prereg + gate tools survived.
import subprocess, sys

HOLD = '9a9d05857'
ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
FILES = {
    'canon': 'research/PERPETUAL_FACES.md',
    'pf': 'scripts/perpetual_faces.py',
    'n1': 'scripts/perpetual_faces_n1.py',
}

def hold_bytes(path):
    r = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (HOLD, path)],
                       capture_output=True)
    assert r.returncode == 0, 'blob fetch fail ' + path
    return r.stdout

def cur_bytes(path):
    with open(ROOT + '\\' + path.replace('/', '\\'), 'rb') as f:
        return f.read()

def lines_index(data):
    # list of (start_offset, line_incl_newline)
    out, i = [], 0
    while i < len(data):
        j = data.find(b'\n', i)
        if j < 0:
            out.append((i, data[i:] + b''))
            break
        out.append((i, data[i:j + 1]))
        i = j + 1
    return out

def block_from_lines(data, start_pred, end_pred, tag):
    ls = lines_index(data)
    si = None
    for idx, (off, ln) in enumerate(ls):
        if start_pred(ln):
            si = idx
            break
    assert si is not None, tag + ': start marker not found'
    for idx in range(si, len(ls)):
        if end_pred(ls[idx][1]):
            return data[ls[si][0]:ls[idx][0] + len(ls[idx][1])], ls[idx][0] + len(ls[idx][1])
    raise AssertionError(tag + ': end marker not found')

def insert_after(cur, anchor_pred, block, tag, guard_pred=None):
    ls = lines_index(cur)
    for idx, (off, ln) in enumerate(ls):
        if anchor_pred(ln):
            end = off + len(ln)
            nxt = cur[end:end + 60]
            if guard_pred:
                assert guard_pred(nxt), tag + ': post-anchor guard fail: %r' % nxt[:60]
            return cur[:end] + block + cur[end:]
    raise AssertionError(tag + ': anchor not found')

report = []

# --- 1. canon W94 row -----------------------------------------------------------
hb = hold_bytes(FILES['canon'])
blk, _ = block_from_lines(
    hb,
    lambda l: l.startswith(b'- N1 ') and '\u6ce294'.encode() in l[:12],
    lambda l: l.rstrip().endswith(b'.') or l.rstrip() == b'',
    'canon-w94')
# canon row is ONE line (bullet); force single-line extraction
ls = lines_index(hb)
w94_off = None
for off, ln in ls:
    if ln.startswith(b'- N1 ') and '\u6ce294'.encode() in ln[:12]:
        w94_off, w94_ln = off, ln
        break
assert w94_off is not None, 'canon W94 row not found in holding'
canon_blk = w94_ln
cb = cur_bytes(FILES['canon'])
if '\u6ce294\uff08r580'.encode('utf-8') in cb:
    print('SKIP canon: W94 row already present')
else:
    cb2 = insert_after(
        cb,
        lambda l: l.startswith(b'- N1 ') and '\u6ce293'.encode() in l[:12],
        canon_blk, 'canon-insert',
        guard_pred=lambda nxt: b'\n' == nxt[:1] or nxt[:1] == b'')
    assert canon_blk in cb2 and cb2.count(canon_blk) == 1
    assert b'- N1 ' + '\u6ce293'.encode() in cb2 and b'- N1 ' + '\u6ce294'.encode() in cb2
    with open(ROOT + '\\research\\PERPETUAL_FACES.md', 'wb') as f:
        f.write(cb2)
    print('canon: W94 row re-inserted after W93 row (+%d bytes)' % len(canon_blk))

# --- 2. pf N1_BANDS[94] entry ---------------------------------------------------
hb = hold_bytes(FILES['pf'])
blk, _ = block_from_lines(
    hb,
    lambda l: l.strip().startswith(b'# EIGHTY-FOURTH ENGINE-OWNED WAVE'),
    lambda l: l.strip() == b'"engine_owner": "bm-a"},',
    'pf-w94')
assert b'94: {"a": (231_004, 233_003)' in blk
pb = cur_bytes(FILES['pf'])
if b'94: {"a": (231_004, 233_003)' in pb:
    print('SKIP pf: W94 entry already present')
else:
    ls = lines_index(pb)
    ai = None
    for idx in range(len(ls) - 1, -1, -1):
        # find the 93: {"a" line, then its engine_owner close
        if ls[idx][1].strip().startswith(b'93: {"a"'):
            assert ls[idx + 1][1].strip() == b'"engine_owner": "bm-b"},', \
                'pf: 93 entry close shape drift: %r' % ls[idx + 1][1][:60]
            ai = idx + 1
            break
    assert ai is not None, 'pf: 93 entry not found'
    end = ls[ai][0] + len(ls[ai][1])
    nxt = pb[end:end + 20]
    assert nxt.startswith(b'}'), 'pf post-anchor guard: expected N1_BANDS close, got %r' % nxt[:20]
    pb2 = pb[:end] + blk + pb[end:]
    assert pb2.count(b'94: {"a": (231_004, 233_003)') == 1
    with open(ROOT + '\\scripts\\perpetual_faces.py', 'wb') as f:
        f.write(pb2)
    print('pf: N1_BANDS[94] re-inserted after 93 entry (+%d bytes)' % len(blk))

# --- 3. n1 WAVE_CONFIGS[94] -----------------------------------------------------
hb = hold_bytes(FILES['n1'])
blk, _ = block_from_lines(
    hb,
    lambda l: l.strip().startswith(b'94: {"batch"'),
    lambda l: l.strip() == b'"engine_owner": "bm-a"},',
    'n1-cfg94')
assert b'PERPETUAL-N1-W94' in blk
nb = cur_bytes(FILES['n1'])
if b'"shard_subdir": "n1_w94"' in nb:
    print('SKIP n1 cfg: W94 entry already present')
else:
    ls = lines_index(nb)
    ai = None
    for idx in range(len(ls) - 1, -1, -1):
        if ls[idx][1].strip().startswith(b'93: {"batch"'):
            # walk to its engine_owner dict-close line (prose mentions of
            # engine_owner inside the prereg string are NOT close lines)
            k = idx
            while ls[k][1].strip() != b'"engine_owner": "bm-b"},':
                k += 1
                assert k < len(ls), 'n1: 93 cfg close not found'
            ai = k
            break
    assert ai is not None, 'n1: 93 cfg entry not found'
    end = ls[ai][0] + len(ls[ai][1])
    nxt = nb[end:end + 30]
    assert b'95' not in nxt[:30], 'n1 cfg post-anchor guard: %r' % nxt[:30]
    nb2 = nb[:end] + blk + nb[end:]
    assert nb2.count(b'"shard_subdir": "n1_w94"') == 1
    nb = nb2
    print('n1: WAVE_CONFIGS[94] re-inserted after 93 entry (+%d bytes)' % len(blk))

# --- 4. n1 W94 materializer leg --------------------------------------------------
blk, _ = block_from_lines(
    hb,
    lambda l: l.lstrip().startswith(b'# --- W94 materializer face'),
    lambda l: l.strip() == b'_set_wave(2)',
    'n1-leg94')
assert b'W94' in blk and b'_set_wave(94)' in blk
if b'W94 materializer face' in nb:
    print('SKIP n1 leg: W94 leg already present')
else:
    ls = lines_index(nb)
    ai = None
    for idx in range(len(ls) - 1, -1, -1):
        if ls[idx][1].lstrip().startswith(b'# --- W93 materializer face'):
            k = idx
            while ls[k][1].strip() != b'_set_wave(2)':
                k += 1
            ai = k
            break
    assert ai is not None, 'n1: W93 leg finally not found'
    end = ls[ai][0] + len(ls[ai][1])
    nxt = nb[end:end + 40]
    assert b'W95' not in nxt[:40] and b'W94' not in nxt[:40], \
        'n1 leg post-anchor guard: %r' % nxt[:40]
    nb2 = nb[:end] + b'\n' + blk + nb[end:] if not nb[end - 1:end] == b'\n' else nb[:end] + blk + nb[end:]
    # ensure exactly one blank line separation preserved by blk's own leading
    nb2 = nb[:end] + blk + nb[end:]
    assert nb2.count(b'W94 materializer face') == 1
    nb = nb2
    print('n1: W94 materializer leg re-inserted after W93 leg (+%d bytes)' % len(blk))

# --- 5. n1 W94 PASS-print fragment ----------------------------------------------
ls = lines_index(hb)
fi = None
for idx, (off, ln) in enumerate(ls):
    if b'"+ W94 materializer face' in ln or (b'W94 materializer face [' in ln and ln.strip().startswith(b'"')):
        fi = idx
        break
assert fi is not None, 'n1 frag: W94 fragment start not found'
# fragment = contiguous string-literal lines from fi to the line ending with bm-a] "
ei = fi
while True:
    if ls[ei][1].rstrip().endswith(b'] "') and b'W94' in ls[ei][1]:
        break
    ei += 1
    assert ei < len(ls), 'n1 frag: end not found'
frag = hb[ls[fi][0]:ls[ei][0] + len(ls[ei][1])]
if b'law sec.4 W94 row, r580 bm-a' in nb:
    print('SKIP n1 frag: W94 fragment already present')
else:
    # current tree: insert after the W93 fragment end line
    ls2 = lines_index(nb)
    ai = None
    for idx in range(len(ls2) - 1, -1, -1):
        if b'law sec.4 W93 row' in ls2[idx][1] and ls2[idx][1].rstrip().endswith(b'] "'):
            ai = idx
            break
    assert ai is not None, 'n1 frag: W93 fragment end not found in current'
    end = ls2[ai][0] + len(ls2[ai][1])
    nxt = nb[end:end + 40]
    assert b'W94' not in nxt[:40], 'n1 frag post-anchor guard: %r' % nxt[:40]
    nb2 = nb[:end] + frag + nb[end:]
    assert nb2.count(frag) == 1
    nb = nb2
    print('n1: W94 PASS fragment re-inserted after W93 fragment (+%d bytes)' % len(frag))

with open(ROOT + '\\scripts\\perpetual_faces_n1.py', 'wb') as f:
    f.write(nb)
print('HEAL_STAGED_OK')
