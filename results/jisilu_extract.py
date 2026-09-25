import sys, io, re, html, collections
sys.stdout.reconfigure(encoding='utf-8')


def strip(x):
    x = re.sub(r'<script.*?</script>', '', x, flags=re.S)
    x = re.sub(r'<style.*?</style>', '', x, flags=re.S)
    x = re.sub(r'<br\s*/?>', '\n', x)
    x = re.sub(r'</p>', '\n', x)
    x = re.sub(r'<[^>]+>', '', x)
    x = html.unescape(x)
    x = re.sub(r'\n{3,}', '\n\n', x)
    return x.strip()


def blocks(raw):
    out = []
    for m in re.finditer(r'<div class="markitup-box[^"]*"[^>]*>(.*?)</div>', raw, re.S):
        t = strip(m.group(1))
        if t:
            out.append(t)
    return out


def load(qid):
    return io.open('results/jisilu_%s.html' % qid, encoding='utf-8').read()


if sys.argv[1] == 'meta':
    for qid in sys.argv[2:]:
        raw = load(qid)
        m = re.search(r'name="description" content="([^"]+)"', raw)
        v = re.search(r'>(\d[\d,]+)</em>\s*浏览', raw) or re.search(r'浏览[^0-9]{0,10}(\d[\d,]+)', raw)
        print(qid, '| views:', v.group(1) if v else '?')
        print('   desc:', html.unescape(m.group(1))[:240] if m else 'NONE')
    sys.exit(0)

if sys.argv[1] == 'grep':
    pat = sys.argv[2]
    for qid in sys.argv[3:]:
        bs = blocks(load(qid))
        print('=' * 20, qid, 'blocks:', len(bs), '=' * 20)
        for i, b in enumerate(bs):
            if re.search(pat, b):
                print('--- block %d ---' % i)
                print(b[:1600])
    sys.exit(0)

if sys.argv[1] == 'inspect':
    for qid in sys.argv[2:]:
        raw = load(qid)
        c = collections.Counter(re.findall(r'class="([a-zA-Z-]+)"', raw))
        print(qid, 'top classes:', c.most_common(25))
    sys.exit(0)

for qid in sys.argv[1:]:
    raw = load(qid)
    bs = blocks(raw)
    joined = strip(raw)
    meta = re.search(r'(\d[\d,]*)\s*次浏览', joined)
    print('=' * 20, qid, 'blocks:', len(bs), '=' * 20)
    print('views:', meta.group(1) if meta else '?')
    t = re.search(r'<title>(.*?)</title>', raw, re.S)
    print('title:', html.unescape(t.group(1)).strip() if t else 'NONE')
    for i, b in enumerate(bs[:14]):
        print('--- block %d (%d chars) ---' % (i, len(b)))
        print(b[:1500])
