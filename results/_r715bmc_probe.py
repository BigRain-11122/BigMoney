# -*- coding: utf-8 -*-
# r715 bm-c probe: py_watermark verdict + post_review face (PS nested-quote avoid law)
import io, json, os, re

# 1) py_watermark verdict from S6 log
verdict = None
with io.open('results/_r715bmc_s6_log.txt', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('{"ts": "2026-10-08 02:08:49'):
            d = json.loads(line)
            verdict = {k: d.get(k) for k in ('verdict', 'reason', 'cands_open', 'board_open', 'bandit_open', 'local_burns') if k in d}
            break
print('PY_VERDICT:', json.dumps(verdict, ensure_ascii=True))

# 2) post_review face: REPORT-2026-10-08.md section + any post_review results file
rp = 'docs/daily_report/REPORT-2026-10-08.md'
if os.path.exists(rp):
    with io.open(rp, encoding='utf-8') as f:
        text = f.read()
    idx = text.find('post_review')
    print('REPORT has post_review section:', idx >= 0)
    if idx >= 0:
        print(text[idx-50:idx+400].replace('\n', ' | ')[:450])
else:
    print('REPORT file missing')

# 3) standalone post_review evidence files
for pat in ('results', 'research'):
    for fn in os.listdir(pat):
        if 'post_review' in fn.lower():
            print('FOUND:', pat + '/' + fn)

# 4) daily_report JSON twin post_review face
jp = 'docs/daily_report/REPORT-2026-10-08.json'
if os.path.exists(jp):
    with io.open(jp, encoding='utf-8') as f:
        d = json.load(f)
    pr = {k: v for k, v in d.items() if 'review' in k.lower() or 'post' in k.lower()}
    print('REPORT JSON review keys:', json.dumps(pr, ensure_ascii=True)[:400])
