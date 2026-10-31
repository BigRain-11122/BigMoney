import sys, os, re, json, collections
sys.path.insert(0, 'scripts')
import e326_template_parameter_consumers as e
import e328_quoted_number_staleness as e328

ROOT = e.ROOT
LATEST = re.compile(r"([A-Za-z0-9_+\-]+)_latest\.json")

rows = collections.OrderedDict()
for path, src in e.corpus():
    rel = e.relp(path)
    for n, t in e.code_lines(src):
        for m in e328.FACE_TOKEN.finditer(t):
            p = e328.face_name(m.group(1))
            if p:
                rows.setdefault(rel, {}).setdefault(p[0], {'dated': [], 'latest': []})['dated'].append((p[1], n))
        for m in LATEST.finditer(t):
            rows.setdefault(rel, {}).setdefault(m.group(1), {'dated': [], 'latest': []})['latest'].append(n)

pairs = [(rel, stem, v) for rel, fams in rows.items() for stem, v in fams.items()
         if v['dated'] and v['latest']]
print('sources naming both a dated cut and the latest pointer for one stem:', len(pairs))
for rel, stem, v in pairs:
    print('==', rel, stem, 'dated', sorted({d.isoformat() for d, n in v['dated']}), 'latest_lines', v['latest'][:3])