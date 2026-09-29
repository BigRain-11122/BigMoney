import re
SRC = open('results/_r442bmb_stage3c.py', encoding='utf-8').read()
lines = SRC.split('\n')
probes = {
    'member-loop': 'for member, gate_name in ((tl7.STREAK_MEMBER',
    'core48-out': '"core48": mom_meta_core',
    'c48-rate': 'core48_mom_open_rate',
    'metas-out': '"amp_meta": amp_meta, "mom_meta": mom_meta,',
    'prep-print': 'mom meta L/D 139-bar-warmup',
    'worker-state': 'mom_state = mom_state_series(prices)',
    'worker-dict': '"mom_state": mom_state}',
    'fin-seglist': '(amp_seg, af), (mom_seg, mf),',
    'fin-fc': '"mom_face_counts": mom_counts,',
    'fin-audit1': 'mom 139-bar warmup',
    'fin-audit2': 'mom_oversold keep face',
    'jcell-degen': 'mom_zeroed_x2": 0',
    'jprep-print': 'mom meta L/D',
}
for tag, pat in probes.items():
    hits = [i + 1 for i, l in enumerate(lines) if pat in l]
    print(f'{tag}: {hits}')
# dump context for the ones needing exact text
for ln in [h for h in
           [i + 1 for i, l in enumerate(lines) if '"core48": mom_meta_core' in l]
           + [i + 1 for i, l in enumerate(lines)
              if 'core48_mom_open_rate' in l]
           + [i + 1 for i, l in enumerate(lines) if 'mom 139-bar warmup' in l]
           + [i + 1 for i, l in enumerate(lines)
              if 'mom_oversold keep face' in l]
           + [i + 1 for i, l in enumerate(lines)
              if '"mom_state": mom_state}' in l]
           + [i + 1 for i, l in enumerate(lines)
              if 'mom_zeroed_x2": 0' in l]
           + [i + 1 for i, l in enumerate(lines)
              if 'mom meta L/D' in l]]:
    a = max(0, ln - 3)
    print(f'---- ctx @ {ln} ----')
    for j in range(a, min(len(lines), ln + 2)):
        print(f'{j+1:5d}: {lines[j][:100]}')
