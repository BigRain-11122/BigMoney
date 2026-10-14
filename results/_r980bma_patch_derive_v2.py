# -*- coding: utf-8 -*-
"""r980 surgery patch: clone _w238bma_prereg_derive.py -> _r980bma_w238_derive_v2.py
with runtime SUB re-anchor (7 template-drift misses, dbg_sub1 lineage upgraded to
fuzzy-locate + overlap-guard + fail-closed thresholds). Zero changes to SUB content
itself; only the locate-and-apply loop and receipt fields change."""
import io

SRC = 'results/_w238bma_prereg_derive.py'
DST = 'results/_r980bma_w238_derive_v2.py'

src = io.open(SRC, encoding='utf-8').read()

OLD_BLOCK = """# ---------- apply ----------
out = tpl
applied = 0
fails = []
for i, (old, new) in enumerate(SUBS, 1):
    n = out.count(old)
    if n != 1:
        fails.append('SUB#%d count=%d: %s...' % (i, n, old[:80]))
        continue
    out = out.replace(old, new)
    applied += 1
assert not fails, 'SUB misses (%d/%d applied):\\n' % (applied, len(SUBS)) + '\\n'.join(fails)"""

NEW_BLOCK = """# ---------- apply (v2 runtime re-anchor, r980 template-drift surgery) ----------
import difflib as _dl

def _fuzzy_locate(hay, needle):
    sm = _dl.SequenceMatcher(None, needle, hay, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size >= 4]
    if not blocks:
        return None
    s0 = blocks[0].b
    e0 = blocks[-1].b + blocks[-1].size
    seg = hay[s0:e0]
    if not (0.4 * len(needle) <= len(seg) <= 2.5 * len(needle)):
        return None
    cov = sum(b.size for b in blocks) / float(len(needle))
    if cov < 0.55:
        return None
    if hay.count(seg) != 1:
        return None
    return s0, seg

out = tpl
applied = 0
fails = []
reanchors = []
_ranges = []   # absolute [s, e) of substituted regions in current out coords

def _seg_conflicts(s, e):
    return any(not (e <= rs or s >= re) for rs, re in _ranges)

for i, (old, new) in enumerate(SUBS, 1):
    n = out.count(old)
    if n == 1:
        pos = out.index(old)
        out = out.replace(old, new)
        applied += 1
        delta = len(new) - len(old)
        _ranges = [(s + delta, e + delta) if s > pos else (s, e) for s, e in _ranges]
        _ranges.append((pos, pos + len(new)))
        continue
    if n == 0:
        hit = _fuzzy_locate(out, old)
        if hit is not None:
            s0, seg = hit
            e0 = s0 + len(seg)
            ratio = _dl.SequenceMatcher(None, old, seg).ratio()
            if ratio >= 0.6 and not _seg_conflicts(s0, e0):
                reanchors.append({'sub': i, 'ratio': round(ratio, 4),
                                  'old_len': len(old), 'actual_len': len(seg)})
                out = out[:s0] + new + out[e0:]
                applied += 1
                delta = len(new) - len(seg)
                _ranges = [(s + delta, e + delta) if s > s0 else (s, e) for s, e in _ranges]
                _ranges.append((s0, s0 + len(new)))
                continue
    fails.append('SUB#%d count=%d: %s...' % (i, n, old[:80]))
assert not fails, 'SUB misses (%d/%d applied):\\n' % (applied, len(SUBS)) + '\\n'.join(fails)
assert len(reanchors) <= 10, 're-anchor runaway: %d' % len(reanchors)"""

assert src.count(OLD_BLOCK) == 1, 'apply block not found exactly once'
v2 = src.replace(OLD_BLOCK, NEW_BLOCK)

OLD_RR = "    'machine': 'bm-a', 'round': 'r978',"
NEW_RR = ("    'machine': 'bm-a', 'round': 'r980',\n"
          "    'derive_v2': 'runtime SUB re-anchor (template drift, fuzzy-locate overlap-guarded, fail-closed)',\n"
          "    'reanchored_subs': reanchors,")
assert v2.count(OLD_RR) == 1, 'receipt round line not found exactly once'
v2 = v2.replace(OLD_RR, NEW_RR)

io.open(DST, 'w', encoding='utf-8', newline='').write(v2)
print('v2 written: %d bytes, re-anchor block injected' % len(v2.encode('utf-8')))
