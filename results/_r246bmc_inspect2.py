import io, sys, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def stage(sid, path):
    b = subprocess.run(['git', 'show', '%s:%s' % (sid, path)], capture_output=True).stdout
    return json.loads(b.decode('utf-8-sig'))

for p in ['results/crash_fuse.json', 'results/regime_state.json']:
    print('=' * 20, p)
    o = stage(':2', p)
    t = stage(':3', p)
    for name, d in (('OURS(bm-b r444)', o), ('THEIRS(r246 mine)', t)):
        print(name, 'keys:', list(d.keys())[:14])
        for k, v in list(d.items())[:14]:
            if isinstance(v, dict):
                print('   %s: dict %s' % (k, list(v.keys())[:8]))
            elif isinstance(v, list):
                print('   %s: list len=%d' % (k, len(v)))
            else:
                print('   %s: %r' % (k, v))

# auto-merged files integrity check (worktree state now)
for p in ['results/compute_audit.json', 'results/gate_attrition.json']:
    try:
        d = json.load(open(p, encoding='utf-8-sig'))
        extra = ''
        if 'history' in d:
            extra = ' history=%d' % len(d['history'])
        print('AUTO-MERGED OK parse:', p, extra)
    except Exception as ex:
        print('AUTO-MERGED BROKEN:', p, ex)
