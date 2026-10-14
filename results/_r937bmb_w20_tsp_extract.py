"""r937 bm-b W20 enrollment slice-1: tick-stock-panel per-family collision census.

Extracts entry-condition faces from the 25 fixture strategies (fetched via
GitHub blobs API into results/_r937bmb_w20_tsp_corpus/) and emits a compact
entry-face digest for the roster mapping (results/_r937bmb_w20_tsp_entryfaces.txt).
"""
import io, glob, os, re

OUT = 'results/_r937bmb_w20_tsp_entryfaces.txt'
out = io.open(OUT, 'w', encoding='utf-8')
n = 0
for p in sorted(glob.glob('results/_r937bmb_w20_tsp_corpus/backend__tests__fixtures__strategies__*.py')):
    src = io.open(p, encoding='utf-8').read()
    m = re.search(r'META\s*=\s*\{(.*?)\n\}', src, re.S)
    meta_id = re.search(r'"id":\s*"([^"]+)"', m.group(1)).group(1) if m else '?'
    meta_name = re.search(r'"name":\s*"([^"]+)"', m.group(1)).group(1) if m else '?'
    at = re.search(r'"asset_types":\s*\[([^\]]*)\]', m.group(1)).group(1) if m else '?'
    entry = re.search(r'ENTRY_SIGNALS\s*=\s*\[([^\]]*)\]', src)
    exit_ = re.search(r'EXIT_SIGNALS\s*=\s*\[([^\]]*)\]', src)
    rf = re.search(r'required_fields.*?frozenset\(\{([^}]*)\}', src, re.S)
    cs = re.search(r'(def compute_signals.*?)(\n    def |\Z)', src, re.S)
    body = cs.group(1) if cs else ''
    body_clean = '\n'.join(l for l in body.splitlines() if l.strip())[:2400]
    out.write('### %s | name=%s | assets=%s | ENTRY=%s | EXIT=%s | fields=%s\n' % (
        meta_id, meta_name, at.strip(),
        entry.group(1) if entry else '?',
        exit_.group(1) if exit_ else '?',
        rf.group(1).strip() if rf else '?'))
    out.write(body_clean + '\n\n')
    n += 1
out.close()
print('files digested:', n, 'bytes:', os.path.getsize(OUT))
