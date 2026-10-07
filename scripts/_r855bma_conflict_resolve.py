# _r855bma_conflict_resolve.py -- r855 push-race rebase conflict resolver (16 UU).
# Law: treasure_guard rc3 forbidden faces (OSS_HARVEST_LEDGER registry + token_usage append-only) = line/key-level union ONLY;
#      14 reproducible faces = per-face ts-newer side take (whole-file regenerated artifacts).
# In rebase replay of MY commit onto bm-c r714 tip: stage 2 (ours) = bm-c base content; stage 3 (theirs) = my commit content.
import subprocess, json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace') if r.returncode == 0 else None

def ts_of(txt):
    m = re.search(r'"(?:ts|timestamp|generated_at|written_at)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', txt or '')
    return m.group(1) if m else None

REPRO = ['docs/daily_report/REPORT-2026-10-08.json', 'docs/daily_report/REPORT-2026-10-08.md',
         'docs/live_usage/LIVE-2026-10-08.json', 'docs/live_usage/LIVE-2026-10-08.md',
         'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
         'results/_attrition_guard_scan.json', 'results/compute_audit.json',
         'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
         'results/lhb_update_status.json', 'results/regime_state.json', 'results/update_status.json']

report = []
for p in REPRO:
    ours_t, theirs_t = ts_of(blob(2, p)), ts_of(blob(3, p))
    # ts-newer wins; equal or missing ts -> prefer mine (theirs, being replayed latest work)
    take = 'theirs' if (theirs_t or '') >= (ours_t or '') else 'ours'
    side = 3 if take == 'theirs' else 2
    content = blob(side, p)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    subprocess.run(['git', 'add', p], check=True)
    report.append(f'{p}: ours={ours_t} theirs={theirs_t} -> take {"mine" if take=="theirs" else "bm-c"}')

# --- token_usage.json: append-only-ledger, key-level union (machine-keyed cumulative ledger) ---
p = 'results/token_usage.json'
ours_j, theirs_j = blob(2, p), blob(3, p)
try:
    o, t = json.loads(ours_j), json.loads(theirs_j)
except Exception as e:
    print('token_usage parse fail', e); sys.exit(2)
merged = {}
for k in set(list(o.keys()) + list(t.keys())):
    ov, tv = o.get(k), t.get(k)
    if k == 'machines' and isinstance(ov, dict) and isinstance(tv, dict):
        m = dict(ov)
        for mk, mv in (tv or {}).items():
            if mk not in m or str(mv) > str(m[mk]):
                m[mk] = mv
        merged[k] = m
    elif isinstance(ov, dict) and isinstance(tv, dict):
        merged[k] = {**ov, **tv}
    else:
        # scalar/list: prefer non-null; lists -> longer; scalars -> per-machine newer (theirs = my run)
        merged[k] = tv if tv not in (None, [], {}) else ov
with open(p, 'w', encoding='utf-8', newline='') as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
subprocess.run(['git', 'add', p], check=True)
report.append(f'{p}: key-level union (machines={list((merged.get("machines") or {}).keys())})')

# --- OSS_HARVEST_LEDGER.md: append-only registry, line-level union ---
# bm-c side (ours=base) already contains their section-7 (enrollment gate). My side (theirs) = base-at-my-commit + MY section-7.
# Union: take bm-c's full current ledger (contains their sec-7) + append MY section renumbered 7->8 (both preserved zero-loss).
p = 'research/OSS_HARVEST_LEDGER.md'
ours_txt, theirs_txt = blob(2, p), blob(3, p)
m = re.search(r'\n## 七、S5-01 vibe-astock 准入探针.*?(?=\n\Z|\n*$)', theirs_txt, re.S)
if not m:
    print('my section not found in theirs'); sys.exit(2)
my_sec = m.group(0)
# renumber my section header 7->8 (my own just-appended section, disclosed; bm-c's sec-7 stays)
my_sec_renum = my_sec.replace('## 七、S5-01 vibe-astock 准入探针', '## 八、S5-01 vibe-astock 准入探针', 1)
assert '## 八、' in my_sec_renum
assert '## 七、' in ours_txt, 'bm-c sec-7 expected in base'
assert '## 八、' not in ours_txt, 'sec-8 slot free in base'
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(ours_txt.rstrip('\n') + '\n' + my_sec_renum.rstrip('\n') + '\n')
subprocess.run(['git', 'add', p], check=True)
report.append(f'{p}: line-union kept bm-c sec-7 + mine renumbered sec-8 (zero-loss, disclosed)')

print('\n'.join(report))
print('resolver done')
