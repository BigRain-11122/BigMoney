# r452 bm-a rebase resolver: research/memory-archive/202609.md (append-ledger-md union + r449 dedupe)
# Stages: :2: = origin (bm-c r245 close @~01:39, added r245 bm-c window-batch section, 2 entries)
#         :3: = replay (bm-a r452 adopt @~01:42, added r452 bm-a window-batch section, 3 entries)
# Collision: r440 撞批三查律 entry verbatim in BOTH suffixes (same-window hot-cold reorgs
#            on both machines). r449 dedupe law: keep earlier occurrence (bm-c r245 section),
#            drop the verbatim dup from the later section, record provenance in the header.
# Zero-loss check: every non-dup suffix line survives verbatim; dup counted once.
import subprocess, sys

def stage(s):
    return subprocess.run(['git', 'show', s], capture_output=True).stdout.decode('utf-8')

o = stage(':2:research/memory-archive/202609.md').splitlines(True)
m = stage(':3:research/memory-archive/202609.md').splitlines(True)

i = 0
while i < min(len(o), len(m)) and o[i] == m[i]:
    i += 1
prefix, osuf, msuf = o[:i], o[i:], m[i:]
print(f'prefix={len(prefix)} origin_suffix={len(osuf)} mine_suffix={len(msuf)}')

oset = set(osuf)
dups = [l for l in msuf if l in oset and l.strip().startswith('- [')]
print(f'verbatim dup lines in mine suffix: {len(dups)}')
for d in dups:
    print('  DUP:', d.strip()[:60])

msuf_kept = [l for l in msuf if l not in dups]
merged = prefix + osuf + msuf_kept
blob = ''.join(merged)

# zero-loss: all origin lines + all non-dup mine lines survive
assert all(l in blob for l in osuf), 'origin suffix line lost'
assert all(l in blob for l in msuf_kept), 'mine suffix line lost'
# dup present exactly once
assert blob.count(dups[0]) == 1 if dups else True
# sections present
assert '## 热冷整编 2026-09-30 r245 bm-c' in blob and '## 热冷整编 2026-09-30 r452 bm-a' in blob

# provenance note appended to my section header parenthetical
old_hdr = [l for l in msuf_kept if l.startswith('## 热冷整编 2026-09-30 r452')][0]
new_hdr = old_hdr.rstrip('\n')[:-1] + '·r440 条与同窗 r245 bm-c 批 verbatim 重叠=在档即删保单存〔r449 dedupe 律〕）\n'
blob = blob.replace(old_hdr, new_hdr)

open(r'research/memory-archive/202609.md', 'w', encoding='utf-8', newline='').write(blob)
nl = blob.count('\n')
print(f'wrote {nl} lines = prefix {len(prefix)} + origin {len(osuf)} + mine-kept {len(msuf_kept)}: '
      f'{len(prefix)+len(osuf)+len(msuf_kept)==nl}')
