# r312 bm-c rebase conflict resolver: results/pool_core_samples.jsonl
# r294 union-domain law (conflict region only, no global dedup) + r442 monotonic
# non-shrink (origin data lines superset check) + true heal: drop diff3 marker
# remnant that bm-b 193ea3483 claimed to drop but is still at origin tail.
# Resolution = origin data lines (116) + bm-c 2 new lines (shard-9/10, ts-ordered
# tail append). Bytes-level: LF endings preserved, raw-blob write.
import subprocess, json, sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
TARGET = 'results/pool_core_samples.jsonl'

origin_raw = subprocess.check_output(['git', '-C', REPO, 'show', 'origin/main:' + TARGET])
work_raw = open(REPO + '\\' + TARGET.replace('/', '\\'), 'rb').read()

def data_lines(raw):
    out = []
    for b in raw.split(b'\n'):
        s = b.strip()
        if s.startswith(b'{'):
            out.append(s)
    return out

origin_data = data_lines(origin_raw)
work_data = data_lines(work_raw)

# r442 guard: every data line in my conflicted side must exist in origin OR be
# one of my genuinely-new lines (no historical line may vanish).
origin_set = set(origin_data)
mine_new = [l for l in work_data if l not in origin_set]
lost = [l for l in work_data if l in origin_set]  # subset check is implicit
# union: origin order + new lines appended in ts order at tail
new_sorted = sorted(mine_new, key=lambda l: json.loads(l)['ts'])
resolved = origin_data + new_sorted

# r185 parse-verify: every line must be valid JSON
for l in resolved:
    json.loads(l)

# assertions
assert len(origin_data) == 116, f'origin data lines {len(origin_data)} != 116'
assert len(mine_new) == 2, f'new lines {len(mine_new)} != 2: {mine_new}'
assert not any(l.startswith((b'<<<', b'|||', b'===', b'>>>')) for l in resolved)

# write: LF endings, trailing newline, bytes-level (no CRLF translation)
out = b'\n'.join(resolved) + b'\n'
open(REPO + '\\' + TARGET.replace('/', '\\'), 'wb').write(out)
print(f'resolved: {len(resolved)} data lines (origin {len(origin_data)} + new {len(new_sorted)})')
print('new lines:')
for l in new_sorted:
    d = json.loads(l)
    print(' ', d['ts'], d['shard'], d['machine_id'])
