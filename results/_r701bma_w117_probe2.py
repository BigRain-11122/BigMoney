# W117 freeze-support probe v2: correct tuple format, tails + upstream + vacancy.
import re, json, os, glob, subprocess
from collections import Counter

def read(p):
    return open(p, encoding='utf-8', errors='replace').read()

out = {}
pf = read('scripts/perpetual_faces.py')
rows = re.findall(r'(\d+)\s*:\s*\{"a":\s*\(([\d_]+),\s*([\d_]+)\),\s*"b_exit":\s*\(([\d_]+),\s*([\d_]+)\)\}', pf)
d = {}
for r in rows:
    d[int(r[0])] = r
ks = sorted(d)
out['pf_rows'] = len(ks)
out['pf_tail'] = [d[k] for k in ks[-5:]]
out['pf_max_wave'] = ks[-1] if ks else None
own = re.findall(r'"engine_owner"\s*:\s*"(\w+)"', pf)
out['owner_counts'] = dict(Counter(own))
# last canon-style row text (engine_owner neighborhood for W114..W116)
for k in ks[-3:]:
    m = re.search(r'(\n[^\n]*\b%d\b[^\n]*\n[^\n]*engine_owner[^\n]*)' % k, pf)
    if m:
        out.setdefault('canon_rows', {})[k] = m.group(1)[:400]

n1f = read('scripts/perpetual_faces_n1.py')
wrows = re.findall(r'(\d+)\s*:\s*\{"a":\s*\(([\d_]+),\s*([\d_]+)\),\s*"b_exit":\s*\(([\d_]+),\s*([\d_]+)\)\}', n1f)
d2 = {}
for r in wrows:
    d2[int(r[0])] = r
ks2 = sorted(d2)
out['n1_rows'] = len(ks2)
out['n1_tail'] = [d2[k] for k in ks2[-4:]]
out['n1_max_wave'] = ks2[-1] if ks2 else None

# upstream finalize landed: search any results json with n1_w11x_results
res = sorted(glob.glob('results/n1_w*_results.json'), key=lambda p: int(re.search(r'n1_w(\d+)', p).group(1)))
out['finalizes'] = [os.path.basename(p) for p in res[-5:]]
# also check research/perpetual/ dir variants
res2 = sorted(glob.glob('results/**/n1_w*_results.json', recursive=True))
out['finalizes_recursive_last'] = [os.path.basename(p) for p in res2[-6:]]

# burned product dirs
for w in (113, 114, 115, 116, 117):
    hits = glob.glob(f'results/**/n1_w{w}/*.json', recursive=True) + glob.glob(f'results/n1_w{w}*')
    out[f'w{w}_prod'] = len(hits)

# seat scan: local + origin inbox/processed filenames
seats = []
for base, dirs in (('', ['fleet/inbox', 'fleet/inbox/processed']),):
    for dd in dirs:
        if os.path.isdir(dd):
            for name in os.listdir(dd):
                if re.search(r'W11[4-9]', name):
                    seats.append(('local:' + dd, name))
        r = subprocess.run(['git', 'ls-tree', '--name-only', f'origin/main:{dd}'], capture_output=True, text=True, encoding='utf-8')
        if r.returncode == 0:
            for name in r.stdout.split():
                if re.search(r'W11[4-9]', name):
                    seats.append(('origin:' + dd, name))
out['seats_recent'] = seats

# prereg files on origin for W115..W117
r = subprocess.run(['git', 'ls-tree', '--name-only', 'origin/main:research'], capture_output=True, text=True, encoding='utf-8')
if r.returncode == 0:
    out['prereg_recent_origin'] = [x for x in r.stdout.split() if re.search(r'PERPETUAL_N1_W11[4-9]', x)]

print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
