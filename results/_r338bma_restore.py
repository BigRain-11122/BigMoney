import subprocess
import json

def show(ref, path):
    r = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True)
    assert r.returncode == 0, f'show {ref}:{path} rc={r.returncode}'
    return r.stdout

# ---------- 1. CODELY: restore 3 lost entries (stub in tree, full verbatim in archive = 21st batch) ----------
o = show('5c5dab93', 'CODELY.md').decode('utf-8', errors='replace')
m = show('0cf7c5eb', 'CODELY.md').decode('utf-8', errors='replace')
cod = open('CODELY.md', 'rb').read()
eol = '\r\n' if b'\r\n' in cod else '\n'
t = cod.decode('utf-8')
lines = t.split(eol)

def find_entry(text, kw):
    for l in text.splitlines():
        if l.strip().startswith('- [') and kw in l:
            return l.strip()
    raise RuntimeError('entry not found: ' + kw)

full_r333 = find_entry(o, 'tick 对 git 危险窗禁止') if '危险窗禁止' in o else find_entry(o, 'r333 bm-b')
full_r90 = find_entry(o, 'r90 bm-c')
full_r89 = find_entry(m, 'r89 bm-c')

stubs = [
    '- [2026-09-27 16:3x r333 bm-b] 坑律（二十一批外迁·指针）：tick 对 git 危险窗禁止（fire :X0:02→commit 落点 :X2:5x）——同窗双批十六批同象双存照 r85 勘注先例。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十一批』节。',
    '- [2026-09-27 16:5x r90 bm-c] 坑律（二十一批外迁·指针）：resolver 对 auto-merged 存档 stage blob 反封锁人工核验（auto-merge 非 UU 面 :1:/:2:/:3: stage 不存在）。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十一批』节。',
    '- [2026-09-27 16:1x r89 bm-c] 坑律（二十一批外迁·指针）：stub-drop 变方案锚全量归档态（指针保留）+probe/resolver 产物统一 encode 字节级。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十一批』节。',
]
while lines and lines[-1] == '':
    lines.pop()
lines += stubs
open('CODELY.md', 'wb').write((eol.join(lines) + eol).encode('utf-8'))
print('CODELY restored, size:', len(eol.join(lines).encode('utf-8')) + len(eol), 'B')

# archive: append 21st batch with the 3 fulls verbatim
ARC = 'research/memory-archive/202609.md'
ab = open(ARC, 'rb').read()
aeol = '\r\n' if ab.count(b'\r\n') > (ab.count(b'\n') - ab.count(b'\r\n')) else '\n'
section = aeol.join([
    '## 坑律归档 2026-09-27 二十一批（r338 bm-a·rebase 撞头零丢失恢复批：CODELY 双侧 5 缺行审计后 3 全文入档·2 存根变体经二十批双节覆盖）',
    full_r333,
    full_r90,
    full_r89,
    ''])
if not ab.endswith(aeol.encode()):
    ab += aeol.encode()
ab += section.encode('utf-8') + aeol.encode()
open(ARC, 'wb').write(ab)
atext = open(ARC, encoding='utf-8', errors='replace').read()
for f in (full_r333, full_r90, full_r89):
    assert f in atext, 'archive verbatim assert FAIL'
print('archive 21st batch appended, verbatim assert x3 PASS')

# ---------- 2. autofill_state.json union (mixed-dict+ledger canon r322/r245) ----------
p = 'results/autofill_state.json'
base = show(':1:', p)
eol2 = '\r\n' if b'\r\n' in base else '\n'
indent = 1
for line in base.decode('utf-8', errors='replace').split(eol2):
    if line.startswith(' '):
        indent = len(line) - len(line.lstrip(' '))
        break
a = json.loads(show(':2:', p).decode('utf-8'))  # HEAD side (origin+bm-a replayed close commit)
b = json.loads(show(':3:', p).decode('utf-8'))  # my tick-absorption side

def key(x):
    return (x.get('ts'), x.get('machine'), x.get('pid'), x.get('runner_sha256'), x.get('entry'), x.get('shard'))

seen = {}
merged = []
for e in a.get('launches', []) + b.get('launches', []):
    k = key(e)
    if k in seen:
        if seen[k] != e:
            f1, f2 = set(seen[k]), set(e)
            if f1 == f2:
                continue
            extra = {kk: kk for kk in f2 - f1}
            merged_e = dict(seen[k])
            merged_e.update({kk: e[kk] for kk in f2 - f1})
            if merged_e != e and merged_e != seen[k]:
                # field-union merge per r322
                seen[k] = merged_e
                merged = [x if key(x) != k else merged_e for x in merged]
            continue
        continue
    seen[k] = e
    merged.append(e)
merged.sort(key=lambda x: x.get('ts', ''))
if len(merged) > 50:
    merged = sorted(merged, key=lambda x: x.get('ts', ''))[-50:]
    merged.sort(key=lambda x: x.get('ts', ''))
la, lb = a.get('last_tick', {}), b.get('last_tick', {})
ta, tb = (la or {}).get('ts'), (lb or {}).get('ts')
lt = la if (ta is not None and (tb is None or ta >= tb)) else lb
if ta == tb:
    lt = la
assert isinstance(lt, dict), 'last_tick not dict'
out = dict(a)
out['launches'] = merged
out['last_tick'] = lt
s = (json.dumps(out, ensure_ascii=False, indent=indent) + '\n').replace('\n', eol2)
open(p, 'wb').write(s.encode('utf-8'))
json.load(open(p, encoding='utf-8'))
print(f'autofill_state: launches {len(a.get("launches", []))}|{len(b.get("launches", []))} -> {len(merged)} composite-union, last_tick ts={(lt or {}).get("ts")}')
print('ALL FILE WORK DONE')
