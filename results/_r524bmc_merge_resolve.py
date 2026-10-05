# r524 bm-c merge resolver: 1-UU face (compute_audit.json rolling ledger) vs bm-b r719-4 wave
# Laws applied: r715 (stage blob = full side source, merge-mode), r711 (format-normalized ts
# compare -- parse via fromisoformat, no raw string max), r719 lineage (row-key union history),
# r522 (all-dict type assert -- count identity != type identity), r704 (read-back assert)
import subprocess, json, io, sys
from datetime import datetime

CREATE_NO_WINDOW = 0x08000000
PATH = 'results/compute_audit.json'


def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True,
                       creationflags=CREATE_NO_WINDOW)
    # r710 B-law: empty stdout = stage absent signal, never an empty-file fact
    if r.returncode != 0 or len(r.stdout) == 0:
        raise RuntimeError(f'stage {stage} empty/absent for {path} rc={r.returncode}')
    return r.stdout


def parse_ts(s):
    s = str(s).strip()
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        try:
            return datetime.fromisoformat(s.replace(' ', 'T', 1))
        except ValueError:
            return None


mine_raw = blob(2, PATH)
theirs_raw = blob(3, PATH)
o = json.loads(mine_raw.decode('utf-8'))
t = json.loads(theirs_raw.decode('utf-8'))

# top-level base = newer ts side (format-normalized compare, r711 law).
# The authoritative newest-snapshot face = 'latest' (both schemas carry it);
# top-level 'ts' (theirs schema only) follows the kept latest -- never regress it.
lat_o = o.get('latest') if isinstance(o.get('latest'), dict) else {}
lat_t = t.get('latest') if isinstance(t.get('latest'), dict) else {}
lts_o = parse_ts(lat_o.get('ts'))
lts_t = parse_ts(lat_t.get('ts'))
if lts_o is not None and lts_t is not None:
    latest_is_ours = lts_o >= lts_t
elif lts_o is not None:
    latest_is_ours = True
else:
    latest_is_ours = False
base = dict(t)  # theirs schema (carries top-level 'ts' key), history/llatest overridden below
base['latest'] = dict(lat_o) if latest_is_ours else dict(lat_t)
base['ts'] = base['latest'].get('ts')

# history = row-key dedup union (r519 lineage), sorted by ts
seen, merged = set(), []
for h in (o.get('history') or []) + (t.get('history') or []):
    k = json.dumps(h, sort_keys=True)
    if k not in seen:
        seen.add(k)
        merged.append(h)
merged.sort(key=lambda h: str(h.get('ts', '')))
base['history'] = merged

# r522 law: all rows must be dicts (count identity != type identity)
bad_types = [i for i, h in enumerate(merged) if not isinstance(h, dict)]
assert not bad_types, f'non-dict history rows at {bad_types}'

raw = json.dumps(base, ensure_ascii=False, indent=1)
with open(PATH, 'wb') as f:
    f.write(raw.encode('utf-8'))

# r704 read-back assert: reparse + row count + kept-latest ts identity
rb = json.load(io.open(PATH, encoding='utf-8'))
assert len(rb['history']) == len(merged), 'history row count mismatch'
assert all(isinstance(h, dict) for h in rb['history']), 'readback non-dict row'
kept_lat = rb.get('latest') or {}
kept_ts = kept_lat.get('ts')
expect_ts = lat_o.get('ts') if latest_is_ours else lat_t.get('ts')
assert kept_ts == expect_ts, 'latest face drifted: %s != %s' % (kept_ts, expect_ts)
assert rb.get('ts') == expect_ts, 'top-level ts not aligned to kept latest'

receipt = {
    PATH: {
        'face': 'rolling-union+latest-newer-wins',
        'latest_kept': 'ours' if latest_is_ours else 'theirs',
        'latest_ts_ours': lat_o.get('ts'), 'latest_ts_theirs': lat_t.get('ts'),
        'ts_ours': o.get('ts'), 'ts_theirs': t.get('ts'),
        'ours_rows': len(o.get('history') or []), 'theirs_rows': len(t.get('history') or []),
        'merged_rows': len(merged), 'asserts': 'reparse+count+all-dict+latest-ts-kept PASS',
    }
}
with io.open('results/_r524bmc_merge_resolve.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('RESOLVED', PATH, 'latest=%s ts_ours=%s ts_theirs=%s rows %s+%s -> %s' %
      ('ours' if latest_is_ours else 'theirs', lat_o.get('ts'), lat_t.get('ts'),
       len(o.get('history') or []), len(t.get('history') or []), len(merged)))
