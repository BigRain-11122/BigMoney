# r1074 bm-a postscript: push_verified + sync faces + shadow-ref re-fire note + products ls-tree + commit/push
import subprocess, sys, json, io, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
def g(*args, cwd=REPO):
    r = subprocess.run(['git','-C',cwd]+list(args), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '')+(r.stderr or '')

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
rc, tip = g('rev-parse','origin/main'); tip = tip.strip()
rc, behind = g('rev-list','--count','main..origin/main'); behind = behind.strip()
rc, ahead = g('rev-list','--count','origin/main..main'); ahead = ahead.strip()
PRODS = ['scripts/a5_acceptance_pack.py',
         'results/a5_acceptance/PACK-2026-10-19.json',
         'results/a5_acceptance/PACK-2026-10-19.md',
         'results/a5_acceptance/streak.jsonl',
         'results/_r1074bma_group_plan_receipt.json',
         'results/_r1074bma_s6chain.ps1',
         'results/_r1074bma_closeout.py',
         'round_reports-bm-a.md',
         'state-bm-a.json',
         'fleet/machines/bm-a.json']
# *.log = repo gitignore policy face (r1071 precedent: chain evidence = on-disk
# + report line + state verify); postscript products land with THIS commit
import os
DISK_ONLY = ['results/_r1074bma_s6chain_rc.log']
POSTSCRIPT_PRODS = ['results/_r1074bma_rebase_resolver.py',
                    'results/_r1074bma_rebase_surgery.py',
                    'results/_r1074bma_postscript.py']
ls = []
for p in PRODS:
    rc, out = g('ls-tree','origin/main','%s' % p)
    ls.append('%s:%s' % ('OK' if out.strip() else 'MISS', p))
for p in DISK_ONLY:
    ls.append('%s:%s' % ('OK' if os.path.exists(os.path.join(REPO,p)) else 'MISS', p) + ' (disk-only, gitignore policy)')
print('\n'.join(ls))
missing = [l for l in ls if l.startswith('MISS')]
assert not missing, 'products missing: %r' % missing

PV = {'ts': NOW, 'origin_tip': tip, 'behind': int(behind), 'ahead': int(ahead),
      'ls_tree_products': PRODS,
      'note': ('r1074 delivery: push #1 raced bm-b r1019 postscript (be88d72a21) -> pull --rebase 12-UU regen twins '
               'ts-newer-wins all-mine (resolver v3 generator-superset law) -> r1032-family continue-refused live-fire #6 '
               '-> quit+commit-C rebuilt fe8be10c2d -> update-ref SHORT-NAME re-fired r1012 shadow-ref pit (.git/main loose '
               'shadow; caught by main/HEAD equality assert BEFORE push) -> shadow deleted + full-path refs/heads/main update '
               '-> push landed be88d72a21..fe8be10c2d first-try behind-0; group-plan CAS e9b9163 delivered same round')}

def rd(p):
    with io.open(p, encoding='utf-8') as f: return json.load(f)
def wr(p, d):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=1); f.write('\n')

st = rd('state-bm-a.json')
st['push_verified'] = dict(PV); st['sync'] = dict(PV)
st['last_delivery_verified_at'] = NOW
notes = st.get('notes_r1074', '')
st['notes_r1074'] = notes + (' || POSTSCRIPT: (a) push race vs bm-b r1019 postscript (be88d72a21): 12-UU all regen/probe '
  'faces, resolver v3 took all-mine (my chain 07:58-08:03 re-derives newer than origin 07:46-07:47; REPORT/LIVE twins '
  'generator-identical + attribution-superset per r1071 law); (b) r1032-family continue-refused live-fire #6 at '
  'all-conflicts-fixed state -> quit+commit-C fe8be10c2d rebuilt on be88d72a21 (r1012/r1014 recipe); (c) r1012 '
  'shadow-ref pit RE-FIRED by this window: `git update-ref main <sha>` (short name) wrote a loose shadow .git/main '
  'instead of refs/heads/main -> rev-parse ambiguity + main still at old commit; caught pre-push by main==HEAD equality '
  'assert (surgery script); cure = direct .git/main file delete (never update-ref -d on ambiguous name) + full-path '
  'update-ref refs/heads/main + symbolic-ref reattach; LAW REFRESH: update-ref in surgery scripts MUST use full '
  'refs/heads/<name> path, assert rev-parse main == HEAD pre-push (saved this window from phantom-race push); '
  '(d) watchdog S4U flip access-denied = carried C-20261016-04')
wr('state-bm-a.json', st)
hb = rd('fleet/machines/bm-a.json')
hb['push_verified'] = dict(PV)
wr('fleet/machines/bm-a.json', hb)
print('push_verified + sync faces written; tip', tip[:12], 'behind', behind, 'ahead', ahead)

rc, _ = g('add','-A')
rc, out = g('commit','-m', 'round 1074 postscript: push_verified faces (push race vs bm-b r1019: 12-UU resolver v3 '
           'all-mine ts-newer-wins + r1032 continue-refused #6 quit+commit-C rebuilt fe8be10c2d + r1012 shadow-ref '
           're-fire caught pre-push by equality assert, .git/main shadow deleted + full-path update) + surgery evidence '
           'scripts')
print('commit rc', rc, out.strip()[:160])
if rc == 0:
    rc, out = g('push')
    print('push rc', rc, out.strip()[:200])
    rc, out = g('fetch','origin')
    rc, behind2 = g('rev-list','--count','main..origin/main')
    print('postscript behind:', behind2.strip())
    ok_ps = True
    for p in POSTSCRIPT_PRODS:
        rc, out = g('ls-tree','origin/main','%s' % p)
        stat = 'OK' if out.strip() else 'MISS'
        print('PS-PRODUCT', stat, p)
        ok_ps = ok_ps and stat == 'OK'
    sys.exit(0 if rc == 0 and behind2.strip() == '0' and ok_ps else 1)
print('nothing to commit or push failed'); sys.exit(0 if rc == 1 else 1)
