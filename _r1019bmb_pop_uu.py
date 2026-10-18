# r1019 push-window stash-pop UU resolver: token_usage r1008 union + watermark_red
# ts newer-wins (r1028). ASCII only.
import subprocess, json

def raw(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True).stdout

ev = []

# token_usage.json: HEAD base + stash bm-b row (r1008 per-machine union)
p = 'results/token_usage.json'
o, l = json.loads(raw('HEAD', p).decode('utf-8', 'replace')), json.loads(raw('stash@{0}', p).decode('utf-8', 'replace'))
if 'bm-b' in l.get('machines', {}):
    o['machines']['bm-b'] = l['machines']['bm-b']
    ev.append('bm-b row <- stash (post-S6 token_meter run)')
o['generated'] = max(str(o.get('generated', '')), str(l.get('generated', '')))
with open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(o, f, indent=2, ensure_ascii=True)
    f.write('\n')

# watermark_red.json: ts newer-wins (60s idleguard tick regenerates anyway)
p = 'results/watermark_red.json'
o, l = json.loads(raw('HEAD', p).decode('utf-8', 'replace')), json.loads(raw('stash@{0}', p).decode('utf-8', 'replace'))
win = l if str(l.get('ts', '')) > str(o.get('ts', '')) else o
with open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(win, f, indent=2, ensure_ascii=True)
    f.write('\n')
ev.append('watermark_red: HEAD[%s] stash[%s] -> %s' % (
    o.get('ts'), l.get('ts'), 'STASH' if win is l else 'HEAD'))

subprocess.run(['git', 'add', '--', 'results/token_usage.json', 'results/watermark_red.json'],
               capture_output=True)
subprocess.run(['git', 'restore', '--staged', '--',
                'results/token_usage.json', 'results/watermark_red.json'], capture_output=True)
r = subprocess.run(['git', 'ls-files', '--unmerged'], capture_output=True)
n = len(r.stdout.decode().strip().splitlines())
print('RESOLVED: ' + ' | '.join(ev))
print('unmerged-left:', n)
assert n == 0
