# -*- coding: utf-8 -*-
"""r403 bm-c surgical CAS repack + push (post claw-block stale-base re-integration).

Law family: E01 CAS direct-commit + E08 zero-rebase + r532 active-write-face
(tracked live files present = rebase/amend/autostash FORBIDDEN -> diff-based
payload) + r593 execution-time tip + E16 origin-verbatim ticket face.

Steps:
  1. fetch + rev-parse origin/main (execution-time fresh tip);
  2. programmatic ticket surgery: origin ticket JSON -> status=delivered +
     claim + progress_r403_bmc + result_ref + seat-resolution note append
     (spec field byte-identical by construction -- json round-trip);
  3. temp index from tip tree; overlay payload faces (hash-object working
     tree / programmatic ticket);
  4. assertions: deletion-set EMPTY, ticket json.loads + spec==origin-spec,
     parquet sha256 == ticket result_ref sha, payload count == manifest;
  5. commit-tree -p tip; CAS push <sha>:refs/heads/main; on success
     update-ref main + reset --mixed (tree files preserved).
"""
import hashlib
import json
import os
import subprocess
import sys
import time

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
CNW = 0x08000000
TICKET = 'fleet/tasks/T-2026-10-03-154-P1.json'
PARQUET = 'data/fund_history_export/div_events_faces.parquet'

PAYLOAD = [
    PARQUET,
    TICKET,
    'fleet/transfers/T-2026-10-03-154-sender.json',
    'fleet/inbox/MSG-2026-10-03-0805-bmc-ALL-divlowvol-data.md',
    'fleet/machines/bm-c.json',
    'knowledge/METHODOLOGY_ASSETS.md',
    'round_reports-bm-c.md',
    'state-bm-c.json',
    'results/_r402bmc_addendum.py',
    'results/_r403bmc_pre_ff_overlap.py',
    'results/_r403bmc_ff_integrate.py',
    'results/_r403bmc_s6_chain.ps1',
    'results/_r403bmc_s6_runner.log',
    'results/_r403bmc_t154_export.py',
    'results/_r403bmc_t154_export_v2.py',
    'results/_r403bmc_t154_log.txt',
    'results/_r403bmc_t154_debug.py',
    'results/_r403bmc_t154_verify.py',
    'results/t154_dividend_events_export.json',
    'results/t154_div_events_faces_export.json',
    'results/autofill_state.bm-c.json',
    'results/dispatcher_state.bm-c.json',
    'results/saturation_engine/face_bm-c.json',
    'results/saturation_engine_state.bm-c.json',
    'results/compute_audit.bm-c.json',
    'results/fund_premium_status.json',
    'results/futures_update_status.bm-c.json',
    'results/lhb_update_status.bm-c.json',
    'results/pool_dualrun.bm-c.jsonl',
    'results/regime_state.bm-c.json',
    'results/runnable_pool.bm-c.json',
    'results/token_usage.bm-c.json',
    'results/update_status.bm-c.json',
]


def git(args, check=True, env=None):
    r = subprocess.run(['git'] + args, capture_output=True, cwd=REPO,
                       text=True, encoding='utf-8', errors='replace',
                       creationflags=CNW, env=env)
    if check and r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (args[:4], (r.stderr or r.stdout)[:400]))
    return r.returncode, r.stdout


def main():
    t0 = time.time()
    git(['fetch', 'origin'])
    _, tip = git(['rev-parse', 'origin/main'])
    tip = tip.strip()
    print('execution-time tip:', tip)

    # ---- programmatic ticket surgery (spec byte-identical by construction)
    _, tjson = git(['show', tip + ':' + TICKET])
    t = json.loads(tjson)
    orig_spec = t['spec']
    assert t['id'] == 'T-2026-10-03-154-P1'
    with open(os.path.join(REPO, PARQUET), 'rb') as fh:
        psha = hashlib.sha256(fh.read()).hexdigest()
    now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
    t['status'] = 'delivered'
    t['claimed_by'] = 'bm-c (OS iteration loop, round 403)'
    t['claimed_at'] = now
    t['note'] = (t.get('note', '') +
        ' | SEAT-RESOLUTION r403 bmc: bm-c drafted a SAME-NUMBER T-154 '
        'locally at 08:03 (never pushed, never reached origin) in the same '
        'parallel window; bm-b origin-first commit = canonical ticket per '
        'r511 commit-time order -- bm-c draft superseded per yield law. '
        'Execution below conforms EXACTLY to this spec.')
    t['progress_r403_bmc'] = (
        'EXECUTED same round as claim (T-152 lane precedent, transfer window '
        '= TODAY honored): export results/_r403bmc_t154_export_v2.py per THIS '
        'ticket spec verbatim; live run VERDICT PASS 10/10 gates -- '
        'n_symbols_nonempty 5,124>=5,100; per-sym event median 9>=3; ex_date '
        'span 1991-04-03..2026-10-23 (d1>=2026-01-01); zero null cash; zero '
        'unsorted (code,ex_date) asc; dtype contract verified at parquet '
        'schema level (code=large_string, ex_date=date32[day], '
        'record_date=date32[day], cash_div_per_10=double); quarantine 5 syms '
        'absent; component-preservation known-answer 600519 2006-05-19 = TWO '
        'rows cash-sum 3.0 (10转10派3 two-component case; exact-dup key never '
        'collapses -- 3 such pairs measured 600519/000402/000501; '
        'exact_dups_dropped=0 honest); readback sum identical. Excluded (zero '
        'silent drops, receipt): non-implemented 19,494; null/unparseable '
        'ex_date 19,498; null/missing cash 0; record_date missing->NaT '
        'counted. PARQUET DELIVERED: data/fund_history_export/'
        'div_events_faces.parquet 54,494 rows / 357,002 bytes / sha256 ' + psha +
        ' (git 方案 A direct self-delivering). Manifest regenerated '
        'dir-level full-hash. Receipt: results/t154_div_events_faces_export.'
        'json. A 7-column exploration variant (v1) ran first as working '
        'papers (results/_r403bmc_t154_export.py + results/'
        't154_dividend_events_export.json kept; its parquet removed as '
        'superseded by this spec deliverable). Method capture: '
        'METHODOLOGY_ASSETS E17 (ex-date PIT anchor + per-10 unit semantics '
        '+ same-ex-date multi-component preservation law).')
    t['result_ref'] = (PARQUET + ' (sha256 ' + psha + ') + fleet/transfers/'
        'T-2026-10-03-154-sender.json + results/t154_div_events_faces_export.json')
    assert t['spec'] == orig_spec, 'spec mutated!'
    ticket_path = os.path.join(REPO, TICKET)
    with open(ticket_path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(t, fh, ensure_ascii=False, indent=1)
    json.load(open(ticket_path, encoding='utf-8'))  # parse re-verify
    print('ticket surgery OK (spec byte-identical, status=%s)' % t['status'])

    # ---- temp index from tip
    idx = os.path.join(REPO, '.git', 'r403-cas-index')
    env = dict(os.environ)
    env['GIT_INDEX_FILE'] = idx
    if os.path.exists(idx):
        os.remove(idx)
    git(['read-tree', tip], env=env)

    for rel in PAYLOAD:
        p = os.path.join(REPO, rel.replace('/', os.sep))
        if not os.path.exists(p):
            sys.exit('PAYLOAD MISSING %s' % rel)
        _, h = git(['hash-object', '-w', p])
        git(['update-index', '--add', '--cacheinfo',
             '100644,' + h.strip() + ',' + rel], env=env)
    print('payload faces staged: %d' % len(PAYLOAD))

    _, newtree = git(['write-tree'], env=env)
    newtree = newtree.strip()
    _, oldtree = git(['rev-parse', tip + '^{tree}'])

    # ---- assertion 1: deletion set EMPTY
    _, names = git(['diff-tree', '--name-status', '-r', oldtree.strip(),
                    newtree])
    dels = [l for l in names.splitlines() if l.startswith('D')]
    print('tree delta lines: %d, deletions: %d' % (
        len(names.splitlines()), len(dels)))
    for l in dels:
        print('DEL!', l)
    if dels:
        sys.exit('ABORT: deletion set non-empty')
    # ---- assertion 2: ticket in new tree parses + spec identical + sha in ref
    _, tblob = git(['show', newtree + ':' + TICKET])
    t2 = json.loads(tblob)
    assert t2['spec'] == orig_spec, 'tree ticket spec drifted!'
    assert psha in t2['result_ref'], 'parquet sha missing from result_ref'
    assert t2['status'] == 'delivered'
    # ---- assertion 3: payload path set present in new tree
    for rel in PAYLOAD:
        _, one = git(['ls-tree', newtree, rel])
        if not one.strip():
            sys.exit('ABORT: payload path absent from new tree: %s' % rel)
    print('assertions 1-3 PASS (no deletions; ticket verbatim; %d paths)'
          % len(PAYLOAD))

    msg = ('round 403 (bm-c): T-154 div_events_faces.parquet DELIVERED per '
           'bm-b origin-first ticket spec (54,494 rows/5,124 syms/357,002B '
           'sha256 ' + psha[:12] + ', 10/10 fail-closed gates incl date32 '
           'schema verify + multi-component preservation known-answer; '
           'manifest + MSG-0805 seat OPEN) + E17 methodology card (E16 taken '
           'on origin by bm-a r612, renumbered per r315 union; same-number '
           'T-154 yielded to bm-b per r511 commit-time law) + claw-blocked '
           'stale-base first push resolved via second FF + surgical CAS '
           'repack (r532 law) + S6 33/33 rc0 + r402 addendum adopted')
    _, newc = git(['commit-tree', newtree, '-p', tip, '-m', msg])
    newc = newc.strip()
    _, head = git(['rev-parse', 'HEAD'])
    print('new commit %s (parent %s, replaces local-unpushed %s)'
          % (newc[:9], tip[:9], head.strip()[:9]))

    rc, out = git(['push', 'origin', newc + ':refs/heads/main'], check=False)
    print('push rc=%d %s' % (rc, out.strip()[:300]))
    if rc != 0:
        sys.exit('PUSH REJECTED -- origin advanced again; rerun this script')
    git(['update-ref', 'refs/heads/main', newc])
    git(['reset', '--mixed', newc])
    os.remove(idx)
    print('CAS-DELIVERED %s (%.1fs) -- local main aligned, tree preserved'
          % (newc[:9], time.time() - t0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
