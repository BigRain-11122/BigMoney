# -*- coding: utf-8 -*-
import json
d = json.load(open('results/_r789bma_w163_face_probe_receipt.json', encoding='utf-8'))
keys = ['"a_seed_base": 371_204,', '"b_exit_seed_base": 373_204,',
        '162: {"a": (371_204, 373_203), "b_exit": (373_204, 373_403),', '162: {"batch"',
        'W161 row bm-a r785 freeze', '678a07d4f, SINGLE STATE zero seat gap W2..W161 all',
        'bm-a r785 freeze 678a07d4f', 'bm-a r787 freeze', 'r787 bm-a freeze',
        'W161 finalize landed same-window r786', 'W161 finalize one-pass bm-a r786',
        'W161 bm-a r786 one-pass', '_r787bma_w162_probe_receipt.json',
        '_r787bma_w162_band_gate.json', 'r785 gate leg3', 'r785 gate',
        'r786 sec8 succession', 'r786 sec8',
        'MSG-2026-10-06-175x', 'bma-w162-seat', 'MSG-175x', '1d43d7906',
        '373_204..375_203', '373_404..373_603',
        'W163 A window; W163 freezer MUST re-derive on the post-W162',
        'jumps to 373_204, first-clean 373_204..373_403 hops=1',
        'jumps to 373_204 -> 373_204..373_403,', '373_204 and lands 373_204..373_403',
        'own-wave A window reserved jumps to 373_204, first-clean ',
        '== 371_204 == 371_203 + 1', '== 373_204 == 373_203 + 1',
        'set(range(371_204, 373_204))', 'set(range(373_204, 373_404))',
        '371_203+1', '373_203+1',
        'PERPETUAL_N1_W162_PREREG.md', 'PERPETUAL-N1-W162', 'n1_w162_results.json',
        'n1_w162', 'n1w162', '759,612', '352,120', 'ONE HUNDRED-AND-FIFTY-SECOND',
        'engine_owner rows 151', 'rows 77 + candidate', 'seventy-eighth', 'twenty-first',
        'move deferred to the W163 finalize window', 'W162 seat still in', 'facts helper',
        'r787', 'r786', 'r785', 'W162', 'W161', '162', '161']
for k in keys:
    c = d['needles'].get(k)
    if c is None:
        print('MISSING FROM PROBE:', repr(k))
        continue
    faces = {f: c[f] for f in ('pf_blk', 'entry', 'mat', 'claim') if c[f] > 0}
    print(f"{k[:64]!r}: faces={faces} fullfile(pf={c['pf']}, n1={c['n1']})")
