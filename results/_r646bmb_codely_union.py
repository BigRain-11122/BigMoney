# r646 bm-b CODELY.md merge resolver v4: mojibake reversal (utf8->gbk bake) + entry union
import re
import subprocess

def show(ref):
    return subprocess.run(['git', 'show', ref],
                         capture_output=True, creationflags=0x08000000).stdout

b_mine = show('HEAD:CODELY.md')
b_theirs = show('MERGE_HEAD:CODELY.md')
assert b_mine and b_theirs
lm = b_mine.decode('utf-8').splitlines()
mine_mk = set(ln[:44] for ln in lm if ln.lstrip().startswith('- ['))
print('mine lines', len(lm), 'entry markers', len(mine_mk))

t = b_theirs.decode('utf-8')
if b_theirs[:3] == b'\xef\xbb\xbf':
    t = t.lstrip('\ufeff')
# reversal: mojibake text --encode gbk--> original utf-8 bytes --decode utf-8--> true text
orig_bytes = t.encode('gbk')            # strict: any failure = reversal assumption wrong
orig_text = orig_bytes.decode('utf-8')  # strict: proves byte-level round-trip
print('reversal OK: mojibake chars', len(t), '-> original bytes', len(orig_bytes),
      '-> text chars', len(orig_text))

segs = orig_text.split('- [')
head_part = segs[0]
assert re.fullmatch(r'#+ Codely Structured Memories#+ User\s*', head_part.replace('#', '#')) or \
       head_part.startswith('#'), head_part[:40]
uniq, seen = [], set()
for seg in segs[1:]:
    s = seg.rstrip()
    s = re.sub(r'(#+\s*\w+\s*)+$', '', s).rstrip()
    mk = ('- [' + s)[:44]
    if mk in mine_mk or mk in seen:
        continue
    seen.add(mk)
    uniq.append('- [' + s)
print('their genuinely-new entries:', len(uniq))
for u in uniq:
    print('  NEW:', u[:70].encode('unicode_escape').decode()[:130])

out = b_mine if b_mine.endswith(b'\n') else b_mine + b'\n'
for u in uniq:
    out += u.encode('utf-8') + b'\n'
bad = [ln[:30] for ln in out.decode('utf-8').splitlines()
       if ln.strip().startswith('<<<<<<<') or ln.strip().startswith('>>>>>>>') or ln.strip() == '=======']
assert not bad, bad
open('CODELY.md', 'wb').write(out)
print('CODELY.md final union: bytes', len(out), 'lines', out.decode('utf-8').count(chr(10)))
