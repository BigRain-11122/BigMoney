"""r285 bm-b: watch faces — pool entries (CN_TREND_ETF_P1 / REV_OSC), Optuna unlock criterion.

r284 lineage verbatim (trader-count face = registered VALIDATED only:
firm/traders/*.json EXCLUDING PROS-* prospect sleeves and _template.json
placeholder id), re-run per r284 'next' pointer.
"""
import json, os, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'round': 'r285', 'machine': 'bm-b'}

# 1. runnable pool entries for the two watch lanes
pool = json.load(open(os.path.join(ROOT, 'results', 'runnable_pool.json'), encoding='utf-8-sig'))
entries = pool if isinstance(pool, list) else pool.get('jobs', pool.get('entries', []))
watch = []
for e in entries if isinstance(entries, list) else []:
    s = json.dumps(e, ensure_ascii=False)
    if 'CN_TREND' in s or 'CN-TREND' in s or 'REV_OSC' in s or 'REV-OSC' in s:
        keep = {k: e.get(k) for k in ('id', 'ticket_ref', 'prereg_ref', 'runner', 'runner_args', 'lane_owner', 'priority', 'status', 'entered_at', 'claimed_by', 'owner') if k in e}
        watch.append(keep)
out['pool_watch'] = watch
print('pool total entries:', len(entries))
print(json.dumps(watch, ensure_ascii=False, indent=1)[:1600])

# 2. Optuna unlock criterion: registered validated traders >= 8 (count face: exclude PROS-*/_template)
validated, prospect, template = [], [], []
for p in glob.glob(os.path.join(ROOT, 'firm', 'traders', '*.json')):
    base = os.path.basename(p)
    if base == '_template.json':
        template.append(base)
    elif base.startswith('PROS-'):
        prospect.append(base)
    else:
        validated.append(base[:-5])
out['optuna_unlock'] = {
    'criterion': 'registered validated >= 8 (frozen O-20260924-1120)',
    'validated_n': len(validated), 'validated': sorted(validated),
    'prospect_sleeves_excluded_n': len(prospect),
    'template_excluded': template,
    'unlocked': len(validated) >= 8,
}
print('validated:', sorted(validated), '-> Optuna stays gated' if len(validated) < 8 else '-> Optuna UNLOCK eligible')

json.dump(out, open(os.path.join(ROOT, 'results', '_r285bmb_watch_faces.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written results/_r285bmb_watch_faces.json')
