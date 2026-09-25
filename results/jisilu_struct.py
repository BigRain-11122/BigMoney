import sys, io, re, html
sys.stdout.reconfigure(encoding='utf-8')

qid = sys.argv[1]
raw = io.open('results/jisilu_%s.html' % qid, encoding='utf-8').read()
# find question-detail style containers
for pat in ['question_detail', 'qa-q-view', 'aw-question-detail', 'question-content', 'markitup-box']:
    idxs = [m.start() for m in re.finditer(re.escape(pat), raw)]
    print(pat, 'hits:', len(idxs), idxs[:6])
# find title in body area
i = raw.find('<h1')
print('--- h1 region ---')
print(repr(raw[i:i + 300]))
