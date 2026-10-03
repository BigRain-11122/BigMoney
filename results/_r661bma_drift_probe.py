"""r661: drift direction probe v2 (face_view + sync_face internal API)."""
import json
import sys

sys.path.insert(0, 'scripts')
import merge_lane_views as mlv

for face in ('gate_attrition', 'post_review_criteria'):
    view = mlv.face_view(face)
    shared_path = view.get('shared_path') if isinstance(view, dict) else None
    print(face, '| view keys:', list(view.keys())[:8] if isinstance(view, dict) else type(view))
    if isinstance(view, dict):
        for k in ('drift', 'shared_blob', 'merged', 'out'):
            if k in view:
                v = view[k]
                print(' ', k, type(v).__name__, (str(v)[:100] if not isinstance(v, (dict, list)) else f'len={len(v)}'))
    # attempt internal sync_face
    try:
        r = mlv.sync_face(face)
        print(' ', 'sync_face ->', str(r)[:200])
    except Exception as e:
        print(' ', 'sync_face err:', str(e)[:150])
