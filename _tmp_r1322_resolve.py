import subprocess, io, re, sys

def stage(n):
    p = subprocess.run(['git','show',f':{n}:knowledge/METHODOLOGY_ASSETS.md'],
                       capture_output=True)
    return p.stdout.decode('utf-8')

base = stage(1)
ours = stage(2)
theirs = stage(3)

# our card = the block that theirs added relative to base
bl = theirs.split('\n')
idx = next(i for i,l in enumerate(bl) if l.startswith('## E183 '))
card = '\n'.join(bl[idx:]).rstrip('\n')

used = set(int(m) for m in re.findall(r'^## E(\d+)', ours, re.M))
n = max(used) + 1
card = card.replace('## E183 ', f'## E{n} ', 1)
card = card.replace('E183/', f'E{n}/')

# sanity: ours must not already contain this card body
assert 'Four published numbers, one book' not in ours, 'already present'
assert card not in ours

out = ours.rstrip('\n') + '\n\n' + card + '\n'
with io.open('knowledge/METHODOLOGY_ASSETS.md','w',encoding='utf-8',newline='\n') as f:
    f.write(out)
print('card renumbered to E%d; appended %d chars' % (n, len(card)))