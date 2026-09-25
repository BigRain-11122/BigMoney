import sys, io, re, html
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


qid, pat = sys.argv[1], sys.argv[2]
raw = io.open('results/jisilu_%s.html' % qid, encoding='utf-8').read()
i = raw.find(pat)
if i < 0:
    print('NOT FOUND in raw')
    sys.exit(0)
seg = raw[max(0, i - 200):i + int(sys.argv[3] if len(sys.argv) > 3 else 6000)]
print(strip(seg)[:4000])
