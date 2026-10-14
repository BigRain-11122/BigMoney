"""r996 bm-a closeout addendum: report addendum line + state sync/push_verified backfill."""
import json, subprocess, datetime

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
GG = 'C:/Program Files/Git/cmd/git.exe'
NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

ADDENDUM = (NOW + ' | r996 bm-a addendum (post-push closeout) | closeout push raced origin x3 '
    '(bm-b r944 waiting-state push + addenda in-flight); rebase cycle-2/3 replayed clean; '
    'PRE-COMMIT CLAW correctly caught marker-contaminated satengine face mid-race (auto-merge '
    'marker face staged) BUT sequencer-continue committed the staged residue bypassing the claw '
    '-> contaminated intermediates 3a47f1034/305f5931d (6/3 marker lines in '
    'results/saturation_engine/face_bm-a.json) -> heal commit cured tip (daemon live-wins clean '
    'face re-landed + pit line research/pit-git-resolver-rebase2.md r996 claw-bypass variant); '
    'final push a9ab3b51d..4a1a70e72 PUSH_RC=0 behind=0 self-verified (rev-list 0); W242 probe '
    'receipt on-disk at pushed tip (disk-actor watch continues); duplicate pre-round checkpoint '
    'pair 3dc435d58+31db02888 noted (broken-loop double commit, idempotent content, cosmetic) | '
    '[r996 bm-a addendum]')
with open(ROOT + r'\round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(ADDENDUM + '\n')

# verify marker-free at pushed tip + W242 receipt in tree
r1 = subprocess.run([GG, 'show', 'HEAD:results/saturation_engine/face_bm-a.json'],
                    capture_output=True, cwd=ROOT).stdout.decode('utf-8', 'replace')
mk = sum(r1.count(x) for x in ('<<<<<<<', '=======', '>>>>>>>'))
r2 = subprocess.run([GG, 'ls-tree', '--name-only', 'HEAD',
                     'results/_w242bma_20261014_probe_receipt.json'],
                    capture_output=True, cwd=ROOT).stdout.decode().strip()
print('tip markers =', mk, '| W242 receipt in tree =', bool(r2))

sp = ROOT + r'\state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
tip = subprocess.run([GG, 'rev-parse', '--short', 'origin/main'], capture_output=True,
                     cwd=ROOT).stdout.decode().strip()
st['push_verified'] = {'ts': NOW,
    'note': 'r996: closeout push a9ab3b51d..4a1a70e72 rc0 behind=0 verified (3-race cycle; heal commit cured claw-bypass marker contamination at tip; addendum line landed)',
    'origin_tip': tip}
st['sync'] = {'ahead_behind': '0/0', 'origin_tip': tip, 'ts': NOW,
    'note': 'r996: closeout push a9ab3b51d..4a1a70e72 verified (range line + rev-list 0); local-not-at-origin commit count=0'}
st['last_round_closed'] = st.get('last_round_closed') or NOW
st['verify'] = st.get('verify', '') + ' + tip marker-free=' + str(mk) + ' + push 4a1a70e72 behind=0'
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state sync backfilled, origin_tip =', tip)
