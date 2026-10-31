import sys, os, re, collections
sys.path.insert(0, 'scripts')
import e326_template_parameter_consumers as e
import e328_quoted_number_staleness as e328

TEMPLATE = re.compile(r"([A-Za-z0-9_+\-]+)-%s\.json")
LATEST = re.compile(r"([A-Za-z0-9_+\-]+)_latest\.json")

per_source = collections.OrderedDict()
for path, src in e.corpus():
    rel = e.relp(path)
    for n, t in e.code_lines(src):
        for m in e328.FACE_TOKEN.finditer(t):
            p = e328.face_name(m.group(1))
            if p:
                per_source.setdefault(rel, []).append(('dated', p[0], p[1], n, t[:110]))
        for m in TEMPLATE.finditer(t):
            per_source.setdefault(rel, []).append(('template', m.group(1), None, n, t[:110]))
        for m in LATEST.finditer(t):
            per_source.setdefault(rel, []).append(('latest', m.group(1), None, n, t[:110]))

rows = []
for rel, hits in per_source.items():
    for stem in {h[1] for h in hits}:
        mine = [h for h in hits if h[1] == stem]
        kinds = {h[0] for h in mine}
        dates = {h[2] for h in mine if h[2]}
        if len(kinds) > 1 or len(dates) > 1:
            rows.append((rel, stem, sorted(kinds), len(dates), mine))

print('sources', len(per_source), 'multi-form rows', len(rows))
print(collections.Counter((tuple(r[2]), r[3]) for r in rows))
for rel, stem, kinds, nd, mine in rows:
    if any(k in kinds for k in ('template', 'latest')) or nd > 1:
        print('==', rel, stem, kinds, 'dates=%d' % nd)
        for h in mine[:4]:
            print('   ', h[0], h[2], h[3], h[4])
