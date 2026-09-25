import io, json, re, os

FILES = [
    'results/autofill_state.json',
    'results/compute_audit.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/token_usage.json',
    'results/update_status.json',
]

def split_blocks(text):
    """Return list of (head_side, ours_side) conflict blocks + non-conflict remainder skeleton."""
    blocks = []
    lines = text.split('\n')
    state = 'common'
    cur = {'head': [], 'ours': []}
    for ln in lines:
        if ln.startswith('<<<<<<<'):
            state = 'head'
            continue
        if ln.startswith('======='):
            state = 'ours'
            continue
        if ln.startswith('>>>>>>>'):
            blocks.append((cur['head'], cur['ours']))
            cur = {'head': [], 'ours': []}
            state = 'common'
            continue
        if state == 'head':
            cur['head'].append(ln)
        elif state == 'ours':
            cur['ours'].append(ln)
    return blocks

def try_json(txt):
    try:
        return json.loads(txt)
    except Exception as e:
        return ('ERR', str(e)[:80])

for f in FILES:
    t = io.open(f, encoding='utf-8').read()
    blocks = split_blocks(t)
    n = len(blocks)
    # extract full head side and ours side by reconstructing: replace block with head lines / ours lines
    lines = t.split('\n')
    head_lines, ours_lines = [], []
    state = 'common'
    for ln in lines:
        if ln.startswith('<<<<<<<'):
            state = 'head'; continue
        if ln.startswith('======='):
            state = 'ours'; continue
        if ln.startswith('>>>>>>>'):
            state = 'common'; continue
        if state == 'head':
            head_lines.append(ln); continue
        if state == 'ours':
            ours_lines.append(ln); continue
        head_lines.append(ln); ours_lines.append(ln)
    head_full = '\n'.join(head_lines)
    ours_full = '\n'.join(ours_lines)
    hj = try_json(head_full)
    oj = try_json(ours_full)
    def sm(x):
        if isinstance(x, dict):
            ts = {k: x[k] for k in ('ts', 'updated', 'now', 'generated', 'generated_at') if k in x}
            return 'dict keys=%d ts=%s' % (len(x), json.dumps(ts, ensure_ascii=False)[:120])
        return str(x)[:100]
    print('%-42s blocks=%d head[%s] ours[%s]' % (os.path.basename(f), n, sm(hj), sm(oj)))
