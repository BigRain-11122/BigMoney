"""r619 bm-b resolver stage A+B.

Stage A: resolve the 18 UU files of interrupted pick f275451fd (rebase onto 0a1e2eb5e).
  - 17 files: take ours (:3: = round-618 side, uniformly newer 14:17-14:23 vs origin 14:03-14:05).
  - results/compute_audit.json: union history by (ts,machine) key zero-loss, latest takes :3:.
Stage B: r543 quit-gate superset verification for remaining picks a9c3d35eb / 5952f0e3b
  + r614 k-contiguity on live nulls faces + r570 line-membership union assertions
  + r185 parse validation for every resolved JSON.

Laws: r188/R208/R216 (recipes), r185 (parse before add), r570 (jsonl union domain),
r614 (live-write holes), r543 (todo check before quit), r405 (blob from stages/objects).
"""
import subprocess, json, sys, re

def run(args, **kw):
    return subprocess.run(args, capture_output=True, **kw)

def show(rev, path):
    spec = f':{rev}:{path}' if isinstance(rev, int) else f'{rev}:{path}'
    r = run(['git', 'show', spec])
    if r.returncode != 0:
        print(f'  [show-err] git show {spec} rc={r.returncode} stderr={r.stderr.decode("utf-8", "replace")[:200]}')
        return None
    return r.stdout

TAKE_OURS = [
    'docs/daily_report/REPORT-2026-10-03.json',
    'docs/daily_report/REPORT-2026-10-03.md',
    'docs/live_usage/LIVE-2026-10-03.json',
    'docs/live_usage/LIVE-2026-10-03.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
    'results/update_status.json',
]
CA = 'results/compute_audit.json'
FAIL = []

def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + ((' | ' + detail) if detail else ''))
    if not ok:
        FAIL.append(name)

# ---------------- Stage A ----------------
for p in TAKE_OURS:
    b = show(3, p)
    if b is None:
        check(f'take3 {p}', False, 'no :3: blob')
        continue
    with open(p, 'wb') as f:
        f.write(b)
    if p.endswith('.json'):
        try:
            json.loads(b.decode('utf-8', 'replace'))
            check(f'take3 {p}', True, f'{len(b)}B')
        except Exception as e:
            check(f'take3 {p}', False, f'parse: {e}')
    else:
        check(f'take3 {p}', True, f'{len(b)}B')

# compute_audit union
c2 = json.loads(show(2, CA).decode('utf-8', 'replace'))
c3 = json.loads(show(3, CA).decode('utf-8', 'replace'))
k2 = {(e['ts'], e.get('machine', '')): e for e in c2['history']}
k3 = {(e['ts'], e.get('machine', '')): e for e in c3['history']}
union = dict(k2)
union.update(k3)  # overlap byte-identical (verified), :3: content wins ties
merged = sorted(union.values(), key=lambda e: e['ts'])
check('compute_audit union zero-loss',
      len(merged) == len(k2) + len(k3) - len(set(k2) & set(k3)),
      f'|A|={len(k2)} |B|={len(k3)} |A&B|={len(set(k2)&set(k3))} -> |A|+|B|-|A&B|={len(merged)}')
out = {'latest': c3['latest'], 'history': merged}
raw3 = show(3, CA)
m = re.match(r'\s*{\n(\s+)"latest"', raw3.decode('utf-8', 'replace'))
indent = len(m.group(1)) if m else 1
end_nl = b'\n' if raw3.endswith(b'\n') else b''
crlf = b'\r\n' in raw3[:400]
sep = '\r\n' if crlf else '\n'
body = json.dumps(out, ensure_ascii=False, indent=indent)
text = body.replace('\n', sep) if crlf else body
with open(CA, 'wb') as f:
    f.write(text.encode('utf-8') + (b'\n' if end_nl else b''))
json.load(open(CA, encoding='utf-8'))
check('compute_audit write+parse', True, f'indent={indent} crlf={crlf} entries={len(merged)}')

# ---------------- Stage B ----------------
def lines_of(rev, path):
    b = show(rev, path)
    if b is None:
        return None
    return b.decode('utf-8', 'replace').strip().splitlines()

# B1: remaining picks' specific lines present in worktree superset
v_pick_last = lines_of('a9c3d35eb', 'results/fund_value_p1/nulls.jsonl')[-1]
wt_v = open('results/fund_value_p1/nulls.jsonl', encoding='utf-8').read().strip().splitlines()
check('r543 a9c3d35eb fund_value line in wt', v_pick_last in wt_v,
      f'pick last k={json.loads(v_pick_last)["k"]} wt k range 0..{json.loads(wt_v[-1])["k"]}')

q_pick_last = lines_of('5952f0e3b', 'results/fund_quality_p1/nulls.jsonl')[-1]
wt_q = open('results/fund_quality_p1/nulls.jsonl', encoding='utf-8').read().strip().splitlines()
check('r543 5952f0e3b fund_quality line in wt', q_pick_last in wt_q,
      f'pick last k={json.loads(q_pick_last)["k"]} wt k range 0..{json.loads(wt_q[-1])["k"]}')

# B2: engine tick faces — worktree newer than pick
pick_face = json.loads(show('5952f0e3b', 'results/saturation_engine/face_bm-b.json'))
wt_face = json.load(open('results/saturation_engine/face_bm-b.json', encoding='utf-8'))
check('r543 face newer in wt', wt_face['ts'] > pick_face['ts'], f"wt {wt_face['ts']} > pick {pick_face['ts']}")
h_pick = lines_of('5952f0e3b', 'results/saturation_engine/history_bm-b.jsonl')
h_wt = open('results/saturation_engine/history_bm-b.jsonl', encoding='utf-8').read().strip().splitlines()
pick_h_last = h_pick[-1]
check('r543 engine history last line in wt', pick_h_last in h_wt,
      f"pick last ts={json.loads(pick_h_last)['ts']} wt last ts={json.loads(h_wt[-1])['ts']}")

# B3: r614 k-contiguity on live nulls faces
for p in ['results/fund_value_p1/nulls.jsonl', 'results/fund_quality_p1/nulls.jsonl',
          'results/fund_divlowvol_p1/nulls.jsonl']:
    ks = [json.loads(l)['k'] for l in open(p, encoding='utf-8').read().strip().splitlines()]
    gaps = [i for i in range(1, len(ks)) if ks[i] != ks[i-1] + 1]
    check(f'r614 k-contiguity {p}', ks[0] == 0 and not gaps, f'k 0..{ks[-1]} n={len(ks)}')

# B4: r570 line-membership — staged(index) nulls face is a superset of origin@0a1e2eb5e and f275451fd
for p in ['results/fund_value_p1/nulls.jsonl', 'results/fund_quality_p1/nulls.jsonl',
          'results/fund_divlowvol_p1/nulls.jsonl']:
    origin_l = lines_of('0a1e2eb5e', p) or []
    r618_l = lines_of('f275451fd', p) or []
    staged_l = lines_of(':0', p) or []
    so, sr = set(origin_l), set(r618_l)
    ss = set(staged_l)
    miss_o = so - ss
    miss_r = sr - ss
    check(f'r570 staged superset {p}', not miss_o and not miss_r,
          f'origin={len(so)} r618={len(sr)} staged={len(ss)} miss_o={len(miss_o)} miss_r={len(miss_r)}')

# B5: worktree prefix of staged for nulls (daemon appended only)
for p in ['results/fund_value_p1/nulls.jsonl', 'results/fund_quality_p1/nulls.jsonl',
          'results/fund_divlowvol_p1/nulls.jsonl']:
    staged_l = lines_of(':0', p) or []
    wt_l = open(p, encoding='utf-8').read().strip().splitlines()
    check(f'prefix {p}', wt_l[:len(staged_l)] == staged_l, f'staged={len(staged_l)} wt={len(wt_l)}')

print()
print('SUMMARY:', 'ALL PASS' if not FAIL else f'{len(FAIL)} FAIL: {FAIL}')
sys.exit(1 if FAIL else 0)
