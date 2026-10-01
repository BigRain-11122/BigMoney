"""r504 bm-b: T-134 ticket JSON syntax repair (r312 note segment appended outside
the note string -> board-wide parse failure). Fold stray segment into the note
field; zero content change beyond the seam. Dual-track: temp index on
origin/main, commit-tree, push; local dirty tree untouched (r512 recipe)."""
import subprocess, json, sys, hashlib

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
PATH = 'fleet/tasks/T-2026-09-30-134-P1.json'

raw = subprocess.check_output(['git', '-C', REPO, 'show', 'origin/main:' + PATH])
s = raw.decode('utf-8')

seam_old = 'census 35->34).",\n | s2 FOURTH CONVERSION landed'
seam_new = 'census 35->34). | s2 FOURTH CONVERSION landed'
assert s.count(seam_old) == 1, 'seam not unique/found: count=%d' % s.count(seam_old)
fixed = s.replace(seam_old, seam_new)

obj = json.loads(fixed)  # hard validate
assert obj['id'] == 'T-2026-09-30-134' and obj['status'] == 'claimed'
note = obj['note']
assert 'FOURTH CONVERSION landed by bm-c r312' in note
for seg in ['s4 DELIVERED', 's2 FIRST CONVERSION', 's2 SECOND CONVERSION',
            's2 THIRD CONVERSION', 's2 FOURTH CANDIDATE SELECTED',
            's2 FOURTH CONVERSION landed']:
    assert note.count(seg) == 1, 'segment missing/dup: ' + seg  # all six note segments preserved

# byte-level accounting: only the seam differs
fixed_b = fixed.encode('utf-8')
print('orig bytes=%d fixed bytes=%d delta=%d' % (len(raw), len(fixed_b), len(fixed_b) - len(raw)))
print('sha_orig=' + hashlib.sha256(raw).hexdigest().upper()[:16])
print('sha_fixed=' + hashlib.sha256(fixed_b).hexdigest().upper()[:16])
with open(r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r504bmb_t134_fixed.json', 'wb') as f:
    f.write(fixed_b)
print('VALID_JSON_OK')
