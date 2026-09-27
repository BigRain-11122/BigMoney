# _r336bmb_gc_verify.py -- escape-valve branch GC content-verify per R323 law:
# git cherry patch-id up front (informational across conflict-resolved replays) + content
# anchors (files-present + durable text anchors in main). NEVER merge-base --is-ancestor.
import subprocess


def sh(*args):
    r = subprocess.run(list(args), capture_output=True)
    assert r.returncode == 0, (args, r.stderr.decode())
    return r.stdout.decode('utf-8', 'replace')


def sh_ok(*args):
    r = subprocess.run(list(args), capture_output=True)
    return r.returncode == 0


main_files = set(sh('git', 'ls-tree', '-r', '--name-only', 'main').splitlines())
report = {}
for branch in ['origin/machine/bm-b-r334', 'origin/machine/bm-b-r335']:
    bfiles = set(sh('git', 'ls-tree', '-r', '--name-only', branch).splitlines())
    missing = sorted(bfiles - main_files)
    cherry = sh('git', 'cherry', 'main', branch)
    plus = sum(1 for l in cherry.splitlines() if l.startswith('+'))
    minus = sum(1 for l in cherry.splitlines() if l.startswith('-'))
    anchors = []
    # durable anchors: resolver/closeout scripts landed via replay
    for f in ['results/_r334bmb_closeout.py', 'results/_r334bmb_resolve4.py', 'results/_r335bmb_resolve.py',
              'results/_r335bmb_probe_race.py', 'results/_r339bma_codeley_archive.py']:
        if f in bfiles:
            anchors.append((f, f in main_files))
    rr = sh('git', 'show', 'main:logs/iteration-loop/round_reports.md')
    anchors.append(('round_reports r334 line', '| r334 bm-b |' in rr))
    anchors.append(('round_reports r335 line', '| r335 |' in rr))
    hd = sh('git', 'show', 'main:research/HANDOVER.md')
    anchors.append(('HANDOVER r335 bm-b 5x row', 'round 335 bm-b' in hd))
    ok_files = (len(missing) == 0)
    ok_anchors = all(v for _, v in anchors)
    report[branch] = dict(missing=missing, cherry_plus=plus, cherry_minus=minus,
                          anchors=[(k, v) for k, v in anchors], ok=ok_files and ok_anchors)
    print(branch)
    print('  missing-in-main files:', missing if missing else 'NONE')
    print('  cherry patch-id: +%d not-equiv / -%d equiv (resolved-replay deltas expected)' % (plus, minus))
    for k, v in anchors:
        print('  anchor %-38s %s' % (k, 'PASS' if v else 'FAIL'))
    print('  -> %s' % ('SAFE-TO-GC' if report[branch]['ok'] else 'KEEP (verification failed)'))
assert all(v['ok'] for v in report.values()), 'GC verification failed -- refuse deletion'
print('GC-VERIFY-PASS both branches fully landed by content anchors')
