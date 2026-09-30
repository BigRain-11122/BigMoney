# r486 bm-b S0: rebuild lane pool runnable_pool.bm-b.json surgically = HEAD text + r485 merge 30 LOWAMP entries
import json, subprocess, os

head_txt = subprocess.check_output(['git', 'show', 'HEAD:results/runnable_pool.bm-b.json']).decode('utf-8-sig')
mine_txt = open(os.path.join(os.environ['TEMP'], 'r486_pool_mine.json'), encoding='utf-8-sig').read()  # placeholder ref
mine_txt = open('results/runnable_pool.bm-b.json', encoding='utf-8-sig').read()

head = json.loads(head_txt)
mine = json.loads(mine_txt)
head_ids = [e['id'] for e in head['entries']]
head_set = set(head_ids)
new_entries = [e for e in mine['entries'] if e['id'] not in head_set]
print('new entries:', len(new_entries))
print('their positions in mine:', [i for i, e in enumerate(mine['entries']) if e['id'] not in head_set][:35])

top_diffs = []
for k in mine:
    if k == 'entries':
        continue
    if k not in head:
        top_diffs.append(('added-key', k))
    elif mine[k] != head[k]:
        top_diffs.append(('changed', k))
print('top-level diffs:', top_diffs)

# insert new entries at their mine-positions to keep ordering faithful (they may be appended)
out_entries = list(head['entries'])
for e in new_entries:
    # find position by scanning mine order relative to neighbors: use mine index among ALL entries
    mi = [x['id'] for x in mine['entries']].index(e['id'])
    # insertion index in out: count of mine entries before mi that are already in out
    prior_ids = [x['id'] for x in mine['entries'][:mi]]
    pos = sum(1 for pid in prior_ids if pid in head_set)
    out_entries.insert(pos, e)

out = dict(head)
out['entries'] = out_entries
for kind, k in top_diffs:
    out[k] = mine[k]

txt = json.dumps(out, ensure_ascii=False, indent=2)
if '\r\n' in head_txt:
    txt = txt.replace('\n', '\r\n')
with open('results/runnable_pool.bm-b.json', 'w', newline='', encoding='utf-8') as f:
    f.write(txt)

chk = json.loads(open('results/runnable_pool.bm-b.json', encoding='utf-8-sig').read())
assert len(chk['entries']) == len(head['entries']) + len(new_entries)
mine_seq = [e['id'] for e in mine['entries']]
chk_seq = [e['id'] for e in chk['entries']]
assert [i for i in chk_seq if i in head_set] == head_ids, 'HEAD order preserved'
print('lane rebuild OK:', len(chk['entries']), 'entries; HEAD order preserved')
