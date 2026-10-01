# -*- coding: utf-8 -*-
# r538 bm-a: reconcile drift diagnosis -- merged view vs shared blob per face (read-only)
import importlib.util, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

spec = importlib.util.spec_from_file_location('mlv', 'scripts/merge_lane_views.py')
mlv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mlv)

for face in ['compute_audit', 'gate_attrition']:
    print('=' * 15, face, '=' * 15)
    merged = mlv.face_view(face)  # deterministic merged dict (face_view = merged reader)
    shared = json.load(open(f'results/{face}.json', encoding='utf-8'))
    # structural compare on the ledger keys
    for k in set(list(merged.keys()) + list(shared.keys())):
        mv, sv = merged.get(k), shared.get(k)
        if mv == sv:
            continue
        tm, ts_ = (len(mv) if hasattr(mv, '__len__') else 1), (len(sv) if hasattr(sv, '__len__') else 1)
        print(f'  DIFF key={k!r}: merged_len={tm} shared_len={ts_}')
        if isinstance(mv, list) and isinstance(sv, list):
            mrows = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in mv}
            srows = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in sv}
            only_m = mrows - srows
            only_s = srows - mrows
            print(f'    rows only in MERGED: {len(only_m)}')
            for r in list(only_m)[:3]:
                print('      +', r[:170])
            print(f'    rows only in SHARED: {len(only_s)}')
            for r in list(only_s)[:3]:
                print('      -', r[:170])
        elif isinstance(mv, dict) and isinstance(sv, dict):
            mk, sk = set(mv), set(sv)
            print('    keys only merged:', sorted(mk - sk)[:6])
            print('    keys only shared:', sorted(sk - mk)[:6])
            for k2 in sorted(mk & sk):
                if mv[k2] != sv[k2]:
                    print(f'    val diff {k2!r}: merged={str(mv[k2])[:80]} shared={str(sv[k2])[:80]}')
                    break
