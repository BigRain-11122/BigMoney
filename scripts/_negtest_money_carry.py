import json, io, shutil, subprocess, sys, os

FACE = 'results/money_carry_one_sided_repair.json'
BAK = FACE + '.negtest.bak'
shutil.copy2(FACE, BAK)


def run_check():
    p = subprocess.run([sys.executable, 'scripts/money_carry_one_sided_repair.py', '--check'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def edit(fn):
    shutil.copy2(BAK, FACE)
    with io.open(FACE, encoding='utf-8') as f:
        face = json.load(f)
    fn(face)
    with io.open(FACE, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write('\n')


try:
    def n3(face):
        face['upstream']['cash_vehicle_rule']['CONSOLIDATION_JUMP'] = -0.006
    edit(n3)
    rc, out = run_check()
    print('N3 rule-change rc=%d stale_in_text=%s' % (rc, 'STALE' in out))
    print('   ', out.strip().split('\n')[-1][:170])

    def n4(face):
        face['upstream']['spike_share'] = 0.9
    edit(n4)
    rc, out = run_check()
    print('N4 spike_share rc=%d stale_in_text=%s' % (rc, 'STALE' in out))
    print('   ', out.strip().split('\n')[-1][:170])

    # N5: a jump's date is hand-edited -> rc1 (the jump list is a contract, not decoration)
    def n5(face):
        for r in face['rows']:
            if r.get('jumps'):
                r['jumps'][0]['date'] = '1999-01-01'
                break
    edit(n5)
    rc, out = run_check()
    print('N5 jump-date rc=%d stale_in_text=%s' % (rc, 'STALE' in out))
    print('   ', out.strip().split('\n')[-1][:170])
finally:
    shutil.copy2(BAK, FACE)
    os.remove(BAK)
    rc, out = run_check()
    print('RESTORED rc=%d' % rc)
