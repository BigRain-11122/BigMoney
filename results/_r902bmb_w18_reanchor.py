import json, sys, os
sys.path.insert(0, 'scripts'); sys.path.insert(0, '.')
import science_gates as sg

ART = r'results\trial_labor_w18\w18_judge_ledger_reanchor_r902.json'
RCPT = r'results\_r902bmb_w18_reanchor_receipt.json'

# idempotence guard: never double-apply
if os.path.exists(ART):
    print('ALREADY_EXISTS: re-anchor artifact present, abort (single-count law)')
    sys.exit(3)

head_before = sg.ledger_head()
assert head_before['total'] == 885789, f'unexpected head: {head_before["total"]}'

block = sg.append_ledger(
    'TRIAL_LAB_W18_JUDGE-REANCHOR-R902', 188,
    file_name=ART,
    evidence_cutoff='2026-09-22',
    note=('fork re-anchor (single-count): TRIAL_LAB_W18_JUDGE finalize (landed 2026-10-12T00:44 bm-b, PID25060 detached) '
          'consumed prev=883589 captured at judge-prep 19:11 (pre-W210); W210 landed 23:2x from same prev (883589+2200=885789) '
          '-> W18 block 883589+188=883777 is a sub-head fork invisible to ledger_head(); the 188 judge trials are counted '
          'exactly ONCE in this row and the superseded branch total 883777 must never be re-added (r807 stale-tree fork family, '
          'E34 landing-head anchor); verdicts untouched: all 188 fail was judged on skill_line 1.1481 @ n_eff 883777 < live '
          '885977-derived line = looser-side verdict, single-read r638 law, re-anchor only tightens -> zero flips'))

art = {'wave': 'TRIAL_LABOR_W18', 'stage': 'ledger-reanchor', 'reanchor_for': 'TRIAL_LAB_W18_JUDGE',
       'ts': '2026-10-12T01:5x', 'trials_ledger': block}
with open(ART, 'w', encoding='utf-8') as f:
    json.dump(art, f, ensure_ascii=False, indent=1)

head_after = sg.ledger_head()
receipt = {'ts_': '2026-10-12T01:5x+08:00', 'head_before': head_before, 'head_after': head_after, 'block': block,
            'file': ART, 'law': 'append-only additive repair; verdicts untouched (r638 single-read); zero double-count (superseded branch 883777 sub-head); zero loss (188 re-anchored); caught pre-push (r807 pre-push fork window)'}
with open(RCPT, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('HEAD_BEFORE:', head_before['total'], head_before['file'])
print('HEAD_AFTER :', head_after['total'], head_after['file'])
assert head_after['total'] == 885977 and head_after['file'].endswith('w18_judge_ledger_reanchor_r902.json')
print('RE-ANCHOR OK: 885789 + 188 = 885977')
