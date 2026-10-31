import sys, os, collections
sys.path.insert(0, 'scripts')
import e326_template_parameter_consumers as e
import e328_quoted_number_staleness as e328

idx = collections.OrderedDict()
for path, src in e.corpus():
    rel = e.relp(path)
    for n, t in e.code_lines(src):
        for m in e328.FACE_TOKEN.finditer(t):
            lit = m.group(1)
            p = e328.face_name(lit)
            if not p:
                continue
            stem, d = p
            i = t.rfind(lit)
            pre = t[:i]
            q = max(pre.rfind('"'), pre.rfind("'"))
            prefix = pre[q + 1:] if q >= 0 else ''
            dironly = os.path.dirname(prefix)
            idx.setdefault((rel, dironly, stem), []).append((n, d, t[:110]))

two = [(k, v) for k, v in idx.items() if len({x[1] for x in v}) > 1]
print('source-family pairs', len(idx), 'multi-vintage', len(two))
for k, v in two[:25]:
    print('==', k)
    for r in v:
        print('   ', r[0], r[1], r[2])