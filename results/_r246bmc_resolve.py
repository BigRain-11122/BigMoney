# r246 bm-c rebase-conflict resolver (5 UU) per r444/r449/r241 canon:
#  CODELY.md          = ours(bm-a r452) + my unique W4 line; my r236 pointer dropped (bm-a combined pointer covers it, r449 dedup)
#  archive 202609.md  = ours verbatim (r452 section already carries r236 verbatim; my r246 section = pure duplicate, dropped)
#  _attrition_guard   = take-newer snapshot (theirs 02:12:27)
#  compute_audit.json = history union by ts (dedupe, sort), latest take-newer (r447 canon)
#  token_usage.json   = theirs base + bm-a lane keys overlay (R31 lane-authority)
import io, sys, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def stage_raw(sid, path):
    return subprocess.run(['git', 'show', '%s:%s' % (sid, path)], capture_output=True).stdout

def sep_of(b):
    return '\r\n' if b'\r\n' in b[:4000] else '\n'

def write_bytes(path, b):
    open(path, 'wb').write(b)

# ---- 1) CODELY.md
raw_o = stage_raw(':2', 'CODELY.md')
raw_t = stage_raw(':3', 'CODELY.md')
sep = sep_of(raw_o)
ours = raw_o.decode('utf-8')
theirs = raw_t.decode('utf-8')
w4lines = [l for l in theirs.split(sep) if l.startswith('- [2026-09-30 02:1x r246 bm-c] W4')]
assert len(w4lines) == 1, 'w4 line not unique in theirs'
w4 = w4lines[0]
assert '冷层指针：r236 GBK 控制台吞链+r444' in ours, 'bm-a combined pointer missing'
assert 'r452 bm-a] 判据字段语义漂移' in ours, 'bm-a r452 memory line missing'
assert '- [2026-09-29 20:0x r236 bm-c] GBK 控制台吞链 runner 坑（S6' not in ours, 'ours still has r236 full entry'
lines = ours.split(sep)
idx = [i for i, l in enumerate(lines) if l.startswith('- 冷层指针：r242 bm-c runner 外科手术四连坑族')]
assert len(idx) == 1, 'r242 pointer anchor not unique in ours'
lines.insert(idx[0] + 1, w4)
out = sep.join(lines)
assert out.count(w4) == 1
assert '- [2026-09-29 20:0x r236 bm-c] GBK 控制台吞链 runner 坑（S6' not in out
write_bytes('CODELY.md', out.encode('utf-8'))
print('CODELY.md resolved: bm-a base + W4 line; size %d B' % len(out.encode('utf-8')))

# ---- 2) archive 202609.md = ours verbatim (dedupe my duplicate section)
raw_a = stage_raw(':2', 'research/memory-archive/202609.md')
theirs_a = stage_raw(':3', 'research/memory-archive/202609.md').decode('utf-8')
assert '- [2026-09-29 20:0x r236 bm-c] GBK 控制台吞链 runner 坑（S6' in raw_a.decode('utf-8'), 'r236 verbatim not in ours archive'
assert '热冷整编 2026-09-30 r246 bm-c 窗批' in theirs_a, 'my section header missing in theirs (sanity)'
write_bytes(r'research\memory-archive\202609.md', raw_a)
print('archive resolved: ours verbatim (%d B), my r246 dup section dropped (r236 already in r452 section)' % len(raw_a))

# ---- 3) _attrition_guard_scan.json = take-newer
g_o = json.loads(stage_raw(':2', 'results/_attrition_guard_scan.json').decode('utf-8-sig'))
g_t = json.loads(stage_raw(':3', 'results/_attrition_guard_scan.json').decode('utf-8-sig'))
g = g_t if g_t['ts'] > g_o['ts'] else g_o
write_bytes('results/_attrition_guard_scan.json', (json.dumps(g, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
print('guard_scan resolved: take-newer ts=%s active_loss=%s' % (g['ts'], g['active_loss']))

# ---- 4) compute_audit.json = history union by ts + latest take-newer
a_o = json.loads(stage_raw(':2', 'results/compute_audit.json').decode('utf-8-sig'))
a_t = json.loads(stage_raw(':3', 'results/compute_audit.json').decode('utf-8-sig'))
seen = {}
for h in a_o['history'] + a_t['history']:
    seen[h['ts']] = h
merged = sorted(seen.values(), key=lambda x: x['ts'])
latest = a_t['latest'] if a_t['latest']['ts'] > a_o['latest']['ts'] else a_o['latest']
out_a = {'latest': latest, 'history': merged}
write_bytes('results/compute_audit.json', (json.dumps(out_a, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
json.loads(open('results/compute_audit.json', encoding='utf-8').read())
print('compute_audit resolved: history union %d+%d -> %d unique, latest ts=%s'
      % (len(a_o['history']), len(a_t['history']), len(merged), latest['ts']))

# ---- 5) token_usage.json = theirs base + bm-a lane overlay + newer envelope
t_o = json.loads(stage_raw(':2', 'results/token_usage.json').decode('utf-8-sig'))
t_t = json.loads(stage_raw(':3', 'results/token_usage.json').decode('utf-8-sig'))
base = dict(t_t if t_t['generated'] > t_o['generated'] else t_o)
src = t_o if base['generated'] == t_t['generated'] else t_t
mach = dict(base.get('machines', {}))
for k in ('bm-a', '-bm-a'):
    if k in src.get('machines', {}):
        mach[k] = src['machines'][k]
base['machines'] = mach
write_bytes('results/token_usage.json', (json.dumps(base, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
json.loads(open('results/token_usage.json', encoding='utf-8').read())
print('token_usage resolved: newer=%s, bm-a lane keys overlaid from bm-a author side' % base['generated'])

print('ALL 5 RESOLVED')
