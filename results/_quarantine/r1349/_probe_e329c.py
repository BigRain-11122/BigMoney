import sys, os, re, collections
sys.path.insert(0, 'scripts')
import e326_template_parameter_consumers as e
import e328_quoted_number_staleness as e328

ROOT = e.ROOT
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def on_disk(stem, date_token):
    """does results/ hold a face for this stem at this date?"""
    hits = []
    for dirpath, _d, files in os.walk(os.path.join(ROOT, 'results')):
        for name in files:
            if not name.endswith('.json'):
                continue
            p = e328.face_name(name)
            if p and p[0] == stem and p[1] == date_token:
                hits.append(os.path.relpath(os.path.join(dirpath, name), ROOT).replace('\\', '/'))
    return hits


sources = collections.OrderedDict()
for path, src in e.corpus():
    rel = e.relp(path)
    for n, t in e.code_lines(src):
        for m in e328.FACE_TOKEN.finditer(t):
            p = e328.face_name(m.group(1))
            if p:
                sources.setdefault(rel, []).append(('dated', p[0], p[1], n, t))

count = 0
for rel, hits in sources.items():
    for stem in sorted({h[1] for h in hits}):
        mine = [h for h in hits if h[1] == stem]
        dates = sorted({h[2] for h in mine})
        if len(dates) < 2:
            continue
        resolved = [(d, on_disk(stem, d)) for d in dates]
        present = [d for d, h in resolved if h]
        if len(present) < 2:
            continue
        count += 1
        print('==', rel, stem, dates)
        for d, h in resolved:
            print('   ', d, 'ON DISK' if h else '-', h[:3])
print('rows with two cuts both present on disk:', count)