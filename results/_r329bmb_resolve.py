# r329 bm-b push-collision resolver (2-UU per classifier: CODELY.md memory-union, compute_audit rolling-ledger)
import subprocess, json, io, sys

ROOT = r'C:\Users\Administrator\Desktop\Bigmoney'

def stage_blob(stage, path):
    b = subprocess.run(['git', '-C', ROOT, 'show', ':%d:%s' % (stage, path)],
                       capture_output=True).stdout
    return b

def write_disk(path, data_bytes):
    with io.open(ROOT + '\\' + path.replace('/', '\\'), 'wb') as f:
        f.write(data_bytes)

receipt = []

# ---------- 1) CODELY.md : memory-union, ADJUDICATED archival-union face ----------
# Upstream (:2:) = bm-c r85 in-place hot-cold archival (9036->7338B: 4 pit-law entries
# moved to research/memory-archive/202609.md + index line refreshed + their r84 entry added).
# Prefix assertion fails by design => manual adjudication per classifier: mine = base+suffix
# (pure append verified), so new = UPSTREAM WHOLE FACE + MY SUFFIX verbatim.
# Zero-loss pre-verified: all 4 removed entries exist in worktree archive; old index line
# replaced by upstream's refreshed index line (index refresh, not data loss).
path = 'CODELY.md'
base = stage_blob(1, path)   # merge-base (9036B round-start face)
up   = stage_blob(2, path)   # upstream archival face (bm-c r85)
mine = stage_blob(3, path)   # my replayed face (base + my r329 entry)
assert mine.startswith(base), 'CODELY mine not base-prefixed (unexpected in-place edit)'
suf_mine = mine[len(base):]
assert b'r329 bm-b' in suf_mine, 'my suffix does not carry the r329 entry'
# zero-loss gate: every hot line upstream removed must exist in the merged archive (stage-0/worktree)
arch_wt = io.open(ROOT + r'\research\memory-archive\202609.md', encoding='utf-8').read()
base_lines = base.decode('utf-8').splitlines()
up_lines = up.decode('utf-8').splitlines()
removed = [l for l in base_lines if l not in up_lines and l.strip()]
up_added = [l for l in up_lines if l not in base_lines]
lost = []
for l in removed:
    if l.startswith('- ['):            # memory entry: must exist verbatim in archive
        if l not in arch_wt:
            lost.append(l[:70])
    else:                               # index/structural line: upstream must carry a same-role replacement
        role_prefix = l[:12]
        if not any(x.startswith(role_prefix) for x in up_added):
            lost.append('NO-REPLACEMENT: ' + l[:70])
assert not lost, 'hot entries lost without archive copy: %r' % lost
new = up + suf_mine
assert len(new) == len(up) + len(suf_mine)
assert len(new) <= 10240, 'CODELY over 10KB line after union: %d' % len(new)
write_disk(path, new)
receipt.append(('CODELY.md', 'memory-union-adjudicated-archival', len(base), len(up), len(suf_mine), len(new), len(removed)))
print('CODELY: base=%dB up=%dB(archival face, %d hot lines moved) mine_suffix=%dB new=%dB' % (
    len(base), len(up), len(removed), len(suf_mine), len(new)))
print('MINE_SUFFIX_TAIL:', repr(suf_mine[-100:]))

# ---------- 2) compute_audit.json : rolling-ledger (history ts-key union zero-loss, latest deep-ts take-new) ----------
path = 'results/compute_audit.json'
upj = json.loads(stage_blob(2, path).decode('utf-8'))
myj = json.loads(stage_blob(3, path).decode('utf-8'))
hist_up = upj.get('history') or []
hist_my = myj.get('history') or []
key = lambda e: e.get('ts')
up_by = {key(e): e for e in hist_up}
collisions, diverged = 0, []
union = list(hist_up)
for e in hist_my:
    k = key(e)
    if k in up_by:
        collisions += 1
        if up_by[k] != e:
            diverged.append(k)
    else:
        union.append(e)
# canonical identity ordering: keep producer order of upstream then new rows appended (ts-asc re-sort)
union_sorted = sorted(union, key=key)
# latest: deep-ts probe (nested latest.ts), existence-checked compare
lu, lm = upj.get('latest') or {}, myj.get('latest') or {}
tsu, tsm = lu.get('ts'), lm.get('ts')
if tsu is None:
    latest, latest_src = lm, 'mine(upstream-latest-missing)'
elif tsm is None:
    latest, latest_src = lu, 'upstream(mine-latest-missing)'
else:
    latest, latest_src = (lm, 'mine') if tsm > tsu else (lu, 'upstream')
merged = {'history': union_sorted, 'latest': latest}
out = json.dumps(merged, ensure_ascii=False, indent=1).encode('utf-8')
# newline mirror: probe base/both-side trailing newline convention
if stage_blob(2, path).endswith(b'}\n') and not out.endswith(b'\n'):
    out += b'\n'
write_disk(path, out)
# parse-verify + zero-loss assertions
chk = json.loads(io.open(ROOT + '\\results\\compute_audit.json', 'rb').read().decode('utf-8'))
assert len(chk['history']) == len(union_sorted)
assert not diverged, 'history key-collision with TRUE divergence: %r' % diverged
receipt.append(('compute_audit.json', 'rolling-ledger', len(hist_up), len(hist_my), len(union_sorted), collisions, latest_src))
print('AUDIT: up_hist=%d mine_hist=%d union=%d collisions=%d diverged=%d latest=%s(%s vs %s)' % (
    len(hist_up), len(hist_my), len(union_sorted), collisions, len(diverged), latest_src, tsu, tsm))

# ---------- summary ----------
print('RECEIPT:', json.dumps(receipt, ensure_ascii=False))
print('RESOLVE_OK')
