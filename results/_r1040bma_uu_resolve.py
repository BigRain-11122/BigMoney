# r1040 UU resolve: shared probe faces, ts newer-wins (r1028 recipe)
# rebase context: ours=HEAD (origin side), theirs=commit being replayed (bm-a absorb face)
import json, re, io

FILES = ['results/watermark_red.json', 'results/zt_pool_crosscheck.json']

def pick_newer(ours: str, theirs: str) -> str:
    def ts_of(block: str):
        m = re.search(r'"ts"\s*:\s*"([^"]+)"', block)
        return m.group(1) if m else ''
    to, tt = ts_of(ours), ts_of(theirs)
    # newer-wins on ts; tie or missing -> take ours (origin) for safety on ties
    if to and tt:
        return theirs if tt > to else ours
    return theirs if tt else ours

for p in FILES:
    raw = io.open(p, encoding='utf-8', newline='').read()
    pat = re.compile(r'<<<<<<< HEAD\r?\n(.*?)=======\r?\n(.*?)>>>>>>> [^\r\n]*\r?\n', re.S)
    resolved, n = pat.subn(lambda m: pick_newer(m.group(1), m.group(2)), raw)
    # validate JSON after resolution
    json.loads(resolved.replace('\r\n', '\n').replace('\n\n', '\n') if False else resolved)
    io.open(p, 'w', encoding='utf-8', newline='').write(resolved)
    print(p, 'hunks_resolved', n, 'json_ok')
print('DONE')
