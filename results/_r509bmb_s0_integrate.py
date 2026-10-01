# r509 bm-b S0 integration: adopt r508 crashed-session residue onto origin/main
# Route: r314 CAS cherry-pick family -> single carry commit (duplicate-content
# dual lineage made per-commit picks pointless; rides are superseded telemetry).
# Gates: parse-verify every touched JSON; surgical diff --stat assertions;
# ledger_head sanity (382,239 must survive; 380,320 phantom must NOT appear).
import subprocess, json, sys, os

def run(cmd, check=True, inp=None):
    r = subprocess.run(cmd, capture_output=True)
    if check and r.returncode != 0:
        print("FAIL CMD:", cmd, "\nSTDOUT:", r.stdout.decode('utf-8', 'replace')[-2000:],
              "\nSTDERR:", r.stderr.decode('utf-8', 'replace')[-2000:])
        sys.exit(1)
    return r

def gb(ref, path):
    return run(['git', 'show', f'{ref}:{path}']).stdout

CARRY = 'ccdd13e87'
BASE  = 'origin/main'

print("== gate 0: worktree clean ==")
st = run(['git', 'status', '--porcelain']).stdout.decode().strip()
if st:
    print("dirty tree, lines:", len(st.splitlines())); print(st[:500]); sys.exit(2)

print("== step 1: detach onto origin/main ==")
run(['git', 'checkout', '--detach', BASE])

print("== step 2: restore carry set (bm-b-owned + origin-untouched-since-fork) ==")
RESTORE = [
    # engine instance + wiring (origin untouched these since fork 5e8312feca)
    'scripts/saturation_engine.py', 'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py', 'monitor/build_status.py',
    'research/PERPETUAL_FACES.md', 'research/PERPETUAL_N1_W10_PREREG.md',
    'Tools/register_satengine_task.ps1', 'Tools/iteration_prompt.txt',
    'dashboard.html',
    # products: W10 wave + claims + engine telemetry + r508 receipts
    'results/p2cal_ext/n1_w10', 'results/pool_claims',
    'results/saturation_engine',
    'results/_r508bmb_s6_log.txt', 'results/_r508bmb_s6_runner.ps1',
    'results/_r508bmb_s6_runner2.ps1', 'results/_r508bmb_w10_band_gate.py',
    # bm-b single-writer lane/state (local freshest; origin untouched since fork)
    'state.json', 'fleet/machines/bm-b.json',
    'logs/iteration-loop/round_reports.md',
    'results/autofill_state.bm-b.json', 'results/crash_fuse.bm-b.json',
    'results/compute_audit.bm-b.json', 'results/token_usage.bm-b.json',
    'results/futures_update_status.bm-b.json', 'results/lhb_update_status.bm-b.json',
    'results/minute_feed_status.bm-b.json', 'results/minute_feed_status.json',
    'results/regime_state.bm-b.json', 'results/update_status.bm-b.json',
    'results/etf_daily_pull_status.json', 'results/astock_daily_update_status.json',
    'results/pool_dualrun.bm-b.jsonl', 'results/runnable_pool.bm-b.json',
    'results/t35_open_fill_verify.json', 'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json', 'results/daily_scorecard.json',
    'results/p1d_gates.json', 'results/x2_watch_log.jsonl',
    'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-30.json', 'results/paper_export/latest.json',
]
run(['git', 'checkout', CARRY, '--'] + RESTORE)
print("   restored", len(RESTORE), "paths")

print("== step 3: CODELY.md memory-union (origin base + r508 bm-b entry) ==")
ob = gb(BASE, 'CODELY.md'); lb = gb(CARRY, 'CODELY.md')
o_lines = ob.decode('utf-8').splitlines()
l_lines = lb.decode('utf-8').splitlines()
o_set = {x.strip() for x in o_lines}
local_only = [x for x in l_lines if x.strip().startswith(('- [', '- 冷层指针')) and x.strip() not in o_set]
print("   local-only entries:", len(local_only))
assert len(local_only) == 1, "expected exactly 1 local-only CODELY entry"
# insert at end of Project section = immediately before '### Reference'
idx = next(i for i, x in enumerate(o_lines) if x.strip() == '### Reference')
merged = o_lines[:idx] + [local_only[0]] + o_lines[idx:]
data = '\n'.join(merged) + ('\n' if ob.endswith(b'\n') else '')
open('CODELY.md', 'wb').write(data.encode('utf-8'))

print("== step 4: T-141 ticket union (origin face + bm-b r508 faces) ==")
tick = 'fleet/tasks/T-2026-10-01-141-P1.json'
od = json.loads(gb(BASE, tick).decode('utf-8-sig'))
ld = json.loads(gb(CARRY, tick).decode('utf-8-sig'))
# keep origin claims; add bm-b slice claims reflecting the BUILT state
od['claims']['s1-engine-core-bm-b'] = {
    "claimed_by": "bm-b", "claimed_at": "2026-10-01 14:26", "status": "done",
    "result_ref": ("scripts/saturation_engine.py v0.1 resident (schtasks Bigmoney-SatEngine-bm-b "
                   "S4U 60s cadence via Tools/register_satengine_task.ps1, selftest 7/7); W10 first "
                   "engine wave 12/12 engine-burned on bm-b (results/p2cal_ext/n1_w10/shard-0..11, "
                   "finalize pending next round); band gate ADMIT receipt results/_r508bmb_w10_band_gate.py; "
                   "engine telemetry results/saturation_engine/*_bm-b.json; acceptance face per law sec.6 "
                   "in flight (3-workday py>=70% measurement)"),
    "scope": ("bm-b engine core instance per law v1.0 (local perpetual queue N1 via perpetual_faces "
              "machinery, PreIgnitionChecks r316, full-core profile, same-tick self-derived completion, "
              "self-restart, state self-derived, zero pool claims)")}
od['claims']['s3-ceo-face-round-zero-bm-b'] = {
    "claimed_by": "bm-b", "claimed_at": "2026-10-01 14:26", "status": "done",
    "result_ref": ("face_bm-b.json live py% standing row + monitor/build_status.py _engine_face_state "
                   "three-machine aggregation reader + dashboard.html chain row + round-zero engine "
                   "item wired into Tools/iteration_prompt.txt (status exit 1 = P0 same-round repair)")}
lp = ld.get('progress', '')
marker = ' || r508 bm-b: '
assert marker in lp, "local progress r508 segment missing"
r508_part = lp.split(marker, 1)[1]
od['progress'] = od.get('progress', '') + ' || r508 bm-b: ' + r508_part
od['claimed_by'] = ld.get('claimed_by'); od['claimed_at'] = ld.get('claimed_at')
od['claim_merge_note'] = ("r509 bm-b carry-merge (r314 CAS route): origin face (bm-a s1 claim + bm-c "
                          "s1 done + s2 in_progress) + bm-b r508 built report + bm-b slice claims unioned")
new = json.dumps(od, ensure_ascii=False, indent=1)
open(tick, 'wb').write(new.encode('utf-8'))

print("== step 5: pool_core_samples.jsonl line-union ==")
pcs = 'results/pool_core_samples.jsonl'
o_lines = [x for x in gb(BASE, pcs).decode('utf-8-sig').splitlines() if x.strip()]
l_lines2 = [x for x in gb(CARRY, pcs).decode('utf-8-sig').splitlines() if x.strip()]
o_set2 = {x.strip() for x in o_lines}
extra = [x for x in l_lines2 if x.strip() not in o_set2]
union = o_lines + extra
for ln in union: json.loads(ln)
open(pcs, 'wb').write(('\n'.join(union) + '\n').encode('utf-8'))
print("   union lines:", len(o_lines), "+", len(extra), "=", len(union))

print("== gate 6: parse-verify every touched JSON ==")
for p in RESTORE:
    if p.endswith('.json') and os.path.isfile(p):
        json.load(open(p, encoding='utf-8-sig'))
json.load(open('CODELY.md'.replace('CODELY.md', tick), encoding='utf-8-sig'))
json.load(open('fleet/machines/bm-b.json', encoding='utf-8-sig'))
json.load(open('state.json', encoding='utf-8-sig'))
print("   all touched JSON parse OK")

print("== gate 7: surgical diff assertions ==")
def dstat(path):
    r = run(['git', 'diff', '--stat', BASE, '--', path]).stdout.decode()
    return r.strip().splitlines()[-1] if r.strip() else "0 files"
for p, maxch in [('CODELY.md', 5), (tick, 60), ('results/pool_core_samples.jsonl', 25)]:
    line = dstat(p)
    print("   ", line)
    import re as _re
    m = _re.search(r'(\d+) insertion', line) or _re.search(r'(\d+) change', line)
    if m:
        assert int(m.group(1)) <= maxch, f"surgical assertion FAILED for {p}: {line}"
# ledger sanity
sys.path.insert(0, 'scripts')
import science_gates as sg
head = sg.ledger_head()
print("   ledger_head after merge:", head.get('total'), head.get('file'))
assert int(head['total']) == 382239, "ledger head must remain 382,239 (W9) pre-furnace-append"
n_w10 = run(['git', 'ls-files', 'results/p2cal_ext/n1_w10']).stdout.decode().strip().splitlines()
n_cl = run(['git', 'ls-files', 'results/pool_claims']).stdout.decode().strip().splitlines()
w10_cl = [x for x in n_cl if 'PERPETUAL-N1-W10' in x]
print("   W10 products tracked:", len(n_w10), "W10 claims tracked:", len(w10_cl))
assert len(n_w10) == 12 and len(w10_cl) == 12

print("== step 8: commit integration ==")
run(['git', 'add', '-A', '--'] + RESTORE + ['CODELY.md', tick, pcs])
r = run(['git', 'commit', '-m',
         "round 509 S0 integration: adopt r508 crashed-session residue onto origin/main "
         "(r314 CAS route, single carry commit) -- bm-b saturation engine instance "
         "(scripts/saturation_engine.py + s3 face wiring) + W10 first engine wave 12/12 "
         "products + pool claims provenance + engine telemetry + bm-b lane faces + "
         "CODELY/ticket/pool-samples union; shared derive faces take origin side "
         "[via bm-b]"], check=False)
if r.returncode != 0:
    print(r.stdout.decode()[-800:], r.stderr.decode()[-800:]); sys.exit(3)
new_sha = run(['git', 'rev-parse', 'HEAD']).stdout.decode().strip()
print("   integration commit:", new_sha)

print("== step 9: CAS move main ref + checkout + verify ==")
cas = run(['git', 'update-ref', 'refs/heads/main', new_sha, '5b8d72c45'], check=False)
if cas.returncode != 0:
    print("CAS FAILED (daemon raced?):", cas.stderr.decode()[-400:]); sys.exit(4)
run(['git', 'checkout', 'main'])
run(['git', 'branch', '-D', 'main-backup-r509'], check=False)
print("   main now at:", run(['git', 'rev-parse', 'main']).stdout.decode().strip())
print("INTEGRATION BUILD OK -> push next (S7/sooner per protocol)")
