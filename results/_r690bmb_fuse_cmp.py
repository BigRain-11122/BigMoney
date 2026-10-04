# r690 bm-b: crash_fuse.json dual-side compare (origin via subprocess raw bytes per r660 law)
import json, subprocess, sys

def load_origin():
    p = subprocess.run(['git', 'show', 'origin/main:results/crash_fuse.json'],
                       capture_output=True)
    return json.loads(p.stdout.decode('utf-8'))

def load_local():
    with open('results/crash_fuse.json', 'rb') as f:
        return json.loads(f.read().decode('utf-8'))

o = load_origin()
l = load_local()
out = []
out.append('TOP KEYS origin: %s | local: %s' % (sorted(o.keys()), sorted(l.keys())))
for side, d in (('ORIGIN', o), ('LOCAL', l)):
    out.append('--- %s ---' % side)
    sigs = d.get('sigs', {})
    if isinstance(sigs, dict):
        for k, v in sorted(sigs.items()):
            if isinstance(v, dict):
                out.append('sig %s: updated=%s sig=%s' % (k, v.get('updated', v.get('ts', '')), str(v.get('sig', ''))[:20]))
            else:
                out.append('sig %s: %s' % (k, str(v)[:60]))
    cl = d.get('cleared', {})
    if isinstance(cl, dict):
        for k, v in sorted(cl.items()):
            if isinstance(v, dict):
                out.append('cleared %s: ts=%s by=%s' % (k, v.get('ts', v.get('at', '')), v.get('by', v.get('machine', ''))))
            else:
                out.append('cleared %s: %s' % (k, str(v)[:60]))
open('results/_r690bmb_fuse_cmp.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('written %d lines' % len(out))
