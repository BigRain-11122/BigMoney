"""r284 bm-b: WM verdict + compute_audit flag readout for round report."""
import json, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# watermark.jsonl last line (local gitignored)
p = os.path.join(ROOT, 'results', 'watermark.jsonl')
last = open(p, encoding='utf-8-sig').read().strip().splitlines()[-1]
w = json.loads(last)
print('WM keys:', {k: w.get(k) for k in ('verdict', 'cpu_total_pct', 'py_cpu_pct', 'py_procs', 'local_batch_running', 'work_cands')})
print('WM verdict:', w.get('verdict'))
print('WM note:', str(w.get('note', ''))[:300])

# compute_audit latest flags
ca = os.path.join(ROOT, 'results', 'compute_audit.json')
d = json.load(open(ca, encoding='utf-8-sig'))
hist = d.get('history', [])
latest = hist[-1] if hist else d
flags = {k: latest.get(k) for k in ('blind_run', 'wasted_run', 'over_limit', 'zombie', 'gpu_overreach') if k in latest}
print('compute_audit flags:', flags or 'check keys:', list(latest.keys())[:20])
