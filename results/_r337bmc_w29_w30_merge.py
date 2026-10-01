# -*- coding: utf-8 -*-
# r337 bm-c constructive merge: W29 (mine, crashed-r336 half-work adopted) x
# W30 (bm-a r541, landed mid-adoption) -- r531 law: theirs-as-base + my
# increment blocks inserted by content anchor + their stale W30 prior-wave
# pin minimally amended (+29, r531-1 minimal-disclosure law).
import io, sys, os, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'

def git(*a):
    r = subprocess.run(['git', '-C', R] + list(a), capture_output=True)
    if r.returncode != 0:
        print('GIT FAIL', a, r.stderr.decode('utf-8', 'replace')[:300])
        sys.exit(1)
    return r.stdout.decode('utf-8')

def blob(path):
    return git('show', 'origin/main:' + path)

def read(p):
    with open(os.path.join(R, p), 'r', encoding='utf-8', newline='') as f:
        return f.read().replace('\r\n', '\n')   # local trees are CRLF, repo blobs LF

def write(p, text):
    with open(os.path.join(R, p), 'w', encoding='utf-8', newline='') as f:
        f.write(text)

def extract(text, start_marker, end_marker, name, skip_anchor=True):
    i = text.index(start_marker)
    j = text.index(end_marker, i)
    s = i + len(start_marker) if skip_anchor else i
    block = text[s:j]
    assert block.strip(), 'empty block ' + name
    return block

def insert_before(base, anchor, block, name):
    i = base.index(anchor)   # raises if absent -> hard fail, good
    return base[:i] + block + base[i:]

# idempotency: start from the pre-merge (my W29-only) state
subprocess.run(['git', '-C', R, 'checkout', 'HEAD', '--',
                'scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py',
                'research/PERPETUAL_FACES.md'], check=True)

# ---------------- file 1: scripts/perpetual_faces.py ------------------------
mine = read('scripts/perpetual_faces.py')
anchor28 = '    28: {"a": (99_004, 101_003), "b_exit": (40_451, 40_650),\n         "engine_owner": "bm-b"},\n'
my_w29_entry = extract(mine, anchor28, '\n}\n# v1 + ext', 'pf W29 block')
base = blob('scripts/perpetual_faces.py')
assert base.count(anchor28) == 1
merged = insert_before(base, '    # W30 (r541 bm-a, prereg-time extension per the W28 row\'s W29+', my_w29_entry, 'pf')
assert merged.count('29: {"a": (101_004, 103_003)') == 1 and merged.count('30: {"a": (103_004, 105_003)') == 1
write('scripts/perpetual_faces.py', merged)
print('pf.py merged: W29 entry inserted before W30 comment, both present')

# ---------------- file 2: scripts/perpetual_faces_n1.py ----------------------
mine = read('scripts/perpetual_faces_n1.py')
base = blob('scripts/perpetual_faces_n1.py')

# 2a. WAVE_CONFIGS block
anchor28c = '                 "b_exit_seed_base": 40_451,    # law sec.4 W28 B: 40_451..40_650 (arithmetic)\n                 "shard_subdir": "n1_w28", "out_name": "n1_w28_results.json",\n                 "engine_owner": "bm-b"},\n'
assert mine.count(anchor28c) == 1 and base.count(anchor28c) == 1
my_cfg = extract(mine, anchor28c, '         }\n\nPREREG = WAVE_CONFIGS[2]["prereg"]', 'n1 W29 cfg')
merged = insert_before(base, '            # W30 (r541 bm-a, prereg-time extension per the W28 row\'s W29+', my_cfg, 'n1-cfg')
assert merged.count('"a_seed_base": 101_004') == 1 and merged.count('"a_seed_base": 103_004') == 1

# 2b. selftest materializer leg (mine before theirs; include the marker line)
my_leg = extract(mine, '    # --- W29 materializer face (r336 bm-c freeze) ---', '    # --- T-141 s2 lane face', 'n1 W29 selftest leg', skip_anchor=False)
merged = insert_before(merged, '    # --- W30 materializer face (r541 bm-a freeze) ---', my_leg, 'n1-leg')

# 2c. guard-string block (mine before theirs; include the marker line)
my_guard = extract(mine, '          "+ W29 materializer face [same guard set', '          "+ T-141 s2 "', 'n1 W29 guard str', skip_anchor=False)
merged = insert_before(merged, '           "+ W30 materializer face [same guard set, dep=W17..W28 "', my_guard, 'n1-guard')

# 2d. their stale W30 prior-wave pin: +29 (r531-1 minimal disclosure)
old_pin = ('        assert sorted(w for w in WAVE_CONFIGS if w < 30) == \\\n'
           '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,\n'
           '             20, 21, 22, 23, 24, 25, 26, 27, 28], \\\n'
           '            "W30 prior-wave set must derive from registry keys (no 15/29)"')
new_pin = ('        # (r337 bm-c same-window amendment: W29 registered -> auto-joined the\n'
           '        #  set by registry derivation exactly as this freeze-window comment\n'
           '        #  projected; expected list +29 per r531 minimal-disclosure law.)\n'
           '        assert sorted(w for w in WAVE_CONFIGS if w < 30) == \\\n'
           '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,\n'
           '             20, 21, 22, 23, 24, 25, 26, 27, 28, 29], \\\n'
           '            "W30 prior-wave set must derive from registry keys (no 15)"')
assert merged.count(old_pin) == 1, 'W30 stale pin not found verbatim'
merged = merged.replace(old_pin, new_pin, 1)
write('scripts/perpetual_faces_n1.py', merged)
print('n1.py merged: cfg + selftest leg + guard str inserted; W30 pin +29 amended')

# ---------------- file 3: research/PERPETUAL_FACES.md -----------------------
mine = read('research/PERPETUAL_FACES.md')
my_row = extract(mine, '- N1 波29（r336 bm-c 落 prereg 时展行', '\n## §5 计账', 'canon W29 row', skip_anchor=False)
base = blob('research/PERPETUAL_FACES.md')
merged = insert_before(base, '- N1 波30（r541 bm-a 落 prereg 时展行', my_row, 'canon')
assert merged.count('- N1 波29（r336 bm-c') == 1 and merged.count('- N1 波30（r541 bm-a') == 1
write('research/PERPETUAL_FACES.md', merged)
print('canon merged: W29 row before W30 row')

# ---------------- sync origin-only files needed by local selftest -----------
for p in ('research/PERPETUAL_N1_W30_PREREG.md',
          'results/perpetual_faces/n1_w27_results.json',
          'results/perpetual_faces/n1_w28_results.json'):
    subprocess.run(['git', '-C', R, 'checkout', 'origin/main', '--', p], check=True)
    print('checked out from origin:', p)
print('MERGE_DONE')
