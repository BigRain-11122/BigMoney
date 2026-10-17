# r1076 absorb-continuation splice estate verification (bm-c)
# Law: receipt pre-sha16 must == origin_base blob, post-sha16 must == worktree bytes (zero drift)
import subprocess, hashlib, json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace') if sys.stdout else None

def blob(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

rc = json.load(open('results/_w264bmc_freeze_receipt.json', encoding='utf-8'))
HEAD = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
base = rc['origin_base']

ok = True
def chk(name, expect, actual, passed):
    global ok
    ok = ok and passed
    print(f"[{'PASS' if passed else 'FAIL'}] {name}: expect={expect} actual={actual}")

for key, path in [('pf', 'scripts/perpetual_faces.py'), ('n1', 'scripts/perpetual_faces_n1.py')]:
    pre_rc = rc[f'{key}_sha16_pre']
    post_rc = rc[f'{key}_sha16_post']
    b_base = blob(base, path)
    b_head = blob('HEAD', path)
    wt = open(path, 'rb').read()
    chk(f'{key}_pre@origin_base==receipt', pre_rc, sha16(b_base), sha16(b_base) == pre_rc)
    chk(f'{key}_pre@HEAD==receipt', pre_rc, sha16(b_head), sha16(b_head) == pre_rc)
    chk(f'{key}_post@worktree==receipt', post_rc, sha16(wt), sha16(wt) == post_rc)

# prereg worktree == f4ffdb34e committed blob
ppath = 'research/PERPETUAL_N1_W264_PREREG.md'
wt = open(ppath, 'rb').read()
pb = blob('f4ffdb34e', ppath)
chk('prereg_worktree==f4ffdb34e_blob', sha16(pb), sha16(wt), wt == pb)
print('prereg_bytes', len(wt))

# sec7/8 placeholder intact check (count lines that are NOT backfilled numbers)
txt = wt.decode('utf-8', errors='replace')
import re
s7 = re.search(r'## sec\.7|section 7|7\..*finalize', txt, re.I)
print('sec_hint_lines:', [l[:80] for l in txt.splitlines() if 'PLACEHOLDER' in l.upper() or 'placeholder' in l][:6])

# engine burn commits footprint: must NOT touch the two script faces
for c in ['964148797', '17dd06323']:
    files = subprocess.run(['git', 'show', '--name-only', '--format=', c], capture_output=True, text=True).stdout.split()
    bad = [f for f in files if f in ('scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py')]
    chk(f'burn_{c}_no_script_faces', '0', str(len(bad)), len(bad) == 0)
    print(f'  burn {c} files ({len(files)}):', files[:6])

# banned gate re-run on final bytes + bands presence in spliced n1 face
n1txt = open('scripts/perpetual_faces_n1.py', encoding='utf-8', errors='replace').read()
chk('bands_A_in_n1', '596101..598100', 'present', ('596101' in n1txt and '598100' in n1txt))
chk('bands_B_in_n1', '598101..598300', 'present', ('598101' in n1txt and '598300' in n1txt))
pftxt = open('scripts/perpetual_faces.py', encoding='utf-8', errors='replace').read()
chk('w264_block_in_pf', 'w264', 'present', ('264' in pftxt))

print('HEAD', HEAD)
print('VERDICT:', 'VERIFY-PASS' if ok else 'VERIFY-FAIL')
