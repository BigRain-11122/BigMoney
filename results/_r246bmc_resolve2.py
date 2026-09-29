# r246 bm-c resolver #2 (storm round 2, bm-b r444 S6-sweep mirror collision)
#  crash_fuse.json  = deep-compare, union if needed (r241 canon), parse-validated
#  regime_state.json = stripped-equal take-newer-ts (mine 02:09:57 > bm-b dead-tick 01:38:59)
import io, sys, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def stage(sid, path):
    b = subprocess.run(['git', 'show', '%s:%s' % (sid, path)], capture_output=True).stdout
    return json.loads(b.decode('utf-8-sig'))

# crash_fuse: union of sigs/cleared dicts
o = stage(':2', 'results/crash_fuse.json')
t = stage(':3', 'results/crash_fuse.json')
same = (o == t)
if same:
    merged = t  # identical -> either
    note = 'deep-equal'
else:
    merged = {'sigs': {}, 'cleared': {}}
    for section in ('sigs', 'cleared'):
        acc = dict(o.get(section, {}))
        acc.update(t.get(section, {}))
        merged[section] = acc
    note = 'union ours+theirs'
open('results/crash_fuse.json', 'wb').write((json.dumps(merged, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
json.load(open('results/crash_fuse.json', encoding='utf-8-sig'))
print('crash_fuse resolved: %s (sigs=%d cleared=%d)' % (note, len(merged['sigs']), len(merged['cleared'])))

# regime_state: take-newer updated ts
o = stage(':2', 'results/regime_state.json')
t = stage(':3', 'results/regime_state.json')
core_o = {k: v for k, v in o.items() if k != 'updated'}
core_t = {k: v for k, v in t.items() if k != 'updated'}
sel = t if t['updated'] > o['updated'] else o
eq = core_o == core_t
open('results/regime_state.json', 'wb').write((json.dumps(sel, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
json.load(open('results/regime_state.json', encoding='utf-8-sig'))
print('regime_state resolved: take-newer updated=%s (stripped-equal=%s, state=%s asof=%s)'
      % (sel['updated'], eq, sel['state'], sel['asof']))
print('RESOLVER2 DONE')
