# -*- coding: utf-8 -*-
"""r437 bm-c post_review cross-machine anchor repoint (P0, bm-b MSG-20261004-0030).

Root cause: r624 CEO-order-2 archive sweep moved 1065 one-off _r* scripts to
.codely-cli/scripts-archive/ (machine-local, gitignored); r638 bm-a repointed 9
shared-criteria file_exists anchors to those local paths -- resolves on bm-a
only, file_exists:ABSENT on every other machine -> 7 permanent NO rows.

Fix: repoint the 9 checks to git_log_file(results/<original>, "*", 100) --
git history exists on ALL machines (original commits + r624 deletion commit =
preservation evidence; archive-not-delete R1 intent preserved verbatim).
Reviewer re-derive flips the 7 NO rows; ledger untouched (reviewer-append-only
law); r638 receipt gates mirrored: G1 only-9-checks-changed, G2 all anchors
resolve cross-machine, G3 idempotent second pass zero candidates.
"""
import datetime
import json
import os
import subprocess
import sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
CRIT = os.path.join(REPO, 'results', 'post_review_criteria.json')
RECEIPT = os.path.join(REPO, 'results', '_r437bmc_pr_anchor_crossmachine_fix_receipt.json')
CREATE = 0x08000000
ARCH = '.codely-cli/scripts-archive/'


def git_hist(path):
    p = subprocess.run(['git', 'log', '--oneline', '-100', '--', path],
                       capture_output=True, creationflags=CREATE, cwd=REPO,
                       text=True, encoding='utf-8', errors='replace')
    return p.returncode, (p.stdout or '').strip()


def main():
    raw = open(CRIT, 'rb').read()
    text_lf = raw.decode('utf-8').replace('\r\n', '\n')
    obj = json.loads(text_lf)

    # G0: formatting law -- re-dump must be byte-identical to source (LF face)
    redump = json.dumps(obj, ensure_ascii=False, indent=1)
    assert redump == text_lf, 'G0 FAIL: dump != source (formatting law)'

    # collect candidates
    edits = []  # (item_id, old_check, new_check, basename)
    for it in obj['items']:
        for c in it.get('checks', []):
            if c.get('kind') == 'file_exists' and c.get('args', [''])[0].startswith(ARCH):
                name = os.path.basename(c['args'][0])
                edits.append((it['id'], name))
    assert len(edits) == 9, 'expected 9 archive anchors, got %d: %r' % (len(edits), edits)
    print('candidates:', len(edits))

    # G2 pre-leg: every original results/ path must have cross-machine git history
    for rid, name in edits:
        rc, out = git_hist('results/' + name)
        assert rc == 0 and out, 'no git history for results/%s (%s)' % (name, rid)
        print('  hist ok: results/%s (%d commits, %s)' % (name, len(out.splitlines()), rid))

    # apply
    changed = []
    for it in obj['items']:
        for c in it.get('checks', []):
            if c.get('kind') == 'file_exists' and c.get('args', [''])[0].startswith(ARCH):
                name = os.path.basename(c['args'][0])
                old = json.dumps(c, ensure_ascii=False)
                c['kind'] = 'git_log_file'
                c['args'] = ['results/' + name, '*', '100']
                changed.append((it['id'], old, json.dumps(c, ensure_ascii=False)))
    assert len(changed) == 9

    # G1: reload before/after, assert exactly these 9 checks differ, no other byte drift
    after = json.dumps(obj, ensure_ascii=False, indent=1)
    open(CRIT, 'w', encoding='utf-8', newline='\r\n').write(after)
    reread = json.loads(open(CRIT, 'rb').read().decode('utf-8').replace('\r\n', '\n'))
    diffs = []
    it_after = {x['id']: x for x in reread['items']}
    it_before = {x['id']: x for x in json.loads(text_lf)['items']}
    assert set(it_after) == set(it_before)
    for k in it_before:
        cb = [json.dumps(c, ensure_ascii=False, sort_keys=True) for c in it_before[k].get('checks', [])]
        ca = [json.dumps(c, ensure_ascii=False, sort_keys=True) for c in it_after[k].get('checks', [])]
        if cb != ca:
            diffs.append((k, len(cb), len(ca)))
    assert len(diffs) == 7, 'G1 FAIL: expected 7 items touched, got %r' % diffs  # 9 checks over 7 items
    total_checks_b = sum(len(v.get('checks', [])) for v in it_before.values())
    total_checks_a = sum(len(v.get('checks', [])) for v in it_after.values())
    assert total_checks_a == total_checks_b, 'check count changed'
    assert reread['_law'] == json.loads(text_lf)['_law']
    assert reread.get('_reconciled') == json.loads(text_lf).get('_reconciled')
    print('G1 OK: 9 checks / 7 items, no other drift (total checks %d)' % total_checks_a)

    # G3: idempotent second pass = zero candidates
    reread2 = json.loads(open(CRIT, 'rb').read().decode('utf-8').replace('\r\n', '\n'))
    n2 = sum(1 for it in reread2['items'] for c in it.get('checks', [])
             if c.get('kind') == 'file_exists' and c.get('args', [''])[0].startswith(ARCH))
    assert n2 == 0, 'G3 FAIL: %d candidates remain' % n2
    print('G3 OK: idempotent second pass zero candidates')

    receipt = {
        'ts': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'round': 'r437 bm-c',
        'law': 'O-20260924-2115 re-derive-to-green (ledger untouched) + r638 repoint receipt precedent + r624 archive-not-delete R1 intent preserved via git-history form',
        'root_cause': 'r638 bm-a repointed shared criteria to machine-local .codely-cli/scripts-archive/ (gitignored) -> file_exists:ABSENT on all non-bm-a machines (bm-b MSG-20261004-0030 P0)',
        'repointed': [{'row_id': rid, 'from': 'file_exists:' + ARCH + name,
                       'to': 'git_log_file:results/' + name + ' [*,100]'}
                      for rid, name in edits],
        'n_repointed': len(edits),
        'g0_roundtrip_formatting_byte_equal': True,
        'g1_only_9_checks_changed': True,
        'g2_git_history_present_all_9': True,
        'g3_idempotent_second_pass_zero': True,
        'verdicts': 're-derived by Tools/post_review.py run in same round; ledger rows appended by reviewer only',
    }
    open(RECEIPT, 'w', encoding='utf-8', newline='\r\n').write(
        json.dumps(receipt, ensure_ascii=False, indent=1))
    print('receipt -> %s' % os.path.relpath(RECEIPT, REPO))
    print('REPOINT DONE: 9 anchors -> git_log_file cross-machine form')


if __name__ == '__main__':
    sys.exit(main())
