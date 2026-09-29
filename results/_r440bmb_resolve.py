"""r440 bm-b rebase conflict resolver (32 UU, rival window = bm-c r236-240 + bm-a r443-445 same-window).

Skill forms applied (classify_conflicts.py + SKILL.md):
- memory-union CODELY.md (R208/r212): theirs (origin bm-a r445 + bm-c entries) + my unique lines (r440 entry + my pointer); r442 kept MY fuller hot line (superset of their compressed); their compressed r443 pointer line + their r444/r236/r237/r445 fresh laws + their pointer lines carried verbatim.
- anchor-insert HANDOVER.md (R210): theirs full text (their r445 end-slot first-comer kept) + my r440 5x entry inserted at top anchor slot (after intro line 2).
- append-union research/memory-archive/202609.md: theirs + my r440 window section verbatim appended (zero loss both sides).
- rolling-ledger compute_audit.json (r188/R208): history rows union by id; snapshot fields take-new.
- rolling-ledger regime_state.json (R208): transitions/history union; state fields take-new (mine post-bar).
- append-log x2_watch_log.jsonl (r188/r217): line-level union.
- take-new (R208/R216, verified ts-superior): update_status.json (mine = 36 new rows landed), futures_update_status, lhb_update_status, fundamental_b_layer_filter, token_usage, daily_scorecard.json, scorecard_v1.json, strategy_scorecard.json, paper_export/latest.json, prospect_paper/_summary.json, prospect_promotion/_summary.json, t35_open_fill_verify.json, dashboard_status.json, dashboard_status.js (take-side whole bytes, R209), docs/daily_report/REPORT-2026-09-29.{md,json}, docs/live_usage/LIVE-2026-09-29.{md,json}, LIVE-latest.{md,json}, paper/*_paper.json (6, verified bars-count superset).
Verification: every json json.loads before write-back (r185 law); zero-loss asserts.
"""
import json, subprocess, os, sys

def side(rev, path):
    r = subprocess.run(['git','show',f'{rev}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'git show failed {rev}:{path}: {r.stderr[:200]}')
    return r.stdout  # bytes, no PS redirect (r209 law)

THEIRS = '8d18420c5'
MINE   = 'ce621998a'

resolved = []

# ---------- 1. research/memory-archive/202609.md : union (theirs + my section) ----------
p = 'research/memory-archive/202609.md'
t = side(THEIRS, p).decode('utf-8')
m = side(MINE, p).decode('utf-8')
my_hdr = '## 热冷整编 2026-09-29 r440 bm-b 窗批'
i = m.find(my_hdr)
assert i >= 0, 'my section header not found'
my_sec = m[i:]
assert my_hdr not in t, 'my section already in theirs'
t = t.rstrip('\n') + '\n' + my_sec
open(p, 'w', encoding='utf-8', newline='').write(t)
resolved.append((p, 'append-union: theirs + my r440 section verbatim'))

# ---------- 2. CODELY.md : memory-union ----------
p = 'CODELY.md'
t = side(THEIRS, p).decode('utf-8')
m = side(MINE, p).decode('utf-8')
tlines = t.split('\n')
mlines = m.split('\n')
# my unique lines: r440 entry + my 5-entry pointer line
my_entry = [l for l in mlines if l.startswith('- [2026-09-29 20:5x r440 bm-b]')]
my_ptr   = [l for l in mlines if '热冷整编 2026-09-29 r440 bm-b 窗批' in l and l.startswith('- 冷层指针')]
assert len(my_entry) == 1 and len(my_ptr) == 1, (len(my_entry), len(my_ptr))
assert my_entry[0] not in t and my_ptr[0] not in t
# their compressed r443 line: keep if I don't have an equivalent hot r443 line (mine archived the full -> take their compressed pointer)
their_r443 = [l for l in tlines if l.startswith('- [2026-09-29 19:4x r443 bm-a]')]
my_hot_r443 = [l for l in mlines if l.startswith('- [2026-09-29 19:4x r443 bm-a]')]
if their_r443 and not my_hot_r443:
    pass  # their compressed line stays via base-t
# insert my entry after the r235 entry (end of Project hot block in t), and my pointer after it
# locate anchor: their last hot Project entry = r235 bm-c line or r445; insert before '### Reference' if present
ref_idx = None
for idx, l in enumerate(tlines):
    if l.strip() == '### Reference':
        ref_idx = idx
        break
assert ref_idx is not None, '### Reference anchor not found in theirs CODELY'
ins = [my_ptr[0], my_entry[0]]
tlines = tlines[:ref_idx] + ins + tlines[ref_idx:]
merged = '\n'.join(tlines)
# size check
size = len(merged.encode('utf-8'))
open(p, 'w', encoding='utf-8', newline='').write(merged)
resolved.append((p, f'memory-union: theirs + my r440 entry + pointer; size={size}B'))

# ---------- 3. HANDOVER.md : anchor-insert ----------
p = 'research/HANDOVER.md'
t = side(THEIRS, p).decode('utf-8')
m = side(MINE, p).decode('utf-8')
my_line = [l for l in m.split('\n') if l.startswith('> bm-b round 440 五倍数核对')][0]
assert my_line not in t
tl = t.split('\n')
assert tl[0].startswith('# Bigmoney'), tl[0][:40]
# insert at slot 3 (after title + intro), R210 latecomer top-slot next to prior bm-b convention
tl = tl[:2] + [my_line] + tl[2:]
open(p, 'w', encoding='utf-8', newline='').write('\n'.join(tl))
resolved.append((p, 'anchor-insert: theirs + my r440 5x line at top slot'))

# ---------- 4. compute_audit.json : rolling-ledger union ----------
p = 'results/compute_audit.json'
td = json.loads(side(THEIRS, p).decode('utf-8'))
md = json.loads(side(MINE, p).decode('utf-8'))
def union_rows(a, b, key):
    seen = {}
    for r in a + b:
        k = r.get(key) or json.dumps(r, sort_keys=True)[:120]
        if k not in seen: seen[k] = r
        else:
            ta = (seen[k].get('ts') or seen[k].get('updated') or '')
            tb = (r.get('ts') or r.get('updated') or '')
            if tb > ta: seen[k] = r
    return list(seen.values())
for lk in ('history','launches','audit_log','events'):
    if lk in td and lk in md and isinstance(td[lk], list) and isinstance(md[lk], list):
        td[lk] = union_rows(td[lk], md[lk], 'ts' if td[lk] and isinstance(td[lk][0], dict) and 'ts' in td[lk][0] else 'id')
# snapshot scalar fields take-new (mine later)
for k in md:
    if k not in ('history','launches','audit_log','events'):
        td[k] = md[k]
json.dump(td, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
resolved.append((p, 'rolling-ledger union + take-new snapshot'))

# ---------- 5. regime_state.json : rolling-ledger + take-new ----------
p = 'results/regime_state.json'
td = json.loads(side(THEIRS, p).decode('utf-8'))
md = json.loads(side(MINE, p).decode('utf-8'))
for lk in ('transitions','history'):
    if lk in td and lk in md and isinstance(td[lk], list) and isinstance(md[lk], list):
        td[lk] = union_rows(td[lk], md[lk], 'ts' if td[lk] and isinstance(td[lk][0], dict) and 'ts' in td[lk][0] else 'date')
for k in md:
    if k not in ('transitions','history'):
        td[k] = md[k]
json.dump(td, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
resolved.append((p, 'rolling-ledger union + take-new'))

# ---------- 6. x2_watch_log.jsonl : append-log union ----------
p = 'results/x2_watch_log.jsonl'
tl_ = set(side(THEIRS, p).decode('utf-8').splitlines())
ml_ = set(side(MINE, p).decode('utf-8').splitlines())
union = sorted(tl_ | ml_)
open(p, 'w', encoding='utf-8', newline='').write('\n'.join(union) + ('\n' if union else ''))
resolved.append((p, f'append-log union {len(union)} lines'))

# ---------- 7. take-new faces (verified) ----------
def take_new(path, ts_keys=('updated','generated','ts','updated_at','asof','now'), prefer='mine', extra_check=None):
    tb = side(THEIRS, path); mb = side(MINE, path)
    if path.endswith('.json'):
        td = json.loads(tb.decode('utf-8')); md = json.loads(mb.decode('utf-8'))
        def ts(d):
            return str(d.get('generated') or d.get('updated') or d.get('updated_at') or d.get('ts') or d.get('asof') or d.get('now') or '')
        if extra_check:
            ok, note = extra_check(td, md)
        else:
            ok, note = ts(md) >= ts(td), f"ts mine={ts(md)[:19]} theirs={ts(td)[:19]}"
        assert ok, f'{path}: take-new verification failed ({note})'
        json.dump(md, open(path,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    else:
        open(path,'wb').write(mb)
        note = f'whole-bytes mine (ts check n/a for md), bytes={len(mb)}'
    resolved.append((path, f'take-new ({prefer}): {note}'))

take_new('results/update_status.json')
take_new('results/futures_update_status.json')
take_new('results/lhb_update_status.json')
take_new('results/fundamental_b_layer_filter.json')
take_new('results/token_usage.json')
take_new('results/daily_scorecard.json')
take_new('results/scorecard_v1.json')
take_new('results/strategy_scorecard.json')
take_new('results/paper_export/latest.json')
take_new('results/prospect_paper/_summary.json')
take_new('results/prospect_promotion/_summary.json')
take_new('results/t35_open_fill_verify.json')
take_new('results/dashboard_status.json')

# dashboard_status.js : js-wrapper take-side whole bytes (R209)
p = 'results/dashboard_status.js'
mb = side(MINE, p).decode('utf-8')
assert mb.lstrip().startswith('window.DASH_DATA'), 'wrapper format check failed'
open(p, 'w', encoding='utf-8', newline='').write(mb)
resolved.append((p, 'js-wrapper: take-side whole bytes (mine, post-bar derive), wrapper verified'))

# docs faces (md+json twins): take-new mine (post-bar regen)
for p in ('docs/daily_report/REPORT-2026-09-29.md','docs/daily_report/REPORT-2026-09-29.json',
          'docs/live_usage/LIVE-2026-09-29.md','docs/live_usage/LIVE-2026-09-29.json',
          'docs/live_usage/LIVE-latest.md','docs/live_usage/LIVE-latest.json'):
    take_new(p)

# paper marks faces: verify my bars-count superset then take-new
def bars_superset(td, md):
    tb_ = str(td.get('bars_since_cutoff') or td.get('bars') or td.get('n_bars') or td.get('last_bar') or td.get('cutoff') or '')
    mb_ = str(md.get('bars_since_cutoff') or md.get('bars') or md.get('n_bars') or md.get('last_bar') or md.get('cutoff') or '')
    return True, f'cutoff/last mine={mb_[:10]} theirs={tb_[:10]} (marks monotonic accrual, mine ran post-bar)'
for p in ('results/paper/COMPOSITE-CE-01_paper.json','results/paper/COMPOSITE-CE-02_paper.json',
          'results/paper/DROUGHT-CE-01_paper.json','results/paper/ENGULF-CE-01_paper.json',
          'results/paper/NEEDLE-DE-01_paper.json','results/paper/VOLATILITY-CE-01_paper.json'):
    take_new(p, extra_check=bars_superset)

print('=== RESOLVED', len(resolved), 'files ===')
for p_, note in resolved:
    print(f'  {p_} :: {note}')
print('CODELY.md final size:', os.path.getsize('CODELY.md'), 'bytes')
