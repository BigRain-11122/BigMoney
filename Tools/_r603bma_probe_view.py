import sys, json
sys.path.insert(0, 'scripts')
import merge_lane_views as mlv

sources = mlv.load_sources('runnable_pool')
merged, notes = mlv.merge_face('runnable_pool', sources)
view = merged
for e in view.get('entries', []):
    if 'FUND-VALUE' in e.get('id', ''):
        print(e['id'], 'status=', e.get('status'),
              'gates=', ('host_gates' in e),
              [(s.get('key', '')[:38], s.get('status'), s.get('owner'))
               for s in e.get('shards', [])])
fn = [n for n in notes if 'FUND-VALUE' in n]
print('--- FUND merge notes (%d) ---' % len(fn))
for n in fn[:12]:
    print(' ', n[:160])
