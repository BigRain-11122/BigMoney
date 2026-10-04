import subprocess, json

def gv(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None

head = 'e1dd04ac62fa3f7f2a3e70b2be36ba4504cbe0aa'
mine = 'fb4f59899bdd6731d4275ab7e224b11407e52229'

# compute_audit: history rows + machines key
for rev, tag in [(head, 'ORIGIN'), (mine, 'MINE')]:
    j = json.loads(gv(rev, 'results/compute_audit.json'))
    h = j.get('history', [])
    print(tag, 'compute_audit top keys:', list(j), '| history rows:', len(h))
    if h:
        print('   last row:', json.dumps(h[-1], ensure_ascii=False)[:200])
    m = j.get('machines')
    if m is not None:
        print('   machines:', json.dumps(m, ensure_ascii=False)[:300])
    lat = j.get('latest')
    if lat:
        print('   latest ts:', lat.get('ts') if isinstance(lat, dict) else str(lat)[:80])

# token_usage: machines entries
for rev, tag in [(head, 'ORIGIN'), (mine, 'MINE')]:
    j = json.loads(gv(rev, 'results/token_usage.json'))
    m = j.get('machines', {})
    print(tag, 'token_usage generated:', j.get('generated'), '| machines keys:', list(m) if isinstance(m, dict) else type(m).__name__)
    if isinstance(m, dict):
        for k, v in m.items():
            print('   ', k, json.dumps(v, ensure_ascii=False)[:150])

# update_status: updated/now
for rev, tag in [(head, 'ORIGIN'), (mine, 'MINE')]:
    j = json.loads(gv(rev, 'results/update_status.json'))
    print(tag, 'update_status updated:', j.get('updated'), '| now:', j.get('now'), '| data_cutoff:', j.get('data_cutoff'), '| total_new_rows:', j.get('total_new_rows'))

# fundamental gates equality (minus ts)
for rev, tag in [(head, 'ORIGIN'), (mine, 'MINE')]:
    j = json.loads(gv(rev, 'results/fundamental_b_layer_filter.json'))
    print(tag, 'b_layer updated:', j.get('updated'), '| gates:', json.dumps(j.get('gates'), ensure_ascii=False)[:120])

# regime updated
for rev, tag in [(head, 'ORIGIN'), (mine, 'MINE')]:
    j = json.loads(gv(rev, 'results/regime_state.json'))
    print(tag, 'regime updated:', j.get('updated'), '| state:', j.get('state'))

# REPORT generated_at
for rev, tag in [(head, 'ORIGIN'), (mine, 'MINE')]:
    j = json.loads(gv(rev, 'docs/daily_report/REPORT-2026-10-04.json'))
    print(tag, 'REPORT generated_at:', j.get('generated_at'))

# futures claim
for rev, tag in [(head, 'ORIGIN'), (mine, 'MINE')]:
    j = json.loads(gv(rev, 'results/futures_update_status.json'))
    print(tag, 'futures ts:', j.get('ts'), '| mode:', j.get('mode'), '| no_op_reason:', j.get('no_op_reason'))

# attrition rc
for rev, tag in [(head, 'ORIGIN'), (mine, 'MINE')]:
    j = json.loads(gv(rev, 'results/_attrition_guard_scan.json'))
    print(tag, 'attrition ts:', j.get('ts'), '| active_loss:', j.get('active_loss'), '| rc:', j.get('rc'), '| files:', len(j.get('files', [])))
