# r579 bm-b D-19 decisions watermark + new-bar date + monthly trio presence check
import hashlib, json, os, subprocess, sys, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
EXPECTED = '937A373DA4339EDC70E95D2EC3E2AC5B1B62E298C834AC84B5FD2955EC5FD4E1'

grp = None
for root in (r'K:\Fluxgroup\FluxGroup', r'C:\Fluxgroup\FluxGroup'):
    r = subprocess.run(['git', '-C', root, 'rev-parse', '--is-inside-work-tree'],
                       capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip() == 'true':
        grp = root
        break
if grp is None:
    print('D19 group_repo=none (r481 bm-b special case, honest skip)')
else:
    subprocess.run(['git', '-C', grp, 'fetch', 'origin'], capture_output=True)
    r = subprocess.run(['git', '-C', grp, 'show', 'origin/main:docs/decisions.md'],
                       capture_output=True)
    if r.returncode != 0:
        print('D19 decisions_path_missing rc=%d (honest report)' % r.returncode)
    else:
        sha = hashlib.sha256(r.stdout).hexdigest().upper()
        print('D19 decisions_sha=%s match=%s' % (sha, 'MATCH-unchanged' if sha == EXPECTED else 'CHANGED'))

# last ETF bar date (new-bar gate for paper block)
p = r'data\daily\sh510300.csv'
with open(p, 'rb') as f:
    f.seek(max(0, os.path.getsize(p) - 300))
    tail = f.read().decode('utf-8', 'replace').strip().splitlines()
print('LAST_BAR=' + tail[-1].split(',')[0])

# monthly trio presence (October first-round duty check)
try:
    sa = json.load(open('results/science_audit.json', encoding='utf-8'))
    hist = sa.get('history', [])
    last = hist[-1].get('month', hist[-1].get('ts', '?')) if hist else '?'
    print('SCIENCE_AUDIT_last=%s' % last)
except Exception as e:
    print('SCIENCE_AUDIT_read_err=%s' % e)
print('BRIEFINGS=' + ','.join(sorted(os.path.basename(x) for x in glob.glob('results/briefings/BRIEF-*.md')))[-120:])
print('SELF_REVIEW=' + ','.join(sorted(os.path.basename(x) for x in glob.glob('results/self_review/SELF-REVIEW-*.md')))[-120:])
