# r663: pool face settle via internal sync_face API (r661 precedent) --
# my S0 r437 checkout replayed the shared pool face; settle to merged lane view
# before pool_dualrun evidence collection to avoid false drift.
import sys
sys.path.insert(0, 'scripts')
import merge_lane_views as mlv

for face in ('runnable_pool', 'crash_fuse'):
    try:
        r = mlv.sync_face(face)
        print(face, 'sync_face ->', str(r)[:220])
    except Exception as e:
        print(face, 'sync_face err:', str(e)[:150])
