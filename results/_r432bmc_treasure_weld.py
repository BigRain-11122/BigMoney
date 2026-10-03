# -*- coding: utf-8 -*-
"""r432 bm-c O-2030 weld demo pack (10-08 acceptance evidence).
Demos: engine selftest re-verify + live hard-reject replay (firm/RULES.md rc3)
+ clean-face rc0 + quarantine-mode manifest demo + sweep-class mixed-set
hard-reject. All child calls carry CREATE_NO_WINDOW (r426 law-3 single-shot
form). Receipt -> results/_r432bmc_treasure_weld.json."""
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000


def run(args):
    p = subprocess.run([sys.executable] + args, capture_output=True,
                       creationflags=CREATE, cwd=REPO)
    return p.returncode, (p.stdout or b'').decode('utf-8', 'replace') \
        + (p.stderr or b'').decode('utf-8', 'replace')


def main():
    receipt = {
        "round": "r432 bm-c",
        "order": "O-20261003-2030",
        "law": "firm/TREASURE_PROTECTION_LAW.md v1.0",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "demos": [],
    }

    # 1) engine selftest re-verify on bm-c host
    rc, out = run(['Tools/treasure_guard.py', 'selftest'])
    npass = sum(1 for l in out.splitlines() if '  PASS ' in l)
    receipt["demos"].append({"demo": "engine_selftest", "rc": rc,
                             "pass_count": npass, "tail": out.strip().splitlines()[-1]})
    assert rc == 0 and npass >= 20, 'selftest fail: %s' % out[-300:]

    # 2) live hard-reject replay: protected law file
    rc, out = run(['Tools/treasure_guard.py', 'prescan', 'firm/RULES.md'])
    receipt["demos"].append({"demo": "hard_reject_law_face", "rc": rc,
                             "hit": 'HARD REJECT' in out})
    assert rc == 3 and 'HARD REJECT' in out, 'hard-reject demo fail: %s' % out

    # 3) clean face zero-hit
    rc, out = run(['Tools/treasure_guard.py', 'prescan',
                  'results/_r432bmc_smoke_log.txt'])
    receipt["demos"].append({"demo": "clean_face_zero_hit", "rc": rc})
    assert rc == 0, 'clean-face fail: %s' % out

    # 4) quarantine-mode demo (disposable artifact -> manifest)
    victim = os.path.join(REPO, 'results', '_r432bmc_qdemo_victim.txt')
    with open(victim, 'w', encoding='utf-8') as f:
        f.write('r432 disposable quarantine demo artifact (O-2030 s2.2 demo)\n')
    rc, out = run(['Tools/treasure_guard.py', 'quarantine',
                   'results/_r432bmc_qdemo_victim.txt', '--reason',
                   'r432 O-2030 s2.2 quarantine-mode demo (disposable artifact, 7-day observation window)'])
    mline = [l for l in out.splitlines() if l.startswith('manifest:')]
    receipt["demos"].append({"demo": "quarantine_manifest", "rc": rc,
                             "manifest": mline[0].split(':', 1)[1].strip() if mline else None})
    assert rc == 0 and mline, 'quarantine demo fail: %s' % out

    # 5) post-quarantine identity assert (s2.3 zero-loss)
    man = mline[0].split(':', 1)[1].strip()
    rc, out = run(['Tools/treasure_guard.py', 'assert', '--manifest', man])
    receipt["demos"].append({"demo": "post_assert_identity", "rc": rc,
                             "manifest": man})
    assert rc == 0, 'assert demo fail: %s' % out

    # 6) sweep-class mixed-target-set hard-reject (clean + protected mixed)
    rc, out = run(['Tools/treasure_guard.py', 'prescan',
                   'results/_r432bmc_smoke_log.txt',
                   'firm/TRIAL_LABOR_LAW.md',
                   'results/_r432bmc_s6_log.txt'])
    receipt["demos"].append({"demo": "sweep_class_mixed_hard_reject", "rc": rc,
                             "hit_path": 'firm/TRIAL_LABOR_LAW.md' in out})
    assert rc == 3 and 'firm/TRIAL_LABOR_LAW.md' in out, 'mixed-set demo fail: %s' % out

    rpath = os.path.join(REPO, 'results', '_r432bmc_treasure_weld.json')
    with open(rpath, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print('WELD DEMO PACK OK: 6/6 demos, receipt -> results/_r432bmc_treasure_weld.json')
    print('quarantine manifest:', man)
    return 0


if __name__ == '__main__':
    sys.exit(main())
