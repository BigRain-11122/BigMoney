import sys, re, html, json, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# hibor.com.cn 金融工程 (jin-gong) title+abstract radar -- RESEARCH_MECHANISM standing channel
# run-2 (R151 wave7-slice4) discovered tab_lta (title+/data/<32hex>.html) + adjacent tab_tdcolor
# (~100-160 char server-rendered abstract, zero login). This script fixes the extractor (wave7-slice4
# sec-5 pointer) and persists raw+parsed baseline so run-4+ diffs machine-grade (run-2 raw was not
# persisted; run-3 diff vs run-2 is theme-level from the digest, honest note).
# R109 serial pacing; direct connection per T4 ProxyHandler({}) recipe; details stay login-walled.

URL = 'https://www.hibor.com.cn/microns_18.html'
RAW = 'results/hibor_microns18_raw.html'
BASE = 'results/hibor_radar_baseline.json'


def pull(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r = op.open(req, timeout=30)
    return r.read().decode('utf-8', 'ignore')


def parse(raw):
    items = []
    # pair each tab_lta title anchor with the nearest following tab_tdcolor abstract block
    pat = re.compile(r'tab_lta[^>]*>\s*<a[^>]+href="(/data/([0-9a-f]{32})\.html)"[^>]*>(.*?)</a>(.*?)(?=tab_lta|</table|\Z)',
                     re.S)
    for m in pat.finditer(raw):
        title = html.unescape(re.sub(r'<[^>]+>', '', m.group(3))).strip()
        seg = m.group(4)
        am = re.search(r'tab_tdcolor[^>]*>(.*?)</(?:td|div|span)>', seg, re.S)
        abstract = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', am.group(1)))).strip() if am else ''
        items.append({'hash': m.group(2), 'title': title, 'abstract': abstract})
    return items


def main():
    raw = pull(URL)
    open(RAW, 'w', encoding='utf-8').write(raw)
    print('raw bytes:', len(raw))
    items = parse(raw)
    print('items:', len(items))
    prev = None
    try:
        prev = json.load(open(BASE, encoding='utf-8'))
    except FileNotFoundError:
        print('no previous machine baseline (run-3 = baseline-establishing run)')
    new_ids, rolled_out = [], []
    if prev:
        prev_ids = {e['hash'] for e in prev.get('entries', [])}
        cur_ids = {e['hash'] for e in items}
        new_ids = sorted(cur_ids - prev_ids)
        rolled_out = sorted(prev_ids - cur_ids)
        print('machine-diff vs prev (ts=%s): %d new / %d rolled-out' % (prev.get('ts'), len(new_ids), len(rolled_out)))
    for e in items:
        print('%s | %s | abs[%d]' % (e['hash'][:8], e['title'][:70], len(e['abstract'])))
    for h in new_ids:
        e = next(x for x in items if x['hash'] == h)
        print('NEW %s | %s' % (h[:8], e['title'][:70]))
        print('  abs:', e['abstract'][:150])
    out = {'ts': time.strftime('%Y-%m-%dT%H:%M') + time.strftime('%z')[:3],
           'url': URL, 'entries': items, 'new_ids': new_ids, 'rolled_out': rolled_out,
           'note': 'hibor jin-gong radar run (title+abstract extractor fixed per wave7-slice4 sec-5; raw persisted for machine-diff)'}
    json.dump(out, open(BASE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('baseline written:', BASE, 'entries:', len(items))


if __name__ == '__main__':
    main()
