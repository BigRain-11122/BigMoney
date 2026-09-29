import re
SRC = open('results/_r442bmb_stage3c.py', encoding='utf-8').read()
fails = []
applied = []


def rex(pattern, repl, tag, count=1):
    global SRC
    hits = re.findall(pattern, SRC, flags=re.M)
    if len(hits) != count:
        fails.append(f'[{tag}] expected {count} got {len(hits)}')
        return
    SRC = re.sub(pattern, repl, SRC, flags=re.M)
    applied.append(tag)


# 1. screen-prep metas (12-space, 2408)
rex(r'(            "amp_meta": amp_meta, "mom_meta": mom_meta,\n)',
    r'\1            "std_meta": std_meta,\n', 'metas-12')
# 2. judge-prep vacuous metas (16-space, 3149)
rex(r'(                "amp_meta": amp_meta, "mom_meta": mom_meta,\n)',
    r'\1                "std_meta": std_meta,\n', 'metas-16')
# 3. jprep print: std print after the amp/mom print statement
rex(r'( +f"\{mom_meta\[\'L\'\]\[\'decidable_days\'\]"\}\)")\n(    return 0)',
    r'\1\n    print(f"std meta L 120-bar-warmup "\n'
    r'          f"{std_meta[\'L\'][\'open_days\']}open/"\n'
    r'          f"{std_meta[\'L\'][\'closed_days\']}closed decidable "\n'
    r'          f"{std_meta[\'L\'][\'decidable_days\']} std10-open "\n'
    r'          f"{std_meta[\'L\'][\'std10_open_days\']}")\n\2',
    'jprep-print')
# 4. screen worker std_state compute line
rex(r'(    mom_state = mom_state_series\(prices\)\n)(    state = \{)',
    r'\1    std_state = std_state_series(prices)\n\2', 'worker-state')
open('results/_r442bmb_stage3c.py', 'w', encoding='utf-8').write(SRC)
print('applied:', applied)
print('fails:', fails)
