import glob, json, os
base = r'C:\Users\Administrator\Desktop\Bigmoney'
for p in sorted(glob.glob(os.path.join(base, 'fleet', 'tasks', '*.json'))):
    d = json.load(open(p, encoding='utf-8-sig'))
    tid = d.get('id') or os.path.basename(p)
    st = d.get('status')
    im = ' IMMEDIATE' if d.get('immediate') else ''
    cb = d.get('claimed_by', '-')
    title = str(d.get('title', ''))[:70]
    print(f"{tid}: {st}{im} claimed_by={cb} | {title}")
print('===WM-RED===')
wr = os.path.join(base, 'results', 'watermark_red.json')
if os.path.exists(wr):
    print(open(wr, encoding='utf-8').read())
else:
    print('watermark_red.json ABSENT')
print('===WM-LATEST===')
wl = os.path.join(base, 'results', 'watermark.jsonl')
if os.path.exists(wl):
    lines = open(wl, encoding='utf-8').read().strip().splitlines()
    print(lines[-1] if lines else 'EMPTY')
else:
    print('watermark.jsonl ABSENT')
print('===NEXT_PICK===')
sc = os.path.join(base, 'results', 'strategy_scorecard.json')
if os.path.exists(sc):
    d = json.load(open(sc, encoding='utf-8'))
    bp = d.get('bandit_pool') or {}
    print('bandit next_pick:', json.dumps(bp.get('next_pick', bp if not isinstance(bp, dict) else ''), ensure_ascii=False)[:400])
