# r1019 S0 stash-pop UU resolver v2 (bm-b). Whole-file winner picks keep raw bytes
# (no re-serialization risk); token_usage real per-machine union (r1008).
# Laws: r1015/r1017 regen origin-newer-wins, r1028 ts newer-wins, r1008 union.
# Stash was dropped; local side read from recorded sha baa47cb7.
import subprocess, json

STASH = 'baa47cb768042915487d141c1b7ab20cafec0461'

def raw(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True).stdout

def pick_raw(path, winner, why):
    with open(path, 'wb') as f:
        f.write(raw(winner, path))
    print(f'PICK {path}: {winner} ({why})')

def jload(rev, path):
    return json.loads(raw(rev, path).decode('utf-8', errors='replace'))

ev = []

# 1) machine-health: origin whole-file (r1015 law; local bm-b snapshot droppable,
#    hourly daemon rewrites -- self-healing)
pick_raw('fleet/machine-health.json', 'HEAD', 'r1015 origin-wins, daemon self-heal')

# 2) futures_update_status: ts newer-wins
o, l = jload('HEAD', 'results/futures_update_status.json'), jload(STASH, 'results/futures_update_status.json')
w = 'HEAD' if o['ts'] >= l['ts'] else STASH
pick_raw('results/futures_update_status.json', w, f"ts {o['ts']} vs {l['ts']}")

# 3) lhb_update_status: updated newer-wins
o, l = jload('HEAD', 'results/lhb_update_status.json'), jload(STASH, 'results/lhb_update_status.json')
ov, lv = str(o.get('updated', o.get('last_attempt', ''))), str(l.get('updated', l.get('last_attempt', '')))
w = 'HEAD' if ov >= lv else STASH
pick_raw('results/lhb_update_status.json', w, f'updated {ov} vs {lv}')

# 4) watermark_red: ts newer-wins (r1028; 60s tick regenerates anyway)
o, l = jload('HEAD', 'results/watermark_red.json'), jload(STASH, 'results/watermark_red.json')
w = 'HEAD' if o['ts'] >= l['ts'] else STASH
pick_raw('results/watermark_red.json', w, f"ts {o['ts']} vs {l['ts']}")

# 5) token_usage: origin base + local bm-b row (r1008 per-machine union)
p = 'results/token_usage.json'
o, l = jload('HEAD', p), jload(STASH, p)
if 'bm-b' in l.get('machines', {}):
    o['machines']['bm-b'] = l['machines']['bm-b']
    ev.append('bm-b row <- local')
o['generated'] = max(str(o.get('generated', '')), str(l.get('generated', '')))
with open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(o, f, indent=2, ensure_ascii=True)
    f.write('\n')
print('MERGE token_usage.json: origin base + ' + ' | '.join(ev))

files = ['fleet/machine-health.json', 'results/futures_update_status.json',
         'results/lhb_update_status.json', 'results/watermark_red.json',
         'results/token_usage.json']
subprocess.run(['git', 'add', '--'] + files, capture_output=True)
subprocess.run(['git', 'restore', '--staged', '--'] + files, capture_output=True)
r = subprocess.run(['git', 'ls-files', '--unmerged'], capture_output=True)
n = len(r.stdout.decode().strip().splitlines())
print('unmerged-left:', n)
assert n == 0, 'UU not cleared'
