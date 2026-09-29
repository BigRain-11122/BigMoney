"""r442 bm-b: stage-3c fixups v2 (clean regex)."""
import re
SRC = open('results/_r442bmb_stage3c.py', encoding='utf-8').read()
fails = []
applied = []


def rex(pattern, repl, tag, count=1, flags=re.M):
    global SRC
    hits = re.findall(pattern, SRC, flags=flags)
    if len(hits) != count:
        fails.append(f'[{tag}] expected {count} got {len(hits)}')
        return
    SRC = re.sub(pattern, repl, SRC, flags=flags)
    applied.append(tag)


# 1. member loops (two sites still without std member)
rex(r'\(MOM_MEMBER, "mom"\)\):',
    '(MOM_MEMBER, "mom"), (STD_MEMBER, "std")):',
    'member-loops', count=2)
# 2. G-MOM core48/legL block -> G-STD after
rex(r'("G-MOM": \{"pass": True,\n'
    r'\s*"core48": mom_meta_core,\n'
    r'\s*"legL": mom_meta,)',
    r'\1\n'
    r'                       "G-STD": {"pass": True,\n'
    r'                                 "core48": std_meta_core,\n'
    r'                                 "legL": std_meta},', 'gmom-block')
# 3. core48 disclosure
rex(r'("core48_mom_open_rate":\n'
    r'\s*MOM_ANCHOR\["core48_mom_open_rate"\],)',
    r'\1\n'
    r'                                     "core48_std20_open_rate":\n'
    r'                                     STD_ANCHOR['
    r'"core48_std20_open_rate"],', 'c48-disc')
# 4. screen-prep outputs metas (12-space)
rex(r'(           "amp_meta": amp_meta, "mom_meta": mom_meta,\n)',
    r'\1           "std_meta": std_meta,\n', 'prep-out-metas-12')
# 5. judge-prep outputs metas (16-space)
rex(r'(                "amp_meta": amp_meta, "mom_meta": mom_meta,\n)',
    r'\1                "std_meta": std_meta,\n', 'jprep-out-metas-16')
# 6. jprep "mom_meta": mom_meta, alone-in-dict site (11-space)
rex(r'(           "mom_meta": mom_meta,\n)'
    r'(?!\s+"std_meta")',
    r'\1           "std_meta": std_meta,\n', 'jprep-out-mom-only')
# 7. worker dict
rex(r'(\s+"mom_state": mom_state\})',
    r'\1\n              "std_state": std_state}', 'worker-dict')
# 8. fin seglist
rex(r'(\(tstate_seg, tf\), \(amp_seg, af\), \(mom_seg, mf\),)',
    r'\1\n                         (std_seg, stf),', 'fin-seglist')
# 9. screen finalize face counts
rex(r'(           "amp_face_counts": amp_counts,\n'
    r'           "mom_face_counts": mom_counts,)',
    r'\1\n           "std_face_counts": std_counts,', 'fin-fc')
# 10. audit warmup
rex(r'("mom 139-bar warmup ")',
    r'"mom 139-bar warmup / std 120-bar warmup "', 'fin-audit1')
rex(r'("streak/tstate/amp/mom_na_window_bars\); ")',
    r'"streak/tstate/amp/mom/std_na_window_bars); "', 'fin-audit1b')
rex(r'("warmup bars as mom_closed, BANNED\); ")',
    r'\1\n'
    r'                              "std20_hi/std10_hi keep face = open '
    r'AND "\n'
    r'                              "decidable (same erratum law); "',
    'fin-audit2')
# 11. jcell degenerate
rex(r'("amp_zeroed_x2": 0, "mom_zeroed": 0,\n'
    r'\s*"mom_zeroed_x2": 0,)',
    r'\1\n                         "std_zeroed": 0,'
    r'\n                         "std_zeroed_x2": 0,', 'jcell-degen')
# 12. jprep print f-string
rex(r'(    print\(f"mom meta L/D 139-bar-warmup ")',
    r'    print(f"std meta L 120-bar-warmup "\n'
    r'          f"{std_meta[\'L\'][\'open_days\']}open/"\n'
    r'          f"{std_meta[\'L\'][\'closed_days\']}closed decidable "\n'
    r'          f"{std_meta[\'L\'][\'decidable_days\']} std10-open "\n'
    r'          f"{std_meta[\'L\'][\'std10_open_days\']}")\n'
    r'    print(f"mom meta L/D 139-bar-warmup "', 'jprep-print')
# 13. curve lazy-init duplicate repair
rex(r'(        mom_state = mom_state_series\(prices\)\n'
    r'    std_state = std_state_series\(prices\)\n'
    r'    if std_state is None:)',
    r'        mom_state = mom_state_series(prices)\n'
    r'    if std_state is None:', 'curve-lazy-repair')

open('results/_r442bmb_stage3c.py', 'w', encoding='utf-8').write(SRC)
print('applied:', len(applied), applied)
print('fails:', len(fails))
for f in fails:
    print(' FAIL', f)
