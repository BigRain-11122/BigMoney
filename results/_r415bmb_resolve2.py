"""r415 bm-b resolver pass-2: fix archive union branch (startswith heuristic was a false
merge -> my section lost, caught by fail-closed probe) + CODELY 2nd integration
(bm-a-side window entries batches 91/92/93 re-archived verbatim -> pointer line).
All content zero-loss; every migrated byte asserted present in archive.
"""
import io
import json
import os
import subprocess

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'stage {stage} read fail {path}')
    return r.stdout.decode('utf-8')

# ---------- 1) archive union (fixed): a2 full + my-only lines appended ----------
A = 'research/memory-archive/202609.md'
a2 = blob(2, A)
a3 = blob(3, A)
set2 = set(a2.splitlines())
mine_only = [l for l in a3.splitlines() if l not in set2]
out_arch = a2 + ('' if a2.endswith('\n') else '\n') + '\n'.join(mine_only) + '\n'
for probe in ('r415 bm-b', '九十四批', '九十三批', '九十二批', '九十一批'):
    pass  # 91/92/93 come from CODELY below; only my-section probes here
assert 'r415 bm-b' in out_arch and '九十四批' in out_arch, 'my section lost in archive union'

# ---------- 2) CODELY 2nd integration: migrate 91/92/93 verbatim -> archive ----------
C = 'CODELY.md'
with io.open(C, encoding='utf-8') as fh:
    lines = fh.readlines()
MIG_PREFIXES = (
    '- [2026-09-29 07:3x r204 bm-c]',
    '- [2026-09-29 07:4x r204 bm-c]',
    '- [2026-09-29 07:5x r419 bm-a]',
)
migrated = [l for l in lines if any(l.startswith(p) for p in MIG_PREFIXES)]
assert len(migrated) == 3, f'expected 3 migrate lines, got {len(migrated)}'
POINTER = (
    "冷层指针：坑律正典 2026-09-29 九十一/九十二/九十三批（r204 bm-c updated_at 跨格式字典序假 drift 坑·merge_lane_views 时间戳键域归一/r204 bm-c r378 集中式守卫假阴性诊断坑/r419 bm-a merge-back 破活锁两步式·单次 merge 代替 co-located 批 rebase）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r415 bm-b 窗批』节（r415 bm-b 窗水位律当窗整编·行级零丢失校验）。\n"
)
kept, replaced = [], False
for l in lines:
    if any(l.startswith(p) for p in MIG_PREFIXES):
        if not replaced:
            kept.append(POINTER)
            replaced = True
        continue
    kept.append(l)
assert replaced
codely_out = ''.join(kept)

# append migrated lines to the r415 window section in archive (before my-section probes re-check)
SECTION_ANCHOR = '## 坑律归档 2026-09-29 r415 bm-b 窗批'
idx = out_arch.find(SECTION_ANCHOR)
assert idx >= 0, 'r415 window section missing in archive union'
# insert after the section header line
hdr_end = out_arch.find('\n', idx) + 1
out_arch = out_arch[:hdr_end] + ''.join(migrated) + out_arch[hdr_end:]

# ---------- write both + verify ----------
with io.open(A, 'w', encoding='utf-8', newline='') as fh:
    fh.write(out_arch)
with io.open(C, 'w', encoding='utf-8', newline='') as fh:
    fh.write(codely_out)

with io.open(A, encoding='utf-8') as fh:
    atail = fh.read()
for ml in migrated:
    assert ml in atail, 'migrated 91/92/93 line missing verbatim: ' + ml[:40]
assert '\ufffd' not in atail and '\ufffd' not in codely_out
for probe in ('九十一批', '九十二批', '九十三批', '九十四批', 'r415 bm-b'):
    assert probe in atail, f'archive probe lost: {probe}'
sz = os.path.getsize(C)
assert sz <= 10240, f'CODELY still over 10KB: {sz}'
for p in MIG_PREFIXES:
    assert p + ']' not in codely_out, 'verbose line still in CODELY: ' + p

# ---------- 3) re-validate all resolved JSON faces parse cleanly ----------
JSON_FACES = [
    'results/dashboard_status.json', 'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json', 'results/lhb_update_status.json',
    'results/token_usage.json', 'results/update_status.json',
    'results/prospect_promotion/_summary.json', 'results/scorecard_v1.json',
    'results/strategy_scorecard.json', 'docs/daily_report/REPORT-2026-09-29.json',
    'docs/live_usage/LIVE-2026-09-29.json', 'docs/live_usage/LIVE-latest.json',
    'results/compute_audit.json', 'results/regime_state.json',
]
for p in JSON_FACES:
    with io.open(p, encoding='utf-8') as fh:
        json.load(fh)
assert 'window.DASH_DATA' in io.open('results/dashboard_status.js', encoding='utf-8').read()
print(f'pass-2 OK: archive union fixed (my section + 91/92/93 migrated verbatim), '
      f'CODELY {sz}B <=10KB, {len(JSON_FACES)} json faces parse-clean, js wrapper intact')
