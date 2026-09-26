import json, re, time, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
raw = io.open('results/guorn_home_raw.html', encoding='utf-8', errors='replace').read()
pat = re.compile(r'<a[^>]+href="(?:https?://(?:www\.)?guorn\.com)?/forum/post/(p\.[\d.]+)"[^>]*>(.*?)</a>', re.S)
seen = {}
for m in pat.finditer(raw):
    anchor = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    seen.setdefault(m.group(1), anchor)
allm = sorted(set(re.findall(r'(?:https?://(?:www\.)?guorn\.com)?/forum/post/(p\.[\d.]+)', raw)))
posts = [{'url': '/forum/post/' + p, 'anchor': seen.get(p, '')} for p in allm]
base = json.load(open('results/guorn_anchor_baseline.json', encoding='utf-8-sig'))
prev = {p['url'].rsplit('/', 1)[1] for p in base['posts']}
cur = set(allm)
new = sorted(cur - prev)
rolled = sorted(prev - cur)
print('posts:', len(allm), '| new:', len(new), '| rolled:', len(rolled),
      '| anchors:', sum(1 for p in posts if p['anchor']))
ts = time.strftime('%Y-%m-%dT%H:%M') + time.strftime('%z')[:3]
json.dump({'ts': ts, 'url': 'https://guorn.com/', 'posts': posts, 'new': new, 'rolled_out': rolled,
           'note': 'guorn run-3 weekly sample (wave10 face-a, bm-b): full unique /forum/post/ href extraction '
                   '(R169 raw-HTML recipe, optional-domain variant); fetch face = PowerShell Invoke-WebRequest '
                   'schannel (python urllib SSL self-signed-chain fail on bm-b, one-retry channel-switch honest '
                   'note); raw persisted results/guorn_home_raw.html; diff vs run-2 machine baseline'},
          open('results/guorn_anchor_baseline.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('baseline rolled')
