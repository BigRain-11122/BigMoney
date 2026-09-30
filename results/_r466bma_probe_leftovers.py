import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
pats = ['20320500', '20321000', '20321500', 'T-124', 'T-125', 'FOURTEEN', 'FIFTEEN',
        'fourteen', 'fifteen', '24-source', '24 real-reads', '25-source', 'W12-GENERATE',
        'W13-GENERATE', 'sixteen', 'SIXTEEN']
for p in pats:
    n = draft.count(p)
    if n:
        print('%-14s -> %d' % (p, n))
        for m in list(re.finditer(re.escape(p), draft))[:3]:
            s = draft[max(0, m.start()-70):m.start()+50].replace('\n', '\\n')
            print('    ...', repr(s[-110:]))
