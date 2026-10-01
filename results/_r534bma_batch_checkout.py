"""r534: batch checkout origin-owned faces after reset --mixed (r512/r524 law), keeping bm-a live files."""
import subprocess

KEEP = {
    'results/autofill_state.bm-a.json',
    'results/saturation_engine/face_bm-a.json',
    'results/saturation_engine/history_bm-a.jsonl',
    'results/saturation_engine/ledger_bm-a.jsonl',
    'results/saturation_engine/state_bm-a.json',
    'results/pool_core_samples.jsonl',
    'results/x2_watch_log.jsonl',
}

st = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
paths = []
for line in st.splitlines():
    if len(line) < 4:
        continue
    tag, p = line[:2], line[3:].strip()
    if tag.strip() not in ('M', 'D'):
        continue
    if p in KEEP or p.startswith('"'):
        continue
    paths.append(p)

print(f'{len(paths)} paths to checkout')
# restore D files (checkout), and refresh M files to HEAD
r = subprocess.run(['git', 'checkout', '--'] + paths, capture_output=True, text=True, encoding='utf-8', errors='replace')
print('rc:', r.returncode, r.stderr[:500] if r.stderr else 'ok')

st2 = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
print('--- remaining diff:')
print(st2)
