# r646 bm-b CODELY.md resolver v7 FINAL: true entries from bm-a closeout source (ast-safe),
# ASCII-skeleton safety scan over the mojibake blob, rebuild = clean base + e1/e2
import ast
import re
import subprocess

def show(ref):
    return subprocess.run(['git', 'show', ref],
                         capture_output=True, creationflags=0x08000000).stdout

b_base = show('HEAD^1:CODELY.md')    # pre-merge bm-b clean 68-line version
b_blob = show('HEAD^2:CODELY.md')    # origin mojibake single-line blob
assert b_base and b_blob
base_lines = b_base.decode('utf-8').splitlines()
base_mk = set(ln[:44] for ln in base_lines if ln.lstrip().startswith('- ['))

# (1) extract bm-a's two true r657 entries from their closeout source (zero execution)
src = open('results/_r657bma_closeout_writes.py', encoding='utf-8').read()
tree = ast.parse(src)
true_entries = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id in ('e1', 'e2'):
                true_entries[tgt.id] = ast.literal_eval(node.value)
assert set(true_entries) == {'e1', 'e2'}, true_entries.keys()
for k, v in true_entries.items():
    assert v.startswith('- [2026-10-04 04:0x r657 bm-a]'), v[:40]
    assert v[:44] not in base_mk, 'already in base?!'
print('true entries extracted: e1', len(true_entries['e1']), 'chars; e2',
      len(true_entries['e2']), 'chars')

# (2) safety scan: every entry segment in the mojibake blob must either
#     skeleton-match the base, or be e1/e2 -- anything else = honest flag
t = b_blob.decode('utf-8').lstrip('\ufeff')
segs = t.split('- [')[1:]
def skel(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^\x20-\x7e]', '', s)).strip()[:60]
base_skels = set(skel(l) for l in base_lines if l.lstrip().startswith('- ['))
true_skels = set(skel(v) for v in true_entries.values())
unmatched = []
for seg in segs:
    s = re.sub(r'(#+\s*\w+\s*)+$', '', seg.rstrip()).rstrip()
    k = skel('- [' + s)
    hit = any(k.startswith(b) or b.startswith(k) for b in base_skels
              if len(b) >= 20) or any(k.startswith(x) or x.startswith(k)
                                     for x in true_skels if len(x) >= 20)
    if not hit:
        unmatched.append(k[:70])
print('blob segments', len(segs), 'skeleton-unmatched (expect 0):', len(unmatched))
for u in unmatched:
    print('  UNMATCHED:', u.encode('unicode_escape').decode()[:120])

# (3) rebuild: base + e1 + e2 (order: e1 then e2 as authored)
out = b_base if b_base.endswith(b'\n') else b_base + b'\n'
for k in ('e1', 'e2'):
    out += true_entries[k].encode('utf-8') + b'\n'
bad = [ln[:30] for ln in out.decode('utf-8').splitlines()
       if ln.strip().startswith('<<<<<<<') or ln.strip().startswith('>>>>>>>') or ln.strip() == '=======']
assert not bad, bad
assert out.decode('utf-8').count(chr(10)) == len(base_lines) + 2
open('CODELY.md', 'wb').write(out)
print('CODELY.md FINAL: bytes', len(out), 'lines', out.decode('utf-8').count(chr(10)),
      '(base', len(base_lines), '+ 2 true r657 entries)')
if unmatched:
    print('WARNING: unmatched segments exist -- see flags above')
