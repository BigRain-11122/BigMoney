# -*- coding: utf-8 -*-
"""r956 bm-c: quarantine r955 QC frame estate (120 PNGs, 82MB, bloat-gate)
treasure_guard prescan rc0 (zero registry hits) passed this window.
Reproducible face: source videos in cph4 archive_i2v + committed extract scripts
(_r955bmc_qc_extract.py etc.) + 3 contact sheets already landed (73d795ef7).
7-day observation window per TREASURE_PROTECTION_LAW §2."""
import os, json, hashlib, shutil, time

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
SRC = os.path.join(REPO, 'results', '_r955bmc_qcframes')
TS = '20261013-r956'
DST = os.path.join(REPO, 'results', '_quarantine', f'_r955bmc_qcframes-{TS}')
os.makedirs(DST, exist_ok=True)

files = sorted(os.listdir(SRC))
entries = []
for f in files:
    p = os.path.join(SRC, f)
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    entries.append({'name': f, 'bytes': os.path.getsize(p), 'sha16': h})

for f in files:
    shutil.move(os.path.join(SRC, f), os.path.join(DST, f))

# post-move assert: DST contents == manifest, SRC empty
moved = sorted(os.listdir(DST))
assert moved == [e['name'] for e in entries], 'move mismatch'
for e in entries:
    assert os.path.getsize(os.path.join(DST, e['name'])) == e['bytes'], f'size drift {e["name"]}'
    assert hashlib.sha256(open(os.path.join(DST, e['name']), 'rb').read()).hexdigest()[:16] == e['sha16']
assert os.listdir(SRC) == [], 'src residue'

man = {
    'quarantine_ts': TS, 'round': 'r956', 'machine': 'bm-c',
    'reason': 'QC frame estate 120 PNGs 82MB exceeds bloat discipline; contact sheets (reviewable evidence face) already committed 73d795ef7; source videos archived in cph4 mv0001-handover bmc/archive_i2v + extraction scripts committed -> reproducible artifacts class',
    'prescan': 'treasure_guard prescan rc0 zero hits (this window)',
    'count': len(entries), 'total_bytes': sum(e['bytes'] for e in entries),
    'observation_window_days': 7,
    'files': entries,
}
mp = os.path.join(DST, '_manifest.json')
json.dump(man, open(mp, 'w', encoding='utf-8'), indent=1)
# manifest self-check: dir file count == manifest count + 1 (manifest itself)
assert len(os.listdir(DST)) == len(entries) + 1
print(f'QUARANTINE OK: {len(entries)} files, {man["total_bytes"]:,} bytes -> {DST}')
