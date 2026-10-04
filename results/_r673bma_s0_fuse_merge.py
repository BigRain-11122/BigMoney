# r673 bm-a S0 pre-alignment: crash_fuse.json per-key max-merge (r626d/MSG-0640 law)
# wt has newer fund-trio sigs (11:18:03 > origin 08:38/09:20); origin has newer theme_judge sig (11:10:04 > 11:08:03) + cleared (11:06:18 > 10:46:04)
import json, subprocess, sys

def origin_blob(path):
    return subprocess.run(['git', 'show', 'origin/main:' + path], capture_output=True).stdout

o = json.loads(origin_blob('results/crash_fuse.json').decode('utf-8'))
w = json.loads(open('results/crash_fuse.json', 'rb').read().decode('utf-8'))

merged = {'sigs': {}, 'cleared': {}}
pick_log = {'sigs': {}, 'cleared': {}}

# sigs: union keys, take-newer by last_refusal_ts (tie: greater refusals)
for k in sorted(set(o['sigs']) | set(w['sigs'])):
    oe, we = o['sigs'].get(k), w['sigs'].get(k)
    if oe is None:
        merged['sigs'][k] = we; pick_log['sigs'][k] = 'wt-only'
    elif we is None:
        merged['sigs'][k] = oe; pick_log['sigs'][k] = 'origin-only'
    else:
        ot, wt_ = oe.get('last_refusal_ts', ''), we.get('last_refusal_ts', '')
        if wt_ > ot:
            merged['sigs'][k] = we; pick_log['sigs'][k] = f'wt-newer ({wt_} > {ot})'
        elif ot > wt_:
            merged['sigs'][k] = oe; pick_log['sigs'][k] = f'origin-newer ({ot} > {wt_})'
        else:
            merged['sigs'][k] = we if we.get('refusals', 0) >= oe.get('refusals', 0) else oe
            pick_log['sigs'][k] = f'tie-take-refusals ({merged["sigs"][k].get("refusals")})'

# cleared: union keys, take-newer by cleared_ts
for k in sorted(set(o.get('cleared', {})) | set(w.get('cleared', {}))):
    oe, we = o.get('cleared', {}).get(k), w.get('cleared', {}).get(k)
    if oe is None:
        merged['cleared'][k] = we; pick_log['cleared'][k] = 'wt-only'
    elif we is None:
        merged['cleared'][k] = oe; pick_log['cleared'][k] = 'origin-only'
    else:
        if we.get('cleared_ts', '') >= oe.get('cleared_ts', ''):
            merged['cleared'][k] = we; pick_log['cleared'][k] = f"wt-newer ({we.get('cleared_ts')}) "
        else:
            merged['cleared'][k] = oe; pick_log['cleared'][k] = f"origin-newer ({oe.get('cleared_ts')})"

# zero-loss assertions: every key present, no key dropped
assert set(merged['sigs']) == set(o['sigs']) | set(w['sigs']), 'sigs key loss'
assert set(merged['cleared']) == set(o.get('cleared', {})) | set(w.get('cleared', {})), 'cleared key loss'
# containment-pin notes must survive (r636/r617 keepblock notes)
for k, v in list(o['sigs'].items()) + list(w['sigs'].items()):
    if v.get('note'):
        assert merged['sigs'][k].get('note') == v['note'] or 'note' in json.dumps(merged['sigs'][k]), f'note lost for {k}'
# verify chosen fund sigs are wt-newer ones and theme_judge is origin-newer one
assert merged['sigs']['scripts/fund_quality_p1.py|run,--nulls']['last_refusal_ts'] == '2026-10-04 11:18:03'
assert merged['sigs']['scripts/theme_judge_p1.py|run']['last_refusal_ts'] == '2026-10-04 11:10:04'
assert merged['cleared']['scripts/theme_judge_p1.py|run']['cleared_ts'] == '2026-10-04 11:06:18'

out = json.dumps(merged, ensure_ascii=False, indent=2) + '\n'
open('results/crash_fuse.json', 'wb').write(out.encode('utf-8'))
print('MERGED OK, keys:', len(merged['sigs']), 'sigs,', len(merged['cleared']), 'cleared')
for k, v in pick_log['sigs'].items():
    if 'newer' in v or 'only' in v:
        print(' sig:', k, '->', v)
for k, v in pick_log['cleared'].items():
    print(' cleared:', k, '->', v)
# reparse self-check
json.loads(open('results/crash_fuse.json', 'rb').read().decode('utf-8'))
print('reparse PASS')
