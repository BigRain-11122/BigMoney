"""r93 bm-c: dedicated verify for stale push-refuge branches machine/bm-c-r72 & r84 (r90-deferred).

Question: does each branch tip contain PERSISTENT work product absent from origin/main?
Rolling-ledger faces (autofill_state/token_usage/compute_audit/x2_watch/update_status/state-*/heartbeat)
are superseded by design (take-new / union / tick-rolled-forward) -> excluded from the
absorption test; only their PRESENCE on main's tip lineage is asserted, not byte-parity.
"""
import subprocess, sys, json

def git(*args):
    r = subprocess.run(['git', *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        raise RuntimeError('git %s -> %s' % (args, r.stderr.strip()))
    return r.stdout

ROLLING_MARKERS = (
    'results/autofill_state.json', 'results/token_usage.json', 'results/compute_audit.json',
    'results/x2_watch_log.jsonl', 'results/update_status.json', 'results/dashboard_status',
    'state-', 'fleet/machines/', 'results/watermark', 'results/_runnable', 'results/regime_state.json',
    'results/strategy_scorecard.json', 'results/scorecard_v1.json', 'results/daily_scorecard.json',
    'results/science_audit.json', 'results/prospect_paper/_summary', 'results/prospect_promotion/_summary',
    'results/paper_export/', 'results/paper/', 'results/t35_', 'results/lhb_update_status',
    'results/heat_update_status', 'results/futures_update_status', 'results/repo_update_status',
    'results/sina_mf_update_status', 'results/options_update_status', 'results/fundamental_',
    'results/autofill', 'docs/daily_report/', 'results/market_clock/', 'results/briefings/',
    'results/self_review/', 'results/rev_osc_live/', 'results/aggr_paper/', 'results/grid_paper/',
    'results/alloc_paper/', 'logs/iteration-loop/round_reports', 'HQ-FEEDBACK.md',
)

BRANCHES = {
    'r72': ('origin/machine/bm-c-r72', '1bbe7dff6990d71210b52d3e986d2238d5062b64'),
    'r84': ('origin/machine/bm-c-r84', 'ef92ff788fff8c8749fe9154dbf967eae8b5bcd3'),
}

def classify(path):
    return 'rolling' if any(m in path for m in ROLLING_MARKERS) else 'persistent'

report = {}
for name, (branch, base) in BRANCHES.items():
    changed = [p for p in git('diff', '--name-only', base, branch).splitlines() if p.strip()]
    pers, roll, missing_substance = [], [], []
    for p in changed:
        (pers if classify(p) == 'persistent' else roll).append(p)
    for p in pers:
        # substance test: does the branch's version content appear within main's current version?
        b = subprocess.run(['git', 'show', branch + ':' + p], capture_output=True)
        m = subprocess.run(['git', 'show', 'origin/main:' + p], capture_output=True)
        if m.returncode != 0:
            # file missing on main entirely -> unique artifact, must inspect
            missing_substance.append((p, 'MISSING_ON_MAIN', len(b.stdout)))
            continue
        btxt, mtxt = b.stdout.decode('utf-8', 'replace'), m.stdout.decode('utf-8', 'replace')
        if btxt == mtxt:
            continue  # byte-identical -> absorbed trivially
        # line-level: branch lines present verbatim in main?
        blines = [l for l in btxt.splitlines() if l.strip()]
        absent = [l for l in blines if l not in mtxt]
        if absent:
            missing_substance.append((p, 'LINES_ABSENT', len(absent)))
    report[name] = {
        'branch': branch, 'merge_base': base, 'files_changed': len(changed),
        'persistent': pers, 'rolling_n': len(roll),
        'absorption_issues': missing_substance,
    }

print(json.dumps(report, ensure_ascii=False, indent=1))
